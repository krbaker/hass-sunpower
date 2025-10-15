"""SunPower PVS client with automatic LocalAPI/Legacy CGI fallback."""

import logging
import traceback

import requests
import simplejson
from urllib.parse import urlencode

try:
    # Suppress TLS warnings when verify=False
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:  # pragma: no cover - optional
    pass


class ConnectionException(Exception):
    """Any failure to connect to sunpower PVS"""


class ParseException(Exception):
    """Any failure to connect to sunpower PVS"""


class SunPowerMonitor:
    """Client for SunPower PVS with automatic LocalAPI/Legacy CGI fallback.
    
    Automatically detects firmware version and uses:
    - LocalAPI (Varserver FCGI) for firmware build >= 61840
    - Legacy CGI endpoints for older firmware
    """
    
    # Minimum firmware build number that supports LocalAPI
    MIN_LOCALAPI_BUILD = 61840

    def __init__(self, host, serial_suffix: str | None = None):
        """Initialize PVS client with automatic API detection.

        - host: IP or hostname of the PVS
        - serial_suffix: last 5 characters of the PVS serial (password for ssm_owner, only needed for LocalAPI)
        """
        self.host = host
        self.base = "http://{0}".format(host)
        self.session = requests.Session()
        self.timeout = 30
        self.use_localapi = False
        self._session_token = None
        self._cache_initialized = False
        self._last_fetch_time = 0
        self._min_fetch_interval = 1.0  # Minimum 1 second between fetches
        
        # Check firmware version to determine which API to use
        support_check = self.check_localapi_support(host, self.timeout)
        
        if support_check["supported"]:
            # Use LocalAPI for newer firmware
            self.use_localapi = True
            
            # Try to auto-fetch serial suffix from supervisor/info if not provided
            if not serial_suffix or not serial_suffix.strip():
                serial_suffix = self._fetch_serial_suffix()
            
            # Use the serial suffix (auto-fetched or provided)
            resolved = (serial_suffix or "").strip()
            
            if not resolved:
                raise ConnectionException(
                    "Missing serial suffix for LocalAPI. Auto-detection failed. "
                    "Unable to retrieve serial number from PVS."
                )
            
            self.serial_suffix = resolved
            self._login()
        else:
            # Use legacy CGI for older firmware
            self.use_localapi = False
            self.command_url = "http://{0}/cgi-bin/dl_cgi?Command=".format(host)
    
    def _fetch_serial_suffix(self) -> str:
        """Attempt to fetch serial number from supervisor/info endpoint.
        
        Returns last 5 characters of serial, or empty string if fetch fails.
        """
        try:
            resp = self.session.get(
                "{0}/cgi-bin/dl_cgi/supervisor/info".format(self.base),
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                if "supervisor" in data and "SERIAL" in data["supervisor"]:
                    serial = data["supervisor"]["SERIAL"]
                    if len(serial) >= 5:
                        return serial[-5:]
        except Exception:
            pass  # Silently fail, will use fallback
        return ""
    
    @staticmethod
    def check_localapi_support(host: str, timeout: int = 30) -> dict:
        """Check if PVS supports LocalAPI by actually testing the endpoint.
        
        Returns dict with:
        - supported: bool
        - build: int or None
        - version: str or None
        - serial: str or None
        - error: str or None
        """
        result = {
            "supported": False,
            "build": None,
            "version": None,
            "serial": None,
            "error": None
        }
        
        try:
            resp = requests.get(
                "http://{0}/cgi-bin/dl_cgi/supervisor/info".format(host),
                timeout=timeout
            )
            
            if resp.status_code != 200:
                result["error"] = "HTTP {0}".format(resp.status_code)
                return result
            
            data = resp.json()
            if "supervisor" not in data:
                result["error"] = "Invalid response format"
                return result
            
            supervisor = data["supervisor"]
            build = supervisor.get("BUILD")
            version = supervisor.get("SWVER")
            serial = supervisor.get("SERIAL")
            
            result["build"] = build
            result["version"] = version
            result["serial"] = serial
            
            # Actually test if LocalAPI endpoint exists (not just build number)
            # Test the /auth endpoint which is the actual LocalAPI path used
            if build and build >= SunPowerMonitor.MIN_LOCALAPI_BUILD:
                try:
                    test_resp = requests.get(
                        "http://{0}/auth".format(host),
                        timeout=5
                    )
                    # If we get anything other than 404, LocalAPI exists
                    # (401/403 means auth required, which is expected)
                    if test_resp.status_code != 404:
                        result["supported"] = True
                    else:
                        result["error"] = "Build {0} but LocalAPI endpoints not found (404)".format(build)
                except Exception:
                    result["error"] = "Build {0} but LocalAPI endpoint test failed".format(build)
            else:
                result["error"] = "Firmware build {0} is too old. LocalAPI requires build {1}+".format(build, SunPowerMonitor.MIN_LOCALAPI_BUILD)
            
            return result
            
        except requests.exceptions.RequestException as e:
            result["error"] = "Connection failed: {0}".format(e)
            return result
        except Exception as e:
            result["error"] = "Unexpected error: {0}".format(e)
            return result

    def _login(self):
        """Authenticate to LocalAPI, storing session token."""
        import base64
        
        # Build Basic auth header (lowercase "basic")
        token = base64.b64encode("ssm_owner:{0}".format(self.serial_suffix).encode("utf-8")).decode("ascii")
        auth_header = "basic {0}".format(token)
        
        try:
            resp = self.session.get(
                "{0}/auth?login".format(self.base),
                headers={"Authorization": auth_header},
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Extract session token and store it for subsequent requests
            session_token = data.get("session")
            if not session_token:
                raise ParseException("Authentication failed: no session token received")
            
            # Store session token in session headers for all future requests
            self.session.headers.update({"Cookie": "session={0}".format(session_token)})
            self._session_token = session_token
            
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 401:
                raise ConnectionException("Authentication failed: invalid credentials")
            raise ConnectionException("Authentication failed: HTTP {0}".format(error.response.status_code))
        except requests.exceptions.RequestException as error:
            raise ConnectionException("Authentication failed: network error")
        except simplejson.errors.JSONDecodeError as error:
            raise ParseException("Authentication failed: invalid response format")

    def _vars(self, *, names=None, match=None, cache=None, fmt_obj=True, retry_count=0):
        """Query /vars endpoint with retry logic.

        names: list of exact variable names
        match: substring match
        cache: cache id to create or query
        fmt_obj: if True, request fmt=obj to get object mapping
        retry_count: internal retry counter
        """
        params = {}
        if names:
            params["name"] = ",".join(names)
        if match:
            params["match"] = match
        if cache:
            params["cache"] = cache
        if fmt_obj:
            params["fmt"] = "obj"
        
        max_retries = 2
        
        try:
            resp = self.session.get("{0}/vars".format(self.base), params=params, timeout=self.timeout)
            
            # Handle session expiration
            if resp.status_code == 401 or resp.status_code == 403:
                if retry_count < max_retries:
                    # Re-authenticate and retry
                    self._login()
                    return self._vars(names=names, match=match, cache=cache, fmt_obj=fmt_obj, retry_count=retry_count + 1)
                else:
                    raise ConnectionException("Authentication failed after retries")
            
            # Handle 400 Bad Request - might indicate LocalAPI not fully supported
            if resp.status_code == 400:
                # Log the response body for debugging
                try:
                    error_body = resp.text
                    logger = logging.getLogger(__name__)
                    logger.debug(f"400 Bad Request response body: {error_body}")
                except Exception:
                    pass
                raise ConnectionException(f"Bad Request (400) - LocalAPI endpoint may not support these parameters. URL: {self.base}/vars, params: {params}")
            
            resp.raise_for_status()
            data = resp.json()
            return data
        except requests.exceptions.Timeout as error:
            if retry_count < max_retries:
                # Retry on timeout
                return self._vars(names=names, match=match, cache=cache, fmt_obj=fmt_obj, retry_count=retry_count + 1)
            raise ConnectionException(f"Request timeout after retries: {error}")
        except requests.exceptions.HTTPError as error:
            # Catch HTTPError before generic RequestException
            raise ConnectionException(f"HTTP {error.response.status_code}: {error}. URL: {self.base}/vars, params: {params}")
        except requests.exceptions.RequestException as error:
            raise ConnectionException(f"Failed to query device variables: {error}. URL: {self.base}/vars, params: {params}")
        except (simplejson.errors.JSONDecodeError, ValueError) as error:
            raise ParseException(f"Failed to parse device response: {error}")

    def _fetch_meters(self, use_cache=True):
        """Fetch all meter variables and group by device index.
        
        use_cache: if True and cache exists, use cached data; if False, refresh cache
        """
        # Note: LocalAPI supports cache parameter but we don't use it for simplicity.
        # With 120s polling intervals, the performance benefit is negligible and
        # avoiding cache state management makes the integration more reliable.
        data = self._vars(match="meter", fmt_obj=True)
        
        # Group by meter index (e.g., /sys/devices/meter/0/field -> meter 0)
        meters = {}
        for var_path, value in data.items():
            if "/sys/devices/meter/" in var_path:
                parts = var_path.split("/")
                if len(parts) >= 5:
                    meter_idx = parts[4]  # e.g., "0", "1"
                    field = parts[5] if len(parts) > 5 else None
                    if field:
                        meter_key = "/sys/devices/meter/{0}".format(meter_idx)
                        if meter_key not in meters:
                            meters[meter_key] = {}
                        meters[meter_key][field] = value
        return meters

    def _fetch_inverters(self, use_cache=True):
        """Fetch all inverter variables and group by device index.
        
        use_cache: if True and cache exists, use cached data; if False, refresh cache
        """
        # Note: LocalAPI supports cache parameter but we don't use it for simplicity.
        # With 120s polling intervals, the performance benefit is negligible and
        # avoiding cache state management makes the integration more reliable.
        data = self._vars(match="inverter", fmt_obj=True)
        
        inverters = {}
        for var_path, value in data.items():
            if "/sys/devices/inverter/" in var_path:
                parts = var_path.split("/")
                if len(parts) >= 5:
                    inv_idx = parts[4]
                    field = parts[5] if len(parts) > 5 else None
                    if field:
                        inv_key = "/sys/devices/inverter/{0}".format(inv_idx)
                        if inv_key not in inverters:
                            inverters[inv_key] = {}
                        inverters[inv_key][field] = value
        return inverters

    def _fetch_sysinfo(self, use_cache=True):
        """Fetch system info variables.
        
        use_cache: if True and cache exists, use cached data; if False, refresh cache
        """
        # Note: LocalAPI supports cache parameter but we don't use it for simplicity.
        # With 120s polling intervals, the performance benefit is negligible and
        # avoiding cache state management makes the integration more reliable.
        data = self._vars(match="info", fmt_obj=True)
        return data

    @staticmethod
    def _key(obj, old_key, new_key, transform=None):
        if old_key in obj:
            val = obj[old_key]
            obj[new_key] = transform(val) if transform else val

    def _legacy_generic_command(self, command):
        """Legacy CGI command for older firmware.
        
        All 'commands' to the PVS module use this url pattern and return json.
        The PVS system can take a very long time to respond so timeout is at 2 minutes.
        """
        try:
            return requests.get(self.command_url + command, timeout=120).json()
        except requests.exceptions.RequestException as error:
            raise ConnectionException("Failed to execute legacy command")
        except simplejson.errors.JSONDecodeError as error:
            raise ParseException("Failed to parse legacy response")

    def device_list(self):
        """Return DeviceList using LocalAPI (new) or legacy CGI (old).

        Structure: {"devices": [ {DEVICE_TYPE, SERIAL, MODEL, TYPE, DESCR, STATE, ...fields} ]}
        """
        if not self.use_localapi:
            # Use legacy CGI endpoint for older firmware
            return self._legacy_generic_command("DeviceList")
        
        # Use LocalAPI for newer firmware
        logger = logging.getLogger(__name__)
        devices = []
        
        # Determine if we should use cached data (after first successful fetch)
        use_cache = self._cache_initialized
        
        # PVS device (minimal info) - always add, even if fetch fails
        pvs_serial = "PVS-{0}".format(self.host)
        pvs_model = "PVS"
        pvs_sw_version = "Unknown"
        
        try:
            sysinfo = self._fetch_sysinfo(use_cache=use_cache)
            # Use actual serial number from PVS if available
            pvs_serial = sysinfo.get("/sys/info/serialnum", pvs_serial)
            pvs_model = sysinfo.get("/sys/info/model", pvs_model)
            pvs_sw_version = sysinfo.get("/sys/info/sw_rev", pvs_sw_version)
        except Exception as e:
            # If sysinfo fails, log but use defaults
            logger.warning("Failed to fetch PVS info, using defaults: {0}".format(e))
        
        # Always add PVS device to devices list
        devices.append(
            {
                "DEVICE_TYPE": "PVS",
                "SERIAL": pvs_serial,
                "MODEL": pvs_model,
                "TYPE": "PVS",
                "DESCR": "{0} {1}".format(pvs_model, pvs_serial),
                "STATE": "working",
                "sw_ver": pvs_sw_version,
                # Legacy dl_* diagnostics unavailable via this minimal sysinfo; omit
            }
        )

        # Meter devices - with error handling
        try:
            meters = self._fetch_meters(use_cache=use_cache)
        except Exception as e:
            logger.warning("Failed to fetch meters: {0}".format(e))
            meters = {}
        
        for path, m in meters.items():
            dev = {
                "DEVICE_TYPE": "Power Meter",
                "SERIAL": m.get("sn", "Unknown"),
                "MODEL": m.get("prodMdlNm", "Unknown"),
                "TYPE": "PVS-METER",
                "DESCR": "Power Meter {0}".format(m.get('sn', '')),
                "STATE": "working",
            }
            # Field mappings
            dev["net_ltea_3phsum_kwh"] = m.get("netLtea3phsumKwh")
            dev["p_3phsum_kw"] = m.get("p3phsumKw")
            dev["q_3phsum_kvar"] = m.get("q3phsumKvar")
            dev["s_3phsum_kva"] = m.get("s3phsumKva")
            dev["tot_pf_rto"] = m.get("totPfRto")
            dev["v12_v"] = m.get("v12V")
            dev["v1n_v"] = m.get("v1nV")
            dev["v2n_v"] = m.get("v2nV")
            dev["freq_hz"] = m.get("freqHz")
            
            # Leg-specific fields
            if "i1A" in m:
                dev["i1_a"] = m.get("i1A")
            if "i2A" in m:
                dev["i2_a"] = m.get("i2A")
            if "p1Kw" in m:
                dev["p1_kw"] = m.get("p1Kw")
            if "p2Kw" in m:
                dev["p2_kw"] = m.get("p2Kw")
            
            # Grid/Home energy tracking (to_grid = negative, to_home = positive)
            if "negLtea3phsumKwh" in m:
                dev["neg_ltea_3phsum_kwh"] = m.get("negLtea3phsumKwh")
            if "posLtea3phsumKwh" in m:
                dev["pos_ltea_3phsum_kwh"] = m.get("posLtea3phsumKwh")
            
            devices.append(dev)

        # Inverter devices - with error handling
        try:
            inverters = self._fetch_inverters(use_cache=use_cache)
        except Exception as e:
            logger.error("Failed to fetch inverters: {0}".format(e))
            logger.debug("Traceback: {0}".format(traceback.format_exc()))
            inverters = {}
        
        for path, inv in inverters.items():
            dev = {
                "DEVICE_TYPE": "Inverter",
                "SERIAL": inv.get("sn", "Unknown"),
                "MODEL": inv.get("prodMdlNm", "Unknown"),
                "TYPE": "MICRO-INVERTER",
                "DESCR": "Inverter {0}".format(inv.get('sn', '')),
                "STATE": "working",
            }
            # Field name mapping: LocalAPI uses camelCase (e.g., ltea3phsumKwh),
            # but we convert to snake_case (e.g., ltea_3phsum_kwh) to match
            # legacy CGI format. This ensures identical data structures for
            # backwards compatibility with all downstream code (sensors, entities).
            
            # Energy
            dev["ltea_3phsum_kwh"] = inv.get("ltea3phsumKwh")
            
            # Power - AC and DC
            dev["p_3phsum_kw"] = inv.get("p3phsumKw")  # AC power (more accurate)
            dev["p_mppt1_kw"] = inv.get("pMppt1Kw")    # DC power
            
            # Voltage - AC and DC
            dev["vln_3phavg_v"] = inv.get("vln3phavgV")  # AC voltage
            dev["v_mppt1_v"] = inv.get("vMppt1V")        # DC voltage
            
            # Current - AC and DC
            dev["i_3phsum_a"] = inv.get("i3phsumA")   # AC current (actual output)
            dev["i_mppt1_a"] = inv.get("iMppt1A")     # DC current
            
            # Temperature and frequency
            dev["t_htsnk_degc"] = inv.get("tHtsnkDegc")
            dev["freq_hz"] = inv.get("freqHz")
            
            # Optional MPPT sum if present
            if "pMpptsumKw" in inv:
                dev["p_mpptsum_kw"] = inv.get("pMpptsumKw")
            
            devices.append(dev)
        
        # Mark cache as initialized after first successful fetch
        if not self._cache_initialized and (meters or inverters):
            self._cache_initialized = True
        
        # Log summary of what was fetched
        logger.info("LocalAPI device_list: PVS={0}, Meters={1}, Inverters={2}".format(
            pvs_serial, len(meters), len(inverters)
        ))

        return {"devices": devices}

    def energy_storage_system_status(self):
        """Return ESS status using LocalAPI (new) or legacy CGI (old).

        Structure expected by callers:
        { "ess_report": { "battery_status": [...], "ess_status": [...], "hub_plus_status": {...} } }
        If detailed vars are not available, return empty lists/dicts and let callers handle gracefully.
        """
        if not self.use_localapi:
            # Use legacy CGI endpoint for older firmware
            try:
                return requests.get(
                    "http://{0}/cgi-bin/dl_cgi/energy-storage-system/status".format(self.host),
                    timeout=120,
                ).json()
            except requests.exceptions.RequestException as error:
                raise ConnectionException("Failed to get ESS status")
            except simplejson.errors.JSONDecodeError as error:
                raise ParseException("Failed to parse ESS response")
        
        # Use LocalAPI for newer firmware
        try:
            livedata = self._vars(match="livedata", cache="ldata", fmt_obj=True)
        except Exception:
            livedata = {}

        report = {
            "battery_status": [],
            "ess_status": [],
            "hub_plus_status": {},
        }

        # Populate minimal aggregate values if present
        if livedata:
            soc = livedata.get("/sys/livedata/soc")
            ess_p = livedata.get("/sys/livedata/ess_p")
            if soc is not None or ess_p is not None:
                report["ess_status"].append(
                    {
                        "serial_number": "ESS-AGG",
                        "ess_meter_reading": {
                            "agg_power": {"value": float(ess_p) if ess_p is not None else 0.0},
                            "meter_a": {"reading": {"current": {"value": 0}, "power": {"value": 0}, "voltage": {"value": 0}}},
                            "meter_b": {"reading": {"current": {"value": 0}, "power": {"value": 0}, "voltage": {"value": 0}}},
                        },
                        "enclosure_humidity": {"value": 0},
                        "enclosure_temperature": {"value": 0},
                    }
                )
                report["hub_plus_status"] = {
                    "serial_number": "HUBPLUS-AGG",
                    "grid_phase1_voltage": {"value": 0},
                    "grid_phase2_voltage": {"value": 0},
                    "hub_humidity": {"value": 0},
                    "hub_temperature": {"value": 0},
                    "inverter_connection_voltage": {"value": 0},
                    "load_phase1_voltage": {"value": 0},
                    "load_phase2_voltage": {"value": 0},
                }

        return {"ess_report": report}

    def network_status(self):
        """Return network/system info using LocalAPI (new) or legacy CGI (old)."""
        if not self.use_localapi:
            # Use legacy CGI endpoint for older firmware
            return self._legacy_generic_command("Get_Comm")
        
        # Use LocalAPI for newer firmware
        info = self._fetch_sysinfo()
        return info
