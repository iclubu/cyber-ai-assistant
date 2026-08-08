import requests
import subprocess
import json
import sys
import re
import os
import socket
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/chat/completions")
MODEL = os.getenv("MODEL", "qwen2.5-coder:7b")
SEARXNG_URL = os.getenv("SEARXNG_URL", "https://searx.be")
MAX_TOOL_CALLS = 5
API_KEY = os.getenv("API_KEY", "dummy")

DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s+/',
    r'mkfs',
    r'dd\s+if=',
    r'>\s*/dev/sd',
    r':(){ :|:& };:',
    r'chmod\s+777\s+/',
]

def is_dangerous_command(cmd):
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return True
    return False

SYSTEM_PROMPT = """You are a cybersecurity assistant. When the user provides log content or asks you to analyze logs, follow these rules:

1. **Summarise** – total entries, suspicious count.
2. **Group by severity** – High (script injection), Medium (event handlers), Low (benign).
3. **Classify the attack** – if it's XSS, SQLi, etc., state it clearly.
4. **Give recommendations** – once, not repeated.

You have access to tools, but for this analysis you already have the log content in the conversation.

Be concise, safe, and actionable."""

def execute_tool(tool_str, interactive=True):
    match = re.match(r'TOOL:\s*(\w+)\s*[| ]\s*(.+)', tool_str, re.IGNORECASE)
    if not match:
        return "Error: tool format should be 'TOOL: toolname|argument'"
    tool, arg = match.group(1).strip(), match.group(2).strip()

    if tool == "read_file":
        if not os.path.isabs(arg):
            arg = os.path.join(os.getcwd(), arg)
        try:
            with open(arg, 'r') as f:
                return f.read()[:2000]
        except Exception as e:
            return f"Error reading file: {str(e)}"

    elif tool == "run_command":
        if is_dangerous_command(arg):
            if interactive:
                print(f"\n⚠️  WARNING: The command '{arg}' appears dangerous.")
                confirm = input("Do you want to execute it? (yes/no): ").strip().lower()
                if confirm != 'yes':
                    return "Command execution cancelled by user."
            else:
                return "Dangerous command blocked (non-interactive mode)."
        try:
            result = subprocess.run(arg, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error running command: {str(e)}"

    elif tool == "fetch_cve":
        try:
            resp = requests.get(f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={arg}")
            data = resp.json()
            if 'vulnerabilities' in data and data['vulnerabilities']:
                cve = data['vulnerabilities'][0]['cve']
                desc = cve['descriptions'][0]['value'] if cve.get('descriptions') else "No description"
                return f"CVE {arg}: {desc[:500]}"
            else:
                return f"No details found for {arg}"
        except Exception as e:
            return f"Error fetching CVE: {str(e)}"

    elif tool == "web_search":
        try:
            params = {"q": arg, "format": "json", "categories": "general", "language": "en"}
            response = requests.get(SEARXNG_URL + "/search", params=params, timeout=15)
            if 'application/json' not in response.headers.get('Content-Type', ''):
                return f"Search service returned non-JSON (status {response.status_code}). No results."
            data = response.json()
            results = data.get("results", [])[:5]
            if not results:
                return "No results found."
            formatted = []
            for r in results:
                title = r.get("title", "No title")
                snippet = r.get("content", "No snippet")
                url = r.get("url", "#")
                formatted.append(f"- {title}: {snippet[:200]} ({url})")
            return "\n".join(formatted)
        except json.JSONDecodeError:
            return "Search service returned invalid JSON. No results."
        except Exception as e:
            return f"Web search error: {str(e)}"

    elif tool == "whois":
        try:
            result = subprocess.run(["whois", arg], capture_output=True, text=True, timeout=10)
            return result.stdout[:2000]
        except Exception as e:
            return f"WHOIS error: {str(e)}"

    elif tool == "ping":
        try:
            result = subprocess.run(["ping", "-c", "4", "-W", "2", arg], capture_output=True, text=True, timeout=10)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Ping error: {str(e)}"

    elif tool == "nslookup":
        try:
            result = subprocess.run(["nslookup", arg], capture_output=True, text=True, timeout=5)
            return result.stdout + result.stderr
        except Exception as e:
            return f"NSLOOKUP error: {str(e)}"

    elif tool == "curl":
        try:
            resp = requests.get(arg, timeout=10, headers={"User-Agent": "AI-Assistant"})
            content = resp.text[:10000]
            return f"Status: {resp.status_code}\nContent:\n{content}"
        except Exception as e:
            return f"CURL error: {str(e)}"

    elif tool == "port_scan":
        try:
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 5900, 8080]
            open_ports = []
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    result = sock.connect_ex((arg, port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    pass
            if open_ports:
                return f"Open ports on {arg}: {', '.join(map(str, open_ports))}"
            else:
                return f"No common ports open on {arg}"
        except Exception as e:
            return f"Port scan error: {str(e)}"

    elif tool == "mtr":
        try:
            result = subprocess.run(["mtr", "--report", "-c", "10", arg], capture_output=True, text=True, timeout=20)
            output = result.stdout + result.stderr
            return output[:2000] if output else "No output from mtr."
        except FileNotFoundError:
            return "mtr command not found. Please install it (e.g., 'brew install mtr' on macOS)."
        except Exception as e:
            return f"MTR error: {str(e)}"

    else:
        return f"Unknown tool: {tool}"

def auto_tool_detect(user_input):
    """
    Returns: (handled, output, content_for_analysis, original_input)
    - handled: bool, True if we executed a tool.
    - output: string to print (if any).
    - content_for_analysis: string (file content) if we read a file and analysis is requested.
    - original_input: the user's input to be used for analysis.
    """
    words = user_input.strip().split()
    if not words:
        return (False, None, None, None)

    cmd = words[0].lower()

    # Network tools
    if cmd in ["mtr", "ping", "whois", "nslookup", "port_scan"]:
        if len(words) < 2:
            return (True, f"Error: Missing argument for {cmd}.", None, None)
        arg = " ".join(words[1:])
        tool_str = f"TOOL: {cmd}|{arg}"
        result = execute_tool(tool_str, interactive=True)
        return (True, result, None, None)

    if cmd == "curl" and len(words) >= 2:
        arg = " ".join(words[1:])
        tool_str = f"TOOL: curl|{arg}"
        result = execute_tool(tool_str, interactive=True)
        return (True, result, None, None)

    # File reading explicit commands
    if cmd in ["read_file", "read", "cat", "show"] and len(words) >= 2:
        arg = " ".join(words[1:])
        tool_str = f"TOOL: read_file|{arg}"
        result = execute_tool(tool_str, interactive=True)
        # Check if user wants analysis
        analysis_keywords = ["analyze", "review", "examine", "inspect", "what type", "is it", "attack", "identify"]
        if any(kw in user_input.lower() for kw in analysis_keywords):
            return (True, result, result, user_input)  # result is file content
        else:
            return (True, result, None, None)

    # Run command
    if cmd in ["run", "run_command"] and len(words) >= 2:
        arg = " ".join(words[1:])
        tool_str = f"TOOL: run_command|{arg}"
        result = execute_tool(tool_str, interactive=True)
        return (True, result, None, None)

    # CVE
    if cmd in ["cve", "fetch_cve"] and len(words) >= 2:
        arg = " ".join(words[1:])
        tool_str = f"TOOL: fetch_cve|{arg}"
        result = execute_tool(tool_str, interactive=True)
        return (True, result, None, None)

    # Web search
    if cmd in ["search", "web_search"] and len(words) >= 2:
        arg = " ".join(words[1:])
        tool_str = f"TOOL: web_search|{arg}"
        result = execute_tool(tool_str, interactive=True)
        return (True, result, None, None)

    # Generic "analyze log.txt" without explicit command
    file_match = re.search(r'\b([^\s]+\.(log|txt|csv|json|yml|yaml|xml))\b', user_input, re.IGNORECASE)
    if file_match:
        filename = file_match.group(1)
        analysis_keywords = ["analyze", "review", "examine", "inspect", "what type", "is it", "attack", "identify", "check", "look at"]
        if any(kw in user_input.lower() for kw in analysis_keywords):
            tool_str = f"TOOL: read_file|{filename}"
            result = execute_tool(tool_str, interactive=True)
            return (True, result, result, user_input)

    return (False, None, None, None)

def main():
    print("AI Assistant (type 'exit' to quit)")
    print("Tools: read_file, run_command, fetch_cve, web_search, whois, ping, nslookup, curl, port_scan, mtr")
    print("Tip: Type commands directly, e.g., 'cat log.txt', 'analyze log.txt'")
    print("-" * 50)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
        if not user_input:
            continue

        # Auto‑detect and get content
        handled, output, content, original_input = auto_tool_detect(user_input)

        if handled and content is not None:
            # We read a file and the user wants analysis
            print("\nFile content (for analysis):\n", content)
            # Build a new user message that includes the file content and the analysis prompt
            analysis_prompt = f"Here is the content of the log file:\n\n{content}\n\nNow answer the user's question: {original_input}\nProvide a clear summary, severity grouping, attack classification, and recommendations."
            messages.append({"role": "user", "content": analysis_prompt})
            # Now let the LLM generate the response
            try:
                response = requests.post(
                    OLLAMA_URL,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": MODEL,
                        "messages": messages,
                        "temperature": 0.2,
                        "stream": False
                    }
                )
                reply = response.json()["choices"][0]["message"]["content"]
                print("\nAssistant:", reply)
                messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                print(f"\nError connecting to LLM: {e}")
            continue

        elif handled and output is not None:
            # Tool executed, just print the output
            print("\nTool Output:\n", output)
            continue

        # Normal LLM flow (no auto-detect)
        messages.append({"role": "user", "content": user_input})
        tool_calls = 0
        reply = None

        while tool_calls < MAX_TOOL_CALLS:
            try:
                response = requests.post(
                    OLLAMA_URL,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": MODEL,
                        "messages": messages,
                        "temperature": 0.2,
                        "stream": False
                    }
                )
                reply = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"\nError connecting to LLM: {e}")
                break

            tool_lines = [line.strip() for line in reply.split('\n') if line.strip().upper().startswith("TOOL:")]
            if tool_lines:
                if len(tool_lines) > 1:
                    print("⚠️  The model requested multiple tools. Using only the first.")
                tool_str = tool_lines[0]
                tool_result = execute_tool(tool_str, interactive=True)

                # Auto‑fallback for web_search + CVE
                if "web_search" in tool_str.lower() and (
                    "no results" in tool_result.lower() or "error" in tool_result.lower()
                ):
                    cve_match = re.search(r'CVE-\d{4}-\d{4,}', user_input, re.IGNORECASE)
                    if cve_match:
                        cve_id = cve_match.group(0).upper()
                        fallback_result = execute_tool(f"TOOL: fetch_cve|{cve_id}", interactive=True)
                        messages.append({"role": "assistant", "content": reply})
                        messages.append({"role": "system", "content": f"Tool result: {tool_result}"})
                        messages.append({"role": "assistant", "content": f"TOOL: fetch_cve|{cve_id}"})
                        messages.append({"role": "system", "content": f"Tool result: {fallback_result}"})
                        tool_calls += 2
                        continue

                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "system", "content": f"Tool result: {tool_result}"})
                tool_calls += 1
            else:
                print("\nAssistant:", reply)
                messages.append({"role": "assistant", "content": reply})
                break
        else:
            print("\nAssistant: Too many tool calls. Last reply:")
            print(reply)
            messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
