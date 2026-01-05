import sqlite3
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sqlite-tools")  # FastMCP auto-builds tool schemas from type hints/docstrings. :contentReference[oaicite:1]{index=1}

DB_PATH = "store.db"

def _is_read_only(sql: str) -> bool:
    forbidden = ["insert", "update", "delete", "drop", "alter", "create", "replace", "truncate", "attach", "pragma"]
    s = sql.strip().lower()
    return s.startswith("select") and not any(k in s for k in forbidden)

@mcp.tool()
def db_schema() -> dict:
    """
    Return database schema: tables and their columns.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cur.fetchall()]

    schema = {}
    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        schema[t] = [{"name": row[1], "type": row[2]} for row in cur.fetchall()]

    conn.close()
    print("schema", schema)
    return schema


@mcp.tool()
def sql_query(query: str) -> List[Dict[str, Any]]:
    """
    Execute a READ-ONLY SQL query against the local SQLite database.
    Input:
      query: SQL SELECT statement (read-only).
    Output:
      List of rows as JSON objects.
    """
    if not _is_read_only(query):
        raise ValueError("Only read-only SELECT queries are allowed.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    # Run over stdio (how Cursor and many clients connect)
    mcp.run()
