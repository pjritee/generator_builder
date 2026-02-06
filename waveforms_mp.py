"""
Copyright (c) 2026 Peter Robinson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This file contains a collection of generator factories that yield floats for cyclic functions.
They are all uses of gb.WaveGeneratorFactory

Example:
    Generate a sine wave for 10 steps:
    
    >>> sine = sine_wave_factory(10)
    >>> values = list(sine())
    >>> print(len(values))  # Will be 8 (rounded to multiple of 4)
    8
"""
import generator_builder_mp as gb
import math
TWO_PI = 2 * math.pi


def sine_function(x):
    """Sine wave function mapping [0, 1] to [0, 1].
    
    Generates one complete sine wave cycle that oscillates between 0 and 1.
    
    Args:
        x: Input value in [0, 1] representing position in the cycle.
        
    Returns:
        Output value in [0, 1] representing the sine wave at that position.
        
    Example:
        >>> sine_function(0.0)  # Start of cycle
        0.5
        >>> sine_function(0.25)  # Quarter cycle
        1.0
        >>> sine_function(0.5)   # Half cycle
        0.5
    """
    return (math.sin(TWO_PI * x) + 1) / 2


def square_wave_function(x):
    """Square wave function mapping [0, 1] to [0, 1].
    
    Generates a square wave that is 1.0 for the first half of the cycle
    and 0.0 for the second half.
    
    Args:
        x: Input value in [0, 1] representing position in the cycle.
        
    Returns:
        1.0 if x < 0.5, otherwise 0.0.
        
    Example:
        >>> square_wave_function(0.25)
        1.0
        >>> square_wave_function(0.75)
        0.0
    """
    return 1.0 if x < 0.5 else 0.0


def sawtooth_wave_function(x):
    """Sawtooth wave function mapping [0, 1] to [0, 1].
    
    Generates a sawtooth wave that is similar to the sine function but using line segments instead.
    
    Args:
        x: Input value in [0, 1] representing position in the cycle.
        
    Returns:
        Output value in [0, 1] representing the sawtooth wave at that position.
        
    Example:
        >>> sawtooth_wave_function(0.125)  # First quarter ramp up
        0.75
        >>> sawtooth_wave_function(0.25)   # Peak
        1.0
        >>> sawtooth_wave_function(0.5)    # Midpoint ramp down
        0.5
        >>> sawtooth_wave_function(0.75)   # Trough
        0.0
        >>> sawtooth_wave_function(0.875)  # Last quarter ramp down
        0.25
    """
    if x < 0.25:
        return 0.5 + 2 * x
    elif x < 0.75:
        return 1.5 - 2 * x
    else:
        return 2 * (x - 0.75)


def sine_wave_factory(*args, **kwargs):
    """Function to create a sine wave generator factory.
    
    Provides a convenient way to create a highly configurable instance of WaveGeneratorFactory configured for 
    sine waveforms.
           
    Returns:
        A GeneratorFactory that yields sine wave values in [0, 1].
        
    Example:
        >>> sine = sine_wave_factory(16)
        >>> values = list(sine())
        >>> len(values)
        16
        >>> print([round(v, 2) for v in values])
        [0.5, 0.69, 0.85, 0.96, 1.0, 0.96, 0.85, 0.69, 0.5, 0.31, 0.15, 0.04, 0.0, 0.04, 0.15, 0.31]
    """
    return gb.WaveGeneratorFactory(sine_function, *args, **kwargs)


def square_wave_factory(*args, **kwargs):
    """Factory function to create a square wave generator.
    
    Provides a convenient way to create a highly configurable instance of WaveGeneratorFactory  configured for 
    square waveforms.
    
    
    Returns:
        A GeneratorFactory that yields square wave values (0.0 or 1.0).
        
    Example:
        >>> square = square_wave_factory(8)
        >>> values = list(square())
        >>> print(values)
        [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    """
    return gb.WaveGeneratorFactory(square_wave_function, *args, **kwargs)


def sawtooth_wave_factory(*args, **kwargs):
    """Factory function to create a sawtooth wave generator.
    
    Provides a convenient way to create a highly configurable instance of WaveGeneratorFactory configured for 
    sawtooth waveforms.
    
    Returns:
        A GeneratorFactory that yields sawtooth wave values in [0, 1].
        
    Example:
        >>> sawtooth = sawtooth_wave_factory(12)
        >>> values = list(sawtooth())
        >>> print([round(v, 2) for v in values])
        [0.5, 0.67, 0.83, 1.0, 0.83, 0.67, 0.5, 0.33, 0.17, 0.0, 0.17, 0.33]
    """
    return gb.WaveGeneratorFactory(sawtooth_wave_function, *args, **kwargs)
