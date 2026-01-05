from mcp.server.fastmcp import FastMCP

# Pass host and port during initialization instead of .run()
mcp = FastMCP("MyMathTools", host="127.0.0.1", port=8000)

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Adds two numbers and returns the result."""
    return a + b

@mcp.tool()
def count_chars(text: str) -> int:
    """Counts the number of characters in a string."""
    return len(text)

if __name__ == "__main__":
    # .run() now only needs the transport type
    mcp.run(transport="sse")
