#include <ETH.h>
#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <ArduinoOTA.h>

// ─────────── Configuration constants ──────────────────────────
const char* HOSTNAME = "ESP32-SUN-GATEWAY"; // Give it a name
const char* ssid = "MYWIFI"; // Your Wi-Fi SSID
const char* password = "MYWIFIPASSWORD"; // Your Wi-Fi password


/**
 *  WT32-ETH01  ▸  Wi-Fi ⇄ Ethernet HTTP proxy
 *  -------------------------------------------------------------
 *  • Wi-Fi : DHCP, 1 s back-off reconnect
 *  • ETH   : Static 172.27.153.2 → 172.27.153.1
 *  • Proxy : Forwards any HTTP method from Wi-Fi to ETH host
 *  Tested with ESP32-Arduino v3.2.0
 * -------------------------------------------------------------
 *  Check Wi-Fi and Ethernet connection status via:
 *   http://<device-ip>/gatewaystatus
 *    or
 *   http://ESP32-SUN-GATEWAY.local/gatewaystatus
 */


// ─────────── Ethernet static IP ───────────────────────────────
IPAddress eth_ip     (172, 27, 153, 2);
IPAddress eth_gateway(172, 27, 153, 1);
IPAddress eth_subnet (255, 255, 255, 0);

// ─────────── WT32-ETH01  (LAN8720) pins & constants ───────────
#define ETH_PHY_ADDR  1
#define ETH_MDC_PIN   23
#define ETH_MDIO_PIN  18
#define ETH_TYPE      ETH_PHY_LAN8720
#define ETH_CLK_MODE  ETH_CLOCK_GPIO17_OUT
#define ETH_POWER_PIN 16            // enables the PHY's 3 V 3 rail

// ─────────── globals ──────────────────────────────────────────
WebServer server(80);
bool wifiConnected = false;
bool ethConnected  = false;

esp_timer_handle_t retryTimer;      // one-shot reconnect timer

// ─────────── helper: disconnect reason → text ─────────────────
const char* reasonToText(uint8_t r)
{
  switch (r) {
    case WIFI_REASON_AUTH_EXPIRE:        return "AUTH_EXPIRE";
    case WIFI_REASON_AUTH_FAIL:          return "AUTH_FAIL";
    case WIFI_REASON_NO_AP_FOUND:        return "NO_AP_FOUND";
    case WIFI_REASON_BEACON_TIMEOUT:     return "BEACON_TIMEOUT";
    case WIFI_REASON_HANDSHAKE_TIMEOUT:  return "4WAY_TIMEOUT";
    default:                             return "OTHER";
  }
}

// ─────────── timer callback: start Wi-Fi again ────────────────
void IRAM_ATTR retryCallback(void*)
{
  WiFi.begin(ssid, password);
}

// ─────────── Wi-Fi event handler (2-arg form) ─────────────────
void handleWiFiEvent(WiFiEvent_t event, WiFiEventInfo_t info)
{
  switch (event) {

    case ARDUINO_EVENT_WIFI_STA_GOT_IP:
      wifiConnected = true;
      Serial.print("Wi-Fi IP: ");
      Serial.println(WiFi.localIP());
      break;

    case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
      wifiConnected = false;
      Serial.printf("Wi-Fi lost — reason: %s (%d). Re-try in 1 s…\n",
                    reasonToText(info.wifi_sta_disconnected.reason),
                    info.wifi_sta_disconnected.reason);
      esp_timer_start_once(retryTimer, 1'000'000);   // 1 000 000 µs
      break;

    default:
      break;
  }
}

// ─────────── Ethernet event handler (simple form) ─────────────
void handleETHEvent(WiFiEvent_t event)
{
  if (event == ARDUINO_EVENT_ETH_CONNECTED) {
    Serial.println("Ethernet connected.");
    ETH.config(eth_ip, eth_gateway, eth_subnet);
    ethConnected = true;
  }
  else if (event == ARDUINO_EVENT_ETH_DISCONNECTED) {
    Serial.println("Ethernet disconnected.");
    ethConnected = false;
  }
}




void setupOTA() {
  ArduinoOTA.setHostname(HOSTNAME);  // Set custom device name
  ArduinoOTA.onStart([]() {
    Serial.println("OTA Update Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA Update Complete");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("OTA Progress: %u%%\r", (progress * 100) / total);
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("OTA Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });

  ArduinoOTA.begin();
}


// ─────────── Arduino setup() ──────────────────────────────────
void setup()
{
  Serial.begin(115200);
  Serial.println("WT32-ETH01 WiFi-Ethernet Proxy Starting...");

  // create one-shot reconnect timer (stopped)
  const esp_timer_create_args_t tCfg = {
      .callback = &retryCallback,
      .name     = "wifiRetry"};
  esp_timer_create(&tCfg, &retryTimer);

  // ── Wi-Fi initialisation ───────────────────────────────────
  WiFi.setHostname(HOSTNAME);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(false);     // we manage retries
  WiFi.onEvent(handleWiFiEvent);    // 2-arg callback
  WiFi.begin(ssid, password);

  setupOTA();

  // ── Ethernet initialisation ────────────────────────────────
  WiFi.onEvent(handleETHEvent);     // ETH callbacks (1-arg ok)
  delay(2500);                      // allow 3 V 3 rail to rise
  ETH.begin(ETH_TYPE, ETH_PHY_ADDR,
            ETH_MDC_PIN, ETH_MDIO_PIN,
            ETH_POWER_PIN, ETH_CLK_MODE);

  // ── HTTP proxy server ──────────────────────────────────────
  server.on("/gatewaystatus", handleStatus);        // Status endpoint
  server.onNotFound(handleProxyRequest);
  server.begin();
  Serial.println("HTTP proxy started on port 80");
  Serial.println("Status available at /gatewaystatus");
}

// ─────────── Arduino loop() ───────────────────────────────────
void loop()
{
  ArduinoOTA.handle();

  server.handleClient();            // non-blocking
}

// ─────────── status handler ───────────────────────────────────
void handleStatus()
{
  String status = "{\n";
  status += "  \"wifi_connected\": " + String(wifiConnected ? "true" : "false") + ",\n";
  status += "  \"wifi_ip\": \"" + WiFi.localIP().toString() + "\",\n";
  status += "  \"eth_connected\": " + String(ethConnected ? "true" : "false") + ",\n";
  status += "  \"eth_ip\": \"" + ETH.localIP().toString() + "\",\n";
  status += "  \"eth_gateway\": \"" + eth_gateway.toString() + "\",\n";
  status += "  \"uptime_ms\": " + String(millis()) + "\n";
  status += "}";
  
  server.send(200, "application/json", status);
}

// ─────────── utils: HTTPMethod → string ───────────────────────
static inline const char* mToStr(HTTPMethod m)
{
  switch (m) {
    case HTTP_GET:     return "GET";
    case HTTP_POST:    return "POST";
    case HTTP_PUT:     return "PUT";
    case HTTP_DELETE:  return "DELETE";
    case HTTP_PATCH:   return "PATCH";
    case HTTP_HEAD:    return "HEAD";
    case HTTP_OPTIONS: return "OPTIONS";
    default:           return "OTHER";
  }
}

// ─────────── main proxy handler ───────────────────────────────
void handleProxyRequest()
{
  if (!ethConnected) {
    server.send(503, "text/plain", "Ethernet not connected.");
    return;
  }

  // Debug: Print current network status
  Serial.printf("ETH Status - IP: %s, Gateway: %s, Connected: %s\n", 
                ETH.localIP().toString().c_str(), 
                ETH.gatewayIP().toString().c_str(),
                ethConnected ? "true" : "false");

  String url = "http://172.27.153.1" + server.uri();
  
  // Add query parameters if they exist
  if (server.args() > 0) {
    url += "?";
    for (int i = 0; i < server.args(); i++) {
      if (i > 0) url += "&";
      url += server.argName(i) + "=" + server.arg(i);
    }
  }
  
  const char* method = mToStr(server.method());

  Serial.printf("Proxy: %s %s\n", method, url.c_str());

  // Test basic connectivity first
  WiFiClient testClient;
  if (!testClient.connect("172.27.153.1", 80)) {
    Serial.println("ERROR: Cannot establish TCP connection to 172.27.153.1:80");
    server.send(502, "text/plain", "Cannot connect to 172.27.153.1:80 - Check network configuration");
    return;
  }
  testClient.stop();
  Serial.println("TCP connection to 172.27.153.1:80 successful");

  WiFiClient ethClient;
  HTTPClient http;
  http.setTimeout(15000);  // Increased timeout to 15 seconds
  http.begin(ethClient, url);

  // forward headers
  for (int i = 0; i < server.headers(); ++i) {
    String headerName = server.headerName(i);
    String headerValue = server.header(i);
    // Skip some headers that shouldn't be forwarded
    if (headerName != "Host" && headerName != "Connection") {
      http.addHeader(headerName, headerValue);
    }
  }

  // forward body if present
  String body = server.arg("plain");
  if (body.isEmpty()) body = server.arg(0);

  int code = (server.method() == HTTP_POST ||
              server.method() == HTTP_PUT  ||
              server.method() == HTTP_PATCH)
             ? http.sendRequest(method, body)
             : http.sendRequest(method);

  // relay response
  if (code > 0) {
    String response = http.getString();
    String cType = http.header("Content-Type");
    
    Serial.printf("Proxy response: %d, size: %d, content-type: %s\n", 
                  code, response.length(), cType.c_str());
    
    // Only set content-type if it was provided by the upstream server
    if (!cType.isEmpty()) {
      server.send(code, cType, response);
    } else {
      // For responses without content-type, let the client handle it
      server.send(code, "", response);
    }
  } else {
    String errorMsg = "HTTP Error: ";
    switch(code) {
      case HTTPC_ERROR_CONNECTION_REFUSED: errorMsg += "Connection refused"; break;
      case HTTPC_ERROR_SEND_HEADER_FAILED: errorMsg += "Send header failed"; break;
      case HTTPC_ERROR_SEND_PAYLOAD_FAILED: errorMsg += "Send payload failed"; break;
      case HTTPC_ERROR_NOT_CONNECTED: errorMsg += "Not connected"; break;
      case HTTPC_ERROR_CONNECTION_LOST: errorMsg += "Connection lost"; break;
      case HTTPC_ERROR_NO_STREAM: errorMsg += "No stream"; break;
      case HTTPC_ERROR_NO_HTTP_SERVER: errorMsg += "No HTTP server"; break;
      case HTTPC_ERROR_TOO_LESS_RAM: errorMsg += "Too less RAM"; break;
      case HTTPC_ERROR_ENCODING: errorMsg += "Encoding error"; break;
      case HTTPC_ERROR_STREAM_WRITE: errorMsg += "Stream write error"; break;
      case HTTPC_ERROR_READ_TIMEOUT: errorMsg += "Read timeout"; break;
      default: errorMsg += "Unknown error (" + String(code) + ")"; break;
    }
    Serial.printf("Proxy error: %d - %s\n", code, errorMsg.c_str());
    server.send(502, "text/plain", "Bad Gateway - " + errorMsg);
  }

  http.end();
}
