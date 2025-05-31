"""
ReAct Agent
 Objectives:
 1. Learn how to create Tools in LangGraph
 2. How to create a ReAct Graph
 3. Work with different types of Messages such as ToolMessages
 4. Test out robustness of our graph
 Main Goal: Create a robust ReAct Agent
"""

from typing import (TypedDict, # define the structure of our agent state
                    Annotated, # message type annotations, eg a message can be type of email or number be a phone number or postal code.
                    Sequence   # defining sequences of messages, To automatically handle the state updates for sequences such as by adding new messages to a chat history.
                    )
from langchain_core.messages import (HumanMessage,  # defining human messages in the chat
                                     # AIMessage,     # defining human and AI messages in the chat
                                     ToolMessage,   # defining different types of messages in the chat to work with tools, such as API calls
                                     BaseMessage,   # defining the base message type, including common attributes for all messages
                                     SystemMessage, # defining the system message type, # which can be used to set the context or instructions for the agent
                                     )
from langgraph.graph.message import add_messages # defining the reducer function to add messages to the chat history, helps reduce boilerplate code and manage the state updates automatically
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END  # Importing necessary components from LangGraph for state management and graph compilation
from langgraph.graph.state import CompiledStateGraph  # Importing CompiledStateGraph to compile the state graph into an executable agent
from langgraph.prebuilt import ToolNode  # Importing ToolNode to handle tool calls within the graph

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""
    messages: Annotated[Sequence[BaseMessage], add_messages]  # Using BaseMessage to allow for different message types, helps manage state updates automatically


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

tools = [add_numbers]

model = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0.0,
).bind_tools(tools)  # Bind the tools to the model, allowing the agent to use them in its responses


def agent_node(state: AgentState) -> AgentState:
    """Processes the agent's state and generates an AI response.
    
    Args:
        state: The current state of the agent containing conversation messages.
    
    Returns:
        The updated agent state with the AI response appended.
    """
    system_message = SystemMessage(content="You are a helpful assistant please answer my questions with best of my abilities. ")

    response = model.invoke(input=[system_message] + list(state["messages"]))  # Invoke the model with a list containing the system message

    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Determines whether the conversation should continue based on the last message.
    
    Args:
        state: The current state of the agent containing conversation messages.
    
    Returns:
        str: "continue" if the last message is a ToolMessage, "end" otherwise.
    """
    
    # Check if the last message is a ToolMessage
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:  # pylint: disable=no-member
        return "continue"
    else:
        return "end"

def create_agent() -> CompiledStateGraph:
    """Creates and compiles the ReAct Agent graph.

    Returns:
        object: The compiled agent ready for interaction.
    """
    graph = StateGraph(AgentState)
    graph.set_entry_point("agent_node")  # Set the entry point of the graph to the agent_node node

    graph.add_node(node="agent_node", action=agent_node)
    tool_node = ToolNode(tools=tools)
    graph.add_node(node="tools", action=tool_node)


    graph.add_conditional_edges(
        source="agent_node",
        path=should_continue,
        path_map={
            "continue": "tools",
            "end": END,
        }
    )

    graph.add_edge(start_key="tools", end_key="agent_node")  # Connect the tools node back to the agent_node node

    agent = graph.compile()  # Compile the graph to create the agent
    return agent


def print_stream(stream ) -> None:
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

def main():
    
    inputs = {"messages": [HumanMessage(content="What is 2 + 4 ?")]}  # Initial input to the agent with a human message
    
    agent = create_agent()  # Create the ReAct Agent
    print("\n\nWelcome to the ReAct Agent! \n")

    print_stream(agent.stream(input=inputs, stream_mode = "values"))    # Stream the response from the agent and print it
    
    print("Thank you for using the ReAct Agent! \n")  # Thank the user for using the agent

if __name__ == "__main__":
    main()

