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


llm = ChatOpenAI(
    model="gpt-4.1-nano",  # Specify the model to use
    temperature=0,  # Set the temperature for response variability
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)  # Initialize embeddings model for text vectorization

pdf_content_path = "artificial_intelligence_engineering.pdf"


if not os.path.exists(pdf_content_path):
    raise FileNotFoundError(f"PDF file {pdf_content_path} does not exist.")

pdf_loader = PypdfLoader(pdf_content_path)  # Load the PDF document

try:
    pages = pdf_loader.load()
    print(f"Loaded {len(pages)} pages from the PDF.")
except Exception as e:
    raise RuntimeError(f"Failed to load PDF: {e}")

# chunking process
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Size of each text chunk
    chunk_overlap=200,  # Overlap between chunks
)

pages_split = text_splitter.split_documents(pages)  # Split the loaded pages into chunks
if not pages_split:
    raise ValueError("No text chunks were created from the PDF document.")

persistent_db_location = r"./chroma_db"  # Location for the Chroma vector store
# if location does not exit create a new one
if not os.path.exists(persistent_db_location):
    os.makedirs(persistent_db_location)

collection_name = "artificial_intelligence_engineering"

try:
    # Initialize Chroma vector store with the embedding function and persistent directory
    vector_store = Chroma.from_documents(
        documents=pages_split,
        embedding=embeddings,
        persist_directory=persistent_db_location,
        collection_name=collection_name,
    )
    # Add the split pages to the Chroma vector store
    vector_store.add_documents(pages_split)
    print(f"Added {len(pages_split)} documents to the Chroma vector store.")

except Exception as e:
    print(f"Error initializing Chroma vector store: {e}")
    raise

# create a retriever
retriever = vector_store.as_retriever(
    search_type="similarity",  # Use similarity search to find relevant documents
    search_kwargs={"k": 3},  # Retrieve the top 3 most relevant documents
)


# retriever tool
@tool
def retriever_tool(query: str) -> str:
    """Retrieves relevant information on artificial intelligence based on the user's query.

    Args:
        query (str): The user's query to search for relevant information.

    Returns:
        str: A string containing the retrieved information.
    """
    try:
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant information found for Artificial Intelligence."

        results = []
        for i, doc in enumerate(docs, start=1):
            # Format the retrieved document content
            results.append(f"Document {i}:\n{doc.page_content}\n")
        return "\n".join(results)
    except Exception as e:
        return f"Error retrieving information: {e}"


tools = [retriever_tool]  # List of tools available to the agent

llm = llm.bind_tools(tools)  # Bind the tools to the language model for use in the graph


