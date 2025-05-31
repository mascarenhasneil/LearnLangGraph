"""
Retrieval-Augmented Generation (RAG) Agent.
This agent uses a retrieval system to fetch relevant documents based on the user's query,
and then generates a response using a language model.

"""

import os
from typing import (
    TypedDict,  # define the structure of our agent state
    Annotated,  # message type annotations, eg a message can be type of email or number be a phone number or postal code.
    Sequence,  # defining sequences of messages, To automatically handle the state updates for sequences such as by adding new messages to a chat history.
)
from langchain_core.messages import (
    HumanMessage,  # defining human messages in the chat
    BaseMessage,  # defining the base message type, including common attributes for all messages
    SystemMessage,  # defining the system message type, # which can be used to set the context or instructions for the agent
    AIMessage,  # defining AI messages in the chat
    ToolMessage,  # defining tool messages in the chat
)
from langchain_openai import (
    ChatOpenAI,  # OpenAI's Chat model for generating responses
    OpenAIEmbeddings,  # Embeddings model for converting text into vector representations
)
from langchain_core.tools import tool
from langgraph.graph import (
    StateGraph,
    END,
)  # Importing necessary components from LangGraph for state management and graph compilation
from langgraph.graph.state import (
    CompiledStateGraph,  # Importing CompiledStateGraph to compile the state graph into an executable agent
)
from operator import (
    add as add_messages,
)  # Importing add_messages to automatically handle the state updates for sequences such as by adding new messages to a chat history
from langchain_community.document_loaders import (
    PypdfLoader,
)  # Importing PypdfLoader to load PDF documents
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)  # Importing RecursiveCharacterTextSplitter to split text into manageable chunks
from langchain_chroma import Chroma  # Importing Chroma for vector storage and retrieval

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file
