# SunPower Integration Debug Tools Guide

This document explains all the debug tools available for developing and testing the SunPower Home Assistant integration.

## 🛠️ **Available Debug Tools**

### **1. `test_api.py` - API Client Testing**

**Purpose**: Test direct communication with PVS hardware
**Use When**: You want to verify PVS connectivity and API responses

```bash
export PVS_HOST=192.168.1.100  # Your PVS IP
python test_api.py
```

**What it tests**:

- ✅ Network connectivity to PVS
- ✅ Basic API commands (network status, device list)
- ✅ ESS functionality (if available)
- ✅ Error handling and timeouts

**Example Output**:

```
Testing SunPower API connection to 192.168.1.100
--------------------------------------------------
1. Testing network status...
✅ Network status successful
2. Testing device list...
✅ Device list successful
Found 30 devices
```

---

### **2. `test_with_sample_data.py` - Integration Logic Testing**

**Purpose**: Test integration logic without requiring real PVS hardware
**Use When**: You want to verify data processing, sensor mapping, and core logic

```bash
python test_with_sample_data.py
```

**What it tests**:

- ✅ Data conversion from PVS format to HA format
- ✅ Sensor field compatibility (which sensors will work)
- ✅ Virtual meter creation
- ✅ Device type processing
- ✅ Integration consistency

**Example Output**:

```
🧪 Testing SunPower Integration with Sample Data
✅ Data conversion successful
📊 Device types found: ['PVS', 'Power Meter', 'Inverter']
Sensor field compatibility:
  - PVS: 9/9 fields available (100.0%)
  - Power Meter: 8/16 fields available (50.0%)
```

---

### **3. `debug_runner.py` - Core Functionality Testing**

**Purpose**: Test core integration functionality with real PVS data
**Use When**: You want to test the integration logic with real PVS responses

```bash
export PVS_HOST=192.168.1.100
python debug_runner.py
```

**What it tests**:

- ✅ API client functionality
- ✅ Data conversion and processing
- ✅ Core integration functions
- ✅ Data fetch mechanisms
- ✅ Error handling and recovery

**Example Output**:

```
🔧 Starting SunPower Integration Debug
1. Testing SunPower API client...
✅ PVS connectivity successful
2. Testing data processing...
3. Testing data fetch function...
✅ Data fetch function successful
```

---

### **4. `test_ha_integration.py` - Home Assistant Compatibility**

**Purpose**: Test Home Assistant specific functionality (coordinators, etc.)
**Use When**: You want to verify HA integration components work correctly

```bash
export PVS_HOST=192.168.1.100
python test_ha_integration.py
```

**What it tests**:

- ✅ DataUpdateCoordinator creation
- ✅ Home Assistant mock compatibility
- ✅ Integration data flow
- ✅ HA-specific error handling

---

### **5. `pytest tests/` - Unit Testing**

**Purpose**: Run automated unit tests
**Use When**: You want to verify code changes don't break existing functionality

```bash
pytest tests/ -v
```

**What it tests**:

- ✅ API client unit tests
- ✅ Mock response handling
- ✅ Error condition testing
- ✅ Edge case validation

---

## 🎯 **Testing Workflow Recommendations**

### **For New Development**

1. **Start with**: `test_with_sample_data.py` (no hardware needed)
2. **Then test**: `debug_runner.py` (with real PVS)
3. **Finally verify**: `pytest tests/` (automated validation)

### **For Bug Investigation**

1. **Check connectivity**: `test_api.py`
2. **Verify logic**: `debug_runner.py`
3. **Test HA integration**: `test_ha_integration.py`

### **For Performance Testing**

1. **Use**: `debug_runner.py` with different update intervals
2. **Monitor**: PVS response times and error rates
3. **Validate**: Sample data processing speed

---

## 🐛 **VS Code Debug Configurations**

All scripts are available as VS Code debug configurations:

| Configuration Name | Script | Purpose |
|-------------------|---------|---------|
| **Test with Sample Data** | `test_with_sample_data.py` | Test logic without hardware |
| **Debug SunPower Integration** | `debug_runner.py` | Test with real PVS |
| **Debug HA Integration** | `test_ha_integration.py` | Test HA compatibility |
| **Debug SunPower API Client** | `test_api.py` | Test API connectivity |

**To use**:

1. Press `F5` in VS Code
2. Select desired configuration
3. Set breakpoints anywhere in the code
4. Step through imports and execution

---

## 🔍 **Debugging Import Issues**

### **Step Through Import Resolution**

1. Set breakpoint at top of any integration file
2. Use "Debug SunPower Integration" configuration
3. Step into (`F11`) import statements
4. Watch variables panel for `sys.path` and module loading

### **Check Python Path**

```python
# In debug console:
import sys
print('\n'.join(sys.path))
```

### **Verify Module Loading**

```python
# In debug console:
import custom_components.sunpower.const as const
print(dir(const))
```

---

## 📊 **Output Interpretation**

### **Success Indicators**

- ✅ Green checkmarks
- 📊 Data statistics (device counts, field availability)
- 📈 Performance metrics
- 🎉 Completion messages

### **Warning Indicators**

- ⚠️ Yellow warnings (expected issues)
- ℹ️ Informational messages
- 💡 Helpful suggestions

### **Error Indicators**

- ❌ Red X marks
- 🔍 Troubleshooting sections
- Detailed error tracebacks

---

## 🔧 **Troubleshooting Common Issues**

### **"No module named 'sunpower'"**

- Check Python path configuration
- Verify VS Code interpreter points to `./venv/bin/python`
- Restart VS Code language server

### **Connection Timeouts**

- Verify PVS IP address in `PVS_HOST`
- Check network connectivity: `curl http://<IP>/cgi-bin/dl_cgi?Command=Get_Comm`
- Try different timeout values

### **Import Errors in Debug**

- Use "Test with Sample Data" first (no external dependencies)
- Check that virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements-dev.txt`

---

## 🚀 **Advanced Debugging Techniques**

### **Custom Data Testing**

1. Modify `samples/device_list.json` with your PVS data
2. Run `test_with_sample_data.py` to validate compatibility
3. Test edge cases with missing or malformed data

### **Performance Profiling**

```bash
python -m cProfile -o profile_stats debug_runner.py
```

### **Memory Usage Monitoring**

```python
# Add to debug scripts:
import tracemalloc
tracemalloc.start()
# ... run tests ...
current, peak = tracemalloc.get_traced_memory()
print(f"Memory: {current / 1024 / 1024:.1f} MB")
```

---

## 📚 **Integration with Development Workflow**

### **Before Committing Code**

```bash
# 1. Run all tests
pytest tests/ -v

# 2. Test with sample data
python test_with_sample_data.py

# 3. Format code (automatic with pre-commit)
black custom_components/ tests/ *.py
```

### **Before Releasing**

```bash
# 1. Test with real PVS
export PVS_HOST=your.pvs.ip
python debug_runner.py

# 2. Test HA integration
python test_ha_integration.py

# 3. Run full test suite
pytest tests/ --cov=custom_components/sunpower
```

This comprehensive debug tool suite ensures you can develop, test, and debug the SunPower integration efficiently at every stage of development.
