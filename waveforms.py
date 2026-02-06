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
import generator_builder as gb
import math



TWO_PI = 2 * math.pi  # Constant for 2π to avoid recalculation

def sine_function(x: float) -> float:
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

def square_wave_function(x: float) -> float:
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

def sawtooth_wave_function(x: float) -> float:
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
        return  1.5 - 2*x   # simplifying 1.0 - 2 * (x - 0.25)
    else:
        return 2 * (x - 0.75)
    

def sine_wave_factory(*args, **kwargs) -> gb.GeneratorFactory[float]:
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

def square_wave_factory(*args, **kwargs) -> gb.GeneratorFactory[float]:
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

def sawtooth_wave_factory(*args, **kwargs) -> gb.GeneratorFactory[float]:
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

if __name__ == "__main__":
    print("Testing float generators...")
    
    print("\n1. Testing sine wave:")
    sine_gen = sine_wave_factory(steps=10, repeater_arg=1)  # (10//4)*4 = 8 steps
    values = list(sine_gen())
    print(f"Sine wave (8 steps): {[round(v, 2) for v in values]}")
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)

    print('\n2. Testing sine wave with step range:')
    sine_rand = sine_wave_factory(steps=(4,16), repeater_arg=1)
    values = list(sine_rand())
    print(f'Sine wave output: {[round(v, 2) for v in values]}')
    assert 4 <= len(values) <= 16
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print("\n3. Testing sawtooth wave:")
    sawtooth_gen = sawtooth_wave_factory(10, repeater_arg=1) # (10//4)*4 = 8 steps
    values = list(sawtooth_gen())
    print(f"Sawtooth wave output: {[round(v, 2) for v in values]}")
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print('\n4. Testing sawtooth wave with step range:')
    sawtooth_rand = sawtooth_wave_factory(steps=(8,16), repeater_arg=1)
    values = list(sawtooth_rand())
    print(f'Sawtooth wave output: {[round(v, 2) for v in values]}')
    assert 8 <= len(values) <= 16
    assert all(0.0 <= v <= 1.0 for v in values) 

    print("\n5. Testing square wave:")
    square_gen = square_wave_factory(steps=10, repeater_arg=1) # (10//4)*4 = 8 steps
    values = list(square_gen())
    print(f"Square wave output: {values}")
    assert len(values) == 8
    assert all(v in [0.0, 1.0] for v in values)
    high_count = sum(1 for v in values if v == 1.0)
    low_count = sum(1 for v in values if v == 0.0)
    assert high_count == low_count
    
    print('\n6. Testing square wave with step range:')
    square_rand = square_wave_factory(steps=(4,12), repeater_arg=1)
    values = list(square_rand())
    print(f'Square wave output: {values}')
    assert 4 <= len(values) <= 12
    assert all(v in [0.0, 1.0] for v in values)
    high_count = sum(1 for v in values if v == 1.0)
    low_count = sum(1 for v in values if v == 0.0)
    assert high_count == low_count

    print("\n7. Testing Constant:")
    const_gen = gb.Constant(0.5)
    values = [next(const_gen()) for _ in range(5)]
    print(f"Constant (0.5): {values}")
    assert all(v == 0.5 for v in values)
    
    print("\n8. Testing Constant:")
    const_for_gen = gb.Constant(0.75, 5)
    values = list(const_for_gen())
    print(f"Constant (0.75, 5 steps): {values}")
    assert len(values) == 5
    assert all(v == 0.75 for v in values)
    
    print("\n9. Testing value ranges:")
    generators = [
        ("Sine wave", sine_wave_factory(100, repeater_arg=1)),
        ("Sawtooth wave", sawtooth_wave_factory(100, repeater_arg=1)),
        ("Square wave", square_wave_factory(100, repeater_arg=1)),
        ("Constant", gb.Constant(0.3)),
        ("ConstantFor", gb.Constant(0.7, 100))
    ]
    
    for name, gen_builder in generators:
        gen = gen_builder()
        limit = 100
        for i, value in enumerate(gen):
            if i >= limit:
                break
            assert 0.0 <= value <= 1.0, f"{name} produced value {value} outside [0,1]"
        print(f"{name}: All values in [0,1]")
    
    print("\n10. Testing sine wave with offset:")
    sine_offset_gen = sine_wave_factory(8, offset=0.75, repeater_arg=1)
    values = list(sine_offset_gen())
    print(f"Sine wave (8 steps, offset=0.75): {[round(v, 2) for v in values]}")
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print('\n11. Testing sawtooth wave with offset:')
    sawtooth_offset_gen = sawtooth_wave_factory(8, offset=0.5, repeater_arg=1)
    values = list(sawtooth_offset_gen())
    print(f'Sawtooth wave (8 steps, offset=0.5): {[round(v, 2) for v in values]}')
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print("\n12. Testing square wave with offset:")
    square_offset_gen = square_wave_factory(8, offset=0.75, repeater_arg=1)
    values = list(square_offset_gen())
    print(f"Square wave (8 steps, offset=0.75): {values}")
    assert len(values) == 8
    assert all(v in [0.0, 1.0] for v in values)
    
    print("\n13. Testing offset produces different values than non-offset:")
    sine_no_offset = list(sine_wave_factory(8, repeater_arg=1)())
    sine_with_offset = list(sine_wave_factory(8, offset=0.5, repeater_arg=1)())
    assert sine_no_offset != sine_with_offset, "Offset should produce different values"
    print("Offset successfully produces different wave values")
    
    print("\nAll tests completed!")