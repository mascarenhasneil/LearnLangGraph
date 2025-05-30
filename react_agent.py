"""
ReAct Agent
 Objectives:
 1. Learn how to create Tools in LangGraph
 2. How to create a ReAct Graph
 3. Work with different types of Messages such as ToolMessages
 4. Test out robustness of our graph
 Main Goal: Create a robust ReAct Agent
"""

from typing import (List,      # defining lists of messages
                    TypedDict, # define the structure of our agent state
                    Annotated, # message type annotations, eg a message can be type of email or number be a phone number or postal code.
                    Sequence   # defining sequences of messages, To automatically handle the state updates for sequences such as by adding new messages to a chat history.
                    )
from langchain_core.messages import (HumanMessage,  # defining human messages in the chat
                                     AIMessage,     # defining human and AI messages in the chat
                                     ToolMessage,   # defining different types of messages in the chat to work with tools, such as API calls
                                     BaseMessage,   # defining the base message type, including common attributes for all messages
                                     SystemMessage, # defining the system message type, # which can be used to set the context or instructions for the agent
                                     add_message    # defining the reducer function to add messages to the chat history, helps reduce boilerplate code and manage the state updates automatically
                                     )

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tool_node

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""
    messages: Annotated[Sequence[BaseMessage], add_message]  # Using BaseMessage to allow for different message types, helps manage state updates automatically


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


def process(state: AgentState) -> AgentState:
    """Processes the agent's state and generates an AI response.
    
    Args:
        state: The current state of the agent containing conversation messages.
    
    Returns:
        The updated agent state with the AI response appended.
    """
    response = model.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nAI: {response.content}\n")
    print(f"Conversation log: {state['messages']}")
    return state


















if __name__ == "__main__":
    pass

