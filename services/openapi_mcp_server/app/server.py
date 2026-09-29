from fastmcp import FastMCP
import asyncio
from servers.openapi_specification.server import openapi_server, setup_openapi_actions_server



mcp = FastMCP("RT MCP Server for SLDC")

async def setup():
    await setup_openapi_actions_server()

    await mcp.import_server(server=openapi_server,prefix='openapi')

if __name__ == "__main__":
    asyncio.run(setup())
    mcp.run(transport="http", host="0.0.0.0", port=8028)
