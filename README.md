# 🛡️🤖 Cyber AI Assistant

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
```

## Usage

### Run the Assistant

From the project directory:

```bash
python assistant.py
```
## For network diagnostics that require root (e.g., mtr on macOS), run with sudo:
```bash
sudo python assistant.py
```

## Optional: Set Up Shell Aliases
### Add these to your ~/.bashrc, ~/.zshrc, or equivalent shell config file:
```bash
# Main interactive assistant
alias aiassist='python /path/to/your/project/assistant.py'

# Sudo version for privileged tools
alias sudosai='sudo python /path/to/your/project/assistant.py'

# Quick one‑off question (if you have oneshot.py)
alias aiask='python /path/to/your/project/oneshot.py'

# One‑off tool‑only query (if you have agent_tools.py)
alias aicmd='python /path/to/your/project/agent_tools.py'
```
### Replace /path/to/your/project with the absolute path to the repository.
### After editing, reload your config:
```bash
source ~/.zshrc   # or ~/.bashrc
```

## Example Commands
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
## Log Analysis Capabilities
### The assistant can analyze various log formats and detect common attacks:
| Log Type | What It Detects |
| :--- | :--- |
| **Web** (Apache, Nginx, WAF) | XSS, SQLi, Path Traversal, Command Injection |
| **EDR/Endpoint** (Sysmon, Windows Events, CrowdStrike) | Backdoors, persistence, privilege escalation, encoded commands |
| **Email** (SMTP, Office 365, mail gateways) | Phishing, spoofing, malicious attachments, impersonation |
| **Firewall** (iptables, pf, cloud flow logs) | Port scanning, DDoS, unusual egress/ingress |
| **DNS** (BIND, Windows DNS) | DGA domains, tunneling, excessive queries |
| **VPN** (OpenVPN, WireGuard, Cisco AnyConnect) | Brute‑force login attempts, unusual client IPs |
| **Cloud** (AWS CloudTrail, Azure, GCP) | IAM privilege escalation, suspicious API calls |
| **General** (syslog, application logs) | Anomalies, crashes, unauthorized access |

## Configuration (.env) 
| Variable | Description |
|----------|-------------|
| `OLLAMA_URL` | Your LLM endpoint (e.g., `http://100.x.x.x:11435/v1/chat/completions`) |
| `API_KEY` | API key (leave `dummy` for local Ollama) |
| `MODEL` | Model name (e.g., `qwen2.5-coder:7b`) |
| `SEARXNG_URL` | SearXNG instance URL (default: `https://searx.be`) |


## File Structure
```bash
cyber-ai-assistant/
├── assistant.py          # Main script
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Ignored files
└── README.md             # This file
```
## Customization
### You can extend the assistant by:
- Adding new tools in the `execute_tool()` function.
- Updating the `SYSTEM_PROMPT` to change the assistant's personality or detection rules.
- Adding more keywords to `auto_tool_detect()` for direct command execution.

## License
### This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

