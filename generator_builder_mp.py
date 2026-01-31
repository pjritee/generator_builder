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
"""
Each GeneratorFactory object is a factory that, when called, returns a generator yielding values of type T.

Many of the subclasses defined below are 'higher order' in that they take one or more generator factories
as parameters and return a new generator factory that combines them in some way.
"""


class GeneratorFactory:
    """Base class for generator factories. Subclasses must implement the _generate method."""

    def __call__(self):
        return self._generate()

    def _generate(self):
        raise NotImplementedError('Subclasses must implement _generate')


class Sequencer(GeneratorFactory):
    """A class that, when called, returns a generator that iterates through the supplied list of generators,
    yielding from each in turn. Note that each generator (except possibly the last one) should be finite."""

    def __init__(self, generators):
        self.generators = generators

    def _generate(self):
        for generator in self.generators:
            yield from generator()


class Chooser(GeneratorFactory):
    """A class that, when called, returns a generator that randomly chooses from the supplied list of generators,
    yielding from the chosen generator."""

    def __init__(self, generators):
        self.generators = generators

    def _generate(self):
        yield from random.choice(self.generators)()


class RepeaterFor(GeneratorFactory):
    """A class that, when called, returns a generator that yields from the supplied generator
    the supplied number of times. Note that the supplied generator should be finite."""

    def __init__(self, number, generator):
        self.number = number
        self.generator = generator

    def _generate(self):
        for _ in range(self.number):
            yield from self.generator()


class RandomRepeater(GeneratorFactory):
    """A class that, when called, returns a generator that yields from the supplied generator
    repeatedly with the supplied probability. Note that the supplied generator should be finite."""

    def __init__(self, probability, generator):
        self.probability = probability
        self.generator = generator

    def _generate(self):
        while random.randint(0, 100) < self.probability:
            yield from self.generator()


class Repeater(GeneratorFactory):
    """A class that, when called, returns a generator that yields from the supplied generator
    forever. Note that the supplied generator should be finite."""

    def __init__(self, generator):
        self.generator = generator

    def _generate(self):
        while True:
            yield from self.generator()


class Tester:
    """A base class for generating testers to be used in TakeWhile"""

    def __call__(self):
        raise NotImplementedError('Subclasses must implement __call__')

    def on_false(self):
        """Called when the tester returns false. Override in subclasses to provide behaviour on false."""
        pass


class TakeWhile(GeneratorFactory):
    """A class that, when called, returns a generator that yields from the supplied generator
    while the supplied tester returns true when called."""

    def __init__(self, tester, generator):
        self.tester = tester
        self.generator = generator

    def _generate(self):
        g = self.generator()
        test = self.tester()
        while test():
            yield next(g)
        self.tester.on_false()


class Constant(GeneratorFactory):
    """A class that, when called, returns a generator that yields a constant value
    indefinitely."""

    def __init__(self, value):
        """value - the constant value to yield"""
        self.value = value

    def _generate(self):
        while True:
            yield self.value


class ConstantFor(GeneratorFactory):
    """A class that, when called, returns a generator that yields a constant value
    for a specified number of steps."""

    def __init__(self, value, steps):
        """value - the constant value to yield
        steps - the number of steps (yielded values)"""
        self.value = value
        self.steps = steps

    def _generate(self):
        for _ in range(self.steps):
            yield self.value


class CountTester(Tester):
    """A tester that returns True while a counter is below a limit."""

    def __init__(self, limit):
        self.limit = limit
        self.count = 0

    def __call__(self):
        self.count = 0

        def test_fun() ->bool:
            result = self.count < self.limit
            self.count += 1
            return result
        return test_fun


class TimeoutTester(Tester):
    """A tester that returns True while elapsed time is below a limit."""

    def __init__(self, limit_seconds):
        self.limit_seconds = limit_seconds

    def _get_time(self):
        """Override this method if running in an environment with a different time API"""
        if 'micropython' in sys.modules:
            return mp_time.ticks_ms() / 1000.0
        else:
            return time.time()

    def __call__(self):
        start_time = self._get_time()

        def test_fun() ->bool:
            return self._get_time() - start_time < self.limit_seconds
        return test_fun
