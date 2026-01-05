import asyncio
import json
import re
import ollama
from pydantic import BaseModel, Field, ValidationError
# Import Client directly from fastmcp
from fastmcp import Client 

# 1. Define Pydantic models for strict validation
class MathResult(BaseModel):
    addition_result: float = Field(description="The result of adding the two numbers.")
    character_count: int = Field(description="The count of characters in the specified string.")
    explanation: str = Field(description="Brief note of what was done.")

async def run_client_poc():
    # 2. Connect to your local HTTP MCP server (ensure server.py is running)
    # FastMCP Client automatically handles the SSE/HTTP transport inference
    async with Client("http://localhost:8000/sse") as mcp_client:
        # Fetch tool definitions
        mcp_tools = await mcp_client.list_tools()
        
        # Format tools for Ollama
        ollama_tools = [
            {
                'type': 'function',
                'function': {
                    'name': t.name,
                    'description': t.description,
                    'parameters': t.inputSchema
                }
            } for t in mcp_tools
        ]
        # print("ollama_tools", ollama_tools)
        # 3. Define the system prompt - encourage tool usage first
        system_prompt_tool_selection = (
            "You are a helpful assistant with access to tools. "
            "When the user asks you to perform calculations or operations, you MUST use the available tools. "
            "Do not try to calculate or answer directly - use the tools provided."
        )
        
        # Final output prompt - interpret tool results and provide natural response
        system_prompt_final = (
            "You are a helpful assistant. Use the tool results provided to answer the user's question. "
            "Provide a clear, natural English response based on the tool execution results."
        )

        user_input = "Add 123 and 456, then count the characters in 'Vishwas'."

        # 4. Model selects tools
        response = ollama.chat(
            model='qwen2.5-coder:3b',
            messages=[
                {'role': 'system', 'content': system_prompt_tool_selection},
                {'role': 'user', 'content': user_input}
            ],
            tools=ollama_tools
        )
        
        # Extract content from response (handle both object and dict formats)
        if isinstance(response, dict):
            content = response.get('message', {}).get('content', '')
        else:
            content = response.message.content if hasattr(response.message, 'content') else ''
        
        print("Response content:", content)
        
        # 5. Simple approach: Find ALL JSON objects in the response and extract tool calls
        tool_calls = []
        
        # Use brace matching to find all complete JSON objects in the raw content
        # This works regardless of markdown formatting, newlines, etc.
        brace_start = -1
        brace_count = 0
        for i, char in enumerate(content):
            if char == '{':
                if brace_count == 0:
                    brace_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and brace_start != -1:
                    # Found a complete JSON object
                    json_str = content[brace_start:i+1]
                    try:
                        tool_data = json.loads(json_str)
                        # If it has a 'name' field, it's a tool call
                        if isinstance(tool_data, dict) and 'name' in tool_data:
                            tool_calls.append(tool_data)
                            print(f"Found tool call: {tool_data.get('name')} with args: {tool_data.get('arguments')}")
                    except json.JSONDecodeError:
                        # Not valid JSON, skip it
                        pass
                    brace_start = -1
        
        print(f"Total tool calls found: {len(tool_calls)}")
        print("Parsed tool_calls:", tool_calls)
        
        # 6. Execute tool calls
        if tool_calls:
            tool_results = {}
            for tool_call in tool_calls:
                name = tool_call.get('name') if isinstance(tool_call, dict) else tool_call.name
                args = tool_call.get('arguments') if isinstance(tool_call, dict) else tool_call.arguments
                
                print(f"Calling tool: {name} with args: {args}")
                
                # Execute tool via MCP
                result = await mcp_client.call_tool(name, args)
                # Handle result content correctly
                if hasattr(result, 'content') and result.content:
                    tool_results[name] = result.content[0].text if isinstance(result.content, list) and len(result.content) > 0 else str(result.content)
                else:
                    tool_results[name] = str(result)
            
            print("Tool results:", tool_results)
            
            # 7. Final call - interpret tool results and provide natural response
            final_response = ollama.chat(
                model='qwen2.5-coder:3b',
                messages=[
                    {'role': 'system', 'content': system_prompt_final},
                    {'role': 'user', 'content': user_input},
                    {'role': 'assistant', 'content': content},  # Tool calls made
                    {'role': 'tool', 'content': json.dumps(tool_results)}  # Tool results
                ]
            )
            
            # 8. Display the final response
            if isinstance(final_response, dict):
                final_content = final_response.get('message', {}).get('content', '').strip()
            else:
                final_content = final_response.message.content.strip() if hasattr(final_response.message, 'content') else ''
            
            print("\n--- Final Response ---")
            print(final_content)
        else:
            print("No tool calls found in response content")
            print(f"Content was: {content}")

if __name__ == "__main__":
    asyncio.run(run_client_poc())
