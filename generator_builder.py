# Copyright (c) 2026 Peter Robinson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Support for building generators that could, for example, be used to drive PWM LEDs

import sys
import random

# These generators are intended to be generally useful and so for writing the implementation
# we use type hints that would be valid in standard Python. However this is not supported in MicroPython
# so we skip type checking support when running in MicroPython
if sys.implementation.name != "micropython":
    from typing import Generator, TypeVar, Callable 
    #from collections.abc import Callable   

    # declare types for generator functions that returns a generator yielding a value of type T
    T = TypeVar('T')

# Base class for all generator builders
class GeneratorBuilder[T]:
    """Base class for generator builders. Subclasses must implement the _generate method."""
    def __call__(self) -> Generator[T, None, None]:
        return self._generate()
    
    def _generate(self) -> Generator[T, None, None]:
        raise NotImplementedError("Subclasses must implement _generate")

# The classes below are intended to be used to build up complex generators from simpler ones.
# Each class has a __call__ method that returns a generator.
# For uniformity we insist that all the generator classes used do not take any arguments in __call__.
# The type hint for such a callable is Callable[[], Generator[T,None,None]].
# 
# For convenience we provide the generator classes that can be instantiated with arguments.

class Sequencer[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that iterates through the supplied list of generators,
    yielding from each in turn."""
    def __init__(self, generators: list[Callable[[], Generator[T,None,None]]]):
        self.generators = generators
    
    def _generate(self) -> Generator[T,None,None]:
        for generator in self.generators:
            yield from generator()

class Chooser[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that randomly chooses from the supplied list of generators,
    yielding from the chosen generator."""
    def __init__(self, generators: list[Callable[[], Generator[T,None,None]]]):
        self.generators = generators
    
    def _generate(self) -> Generator[T,None,None]:
        yield from random.choice(self.generators)()

class Repeater[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    the supplied number of times."""
    def __init__(self, number: int, generator: Callable[[], Generator[T,None,None]]):
        self.number = number
        self.generator = generator
    
    def __call__(self) -> Generator[T,None,None]:
        return self._generate()
    
    def _generate(self) -> Generator[T,None,None]:
        for _ in range(self.number):
            yield from self.generator()

class RandomRepeater[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    repeatedly with the supplied probability."""
    def __init__(self, probability: int, generator: Callable[[], Generator[T,None,None]]):
        self.probability = probability
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        while random.randint(0,100) < self.probability:
            yield from self.generator()

class AlwaysRepeater[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    forever."""
    def __init__(self, generator: Callable[[], Generator[T,None,None]]):
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        while True:
            yield from self.generator()  

class TakeWhile[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    while the supplied condition is true."""
    def __init__(self, condition: Callable[[], bool], generator: Callable[[], Generator[T,None,None]]):
        self.condition = condition
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        g = self.generator()
        while self.condition():
            yield next(g)

class Timer[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    for a specified duration in seconds."""
    def __init__(self, duration: float, generator: Callable[[], Generator[T,None,None]], time_func: Callable[[], float]):
        self.duration = duration
        self.generator = generator
        self.time_func = time_func
    
    def _generate(self) -> Generator[T,None,None]:
        start_time = self.time_func()
        g = self.generator()
        while (self.time_func() - start_time) < self.duration:
            yield next(g)

class CountedTakeWhile[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    until a specified count is reached."""
    def __init__(self, count: int, generator: Callable[[], Generator[T,None,None]]):
        self.count = count
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        g = self.generator()
        current_count = 0
        while current_count < self.count:
            yield next(g)
            current_count += 1

# Test code and example usage
if __name__ == "__main__":
    # Simple test generators
    class ConstantGen(GeneratorBuilder[float]):
        """A simple generator that always yields the same value."""
        def __init__(self, value: float):
            self.value = value
        
        def _generate(self) -> Generator[float, None, None]:
            while True:
                yield self.value
    
    class RampGen(GeneratorBuilder[float]):
        """A generator that yields values from start to end in steps."""
        def __init__(self, start: float, end: float, steps: int):
            self.start = start
            self.end = end
            self.steps = steps
        
        def _generate(self) -> Generator[float, None, None]:
            step_size = (self.end - self.start) / self.steps
            current = self.start
            for _ in range(self.steps):
                yield current
                current += step_size
    
    class SineWaveGen(GeneratorBuilder[float]):
        """A generator that yields values from a sine wave."""
        def __init__(self, amplitude: float = 1.0, frequency: float = 1.0, steps: int = 100):
            self.amplitude = amplitude
            self.frequency = frequency
            self.steps = steps
        
        def _generate(self) -> Generator[float, None, None]:
            import math
            for i in range(self.steps):
                yield self.amplitude * math.sin(2 * math.pi * self.frequency * i / self.steps)
    
    # Test the generator builders
    print("Testing generator builders...")
    
    # Test sequencer
    print("\n1. Testing sequencer:")
    seq_gen = Sequencer([
        ConstantGen(1.0),
        RampGen(0.0, 1.0, 5),
        ConstantGen(0.5)
    ])
    values = []
    for i, val in enumerate(seq_gen()):
        values.append(round(val, 2))
        if len(values) >= 10:  # Limit output
            break
    print(f"Sequencer output: {values}")
    
    # Test chooser
    print("\n2. Testing chooser:")
    choose_gen = Chooser([
        ConstantGen(1.0),
        ConstantGen(2.0),
        ConstantGen(3.0)
    ])
    values = []
    for i in range(10):
        val = next(choose_gen())
        values.append(val)
    print(f"Chooser output (10 random choices): {values}")
    
    # Test repeater
    print("\n3. Testing repeater:")
    repeat_gen = Repeater(3, RampGen(0.0, 1.0, 3))
    values = []
    for val in repeat_gen():
        values.append(round(val, 2))
    print(f"Repeater output (3 times): {values}")
    
    # Test random_repeater
    print("\n4. Testing random_repeater:")
    random_repeat_gen = RandomRepeater(50, ConstantGen(1.0))  # 50% probability
    values = []
    count = 0
    for val in random_repeat_gen():
        values.append(val)
        count += 1
        if count >= 20:  # Safety limit
            break
    print(f"Random repeater output (up to 20 values): {values}")
    
    # Test always_repeater
    print("\n5. Testing always_repeater:")
    always_repeat_gen = AlwaysRepeater(ConstantGen(42.0))
    values = []
    for i, val in enumerate(always_repeat_gen()):
        values.append(val)
        if i >= 4:  # Only take first 5 values
            break
    print(f"Always repeater output (first 5): {values}")
    
    # Test take_while
    print("\n6. Testing take_while:")
    counter = [0]  # Use list to modify in nested function
    def stopping_condition() -> bool:
        print(counter)
        return counter[0] < 3
    
    take_while_gen = TakeWhile(stopping_condition, ConstantGen(1.0))
    values = []
    for val in take_while_gen():
        print(counter[0])
        values.append(val)
        counter[0] += 1
    print(f"Take while output (while counter < 3): {values}")
    
    # Test sine_wave_gen
    print("\n7. Testing sine_wave_gen:")
    sine_gen = SineWaveGen(amplitude=1.0, frequency=1.0, steps=10)
    values = []
    for val in sine_gen():
        values.append(round(val, 2))
    print(f"Sine wave output (first 10 steps): {values}")
    
    # Test inheritance and callable interface
    print("\n8. Testing inheritance and callable interface:")
    generators = [
        Sequencer([ConstantGen(1.0)]),
        Chooser([ConstantGen(1.0)]),
        Repeater(1, ConstantGen(1.0)),
        RandomRepeater(100, ConstantGen(1.0)),
        AlwaysRepeater(ConstantGen(1.0)),
        TakeWhile(lambda: True, ConstantGen(1.0)),
        ConstantGen(1.0),
        RampGen(0.0, 1.0, 5),
        SineWaveGen()
    ]
    
    for gen in generators:
        print(f"{gen.__class__.__name__}: isinstance(GeneratorBuilder) = {isinstance(gen, GeneratorBuilder)}")
        gen_iter = gen()
        print(f"  Returns generator: {hasattr(gen_iter, '__iter__') and hasattr(gen_iter, '__next__')}")
        # Test that calling again gives a new generator
        gen_iter2 = gen()
        print(f"  Fresh generator each call: {gen_iter is not gen_iter2}")
    
    print("\nAll tests completed!")
