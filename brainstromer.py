"""
Brainstormer.py

This module provides a class for brainstorming ideas based on a given prompt.
#     the last message in the conversation. If the last message is a response to a brainstorming prompt,
#     the Brainstormer will generate a list of related ideas or suggestions.
#     otherwise, it will return an empty string.
It defines a `Brainstormer` class that can be used to generate ideas based on a prompt.
    The class includes methods for adding new ideas, retrieving existing ideas, and clearing all ideas.
"""

from typing import (
    TypedDict,                      # define the structure of our agent state
    Annotated,                      # message type annotations, eg a message can be type of email or number be a phone number or postal code.
    Sequence,                       # defining sequences of messages, To automatically handle the state updates for sequences such as by adding new messages to a chat history.
)
from langchain_core.messages import (
    HumanMessage,                   # defining human messages in the chat
    BaseMessage,                    # defining the base message type, including common attributes for all messages
    SystemMessage,                  # defining the system message type, # which can be used to set the context or instructions for the agent
    AIMessage,                      # defining AI messages in the chat
    ToolMessage,                    # defining tool messages in the chat
)
from langgraph.graph.message import (
    add_messages,                   # Importing add_messages to automatically handle the state updates for sequences such as by adding new messages to a chat history   
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import (
    StateGraph,
    END,
)  # Importing necessary components from LangGraph for state management and graph compilation
from langgraph.graph.state import (
    CompiledStateGraph,             # Importing CompiledStateGraph to compile the state graph into an executable agent
)
from langgraph.prebuilt import (
    ToolNode,                       # Importing ToolNode to handle tool calls within the graph
)
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file


discussion_content : str = ""


