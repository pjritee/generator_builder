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

Support for building generators that could, for example, be used to drive PWM LEDs.

This module provides a set of generator factory classes that make it easy to compose and reuse
generator behavior across applications. Each GeneratorFactory, when called, returns a fresh generator
that yields values. Many classes are 'higher order' - they take generator factories as parameters
and return new factories that combine them in useful ways (sequencing, repeating, filtering, etc.)

Example:
    Create and compose generators:
    
    >>> constant_seq_gen = Sequencer([ConstantFor(1.0,2), ConstantFor(0.0,1)])
    >>> repeater = RepeaterFor(2, constant_seq_gen)
    >>> for value in repeater():
    ...     print(value)
    1.0
    1.0
    0.0
    1.0
    1.0
    0.0  
"""
import sys
import random
import time

# These generators are intended to be generally useful and so for writing the implementation
# we use type hints that would be valid in standard Python. However this is not supported in MicroPython
# so we skip type checking support when running in MicroPython
# The following two lines (as well as any type annotations) are removed when strip_type_hints.py is run
from typing import Generator, TypeVar, Callable

T = TypeVar('T')

class GeneratorFactory[T]:
    """Base class for all generator factories.
    
    A GeneratorFactory is a callable object that returns a fresh generator each time it is called.
    Subclasses implement the _generate() method to define the specific generator behavior.
    
    This design allows factories to be composed together to create complex generator behaviors
    while maintaining the ability to generate fresh, independent instances.
    
    Example:
        >>> gen_factory = Constant(42)
        >>> gen1 = gen_factory()  # Fresh generator
        >>> next(gen1)
        42
        >>> gen2 = gen_factory()  # Another fresh generator
        >>> gen1 is gen2
        False
    """
    def __call__(self) -> Generator[T, None, None]:
        """Create and return a fresh generator instance.
        
        Returns:
            A new generator that yields values of type T.
        """
        return self._generate()
    
    def _generate(self) -> Generator[T, None, None]:
        """Generate values. Must be implemented by subclasses.
        
        This is an abstract method that subclasses must override to provide
        the actual generator logic.
        
        Returns:
            A generator yielding values of type T.
            
        Raises:
            NotImplementedError: Always, as this is an abstract method.
        """
        raise NotImplementedError("Subclasses must implement _generate")

class Sequencer[T](GeneratorFactory[T]):
    """Chains multiple generators sequentially.
    
    When called, returns a generator that yields all values from an instance of the first generator factory,
    then all values from an instance of the second, and so on. Each generator factory is called once to create
    a fresh generator.
    
    Note: Each generator (except possibly the last) should be finite, otherwise the sequencer
    will never move on to the next generator.
    
    Args:
        generators: A list of generator factory callables that return generators.
        
    Example:
        >>> gen1 = ConstantFor(1, 2)  # Yield 1 twice
        >>> gen2 = ConstantFor(2, 2)  # Yield 2 twice
        >>> seq = Sequencer([gen1, gen2])
        >>> list(seq())
        [1, 1, 2, 2]
    """
    def __init__(self, generators: list[Callable[[], Generator[T,None,None]]]):
        """Initialize the Sequencer.
        
        Args:
            generators: A list of generator factory callables.
        """
        self.generators = generators
    
    def _generate(self) -> Generator[T,None,None]:
        """Yield values from each generator in sequence.
        
        Yields:
            Values from the  generator instance from each generator factory in order.
        """
        for generator in self.generators:
            yield from generator()

class Chooser[T](GeneratorFactory[T]):
    """Randomly selects one generator and yields all its values.
    
    When called, randomly chooses one generator factory from the list and returns a generator
    that yields all values from an instance of the chosen generator factory. Each call to the Chooser factory will
    make a new random selection.
    
    Args:
        generators: A list of generator factory callables to choose from.
        
    Example:
        >>> gen1 = ConstantFor(1, 2)
        >>> gen2 = ConstantFor(2, 2)
        >>> chooser = Chooser([gen1, gen2])
        >>> # Result is either [1, 1] or [2, 2], chosen randomly
        >>> list(chooser())
    """
    def __init__(self, generators: list[Callable[[], Generator[T,None,None]]]):
        """Initialize the Chooser.
        
        Args:
            generators: A list of generator factory callables.
        """
        self.generators = generators
    
    def _generate(self) -> Generator[T,None,None]:
        """Randomly select and yield from one generator.
        
        Yields:
            All values from a randomly selected generator factory call.
        """
        yield from random.choice(self.generators)()

class RepeaterFor[T](GeneratorFactory[T]):
    """Repeats a generator a fixed number of times.
    
    When called, returns a generator that yields from the supplied generator factory the specified
    number of times. Each repetition uses a fresh generator from the factory.
    
    Note: Each generator produced from the supplied factory should be finite, otherwise the repeater is redundant.
    
    Args:
        number: The number of times to repeat the generator.
        generator: A generator factory callable that produces generators.
        
    Example:
        >>> gen = ConstantFor(1, 2)  # Yield 1 twice
        >>> repeater = RepeaterFor(3, gen)  # Repeat 3 times
        >>> list(repeater())
        [1, 1, 1, 1, 1, 1]
    """
    def __init__(self, number: int, generator: Callable[[], Generator[T,None,None]]):
        """Initialize the RepeaterFor.
        
        Args:
            number: The number of times to repeat.
            generator: A generator factory callable.
        """
        self.number = number
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        """Yield values from the generator, repeated the specified number of times.
        
        Yields:
            Values from the generator, repeated for the specified number of iterations.
        """
        for _ in range(self.number):
            yield from self.generator()

class RandomRepeater[T](GeneratorFactory[T]):
    """Repeats a generator with a specified probability.
    
    When called, returns a generator that repeatedly yields from the supplied generator factory
    with the specified probability. On each iteration, a random number determines whether to yield
    from the generator again or stop. Each repetition uses a fresh generator from the factory.
    
    Note: The supplied generator should be finite, otherwise each repetition will not complete.
    
    Args:
        probability: Probability (0-100) of repeating the generator on each iteration.
        generator: A generator factory callable that produces generators.
        
    Example:
        >>> gen = ConstantFor(1, 1)  # Yield 1 once
        >>> repeater = RandomRepeater(50, gen)  # 50% chance to repeat
        >>> list(repeater())  # Result varies: could be [1] or [1, 1] or [1, 1, 1], etc.
    """
    def __init__(self, probability: int, generator: Callable[[], Generator[T,None,None]]):
        """Initialize the RandomRepeater.
        
        Args:
            probability: The probability (0-100) of repeating on each iteration.
            generator: A generator factory callable.
        """
        self.probability = probability
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        """Yield values from the generator, repeating based on random probability.
        
        Yields:
            Values from the generator. After each iteration, continues with supplied probability %.
        """
        while random.randint(0,100) < self.probability:
            yield from self.generator()

class Repeater[T](GeneratorFactory[T]):
    """Infinitely repeats a generator.
    
    When called, returns a generator that yields from the supplied generator factory infinitely,
    creating a fresh generator each time the current one is exhausted.
    
    Note: The supplied generator should be finite, otherwise the repeater will yield forever from
    the first generator and never move to subsequent repetitions.
    
    Args:
        generator: A generator factory callable that produces generators.
        
    Example:
        >>> gen = ConstantFor(1, 2)  # Yield 1 twice
        >>> repeater = Repeater(gen)
        >>> gen_iter = repeater()
        >>> [next(gen_iter) for _ in range(6)]  # Get 6 values
        [1, 1, 1, 1, 1, 1]
    """
    def __init__(self, generator: Callable[[], Generator[T,None,None]]):
        """Initialize the Repeater.
        
        Args:
            generator: A generator factory callable.
        """
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        """Infinitely yield values from the generator.
        
        Yields:
            Values from the generator, infinitely repeating when exhausted.
        """
        while True:
            yield from self.generator()  

class GeneratorFactoryFromFunction[T](GeneratorFactory[T]):
    """Generator factory derived from a function that has configurable discretization and offset.
    
    Yields values according to a function that maps the interval [0, 1] to [0, 1]. The function is discretized into a configurable
    number of steps and can be repeated multiple times or infinitely.
    
    When the function represents a cyclic function (like sine) for one period, then increasing the number of runs
    will extend the cyclic behavior. The offset parameter allows starting the cycle at different points.    

    The number of steps is automatically adjusted to be a multiple of 4 to ensure
    proper symmetry when used with cyclic functions such as sine.
    
    Args:
        func: A callable that takes a float in [0, 1] and returns a float in [0, 1]. 
        steps: Either an integer (number of steps per cycle) or a tuple (min_steps, max_steps)
            for random step counts. Steps are adjusted to be multiples of 4.
        offset: Offset the starting point of function evaluation. The function is first evaluated on values from [offset, 1]
            and then from [0, offset].  offset should be in the range [0,1]. Default is 0.0.
        runs: Number of times to repeat the function evaluations. 0 means infinite repetition. Default is 1.
        
    Attributes:
        func: The supplied function.
        steps: Adjusted step count(s), guaranteed to be multiples of 4.
        offset: The supplied offset.
        runs: Number of repetitions (0 for infinite).
        is_random: True if step count is randomly selected.
        
    Example:
        >>> sine_wave = GeneratorFactoryFromFunction(sine_function, 16)
        >>> gen = sine_wave()
        >>> values = list(gen)
        >>> len(values)
        16
    """
    def __init__(self, func: Callable[[float], T], steps: int | tuple[int, int], offset: float = 0.0, runs = 1):
        """Initialize the GeneratorFactoryFromFunction generator factory.
        
        Args:
            func: A function mapping [0, 1] to [0, 1].
            steps: Integer number of steps, or tuple (min_steps, max_steps) for randomized counts.
                All values are adjusted to be multiples of 4 for wave symmetry.
            offset: Offset for function evaluation. Default is 0.0.
            runs: Number of complete evaluations to generate. Use 0 for infinite cycles. Default is 1.
        """
        self.func = func
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
    
    def _an_evaluation_generator(self):
        """Generate an evaluation of the function over [0,1].
        
        Yields:
            Values of type T representing the function evaluated over [0, 1],
            with discretization determined by the step count.
        """
        if self.is_random:
            num_steps:int = 4*random.randint(self.steps[0], self.steps[1])
        else:
            num_steps:int = self.steps
        step_slice = 1.0 / num_steps
        for i in range(num_steps):
            position = (self.offset + i * step_slice) % 1.0 # float version of modulo for wrap-around
            yield self.func(position)  

    def _generate(self) -> Generator[T, None, None]:
        """Generate one or more complete cycles of the waveform.
        
        Yields:
            Float values in [0, 1] from the waveform, repeated for the specified number of runs.
            If runs is 0, yields infinitely.
            
        """
        if self.runs == 0:
            while True:
                yield from self._an_evaluation_generator()
        else:
            for _ in range(self.runs):
                yield from self._an_evaluation_generator()

class Tester:
    """Base class for testers used with TakeWhile.
    
    A Tester is used by TakeWhile to determine when to stop yielding values.
    When called, a Tester returns a callable that can be invoked repeatedly to test a condition.
    
    The design separates the tester factory (the Tester object itself) from the actual test function,
    allowing state to be reset for each new use of a TakeWhile generator.
    
    Subclasses should override __call__() to return a test function, and may override on_false()
    to perform cleanup when the test first returns False.
    """

    def __call__(self) -> Callable[[], bool]:
        """Create and return a fresh test function.
        
        Returns:
            A callable that takes no arguments and returns a boolean. The callable will be
            invoked repeatedly by TakeWhile until it returns False.
            
        Raises:
            NotImplementedError: Always, as this is an abstract method.
        """
        raise NotImplementedError("Subclasses must implement __call__")
    
    def on_false(self):
        """Called when the tester returns False for the first time.
        
        Override this method in subclasses to perform cleanup or state management when
        the test condition becomes false. The default implementation does nothing.
        """
        pass

class TakeWhile[T](GeneratorFactory[T]):
    """Yields values while a test condition is true.
    
    When called, returns a generator that yields values from the supplied generator factory
    only while the supplied tester returns True. Once the tester returns False, the generator
    stops and the tester's on_false() method is called.
    
    This allows for sophisticated filtering and early termination based on custom conditions,
    including time-based or count-based limits.
    
    Args:
        tester: A Tester object that determines when to stop yielding.
        generator: A generator factory callable that produces generators.
        
    Example:
        >>> tester = CountTester(3)  # Stop after 3 values
        >>> gen = Constant(1)  # Infinite generator
        >>> take_while = TakeWhile(tester, gen)
        >>> list(take_while())
        [1, 1, 1]
    """
    def __init__(self, tester: Tester, generator: Callable[[], Generator[T,None,None]]):
        """Initialize the TakeWhile.
        
        Args:
            tester: A Tester instance.
            generator: A generator factory callable.
        """
        self.tester = tester
        self.generator = generator
    
    def _generate(self) -> Generator[T,None,None]:
        """Yield values while the test condition is true.
        
        Yields:
            Values from the generator while the tester's test function returns True.
            After yielding stops, calls tester.on_false().
        """
        g = self.generator() # Get a fresh generator
        test = self.tester() # Get a fresh tester function
        while test():
            yield next(g)
        # Tester returned false
        self.tester.on_false()

class Constant[T](GeneratorFactory[T]):
    """Yields a constant value infinitely.
    
    When called, returns a generator that yields the same value forever.
    Useful as a base for composing with other generators that limit or modify the output.
    
    Args:
        value: The constant value to yield indefinitely.
        
    Example:
        >>> const = Constant(42)
        >>> gen = const()
        >>> [next(gen) for _ in range(3)]
        [42, 42, 42]
    """

    def __init__(self, value: T):
        """Initialize the Constant.
        
        Args:
            value: The constant value to yield.
        """
        self.value = value

    def _generate(self) -> Generator[T, None, None]:
        """Infinitely yield the constant value.
        
        Yields:
            The constant value indefinitely.
        """
        while True:
            yield self.value

class ConstantFor[T](GeneratorFactory[T]):
    """Yields a constant value a specified number of times.
    
    When called, returns a generator that yields the same value for a fixed number of iterations,
    then stops. Useful for fixed-duration operations or as a building block in compositions.
    
    Args:
        value: The constant value to yield.
        steps: The number of times to yield the value.
        
    Example:
        >>> const = ConstantFor(10, 3)  # Yield 10 three times
        >>> list(const())
        [10, 10, 10]
    """

    def __init__(self, value: T, steps: int):
        """Initialize the ConstantFor.
        
        Args:
            value: The constant value to yield.
            steps: The number of times to yield the value.
        """
        self.value = value
        self.steps = steps

    def _generate(self) -> Generator[T, None, None]:
        """Yield the constant value the specified number of times.
        
        Yields:
            The constant value, repeated for the specified number of steps.
        """
        for _ in range(self.steps):
            yield self.value

class CountTester(Tester):
    """Tester that stops after a specified number of iterations.
    
    Returns True while an internal counter is below the limit, False once the limit is reached.
    Resets the counter each time __call__() is invoked, allowing fresh starts for multiple
    uses of TakeWhile with the same tester.
    
    Args:
        limit: The maximum number of iterations before returning False.
        
    Example:
        >>> tester = CountTester(3)
        >>> gen = TakeWhile(tester, Constant(1))
        >>> list(gen())
        [1, 1, 1]
    """
    def __init__(self, limit: int):
        """Initialize the CountTester.
        
        Args:
            limit: The iteration limit.
        """
        self.limit = limit
        self.count = 0
    
    def __call__(self) -> Callable[[], bool]:
        """Create a fresh test function with counter reset.
        
        Returns:
            A callable that returns True while counter < limit, False when limit is reached.
        """
        # reset count each time __call__ is invoked as part of a fresh
        # use of a TakeWhile generator
        self.count = 0  
        def test_fun() -> bool:
            result = self.count < self.limit
            self.count += 1
            return result
        return test_fun

class TimeoutTester(Tester):
    """Tester that stops after a specified time duration.
    
    Returns True while elapsed time is below the limit, False once the time limit is exceeded.
    Resets the start time each time __call__() is invoked, allowing fresh starts for multiple
    uses of TakeWhile with the same tester.
    
    The time measurement can be overridden via _get_time() for different environments
    (e.g., MicroPython vs standard Python).
    
    Args:
        limit_seconds: The maximum time in seconds before returning False.
        
    Example:
        >>> tester = TimeoutTester(1.0)  # 1 second timeout
        >>> gen = TakeWhile(tester, Constant(1))
        >>> # Yields values for 1 second, then stops
        >>> list(gen())
    """
    def __init__(self, limit_seconds: float):
        """Initialize the TimeoutTester.
        
        Args:
            limit_seconds: The time limit in seconds.
        """
        self.limit_seconds = limit_seconds
    
    def _get_time(self) -> float:
        """Get the current time in seconds.
        
        Override this method if running in an environment with a different time API
        (e.g., MicroPython). For standard Python, uses time.time(). For MicroPython,
        attempts to use mp_time.ticks_ms().
        
        Returns:
            Current time in seconds as a float.
        """
        if 'micropython' in sys.modules:
            return mp_time.ticks_ms() / 1000.0
        else:
            return time.time()
    
    def __call__(self) -> Callable[[], bool]:
        """Create a fresh test function with timer reset.
        
        Returns:
            A callable that returns True if elapsed time < limit, False otherwise.
        """
        # reset start time each time __call__ is invoked as part of a fresh
        # use of a TakeWhile generator   
        start_time = self._get_time()
        def test_fun() -> bool:
            return (self._get_time() - start_time) < self.limit_seconds
            
        return test_fun


# Test code and example usage
if __name__ == "__main__":
    
    class RampGen(GeneratorFactory[float]):
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
    
    class SineGeneratorFactoryFromFunctionGen(GeneratorFactory[float]):
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
    repeat_gen = RepeaterFor(3, RampGen(0.0, 1.0, 3))
    values = []
    for val in repeat_gen():
        values.append(round(val, 2))
    print(f"Repeater output (3 times): {values}")

    print("\n4. Testing chooser:")
    choose_gen = RepeaterFor(10, Chooser([
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
    always_repeat_gen = Repeater(Sequencer([take_while_1, take_while_2]))
    values = []
    for i, val in enumerate(always_repeat_gen()):
        values.append(val)
        if i >= 20:  # Only take first 20 values
            break
    print(f"Always repeater output (first 20): {values}")
    
    print("\n7. Testing sine_wave_gen:")
    sine_gen = SineGeneratorFactoryFromFunctionGen(amplitude=1.0, frequency=1.0, steps=10)
    values = []
    for val in sine_gen():
        values.append(round(val, 2))
    print(f"Sine wave output (first 10 steps): {values}")
    
    print("\n8. Testing inheritance and callable interface:")
    generators = [
        Sequencer([Constant(1.0)]),
        Chooser([Constant(1.0)]),
        RepeaterFor(1, Constant(1.0)),
        RandomRepeater(100, Constant(1.0)),
        Repeater(Constant(1.0)),
        TakeWhile(AlwaysTrueTester(), Constant(1.0)),
        Constant(1.0),
        ConstantFor(1.0, 5),
        RampGen(0.0, 1.0, 5),
        SineGeneratorFactoryFromFunctionGen()
    ]
    
    for gen in generators:
        print(f"{gen.__class__.__name__}: isinstance(GeneratorFactory) = {isinstance(gen, GeneratorFactory)}")
        gen_iter = gen()
        print(f"  Returns generator: {hasattr(gen_iter, '__iter__') and hasattr(gen_iter, '__next__')}")
        gen_iter2 = gen()
        print(f"  Fresh generator each call: {gen_iter is not gen_iter2}")
    
    print("\nAll tests completed!")
