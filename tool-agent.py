# detailed comments and description of this code you can find in 

# 1-model-selects-tool.py
# 2-view-model-tool-selection.py
# 3-call-tool.py
# 4-result-back-to-LLM.py

# This file brings everything together in production ready mode
# there are few new things here where I added comments, you can find that in later part of this file 

import json
from typing import Any, Dict, Literal, Optional

from openai import OpenAI
from pydantic import BaseModel, ValidationError, Field


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  
)

MODEL = "qwen2.5-coder:3b"


def count_o(text: str) -> int:
    """Count letter 'o' or 'O' in the given text."""
    return sum(1 for ch in text if ch.lower() == "o")

def add(a: float, b: float) -> float:
    return a + b


TOOLS = {
    "count_o": count_o,
    "add": add,
}


# --------- 3) Define the ONLY JSON format the model is allowed to output ----------
class ToolCall(BaseModel):
    tool: Literal["count_o", "add", "none"]
    args: Dict[str, Any] = Field(default_factory=dict)
    final: Optional[str] = None  # used only if tool == "none"


SYSTEM = f"""
You are a tool-using assistant.

You MUST respond with ONLY valid JSON (no markdown, no explanation).
Schema:
- If you want to call a tool:
  {{"tool":"<tool_name>","args":{{...}}}}
- If no tool is needed:
  {{"tool":"none","final":"<your answer>"}}

Available tools:
1) count_o(text: string) -> integer
2) add(a: number, b: number) -> number
"""


def get_tool_decision(user_msg: str) -> ToolCall:
    """Ask the model whether to call a tool. Enforce strict JSON output."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        temperature=0,
    )
    text = resp.choices[0].message.content.strip()

    try:
        data = json.loads(text)
        print("data: ", data)
        return ToolCall.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise RuntimeError(f"Model did not return valid tool JSON.\nRaw:\n{text}\n\nError:\n{e}") from e


def execute_tool(call: ToolCall) -> Any:
    """Run the selected tool locally."""
    if call.tool == "none":
        return call.final

    fn = TOOLS[call.tool]
    return fn(**call.args)


def get_final_answer(user_msg: str, call_json: str, tool_result: Any) -> str:
    """Ask the model to produce the final user-facing response using tool result."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Use the tool result to answer."},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": call_json},
            {"role": "user", "content": f"Tool result: {tool_result}\nNow answer clearly in 1-3 sentences."},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def run(user_msg: str) -> str:
    call = get_tool_decision(user_msg)
    call_json = call.model_dump_json()
    result = execute_tool(call)

    # If tool == none, result already is the final answer
    if call.tool == "none":
        return str(result)

    return get_final_answer(user_msg, call_json, result)


if __name__ == "__main__":
    print(run("Count how many O's are in this sentence: 'Hello, World!'"))
    print(run("What is 19 + 23? Use the add tool."))

    # here we are asking a question which is neither related with counting nor related with addition 
    # this demonstrates that model still can answer question without tools also, but will call tool whenver users ask question that should be answered by the tool

    print(run("What is the capital of USA"))
