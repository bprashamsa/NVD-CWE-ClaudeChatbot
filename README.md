# NVD + CWE + Risk Chatbot (Claude Edition)

A CLI chatbot that answers security questions using live data from the NVD
CVE API and the MITRE CWE feed — powered by Claude via LangChain, with a
composite **risk score** that goes beyond raw CVSS.

## What's different from the original OpenAI version

- Uses **Claude** (via `langchain-anthropic`) instead of OpenAI for the
  natural-language agent.
- Adds a **risk scoring** tool (`tools/risk_tool.py`) that combines CVSS
  severity with **EPSS** (Exploit Prediction Scoring System) — a free
  FIRST.org score estimating real-world exploitation probability — into a
  single 0–100 risk score and tier (LOW/MEDIUM/HIGH/CRITICAL). This answers
  "what should I patch first?" instead of just "how bad is this in theory?".

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY` (get one at
   platform.claude.com). `NVD_API_KEY` is optional but reduces rate-limiting.
4. Run it:
   ```
   python main.py
   ```

## Browser chat interface

Start the chat API:

```
python web_app.py
```

Then use VS Code Live Server to open `website.html`. The browser interface
uses the same Claude agent when `ANTHROPIC_API_KEY` is configured, and the
same direct-routing fallback when it is not.

If no `ANTHROPIC_API_KEY` is set, the app falls back to direct regex-based
routing using the same tools, without an LLM in the loop.

## Example queries

```
CVE-2021-44228
CVSS of CVE-2021-44228
What is the risk of CVE-2021-44228?          <- new: composite risk score
How worried should I be about CVE-2024-3094? <- new: composite risk score
What is SQL injection?
CWE-79
What year was Heartbleed discovered?
List openssl vulnerabilities in 2025
recent openssl vulnerabilities
```

## Project layout

```
main.py               - CLI entrypoint, agent + fallback routing
tools/nvd_tool.py      - NVD API queries (CVE lookup, keyword/date search)
tools/cwe_tool.py      - MITRE CWE feed fetch + cache, ID/topic lookup
tools/cvss_tool.py     - CVSS score/severity lookup, colored output
tools/risk_tool.py     - NEW: EPSS lookup + composite CVSS+EPSS risk score
tools/utils.py         - CVE/CWE ID normalization helpers
```

## Notes on the risk score

`risk_score = (CVSS/10 * 0.4 + EPSS * 0.6) * 100`

EPSS is weighted higher than CVSS because it reflects *observed* real-world
exploitation likelihood, while CVSS only reflects *theoretical* severity if
exploited. You can tune these weights in `tools/risk_tool.py`.

Tiers: **CRITICAL** ≥75, **HIGH** ≥50, **MEDIUM** ≥25, **LOW** below that.
