import asyncio
from codecs import raw_unicode_escape_decode
import json

import re
from typing import Any, Dict, Optional

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ollama OpenAI-compatible client
llm = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "qwen2.5-coder:3b"


# this pydantic tool class make sure that model calls tool with following
# tool --> it should be a string , in this case it will be sql_query
# args --> it tells it will be dict with key as string and value could be Any

class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)
    final: Optional[str] = None


# system prompt asking model to following a proper json format
SYSTEM = """
You are a tool-using assistant.
Return ONLY valid JSON (no markdown, no explanation, no ``` fences).

If you will call sql_query, first call db_schema to learn valid table/column names, then generate SQL using only those names.

If you need a tool:
{"tool":"<tool_name>","args":{...}}

If no tool needed:
{"tool":"none","final":"..."}
"""

# some model returns values in this style ```json { ... } ``` and those needs to be removed and following
# function is made for that purpose 

def extract_json_object(text: str) -> dict:
    """
    Robustly extract a JSON object from model output.
    Handles ```json fences and extra text before/after.
    """
    text = text.strip()

    # If fenced like ```json { ... } ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if m:
        text = m.group(1).strip()

    # Otherwise, grab the first {...} block
    m = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if m:
        text = m.group(1).strip()

    return json.loads(text)

# now this is the main thing here, so far we haven't used async in front of tools or functions when we were calling functions without MCP
# but now you can see functions having aysnc in front of them


async def main():
    # Start MCP server as a subprocess via stdio
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-2-mcp-sqlite-server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from MCP
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print("tool names", tool_names)


            schema_res = await session.call_tool("db_schema", {})

            # Most MCP servers return JSON as text content
            schema_text_raw = schema_res.content[0].text
            schema = json.loads(schema_text_raw)

            schema_text = json.dumps(schema, indent=2)

            # user_msg = "Find products sold till date. Return product_name, total_qty_sold, total_sales_amount."
            user_msg = f"""
                You MUST use only these tables/columns (SQLite):
                {schema_text}

                Now write ONE SQLite SELECT query to answer:
                Find products sold till date (qty and sales amount).
                """

            # Give the tool list to the LLM
            prompt = (
                SYSTEM
                + "\nAvailable tools:\n- "
                + "\n- ".join(tool_names)
                + "\n\nIf using sql_query, pass args: {\"query\": \"<SQL>\"}."
            )

            resp = llm.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0,
            )

            raw = resp.choices[0].message.content.strip()
            # print("raw", raw)
            try:
                # call = ToolCall.model_validate(json.loads(raw))
                call = ToolCall.model_validate(extract_json_object(raw))

            except (json.JSONDecodeError, ValidationError) as e:
                raise RuntimeError(f"Bad JSON from model:\n{raw}\n\n{e}")

            # print("call", call)
            if call.tool == "none":
                print(call.final)
                return

            # Call MCP tool
            tool_result = await session.call_tool(call.tool, call.args)

            # Ask LLM to summarize results
            resp2 = llm.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "user", "content": f"Here are tool results:\n{tool_result}\nSummarize neatly."}
                ],
                temperature=0,
            )
            print(resp2.choices[0].message.content)

if __name__ == "__main__":
    asyncio.run(main())
