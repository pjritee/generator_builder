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


class SineWave(gb.GeneratorBuilder):
    """A class that, when called, returns a generator that yields values in a 
    sine wave pattern in the range [0,1] for one cycle."""

    def __init__(self, steps):
        """steps - the number of steps (yielded values) in the sine wave cycle if
        an integer is provided. If a tuple is provided, it is interpreted as (min_steps, max_steps)
        and a random number of steps in that range is chosen each time the generator is created."""
        self.steps = steps
        self.is_random = isinstance(steps, tuple)

    def _generate(self):
        if self.is_random:
            num_steps = random.randint(self.steps[0], self.steps[1])
        else:
            num_steps = self.steps
        step_slice = 2 * math.pi / (num_steps - 1)
        for i in range(num_steps):
            yield (math.sin(i * step_slice) + 1) / 2


class SawtoothWave(gb.GeneratorBuilder):
    """A class that, when called, returns a generator that yields values in a 
    sawtooth wave pattern in the range [0,1] for one cycle."""

    def __init__(self, steps):
        """steps - the number of steps (yielded values) in the sawtooth wave cycle if
        an integer is provided. If a tuple is provided, it is interpreted as (min_steps, max_steps)
        and a random number of steps in that range is chosen each time the generator is created.
        steps is changed to 1 + (steps//4)*4 in order to simplify the implementation."""
        self.steps = steps
        self.is_random = isinstance(steps, tuple)

    def _generate(self):
        if self.is_random:
            num_steps = random.randint(self.steps[0], self.steps[1])
        else:
            num_steps = self.steps
        quater_steps = num_steps // 4
        delta = 0.5 / quater_steps
        value = 0.5
        yield value
        for i in range(quater_steps - 1):
            value += delta
            yield value
        yield 1.0
        value = 1.0
        for i in range(2 * quater_steps - 1):
            value -= delta
            yield value
        yield 0.0
        value = 0.0
        for i in range(quater_steps - 1):
            value += delta
            yield value
        yield 0.5


class SquareWave(gb.GeneratorBuilder):
    """A class that, when called, returns a generator that yields values in a 
    square wave pattern in the range [0,1] for one cycle."""

    def __init__(self, steps):
        """steps - the number of steps (yielded values) in the square wave cycle if an integer is provided. 
        If a tuple is provided, it is interpreted as (min_steps, max_steps)
        and a random number of steps in that range is chosen each time the generator is created..
        steps is rounded up to the nearest multiple of 2 in order to simplify the implementation."""
        self.steps = steps
        self.is_random = isinstance(steps, tuple)

    def _generate(self):
        if self.is_random:
            num_steps = random.randint(self.steps[0], self.steps[1])
        else:
            num_steps = self.steps
        half_steps = (num_steps + 1) // 2
        for i in range(half_steps):
            yield 1.0
        for i in range(half_steps):
            yield 0.0


if __name__ == '__main__':
    print('Testing float generators...')
    print('\n1. Testing SineWave:')
    sine_gen = SineWave(10)
    values = list(sine_gen())
    print(f'SineWave (10 steps): {[round(v, 2) for v in values]}')
    assert len(values) == 10
    assert all(0.0 <= v <= 1.0 for v in values)
    print('\n2. Testing SineWave with step range:')
    sine_rand = SineWave((5, 15))
    for _ in range(3):
        values = list(sine_rand())
    print(f'SineWave output: {[round(v, 2) for v in values]}')
    assert 5 <= len(values) <= 15
    assert all(0.0 <= v <= 1.0 for v in values)
    print('\n3. Testing SawtoothWave:')
    sawtooth_gen = SawtoothWave(10)
    values = list(sawtooth_gen())
    print(f'SawtoothWave output: {[round(v, 2) for v in values]}')
    assert len(values) == 9
    assert all(0.0 <= v <= 1.0 for v in values)
    assert 1.0 in values and 0.0 in values
    print('\n4. Testing SawtoothWave with step range:')
    sawtooth_rand = SawtoothWave((8, 16))
    values = list(sawtooth_rand())
    print(f'SawtoothWave output: {[round(v, 2) for v in values]}')
    assert 8 <= len(values) <= 16
    assert all(0.0 <= v <= 1.0 for v in values)
    print('\n5. Testing SquareWave:')
    square_gen = SquareWave(10)
    values = list(square_gen())
    print(f'SquareWave output: {values}')
    assert len(values) == 10
    assert all(v in [0.0, 1.0] for v in values)
    high_count = sum(1 for v in values if v == 1.0)
    low_count = sum(1 for v in values if v == 0.0)
    assert high_count == low_count
    print('\n6. Testing SquareWave with step range:')
    square_rand = SquareWave((6, 12))
    values = list(square_rand())
    print(f'SquareWave output: {values}')
    assert 6 <= len(values) <= 12
    assert all(v in [0.0, 1.0] for v in values)
    high_count = sum(1 for v in values if v == 1.0)
    low_count = sum(1 for v in values if v == 0.0)
    assert high_count == low_count
    print('\n7. Testing Constant:')
    const_gen = gb.Constant(0.5)
    values = [next(const_gen()) for _ in range(5)]
    print(f'Constant (0.5): {values}')
    assert all(v == 0.5 for v in values)
    print('\n8. Testing ConstantFor:')
    const_for_gen = gb.ConstantFor(0.75, 5)
    values = list(const_for_gen())
    print(f'ConstantFor (0.75, 5 steps): {values}')
    assert len(values) == 5
    assert all(v == 0.75 for v in values)
    print('\n9. Testing value ranges:')
    generators = [('SineWave', SineWave(100)), ('SawtoothWave',
        SawtoothWave(100)), ('SquareWave', SawtoothWave(100)), ('Constant',
        gb.Constant(0.3)), ('ConstantFor', gb.ConstantFor(0.7, 100))]
    for name, gen_builder in generators:
        gen = gen_builder()
        limit = 100
        for i, value in enumerate(gen):
            if i >= limit:
                break
            assert 0.0 <= value <= 1.0, f'{name} produced value {value} outside [0,1]'
        print(f'{name}: All values in [0,1]')
    print('\nAll tests completed!')
