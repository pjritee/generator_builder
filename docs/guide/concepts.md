# Core Concepts

## Generator Factories

A **GeneratorFactory** is the central concept in this library. It's a callable class that produces fresh generators each time it's called.

### Why Use Factories?

When you call a generator factory multiple times, you get independent generator instances:

```python
from generator_builder import Constant

factory = Constant(42)  # yields 42 indefinitely
gen1 = factory()
gen2 = factory()

# Both generators are fresh and independent
print(next(gen1))  # 42
print(next(gen2))  # 42
print(next(gen1))  # 42
```

This design allows you to:

- Reuse factories across different contexts
- Create generator pipelines
- Compose complex behaviors from simple building blocks

## Higher-Order Factories

Many classes are **higher-order** — they take generator factories as parameters and return new factories that combine them:

```python
from generator_builder import Constant, Repeater, Sequencer


const = Constant(1, 2) 


# Higher-order factory that repeatedly yields from const
# This is a simple illustration - it could be more simply written as Constant(1, 6)
repeated = Repeater(const, 3)


list(repeated())  # [1, 1, 1, 1, 1, 1]
```

## Common Patterns

### Sequential Composition

Chain multiple generators:

```python
from generator_builder import Sequencer, Constant

seq = Sequencer([
    Constant(1, 1),
    Constant(2, 2),
    Constant(3, 3)
])

print(list(seq())) #[1, 2, 2, 3, 3, 3]

```

### Repetition

Repeat a finite generator:

```python
from generator_builder import Sequencer, Constant, Repeater

seq = Repeater(Sequencer([
    Constant(1, 1),
    Constant(2, 2),
    Constant(3, 3)
    ]), 2)

print(list(seq())) # [1, 2, 2, 3, 3, 3, 1, 2, 2, 3, 3, 3]
```

### Conditional Execution

Use testers to control generator lifetime:

```python
from generator_builder import TakeWhile, CountTester, Constant

tester = CountTester(3)
factory = TakeWhile(tester, Constant(1))

list(factory()) # [1,1,1]
```

### Random Selection

Randomly choose from multiple generators:

```python
from generator_builder import Chooser, Constant

factory = Chooser([
    Constant(1,1),
    Constant(2,2),
    Constant(3,3)
])

# Result is one of the three, chosen randomly
list(factory())    # one of [1]  [2,2]  [3,3,3]
```

## Testers

**Testers** determine when a generator should stop producing values. They're used with `TakeWhile`:

```python
from generator_builder import TakeWhile, TimeoutTester, Constant

# Stop after 0.1 second
tester = TimeoutTester(0.1)
factory = TakeWhile(tester, Constant(1))

# Yields 1 for approximately 0.1 seconds
```

### Custom Testers

Implement custom test conditions:

```python
from generator_builder import Tester, TakeWhile

class Flag:
    """Create a flag object"""
    def __init__(self):
        self.flag = False

    def set_flag(self):
        self.flag = True

class FlagTester(Tester):
    
    def __init__(self, flagobj):
        self.flagobj = flagobj

    def __call__(self):
        def test():
            return not self.flagobj.flag
        return test

# When used as a tester in TakeWhile the generator will terminate when the flag is set 
# by some other generator or process
```

## Wave forms

Float generators produce smooth varying values useful for PWM control:

```python
from waveforms import sine_wave_factory

# Create a sine wave 
sine = sine_wave_factory(100, repeats=1)  # 100 steps per cycle, one cycle

# Values oscillate between 0 and 1
for value in sine():
    print(f"PWM duty cycle: {value * 100:.1f}%")
```

### Available wave forms

- **Sine**: Smooth oscillation
- **Square**: Digital on/off
- **Sawtooth**: Linear ramps

All support:

- Custom step counts
- Random step ranges
- Phase offset
- Multiple cycles or infinite repetition

## Design Philosophy

The library emphasizes:

1. **Composability**: Chain and nest factories to create complex behaviors
2. **Reusability**: Factories can be used multiple times and in different contexts
3. **Simplicity**: Each class has a single, clear responsibility
4. **Flexibility**: Use with any value type through generics
