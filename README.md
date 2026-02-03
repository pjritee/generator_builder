# Generator Builder


A small collection of generator-builder utilities and helpers for creating
reusable Python generator components (for example, to drive PWM LEDs). This project 
evolved from the PWM example in the `RPi-Pico` repository.

**Overview**
- **What:** A set of tiny classes that build generator factories (sequencers, repeaters,
  choosers, take-while helpers) that produce generators when called and a collection of float-valued
  generator factories such as sine, sawtooth, square, constant. The `Tester` class is
  designed to be used in the `TakeWhile` generator factory.
- **Why:** Make it easy to compose and reuse generator behaviour across
  applications, with a MicroPython-friendly option by stripping type hints. By designing the `Tester` class this way it is possible to write testers that communicate with other testers using a shared object of some kind. This could be used, for example, to program an oscillation between the behaviours of two collections of PWM controlled LEDs using a pair of timing testers and another pair of testers looking for a change to a shared object.

**Repository Files**
- **generator_builder.py:** Core generator-builder classes and example
  usage and tests.
- **float_generator.py:** Concrete float-producing generator factories such as sine, sawtooth,
  square, constant, constant-for.
- **generator_visualizer.py:** TkInter GUI application for testing and visualizing generators in real-time.
- **strip_type_hints.py:** Tool to remove Python type hints and `typing`
  imports to produce MicroPython-compatible source.
- **.gitignore:** Ignores Python cache files and pytest cache.

**Usage**
- Run the example/tests in `generator_builder.py`:

  ```bash
  python3 generator_builder.py
  ```

- Run the float generator checks:

  ```bash
  python3 float_generator.py
  ```

- Launch the Generator Visualizer (TkInter GUI):

  ```bash
  python3 generator_visualizer.py
  ```

  The visualizer provides:
  - **Code Editor**: Write or load Python code with a `get_generator()` function
  - **Live Canvas**: Real-time visualization of generator output as a waveform
  - **Interactive Controls**: Run, stop, and clear graphs; adjust max points (10-10000)
  - **Statistics**: View point count, min, max, and average values
  - **File Loading**: Load generator scripts from disk
  
  See the [full documentation](https://pjritee.github.io/generator_builder/api/generator_visualizer/) for examples and usage details.

**Stripping Type Hints for MicroPython**
- To produce a MicroPython-friendly copy of `generator_builder.py`, run:

  ```bash
  python3 strip_type_hints.py generator_builder.py generator_builder_mp.py
  ```

  The script removes `typing` imports, `TypeVar(...)` assignments and
  function/class annotations so the resulting file can be used on constrained
  interpreters.

**Git Hook / Automation**
- For local automation, add a git `pre-push` hook that runs the strip script and
  stages the generated file before pushing. See `.git/hooks/pre-push`.

**Documentation**
The project documentation is available at [https://pjritee.github.io/generator_builder](https://pjritee.github.io/generator_builder)

**License**
- MIT — see the header in `generator_builder.py` for the full text.

