# Generator Builder

A small collection of generator-builder utilities and helpers for creating reusable Python generator components (for example, to drive PWM LEDs). This project evolved from the PWM example in the `RPi-Pico` repository.

## Overview

**What:** A set of tiny classes that build generator factories (sequencers, repeaters, choosers, take-while helpers) that produce generators when called and a collection of float-valued generator factories such as sine, sawtooth, square, constant.

**Why:** Make it easy to compose and reuse generator behavior across applications, with a MicroPython-friendly option by stripping type hints. By designing the `Tester` class, it is possible to write testers that communicate with other testers using a shared object. This could be used to program oscillations between the behaviors of collections of PWM-controlled LEDs.

## Key Features

- **Generator Factories**: Compose reusable generator patterns
- **Wave Generators**: Built-in sine, square, and sawtooth wave generators
- **Flexible Control**: Sequencing, repeating, random selection, and conditional testing
- **MicroPython Compatible**: Strip type hints for constrained environments
- **Well Documented**: Comprehensive docstrings and examples

## Quick Start

```python
from generator_builder import Constant, RepeaterFor, TakeWhile, CountTester
from float_generator import sine_wave_factory

# Create a sine wave that cycles 3 times
sine = sine_wave_factory(16, runs=3)

# Generate values
for value in sine():
    print(round(value, 2))
```

## Repository Structure

| File | Purpose |
|------|---------|
| `generator_builder.py` | Core generator-builder classes and examples |
| `float_generator.py` | Float-producing generator factories |
| `generator_builder_mp.py` | MicroPython-compatible version |
| `float_generator_mp.py` | MicroPython-compatible float generators |
| `strip_type_hints.py` | Utility to remove type hints |
| `pwm_leds/` | PWM LED control examples |

## License

MIT License — see [LICENSE](LICENSE.md) for details.
