import asyncio
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession

SERVER_URL = "https://mcp.deepwiki.com/mcp"

async def main():
    async with streamable_http_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("\n=== Tools ===")
            for t in tools.tools:
                print("-", t.name)

            # Try a tool call
            res = await session.call_tool(
                "ask_question",
                {
                    "repoName": "modelcontextprotocol/python-sdk",
                    "question": "What tools and transports does this SDK support?"
                }
            )

            print("\n=== Answer ===")
            for item in res.content:
                if hasattr(item, "text") and item.text:
                    print(item.text)

if __name__ == "__main__":
    asyncio.run(main())
