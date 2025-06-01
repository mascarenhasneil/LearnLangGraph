"""
Agent V: Retrieval-Augmented Generation (RAG) Agent.
Author: Neil Mascarenhas

This agent employs a hybrid approach by combining retrieval mechanisms with the power of generative
language models. It uses a retrieval system to fetch relevant documents based on the user's query,
enhances its context with the retrieved content, and then generates an informed response. The agent
leverages a state graph to manage interaction flow between the language model and document retriever,
enabling iterative refinement of its responses.

Key Features:
- Integration with PDF document loaders and text splitters for effective document segmentation.
- Embedding-based similarity search using a persistent Chroma vector store.
- Custom tool integration for externally fetching domain-specific information.
- State management via a graph-based structure to facilitate adaptive tool calls.
- Robust error handling and logging for diagnosing issues during retrieval and response generation.
- Flexible configuration with clear system prompts to guide the conversational context.

This detailed design ensures that the agent provides accurate and context-rich responses on topics
related to Artificial Intelligence Engineering.
"""

import os
from typing import (
    TypedDict,  # define the structure of our agent state
    Annotated,  # message type annotations, e.g. a message can be type of email or number be a phone number or postal code.
    Sequence,   # defining sequences of messages, to automatically handle the state updates for sequences such as by adding new messages to a chat history.
)
from langchain_core.messages import (
    HumanMessage,   # defining human messages in the chat
    BaseMessage,    # defining the base message type, including common attributes for all messages
    SystemMessage,  # defining the system message type, which can be used to set the context or instructions for the agent
    ToolMessage,    # defining tool messages in the chat
)
from langchain_openai import (
    ChatOpenAI,         # OpenAI's Chat model for generating responses
    OpenAIEmbeddings,   # Embeddings model for converting text into vector representations
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
    PyPDFLoader,
)  # Importing PyPDFLoader to load PDF documents
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)  # Importing RecursiveCharacterTextSplitter to split text into manageable chunks
from langchain_chroma import Chroma  # Importing Chroma for vector storage and retrieval

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""
    messages: Annotated[
        Sequence[BaseMessage], add_messages
    ]  # Using BaseMessage to allow for different message types, helps manage state updates automatically


class RagAgent:
    """RAG Agent class that encapsulates the retrieval and generation logic."""

    def __init__(self) -> None:
        # Initialize the language model with a specific model and temperature setting.
        self.llm = ChatOpenAI(
            model="gpt-4.1-nano",   # Specify the model to use
            temperature=0,          # Set the temperature for response variability
        )

        # Initialize embeddings model for text vectorization.
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        self.pdf_content_path = "artificial_intelligence_engineering.pdf"

        if not os.path.exists(self.pdf_content_path):
            raise FileNotFoundError(
                f"PDF file {self.pdf_content_path} does not exist."
            )

        self.pdf_loader = PyPDFLoader(self.pdf_content_path)  # Load the PDF document

        try:
            self.pages = self.pdf_loader.load()
            print(f"Loaded {len(self.pages)} pages from the PDF.")
        except Exception as e:
            raise RuntimeError(f"Failed to load PDF: {e}")

        # Chunking process
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Size of each text chunk
            chunk_overlap=200,  # Overlap between chunks
        )

        self.pages_split = self.text_splitter.split_documents(self.pages)  # Split the loaded pages into chunks
        if not self.pages_split:
            raise ValueError("No text chunks were created from the PDF document.")

        self.persistent_db_location = r"./chroma_db"  # Location for the Chroma vector store
        # If location does not exist create a new one.
        if not os.path.exists(self.persistent_db_location):
            os.makedirs(self.persistent_db_location)

        self.collection_name = "artificial_intelligence_engineering"

        try:
            # Initialize Chroma vector store with the embedding function and persistent directory.
            self.vector_store = Chroma.from_documents(
                documents=self.pages_split,
                embedding=self.embeddings,
                persist_directory=self.persistent_db_location,
                collection_name=self.collection_name,
            )
            # Add the split pages to the Chroma vector store.
            self.vector_store.add_documents(self.pages_split)
            print(f"Added {len(self.pages_split)} documents to the Chroma vector store.")
        except Exception as e:
            print(f"Error initializing Chroma vector store: {e}")
            raise

        # Create a retriever.
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",   # Use similarity search to find relevant documents
            search_kwargs={"k": 3},     # Retrieve the top 3 most relevant documents
        )

        # Define the retriever tool.
        @tool
        def retriever_tool(query: str) -> str:
            """Retrieves relevant information on artificial intelligence based on the user's query.

            Args:
                query (str): The user's query to search for relevant information.

            Returns:
                str: A string containing the retrieved information.
            """
            try:
                docs = self.retriever.invoke(query)
                if not docs:
                    return "No relevant information found for Artificial Intelligence."
                results = []
                for i, doc in enumerate(docs, start=1):
                    # Format the retrieved document content.
                    results.append(f"Document {i}:\n{doc.page_content}\n")
                return "\n".join(results)
            except Exception as e:
                return f"Error retrieving information: {e}"

        self.tools = [retriever_tool]        # List of tools available to the agent

        # Bind the tools to the language model for use in the graph.
        self.llm = self.llm.bind_tools(self.tools)

        self.tools_dict = {
            tool.name: tool for tool in self.tools
        }  # Create a dictionary of tools for easy access

        self.system_prompt = (
            "You are an intelligent AI assistant who answers questions about Artificial Intelligence Engineering "
            "based on the PDF document loaded into your knowledge base. Use the retriever tool available to answer "
            "questions about the Artificial Intelligence Engineering data. You can make multiple calls if needed. "
            "If you need to look up some information before asking a follow up question, you are allowed to do that! "
            "Please always cite the specific parts of the documents you use in your answers."
        )

        # Build the state graph for the agent.
        self._build_graph()

    def _build_graph(self) -> None:
        """Builds the state graph for the RAG agent."""
        self.graph = StateGraph(AgentState)  # Create a state graph for the agent
        self.graph.add_node(node="llm_node", action=self.call_llm)  # Add the LLM node to the graph
        self.graph.add_node(node="retriever_node", action=self.retriever_agent)

        # If should_continue is True, go to retriever_node, else end the graph.
        self.graph.add_conditional_edges(
            source="llm_node",
            path=self.should_continue,
            path_map={True: "retriever_node", False: END},
        )

        # Add an edge from retriever_node back to llm_node for further processing.
        self.graph.add_edge(start_key="retriever_node", end_key="llm_node")

        self.graph.set_entry_point(key="llm_node")

        # Compile the graph to create the RAG agent.
        self.rag_agent: CompiledStateGraph = self.graph.compile()

    def should_continue(self, state: AgentState) -> bool:
        """Checks if the last message was a tool call and to continue or not."""
        if not state["messages"]:
            return False  # Stop if there are no messages

        last_message = state["messages"][-1]
        # Continue if the last message is from tool.
        return hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0  # type: ignore[reportAttributeAccessIssue]

    def call_llm(self, state: AgentState) -> AgentState:
        """Generates a response from the language model based on the current state.

        Args:
            state (AgentState): The current state of the agent containing conversation messages.

        Returns:
            AgentState: The updated agent state with the AI response appended.
        """
        messages = list(state["messages"])
        messages = [SystemMessage(content=self.system_prompt)] + messages  # Add the system message to the conversation history

        response = self.llm.invoke(input=messages)  # Invoke the language model with the conversation history

        return {"messages": [response]}  # Return the updated state with the AI response

    def retriever_agent(self, state: AgentState) -> AgentState:
        """
        Processes the agent's state and generates a response using the retriever tool.
        Args:
            state (AgentState): The current state of the agent containing conversation messages.
        Returns:
            AgentState: The updated agent state with the retriever tool response appended.
        """
        # Get the tool calls from the last message.
        tool_calls = state["messages"][-1].tool_calls  # type: ignore[reportAttributeAccessIssue]

        messages = []
        for tool_call in tool_calls:
            # Use single quotes for outer string to allow inner double quotes.
            print(
                f'Calling Tool: {tool_call["name"]} with query: {tool_call["args"].get("query", "No query provided")}'
            )

            if tool_call["name"] not in self.tools_dict:  # Checks if the tools are valid and present.
                print(f"Tool {tool_call['name']} not found in known tools.")
                result = f"Tool {tool_call['name']} not found. Retry and select tool from list of Available tools"
            else:
                result = self.tools_dict[tool_call["name"]].invoke(
                    input=tool_call["args"].get("query", "")
                )
                print(f"Tool Result length: {len(str(result))} characters")

            messages.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                    content=str(result),
                )
            )

        print("Tool Execution is complete, retuning to the model!")
        # Update the agent state with the new responses.
        return {"messages": messages}

    def run_agent(self) -> None:
        """Runs the RAG agent to interact with the user."""
        print(
            "Welcome to the RAG Agent! Ask me anything about Artificial Intelligence Engineering."
        )
        print("Type 'exit/quit' to end the conversation.")

        state: AgentState = {"messages": []}  # Initialize the agent state with an empty message list
        # Start the conversation loop.
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation. Goodbye!")
                break

            # Append the user's message to the state.
            state["messages"].append(HumanMessage(content=user_input))  # type: ignore[reportAttributeAccessIssue]

            # Run the agent with the current state.
            response_stream = self.rag_agent.invoke(input=state)

            # Print the response from the agent.
            for message in response_stream["messages"]:
                message.pretty_print()  # Print each message in a readable format


def main() -> None:
    """Main function to run the RAG agent."""
    agent = RagAgent()
    agent.run_agent()


if __name__ == "__main__":
    main()
