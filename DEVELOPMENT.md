# Development Guide for SunPower Home Assistant Integration

This guide will help new developers get started with contributing to the SunPower Home Assistant integration.

## Prerequisites

- Python 3.11 or higher
- Git
- A SunPower PVS system for testing (optional but recommended)

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/krbaker/hass-sunpower.git
cd hass-sunpower
```

### 2. Set Up Python Virtual Environment

Create and activate a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

Install the required packages for development:

```bash
# Install Home Assistant and integration dependencies
pip install homeassistant
pip install -r requirements-dev.txt

# If requirements-dev.txt doesn't exist, install common dependencies:
pip install pytest requests voluptuous
```

### 4. Install Pre-commit Hooks (Optional but Recommended)

Pre-commit hooks help maintain code quality:

```bash
pip install pre-commit
pre-commit install
```

## Project Structure

```text
hass-sunpower/
├── custom_components/sunpower/     # Main integration code
│   ├── __init__.py                 # Integration setup and coordinator
│   ├── config_flow.py             # Configuration flow (UI setup)
│   ├── const.py                   # Constants and sensor definitions
│   ├── entity.py                  # Base entity class
│   ├── sensor.py                  # Sensor platform implementation
│   ├── binary_sensor.py           # Binary sensor platform
│   ├── sunpower.py                # SunPower API client
│   ├── manifest.json              # Integration metadata
│   ├── strings.json               # UI strings
│   └── translations/              # Localization files
├── tests/                         # Test files
├── .vscode/                       # VS Code configuration
├── README.md                      # User documentation
└── DEVELOPMENT.md                 # This file
```

## Running Tests

### Test the SunPower API Client

The integration includes tests for the core API functionality:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_sunpower_api.py -v

# Run with coverage
python -m pytest tests/ --cov=custom_components/sunpower --cov-report=html
```

### Test Integration with Home Assistant

For integration testing with Home Assistant:

```bash
# Install Home Assistant in development mode
pip install homeassistant

# Create a test configuration
mkdir -p config/custom_components
ln -s $(pwd)/custom_components/sunpower config/custom_components/

# Run Home Assistant with test config
hass -c config --debug
```

## Development Workflow

### 1. Making Changes

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** to the appropriate files in `custom_components/sunpower/`

3. **Test your changes**:

   ```bash
   # Run tests
   source venv/bin/activate
   python -m pytest tests/ -v

   # Check code formatting
   pre-commit run --all-files
   ```

### 2. Testing Configuration Changes

If you modify the configuration flow (`config_flow.py`):

1. Delete any existing SunPower integration entries in Home Assistant
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "SunPower" and test the setup flow

### 3. Testing Sensor Changes

If you modify sensors (`sensor.py`, `binary_sensor.py`, `const.py`):

1. Restart Home Assistant or reload the integration
2. Check that entities appear correctly in Developer Tools → States
3. Verify data updates are working

## Common Development Tasks

### Adding a New Sensor

1. **Define the sensor** in `const.py`:

   ```python
   "NEW_SENSOR": {
       "field": "api_field_name",
       "title": "Display Name",
       "unit": UnitOfMeasurement.UNIT,
       "icon": "mdi:icon-name",
       "device": SensorDeviceClass.CLASS,
       "state": SensorStateClass.MEASUREMENT,
   }
   ```

2. **Test with real data** to ensure the field exists in API responses

3. **Update tests** if needed

### Modifying the Configuration Flow

1. **Update the schema** in `config_flow.py`:

   ```python
   DATA_SCHEMA = vol.Schema({
       vol.Required(CONF_HOST): str,
       vol.Optional(CONF_NEW_FIELD): str,
   })
   ```

2. **Update validation** in `validate_input()` function

3. **Test the flow** by adding the integration through the UI

### Debugging

#### Enable Debug Logging

Add to your Home Assistant `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.sunpower: debug
```

#### Common Debug Commands

```bash
# Check if integration loads
hass --script check_config -c config

# View logs in real-time
tail -f config/home-assistant.log | grep sunpower
```

## Testing Environment

### Mocking SunPower API

For development without a physical SunPower system, you can:

1. **Use the existing mock data** in tests
2. **Create a mock server** that responds to SunPower API endpoints
3. **Modify `sunpower.py`** to return sample data when in development mode

### Sample Test Data

The `samples/` directory contains example API responses that can be used for testing.

## Code Quality Standards

### Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for automatic formatting
- Use type hints where possible
- Add docstrings to functions and classes

### Testing Requirements

- All new features should include tests
- API client functions must have unit tests
- Configuration flow changes should be manually tested
- Maintain test coverage above 80%

### Documentation

- Update this DEVELOPMENT.md for any workflow changes
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update `strings.json` for any UI text changes

## Submitting Changes

### Before Submitting a Pull Request

1. **Run all tests**:

   ```bash
   source venv/bin/activate
   python -m pytest tests/ -v
   ```

2. **Check code style**:

   ```bash
   pre-commit run --all-files
   ```

3. **Test manually** with Home Assistant if possible

4. **Update documentation** if needed

### Pull Request Guidelines

- Use clear, descriptive commit messages
- Reference any related issues
- Include tests for new functionality
- Update documentation as needed
- Keep changes focused and atomic

## Getting Help

- **Check existing issues** on GitHub
- **Review Home Assistant developer docs**: <https://developers.home-assistant.io/>
- **Ask questions** in the project's GitHub Discussions or Issues

## Useful Resources

- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
- [Home Assistant Integration Development](https://developers.home-assistant.io/docs/creating_component_index/)
- [SunPower API Documentation](README.md#api-endpoints) (see README.md)
- [Python Testing with pytest](https://docs.pytest.org/)

---

Happy coding! 🚀
