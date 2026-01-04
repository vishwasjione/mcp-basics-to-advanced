# mcp-basics-to-advanced
This repo helps AI developers in learning about MCP and how to develop AI application using MCP, we will not use any API as such and entire execution will happen in local computer so developers won't have worry about API keys and cost of using an LLM.

Before we start using MCP, we will do same stuff without using MCP i.e. coding all kinds of tools in the same file or code base where LLM is also configured.
This will explain why MCP is needed and then we will swtich to doing same thing using MCP.

but before we do that we will have to setup the local envrionment, please follow following steps to set it up

1.  Install ollama


```bash
curl -fsSL https://ollama.com/install.sh | sh
```

We are using Ollama but you can using other model providers as well

2. Start Ollama 

```bash
ollama serve
```

it wills start the server which you can use in your code for calling model

3. download model 

```bash
ollama run qwen2.5-coder:3b
```
it will start command prompt and you can ask simple questions to make sure, ollama in local is working fine.

4. Open cursor or vs code and open terminal and install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

5. Create  virutal environment 

```bash
uv venv .venv
```
activate it 

```bash
source .venv/bin/activate
```


6. Intall openai

```bash
uv pip install openai
```

7. Check installed libs

```bash
up pip list
```

mine look like following 

| Package           | Version        |
|-------------------|---------------|
| annotated-types   | 0.7.0         |
| anyio             | 4.12.0        |
| certifi           | 2025.11.12    |
| distro            | 1.9.0         |
| h11               | 0.16.0        |
| httpcore          | 1.0.9         |
| httpx             | 0.28.1        |
| idna              | 3.11          |
| jiter             | 0.12.0        |
| numpy             | 2.4.0         |
| openai            | 2.14.0        |
| pandas            | 2.3.3         |
| pydantic          | 2.12.5        |
| pydantic-core     | 2.41.5        |
| python-dateutil   | 2.9.0.post0   |
| pytz              | 2025.2        |
| six               | 1.17.0        |
| sniffio           | 1.3.1         |
| tqdm              | 4.67.1        |
| typing-extensions | 4.15.0        |
| typing-inspection | 0.4.2         |
| tzdata            | 2025.3        |

Note :- In case of any setup error you can always take help of google/llms to fix the error

8.  IDE to use venv

Configure IDE so that it uses the venv you just created


# Step by step calling tool (first without MCP)


- **1-model-selects-tool.py**:  
  This file demonstrates how to prompt a language model to decide which tool (function) should be used based on a user query. The model assesses the user's message, selects the most appropriate tool, and outputs its choice in a structured JSON format.

- **2-view-model-tool-selection.py**:  
  This script allows you to inspect how the model makes tool selection decisions. It runs queries and displays the model's JSON response that indicates which tool should be called and with what arguments. This is useful for understanding and debugging the tool selection process.

- **3-call-tool.py**:  
  Here, the model's tool-selection JSON is used to directly call Python functions. The script parses the model's output, maps the selected tool name to a Python function, runs it with the parsed arguments, and prints the result. It also handles cases where the model doesn't select a tool and just provides a final answer directly.
  
- **4-result-back-to-LLM.py**:  
  This script expands the tool-calling pipeline by not only having the model select and call a tool, but also sending the tool's result back to the model to synthesize a final user-facing answer. The workflow includes:
  
  1. The user asks a question.
  2. The model is prompted to return a JSON object indicating which tool (if any) to use, plus its arguments.
  3. The tool is executed according to this JSON, and the output is obtained.
  4. This tool output, alongside the original user query and model's tool-selection JSON, are given back to the model.
  5. The model is then asked to generate a final, conversational answer based on the tool result.

  In this way, the model not only orchestrates tool use, but also "post-processes" the outcome to produce a clear, helpful final response for the end user. The script demonstrates the full closed-loop cycle from user prompt → model tool selection → tool execution → model-formulated answer.

Together, these files exemplify how to build, debug, and integrate LLM-controlled tool use in Python applications.

- **tool-agent.py**:  
  This script provides a complete, production-style implementation that combines all steps from the above example scripts. It serves as an "all-in-one" agent for tool use powered by an LLM and integrates:

  1. **Tool selection**: The model receives the user query and returns structured JSON indicating which tool to use (or whether to answer directly).
  2. **Tool execution**: The chosen Python function is executed with the arguments extracted from the model's response.
  3. **Final answer synthesis**: If a tool was called, the result is returned to the model, which produces a final clear, conversational answer for the user.

  The script exposes a single `run(user_msg)` function for end-to-end processing of any user question, handling all the orchestration internally. Example usage (when run as `python tool-agent.py`) shows how it answers user questions, delegates to tools, and combines the results using the model. This file is intended as the recommended interface for tool-using LLMs, where the earlier example files are primarily didactic and incremental in nature.
