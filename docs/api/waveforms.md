# Waveforms API

Complete API reference for the waveforms module.

See [waveform.py](https://github.com/pjritee/generator_builder/blob/main/waveforms.py) for the source code and comprehensive docstrings.


## Functions defining one cycle of a periodic function

These functions map [0, 1] to [0, 1] and are used by the  class:

- `sine_function(x)` - Sine wave function
- `square_wave_function(x)` - Square wave function
- `sawtooth_wave_function(x)` - Sawtooth wave function

## Factory Functions

Convenience functions to create WaveGeneratorFactory generators with specific waveforms:

- `sine_wave_factory` - Create a sine wave generator
- `square_wave_factory` - Create a square wave generator
- `sawtooth_wave_factory` - Create a sawtooth wave generator

### Parameters
The `steps` parameter is first and is typically always given. All others should be given as keyword arguments.

- `steps`: Integer number of steps per cycle, or tuple `(min_steps, max_steps)` for randomized steps  (default: 4)
- `offset`: Phase offset in [0, 1], determining where in the cycle to start (default: 0.0)
- `runs`: Integer number of complete cycles, or  tuple `(min_steps, max_steps)` for randomized runs (default: 1)
- `repeats`: Specifies the repeating behaviour - the argument to `Repeater`.

All classes and functions include comprehensive docstrings accessible via Python's `help()` function:

```python
from waveforms import sine_wave_factory
help(sine_wave_factory)
```
