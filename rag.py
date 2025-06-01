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


class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""

    messages: Annotated[
        Sequence[BaseMessage], add_messages
    ]  # Using BaseMessage to allow for different message types, helps manage state updates automatically


def should_continue(state: AgentState) -> bool:
    """Checks if the last message was a tool call and to continue or not"""
    if not state["messages"]:
        return False  # Stop if there are no messages

    last_message = state["messages"][-1]
    # Continue if the last message is from tool
    return hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0  # type: ignore[reportAttributeAccessIssue]


system_prompt = """You are an intelligent AI assistant who answers questions about Artificial Intelligence Engineering based on the PDF document loaded into your knowledge base. Use the retriever tool available to answer questions about the Artificial Intelligence Engineering data. You can make multiple calls if needed. If you need to look up some information before asking a follow up question, you are allowed to do that! Please always cite the specific parts of the documents you use in your answers.
"""

tools_dict = {
    tool.name: tool for tool in tools
}  # Create a dictionary of tools for easy access


# the LLM Agent
def call_llm(state: AgentState) -> AgentState:
    """Generates a response from the language model based on the current state.

    Args:
        state (AgentState): The current state of the agent containing conversation messages.

    Returns:
        AgentState: The updated agent state with the AI response appended.
    """

    messages = list(state["messages"])
    messages = [
        SystemMessage(content=system_prompt)
    ] + messages  # Add the system message to the conversation history

    response = llm.invoke(
        input=messages
    )  # Invoke the language model with the conversation history

    return {"messages": [response]}  # Return the updated state with the AI response



# Retriever Agent
def retriever_agent(state: AgentState) -> AgentState:
    """
    Processes the agent's state and generates a response using the retriever tool.
    Args:
        state (AgentState): The current state of the agent containing conversation messages.
    Returns:
        AgentState: The updated agent state with the retriever tool response appended.
    """
    # Get the tool calls from the last message
    tool_calls = state["messages"][-1].tool_calls  # type: ignore[reportAttributeAccessIssue]

    # Process each tool call and generate a response
    messages = []
    for tool_name in tool_calls:
        print(
            f"Calling Tool: {tool_name["name"]} with query: {tool_name["args"].get("query", "No query provided")}"
        )

        if (
            not tool_name["name"] in tools_dict
        ):  # Checks if the tools are are valid and present.
            print(f"Tool {tool_name['name']} not found in known tools.")
            result = f"Tool {tool_name['name']} not found. Retry and select tool from list of Available tools"

        else:
            result = tools_dict[tool_name["name"]].invoke(
                input=tool_name["args"].get("query", "")
            )
            print(f"Tool Result length: {len(str(result))} characters")

        messages.append(
            ToolMessage(
                tool_call_id=tool_name["id"],
                name=tool_name["name"],
                content=str(result),
            )
        )

    print("Tool Execution is complete, retuning to the model!")
    # Update the agent state with the new responses
    return {"messages": messages}