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

A collection of basic generator builders that yield floats in the range [0,1] that, 
for example, could be used to drive PWM LEDs.
"""
import generator_builder as gb
import math
import random
from typing import Generator, Callable

class Wave(gb.GeneratorFactory[float]):
    """A class that, when called, returns a generator that yields values according to
    the provided wave (cyclic) function in the range [0,1] for one cycle."""
    def __init__(self, wave_func: Callable[[float], float], steps: int | tuple[int, int], offset: float = 0.0, runs = 1):
        """ wave_func - a function that takes a float in the range [0,1] and returns a float in the range [0,1]. 
        This function is cyclic with a period of 1.0.
        steps - the number of steps (yielded values) in the wave cycle if an integer is provided. 
        If a tuple is provided, it is interpreted as (min_steps, max_steps) and a random number of steps in that 
        range is chosen each time the generator is created.
        offset - a float in the range [0,1] that specifies the starting point in the wave cycle. 
        runs - number of times to run the wave cycle (default is 1). 0 means infinite.

        We will adjust steps to be a multiple of 4 to ensure wave symmetry.
        """
        self.wave_func = wave_func
        if isinstance(steps, int):
            self.steps = (steps//4)*4  # Ensure multiple of 4 for wave symmetry
            self.is_random = False
        else:
            # We divide by 4 here to keep the random range consistent after multiplying back in _a_cycle_generator
            self.steps = (steps[0]//4, steps[1]//4)  
            self.is_random = True

        self.is_random = isinstance(steps, tuple)
        self.offset = offset
        self.runs = runs
    def _a_cycle_generator(self):
        if self.is_random:
            num_steps = 4*random.randint(self.steps[0], self.steps[1])
        else:
            num_steps = self.steps
        step_slice = 1.0 / num_steps
        for i in range(num_steps):
            position = (self.offset + i * step_slice) % 1.0
            yield self.wave_func(position)  

    def _generate(self) -> Generator[float, None, None]:
        if self.runs == 0:
            while True:
                yield from self._a_cycle_generator()
        else:
            for _ in range(self.runs):
                yield from self._a_cycle_generator()

TWO_PI = 2 * math.pi # Constant for 2pi to save recalculating

def sine_function(x: float) -> float:
    """A sine wave function that maps [0,1] to [0,1]."""
    return (math.sin(TWO_PI * x) + 1) / 2

def square_wave_function(x: float) -> float:
    """A square wave function that maps [0,1] to [0,1]."""
    return 1.0 if x < 0.5 else 0.0

def sawtooth_wave_function(x: float) -> float:
    """A sawtooth wave function that maps [0,1] to [0,1]."""
    if x < 0.25:
        return 0.5 + 2 * x
    elif x < 0.75:
        return  1.5 - 2*x   # simplifying 1.0 - 2 * (x - 0.25)
    else:
        return 2 * (x - 0.75)
    

def sine_wave_factory(steps: int | tuple[int, int], offset: float = 0.0, runs: int = 1) -> gb.GeneratorFactory[float]:
    """Returns a generator factory that creates a sine wave generator."""
    return Wave(sine_function, steps, offset, runs)
def square_wave_factory(steps: int | tuple[int, int], offset: float = 0.0, runs: int = 1) -> gb.GeneratorFactory[float]:
    """Returns a generator factory that creates a square wave generator."""
    return Wave(square_wave_function, steps, offset, runs)
def sawtooth_wave_factory(steps: int | tuple[int, int], offset: float = 0.0, runs: int = 1) -> gb.GeneratorFactory[float]:
    """Returns a generator factory that creates a sawtooth wave generator."""
    return Wave(sawtooth_wave_function, steps, offset, runs)



if __name__ == "__main__":
    print("Testing float generators...")
    
    print("\n1. Testing sine wave:")
    sine_gen = sine_wave_factory(10)  # (10//4)*4 = 8 steps
    values = list(sine_gen())
    print(f"Sine wave (8 steps): {[round(v, 2) for v in values]}")
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)

    print('\n2. Testing sine wave with step range:')
    sine_rand = sine_wave_factory((4,16))
    values = list(sine_rand())
    print(f'Sine wave output: {[round(v, 2) for v in values]}')
    assert 4 <= len(values) <= 16
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print("\n3. Testing sawtooth wave:")
    sawtooth_gen = sawtooth_wave_factory(10) # (10//4)*4 = 8 steps
    values = list(sawtooth_gen())
    print(f"Sawtooth wave output: {[round(v, 2) for v in values]}")
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print('\n4. Testing sawtooth wave with step range:')
    sawtooth_rand = sawtooth_wave_factory((8,16))
    values = list(sawtooth_rand())
    print(f'Sawtooth wave output: {[round(v, 2) for v in values]}')
    assert 8 <= len(values) <= 16
    assert all(0.0 <= v <= 1.0 for v in values) 

    print("\n5. Testing square wave:")
    square_gen = square_wave_factory(10) # (10//4)*4 = 8 steps
    values = list(square_gen())
    print(f"Square wave output: {values}")
    assert len(values) == 8
    assert all(v in [0.0, 1.0] for v in values)
    high_count = sum(1 for v in values if v == 1.0)
    low_count = sum(1 for v in values if v == 0.0)
    assert high_count == low_count
    
    print('\n6. Testing square wave with step range:')
    square_rand = square_wave_factory((4,12))
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
    
    print("\n8. Testing ConstantFor:")
    const_for_gen = gb.ConstantFor(0.75, 5)
    values = list(const_for_gen())
    print(f"ConstantFor (0.75, 5 steps): {values}")
    assert len(values) == 5
    assert all(v == 0.75 for v in values)
    
    print("\n9. Testing value ranges:")
    generators = [
        ("Sine wave", sine_wave_factory(100)),
        ("Sawtooth wave", sawtooth_wave_factory(100)),
        ("Square wave", square_wave_factory(100)),
        ("Constant", gb.Constant(0.3)),
        ("ConstantFor", gb.ConstantFor(0.7, 100))
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
    sine_offset_gen = sine_wave_factory(8, offset=0.75)
    values = list(sine_offset_gen())
    print(f"Sine wave (8 steps, offset=0.75): {[round(v, 2) for v in values]}")
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print('\n11. Testing sawtooth wave with offset:')
    sawtooth_offset_gen = sawtooth_wave_factory(8, offset=0.5)
    values = list(sawtooth_offset_gen())
    print(f'Sawtooth wave (8 steps, offset=0.5): {[round(v, 2) for v in values]}')
    assert len(values) == 8
    assert all(0.0 <= v <= 1.0 for v in values)
    
    print("\n12. Testing square wave with offset:")
    square_offset_gen = square_wave_factory(8, offset=0.75)
    values = list(square_offset_gen())
    print(f"Square wave (8 steps, offset=0.75): {values}")
    assert len(values) == 8
    assert all(v in [0.0, 1.0] for v in values)
    
    print("\n13. Testing offset produces different values than non-offset:")
    sine_no_offset = list(sine_wave_factory(8)())
    sine_with_offset = list(sine_wave_factory(8, offset=0.5)())
    assert sine_no_offset != sine_with_offset, "Offset should produce different values"
    print("Offset successfully produces different wave values")
    
    print("\nAll tests completed!")