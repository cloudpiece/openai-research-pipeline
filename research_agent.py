"""
Research Agent
Searches the web and writes a structured Markdown report to a file.
"""

from pathlib import Path

from openai import OpenAI

from agent_runner import run_agent
from tools import FILE_HANDLERS, WEB_HANDLERS, FILE_TOOLS, WEB_TOOLS

SYSTEM_PROMPT = """You are an expert research assistant. Your job is to:
1. Search the web multiple times with varied queries to gather broad, accurate information
2. Fetch and read the most relevant pages for detailed content
3. Synthesize everything into a clear, well-structured Markdown report
4. Save the final report to a file using write_file

Research methodology:
- Perform at least 4-5 searches with different angles on the topic
- Fetch at least 3-4 pages to get detailed information
- Cross-reference sources for accuracy
- Always list every source URL you used

Report format (use exactly):
# [Topic Title]
**Summary:** [2-3 sentence executive summary]

## Key Findings
[Bullet points of the most important discoveries]

## Detailed Analysis
[In-depth sections with subheadings for each major subtopic]

## Sources
[Numbered list of all URLs consulted]

## Conclusion
[Final synthesis and key takeaways]
"""

ALL_TOOLS = WEB_TOOLS + FILE_TOOLS
ALL_HANDLERS = {**WEB_HANDLERS, **FILE_HANDLERS}


def run(client: OpenAI, topic: str, output_path: str, docs_dir: str | None = None) -> str:
    """Run the research agent. Returns the report content."""
    print(f"\n[Research Agent] Starting research: {topic}")

    extra = ""
    if docs_dir and Path(docs_dir).is_dir():
        extra = f"\nAlso search local documents in: {docs_dir} using read_file."

    prompt = f"""Research this topic thoroughly and save a Markdown report.

Topic: {topic}
Save the report to: {output_path}
{extra}

Steps:
1. Run 4-5 web searches with different queries about the topic
2. Fetch and read 3-4 of the most relevant pages
3. Write the complete Markdown report
4. Save it to {output_path} using write_file
"""

    result = run_agent(
        client=client,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        tools=ALL_TOOLS,
        tool_handlers=ALL_HANDLERS,
        model="gpt-4o-mini",
        max_turns=30,
        label="Research",
    )

    if Path(output_path).exists():
        size = Path(output_path).stat().st_size
        print(f"[Research Agent] Report saved: {output_path} ({size:,} bytes)")
    else:
        print(f"[Research Agent] Warning: report file not found at {output_path}")

    return result
