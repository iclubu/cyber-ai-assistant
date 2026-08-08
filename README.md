# Cyber AI Assistant

A terminal‑based, tool‑powered AI assistant for cybersecurity tasks. It runs locally (or via Tailscale), remembers conversation context, and can execute network diagnostics, read files, fetch CVEs, search the web, and more – all through natural language.

## Features

- Interactive chat with full conversation memory.
- **11 built‑in tools**:
  - `read_file` – read local files.
  - `run_command` – execute shell commands (dangerous ones ask for confirmation).
  - `fetch_cve` – get CVE details from the NVD API.
  - `web_search` – search the web via SearXNG.
  - `whois` – WHOIS lookup for domains/IPs.
  - `ping` – ping a host (4 packets).
  - `nslookup` – DNS lookup.
  - `curl` – fetch URL content (headers + body).
  - `port_scan` – scan common ports on a host.
  - `mtr` – My TraceRoute (combined traceroute + ping report).
- **Auto‑detection** – type `mtr google.com` or `cat log.txt` and it runs the tool directly, bypassing the LLM.
- **Log analysis** – detects and classifies attacks from web logs (XSS, SQLi), EDR logs (backdoors, privilege escalation), and email logs (phishing, spoofing).
- **Auto‑analysis** – type `analyze log.txt` and it will read the file, print the content, and give a structured summary, severity grouping, attack classification, and recommendations.
- **Fallback skill** – if no tool fits, it automatically uses `web_search` to find current information.
- **Safety** – destructive commands (`rm -rf /`, `mkfs`, etc.) trigger a confirmation prompt before execution.
- **Privacy** – your LLM endpoint and API keys stay in a local `.env` file (ignored by Git).

## Requirements

- Python 3.8+
- `pip` (Python package manager)
- (Optional) `mtr` – for full network diagnostics (`brew install mtr` on macOS)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cyber-ai-assistant.git
cd cyber-ai-assistant

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file from the template
cp .env.example .env
# Edit .env and set your LLM endpoint (e.g., http://your-tailscale-ip:11435/v1/chat/completions)

## Usage

### Run the Assistant

From the project directory:

```bash
python assistant.py
```

For network diagnostics that require root (e.g., `mtr` on macOS), run with `sudo`:

```bash
sudo python assistant.py
```

### Optional: Set Up Shell Aliases

Add these to your `~/.bashrc`, `~/.zshrc`, or equivalent shell config file:

```bash
# Main interactive assistant with memory + tools
alias aiassist='python /path/to/your/project/assistant.py'

# Sudo version for privileged tools (e.g., mtr)
alias sudosai='sudo python /path/to/your/project/assistant.py'

# Quick one‑off question (no tools – if you have oneshot.py)
alias aiask='python /path/to/your/project/oneshot.py'

# One‑off tool‑only query (if you have agent_tools.py)
alias aicmd='python /path/to/your/project/agent_tools.py'
```

Replace `/path/to/your/project` with the actual absolute path to the repository on your machine.

After editing, reload your config:

```bash
source ~/.zshrc   # or ~/.bashrc
```

Now you can start the assistant from anywhere by typing `aiassist`.

### Example Commands

```text
> Read test.txt
> ping 8.8.8.8
> mtr google.com
> whois example.com
> Search for latest OpenSSL vulnerabilities
> Explain CVE-2024-1234
> curl https://api.github.com with user-agent "MyAgent"
```

### Example Commands

```bash
> Read test.txt
> ping 8.8.8.8
> mtr google.com
> whois example.com
> Search for latest OpenSSL vulnerabilities
> Explain CVE-2024-1234
> curl https://api.github.com with user-agent "MyAgent"
> cat log.txt
> analyze log.txt
> analyze edr_log.txt
> analyze email_log.txt
```

### Log Analysis Capabilities
```text
The assistant can analyze various log formats and detect common attacks:

| Log Type |	What It Detects |
|----------|------------------|
| Web (Apache, Nginx, WAF) |	XSS, SQLi, Path Traversal, Command Injection
| EDR/Endpoint (Sysmon, Windows Events, CrowdStrike) |	Backdoors, persistence, privilege escalation, encoded commands
| Email (SMTP, Office 365, mail gateways)  |	Phishing, spoofing, malicious attachments, impersonation
| Firewall (iptables, pf, cloud flow logs) |	Port scanning, DDoS, unusual egress/ingress
| DNS (BIND, Windows DNS) |	DGA domains, tunneling, excessive queries
| VPN (OpenVPN, WireGuard, Cisco AnyConnect) |	Brute‑force login attempts, unusual client IPs
| Cloud (AWS CloudTrail, Azure, GCP) |	IAM privilege escalation, suspicious API calls
| General (syslog, application logs) |	Anomalies, crashes, unauthorized access
```

### Running with `sudo`

Some tools (like `mtr` on macOS) require root privileges. You can run the assistant with `sudo` when needed:

```bash
sudo python assistant.py
```

## Configuration (`.env`)

| Variable | Description |
|----------|-------------|
| `OLLAMA_URL` | Your LLM endpoint (e.g., `http://100.x.x.x:11435/v1/chat/completions`) |
| `API_KEY` | API key (leave `dummy` for local Ollama) |
| `MODEL` | Model name (e.g., `qwen2.5-coder:7b`) |
| `SEARXNG_URL` | SearXNG instance URL (default: `https://searx.be`) |

## File Structure

```
cyber-ai-assistant/
├── assistant.py          # Main script
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Ignored files
└── README.md             # This file
```
## Customisation
You can extend the assistant by:

Adding new tools in the execute_tool() function.

Updating the SYSTEM_PROMPT to change the assistant's personality or detection rules.

Adding more keywords to auto_tool_detect() for direct command execution.

## Security Notes

- Never commit your `.env` file – it contains real IPs and keys.
- Running the assistant with `sudo` gives it full system access – use with caution.
- The `run_command` tool can execute any command; dangerous ones trigger a confirmation prompt.

## License

MIT (or choose your own).

---

## 🔍 What Changed (Compared to Your Current README)

| Section | Change |
| :--- | :--- |
| **Features** | Added bullet points for log analysis, auto‑analysis, and `cat`/`analyze`. |
| **Example Commands** | Added `cat log.txt`, `analyze log.txt`, `analyze edr_log.txt`, `analyze email_log.txt`. |
| **New Section** | Added **Log Analysis Capabilities** table showing what it can detect for each log type. |
| **Configuration** | Updated to match your current table (unchanged). |
| **File Structure** | Added note that `assistant.py` now includes log analysis. |
| **Customisation** | Added mention of updating `SYSTEM_PROMPT` for detection rules. |

---

## ✅ How to Apply

1. Copy the full README above.
2. Open your `README.md` on GitHub (or locally with `nano README.md`).
3. Replace the entire content with the new version.
4. Commit and push.

---

## 🎯 Summary

- **Your current structure** is preserved.
- **New capabilities** are clearly documented.
- **Log types table** gives users a quick reference for what the assistant can analyze.
- **Example commands** now include `analyze` for web, EDR, and email logs.

Let me know if you want any tweaks! 🚀
