"""
Agent I: Simple Bot - Integrating Language Models with a Graph-based Workflow (Not exactly an agent but a foundation for Agent AI)
Author: Neil Mascarenhas

Objectives:
 1. Define the AgentState structure using a list of HumanMessage objects to represent the
    conversation state.
 2. Initialize a high-performance GPT-4.1 nano model via LangChain's ChatOpenAI for efficient
    handling of language generation tasks.
 3. Enable robust handling of different message types to seamlessly bridge human inputs and AI responses.
 4. Construct and compile a state graph using the LangGraph library to model the agent's processing
    workflow.
 5. Demonstrate modular design by clearly separating the logic for state management, graph compilation,
    and message processing.
 6. Facilitate interactive testing with a command-line interface that supports both single-message
    and continuous chat interactions.

Main Goal:
    Showcase how to effectively integrate advanced language models within a stateful graph framework,
    promoting clean, maintainable, and testable code as per functional and modular design principles.

Additional Notes:
    - Environment variables are managed via dotenv, ensuring secure configuration handling.
    - Type hints and structured logging (if extended) aid in debugging and static analysis.
"""

from typing import List, TypedDict
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from dotenv import (
    load_dotenv,
)  # we use it for loading environment variables secrets and stuff.

load_dotenv()  # Load environment variables from a .env file


class SimpleBot:
    """Agent I: Simple Bot - Integrating Language Models with a Graph-based Workflow (Not exactly an agent but a foundation for Agent AI)"""

    def __init__(self) -> None:
        # Initialize the language model for efficient handling of language generation tasks.
        self.llm = ChatOpenAI(
            model="gpt-4.1-nano",
            temperature=0.0,
        )
        # Construct and compile a state graph using the LangGraph library to model the agent's processing workflow.
        self.agent = self._setup_agent()

    class AgentState(TypedDict):
        """Initial state of the agent with a list of human messages."""
        messages: List[HumanMessage]

    def process(self, state: "SimpleBot.AgentState") -> "SimpleBot.AgentState":
        """Process the agent's state and generate a response"""
        response = self.llm.invoke(state["messages"])
        print(f"\nAI: {response.content}\n")
        return state

    def _setup_agent(self) -> object:
        """Setup the state graph and compile the agent."""
        graph = StateGraph(SimpleBot.AgentState)
        graph.add_node(node="process", action=self.process)
        graph.add_edge(start_key=START, end_key="process")
        graph.add_edge(start_key="process", end_key=END)
        return graph.compile()

    def run(self) -> None:
        chat_type = input(
            """Welcome to the Simple Bot!
    Choose a chat type:
    1. Only 1 Human Message
    2. Chat with AI Messages
    Enter 1 or 2: """
        )

        # Validate user input for chat type if not 1 or 2 then exit the program
        if chat_type not in ["1", "2"]:
            print("Invalid choice. Please enter 1 or 2.")
            exit()

        user_input = input("You: ")

        # Get user input based on the selected chat type
        if chat_type == "2":
            # initializes a simple agent that processes human messages using a GPT-4.1 nano model.
            while user_input.lower() != "exit":
                self.agent.invoke(input={"messages": [HumanMessage(content=user_input)]})   # type: ignore[reportAttributeAccessIssue]
                user_input = input("You: ")
        else:
            self.agent.invoke(input={"messages": [HumanMessage(content=user_input)]})       # type: ignore[reportAttributeAccessIssue]
            exit()


if __name__ == "__main__":
    bot = SimpleBot()
    bot.run()
