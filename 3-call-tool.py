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

# now we are adding too or function, as we want to call the function
# count_o function or tool
def count_o(text: str) -> int:
    return sum(1 for ch in text if ch.lower() == "o")

# now we are adding too or function, as we want to call the function
# add function or tool

def add(a: float, b: float) -> float:
    return a + b


TOOLS = {
    "count_o": count_o,
    "add": add,
}



call =get_tool_decision("Count how many O's are in this sentence: 'Hello, World!'")
call_json = call.model_dump_json()

# if code execution comes to line number 80 above that means model output got validated fine 
# and it has tool/function value as well as proper arguments to call that tool/function

# TOOLS is a dict and it will give literal value as per the key passsed
# and as model output is validated it must be having values like "count_o", "add", "none"
fn = TOOLS[call.tool]

# call the selected tool and pass the arguments
result = fn(**call.args)

# it will show the result of function
print("result: ", result)


call = get_tool_decision("What is sum of 19 and 23? ")
call_json = call.model_dump_json()

# TOOLS is a dict and it will give literal value as per the key passsed
# and as model output is validated it must be having values like "count_o", "add", "none"
fn = TOOLS[call.tool]

# call the selected tool and pass the arguments
result = fn(**call.args)
#result:  2
# this is the result and which looks correct but model needs to take this result and provide answer in proper wording
# so this result is actually context that are providing to use it for crafting answer

# it will show the result of function

print("result: ", result)
#result:  42
# this is the result and which looks correct but model needs to take this result and provide answer in proper wording
# so this result is actually context that are providing to use it for crafting answer


# now you can move to 4-results-back-to-LLM.py which will pass results back to model to prepare for final answer