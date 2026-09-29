from fastmcp import FastMCP
from servers.openapi_specification.tools.openapi_actions import openapi_actions_server

openapi_server = FastMCP(name='OpenAPI Server')


async def setup_openapi_actions_server():
    await openapi_server.import_server(server=openapi_actions_server)


