
# This script explains basics how LLM model is used to decide on tools

import json
from typing import Any, Dict, Literal, Optional

from openai import OpenAI
from pydantic import BaseModel, ValidationError, Field


# This script demonstrates how to prompt a language model to decide which tool (function) should be used based on a user query. The model assesses the user's message, selects the most appropriate tool, and outputs its choice in a structured JSON format.

# Initialize the OpenAI client for local LLM inference
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  
)

# Define the model to use
MODEL = "qwen2.5-coder:3b"

# Define the tool call schema
# This schema defines the structure of the tool call JSON that the model will output.
# It includes the tool name, its arguments, and a final answer if no tool is needed.
# This is used to validate the model's output.

class ToolCall(BaseModel):
    tool: Literal["count_o", "add", "none"] # tool name literal values count_o, add, none
    args: Dict[str, Any] = Field(default_factory=dict) # tool arguments dictionary
    # Dict[str, Any] is a dictionary with string keys and any values
    # Field(default_factory=dict) is a field that is a dictionary with string keys and any values
    # default_factory=dict is a default factory that returns a dictionary with string keys and any values
    # Optional[str] is an optional string   
    final: Optional[str] = None  # final answer if no tool is needed

# Define the system prompt
# This prompt is used to guide the model's behavior.
# It tells the model that it is a tool-using assistant and that it must respond with ONLY valid JSON (no markdown, no explanation).
# It also defines the schema for the tool call JSON that the model will output.

# here we are saying to follow strcit json and providing format of json that model will output
# and we are also providing available tools and their signatures
# which will help model to create argument properly

# extra curly braces are used to escape the curly braces in the json string
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

# Define the function to get the tool decision
# This function takes a user message and returns a ToolCall object.
# It uses the OpenAI client to call the model and get the response.
# It then validates the response and returns a ToolCall object.
# If the response is not valid JSON, it raises an error.

# ToolCall.model_validate is going to validate the response returned by model
# it is going to use ToolCall schema to validate the response which we defined above
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
        # data is a dictionary with string keys and any values
        # which is returned by model
        # we are going to validate the data using ToolCall schema
        # which we defined above
        print("data: ", data)
        return ToolCall.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise RuntimeError(f"Model did not return valid tool JSON.\nRaw:\n{text}\n\nError:\n{e}") from e



# We haven't yet written these functions, we are just checking LLMs output if it can 
# understand the question and response properly with proper tool/function selection and right arguments

get_tool_decision("Count how many O's are in this sentence: 'Hello, World!'")

# it provides following output
# data:  {'tool': 'count_o', 'args': {'text': 'Hello, World!'}}
# which looks perfact as it is using right tool/function and also passing write arguments

get_tool_decision("What is sum of 19 and 23? ")

# it provides following output 
# data:  {'tool': 'add', 'args': {'a': 19, 'b': 23}}
# which looks perfact as it is using right tool/function and also passing write arguments
# look at args here, it is following add(a: number, b: number) -> number which we provided in system prompt

# now for next step move to 2-view-model-selection.py