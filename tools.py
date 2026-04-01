"""
Tool implementations for the research pipeline agents.
- web_search: DuckDuckGo search (no API key needed)
- fetch_url:  fetch and extract readable text from a URL
- read_file:  read a local file
- write_file: write content to a local file
- run_command: run a shell command
"""

import json
import subprocess
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS


# ---------------------------------------------------------------------------
# Web tools
# ---------------------------------------------------------------------------

def web_search(query: str, max_results: int = 6) -> str:
    """Search the web using DuckDuckGo. Returns JSON list of results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Search error: {e}"


def fetch_url(url: str, max_chars: int = 6000) -> str:
    """Fetch a URL and return readable plain text (scripts/styles stripped)."""
    try:
        response = httpx.get(url, follow_redirects=True, timeout=15,
                             headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:max_chars]
    except Exception as e:
        return f"Fetch error: {e}"


# ---------------------------------------------------------------------------
# File system tools
# ---------------------------------------------------------------------------

def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return f"Read error: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories as needed."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written: {path} ({len(content):,} chars)"
    except Exception as e:
        return f"Write error: {e}"


def run_command(command: str, cwd: str | None = None) -> str:
    """Run a shell command and return stdout + stderr."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=30
        )
        output = result.stdout.strip()
        if result.stderr.strip():
            output += f"\nSTDERR: {result.stderr.strip()}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return output or "(no output)"
    except Exception as e:
        return f"Command error: {e}"


# ---------------------------------------------------------------------------
# Tool schemas (OpenAI function definitions)
# ---------------------------------------------------------------------------

WEB_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information on a topic. Returns titles, URLs, and snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {"type": "integer", "description": "Number of results (default 6)", "default": 6},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch a webpage and return its readable text content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch"},
                },
                "required": ["url"],
            },
        },
    },
]

FILE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a local file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a local file (creates parent directories if needed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command. Use for git operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"},
                    "cwd": {"type": "string", "description": "Working directory (optional)"},
                },
                "required": ["command"],
            },
        },
    },
]

# Handler maps
WEB_HANDLERS = {"web_search": web_search, "fetch_url": fetch_url}
FILE_HANDLERS = {"read_file": read_file, "write_file": write_file, "run_command": run_command}
