"""
Agent IV: Brainstormer Agent - AI Assistant
Author: Neil Mascarenhas


This module provides a class for brainstorming ideas based on a given prompt.
It sets up the foundation for managing a conversation state where brainstorming
ideas are generated, updated, and saved. The module uses functional patterns,
state management through a graph structure, and tools integration to ensure
seamless interaction with an AI agent.

The Brainstormer class (or agent) includes methods to:
    - Generate a list of creative ideas based on user input.
    - Append new ideas to the ongoing Brainstorming.
    - Save the content of the brainstorming session to an external file
      for later review.

Additional details:
    - It is designed to integrate with LangChain and LangGraph utilities, ensuring that
      conversation states and tool calls are handled dynamically.
    - It actively checks for the session's status, determining if the session should continue
      or end after saving the brainstorming document.

This module is ideal for applications that require interactive brainstorming sessions,
where ideas are not only generated but also managed and persisted over time.
"""

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
from langgraph.graph.message import (
    add_messages,  # Importing add_messages to automatically handle the state updates for sequences such as by adding new messages to a chat history
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import (
    StateGraph,
    END,
)  # Importing necessary components from LangGraph for state management and graph compilation
from langgraph.graph.state import (
    CompiledStateGraph,  # Importing CompiledStateGraph to compile the state graph into an executable agent
)
from langgraph.prebuilt import (
    ToolNode,  # Importing ToolNode to handle tool calls within the graph
)
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file


class AgentState(TypedDict):
    """State of the agent containing a list of conversation messages."""

    messages: Annotated[
        Sequence[BaseMessage], add_messages
    ]  # Using BaseMessage to allow for different message types, helps manage state updates automatically


class BrainstormerAgent:
    """Brainstormer Agent class to generate, update, and save brainstorming ideas."""

    def __init__(self) -> None:
        self.brainstorming_content: str = ""
        # Bind the tools to the instance methods
        self.tools = [self.update, self.save]
        self.model = ChatOpenAI(
            model="gpt-4.1-nano",  # Specify the model to use
            temperature=0.7,  # Set the temperature for response variability
        ).bind_tools(
            self.tools
        )  # Bind the tools to the model for use in the graph

    @tool
    def update(self, content: str) -> str:
        """Updates the Brainstorming content with the provided string.

        Args:
            content (str): The content to update the Brainstorming with.

        Returns:
            str: The updated Brainstorming content.
        """
        self.brainstorming_content += f"\n{content}"
        return self.brainstorming_content

    @tool
    def save(self, filename: str) -> str:
        """Saves the current Brainstorming content to a document file.
        Args:
            filename (str): The name of the document to save the Brainstorming content to.

        Returns:
            str: A message indicating that the document has been saved.
        """
        if not filename.endswith(".txt"):
            filename += ".txt"

        try:
            with open(filename, mode="w") as file:
                file.write(self.brainstorming_content)
            return f"Brainstorming content saved to {filename}."
        except Exception as e:
            return f"Error saving Brainstorming content to {filename}: {e}"

    def brainstormer_agent(self, state: AgentState) -> AgentState:
        """Creates a state graph for the brainstorming agent."""
        system_prompt = f"""
        You are a brainstorming agent. Your task is to generate ideas based on the provided prompt.
        You should respond with a list of related ideas or suggestions and help user to update or modify the the content. 
           - If you receive a prompt that is not related to brainstorming, respond with an appropriate message.
           - Always respond with a clear and concise list of only 10 ideas.
           - If the user wants to update or modify content, use the `update` tool to append new ideas.
           - If the user wants to save the Brainstorming, use the `save` tool with a filename.
           - Make sure to always show the content document state after modifications.
        the current Brainstorming content is: {self.brainstorming_content}
        """
        # Define the system message to set the context for the agent
        system_message = SystemMessage(content=system_prompt)

        if not state["messages"]:
            user_input = input(
                "\n\nI am ready to brainstorm ideas. what do you have in mind?"
            )

            user_message = HumanMessage(content=user_input)

        else:
            user_input = input("\nWhat do you think of this? Want me to update/save it?")
            print(f"\nUser input: {user_input}")
            user_message = HumanMessage(content=user_input)

        all_messages = (
            [system_message] + list(state["messages"]) + [user_message]
        )  # Combine all messages for the model input

        response = self.model.invoke(
            input=all_messages
        )  # Invoke the model with the combined messages

        print(f"\nAI response: {response.content}")
        if hasattr(response, "tool_calls") and response.tool_calls:  # type: ignore[reportAttributeAccessIssue]
            # If the response contains tool calls, process them
            print(f"\nTool calls: { [tc['name'] for tc in response.tool_calls]}")  # type: ignore[reportAttributeAccessIssue]

        return {
            "messages": list(state["messages"]) + [user_message, response]
        }  # Return the updated state with the new messages

    def should_continue(self, state: AgentState) -> str:
        """Determines whether the conversation should continue based on the last message."""
        messages: list[BaseMessage] = state["messages"]

        if not messages:
            return "continue"

        for message in reversed(messages):
            message_content_lower = message.content.lower()  # type: ignore[reportAttributeAccessIssue]
            if (
                isinstance(message, ToolMessage)
                and "saved" in message_content_lower
                and (
                    "document" in message_content_lower
                    or "content" in message_content_lower
                )
            ):
                return "end"  # If the last message indicates the document has been saved, end the

        return "continue"

    def print_messages(self, messages: list[BaseMessage]) -> None:
        """Prints the messages in the conversation."""

        if not messages:
            return

        for message in messages[-3:]:
            if isinstance(message, ToolMessage):
                print(f"Tool Message: {message.content}")

    def create_agent(self) -> CompiledStateGraph:
        """Creates and compiles the ReAct Agent graph with the defined nodes and tools.
        Returns:
            object: The compiled agent ready for interaction.
        """
        graph = StateGraph(AgentState)
        graph.set_entry_point(
            "brainstormer_agent"  # Set the entry point of the graph to the brainstormer_agent node
        )  # Set the entry point of the graph to the agent_node node

        graph.add_node(
            node="brainstormer_agent", action=self.brainstormer_agent
        )  # Add the agent node with the brainstorming action
        tool_node = ToolNode(tools=self.tools)
        graph.add_node(node="tools", action=tool_node)

        graph.add_conditional_edges(
            source="tools",
            path=self.should_continue,
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

    def run(self) -> None:
        """Runs the brainstorming agent."""
        agent = self.create_agent()  # Create the agent
        state: AgentState = {
            "messages": []
        }  # Initialize the state with an empty message list

        for step in agent.stream(input=state, stream_mode="values"):
            if "messages" in step:
                self.print_messages(step["messages"])

        print("\nBrainstorming session ended. Thank you for using the Brainstormer agent!")


if __name__ == "__main__":
    agent = BrainstormerAgent()
    agent.run()  # Run the brainstorming agent when the script is executed
