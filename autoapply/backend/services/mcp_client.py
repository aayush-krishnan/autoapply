import asyncio
import logging
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("autoapply.mcp")

class MCPClientService:
    """
    Service for interacting with Model Context Protocol (MCP) servers.
    Provides a standardized way to call tools for job searching and other services.
    """
    
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self._session: Optional[ClientSession] = None
        self._client_context = None

    async def _get_session(self) -> ClientSession:
        """Initialize and return the client session."""
        if self._session:
            return self._session
            
        logger.info(f"Connecting to MCP server: {' '.join(self.server_params.command)}")
        self._client_context = stdio_client(self.server_params)
        read, write = await self._client_context.__aenter__()
        self._session = ClientSession(read, write)
        await self._session.__aenter__()
        await self._session.initialize()
        return self._session

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool on the MCP server."""
        session = await self._get_session()
        try:
            logger.info(f"Calling MCP tool '{tool_name}' with args: {arguments}")
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling MCP tool '{tool_name}': {e}")
            raise
            
    async def list_tools(self) -> List[Any]:
        """List available tools on the MCP server."""
        session = await self._get_session()
        result = await session.list_tools()
        return result.tools

    async def close(self):
        """Close the MCP connection."""
        if self._session:
            await self._session.__aexit__(None, None, None)
            self._session = None
        if self._client_context:
            await self._client_context.__aexit__(None, None, None)
            self._client_context = None

# Factory and global instances can be managed based on config
mcp_client_instances: Dict[str, MCPClientService] = {}

async def get_mcp_client(name: str, command: List[str], args: List[str] = []) -> MCPClientService:
    """Helper to get or create an MCP client instance by name."""
    if name not in mcp_client_instances:
        params = StdioServerParameters(command=command[0], args=command[1:] + args)
        mcp_client_instances[name] = MCPClientService(params)
    return mcp_client_instances[name]
