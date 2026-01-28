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

Support for building generators that could, for example, be used to drive PWM LEDs
"""
import sys
import random
import time

# These generators are intended to be generally useful and so for writing the implementation
# we use type hints that would be valid in standard Python. However this is not supported in MicroPython
# so we skip type checking support when running in MicroPython
# The following two lines are removed when strip_type_hints.py is run
from typing import Generator, TypeVar, Callable

T = TypeVar('T')


class GeneratorBuilder[T]:
    """Base class for generator builders. Subclasses must implement the _generate method."""
    def __call__(self) -> Generator[T, None, None]:
        return self._generate()
    
    def _generate(self) -> Generator[T, None, None]:
        raise NotImplementedError("Subclasses must implement _generate")

class Sequencer[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that iterates through the supplied list of generators,
    yielding from each in turn. Note that each generator (except possibly the last one) should be finite."""
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
    the supplied number of times. Note that the supplied generator should be finite."""
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
    repeatedly with the supplied probability. Note that the supplied generator should be finite."""
    def __init__(self, probability: int, generator: Callable[[], Generator[T,None,None]]):
        self.probability = probability
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        while random.randint(0,100) < self.probability:
            yield from self.generator()

class AlwaysRepeater[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    forever. Note that the supplied generator should be finite."""
    def __init__(self, generator: Callable[[], Generator[T,None,None]]):
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        while True:
            yield from self.generator()  

class Tester:
    """A base class for generating testers to be used in TakeWhile"""

    def __call__(self) -> Callable[[], bool]:
        raise NotImplementedError("Subclasses must implement __call__")

class TakeWhile[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields from the supplied generator
    while the supplied condition is true."""
    def __init__(self, tester: Tester, generator: Callable[[], Generator[T,None,None]]):
        self.tester = tester
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        g = self.generator()
        test = self.tester()
        while test():
            yield next(g)

class Constant[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields a constant value
    indefinitely."""

    def __init__(self, value: T):
        """value - the constant value to yield"""
        self.value = value

    def _generate(self) -> Generator[T, None, None]:
        while True:
            yield self.value

class ConstantFor[T](GeneratorBuilder[T]):
    """A class that, when called, returns a generator that yields a constant value
    for a specified number of steps."""

    def __init__(self, value: T, steps: int):
        """value - the constant value to yield
        steps - the number of steps (yielded values)"""
        self.value = value
        self.steps = steps

    def _generate(self) -> Generator[T, None, None]:
        for _ in range(self.steps):
            yield self.value

class CountTester(Tester):
        """A tester that returns True while a counter is below a limit."""
        def __init__(self, limit: int):
            self.limit = limit
            self.count = 0
        
        def __call__(self) -> Callable[[], bool]:
            # reset count each time __call__ is invoked as part of a fresh
            # use of a TakeWhile generator
            self.count = 0  
            def test_fun() -> bool:
                result = self.count < self.limit
                self.count += 1
                return result
            return test_fun
        
class TimeoutTester(Tester):
    """A tester that returns True while elapsed time is below a limit."""
    def __init__(self, limit_seconds: float):
        self.limit_seconds = limit_seconds
    
    def _get_time(self) -> float:
        """Override this method if running in an environment with a different time API"""
        if 'micropython' in sys.modules:
            return mp_time.ticks_ms() / 1000.0
        else:
            return time.time()
    def __call__(self) -> Callable[[], bool]:
        # reset start time each time __call__ is invoked as part of a fresh
        # use of a TakeWhile generator   
        start_time = self._get_time()
        def test_fun() -> bool:
            return (self._get_time() - start_time) < self.limit_seconds
        return test_fun

# Test code and example usage
if __name__ == "__main__":
    
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
    
    class AlwaysTrueTester(Tester):
        """A tester that always returns True."""
        def __call__(self) -> Callable[[], bool]:
            def test_fun() -> bool:
                return True
            return test_fun
        
    print("Testing generator builders...")

    print("\n1. Testing take_while:")
    tester = CountTester(3)
    take_while_gen = TakeWhile(tester, Constant(1.0))
    values = []
    for val in take_while_gen():
        values.append(val)
    print(f"Take while output (while counter < 3): {values}")
    
    take_while_1 = TakeWhile(CountTester(3), Constant(1.0))
    take_while_2 = TakeWhile(CountTester(3), Constant(2.0))
    take_while_3 = TakeWhile(CountTester(3), Constant(3.0))

    print("\n2. Testing sequencer:")
    seq_gen = Sequencer([
        TakeWhile(CountTester(3), Constant(1.0)),
        TakeWhile(CountTester(5), RampGen(0.0, 1.0, 5)),
        ConstantFor(0.01, 1)
    ])
    values = []
    for i, val in enumerate(seq_gen()):
        values.append(round(val, 2))
        if len(values) >= 10:  # Limit output
            break
    print(f"Sequencer output: {values}")
    
    print("\n3. Testing repeater:")
    repeat_gen = Repeater(3, RampGen(0.0, 1.0, 3))
    values = []
    for val in repeat_gen():
        values.append(round(val, 2))
    print(f"Repeater output (3 times): {values}")

    print("\n4. Testing chooser:")
    choose_gen = Repeater(10, Chooser([
        take_while_1,
        take_while_2,
        take_while_3    
    ]))

    values = []
    gen = choose_gen()
    for i in range(20):
        val = next(gen)
        values.append(val)
    print(f"Chooser output (20 random choices): {values}")
    
    print("\n5. Testing random_repeater:")
    random_repeat_gen = RandomRepeater(50, take_while_1)  # 50% probability
    values = []
    count = 0
    for val in random_repeat_gen():
        values.append(val)
        count += 1
        if count >= 20:  # Safety limit
            break
    print(f"Random repeater output (up to 20 values): {values}")
    
    print("\n6. Testing always_repeater:")
    always_repeat_gen = AlwaysRepeater(Sequencer([take_while_1, take_while_2]))
    values = []
    for i, val in enumerate(always_repeat_gen()):
        values.append(val)
        if i >= 20:  # Only take first 20 values
            break
    print(f"Always repeater output (first 20): {values}")
    
    print("\n7. Testing sine_wave_gen:")
    sine_gen = SineWaveGen(amplitude=1.0, frequency=1.0, steps=10)
    values = []
    for val in sine_gen():
        values.append(round(val, 2))
    print(f"Sine wave output (first 10 steps): {values}")
    
    print("\n8. Testing inheritance and callable interface:")
    generators = [
        Sequencer([Constant(1.0)]),
        Chooser([Constant(1.0)]),
        Repeater(1, Constant(1.0)),
        RandomRepeater(100, Constant(1.0)),
        AlwaysRepeater(Constant(1.0)),
        TakeWhile(AlwaysTrueTester(), Constant(1.0)),
        Constant(1.0),
        ConstantFor(1.0, 5),
        RampGen(0.0, 1.0, 5),
        SineWaveGen()
    ]
    
    for gen in generators:
        print(f"{gen.__class__.__name__}: isinstance(GeneratorBuilder) = {isinstance(gen, GeneratorBuilder)}")
        gen_iter = gen()
        print(f"  Returns generator: {hasattr(gen_iter, '__iter__') and hasattr(gen_iter, '__next__')}")
        gen_iter2 = gen()
        print(f"  Fresh generator each call: {gen_iter is not gen_iter2}")
    
    print("\nAll tests completed!")
