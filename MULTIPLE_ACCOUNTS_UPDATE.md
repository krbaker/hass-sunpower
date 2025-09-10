# Multiple Accounts/Locations Support Update

## Overview

This update enables the SunPower Home Assistant integration to support multiple accounts and locations without sensor or device conflicts. Each account/location installation is now properly isolated with unique identifiers.

## Changes Made

### 1. Config Flow Updates (`config_flow.py`)

- Added optional `name` field for location identification
- Updated unique_id generation to include location name when provided
- Enhanced validation and error handling
- Updated UI strings and translations

### 2. Core Architecture Changes (`__init__.py`)

- **Fixed global data storage issue**: Replaced global variables with entry-specific cache (`ENTRY_DATA_CACHE`)
- Updated `sunpower_fetch()` to accept and use `entry_id` parameter
- Added proper cleanup in `async_unload_entry()` to prevent memory leaks
- Enhanced data isolation between multiple installations

### 3. Entity Identification System (`entity.py`, `sensor.py`, `binary_sensor.py`)

- **Enhanced unique_id generation**: All entities now include entry_id in their unique_id to prevent conflicts
- **Updated device identifiers**: Device identifiers now include entry_id to ensure device uniqueness
- **Backwards compatibility**: System falls back to old format when entry_id is not available
- Added entry_id parameter to all entity constructors

### 4. Translation Updates

- Updated `strings.json` and `translations/en.json` with new location name field
- Enhanced descriptions to guide users on multiple account setup

## Key Features

### Conflict Prevention

- **Entity unique_id format**: `{entry_id}_{device_serial}_pvs_{field}` (vs old: `{device_serial}_pvs_{field}`)
- **Device identifiers**: `(domain, "{entry_id}_{device_serial}")` (vs old: `(domain, "{device_serial}")`)
- **Config entry unique_id**: `{host}_{location_name}` (vs old: `{host}`)

### Data Isolation

- Each account/location has its own data cache
- No shared global variables between installations
- Proper cleanup on entry removal

### User Experience

- Optional location name field for easy identification
- Clear UI guidance for multiple account setup
- Backwards compatible with existing installations

## Testing Plan

### 1. Single Account (Backwards Compatibility)

1. Install integration without location name
2. Verify all sensors and devices work as before
3. Check entity unique_ids maintain backwards compatibility

### 2. Multiple Accounts Setup

1. **First Account**:
   - Configure with Host: `192.168.1.100` and Name: `Home Main`
   - Verify all entities are created with format: `{entry_id}_...`

2. **Second Account**:
   - Configure with Host: `192.168.1.101` and Name: `Cabin Solar`
   - Verify no conflicts with first account
   - Check that devices and entities are properly separated

3. **Same Host, Different Names**:
   - Configure with Host: `192.168.1.100` and Name: `Home Backup`
   - Verify this creates a separate integration instance
   - Confirm no entity or device conflicts

### 3. Conflict Validation

1. Check Home Assistant's Developer Tools → States
2. Verify no duplicate entity IDs exist
3. Confirm device registry shows separate devices for each account
4. Test that data updates work independently for each account

### 4. Cleanup Testing

1. Remove one integration instance
2. Verify the cache is properly cleaned up
3. Confirm other instances continue working normally
4. Check for memory leaks in logs

## Migration Notes

### For Existing Users

- **No action required**: Existing installations will continue to work unchanged
- Entity unique_ids remain the same for backwards compatibility
- Devices maintain their current identifiers

### For New Multi-Account Users

1. When adding a second account, **always use the location name field**
2. Use descriptive names like "Main House", "Cabin", "Garage", etc.
3. Each location should have a unique combination of host and name

## Technical Details

### Entry-Specific Data Cache

```python
ENTRY_DATA_CACHE = {
    "entry_id_1": {
        "pvs_sample_time": 0,
        "pvs_sample": {},
        "ess_sample_time": 0,
        "ess_sample": {}
    },
    "entry_id_2": {
        # ... separate cache for another account
    }
}
```

### Entity Unique ID Examples

```python
# Old format (still used for backwards compatibility)
"E00202040011392_pvs_ltea_3phsum_kwh"

# New format with entry_id
"abc123def456_E00202040011392_pvs_ltea_3phsum_kwh"
```

### Device Identifier Examples

```python
# Old format
("sunpower", "E00202040011392")

# New format
("sunpower", "abc123def456_E00202040011392")
```

## Troubleshooting

### If You See Entity Conflicts

1. Ensure each account uses a unique location name
2. Restart Home Assistant after configuration changes
3. Check Developer Tools → States for duplicate entities

### Performance Considerations

- Each account maintains its own update intervals
- Data caching is isolated per account to prevent interference
- Memory usage scales linearly with number of accounts

## Future Enhancements

Potential future improvements:

1. Bulk account configuration
2. Account grouping in UI
3. Cross-account energy summary
4. Advanced conflict detection and resolution

## Breaking Changes

**None** - This update is fully backwards compatible with existing installations.
