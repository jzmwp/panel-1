"""Claude API client with streaming tool-use for mine data queries."""

import json
import logging
from typing import AsyncGenerator

import anthropic

from backend.config import settings
from backend.ai.tools import TOOLS
from backend.ai.prompts import SYSTEM_PROMPT
from backend.services.query_builder import execute_query, get_schema_info
from backend.services.chart_service import generate_chart

logger = logging.getLogger(__name__)


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _handle_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool call and return the result."""
    if tool_name == "query_database":
        return execute_query(tool_input["sql"], tool_input.get("max_rows", 100))

    elif tool_name == "get_schema_info":
        return get_schema_info(tool_input.get("table_name"))

    elif tool_name == "get_recent_reports_summary":
        days = tool_input.get("days", 7)
        sql = f"""
            SELECT report_type, COUNT(*) as count,
                   MIN(report_date) as earliest, MAX(report_date) as latest
            FROM reports
            WHERE report_date >= date('now', '-{days} days')
            GROUP BY report_type
            ORDER BY count DESC
        """
        return execute_query(sql)

    elif tool_name == "generate_chart":
        return generate_chart(tool_input)

    return {"error": f"Unknown tool: {tool_name}"}


async def chat_with_tools(
    user_message: str,
    conversation_history: list[dict],
) -> AsyncGenerator[dict, None]:
    """Send a message to Claude with streaming tool-use, yielding tokens as they arrive."""
    client = get_client()

    messages = conversation_history + [{"role": "user", "content": user_message}]

    while True:
        # Stream the response token by token
        collected_content = []  # content blocks for tool-use continuation
        current_tool_name = ""
        current_tool_input_json = ""
        current_tool_id = ""
        has_tool_use = False

        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                if event.type == "content_block_start":
                    block = event.content_block
                    if block.type == "text":
                        pass  # text deltas come via content_block_delta
                    elif block.type == "tool_use":
                        has_tool_use = True
                        current_tool_name = block.name
                        current_tool_id = block.id
                        current_tool_input_json = ""
                        # Let the frontend know we're calling a tool
                        yield {"type": "tool_start", "tool": current_tool_name}

                elif event.type == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta":
                        # Stream each text token to the frontend
                        yield {"type": "text", "content": delta.text}
                    elif delta.type == "input_json_delta":
                        current_tool_input_json += delta.partial_json

                elif event.type == "content_block_stop":
                    pass

            # Get the final message for tool-use continuation
            final_message = stream.get_final_message()

        # If no tool use, we're done
        if final_message.stop_reason != "tool_use":
            break

        # Process tool calls
        assistant_content = final_message.content
        tool_results = []

        for block in assistant_content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                logger.info(f"Tool call: {tool_name}({json.dumps(tool_input)[:200]})")

                # Show the query to the frontend
                if tool_name == "query_database":
                    yield {"type": "tool_use", "tool": tool_name, "query": tool_input.get("sql", "")}

                result = _handle_tool_call(tool_name, tool_input)

                # Yield chart if generated
                if tool_name == "generate_chart" and "image" in result:
                    yield {"type": "chart", "image": result["image"]}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=str),
                })

        # Continue conversation with tool results
        messages.append({"role": "assistant", "content": assistant_content})
        messages.append({"role": "user", "content": tool_results})
        # Loop back to stream the next response
