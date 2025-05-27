# LangGraph Agent Exercises

This repository contains a series of hands-on exercises demonstrating the **LangGraph** framework in Python. Each exercise builds a small agent graph using `StateGraph` to process and route stateful data.

## Repository Structure

- `AgentExercise.ipynb` – Jupyter notebook with all five agent exercises  
- `requirements.txt` – Python dependencies  
- `.vscode/` – VS Code settings and launch configurations  
- `.github/instructions/` – PR & coding guidelines  

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

## Contributing

Please follow our [coding style guidelines](.github/instructions/coding-style.instructions.md) and [PR description template](.github/instructions/pull-request-description.instructions.md).

## License

Licensed under the terms of the [MIT License](LICENSE).
