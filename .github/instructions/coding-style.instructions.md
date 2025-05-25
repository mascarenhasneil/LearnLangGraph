---
description: "This file provides guidelines for writing clean, maintainable, and idiomatic Python code with a focus on functional patterns, proper abstraction, and PEP 8 compliance."
---

## Type Definitions:

- Prefer dataclasses for data types:
    ```python
    # Good: Immutable data type with value semantics
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class CustomerDto:
        name: str
        email: str
    
    # Avoid: Mutable class with no type hints
    class Customer:
        pass
    ```
- Make classes final by convention unless inheritance is required:
    ```python
    # Good: Use composition or mark with a comment if not intended for inheritance
    class OrderProcessor:
        ...
    
    # Only allow inheritance when specifically designed for
    class Repository:
        ...
    ```

## Variable Declarations:

- Use type hints and meaningful names:
    ```python
    # Good: Using type hints and clear names
    fruit: str = "Apple"
    number: int = 42
    order = Order(fruit, number)
    ```

## Control Flow:

- Prefer slicing over itertools for simple cases:
    ```python
    # Good: Using slicing with clear comments
    last_item = items[-1]  # -1 means "last item"
    first_three = items[:3]  # :3 means "take first 3 items"
    slice_ = items[2:5]  # take items from index 2 to 4 (5 exclusive)
    
    # Avoid: Using itertools when slicing is clearer
    import itertools
    last_item = list(itertools.islice(items, len(items)-1, None))[0]
    first_three = list(itertools.islice(items, 3))
    slice_ = list(itertools.islice(items, 2, 5))
    ```
- Prefer list/set/dict comprehensions:
    ```python
    # Good: Using comprehensions
    fruits = ["Apple", "Banana", "Cherry"]
    squares = [x**2 for x in range(10)]
    
    # Avoid: Using map/lambda when comprehensions are clearer
    squares = list(map(lambda x: x**2, range(10)))
    ```
- Use pattern matching (Python 3.10+):
    ```python
    # Good: Clear pattern matching
    def calculate_discount(customer):
        match customer.tier:
            case "gold":
                return 0.2
            case "silver":
                return 0.1
            case _:
                return 0.0
    
    # Avoid: Nested if statements
    def calculate_discount(customer):
        if customer.tier == "gold":
            return 0.2
        elif customer.tier == "silver":
            return 0.1
        else:
            return 0.0
    ```

## Nullability:

- Use Optional for nullable types and document None returns:
    ```python
    from typing import Optional
    
    def find_order(order_id: int) -> Optional[Order]:
        """Returns an Order if found, otherwise None."""
        ...
    ```
- Use explicit None checks only when necessary:
    ```python
    def process_order(order: Optional[Order]) -> None:
        if order is None:
            raise ValueError("Order must not be None")
        ...
    ```
- Use type casting with care:
    ```python
    from typing import cast
    
    value = cast(str, possibly_str)
    ```

## Safe Operations:

- Use get methods and exception handling for safe access:
    ```python
    # Good: Using dict.get for safe access
    value = dictionary.get(key)
    if value is None:
        ...
    
    # Avoid: Direct indexing which can throw
    value = dictionary[key]  # Raises KeyError if key doesn't exist
    ```
- Use try/except for error handling, not for control flow:
    ```python
    # Good: Using try/except for exceptional cases
    try:
        price = float(price_str)
    except ValueError:
        price = 0.0
    
    # Avoid: Using exceptions for normal control flow
    ```

## Asynchronous Programming:

- Use async/await for asynchronous code:
    ```python
    import asyncio
    
    async def get_default_quantity() -> int:
        return 42
    
    # Prefer await over loop.run_until_complete
    ```
- Always propagate cancellation (if using asyncio tasks):
    ```python
    async def process():
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            # Handle cancellation
            raise
    ```
- Never use blocking calls in async code:
    ```python
    # Avoid: time.sleep in async functions
    # Good: await asyncio.sleep
    ```

## Symbol References:

- Use __name__ and __class__.__name__ for logging and exceptions:
    ```python
    class MyClass:
        def do_something(self):
            print(f"{self.__class__.__name__}: Doing something")
    ```
- Use f-strings for formatting:
    ```python
    name = "world"
    print(f"Hello, {name}!")
    ```

### Imports and Modules:

- Use explicit relative imports within packages:
    ```python
    from .module import MyClass
    ```
- Group imports: standard library, third-party, local
    ```python
    import os
    import sys
    
    import numpy as np
    
    from .my_module import MyClass
    ```
- Avoid wildcard imports:
    ```python
    # Avoid: from module import *
    ```

## Docstrings and Documentation:

- Use Google-style docstrings:
    ```python
    def fetch_smalltable_rows(
    table_handle: smalltable.Table,
    keys: Sequence[bytes | str],
    require_all_keys: bool = False,
    ) -> Mapping[bytes, tuple[str, ...]]:
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
      table_handle:
        An open smalltable.Table instance.
      keys:
        A sequence of strings representing the key of each table row to
        fetch.  String keys will be UTF-8 encoded.
      require_all_keys:
        If True only rows with values set for all keys will be returned.

    Returns:
      A dict mapping keys to the corresponding table row data
      fetched. Each row is represented as a tuple of strings. For
      example:

      {b'Serak': ('Rigel VII', 'Preparer'),
       b'Zim': ('Irk', 'Invader'),
       b'Lrrr': ('Omicron Persei 8', 'Emperor')}

      Returned keys are always bytes.  If a key from the keys argument is
      missing from the dictionary, then that row was not found in the
      table (and require_all_keys must have been False).

    Raises:
      IOError: An error occurred accessing the smalltable.
    """
    ```
- Document all public classes, methods, and functions.
- Include type hints for all function arguments and return types.

