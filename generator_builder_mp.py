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
    
    >>> constant_seq_gen = Sequencer([Constant(1.0,2), Constant(0.0,1)])
    >>> repeater = Repeater(constant_seq_gen, 2)
    >>> for value in repeater():
    ...     print(value)
    1.0
    1.0
    0.0
    1.0
    1.0
    0.0  

Note: Throughout the documentation there is a slight abuse of notation. When we say "yields from a generator factory"
we really mean "yields from a generator created by calling the generator factory"

"""
import sys
import random
import time


class GeneratorFactory:
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

    def __call__(self):
        """Create and return a fresh generator instance.
        
        Returns:
            A new generator that yields values of type T.
        """
        return self._generate()

    def _generate(self):
        """Generate values. Must be implemented by subclasses.
        
        This is an abstract method that subclasses must override to provide
        the actual generator logic.
        
        Returns:
            A generator yielding values of type T.
            
        Raises:
            NotImplementedError: Always, as this is an abstract method.
        """
        raise NotImplementedError('Subclasses must implement _generate')


class Sequencer(GeneratorFactory):
    """Chains multiple generators sequentially.
    
    When called, returns a generator factory that yields all values from the first generator factory,
    then all values from the second, and so on. Each generator factory is called once to create
    a fresh generator.
    
    Note: Each generator (except possibly the last) should be finite, otherwise the sequencer
    will never move on to the next generator.
    
    Args:
        factories: A list of generator factory callables that return generators.
        
    Example:
        >>> fact1 = ConstantFor(1, 2)  # Yield 1 twice
        >>> fact2 = ConstantFor(2, 2)  # Yield 2 twice
        >>> seq = Sequencer([fact1, fact2])
        >>> list(seq())
        [1, 1, 2, 2]
    """

    def __init__(self, factories):
        """Initialize the Sequencer.
        
        Args:
            factories: A list of generator factories.
        """
        self.factories = factories

    def _generate(self):
        """Yield values from each generator in sequence.
        
        Yields:
            Values from the  generator instance from each generator factory in order.
        """
        for factory in self.factories:
            yield from factory()


class Chooser(GeneratorFactory):
    """Randomly selects one factory and yields all the values from that factory.
    
    When called, randomly chooses one generator factory from the list and returns a generator factory
    that yields all values from the chosen generator factory. Each call to the Chooser factory will
    make a new random selection.
    
    Args:
        factories: A list of generator factories to choose from.
        
    Example:
        >>> fact1 = ConstantFor(1, 2)
        >>> fact2 = ConstantFor(2, 2)
        >>> chooser = Chooser([fact1, fact2])
        >>> # Result is either [1, 1] or [2, 2], chosen randomly
        >>> list(chooser())
    """

    def __init__(self, factories):
        """Initialize the Chooser.
        
        Args:
            factories: A list of generator factories.
        """
        self.factories = factories

    def _generate(self):
        """Randomly select and yield from one generator factory.
        
        Yields:
            All values from a randomly selected generator factory call.
        """
        yield from random.choice(self.factories)()


class Repeater(GeneratorFactory):
    """ This generator factory repeats in three different ways depending on the supplied arguments.
    
    The first argument is a generator factory. 
    The second argument defines the repeating behaviour:
        - None: repeat indefinitely.
        - number: repeat that many times.
        - [min, max]: repeat a random number of times between min and max (inclusive).
    
    When called, returns a generator factory that yields from the supplied generator factory the specified number of times. 
    Each repetition uses a fresh generator from the factory.

    Note: Each generator produced from the supplied factory should be finite, otherwise the repeater is redundant.

    Args:
        factory: A generator factory.
        repeats: Arguments to determine repetition behavior.
            - None: repeat indefinitely.
            - number: repeat that many times.
            - [min, max]: repeat a random number of times between min and max (inclusive).

    """

    def __init__(self, factory, repeats=None):
        """Initialize the Repeater.
        
        Args:
            factory: A generator factory callable.
            repeats: Arguments to determine repetition behavior.
                - None: repeat indefinitely.
                - number: repeat that many times.
                - [min, max]: repeat a random number of times between min and max (inclusive).
        """
        self.factory = factory
        self.repeats = repeats

    def _generate(self):
        """Yield values from the generator, repeated according to the specified behavior.
        
        Yields:
            Values from the generator, repeated according to the initialization parameters.

        Note that each repitition calls the factory producing a new generator.
        """
        if self.repeats is None:
            while True:
                yield from self.factory()
        elif isinstance(self.repeats, int):
            for _ in range(self.repeats):
                yield from self.factory()
        else:
            count = random.randint(self.repeats[0], self.repeats[1])
            for _ in range(count):
                yield from self.factory()


class ProbabilityRepeater(GeneratorFactory):
    """Repeats a generator with a specified probability.
    
    When called, returns a generator factory that repeatedly yields from the supplied generator factory
    with the specified probability. On each iteration, a random number determines whether to yield
    from the generator again or stop. Each repetition uses a fresh generator from the factory.
    
    Note: The supplied generator factory should be finite, otherwise each repetition will not complete.
    
    Args:
        probability: Probability (0-100) of repeating the generator on each iteration.
        factory: A generator factory.
        
    Example:
        >>> fact = Constant(1, 1)  # Yield 1 once
        >>> repeater = ProbabilityRepeater(50, fact)  # 50% chance to repeat
        >>> list(repeater())  # Result varies: could be [1] or [1, 1] or [1, 1, 1], etc.
    """

    def __init__(self, probability, factory):
        """Initialize the ProbabilityRepeater.
        
        Args:
            probability: The probability (0-100) of repeating on each iteration.
            factory: A generator factory.
        """
        self.probability = probability
        self.factory = factory

    def _generate(self):
        """Yield values from the generator factory, repeating based on random probability.
        
        Yields:
            Values from the generator factory. After each iteration, continues with supplied probability %.
            A new generator is created on each iteration
        """
        while random.randint(0, 100) < self.probability:
            yield from self.factory()


class SingleConstant(GeneratorFactory):
    """Yields a single constant value.
    
    When called, returns a generator that yields the specified value once and then stops.
    Useful for fixed single-value outputs or as a building block in compositions.

    It is expected that the user will not use this directly as yielding a constant once is not very useful.
    Instead Constant is SingleConstant wrapped with a Repeater - see below.   
    
    Args:
        value: The constant value to yield once.
    Example:
        >>> single_const = SingleConstant(42)
        >>> list(single_const())
        [42]
    """

    def __init__(self, value):
        """Initialize the SingleConstant.
        
        Args:
            value: The constant value to yield.
        """
        self.value = value

    def _generate(self):
        """Yield the constant value once.
        
        Yields:
            The constant value a single time.
        """
        yield self.value


def Constant(value, *args):
    """A factory function that creates a generator factory yielding a constant value with flexible repetition.

    This function provides a convenient interface for creating generator factories that yield a constant value 
    with various repetition behaviors. The aditional argument determine how the constant value is repeated and is
    the same as for the Repeater class"""
    return Repeater(SingleConstant(value), *args)


class BasicWaveGeneratorFactory(GeneratorFactory):
    """Generator factory derived from a function that has configurable discretization and offset.
    
    Yields values according to a function that maps the interval [0, 1] to [0, 1]. The function is discretized into a 
    configurable number of steps and can be repeated multiple times. The function is treated as defining one complete
    cycle of a periodic function.
    
    As with SingleConstant it is expected that the user will more typically use this with a Repeater wrapper - see below.

    Args:
        func: A callable that takes a float in [0, 1] and returns a float in [0, 1]. 
        steps: the number of steps for one cycle of the periodic function (default 4) is either:
            int: the number of steps
            (low, hi): choose a random number in the range [low, hi]
        runs:  the number of cycles computed (default 1) is either:
            int: the number of steps
            (low, hi): choose a random number in the range [low, hi]
        offset: an offset for the start of the cycle (default 0.0)

    For symmetry reasons steps/steps range is modified so that the staps become a multiple of 4.
            
    Attributes:
        func: The supplied function.
        steps_is_int: True iff the steps argument is an int
        steps: the number of steps for one cycle of the periodic function (0 if not steps_is_int)
        low_steps_4: if not steps_is_int then this is the first element of steps divided by 4 (0 if steps_is_int)
        hi_steps_4: if not steps_is_int then this is the second element of steps divided by 4 (0 if steps_is_int)
        runs_is_int: True iff the steps argument is an int
        runs:  the number of cycles computed (0 if not runs_is_int)
        low_runs: if not runs_is_int then this is the first element of runs (0 if runs_is_int)
        hi_runs: if not runs_is_int then this is the second element of runs (0 if runs_is_int)
        offset: an offset for the start of the cycle (default 0.0)
        
        
    Example:
        >>> sine_wave = BasicWaveGeneratorFactory(sine_function, steps=16)
        >>> gen = sine_wave()
        >>> values = list(gen)
        >>> len(values)
        16
    """

    def __init__(self, func, steps=4, runs=1, offset=0.0):
        """Initialize the BasicWaveGeneratorFactory generator factory.
        
        Args:
            func: A callable that takes a float in [0, 1] and returns a float in [0, 1]. 
            steps: the number of steps for one cycle of the periodic function (default 4) is either:
                int: the number of steps
                (low, hi): choose a random number in the range [low, hi]
            runs:  the number of cycles computed (default 1) is either:
                int: the number of steps
                (low, hi): choose a random number in the range [low, hi]
            offset: an offset for the start of the cycle (default 0.0)    
        """
        self.func = func
        if isinstance(steps, int):
            self.steps_is_int = True
            self.steps = 4 * (steps // 4)
            self.low_steps_4 = 0
            self.hi_steps_4 = 0
        else:
            self.steps_is_int = False
            self.steps = 0
            self.low_steps_4 = steps[0] // 4
            self.hi_steps_4 = steps[1] // 4
        if isinstance(runs, int):
            self.runs_is_int = True
            self.runs = runs
            self.low_runs = 0
            self.hi_runs = 0
        else:
            self.runs_is_int = False
            self.runs = 0
            self.low_runs = runs[0]
            self.hi_runs = runs[1]
        self.offset = offset

    def _generate(self):
        """Generate one or more complete cycles of the waveform.
        
        Yields:
            Float values in [0, 1] from the waveform
            
        """
        if self.steps_is_int:
            steps = self.steps
        else:
            steps = 4 * random.randint(self.low_steps_4, self.hi_steps_4)
        if self.runs_is_int:
            runs = self.runs
        else:
            runs = random.randint(self.low_runs, self.hi_runs)
        step_slice = 1.0 / steps
        for _ in range(runs):
            for i in range(steps):
                position = (self.offset + i * step_slice) % 1.0
                yield self.func(position)


def WaveGeneratorFactory(func, *args, **kwargs):
    """A factory function that creates a generator factory yielding values from a wave factory with flexible repetition.

    This function provides a convenient interface for creating generator factories for waves 
    with various repetition behaviors. This factory is a BasicWaveGeneratorFactory wrapped in a Repeater factory.
    If repeats is given (defaults to prducing an infinite generator) it needs to be given as a keyword arg.
    The runs argument only needs to be set to anything other than the default of 1 if steps is chosen randomly as
    the repart part will take care of repition.

    Example:
        >>> sine_wave = BasicWaveGeneratorFactory(sine_function, steps=16, repeats = 2)
        >>> gen = sine_wave()
        >>> values = list(gen)
        >>> len(values)
        32
    """
    repeats = kwargs.pop('repeats', None)
    if repeats == 1:
        return BasicWaveGeneratorFactory(func, *args, **kwargs)
    return Repeater(BasicWaveGeneratorFactory(func, *args, **kwargs), repeats)


class TabledFunction:
    """This class is used to precompute fuction values and store them in a table and then look up values
    rather than compute the function.
    
    Args:
        func: a function defined on [0,1]
        power: a table (list) is constructed of size 2**power. The bigger power is the more accurate the calculation
        is at the expense of consuming more space.

    Attributes:
        table_size: the size of the table (2**power)
        table_size_1:  2**power-1
        table: a list of precomputed values
    """

    def __init__(self, func, power):
        """Args:
        func: a function defined on [0,1]
        power: a table (list) is constructed of size 2**power. The bigger power is the more accurate the calculation
        is at the expense of consuming more space.
        """
        self.func = func
        self.table_size = 2 ** power
        self.table_size_1 = self.table_size - 1
        self.table = []
        for index in range(self.table_size):
            self.table.append(self.func(index / self.table_size_1))

    def __call__(self, x):
        return self.table[round(x * self.table_size_1) & self.table_size_1]


class Tester:
    """Base class for testers used with TakeWhile.
    
    A Tester is used by TakeWhile to determine when to stop yielding values.
    When called, a Tester returns a callable that can be invoked repeatedly to test a condition.
    
    The design separates the tester factory (the Tester object itself) from the actual test function,
    allowing state to be reset for each new use of a TakeWhile generator.
    
    Subclasses should override __call__() to return a test function, and may override on_false()
    to perform cleanup when the test first returns False.
    """

    def __call__(self):
        """Create and return a fresh test function.
        
        Returns:
            A callable that takes no arguments and returns a boolean. The callable will be
            invoked repeatedly by TakeWhile until it returns False.
            
        Raises:
            NotImplementedError: Always, as this is an abstract method.
        """
        raise NotImplementedError('Subclasses must implement __call__')

    def on_false(self):
        """Called when the tester returns False for the first time.
        
        Override this method in subclasses to perform cleanup or state management when
        the test condition becomes false. The default implementation does nothing.
        """
        pass


class TakeWhile(GeneratorFactory):
    """Yields values while a test condition is true.
    
    When called, returns a generator that yields values from the supplied generator factory
    only while the supplied tester returns True. Once the tester returns False, the generator
    stops and the tester's on_false() method is called.
    
    This allows for sophisticated filtering and early termination based on custom conditions,
    including time-based or count-based limits.
    
    Args:
        tester: A Tester object that determines when to stop yielding.
        factory: A generator factory callable that produces generators.
        
    Example:
        >>> tester = CountTester(3)  # Stop after 3 values
        >>> gen = Constant(1)  # Infinite generator
        >>> take_while = TakeWhile(tester, gen)
        >>> list(take_while())
        [1, 1, 1]
    """

    def __init__(self, tester, factory):
        """Initialize the TakeWhile.
        
        Args:
            tester: A Tester instance.
            factory: A generator factory.
        """
        self.tester = tester
        self.factory = factory

    def _generate(self):
        """Yield values while the test condition is true.
        
        Yields:
            Values from the generator while the tester's test function returns True.
            After yielding stops, calls tester.on_false().
        """
        g = self.factory()
        test = self.tester()
        while test():
            yield next(g)
        self.tester.on_false()


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

    def __init__(self, limit):
        """Initialize the CountTester.
        
        Args:
            limit: The iteration limit.
        """
        self.limit = limit
        self.count = 0

    def __call__(self):
        """Create a fresh test function with counter reset.
        
        Returns:
            A callable that returns True while counter < limit, False when limit is reached.
        """
        self.count = 0

        def test_fun() ->bool:
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

    def __init__(self, limit_seconds):
        """Initialize the TimeoutTester.
        
        Args:
            limit_seconds: The time limit in seconds.
        """
        self.limit_seconds = limit_seconds

    def _get_time(self):
        """Get the current time in seconds.
        
        Override this method if running in an environment with a different time API
        (e.g., MicroPython). For standard Python, uses time.time(). For MicroPython,
        attempts to use mp_time.ticks_ms().
        
        Returns:
            Current time in seconds as a float.
        """
        if 'micropython' in sys.modules:
            return time.ticks_ms() / 1000.0
        else:
            return time.time()

    def __call__(self):
        """Create a fresh test function with timer reset.
        
        Returns:
            A callable that returns True if elapsed time < limit, False otherwise.
        """
        start_time = self._get_time()

        def test_fun() ->bool:
            return self._get_time() - start_time < self.limit_seconds
        return test_fun
