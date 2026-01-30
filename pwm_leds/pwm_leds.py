
"""
This is an experiment with 16 independent PWM control_generatorled LEDs on a Raspberry Pi Pico.

From  https://deepbluembedded.com/raspberry-pi-pico-w-pinout-diagram-gpio-guide/ :
The Raspberry Pi Pico has 8 independent PWM generators, called slices. Each slice has two channels (A and B), which gives us a total of 16 PWM channels.
 

Pin mapping:
  0    0A
  1    0B
  2    1A
  3    1B
  4    2A
  5    2B
  22   3A
  7    3B 
  8    4A
  9    4B
  26   5A
  27   5B
  28   6A
  13   6B
  14   7A   
  15   7B
 
"""


from machine import Pin, PWM
import time
import random
import math
import float_generator_mp as fg
import generator_builder_mp as gb

MAX_DUTY = 65535
HALF_MAX_DUTY = 32768

leds = [
    PWM(Pin(0)),    # 0A   R
    PWM(Pin(1)),    # 0B   B   
    PWM(Pin(2)),    # 1A   Y 
    PWM(Pin(3)),    # 1B   R 
    PWM(Pin(4)),    # 2A   Y 
    PWM(Pin(5)),    # 2B   R 
    PWM(Pin(7)),    # 3B   B
    PWM(Pin(8)),    # 4A   Y
    PWM(Pin(9)),    # 4B   B 
    PWM(Pin(13)),   # 6B   Y
    PWM(Pin(14)),   # 7A   R
    PWM(Pin(15)),   # 7B   B
    PWM(Pin(28)),   # 6A   R
    PWM(Pin(27)),   # 5B   B 
    PWM(Pin(26)),   # 5A   Y 
    PWM(Pin(22))    # 3A   R
    ]

red_leds = [leds[0], leds[3],leds[5],leds[10],leds[12],leds[15]]
blue_leds = [leds[1],leds[6],leds[8],leds[11],leds[13]]
yellow_leds = [leds[2],leds[4],leds[7],leds[9],leds[14]]
            
leds_array = [leds[0:4], leds[4:8], leds[8:12], leds[12:16]]

# Initialize PWM frequencies
for led in leds:
    led.freq(1000)	

def float2u16(value: float) -> int:
    """Convert a float in the range 0.0 to 1.0 to a u16 value for PWM duty cycle."""
    if value <= 0.0:
        return 0
    elif value >= 1.0:
        return MAX_DUTY
    else:
        return round(value * MAX_DUTY)   
         
# Example generator sequences for each LED
# A factory that creates a generator producing a sequence consisting of:
#   - An initial delay of between 20 and 100 steps (random)
#   - A repeating sequence consisting of:
#       - A random square wave of length between 50 and 100 steps with a 20% chance of repeating
#       - A sine wave of length between 100 and 300 steps with a 70% chance of repeating
#       - An 'on' generator for 50 steps with a 25% chance of repeating
generator_factory = gb.Sequencer([
    gb.ConstantFor(0.0, random.randint(20,100)),
    gb.Repeater(gb.Sequencer([
        # A random square wave whose length is between 50 and 100 steps, with a 20% chance of repeating
        gb.RandomRepeater(20, fg.SquareWave((50, 100))),
        # A sine wave  whose length is between 100 and 300 steps, with a 70% chance of repeating
        gb.RandomRepeater(70, fg.SineWave((100, 300))),
        # An on generator for 50 steps with a 25% chance of repeating
        gb.RandomRepeater(25, gb.ConstantFor(1.0, 50))
        ]))
    ])

# A factory that creates a sine wave generator of length 200 steps
sine_wave_factory = fg.SineWave(400)

# For the following generator we want to have the red LEDs follow a sine wave for a specified time with the other LEDs off.
# Then we want the blue LEDs to follow the sine wave with the other LEDs off, and then the yellow LEDs to follow the sine wave with the other LEDs off.
# To do this we write testers that can communicate which colour is to be active. When a timer tester expires we need to set a 
# diferent set of LEDs active. This needs to be done in such a way that all the testers see the same state.
# This can be done by having a shared state object that all the testers can access.

# We let 0,1,2 represent red, blue, yellow active respectively and define the following simple data class to hold the state.

class ColourState:
    def __init__(self):
        self.active_colour = 0  # Start with red active

    def set_colour(self, colour: int):
        self.active_colour = colour 

colour_state = ColourState()

# We now need to define two testers:
# 1. A tester that tests whether a specified colour is not active
class ColourTester(gb.Tester):
    def __init__(self, colour_state: ColourState, colour: int):
        self.colour_state = colour_state
        self.colour = colour

    def __call__(self) -> Callable[[], bool]:
        def test_fun() -> bool:
            return self.colour_state.active_colour != self.colour
        return test_fun
    
    
# 2. A tester that after a specified time changes the active colour to the next one
class ColourTimerTester(gb.TimeoutTester):
    def __init__(self, colour_state: ColourState, colour: int, limit_seconds: float):
        super().__init__(limit_seconds)
        self.colour_state = colour_state
        self.colour = colour

    def on_false(self):
        # Change the active colour to the next one
        # Note that will be called "at the same time" by all instances of this tester when their timeouts occur and
        # they will all set the same next colour.
        next_colour = (self.colour + 1) % 3
        self.colour_state.set_colour(next_colour)

def make_timer_testers(limit_seconds: float) -> list[ColourTimerTester]:
    """Create a list of ColourTimerTesters for each colour with the specified limit_seconds."""
    return [ColourTimerTester(colour_state, colour, limit_seconds) for colour in range(3)]

def make_colour_testers() -> list[ColourTester]:
    """Create a list of ColourTesters for each colour."""
    return [ColourTester(colour_state, colour) for colour in range(3)]

colour_testers = make_colour_testers()
timer_testers = make_timer_testers(5.0)  # Change colour every 5 seconds
zero_factory = gb.Repeater(gb.Constant(0.0))
repeating_sine_factory = gb.Repeater(sine_wave_factory)

# Now we can define the generator factories for this behaviour
def rgb_generator_factory(colour: int) -> gb.GeneratorFactory[float]: 
    """Returns a generator factory that creates a generator that produces a sine wave
    when the specified colour is active and 0.0 otherwise."""
    
    return gb.Repeater(gb.Sequencer([
        gb.TakeWhile(colour_testers[colour], zero_factory),
        gb.TakeWhile(timer_testers[colour], repeating_sine_factory)
        
        ]))

# Create a list of pairs each consisting of a led and a generator to be used for that led.
# For LEDs that are to have the same behaviour we can reuse the same generator factory for all the LEDs since each call 
# to the factory creates a new generator instance.
led_controls = [
    
    # First control set: each LED gets a sequence generator consisting of a random delay followed by a sequence generator 
    # created by the generator_factory defined above
    [(led, generator_factory()) for led in leds],

     # Second control set: each LED gets a sequence generator consisting of an increasing delay followed by a sine wave generator
    [(led, gb.Sequencer([gb.ConstantFor(0.0, i*20), sine_wave_factory])()) for i, led in enumerate(leds)],

    # Third control set: red, blue, yellow LEDs take turns to follow a sine wave while the other LEDs are off
    [(led, rgb_generator_factory(0)()) for led in red_leds] +
    [(led, rgb_generator_factory(1)()) for led in blue_leds] +
    [(led, rgb_generator_factory(2)()) for led in yellow_leds]
]

# Initialize all LEDs to off
for led in leds:
    led.duty_u16(0)

# Button to switch between control sets
up_pressed = False
last_pressed = time.ticks_ms()
def handle_press(arg):
    global up_pressed, last_pressed
    if time.ticks_diff(time.ticks_ms(), last_pressed) > 500:   
        last_pressed = time.ticks_ms()
        print("press", arg)
        up_pressed = True
up_button = Pin(16, Pin.IN, Pin.PULL_UP)
up_button.irq(trigger=Pin.IRQ_FALLING, handler=handle_press)

# Processing all the LEDs in a loop takes around 2ms and so setting this to 
# anything about that will give consistent timing.
STEP_TIME = 10  # milliseconds per step

# With STEP_TIME of 10ms, a sine wave of length 200 will have a period of about 2 seconds.
index = 0
while True:
    start = time.ticks_ms()
    if up_pressed:
        up_pressed = False
        if index == 0:
            index = 1
        else:
            index = 0
    
    
    # Step each control generator
    
    for led, gen in led_controls[index]:
        led.duty_u16(float2u16(next(gen)))
    
    # Wait until the next step time
    time.sleep_ms( STEP_TIME + start - time.ticks_ms())
