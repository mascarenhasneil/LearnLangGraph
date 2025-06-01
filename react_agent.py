"""
Agent III: ReAct (Reasoning and Acting) Agent
Author: Neil Mascarenhas

Objectives:
    1. Learn how to create Tools in LangGraph.
    2. Build and integrate a robust ReAct Graph.
    3. Explore different types of messages including ToolMessages.
    4. Test and iterate on the graph's resilience and adaptability.

Main Goal:
    Create a robust and dynamic ReAct Agent that seamlessly integrates
    tool calls and message handling to simulate a real-world conversational
    AI system. Enhance the agent's capabilities by demonstrating comprehensive
    message routing, state management, and custom tool integration.

Future Enhancements:
    - Incorporate advanced logging and error handling.
    - Expand the suite of tools for handling more complex operations.
    - Optimize state transitions for performance and scalability.

This example serves both as an instructional guide and a foundation for
developing more sophisticated agent architectures.
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

class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""
    messages: Annotated[
        Sequence[BaseMessage], add_messages
    ]  # Using BaseMessage to allow for different message types, helps manage state updates automatically

class ReActAgent:
    """ReAct Agent class encapsulating the agent functionality and tools."""

    def __init__(self) -> None:
        """Initialize the ReAct Agent by binding tools and setting up the model."""
        self.tools = [
            ReActAgent.add_numbers,
            ReActAgent.subtract_numbers,
            ReActAgent.multiply_numbers,
            ReActAgent.divide_numbers,
        ]
        self.model = ChatOpenAI(
            model="gpt-4.1-nano",
            temperature=0.0,
        ).bind_tools(
            self.tools
        )  # Bind the tools to the model, allowing the agent to use them in its responses

    @staticmethod
    @tool
    def add_numbers(a: int, b: int) -> int:
        """Adds two numbers together.
        Args:
            a (int): The first number.
            b (int): The second number.
        Returns:
            int: The sum of the two numbers.
        """
        return a + b

    @staticmethod
    @tool
    def subtract_numbers(a: int, b: int) -> int:
        """Subtracts two numbers.
        Args:
            a (int): The first number.
            b (int): The second number.
        Returns:
            int: The difference of the two numbers.
        """
        return a - b

    @staticmethod
    @tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiplies two numbers together.
        Args:
            a (int): The first number.
            b (int): The second number.
        Returns:
            int: The product of the two numbers.
        """
        return a * b

    @staticmethod
    @tool
    def divide_numbers(a: int, b: int) -> int:
        """Divides two numbers.
        Args:
            a (int): The first number.
            b (int): The second number.
        Returns:
            int: The quotient of the two numbers.
        """
        return int(round(a / b))

    def agent_node(self, state: AgentState) -> AgentState:
        """Processes the agent's state and generates an AI response.

        Args:
            state: The current state of the agent containing conversation messages.

        Returns:
            The updated agent state with the AI response appended.
        """
        system_message = SystemMessage(
            content="You are a helpful assistant please answer my questions with best of my abilities. "
        )

        response = self.model.invoke(
            input=[system_message] + list(state["messages"])
        )  # Invoke the model with a list containing the system message

        return {"messages": [response]}

    def should_continue(self, state: AgentState) -> str:
        """Determines whether the conversation should continue based on the last
        message.

        This function inspects the current agent state and specifically examines
        the last message in the conversation history. It checks whether the last
        message signals a tool invocation by verifying if it possesses tool call
        attributes. If such an attribute exists, the conversation is to continue,
        paving the way for further tool processing and subsequent interactions.
        Otherwise, it indicates the conversation should end.

        Args:
            state: The current state of the agent containing conversation messages,
                represented as a sequence of BaseMessage instances.

        Returns:
            str: "continue" if the last message entails a tool call; "end" otherwise.
        """
        messages = state["messages"]
        last_message = messages[-1]
        # Check if the last message has a tool call.
        if last_message.tool_calls:  # type: ignore[reportAttributeAccessIssue]
            return "continue"
        else:
            return "end"

    def create_agent(self) -> CompiledStateGraph:
        """Creates and compiles the ReAct Agent graph with the defined nodes and tools.
        Returns:
            object: The compiled agent ready for interaction.
        """
        graph = StateGraph(AgentState)
        graph.set_entry_point(
            "agent_node"
        )  # Set the entry point of the graph to the agent_node node

        graph.add_node(node="agent_node", action=self.agent_node)
        tool_node = ToolNode(tools=self.tools)
        graph.add_node(node="tools", action=tool_node)

        graph.add_conditional_edges(
            source="agent_node",
            path=self.should_continue,
            path_map={
                "continue": "tools",
                "end": END,
            },
        )

        graph.add_edge(
            start_key="tools", end_key="agent_node"
        )  # Connect the tools node back to the agent_node node

        agent = graph.compile()  # Compile the graph to create the agent
        return agent

    def print_stream(self, stream) -> None:
        """Prints the streamed response from the agent.

        Args:
            stream: The streamed response from the agent.
        """
        for s in stream:
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

    def run(self) -> None:
        """Main function to run the ReAct Agent.
        It initializes the agent, processes user input, and manages the conversation flow.
        The conversation continues until the user types 'exit', at which point the program ends.
        """
        inputs = {
            "messages": [HumanMessage(content="Can you calculate this 2 + 4 then multiply by 10 divide by 2 and subtract 3?")]
        }  # Initial input to the agent with a human message
        agent = self.create_agent()  # Create the ReAct Agent
        print("\n\nWelcome to the ReAct Agent! \n")

        self.print_stream(
            agent.stream(input=inputs, stream_mode="values")
        )  # Stream the response from the agent and print it

        print(
            "Thank you for using the ReAct Agent! \n"
        )  # Thank the user for using the agent

if __name__ == "__main__":
    agent_instance = ReActAgent()
    agent_instance.run()
