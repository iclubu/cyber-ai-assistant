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






