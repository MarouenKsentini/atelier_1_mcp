import asyncio
import os

from fastmcp import FastMCP
from tools import (
    articles_tools,
    clients_tools,
    analyse_reglements_tools,
    analyse_clients_tools,
)

mcp_server = FastMCP("Facturation Server")

mcp_server.mount(articles_tools.mcp)
mcp_server.mount(clients_tools.mcp)
mcp_server.mount(analyse_reglements_tools.mcp)
mcp_server.mount(analyse_clients_tools.mcp)
# On some fastmcp versions the older name is import_server(...)


async def main():
    await mcp_server.run_async(
        transport="streamable-http",
        host=os.getenv("MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("MCP_PORT", "8000")),
        path="/mcp",
    )


if __name__ == "__main__":
    asyncio.run(main())