"""
Base tool interface for all tools in the system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        Return the tool parameters in JSON Schema format.

        Returns:
            Dictionary with JSON Schema describing the tool parameters
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given arguments.

        Args:
            **kwargs: Tool-specific arguments

        Returns:
            Dictionary with tool execution result
        """
        pass

    def to_openai_definition(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI function calling format.

        Returns:
            Dictionary in OpenAI function format
        """
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
