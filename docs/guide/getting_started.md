# Getting Started

## Installation

Generator Builder is a pure Python module. To use it in your project:

### Standard Python

```bash
# Copy the files to your project
cp generator_builder.py your_project/
cp float_generator.py your_project/
```

### MicroPython

For use on Raspberry Pi Pico or other MicroPython environments:

```bash
# Generate MicroPython-compatible versions
python3 strip_type_hints.py generator_builder.py generator_builder_mp.py
python3 strip_type_hints.py float_generator.py float_generator_mp.py

# Copy the _mp.py files to your device
```

## Running Tests

### Generator Builder Tests

```bash
python3 generator_builder.py
```

This runs comprehensive tests of all generator factory classes and demonstrates their usage.

### Float Generator Tests

```bash
python3 float_generator.py
```

This tests all waveform generators and validates output ranges.

## Basic Concepts

### Generator Factories

A **GeneratorFactory** is a callable object that creates fresh generators:

```python
from generator_builder import ConstantFor

# Create a factory
factory = ConstantFor(42, 2)

# Each call produces a fresh generator
gen1 = factory()
gen2 = factory()

# They are independent instances
print(list(gen1))  # [42, 42]
print(list(gen2))  # [42, 42]
```

### Composing Generators

Combine multiple factories to create complex behaviors:

```python
from generator_builder import ConstantFor, RepeaterFor, Sequencer

# Create individual factories
gen1 = ConstantFor(1, 3)
gen2 = ConstantFor(2, 2)

# Combine them
seq = Sequencer([gen1, gen2])

# Run
print(list(seq()))   # [1, 1, 1, 2, 2]
```

### Wave forms

Use built-in waveform generators to produce values from the waveform:

```python
from float_generator import sine_wave_factory

# Create a sine wave with 16 steps per cycle
sine = sine_wave_factory(16)

# Generate values in [0, 1]
for value in sine():
    print(f"Value: {value:.2f}")
```

## Next Steps

- Read the [Core Concepts](concepts.md) guide for detailed explanations
- Explore [Usage Examples](examples.md) for practical patterns
- Check the [API Reference](../api/generator_builder.md) for complete documentation
