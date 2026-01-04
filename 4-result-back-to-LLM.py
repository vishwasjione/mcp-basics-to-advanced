# complete description of this code is available in 1-model-selects-tool.py
# I will add description/comments to the new lines added to this py file , you can find those at the end of this file




import json
from typing import Any, Dict, Literal, Optional

from openai import OpenAI
from pydantic import BaseModel, ValidationError, Field


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  
)

MODEL = "qwen2.5-coder:3b"


class ToolCall(BaseModel):
    tool: Literal["count_o", "add", "none"]
    args: Dict[str, Any] = Field(default_factory=dict)
    final: Optional[str] = None  


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
        # print("data: ", data)
        return ToolCall.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise RuntimeError(f"Model did not return valid tool JSON.\nRaw:\n{text}\n\nError:\n{e}") from e

def count_o(text: str) -> int:
    return sum(1 for ch in text if ch.lower() == "o")

def add(a: float, b: float) -> float:
    return a + b

# This is a second call to model, first call gave us output which helped us with tool/functoin selection
# and we used that to call the right functions/tools and got results
# now we are calling the model again providing the result of those tool calls 
# we are giving the context again like system prompbt and user prompt 

# one extra thing we doing is here using "assistant" prompt which reminds model what he returned earlire
# this creates a chain kind of thing and model can remember what it delivered earlire and this in continuation of the same

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

TOOLS = {
    "count_o": count_o,
    "add": add,
}



call =get_tool_decision("Count how many O's are in this sentence: 'Hello, World!'")
call_json = call.model_dump_json()

fn = TOOLS[call.tool]
result = fn(**call.args)

print("result: ", result)

# calling the model again and providing following inputs
# original question that was asked 
# output that model earlire provided
# output of the tool calls 

model_response = get_final_answer("Count how many O's are in this sentence: 'Hello, World!'", call_json, result)
print("model_response: ", model_response)


call = get_tool_decision("What is sum of 19 and 23? ")
call_json = call.model_dump_json()


fn = TOOLS[call.tool]
result = fn(**call.args)

print("result: ", result)

# calling the model again and providing following inputs
# original question that was asked 
# output that model earlire provided
# output of the tool calls 

model_response = get_final_answer("What is sum of 19 and 23? ", call_json, result)
print("model_response: ", model_response)


