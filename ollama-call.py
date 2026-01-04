from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # dummy
)

resp = client.chat.completions.create(
    model="qwen2.5-coder:3b",
    messages=[{"role": "user", "content": "Say hello"}],
)

print(resp.choices[0].message.content)
