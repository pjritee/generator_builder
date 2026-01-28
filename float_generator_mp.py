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


class SineWave(gb.GeneratorBuilder):
    """A class that, when called, returns a generator that yields values in a 
    sine wave pattern in the range [0,1] for one cycle."""

    def __init__(self, steps):
        """steps - the number of steps (yielded values) in the sine wave cycle"""
        self.steps = steps

    def _generate(self):
        step_slice = 2 * math.pi / self.steps
        for i in range(self.steps):
            yield (math.sin(i * step_slice) + 1) / 2


class SawtoothWave(gb.GeneratorBuilder):
    """A class that, when called, returns a generator that yields values in a 
    sawtooth wave pattern in the range [0,1] for one cycle."""

    def __init__(self, steps):
        """steps - the number of steps (yielded values) in the sawtooth wave cycle.
        steps is changed to 1 + (steps//4)*4 in order to simplify the implementation."""
        self.quater_steps = steps // 4

    def _generate(self):
        quater_steps = self.quater_steps
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
        """steps - the number of steps (yielded values) in the square wave cycle.
        steps is rounded up to the nearest multiple of 2 in order to simplify the implementation."""
        self.steps = (steps + 1) // 2 * 2

    def _generate(self):
        half_steps = self.steps // 2
        for i in range(half_steps):
            yield 1.0
        for i in range(half_steps):
            yield 0.0


class Constant(gb.GeneratorBuilder):
    """A class that, when called, returns a generator that yields a constant value
    indefinitely."""

    def __init__(self, value):
        """value - the constant value to yield"""
        if not 0.0 <= value <= 1.0:
            raise ValueError('Constant value must be in the range [0,1]')
        self.value = value

    def _generate(self):
        while True:
            yield self.value


class ConstantFor(gb.GeneratorBuilder):
    """A class that, when called, returns a generator that yields a constant value
    for a specified number of steps."""

    def __init__(self, value, steps):
        """value - the constant value to yield
        steps - the number of steps (yielded values)"""
        if not 0.0 <= value <= 1.0:
            raise ValueError('ConstantFor value must be in the range [0,1]')
        self.value = value
        self.steps = steps

    def _generate(self):
        for _ in range(self.steps):
            yield self.value


if __name__ == '__main__':
    print('Testing float generators...')
    print('\n1. Testing SineWave:')
    sine_gen = SineWave(10)
    values = list(sine_gen())
    print(f'SineWave (10 steps): {[round(v, 2) for v in values]}')
    assert len(values) == 10
    assert all(0.0 <= v <= 1.0 for v in values)
    print('\n2. Testing SawtoothWave:')
    sawtooth_gen = SawtoothWave(10)
    values = list(sawtooth_gen())
    print(f'SawtoothWave output: {[round(v, 2) for v in values]}')
    assert len(values) == 9
    assert all(0.0 <= v <= 1.0 for v in values)
    assert 1.0 in values and 0.0 in values
    print('\n3. Testing SquareWave:')
    square_gen = SquareWave(10)
    values = list(square_gen())
    print(f'SquareWave output: {values}')
    assert len(values) == 10
    assert all(v in [0.0, 1.0] for v in values)
    high_count = sum(1 for v in values if v == 1.0)
    low_count = sum(1 for v in values if v == 0.0)
    assert high_count == low_count
    print('\n4. Testing Constant:')
    const_gen = Constant(0.5)
    values = [next(const_gen()) for _ in range(5)]
    print(f'Constant (0.5): {values}')
    assert all(v == 0.5 for v in values)
    print('\n5. Testing ConstantFor:')
    const_for_gen = ConstantFor(0.75, 5)
    values = list(const_for_gen())
    print(f'ConstantFor (0.75, 5 steps): {values}')
    assert len(values) == 5
    assert all(v == 0.75 for v in values)
    print('\n6. Testing value ranges:')
    generators = [('SineWave', SineWave(100)), ('SawtoothWave',
        SawtoothWave(100)), ('SquareWave', SawtoothWave(100)), ('Constant',
        Constant(0.3)), ('ConstantFor', ConstantFor(0.7, 100))]
    for name, gen_builder in generators:
        gen = gen_builder()
        limit = 100
        for i, value in enumerate(gen):
            if i >= limit:
                break
            assert 0.0 <= value <= 1.0, f'{name} produced value {value} outside [0,1]'
        print(f'{name}: All values in [0,1]')
    print('\n7. Testing invalid Constant values:')
    try:
        Constant(-0.1)
        assert False, 'Should reject negative value'
    except ValueError as e:
        print(f'Correctly rejected negative: {e}')
    try:
        Constant(1.1)
        assert False, 'Should reject value > 1'
    except ValueError as e:
        print(f'Correctly rejected > 1: {e}')
    print('\n8. Testing invalid ConstantFor values:')
    try:
        ConstantFor(-0.1, 5)
        assert False, 'Should reject negative value'
    except ValueError as e:
        print(f'Correctly rejected negative: {e}')
    try:
        ConstantFor(1.5, 5)
        assert False, 'Should reject value > 1'
    except ValueError as e:
        print(f'Correctly rejected > 1: {e}')
    print('\nAll tests completed!')
