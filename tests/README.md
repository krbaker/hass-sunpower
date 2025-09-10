# SunPower Integration Testing Suite

This directory contains comprehensive testing tools
and documentation for the SunPower Home Assistant
integration.

## 📁 **Tests Directory Structure**

```console
tests/
├── samples/
│   └── device_list.json          # Sample PVS data for testing
│   └── DEBUG_TOOLS_GUIDE.md      # Detailed debug tools documentation
├── test_api.py                   # Test PVS API connectivity
├── test_with_sample_data.py      # Test integration logic (no hardware)
├── debug_runner.py               # Test core functionality
├── test_ha_integration.py        # Test Home Assistant compatibility
└── README.md                     # This file
```

## 🚀 **Quick Start**

### **Test Without Hardware** (Recommended first step)

```bash
cd testing
python test_with_sample_data.py
```

### **Test With Your PVS**

```bash
cd testing
export PVS_HOST=192.168.1.100  # Your PVS IP
python test_api.py
python debug_runner.py
```

## 🛠️ **Testing Tools**

| Script | Purpose | Requires PVS |
|--------|---------|-------------|
| **`test_with_sample_data.py`** | Validate integration logic with sample data | ❌ |
| **`test_api.py`** | Test PVS connectivity and API responses | ✅ |
| **`debug_runner.py`** | Test core integration functionality | ✅ |
| **`test_ha_integration.py`** | Test Home Assistant compatibility | ✅ |

## 🔧 **VS Code Integration**

All test scripts are configured as VS Code debug targets:

1. **Open** the main project directory in VS Code
2. **Press F5** to see debug configurations
3. **Select** your desired test script
4. **Set breakpoints** and debug through the code

## 📊 **Sample Data**

The `samples/device_list.json` contains real PVS API response data for testing:

- **1 PVS** (Photovoltaic Supervisor)
- **3 Power Meters** (including 1 virtual meter)
- **20 Inverters** (solar panel micro-inverters)

This allows complete testing of the integration logic without needing physical hardware.

## 📚 **Documentation**

### **`docs/DEVELOPMENT_SETUP.md`**

Complete guide for setting up the development environment including:

- Python environment setup
- VS Code configuration
- Debugging setup
- Network configuration

### **`docs/DEBUG_TOOLS_GUIDE.md`**

Detailed documentation for all debug tools including:

- Purpose and usage of each script
- Expected output examples
- Troubleshooting common issues
- Advanced debugging techniques

## 🎯 **Development Workflow**

### **For New Features**

1. **Start**: `python test_with_sample_data.py` (validate logic)
2. **Test**: `python debug_runner.py` (test with real PVS)
3. **Verify**: `python test_ha_integration.py` (HA compatibility)

### **For Bug Fixes**

1. **Isolate**: `python test_api.py` (check connectivity)
2. **Debug**: Set breakpoints in VS Code and step through
3. **Validate**: Run all tests to ensure fix doesn't break anything

### **Before Committing**

```bash
# From project root
pytest tests/ -v                    # Unit tests
cd testing
python test_with_sample_data.py     # Integration logic test
```

## 🆘 **Troubleshooting**

### **Import Errors**

- Ensure you're running from the `testing/` directory
- Check that virtual environment is activated
- Verify Python path includes `custom_components`

### **PVS Connection Issues**

- Set `PVS_HOST` environment variable
- Test connectivity: `curl http://$PVS_HOST/cgi-bin/dl_cgi?Command=Get_Comm`
- Check network configuration (see development setup guide)

### **VS Code Debug Issues**

- Ensure Python interpreter points to `../venv/bin/python`
- Restart VS Code language server if needed
- Check that debug configurations point to correct file paths

## 📈 **Adding New Tests**

When adding new test functionality:

1. **Follow naming convention**: `test_*.py`
2. **Add VS Code debug config** in `../.vscode/launch.json`
3. **Update documentation** in `docs/DEBUG_TOOLS_GUIDE.md`
4. **Include error handling** and helpful output messages

## 🔗 **Related Files**

- **Unit Tests**: `../tests/` (pytest-based unit tests)
- **VS Code Config**: `../.vscode/` (debug configurations, settings)
- **Integration Code**: `../custom_components/sunpower/` (main integration)
- **Requirements**: `../requirements-dev.txt` (development dependencies)

---

For complete setup instructions, see [`docs/DEVELOPMENT_SETUP.md`](docs/DEVELOPMENT_SETUP.md).

For detailed tool documentation, see [`docs/DEBUG_TOOLS_GUIDE.md`](docs/DEBUG_TOOLS_GUIDE.md).
