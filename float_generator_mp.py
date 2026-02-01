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
import generator_builder_mp as gb
import math
import random


class Wave(gb.GeneratorFactory):
    """A class that, when called, returns a generator that yields values according to
    the provided wave (cyclic) function in the range [0,1] for one cycle."""

    def __init__(self, wave_func, steps, offset=0.0, runs=1):
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
            self.steps = steps // 4 * 4
            self.is_random = False
        else:
            self.steps = steps[0] // 4, steps[1] // 4
            self.is_random = True
        self.is_random = isinstance(steps, tuple)
        self.offset = offset
        self.runs = runs

    def _a_cycle_generator(self):
        if self.is_random:
            num_steps = 4 * random.randint(self.steps[0], self.steps[1])
        else:
            num_steps = self.steps
        step_slice = 1.0 / num_steps
        for i in range(num_steps):
            position = (self.offset + i * step_slice) % 1.0
            yield self.wave_func(position)

    def _generate(self):
        if self.runs == 0:
            while True:
                yield from self._a_cycle_generator()
        else:
            for _ in range(self.runs):
                yield from self._a_cycle_generator()


TWO_PI = 2 * math.pi


def sine_function(x):
    """A sine wave function that maps [0,1] to [0,1]."""
    return (math.sin(TWO_PI * x) + 1) / 2


def square_wave_function(x):
    """A square wave function that maps [0,1] to [0,1]."""
    return 1.0 if x < 0.5 else 0.0


def sawtooth_wave_function(x):
    """A sawtooth wave function that maps [0,1] to [0,1]."""
    if x < 0.25:
        return 0.5 + 2 * x
    elif x < 0.75:
        return 1.5 - 2 * x
    else:
        return 2 * (x - 0.75)


def sine_wave_factory(steps, offset=0.0, runs=1):
    """Returns a generator factory that creates a sine wave generator."""
    return Wave(sine_function, steps, offset, runs)


def square_wave_factory(steps, offset=0.0, runs=1):
    """Returns a generator factory that creates a square wave generator."""
    return Wave(square_wave_function, steps, offset, runs)


def sawtooth_wave_factory(steps, offset=0.0, runs=1):
    """Returns a generator factory that creates a sawtooth wave generator."""
    return Wave(sawtooth_wave_function, steps, offset, runs)
