# pwm_leds.py

Short README for the PWM LED demo used with a Raspberry Pi Pico.

**Purpose:**
- Demonstrates independent PWM control of up to 16 LEDs (8 PWM slices × 2 channels) on a Raspberry Pi Pico. This is an updated version
of the corresponding program in the RPi-Pico repository using the generator builder tools in this repository and with a little more complex behaviours. See youtube https://youtube.com/shorts/wqvX2MKz4js for an example run of the previous program.

**Features:**
- Configures 16 PWM channels at 1 kHz and provides several LED behaviour sets driven by generator factories.
- Includes: randomized sequences, repeating sine-wave generators, and a colour-rotation demo (red / blue / yellow).
- A single push button (Pin 16) cycles between control sets.


Key variables & behaviour (see implementation in [pwm_leds.py](pwm_leds/pwm_leds.py)):

- `MAX_DUTY` / `float2u16()` — helper for mapping 0.0–1.0 floats to 16-bit PWM duty values.
- `leds` — list of `PWM(Pin(...))` objects for the mapped pins; each is initialized to `freq(1000)`.
- `led_controls` — three control sets:
	- randomized sequences using generator factories
	- per-LED delayed sine waves
	- colour-rotation demo where red/blue/yellow groups take turns following a sine wave
- `STEP_TIME` — milliseconds per step (default `10` ms). The main loop advances generators and updates duties.
- Button on Pin 16 toggles the active control set (debounced in software, ~500 ms).

Dependencies
- This script uses the local modules `float_generator_mp.py` and `generator_builder_mp.py` which are included in the repository. It expects to run on MicroPython (Raspberry Pi Pico / RP2040).

Usage
- Copy the repository files to your Pico (via Thonny, rshell, ampy, mpremote, etc.).
- Ensure LEDs have appropriate current-limiting resistors and are wired to the appropriate pins.
- Open and run `pwm_leds.py` on the board. Press the button wired to Pin 16 (to GND) to cycle control sets.
- In order to run the program automatically on power up save `pwm_leds.py` as `main.py` on the Pico.

Safety and troubleshooting
- Verify wiring and resistor values before powering the board. Avoid driving LEDs without resistors.
- If PWM updates appear slow try decreasing `STEP_TIME`
