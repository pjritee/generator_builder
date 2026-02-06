# Usage Examples

We assume `set_brightness` has been defined appropriately.

## LED Brightness Control

Smoothly fade a LED up and down:

```python
from waveforms import sine_wave_factory
from generator_builder import Repeater

# Create infinite sine wave cycles
sine = sine_wave_factory(50)

for brightness in sine():  # runs indefinitely
    set_brightness(brightness)  # 0.0 to 1.0
    time.sleep(0.01)
```

## Multiple LEDs with Different Patterns

Control multiple LEDs with different waveforms:

```python
from waveforms import sine_wave_factory, square_wave_factory
from generator_builder import Repeater

# LED 1: smooth sine wave
sine = sine_wave_factory(50)

# LED 2: square wave blink
square = square_wave_factory(20)

leds_control = [(led1, sine()), (leds2, square())]

while True:
    for led, gen in leds_control:
        led.set_brightness(next(gen))
        time.sleep(0.01)

```

## Time-Limited Sequences

Create sequences that stop after a timeout:

```python
from generator_builder import (
    Sequencer, TakeWhile, TimeoutTester,
    Constant
)
from waveforms import sine_wave_factory

# Run for 5 seconds max
tester = TimeoutTester(5.0)

sequence = TakeWhile(
    tester,
    Repeater(Sequencer([
        sine_wave_factory(20, repeater_arg=1), # one cycle of sine
        Constant(0.5, 50),  # Hold at 50% brightness for 50 steps
        Constant(0.0, 50),  # Turn off
    ]))
)

for value in sequence():
    set_brightness(value)
```

## Random Pattern Selection

Alternate between patterns randomly:

```python
from generator_builder import (
    Repeater, Chooser, TakeWhile, CountTester
)
from waveforms import (
    sine_wave_factory, square_wave_factory,
    sawtooth_wave_factory
)

# Create multiple pattern factories
patterns = Chooser([
    sine_wave_factory(50, repeater_arg=10),
    square_wave_factory(20, repeater_arg=10),
    sawtooth_wave_factory(30, repeater_arg=10),
])

# Run 3 random selections
test = CountTester(300)  # Adjust based on expected steps
sequence = TakeWhile(test, Repeater(patterns))

for value in sequence():
    set_brightness(value)
```


## Pulse Train with Random Duration

Create pulses with random lengths:

```python
from generator_builder import ProbabilityRepeater, Constant, Sequencer

# One pulse: high then low
pulse = Sequencer([
    Constant(1.0, 20),  # High for 20 steps
    Constant(0.0, 20),  # Low for 20 steps
])

# Repeat randomly with 75% probability
train = ProbabilityRepeater(75, pulse)

for value in train():
    set_brightness(value)
    
```

## MicroPython Examples

Control PWM LEDs on Raspberry Pi Pico:

```python
from machine import Pin, PWM
import generator_builder_mp as gb
import waveform_mp as fg

# Setup PWM
led = PWM(Pin(15))
led.freq(1000)  # 1 kHz

# Create pattern
sine = fg.sine_wave_factory(100)

# Generate and apply
for brightness in sine():
    duty = int(brightness * 65535)
    led.duty_u16(duty)
```

## Synchronized Multi-LED Control

Offset different LEDs for visual effect:

```python
from waveforms_mp import sine_wave_factory
from generator_builder_mp import Repeater

led_configs = [
    (led1, 0.0),    # Start at 0
    (led2, 0.33),   # Start at 1/3 through
    (led3, 0.66),   # Start at 2/3 through
]

generators = [
    (led, sine_wave_factory(100, offset=offset)())
    for led, offset in led_configs
]

# Run
while True:
    for led, gen in generators:
        duty = int(next(gen)* 65535)
        led.duty_u16(duty)
        time.sleep(0.01)
```

## Breathing LED Effect

Classic "breathing" effect using sine wave:

```python
from waveforms_mp import sine_wave_factory
from generator_builder_mp import Repeater
import time

# Slow sine wave for breathing
breathing = sine_wave_factory(200)

min_brightness = 0.1
max_brightness = 1.0

for normalized_value in breathing():
    # Scale to min/max range
    brightness = min_brightness + normalized_value * (max_brightness - min_brightness)
    duty = int(brightness* 65535)
    led.duty_u16(duty)
    time.sleep(4)  # 4 second breathing cycle
```
