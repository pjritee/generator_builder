
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
        return int(value * MAX_DUTY)   
         
# Example generator sequences for each LED
generators = [
    # A random square wave whose length is between 50 and 100 steps, with a 20% chance of repeating
    gb.RandomRepeater(20, fg.SquareWave((50, 100))),
    # A sine wave  whose length is between 100 and 300 steps, with a 70% chance of repeating
    gb.RandomRepeater(70, fg.SineWave((100, 300))),
    # An on generator for 50 steps with a 25% chance of repeating
    gb.RandomRepeater(25, gb.ConstantFor(1.0, 50)),
    ]

# Create a list of pairs each consisting of a led and a generator to be used for that led with each generator being a choice generator using 
# a random delay between 20 and 200 steps to stagger the starting times
led_controls = [
    
    # First control set: each LED gets a sequence generator consisting of a random delay followed by a choice of the above generators
    [(led, gb.AlwaysRepeater(gb.Sequencer([gb.ConstantFor(0.0, random.randint(20,100))]+generators))()) for led in leds],
     # Second control set: each LED gets a sequence generator consisting of an increasing delay followed by a sine wave generator
    [(led, gb.Sequencer([gb.ConstantFor(0.0, i*20), gb.AlwaysRepeater(fg.SineWave(200))])()) for i, led in enumerate(leds)]
]

# Initialize all LEDs to off
for led in leds:
    led.duty_u16(0)

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
