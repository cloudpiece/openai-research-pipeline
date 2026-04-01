"""
Publisher Agent
Reads a Markdown report and publishes it as an MDX file to the website,
then commits and pushes to GitHub.
"""

from openai import OpenAI

from agent_runner import run_agent
from tools import FILE_HANDLERS, FILE_TOOLS

SYSTEM_PROMPT = """You are a content publisher for a research website.
Your job is to:
1. Read a Markdown research report using read_file
2. Convert it to a clean MDX file with proper YAML frontmatter
3. Save the MDX file to the correct path using write_file
4. Commit and push to GitHub using run_command

MDX file format:
---
title: "Concise title derived from the report"
date: "YYYY-MM-DD"
excerpt: "1-2 sentence summary from the report's Summary section"
tags: ["tag1", "tag2"]
---

[report content here — preserve all headings, lists, links, and sources]

Rules:
- Derive the title from the report's main heading
- Write the excerpt from the Summary section
- Keep all content, headings, bullet points, and source links intact
- Do not add or remove any factual content
"""


def run(
    client: OpenAI,
    report_path: str,
    publish_path: str,
    website_dir: str,
    topic: str,
    slug: str,
    content_type: str,
    date: str,
    tags: list[str],
    authors: list[str],
    venue: str,
    doi: str,
) -> str:
    """Run the publisher agent."""
    print(f"\n[Publisher Agent] Publishing: {publish_path}")

    extra_frontmatter = ""
    if content_type == "papers":
        extra_frontmatter = f"""authors: {authors}
venue: "{venue}"
doi: "{doi}"
"""

    prompt = f"""Publish a research report to the website.

1. Read the report from: {report_path}

2. Convert it to MDX with this frontmatter template:
---
title: (derive from report heading)
date: "{date}"
excerpt: (1-2 sentences from the Summary section)
tags: {tags}
{extra_frontmatter}---

3. Save the MDX to: {publish_path}

4. Run these git commands to publish:
   cd {website_dir} && git add content/{content_type}/{slug}.mdx && git commit -m "publish: {topic}" && git push

Confirm when done.
"""

    result = run_agent(
        client=client,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        tools=FILE_TOOLS,
        tool_handlers=FILE_HANDLERS,
        model="gpt-4o-mini",
        max_turns=15,
        label="Publisher",
    )

    print("[Publisher Agent] Done.")
    return result
