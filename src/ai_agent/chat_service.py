"""
Chat service module for handling AI agent interactions.
"""

import json
import logging
from uuid import uuid4
from typing import Dict, Any, List

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from ai_agent import get_agent

# Configure logging
logger = logging.getLogger(__name__)


class ChatService:
    """
    Service class to handle AI agent chat operations.
    """

    def __init__(self):
        """Initialize the chat service with a fresh checkpointer and agent."""
        self.checkpointer = InMemorySaver()
        self.agent = get_agent(self.checkpointer)

    def process_chat(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """
        Process chat input and return agent response.

        Args:
            user_input: The user's message
            user_id: The ID of the user

        Returns:
            Dictionary containing processed tool messages

        Raises:
            ValueError: If user_input is empty
            Exception: For any other processing errors
        """
        if not user_input or not user_input.strip():
            raise ValueError("Message cannot be empty")

        config = {
            "configurable": {
                "created_by": user_id,
                "thread_id": str(uuid4())
            }
        }

        logger.info(f"Processing chat for user {user_id}")

        try:
            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config
            )

            tool_messages = self._extract_tool_messages(response["messages"])
            logger.info(f"Successfully processed chat for user {user_id}")

            return {"data": tool_messages}

        except Exception as e:
            logger.error(f"Error processing chat for user {user_id}: {str(e)}")
            raise

    def _extract_tool_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """
        Extract and format tool messages from agent response.

        Args:
            messages: List of messages from agent response

        Returns:
            List of formatted tool message dictionaries
        """
        tool_messages = []

        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_message = {
                    "content": self._parse_content(msg.content),
                    "name": msg.name,
                    "status": getattr(msg, "status", None),
                    "tool_call_id": getattr(msg, "tool_call_id", None),
                }
                tool_messages.append(tool_message)

        return tool_messages

    @staticmethod
    def _parse_content(content: Any) -> Any:
        """
        Parse content, attempting JSON deserialization if it's a string.

        Args:
            content: Content to parse

        Returns:
            Parsed content (JSON object if valid JSON string, otherwise original content)
        """
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
        return content


class ChatServiceFactory:
    """
    Factory class for creating ChatService instances.
    Useful for dependency injection and testing.
    """

    @staticmethod
    def create_service() -> ChatService:
        """
        Create a new ChatService instance.

        Returns:
            A new ChatService instance
        """
        return ChatService()

    @staticmethod
    def create_service_with_custom_agent(agent_factory_func) -> ChatService:
        """
        Create a ChatService with a custom agent factory function.
        Useful for testing or different agent configurations.

        Args:
            agent_factory_func: Function that takes a checkpointer and returns an agent

        Returns:
            A new ChatService instance with custom agent
        """
        service = ChatService.__new__(ChatService)
        service.checkpointer = InMemorySaver()
        service.agent = agent_factory_func(service.checkpointer)
        return service
