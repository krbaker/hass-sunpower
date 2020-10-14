# hass-sunpower
Home Assistant SunPower Integration using the local installer ethernet interface.

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
![Project Maintenance][maintenance-shield]

## Component to integrate with [sunpower][sunpower-us] PVS 5/6 monitors

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Working/Not Working status for each device.
`sensor` | Most data available from the PVS system including per-panel data.

## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Sunpower".



## Configuration is done in the UI
 * it will ask for a host (ip works)
 * hint: most sunpower systems are at 172.27.153.1

<!---->

## Network Setup
This integration requires connectivity to the management interface used for installing the system.  The PVS systems have a second lan interface in the box.  *DO NOT PLUG THIS INTO YOUR LAN!!!* it is running its own DHCP server which will cause all sorts of IP addressing issues.  I run a Linux router with a spare ethernet port and route to the sunpower interface and allow my home assistant system to connect directly to the PVS.  Also note that the command used to dump data 'device list' is very slow and sometimes times out.  I've built in some retry logic so setup passes pretty reliably.  Sometimes you may see data go blank if the fetch times out.

***

[sunpower]: https://github.com/krbaker/hass-sunpower
[commits-shield]: https://img.shields.io/github/commit-activity/y/custom-components/blueprint.svg?style=for-the-badge
[commits]: https://github.com/krbaker/hass-sunpower/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Keith%20Baker%20%40krbaker-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/krbaker/hass-sunpower.svg?style=for-the-badge
[releases]: https://github.com/krbaker/hass-sunpower/releases
[sunpower-us]: https://us.sunpower.com/products/solar-panels