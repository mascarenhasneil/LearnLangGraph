"""
Objectives:
 1. Define state structure with a list of HumanMessage objects.
 2. Initialize a GPT-4o model using LangChain's ChatOpenAI
 3. Sending and handling different types of messages
 4. Building and compiling the graph of the Agent

 Main Goal: How to integrate LLMs in our Graphs

"""

from typing import List, TypedDict
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from dotenv import (
    load_dotenv,
)  # we use it for loading environment variables secrets and stuff.


load_dotenv()  # Load environment variables from a .env file


class AgentState(TypedDict):
    """Initial state of the agent with a list of human messages."""

    messages: List[HumanMessage]


llm = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0.0,
)


def process(state: AgentState) -> AgentState:
    """Process the agent's state and generate a response"""

    response = llm.invoke(state["messages"])
    print(f"\nAI: {response.content}\n")

    return state


graph = StateGraph(AgentState)
graph.add_node(node="process", action=process)
graph.add_edge(start_key=START, end_key="process")
graph.add_edge(start_key="process", end_key=END)

agent = graph.compile()

user_input = input("You: ")

# code above initializes a simple agent that processes human messages using a GPT-4.1 nano model.
agent.invoke(input={"messages": [HumanMessage(content=user_input)]})
