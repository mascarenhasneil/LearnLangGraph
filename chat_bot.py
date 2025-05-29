"""
Chatbot Agent with Enhanced Conversational Memory

This module provides a highly interactive chatbot agent that leverages LangChain's 
ChatOpenAI model (GPT-4o) to maintain a conversation history with distinct message types: 
HumanMessage and AIMessage. It utilizes a state graph system to manage conversation flow 
and ensure smooth state transitions during interactions.

Features:
    - Differentiates between human and AI messages using dedicated types.
    - Maintains a complete conversation history to emulate memory across multiple interactions.
    - Employs a state graph-based design for clear abstraction and dynamic conversation management.
    - Utilizes environment configurations via dotenv for secure API key and settings management.
    - Follows best practices for clean, maintainable, and idiomatic Python code.

Main Objectives:
    1. Use structured message types (HumanMessage, AIMessage) for clear participant differentiation.
    2. Retain the full conversation history to provide context-aware responses.
    3. Leverage the GPT-4o model via LangChain's ChatOpenAI for advanced response generation.
    4. Integrate a state graph approach to manage conversation flow and agent memory.
    5. Enhance the agent’s memory capabilities for a more natural and dynamic conversation loop.

Usage:
    Execute this module to start an interactive conversation loop. The agent captures user inputs, 
    generates AI responses, and updates its conversation state dynamically.

Note:
    Ensure all required environment variables are set in a .env file prior to running the module.
"""

from typing import List, TypedDict, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

# Define the agent state with a list of messages.
class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""
    messages: List[Union[HumanMessage, AIMessage]]


# Initialize the ChatOpenAI model with desired configuration.
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.0)


def process(state: AgentState) -> AgentState:
    """Processes the agent's state and generates an AI response.

    Args:
        state: The current state of the agent containing conversation messages.

    Returns:
        The updated agent state with the AI response appended.
    """
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nAI: {response.content}\n")
    print(f"Conversation log: {state['messages']}")
    return state


