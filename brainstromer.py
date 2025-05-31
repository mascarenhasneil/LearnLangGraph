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


class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""

    messages: Annotated[
        Sequence[BaseMessage], add_messages
    ]  # Using BaseMessage to allow for different message types, helps manage state updates automatically


@tool
def update(content: str) -> str:
    """Updates the discussion content with the provided string.
    
    Args:
        content (str): The content to update the discussion with.
        
    Returns:
        str: The updated discussion content.
    """
    global discussion_content
    discussion_content += f"\n{content}"
    return discussion_content

@tool
def save(filename: str) -> str:
    """Saves the current discussion content to a document file.
    Args:
        filename (str): The name of the document to save the discussion content to.

    Returns:
        str: A message indicating that the document has been saved.
    """
    global discussion_content
    if not filename.endswith('.txt'):
        filename += '.txt'
        
    try: 
        with open(filename, 'w') as file:
            file.write(discussion_content)
        return f"Discussion content saved to {filename}."
    except Exception as e:
        return f"Error saving discussion content to {filename}: {e}"
    
    
tools = [update, save] 

model = ChatOpenAI(
    model="gpt-4o",  # Specify the model to use
    temperature=0.7  # Set the temperature for response variability
).bind_tools(tools)  # Bind the tools to the model for use in the graph

def brainstormer_agent(state: AgentState) -> AgentState:
    """Creates a state graph for the brainstorming agent."""
    system_prompt = f"""
        You are a brainstorming agent. Your task is to generate ideas based on the provided prompt.
        You will receive a prompt from the user, and you should respond with a list of related ideas or suggestions.
           - If you receive a prompt that is not related to brainstorming, respond with an appropriate message.
           - Always respond with a clear and concise list of ideas.
           - If the user wants to update or modify content, use the `update` tool to append new ideas.
           - If the user wants to save the discussion, use the `save` tool with a filename.
           - Make sure to always show the content document state after modifications.
        the current discussion content is: {discussion_content}
    """
    # Define the system message to set the context for the agent
    system_message = SystemMessage(content=system_prompt)
    
    if not state['messages']:
        user_input = "\n\nI am ready to brainstorm ideas. what do you have in mind?"
        user_message = HumanMessage(content=user_input)
        
    else:
        user_input = input("\nWhat would you like to do with the brainstorming session? ")
        print(f"\nUser input: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_message] + list(state["messages"]) + [user_message] # Combine all messages for the model input
    
    response = model.invoke(input=all_messages)  # Invoke the model with the combined messages
    
    print(f"\nAI response: {response.content}")
    if hasattr(response, 'tool_calls') and response.tool_calls: # type: ignore[reportAttributeAccessIssue]
        # If the response contains tool calls, process them
        print(f"\nTool calls: { [tc["name"] for tc in  response.tool_calls]}") # type: ignore[reportAttributeAccessIssue]


    return {"messages": list(state["messages"]) + [user_message, response]}  # Return the updated state with the new messages




def should_continue(state : AgentState) -> str:
    """Determines whether the conversation should continue based on the last message."""
    messages : str = state["messages"]
    
    if not messages:
        return "continue"

    for message in reversed(messages):
        if (isinstance(message,ToolMessage) and 
            "saved" in message.content.lower() and      # type: ignore[reportAttributeAccessIssue]
            "document" in message.content.lower()):     # type: ignore[reportAttributeAccessIssue]
            
            return "end" # If the last message indicates the document has been saved, end the

    return "continue"


def print_messages(messages: list[BaseMessage]):
    """Prints the messages in the conversation."""

    if not messages:
        print("No messages in the conversation.")
        return

    for message in messages[-3:]:
        if isinstance(message,ToolMessage):
            print(f"Tool Message: {message.content}")
            

def create_agent() -> CompiledStateGraph:
    """Creates and compiles the ReAct Agent graph with the defined nodes and tools.
    Returns:
        object: The compiled agent ready for interaction.
    """
    graph = StateGraph(AgentState)
    graph.set_entry_point(
        "brainstormer_agent"  # Set the entry point of the graph to the brainstormer_agent node
    )  # Set the entry point of the graph to the agent_node node

    graph.add_node(node="brainstormer_agent", action=brainstormer_agent)  # Add the agent node with the brainstorming action
    tool_node = ToolNode(tools=tools)
    graph.add_node(node="tools", action=tool_node)

    graph.add_conditional_edges(
        source="brainstormer_agent",
        path=should_continue,
        path_map={
            "continue": "brainstormer_agent",  # If the conversation should continue, loop back to the brainstormer_agent node
            "end": END,
        },
    )

    graph.add_edge(
        start_key="brainstormer_agent", end_key="tools" 
    )  # Connect the tools node back to the brainstormer_agent node

    agent = graph.compile()  # Compile the graph to create the agent
    return agent

