"""
OpenAI Research-to-Publish Pipeline
Orchestrates two agents:
  1. Research Agent  — searches the web, writes a Markdown report
  2. Publisher Agent — converts the report to MDX and publishes it to the website

Usage:
    python pipeline.py                         # interactive mode
    python pipeline.py --topic "AI trends"     # direct topic
    python pipeline.py --auto                  # pick next from daily_topics.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

import publisher_agent
import research_agent

# Paths
ROOT = Path(__file__).parent.resolve()
WEBSITE_DIR = Path(os.environ.get("WEBSITE_DIR", ROOT / "website"))
REPORTS_DIR = ROOT / "reports"
TOPICS_FILE = ROOT / "daily_topics.json"


# ---------------------------------------------------------------------------
# Interactive prompt helpers
# ---------------------------------------------------------------------------

def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(0)
    return value or default


def ask_list(prompt: str) -> list[str]:
    raw = ask(f"{prompt} (comma-separated, or leave blank)")
    return [t.strip() for t in raw.split(",") if t.strip()] if raw else []


def gather_inputs() -> dict:
    print("\n" + "=" * 60)
    print("  OpenAI Research → Publish Pipeline")
    print("=" * 60)

    topic = ""
    while not topic:
        topic = ask("\nResearch topic")
        if not topic:
            print("  Topic cannot be empty.")

    print("\nContent type:")
    print("  1. Blog post")
    print("  2. Research paper")
    choice = ""
    while choice not in ("1", "2"):
        choice = ask("Choose", default="1")
    content_type = "blog" if choice == "1" else "papers"

    tags = ask_list("Tags")

    authors: list[str] = []
    venue = ""
    doi = ""
    if content_type == "papers":
        authors = ask_list("Authors")
        venue = ask("Venue (journal/conference)", default="")
        doi = ask("DOI (optional)", default="")

    docs_dir = ask("\nLocal docs directory (optional, leave blank to skip)", default="")
    docs_dir = str(Path(docs_dir).resolve()) if docs_dir else None

    return {
        "topic": topic,
        "content_type": content_type,
        "tags": tags,
        "authors": authors,
        "venue": venue,
        "doi": doi,
        "docs_dir": docs_dir,
    }


# ---------------------------------------------------------------------------
# Auto mode: rotate through daily_topics.json
# ---------------------------------------------------------------------------

def pick_next_topic() -> dict:
    if not TOPICS_FILE.exists():
        print(f"Error: {TOPICS_FILE} not found.")
        sys.exit(1)

    data = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    topics = data.get("topics", [])
    last_index = data.get("last_index", -1)

    if not topics:
        print("Error: No topics in daily_topics.json.")
        sys.exit(1)

    next_index = (last_index + 1) % len(topics)
    entry = topics[next_index]

    data["last_index"] = next_index
    TOPICS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"\nAuto mode: topic {next_index + 1}/{len(topics)}: {entry['topic']}")
    return {
        "topic": entry["topic"],
        "content_type": entry.get("type", "blog"),
        "tags": entry.get("tags", []),
        "authors": entry.get("authors", []),
        "venue": entry.get("venue", ""),
        "doi": entry.get("doi", ""),
        "docs_dir": None,
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(inputs: dict) -> None:
    topic = inputs["topic"]
    content_type = inputs["content_type"]
    tags = inputs["tags"]
    authors = inputs["authors"]
    venue = inputs["venue"]
    doi = inputs["doi"]
    docs_dir = inputs["docs_dir"]

    # Prepare file paths
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
    safe = safe[:40].strip().replace(" ", "_")
    slug = safe.lower().replace("_", "-")

    report_path = str(REPORTS_DIR / f"report_{safe}_{timestamp}.md")
    publish_path = str(WEBSITE_DIR / "content" / content_type / f"{slug}.mdx")
    today = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "=" * 60)
    print(f"  Topic:   {topic}")
    print(f"  Type:    {content_type}")
    print(f"  Report:  {report_path}")
    print(f"  Publish: {publish_path}")
    print("=" * 60)

    client = OpenAI()  # uses OPENAI_API_KEY env var

    # Step 1 — Research
    print("\nStep 1: Research")
    research_agent.run(
        client=client,
        topic=topic,
        output_path=report_path,
        docs_dir=docs_dir,
    )

    # Step 2 — Publish
    print("\nStep 2: Publish")
    publisher_agent.run(
        client=client,
        report_path=report_path,
        publish_path=publish_path,
        website_dir=str(WEBSITE_DIR),
        topic=topic,
        slug=slug,
        content_type=content_type,
        date=today,
        tags=tags,
        authors=authors,
        venue=venue,
        doi=doi,
    )

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print(f"Published: {publish_path}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI research-to-publish pipeline.")
    parser.add_argument("--topic", help="Research topic (skips interactive prompt)")
    parser.add_argument("--type", choices=["blog", "papers"], default="blog", dest="content_type")
    parser.add_argument("--tags", help="Comma-separated tags", default="")
    parser.add_argument("--auto", action="store_true", help="Pick next topic from daily_topics.json")
    args = parser.parse_args()

    if args.auto:
        inputs = pick_next_topic()
    elif args.topic:
        inputs = {
            "topic": args.topic,
            "content_type": args.content_type,
            "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
            "authors": [],
            "venue": "",
            "doi": "",
            "docs_dir": None,
        }
    else:
        inputs = gather_inputs()

    run_pipeline(inputs)


if __name__ == "__main__":
    main()
