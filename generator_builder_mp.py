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


class GeneratorBuilder:
    """Base class for generator builders. Subclasses must implement the _generate method."""

    def __call__(self):
        return self._generate()

    def _generate(self):
        raise NotImplementedError('Subclasses must implement _generate')


class Sequencer(GeneratorBuilder):
    """A class that, when called, returns a generator that iterates through the supplied list of generators,
    yielding from each in turn."""

    def __init__(self, generators):
        self.generators = generators

    def _generate(self):
        for generator in self.generators:
            yield from generator()


class Chooser(GeneratorBuilder):
    """A class that, when called, returns a generator that randomly chooses from the supplied list of generators,
    yielding from the chosen generator."""

    def __init__(self, generators):
        self.generators = generators

    def _generate(self):
        yield from random.choice(self.generators)()


class Repeater(GeneratorBuilder):
    """A class that, when called, returns a generator that yields from the supplied generator
    the supplied number of times."""

    def __init__(self, number, generator):
        self.number = number
        self.generator = generator

    def __call__(self):
        return self._generate()

    def _generate(self):
        for _ in range(self.number):
            yield from self.generator()


class RandomRepeater(GeneratorBuilder):
    """A class that, when called, returns a generator that yields from the supplied generator
    repeatedly with the supplied probability."""

    def __init__(self, probability, generator):
        self.probability = probability
        self.generator = generator

    def _generate(self):
        while random.randint(0, 100) < self.probability:
            yield from self.generator()


class AlwaysRepeater(GeneratorBuilder):
    """A class that, when called, returns a generator that yields from the supplied generator
    forever."""

    def __init__(self, generator):
        self.generator = generator

    def _generate(self):
        while True:
            yield from self.generator()


class Tester:
    """A base class for generating testers to be used in TakeWhile"""

    def __call__(self):
        raise NotImplementedError('Subclasses must implement __call__')


class TakeWhile(GeneratorBuilder):
    """A class that, when called, returns a generator that yields from the supplied generator
    while the supplied condition is true."""

    def __init__(self, tester, generator):
        self.tester = tester
        self.generator = generator

    def _generate(self):
        g = self.generator()
        test = self.tester()
        while test():
            yield next(g)


if __name__ == '__main__':


    class ConstantGen(GeneratorBuilder):
        """A simple generator that always yields the same value."""

        def __init__(self, value):
            self.value = value

        def _generate(self):
            while True:
                yield self.value


    class RampGen(GeneratorBuilder):
        """A generator that yields values from start to end in steps."""

        def __init__(self, start, end, steps):
            self.start = start
            self.end = end
            self.steps = steps

        def _generate(self):
            step_size = (self.end - self.start) / self.steps
            current = self.start
            for _ in range(self.steps):
                yield current
                current += step_size


    class SineWaveGen(GeneratorBuilder):
        """A generator that yields values from a sine wave."""

        def __init__(self, amplitude=1.0, frequency=1.0, steps=100):
            self.amplitude = amplitude
            self.frequency = frequency
            self.steps = steps

        def _generate(self):
            import math
            for i in range(self.steps):
                yield self.amplitude * math.sin(2 * math.pi * self.
                    frequency * i / self.steps)


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
    print('Testing generator builders...')
    print('\n1. Testing sequencer:')
    seq_gen = Sequencer([ConstantGen(1.0), RampGen(0.0, 1.0, 5),
        ConstantGen(0.5)])
    values = []
    for i, val in enumerate(seq_gen()):
        values.append(round(val, 2))
        if len(values) >= 10:
            break
    print(f'Sequencer output: {values}')
    print('\n2. Testing chooser:')
    choose_gen = Chooser([ConstantGen(1.0), ConstantGen(2.0), ConstantGen(3.0)]
        )
    values = []
    for i in range(10):
        val = next(choose_gen())
        values.append(val)
    print(f'Chooser output (10 random choices): {values}')
    print('\n3. Testing repeater:')
    repeat_gen = Repeater(3, RampGen(0.0, 1.0, 3))
    values = []
    for val in repeat_gen():
        values.append(round(val, 2))
    print(f'Repeater output (3 times): {values}')
    print('\n4. Testing random_repeater:')
    random_repeat_gen = RandomRepeater(50, ConstantGen(1.0))
    values = []
    count = 0
    for val in random_repeat_gen():
        values.append(val)
        count += 1
        if count >= 20:
            break
    print(f'Random repeater output (up to 20 values): {values}')
    print('\n5. Testing always_repeater:')
    always_repeat_gen = AlwaysRepeater(ConstantGen(42.0))
    values = []
    for i, val in enumerate(always_repeat_gen()):
        values.append(val)
        if i >= 4:
            break
    print(f'Always repeater output (first 5): {values}')
    print('\n6. Testing take_while:')
    tester = CountTester(3)
    take_while_gen = TakeWhile(tester, ConstantGen(1.0))
    values = []
    for val in take_while_gen():
        values.append(val)
    print(f'Take while output (while counter < 3): {values}')
    print('\n7. Testing sine_wave_gen:')
    sine_gen = SineWaveGen(amplitude=1.0, frequency=1.0, steps=10)
    values = []
    for val in sine_gen():
        values.append(round(val, 2))
    print(f'Sine wave output (first 10 steps): {values}')
    print('\n8. Testing inheritance and callable interface:')


    class AlwaysTrueTester(Tester):

        def __call__(self):
            return True
    generators = [Sequencer([ConstantGen(1.0)]), Chooser([ConstantGen(1.0)]
        ), Repeater(1, ConstantGen(1.0)), RandomRepeater(100, ConstantGen(
        1.0)), AlwaysRepeater(ConstantGen(1.0)), TakeWhile(AlwaysTrueTester
        (), ConstantGen(1.0)), ConstantGen(1.0), RampGen(0.0, 1.0, 5),
        SineWaveGen()]
    for gen in generators:
        print(
            f'{gen.__class__.__name__}: isinstance(GeneratorBuilder) = {isinstance(gen, GeneratorBuilder)}'
            )
        gen_iter = gen()
        print(
            f"  Returns generator: {hasattr(gen_iter, '__iter__') and hasattr(gen_iter, '__next__')}"
            )
        gen_iter2 = gen()
        print(f'  Fresh generator each call: {gen_iter is not gen_iter2}')
    print('\nAll tests completed!')
