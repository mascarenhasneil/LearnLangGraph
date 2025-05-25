---
description: "This file provides guidelines for writing clean, maintainable, and idiomatic Python code with a focus on functional patterns, proper abstraction, and PEP 8/Google style compliance."
---
# 1 Role Definition:

- Python Language Expert
- Software Architect
- Code Quality Specialist

## 2 Python Language Rules

### 2.1 Lint Pylance and mypy
- Use Pylance and mypy for static type checking and linting.
- Fix all reported errors and warnings before committing code.

### 2.2 Imports
- Use absolute imports whenever possible.
- Group imports: standard library, third-party, local modules.
- Avoid wildcard imports (`from module import *`).
- Place all imports at the top of the file, after module docstring.
    ```python
    """Module docstring."""
    import os
    import sys
    import numpy as np
    from . import mymodule
    ```

### 2.3 Packages
- Organize code into packages for logical grouping.
- Use `__init__.py` to mark directories as packages.
- Avoid circular imports.
    ```python
    # Directory structure:
    # mypkg/
    #   __init__.py
    #   module1.py
    #   module2.py
    ```

### 2.4 Exceptions
- Use built-in exceptions where possible.
- Catch specific exceptions, not bare `except:`.
- Document raised exceptions in docstrings.
- Prefer custom exception classes for domain-specific errors.
    ```python
    class MyCustomError(Exception):
        """Custom exception for domain-specific errors."""
        pass

    def divide(a: float, b: float) -> float:
        """Divides a by b.

        Raises:
            ZeroDivisionError: If b is zero.
        """
        if b == 0:
            raise ZeroDivisionError("b must not be zero")
        return a / b
    ```

### 2.5 Mutable Global State
- Avoid mutable global state. Use constants or configuration objects.
- If necessary, prefix with `_` and document usage.
    ```python
    MAX_RETRIES = 3  # Constant
    _cache = {}  # Internal mutable state, document usage
    ```

### 2.6 Nested/Local/Inner Classes and Functions
- Use nested functions for closures or helper logic only.
- Avoid nested classes unless required for scoping.
    ```python
    def outer():
        def inner():
            ...
        return inner
    ```

### 2.7 Comprehensions & Generator Expressions
- Prefer comprehensions for simple list/set/dict creation.
- Use generator expressions for memory efficiency with large data.
    ```python
    squares = [x**2 for x in range(10)]
    even_squares = (x**2 for x in range(1000000) if x % 2 == 0)
    ```

### 2.8 Default Iterators and Operators
- Use default iterators (`for x in list`, `dict.items()`, etc.)
- Prefer built-in operators over manual loops (e.g., `sum()`, `any()`, `all()`).
    ```python
    total = sum(numbers)
    if any(x < 0 for x in numbers):
        print("Negative number found")
    ```

### 2.9 Generators
- Use generators for streaming large data or pipelines.
- Use `yield` for producing values lazily.
    ```python
    def count_up_to(n: int):
        """Yields numbers from 0 to n-1."""
        for i in range(n):
            yield i
    ```

### 2.10 Lambda Functions
- Use `lambda` for short, simple functions.
- Prefer named functions for complex logic.
    ```python
    add_one = lambda x: x + 1
    sorted_list = sorted(items, key=lambda x: x.value)
    ```

### 2.11 Conditional Expressions
- Use ternary expressions for simple assignments:
    ```python
    x = a if cond else b
    ```

### 2.12 Default Argument Values
- Do not use mutable objects as default arguments.
- Use `None` and set defaults inside the function.
    ```python
    def append_item(item, items=None):
        if items is None:
            items = []
        items.append(item)
        return items
    ```

### 2.13 Properties
- Use `@property` for computed attributes.
- Avoid unnecessary getters/setters.
    ```python
    class Circle:
        def __init__(self, radius: float):
            self.radius = radius

        @property
        def area(self) -> float:
            return 3.14159 * self.radius ** 2
    ```

### 2.14 True/False Evaluations
- Use implicit truthiness (`if x:`) unless explicit check is needed.
- Avoid `if x == True:` or `if x is False:`.
    ```python
    if items:
        print("List is not empty")
    ```

### 2.16 Lexical Scoping
- Use closures and nonlocal variables judiciously.
- Avoid excessive nesting.
    ```python
    def make_multiplier(factor):
        def multiplier(x):
            return x * factor
        return multiplier
    ```

### 2.17 Function and Method Decorators
- Use standard decorators (`@staticmethod`, `@classmethod`, `@property`).
- Document custom decorators.
    ```python
    def my_decorator(func):
        """Decorator that logs function calls."""
        def wrapper(*args, **kwargs):
            print(f"Calling {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    ```

### 2.18 Threading
- Use `threading` or `concurrent.futures` for concurrency.
- Use locks for shared mutable state.
    ```python
    import threading
    lock = threading.Lock()
    with lock:
        # critical section
        ...
    ```

### 2.19 Power Features
- Use advanced features (metaclasses, descriptors) only when necessary and document thoroughly.
    ```python
    class MyMeta(type):
        pass
    class MyClass(metaclass=MyMeta):
        pass
    ```

### 2.20 Modern Python: from __future__ imports
- Use `from __future__ import annotations` for forward references if needed.
    ```python
    from __future__ import annotations
    ```

### 2.21 Type Annotated Code
- Use type hints for all public functions, methods, and class attributes.
- Use `Optional`, `Union`, and generics as appropriate.
- Run mypy to check type correctness.
    ```python
    from typing import Optional, Union, List
    def foo(bar: Optional[int]) -> Union[str, None]:
        ...
    numbers: List[int] = [1, 2, 3]
    ```

## 3 Python Style Rules

### 3.1 Semicolons
- Do not use semicolons to separate statements.
    ```python
    # Avoid:
    x = 1; y = 2
    ```

### 3.2 Line length
- Limit lines to 80 characters (exceptions: URLs, long import statements).

### 3.3 Parentheses
- Use parentheses for line continuation and grouping.
- Avoid unnecessary parentheses.
    ```python
    # Good:
    result = (
        a_long_function_name(
            arg1, arg2, arg3
        )
    )
    ```

### 3.4 Indentation
- Use 4 spaces per indentation level.
- Never use tabs.

#### 3.4.1 Trailing commas in sequences of items?
- Use trailing commas in multi-line collections and function arguments.
    ```python
    my_list = [
        1,
        2,
        3,
    ]
    ```

### 3.5 Blank Lines
- Two blank lines before top-level functions/classes.
- One blank line between methods.

### 3.6 Whitespace
- No extra spaces inside parentheses, brackets, or braces.
- One space after commas, colons, and semicolons.
- No trailing whitespace.
    ```python
    # Good:
    foo(a, b)
    # Avoid:
    foo( a , b )
    ```

### 3.7 Shebang Line
- Use `#!/usr/bin/env python3` for executable scripts.
    ```python
    #!/usr/bin/env python3
    ```

### 3.8 Comments and Docstrings
- Use complete sentences, proper grammar, and punctuation.
- Update comments and docstrings when code changes.

#### 3.8.1 Docstrings
- Use triple double-quoted strings for all public modules, classes, functions, and methods.
- Google-style docstrings preferred.
    ```python
    def fetch_rows(
        table_handle: smalltable.Table,
        keys: list[str],
        require_all_keys: bool = False,
    ) -> dict[bytes, tuple[str, ...]]:
        """Fetches rows from a table by key.

        Args:
            table_handle: An open smalltable.Table instance.
            keys: A sequence of strings representing the key of each table row to fetch. String keys will be UTF-8 encoded.
            require_all_keys: If True, only rows with values set for all keys will be returned.

        Returns:
            A dict mapping keys to the corresponding table row data fetched. Each row is represented as a tuple of strings. For example:

                {b'Serak': ('Rigel VII', 'Preparer'),
                 b'Zim': ('Irk', 'Invader'),
                 b'Lrrr': ('Omicron Persei 8', 'Emperor')}

            Returned keys are always bytes. If a key from the keys argument is missing from the dictionary, then that row was not found in the table (and require_all_keys must have been False).

        Raises:
            IOError: An error occurred accessing the smalltable.
        """
        # ...function implementation...
    ```

#### 3.8.2 Modules
- Start each module with a docstring describing its purpose.
    ```python
    """This module provides utility functions for math operations."""
    ```

##### 3.8.2.1 Test modules
- Test modules should document test coverage and edge cases.
    ```python
    """Test module for math_utils.py. Covers edge cases for add and divide."""
    ```

#### 3.8.3 Functions and Methods
- Document all arguments, return values, and exceptions.

##### 3.8.3.1 Overridden Methods
- Document only differences from the base method.

#### 3.8.4 Classes
- Document class purpose and attributes.
    ```python
    class Person:
        """Represents a person.

        Attributes:
            name: The person's name.
            age: The person's age.
        """
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age
    ```

#### 3.8.5 Block and Inline Comments
- Use block comments for complex logic.
- Inline comments should be at least two spaces from code.
    ```python
    # Block comment explaining the next section
    for i in range(10):
        ...  # Inline comment
    ```

#### 3.8.6 Punctuation, Spelling, and Grammar
- Use correct spelling and grammar in all comments and docstrings.

### 3.10 Strings
- Prefer f-strings for formatting.
- Use triple double-quotes for docstrings.
    ```python
    name = "Alice"
    print(f"Hello, {name}!")
    ```

#### 3.10.1 Logging
- Use the `logging` module for logging.
- Prefer structured log messages.
    ```python
    import logging
    logging.info("Processing item %s", item_id)
    ```

#### 3.10.2 Error Messages
- Provide clear, actionable error messages.
    ```python
    raise ValueError("Input must be a positive integer.")
    ```

### 3.11 Files, Sockets, and similar Stateful Resources
- Use context managers (`with` statement) for resource management.
    ```python
    with open("file.txt") as f:
        data = f.read()
    ```

### 3.12 TODO Comments
- Use `TODO(name):` for actionable items, referencing an issue if possible.
    ```python
    # TODO(neil): Refactor this function for efficiency. See issue #42.
    ```

### 3.13 Imports formatting
- One import per line.
- Group imports as described above.

### 3.14 Statements
- One statement per line.

### 3.15 Accessors
- Use direct attribute access unless logic is needed.
    ```python
    person.name = "Bob"
    ```

### 3.16 Naming
- Use snake_case for functions, variables, and methods.
- Use CapWords for classes.
- Use ALL_CAPS for constants.
    ```python
    MAX_SIZE = 100
    class MyClass:
        ...
    def my_function():
        ...
    ```

#### 3.16.1 Names to Avoid
- Avoid single-character names except for counters and exceptions.
- Avoid ambiguous names (e.g., `l`, `O`, `I`).

#### 3.16.2 Naming Conventions
- Follow PEP 8 and Google Python Style Guide naming conventions.

#### 3.16.3 File Naming
- Use lowercase_with_underscores for file names.

#### 3.16.4 Guidelines derived from Guido’s Recommendations
- Be consistent and clear in naming.

### 3.17 Main
- Place script logic in a `main()` function.
- Use `if __name__ == "__main__": main()` idiom.
    ```python
    def main():
        ...
    if __name__ == "__main__":
        main()
    ```

### 3.18 Function length
- Prefer small, focused functions. Refactor if a function exceeds ~40 lines.

### 3.19 Type Annotations
#### 3.19.1 General Rules
- Use type hints for all public APIs.
    ```python
    def process_data(data: list[str]) -> int:
        ...
    ```
#### 3.19.2 Line Breaking
- Break long type annotations after commas.
    ```python
    def foo(
        a: int,
        b: str,
        c: list[float],
    ) -> None:
        ...
    ```
#### 3.19.3 Forward Declarations
- Use string annotations or `from __future__ import annotations`.
    ```python
    from __future__ import annotations
    def foo(bar: "Bar") -> "Baz":
        ...
    ```
#### 3.19.4 Default Values
- Use `Optional[...] = None` for optional arguments.
    ```python
    from typing import Optional
    def foo(bar: Optional[int] = None) -> None:
        ...
    ```
#### 3.19.5 NoneType
- Use `Optional` for arguments/returns that may be `None`.
#### 3.19.6 Type Aliases
- Use type aliases for complex types.
    ```python
    from typing import List, Tuple
    Vector = List[Tuple[float, float]]
    ```
#### 3.19.7 Ignoring Types
- Use `# type: ignore` only when necessary, and comment why.
    ```python
    value = some_func()  # type: ignore  # third-party bug
    ```
#### 3.19.8 Typing Variables
- Use annotated assignments for variables with non-obvious types.
    ```python
    count: int = 0
    ```
#### 3.19.9 Tuples vs Lists
- Use `Tuple` for fixed-length, `List` for variable-length sequences.
    ```python
    from typing import Tuple, List
    point: Tuple[float, float] = (1.0, 2.0)
    numbers: List[int] = [1, 2, 3]
    ```
#### 3.19.10 Type variables
- Use `TypeVar` for generics.
    ```python
    from typing import TypeVar, Generic
    T = TypeVar('T')
    class Stack(Generic[T]):
        ...
    ```
#### 3.19.11 String types
- Use `str` for text, `bytes` for binary data.
#### 3.19.12 Imports For Typing
- Import from `typing` as needed.
#### 3.19.13 Conditional Imports
- Use `if TYPE_CHECKING:` for imports used only in type hints.
    ```python
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from .my_module import MyClass
    ```
#### 3.19.14 Circular Dependencies
- Use forward references and `TYPE_CHECKING` to avoid circular imports.
#### 3.19.15 Generics
- Use generics for reusable code.
#### 3.19.16 Build Dependencies
- Document all build and type dependencies in `requirements.txt` or `pyproject.toml`.
