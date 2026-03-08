"""
Central Claude API wrapper. All AI calls in this codebase route through here.
NEVER call the Anthropic SDK directly from routers, services, or workers.
"""
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


async def call_claude(
    prompt: str,
    system_prompt: str,
    max_tokens: int = 2048,
) -> str:
    """
    Central wrapper for all synchronous Claude API calls.
    Logs prompt length for monitoring. Handles errors gracefully.
    """
    import anthropic
    import os

    # API key loaded from environment — never hardcoded
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

    client = anthropic.Anthropic(api_key=api_key)
    logger.info("Claude API call initiated", extra={"prompt_length": len(prompt)})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text if response.content and response.content[0].type == "text" else ""


async def stream_claude(
    prompt: str,
    system_prompt: str,
    max_tokens: int = 2048,
) -> AsyncGenerator[str, None]:
    """
    Streaming wrapper for Claude API calls.
    Powers the typewriter effect in the frontend UI.
    """
    import anthropic
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

    client = anthropic.Anthropic(api_key=api_key)

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
