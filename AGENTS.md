# AGENTS.md - Ship's Bell Project

## Build/Test/Lint Commands
- **Lint**: `make pylint` or `pylint3 *.py tests/*.py`
- **Test all**: `make test` (runs pylint + unittest)
- **Test core**: `python3 -m unittest tests.test_ships_bell`
- **Test installers**: `python3 -m unittest tests.test_installers`
- **Test single**: `python3 -m unittest tests.test_ships_bell.TestShipsBell.test_method_name`
- **Coverage**: `make test_cover` (100% coverage required)
- **Clean**: `make clean`

## Code Style Guidelines
- **Language**: Python 3.3+
- **Imports**: Standard library imports first, then local imports
- **Classes**: PascalCase (e.g., `ShipsBell`, `ShipsBellError`)
- **Methods/Variables**: snake_case (e.g., `compute_strikes`, `start_time`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `SECONDS_PER_MINUTE`)
- **Error Handling**: Custom exceptions inherit from `Exception`, use specific error messages
- **Testing**: unittest framework, Mock for external dependencies, 100% coverage required
- **Docstrings**: Module-level docstrings required, method docstrings for complex logic
- **Pragma**: Use `# pragma: no cover` for main execution blocks
- **Pylint**: Must pass pylint3 checks, disable specific rules with inline comments when needed