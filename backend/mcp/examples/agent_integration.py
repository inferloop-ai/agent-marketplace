"""
Example of integrating MCP server with an AI agent.

This example demonstrates how to use the MCP server to manage context for an AI agent,
including creating, updating, and retrieving context during a conversation.
"""

import asyncio
from datetime import datetime
from mcp.client import MCPClient
from typing import Dict, Any


class ChatAgent:
    """A simple chat agent that uses MCP for context management."""
    
    def __init__(self, agent_id: str, agent_type: str = "chat"):
        """Initialize the chat agent.
        
        Args:
            agent_id: Unique identifier for this agent
            agent_type: Type of the agent (default: "chat")
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.client = MCPClient()
        self.current_context_id: str = None
        
    async def start_conversation(self, user_id: str) -> str:
        """Start a new conversation and create initial context.
        
        Args:
            user_id: ID of the user starting the conversation
            
        Returns:
            str: The context ID for this conversation
        """
        # Create initial context
        initial_context = {
            "user_id": user_id,
            "conversation_history": [],
            "user_preferences": {},
            "session_start": datetime.utcnow().isoformat()
        }
        
        context = await self.client.create_context(
            data=initial_context,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            tags=["conversation", "active"],
            description=f"New conversation with user {user_id}"
        )
        
        self.current_context_id = context.id
        return context.id
    
    async def process_message(self, message: str) -> str:
        """Process a message in the conversation.
        
        Args:
            message: The user's message
            
        Returns:
            str: The agent's response
        """
        if not self.current_context_id:
            raise ValueError("No active conversation context")
        
        # Get current context
        context = await self.client.get_context(self.current_context_id)
        
        # Update conversation history
        history = context.data.content["conversation_history"]
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "role": "user",
            "content": message
        })
        
        # Generate response (in a real implementation, this would use an LLM)
        response = self._generate_response(message, context)
        
        # Update context with new history and response
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "role": "assistant",
            "content": response
        })
        
        await self.client.update_context(
            self.current_context_id,
            data={
                "conversation_history": history,
                "last_message": message,
                "last_response": response
            },
            tags=["conversation", "active"],
            description="Updated conversation history"
        )
        
        return response
    
    def _generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate a response based on the message and context.
        
        Args:
            message: The user's message
            context: Current conversation context
            
        Returns:
            str: The agent's response
        """
        # In a real implementation, this would use an LLM
        # Here we just echo the message with a friendly greeting
        return f"Echo: {message}"
    
    async def end_conversation(self) -> None:
        """End the current conversation and update context status."""
        if self.current_context_id:
            await self.client.update_context(
                self.current_context_id,
                tags=["conversation", "completed"],
                description="Conversation ended"
            )
            self.current_context_id = None

async def main():
    """Example usage of the ChatAgent."""
    # Initialize agent
    agent = ChatAgent(agent_id="chat-agent-1")
    
    try:
        # Start conversation
        print("Starting conversation...")
        context_id = await agent.start_conversation(user_id="user-123")
        print(f"Conversation started with context ID: {context_id}")
        
        # Process messages
        messages = [
            "Hello, how are you?",
            "What can you do?",
            "Goodbye"
        ]
        
        for message in messages:
            print(f"\nUser: {message}")
            response = await agent.process_message(message)
            print(f"Agent: {response}")
        
    finally:
        # End conversation
        print("\nEnding conversation...")
        await agent.end_conversation()

if __name__ == "__main__":
    asyncio.run(main())
