
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





# here we are getting return from ToolCall.model_validate which is used in get_tool_decition function
call =get_tool_decision("Count how many O's are in this sentence: 'Hello, World!'")
# we are converting it into json format
call_json = call.model_dump_json()
call2 = get_tool_decision("What is sum of 19 and 23? ")
call2_json = call2.model_dump_json()

print("call_json: ", call_json)

# the output of this looks like following 
# call_json:  {"tool":"count_o","args":{"text":"Hello, World!"},"final":null}
# We can see here one extra "final":null, which was actully not model output as we have seen in 1-model-tool-selection.py
# this is the beauty of pydantic validation, it will always complete schema as per its definition

print("call2_json: ", call2_json)

# the output of this looks like following
# call2_json:  {"tool":"add","args":{"a":19,"b":23},"final":null}
# We can see here one extra "final":null, which was actully not model output as we have seen in 1-model-tool-selection.py
# this is the beauty of pydantic validation, it will always complete schema as per its definition

# now for next step move to 3-call-tool.py