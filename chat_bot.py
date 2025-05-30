"""
Chatbot Agent with Enhanced Conversational Memory

This module powers an interactive chatbot agent leveraging LangChain's ChatOpenAI
model (GPT-4.1-nano) to deliver context-aware responses. It maintains a complete 
conversation history using structured message types (HumanMessage and AIMessage) and 
manages state transitions through a state graph approach.

Core Features:
    - Uses a state graph system for dynamic conversation flow.
    - Retains full conversation history to provide contextual understanding.
    - Differentiates between human and AI messages with dedicated types.
    - Loads environment configurations via dotenv for secure API key management.
    - Logs conversation history to a file upon exit.

Workflow:
    1. The agent is built using a state graph that manages the conversation flow.
    2. User input is captured as HumanMessage and appended to the conversation history.
    3. The ChatOpenAI model processes the message history to generate an AI response,
       which is then appended as an AIMessage.
    4. The updated conversation state is maintained dynamically during interactions.
    5. Upon termination, the complete conversation log is saved to a text file.

Usage:
    Execute this module to start an interactive conversation loop. Ensure that all 
    required environment variables are set in a .env file prior to running the module.
"""

from typing import List, TypedDict, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

# Define the agent state with a list of messages.
class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""
    messages: List[Union[HumanMessage, AIMessage]]


# Initialize the ChatOpenAI model with desired configuration.
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.0)


def process(state: AgentState) -> AgentState:
    """Processes the agent's state and generates an AI response.

    Args:
        state: The current state of the agent containing conversation messages.

    Returns:
        The updated agent state with the AI response appended.
    """
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nAI: {response.content}\n")
    print(f"Conversation log: {state['messages']}")
    return state

def log_conversation(conversation_history: List[Union[HumanMessage, AIMessage]]) -> None:
    """Saves the conversation history to a text file.
    Args:
        conversation_history: The list of messages exchanged during the conversation.
    """
    with open("conversation_log.txt", "w") as log_file:
        log_file.write("Conversation History:\n")
        for message in conversation_history:
            if isinstance(message, HumanMessage):
                log_file.write(f"You: {message.content}\n")
            elif isinstance(message, AIMessage):
                log_file.write(f"AI: {message.content}\n")
        log_file.write("\nEnd of conversation log.\n")
    # Save the conversation history to a file
    print("Conversation history saved to conversation_log.txt")


def main() -> None:
    """Main function to run the conversation loop for the chatbot agent. 
    It initializes the state graph, processes user input, and manages the conversation flow.
    The conversation continues until the user types 'exit', at which point the conversation history is saved.
    """
    
    graph = StateGraph(AgentState)
    graph.add_node(node="process", action=process)
    graph.add_edge(start_key=START, end_key="process")
    graph.add_edge(start_key="process", end_key=END)
    agent = graph.compile()

    conversation_history: List[Union[HumanMessage, AIMessage]] = []
    user_input = input("\n\nWelcome to the Chatbot! Type your message (or 'exit' to quit): ")

    while user_input.lower() != "exit":
        conversation_history.append(HumanMessage(content=user_input))
        agent.invoke({"messages": conversation_history})
        user_input = input("\nYou: ")
        
    print("\nThank you for chatting! Saving conversation history...")
    log_conversation(conversation_history=conversation_history)


if __name__ == "__main__":
    main()
