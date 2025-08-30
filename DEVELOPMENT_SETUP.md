# SunPower Integration Development Setup

This guide will help you set up a complete development environment for the SunPower Home Assistant integration, including debugging capabilities and import stepping.

## 🏗️ **Project Overview**

This is a **Home Assistant custom integration** for monitoring SunPower solar systems via local PVS (Photovoltaic Supervisor) interface. The integration provides real-time data for:

- Solar panel production (per-panel data)
- Power consumption and grid interaction
- Battery storage systems (SunVault)
- System health and diagnostics

## 📋 **Prerequisites**

- **Python 3.11+** (tested with 3.13.5)
- **VS Code** (recommended) or PyCharm
- **Git** for version control
- Access to a **SunPower PVS system** (for testing)

## 🚀 **Quick Setup**

### 1. **Clone and Enter Project**

```bash
cd /path/to/your/projects
git clone https://github.com/krbaker/hass-sunpower.git
cd hass-sunpower
```

### 2. **Create Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. **Setup Pre-commit Hooks**

```bash
pre-commit install
```

### 5. **Configure Environment**

```bash
cp env.example .env
# Edit .env with your PVS IP address
```

## 🔧 **VS Code Setup**

The project includes pre-configured VS Code settings for optimal development:

### **Extensions (Install these):**

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)
- GitLens (eamodio.gitlens)

### **Key Features Configured:**

- ✅ **Auto-formatting** with Black (line length 99)
- ✅ **Import sorting** with isort
- ✅ **Linting** with Flake8
- ✅ **Type checking** with Pylance
- ✅ **Auto-save formatting**
- ✅ **Debugging configurations**

## 🐛 **Debugging Setup**

### **Debug Configurations Available:**

1. **Debug SunPower Integration** - Test core functionality (no HA required)
2. **Test with Sample Data** - Test integration logic with sample data
3. **Debug HA Integration** - Test Home Assistant coordinator setup
4. **Debug SunPower API Client** - Test just the API client
5. **Debug Current File** - Debug any Python file
6. **Run Tests** - Debug test cases

### **Setting Breakpoints:**

1. **Open any Python file** in the integration
2. **Click in the gutter** (left of line numbers) to set breakpoints
3. **Press F5** or use Debug menu to start debugging
4. **Step through code** with F10 (step over), F11 (step into)

### **Debug Scripts:**

#### **Test API Connection:**

```bash
# Set your PVS IP
export PVS_HOST=192.168.1.100  # Replace with your PVS IP
python test_api.py
```

Example Output

```bash
➜  hass-sunpower git:(main) ✗ ./venv/bin/python3 test_api.py
Testing SunPower API connection to young-ave.dynamic-dns.net:8081
--------------------------------------------------
1. Testing network status...
✅ Network status successful
{'networkstatus': {'interfaces': [{'interface': 'wan',
                                   'internet': 'down',
                                   'ipaddr': '',
                                   'link': 'disconnected',
                                   'mode': 'wan',
                                   'sms': 'unreachable',
                                   'state': 'down'},
                                  {'interface': 'plc',
                                   'internet': 'down',
                                   'ipaddr': '',
                                   'link': 'disconnected',
                                   'pairing': 'unpaired',
                                   'sms': 'unreachable',
                                   'speed': 0,
                                   'state': 'down'},
                                  {'interface': 'sta0',
                                   'internet': 'up',
                                   'ipaddr': '192.168.1.25',
                                   'signal': '-80',
                                   'sms': 'reachable',
                                   'ssid': "XYZ's Network",
                                   'status': 'connected'},
                                  {'interface': 'cell',
                                   'internet': 'down',
                                   'ipaddr': '',
                                   'is_alwayson': False,
                                   'is_primary': False,
                                   'link': 'disconnected',
                                   'modem': 'MODEM_OK',
                                   'provider': 'UNKNOWN',
                                   'signal': 0,
                                   'sim': 'SIM_READY',
                                   'sms': 'unreachable',
                                   'state': 'DOWN',
                                   'status': 'NOT_REGISTERED'}],
                   'system': {'interface': 'sta0',
                              'interface_name': 'sta0',
                              'internet': 'up',
                              'sms': 'reachable'},
                   'ts': '1756569304'},
 'result': 'succeed'}

2. Testing device list...
✅ Device list successful
Found 30 devices
Device breakdown:
  - PVS: 1
  - Power Meter: 2
  - Inverter: 27

3. Testing energy storage system status...
✅ ESS status successful
{'result': 'Make sure you have run discovery to successful completion'}
```

#### **Test with Sample Data (No PVS Required):**

```bash
python test_with_sample_data.py
```

#### **Debug Integration Logic:**

```bash
export PVS_HOST=192.168.1.100
python debug_runner.py
```

#### **Test Home Assistant Integration:**

```bash
export PVS_HOST=192.168.1.100
python test_ha_integration.py
```

## 🧪 **Testing**

### **Run All Tests:**

```bash
pytest tests/ -v
```

### **Run Specific Test:**

```bash
pytest tests/test_sunpower_api.py::TestSunPowerMonitor::test_init -v
```

### **Run Tests with Coverage:**

```bash
pytest tests/ --cov=custom_components/sunpower --cov-report=html
```

## 🔍 **Code Quality Tools**

### **Manual Code Checks:**

```bash
# Format code
black custom_components/ tests/ *.py

# Sort imports
isort custom_components/ tests/ *.py

# Lint code
flake8 custom_components/ tests/ *.py

# Type checking
mypy custom_components/sunpower/
```

### **Pre-commit (Automatic):**

Code quality checks run automatically on commit. To run manually:

```bash
pre-commit run --all-files
```

## 📁 **Key Files for Development**

### **Core Integration Files:**

- `custom_components/sunpower/__init__.py` - Integration entry point
- `custom_components/sunpower/sunpower.py` - API client
- `custom_components/sunpower/const.py` - Constants and sensor definitions
- `custom_components/sunpower/config_flow.py` - UI configuration
- `custom_components/sunpower/sensor.py` - Sensor entities
- `custom_components/sunpower/entity.py` - Base entity class

### **Development Files:**

- `test_api.py` - Test PVS API connection
- `debug_runner.py` - Debug full integration
- `requirements-dev.txt` - Development dependencies
- `.vscode/launch.json` - Debug configurations
- `tests/` - Test suite

## 🌐 **Network Setup for Testing**

The integration connects to the PVS management interface:

### **Common PVS IP Addresses:**

- **NAT setup**: `172.27.153.1` (most common)
- **Direct connection**: Your PVS's actual IP
- **Router assignment**: Check your router's DHCP clients

### **Testing Connectivity:**

```bash
# Test if PVS is reachable
curl "http://172.27.153.1/cgi-bin/dl_cgi?Command=Get_Comm"

# Or use our test script
export PVS_HOST=172.27.153.1
python test_api.py
```

## 🚨 **Important Notes**

### **PVS Management Interface:**

- ⚠️ **DO NOT** plug the PVS management port directly into your LAN
- It runs its own DHCP server and will cause network issues
- Use a separate network interface or NAT setup

### **Development Safety:**

- Use longer polling intervals (120s+) to avoid overwhelming the PVS
- The PVS API is slow and can timeout - be patient
- Monitor PVS logs for any issues during development

## 🔧 **Stepping Through Imports**

### **Debug Import Issues:**

1. **Set breakpoint** in `__init__.py` at the import statements
2. **Start debug session** "Debug SunPower Integration"
3. **Step through** (F11) each import to see what's loaded
4. **Check sys.path** in debug console: `sys.path`
5. **Verify module loading** in debug console: `import custom_components.sunpower.const`

### **Import Path Configuration:**

```python
# VS Code settings already include:
"python.analysis.extraPaths": ["./custom_components"]

# Debug scripts add:
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))
```

## 📝 **Common Development Tasks**

### **Adding a New Sensor:**

1. **Add sensor definition** in `const.py`
2. **Test data availability** in sample JSON
3. **Add unit tests** in `tests/`
4. **Test with real PVS** using debug scripts

### **Debugging Connection Issues:**

1. **Check network connectivity**: `python test_api.py`
2. **Verify PVS responds**: `curl http://<IP>/cgi-bin/dl_cgi?Command=Get_Comm`
3. **Debug data parsing**: Set breakpoints in `sunpower_fetch()`
4. **Check coordinator updates**: Debug in `async_update_data()`

### **Adding Multi-Account Support:**

The integration supports multiple PVS systems:

1. **Use unique names** in config flow
2. **Test entry_id isolation** in debug scripts
3. **Verify device/entity separation** in Home Assistant

## 🆘 **Troubleshooting**

### **Import Errors:**

```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify module structure
find custom_components/ -name "*.py" | head -10
```

### **VS Code Issues:**

- **Restart Python interpreter**: Cmd+Shift+P → "Python: Restart Language Server"
- **Check interpreter**: Cmd+Shift+P → "Python: Select Interpreter" → Choose `./venv/bin/python`
- **Reload window**: Cmd+Shift+P → "Developer: Reload Window"

### **Debug Not Working:**

1. **Check .env file** exists with PVS_HOST
2. **Verify PVS connectivity** with `test_api.py`
3. **Check Python interpreter** points to `./venv/bin/python`
4. **Look at debug console** for error messages

## 🎯 **Next Steps**

1. **Test with your PVS**: Update `.env` with your PVS IP
2. **Run debug script**: `python debug_runner.py`
3. **Set breakpoints**: Try debugging the data flow
4. **Add tests**: Create tests for any new features
5. **Submit PRs**: Follow the project's contribution guidelines

---

## 📚 **Additional Resources**

- **Home Assistant Developer Docs**: <https://developers.home-assistant.io/>
- **SunPower Integration Issues**: <https://github.com/krbaker/hass-sunpower/issues>
- **Home Assistant Discord**: #devs_custom_components
- **Python Debugging Guide**: <https://docs.python.org/3/library/pdb.html>

Happy coding! 🚀
