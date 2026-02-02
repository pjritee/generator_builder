# Generator Builder API

Complete API reference for the generator builder module.

See the source code [generator_builder.py](https://github.com/pjritee/generator_builder/blob/main/generator_builder.py) for comprehensive docstrings.

## Main Classes

- `GeneratorFactory[T]` - Base class for all generator factories
- `Sequencer[T]` - Chains multiple generators sequentially
- `Chooser[T]` - Randomly selects one generator
- `RepeaterFor[T]` - Repeats a generator a fixed number of times
- `RandomRepeater[T]` - Repeats a generator with specified probability
- `Repeater[T]` - Infinitely repeats a generator
- `GeneratorFactoryFromFunction[T]` - Generator factory derived from a function with configurable discretization and offset
- `TakeWhile[T]` - Yields values while a test condition is true
- `Constant[T]` - Yields a constant value infinitely
- `ConstantFor[T]` - Yields a constant value a specified number of times

## Tester Classes

- `Tester` - Base class for testers used with TakeWhile
- `CountTester` - Stops after a specified number of iterations
- `TimeoutTester` - Stops after a specified time duration

All classes include comprehensive docstrings accessible via Python's `help()` function:

```python
from generator_builder import Sequencer
help(Sequencer)
```
