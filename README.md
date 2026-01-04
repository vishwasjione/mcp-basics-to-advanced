# mcp-basics-to-advanced
This repo helps AI developers in learning about MCP and how to develop AI application using MCP
The following files illustrate how to use MCP (Model-Controlled Programming) for building a tool-using AI assistant:

- **1-model-selects-tool.py**:  
  This file demonstrates how to prompt a language model to decide which tool (function) should be used based on a user query. The model assesses the user's message, selects the most appropriate tool, and outputs its choice in a structured JSON format.

- **2-view-model-tool-selection.py**:  
  This script allows you to inspect how the model makes tool selection decisions. It runs queries and displays the model's JSON response that indicates which tool should be called and with what arguments. This is useful for understanding and debugging the tool selection process.

- **3-call-tool.py**:  
  Here, the model's tool-selection JSON is used to directly call Python functions. The script parses the model's output, maps the selected tool name to a Python function, runs it with the parsed arguments, and prints the result. It also handles cases where the model doesn't select a tool and just provides a final answer directly.

Together, these files exemplify how to build, debug, and integrate LLM-controlled tool use in Python applications.
