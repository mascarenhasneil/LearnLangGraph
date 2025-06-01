# LangGraph Agent Exercises

LangGraph Agent Exercises is a hands-on playground for mastering stateful AI agents using the LangGraph framework in Python. Through sequential examples—from a simple command-line bot to sophisticated RAG-powered assistants—you’ll learn to design resilient conversation flows, bind custom tools, and ground language models with real data.

This repository covers essential AI engineering concepts:

- Structured state management with `AiMessages`, `HumanMessages`, `ToolsMessages`, `SystemMessage` and dynamic workflows via LangGraph's `StateGraph`.
- Modular tool integration, custom message routing, and prompt engineering best practices.
- Retrieval-Augmented Generation (RAG) to enhance accuracy by combining retrieval and generation.

By completing these exercises, you’ll gain practical experience in building scalable, maintainable LLM applications and understand how modern AI agents orchestrate retrieval, reasoning, and generation to deliver context-aware, factual responses.

## Key Concepts

**LangChain & LangGraph**  
LangChain lets you wire together prompts, embeddings, and tools to build LLM-powered apps. LangGraph adds a **state-graph** layer, so your agents can manage conversation flows, tool calls, and data pipelines as clear, visual workflows.

**Retrieval-Augmented Generation (RAG)**  
RAG supercharges your AI’s knowledge by combining retrieval of real documents with the power of generative models. Imagine your agent has a library of PDFs and articles:

1. **Query Understanding:** When you ask a question, the agent turns your words into a numerical vector (embedding).

2. **Smart Search:** It then “zooms in” on the most relevant passages in its document store, pulling out the top 3–5 snippets.

3. **Context Assembly:** Those snippets get stitched into your prompt, so the AI has actual facts right in front of it.

4. **Knowledgeable Answer:** Finally, the LLM writes a response **informed** by those precise excerpts.

RAG gives you both **accuracy** (factual grounding) and **creativity** (natural-language answers), making it perfect for anything from customer support to research assistants.

## OpenAI ChatGPT API Setup & Usage

1. **Install SDKs:**

   ```bash
   pip install openai langchain langchain_core langchain_openai
   ```

2. **API Key:**

   - Create an `.env` file at project root with:

     ```dotenv
     OPENAI_API_KEY=sk-...
     ```

   - Load keys in Python:

     ```python
     from dotenv import load_dotenv
     load_dotenv()
     ```

3. **Instantiate Client:**

   ```python
   from langchain_openai import ChatOpenAI
   
   client = ChatOpenAI(
       model='gpt-4.1-nano',
       temperature=0.0,
   )
   ```

4. **Send Messages:**

   ```python
   from langchain_core.messages import SystemMessage, HumanMessage
   
   msgs = [SystemMessage(content='You are an expert helper'), HumanMessage(content='Hello!')]
   reply = client.invoke(input=msgs)
   ```

## Repository Structure

- `AgentExercise.ipynb` – Jupyter notebook with all five agent exercises  
- `requirements.txt` – Python dependencies  
- `.vscode/` – VS Code settings and launch configurations  

## Prerequisites

- Python 3.10+ (tested on 3.13.2)  
- Virtual environment tool (venv, conda, etc.)  

## Setup

```bash
# Create & activate a virtual environment
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Exercises

1. Open `AgentExercise.ipynb` in VS Code or Jupyter.  
2. Execute cells in order.  
3. View graph diagrams inline via `display(Image(app.get_graph().draw_mermaid_png()))`.

## Exercise Overview

### Agent 1: Personalized Compliment  

- **State:** `{ name: str }`  
- **Node:** `compliment_node`  
- **Output:** `"Hi {name}, you're doing an amazing job learning LangGraph!"`

### Agent 2: List Processor

- **State:** `{ name: str, values: list[int], operation: "+"|"*" }`  
- **Node:** `process_values`  
- Performs addition or multiplication on `values`.

### Agent 3: User Profile Graph

- **State:** `{ name: str, age: int, skills: list[str], result: str }`  
- Three nodes: greeting → age description → skill listing.

### Agent 4: Dual Operation Graph

- **State:** `{ number1, number2, number3, number4: int; operation1, operation2: "+"|"-"; result: str }`  
- Two conditional routers apply `+` or `-` twice and combine results.

### Agent 5: Auto Guessing Game

- **State:** `{ player_name, guesses: list[int], attempts, lower_bound, upper_bound, target_number, hints }`  
- Looping graph: guess → hint → continue/exit until correct or max 7 attempts.

## Customization & Extension

- You can extract each graph into standalone Python modules under `src/` and add unit tests via `pytest` or `unittest`.  
- Extend state schemas by defining new `TypedDict` entries.

## Module Details

### `simple_bot.py`

A foundational example (Agent I) showing how to integrate LangChain’s `ChatOpenAI` model with a graph-based workflow. It:

- Defines an `AgentState` using a list of `HumanMessage` objects.
- Initializes a GPT-4.1 nano model for language generation.
- Builds and compiles a `StateGraph` to manage message processing.
- Demonstrates modular design and command-line interaction.

### `chat_bot.py`

Agent II: a full-featured chatbot with conversational memory. It:

- Uses `TypedDict` for structured state (`HumanMessage`/`AIMessage`).
- Maintains entire history and routes messages via `StateGraph`.
- Loads API credentials from `.env` and logs conversation to a file.
- Provides an interactive loop for context-aware AI responses.

### `react_agent.py`

Agent III: a ReAct (Reasoning + Acting) agent. It:

- Shows how to create and bind custom tools (`@tool` functions).
- Constructs a ReAct graph to interleave reasoning and external tool calls.
- Routes `ToolMessage` and `SystemMessage` through `StateGraph`.
- Handles dynamic message updates and error-resilient tool integration.

### `brainstormer.py`

Agent IV: Brainstormer agent for idea generation. It:

- Generates creative prompts and appends ideas to the session state.
- Persists brainstorming output to an external file.
- Integrates with LangChain tools and a graph-based session flow.
- Illustrates functional patterns in state management.

### `rag_agent.py`

Agent V: Retrieval-Augmented Generation (RAG) agent. It:

- Loads documents (e.g., PDF) and splits text for indexing.
- Uses `OpenAIEmbeddings` and a Chroma vector store for similarity search.
- Enhances model context with retrieved content before generation.
- Manages retrieval + generation loops via `StateGraph`.

## Contributing

Please follow our [coding style guidelines](.github/instructions/coding-style.instructions.md) and [PR description template](.github/instructions/pull-request-description.instructions.md).

## License

Licensed under the terms of the [MIT License](LICENSE).
