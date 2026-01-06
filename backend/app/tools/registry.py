"""
Tool registry for managing and executing tools.
"""
from typing import Dict, Any, List, Optional
from .base import BaseTool
from ..utils.logger import logger
from ..utils.exceptions import ToolException


class ToolRegistry:
    """
    Registry for managing all available tools.
    """

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        logger.info("Tool registry initialized")

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register

        Raises:
            ToolException: If tool with same name already exists
        """
        if tool.name in self._tools:
            raise ToolException(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def get_all_definitions(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI function definitions for all registered tools.

        Returns:
            List of tool definitions in OpenAI format
        """
        return [tool.to_openai_definition() for tool in self._tools.values()]

    async def execute(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Dictionary with execution result
        """
        tool = self.get_tool(name)

        if not tool:
            logger.error(f"Tool not found: {name}")
            return {
                "success": False,
                "error": f"Tool '{name}' not found",
                "fallback": "I'm sorry, I don't have access to that capability right now."
            }

        try:
            logger.info(f"Executing tool '{name}' with arguments: {arguments}")
            result = await tool.execute(**arguments)
            logger.info(f"Tool '{name}' executed successfully")
            return result

        except Exception as e:
            logger.error(f"Tool '{name}' execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "fallback": f"I encountered an error while trying to {name.replace('_', ' ')}. Please try again."
            }

    @property
    def tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())

    @property
    def tool_count(self) -> int:
        """Get count of registered tools."""
        return len(self._tools)


# Global tool registry instance
tool_registry = ToolRegistry()


def setup_tools() -> ToolRegistry:
    """
    Set up and register all available tools.

    Returns:
        Configured tool registry
    """
    from .web_search import WebSearchTool

    # Register tools
    tool_registry.register(WebSearchTool())

    logger.info(f"Registered {tool_registry.tool_count} tools: {tool_registry.tool_names}")
    return tool_registry
