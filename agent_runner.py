"""
Generic OpenAI agent runner.
Handles the tool-use loop: call model → execute tools → repeat until done.
"""

import json
from typing import Any, Callable

from openai import OpenAI


def run_agent(
    client: OpenAI,
    system_prompt: str,
    user_prompt: str,
    tools: list[dict],
    tool_handlers: dict[str, Callable],
    model: str = "gpt-4o-mini",
    max_turns: int = 30,
    label: str = "Agent",
) -> str:
    """
    Run an agent loop until the model stops calling tools or max_turns is reached.
    Returns the final text response.
    """
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools or None,
            tool_choice="auto" if tools else None,
        )

        choice = response.choices[0]
        message = choice.message
        messages.append(message)

        # No tool calls → agent is done
        if not message.tool_calls:
            return message.content or ""

        # Execute each tool call
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"  [{label}] → {name}({', '.join(f'{k}={repr(v)[:60]}' for k, v in args.items())})")

            if name in tool_handlers:
                result = tool_handlers[name](**args)
            else:
                result = f"Error: unknown tool '{name}'"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    return "Max turns reached without a final response."
