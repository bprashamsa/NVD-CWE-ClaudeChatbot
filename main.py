"""NVD + CWE + Risk chatbot, powered by Claude via LangChain.

Answers security questions using live data from NVD and MITRE CWE, plus a
composite risk score (CVSS + EPSS) that goes beyond raw CVSS severity.

If ANTHROPIC_API_KEY is set, natural language is routed through a Claude
tool-calling agent. Otherwise, the app falls back to simple regex-based
direct routing using the same underlying tools.
"""
import os
import re

from dotenv import load_dotenv
from rich.console import Console

from tools.utils import normalize_cve_id, normalize_cwe_id
from tools.nvd_tool import get_cve_details, search_cves, earliest_publication_year
from tools.cwe_tool import lookup_cwe, search_cwe_by_topic
from tools.cvss_tool import get_cvss
from tools.risk_tool import get_risk_score

load_dotenv()
console = Console()


# ---------------------------------------------------------------------------
# LangChain tool wrappers
# ---------------------------------------------------------------------------
def _build_tools():
    from langchain_core.tools import tool

    @tool
    def cve_lookup(cve_id: str) -> dict:
        """Look up full details for a specific CVE ID, e.g. 'CVE-2021-44228'."""
        return get_cve_details(cve_id)

    @tool
    def cvss_lookup(cve_id: str) -> dict:
        """Get the CVSS score and severity for a specific CVE ID."""
        return get_cvss(cve_id)

    @tool
    def risk_score_lookup(cve_id: str) -> dict:
        """Get a composite risk score (0-100) for a CVE, combining CVSS
        severity with EPSS real-world exploitation probability. Use this
        whenever the user asks about risk, priority, urgency, or 'how
        worried should I be' about a CVE — not just its raw CVSS score."""
        return get_risk_score(cve_id)

    @tool
    def cwe_lookup(cwe_id: str) -> dict:
        """Look up a specific CWE ID, e.g. 'CWE-79'."""
        return lookup_cwe(cwe_id)

    @tool
    def cwe_topic_search(topic: str) -> list:
        """Find CWE entries matching a vulnerability topic, e.g. 'SQL injection'
        or 'cross-site scripting'. Use this for 'what is X' style questions."""
        return search_cwe_by_topic(topic)

    @tool
    def cve_keyword_search(
        keyword: str, year: int = None, month: int = None, days_back: int = None
    ) -> list:
        """Search for CVEs by keyword (e.g. product name like 'openssl').
        Optionally scope by year, by month+year, or by a rolling days_back
        window for 'recent' queries (defaults to ~90 days when the user
        asks for recent/latest results without a specific date)."""
        return search_cves(keyword, year=year, month=month, days_back=days_back)

    @tool
    def cve_discovery_year(keyword: str) -> dict:
        """Find the earliest NVD publication year for a keyword/product,
        e.g. answering 'what year was Heartbleed discovered?'."""
        year = earliest_publication_year(keyword)
        return {"keyword": keyword, "earliest_year": year}

    return [
        cve_lookup,
        cvss_lookup,
        risk_score_lookup,
        cwe_lookup,
        cwe_topic_search,
        cve_keyword_search,
        cve_discovery_year,
    ]


# ---------------------------------------------------------------------------
# Claude agent mode
# ---------------------------------------------------------------------------
def answer_question(user_input: str):
    """Answer one question through Claude when configured, else direct routing."""
    if os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage, ToolMessage

        tools = _build_tools()
        tool_map = {tool.name: tool for tool in tools}
        messages = [HumanMessage(user_input)]
        llm = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"))
        llm_with_tools = llm.bind_tools(tools)
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        while ai_msg.tool_calls:
            for call in ai_msg.tool_calls:
                try:
                    result = tool_map[call["name"]].invoke(call["args"])
                except Exception as exc:  # noqa: BLE001 - surface tool errors to the LLM
                    result = {"error": str(exc)}
                messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)
        return ai_msg.content

    lowered = user_input.lower()
    cve_id = normalize_cve_id(user_input)
    cwe_id = normalize_cwe_id(user_input)

    if cve_id and ("risk" in lowered or "priorit" in lowered or "worried" in lowered):
        return get_risk_score(cve_id)
    if cve_id and "cvss" in lowered:
        return get_cvss(cve_id)
    if cve_id:
        return get_cve_details(cve_id)
    if cwe_id:
        return lookup_cwe(cwe_id)
    if lowered.startswith("what is") or "explain" in lowered:
        topic = re.sub(r"what is|explain|\?", "", lowered).strip()
        return search_cwe_by_topic(topic)
    if "what year" in lowered:
        topic = re.sub(r"what year (was|did)|discovered|vulnerability|\?", "", lowered).strip()
        return {"earliest_year": earliest_publication_year(topic)}
    return search_cves(user_input, days_back=90)


def run_agent_mode():
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, ToolMessage

    llm = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"))

    console.print("[bold green]Claude agent mode (LangChain, custom tools enabled).[/bold green]")
    console.print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = console.input("[bold cyan]> [/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        console.print(answer_question(user_input))


# ---------------------------------------------------------------------------
# Direct routing mode (no API key needed)
# ---------------------------------------------------------------------------
def run_direct_mode():
    console.print("[bold yellow]Direct mode (no LangChain agent) — set ANTHROPIC_API_KEY to enable Claude.[/bold yellow]")
    console.print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = console.input("[bold cyan]> [/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        console.print(answer_question(user_input))


if __name__ == "__main__":
    if os.getenv("ANTHROPIC_API_KEY"):
        run_agent_mode()
    else:
        run_direct_mode()
