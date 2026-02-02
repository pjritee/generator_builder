# Contributing

We welcome contributions to the Generator Builder project!

## How to Contribute

### Reporting Issues

Found a bug or have a suggestion? Please:

1. Check existing issues to avoid duplicates
2. Provide a clear description of the problem
3. Include steps to reproduce (if applicable)
4. Mention your Python version and environment

### Submitting Changes

1. **Fork** the repository
2. **Create a branch** for your changes
3. **Write tests** for new features
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

## Development Setup

```bash
# Clone the repository
git clone https://github.com/pjritee/generator_builder.git
cd generator_builder

# Run tests
python3 generator_builder.py
python3 float_generator.py

# Generate MicroPython versions
python3 strip_type_hints.py generator_builder.py generator_builder_mp.py
python3 strip_type_hints.py float_generator.py float_generator_mp.py
```

## Code Style

- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings to public classes and methods
- Keep functions focused and composable

## Documentation

- Update docstrings when modifying behavior
- Add examples for new features
- Update API documentation in `docs/api/`
- Keep the README and guides current

## Testing

- Test new features thoroughly
- Ensure MicroPython compatibility
- Test with the `_mp.py` versions
- Include both unit tests and integration examples

## License

All contributions are under the MIT License. By submitting a pull request, you agree to license your contribution under the MIT License.

Thank you for contributing! 🎉
