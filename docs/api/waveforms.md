# Waveforms API

Complete API reference for the waveforms module.

See [waveform.py](https://github.com/pjritee/generator_builder/blob/main/waveforms.py) for the source code and comprehensive docstrings.


## GeneratorFactoryFromFunctionform Functions

These functions map [0, 1] to [0, 1] and are used by the GeneratorFactoryFromFunction class:

- `sine_function(x)` - Sine wave function
- `square_wave_function(x)` - Square wave function
- `sawtooth_wave_function(x)` - Sawtooth wave function

## Factory Functions

Convenience functions to create GeneratorFactoryFromFunction generators with specific waveforms:

- `sine_wave_factory(steps, offset=0.0, runs=1)` - Create a sine wave generator
- `square_wave_factory(steps, offset=0.0, runs=1)` - Create a square wave generator
- `sawtooth_wave_factory(steps, offset=0.0, runs=1)` - Create a sawtooth wave generator

### Parameters

- `steps`: Integer number of steps per cycle, or tuple `(min_steps, max_steps)` for randomized counts
- `offset`: Phase offset in [0, 1], determining where in the cycle to start (default: 0.0)
- `runs`: Number of complete cycles. Use 0 for infinite cycles (default: 1)

All classes and functions include comprehensive docstrings accessible via Python's `help()` function:

```python
from waveforms import sine_wave_factory
help(sine_wave_factory)
```
