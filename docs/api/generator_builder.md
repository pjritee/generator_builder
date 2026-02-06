# Generator Builder API

Complete API reference for the generator builder module.

See the source code [generator_builder.py](https://github.com/pjritee/generator_builder/blob/main/generator_builder.py) for comprehensive docstrings.

## Main Classes

- `GeneratorFactory[T]` - Base class for all generator factories
- `Sequencer[T]` - Chains multiple generators sequentially
- `Chooser[T]` - Randomly selects one generator
- `Repeater[T]` - Repeats a generator for a specified number of times (the default is indefinitely)
- `ProbabilityRepeater[T]` - Repeats a generator with specified probability
- `SingleConstant[T]` - Yields a constant value once. Probably not useful directly (used inside the definition of `Constant`)
- `Constant[T]` - Yields a constant a number of times specified by the `repeater_arg` value (default is indefinitely)
- `BasicWaveGeneratorFactory[T]` - Basic generator factory derived from a function with configurable discretization and offset
- `WaveGeneratorFactory[T]` - A `BasicWaveGeneratorFactory[T]` wrapped in a `Repeater[T]` - similar to the way `Constant` is implemented.
- `TakeWhile[T]` - Yields values while a test condition is true


## Tester Classes

- `Tester` - Base class for testers used with TakeWhile
- `CountTester` - Stops after a specified number of iterations
- `TimeoutTester` - Stops after a specified time duration

All classes include comprehensive docstrings accessible via Python's `help()` function:

```python
from generator_builder import Sequencer
help(Sequencer)
```
