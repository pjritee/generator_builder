# Generator Builder

A small collection of generator-builder utilities and helpers for creating
reusable Python generator components (for example, to drive PWM LEDs). This project 
evolved from the PWM example in the RPi-Pico repository.

**Overview**
- **What:** A set of tiny classes that build generators (sequencers, repeaters,
  choosers, take-while helpers) and a collection of float-valued
  generators such as sine, sawtooth, square, constant.
- **Why:** Make it easy to compose and reuse generator behaviour across
  applications, with a MicroPython-friendly option by stripping type hints.

**Repository Files**
- **generator_builder.py:** Core generator-builder classes and example
  usage and tests.
- **float_generator.py:** Concrete float-producing generators such as sine, sawtooth,
  square, constant, constant-for.
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


**License**
- MIT — see the header in `generator_builder.py` for the full text.

