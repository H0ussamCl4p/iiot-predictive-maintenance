# ESP32 MQTT Integration Guide

## Overview
Connect your PLC/sensors to the IIoT Predictive Maintenance Dashboard using ESP32 as an MQTT bridge on your local network.

## Requirements
- ESP32 and server on **same WiFi network**
- MQTT Broker: `192.168.x.x:1883` (server's local IP)

## Hardware Requirements
- ESP32 Development Board
- Sensors (Vibration, Temperature, Humidity)
- Connection to PLC (RS485/Modbus optional)

## Software Setup

### 1. Install Arduino Libraries
```bash
# Install via Arduino Library Manager:
- PubSubClient (MQTT)
- WiFi (built-in)
- ArduinoJson
```

### 2. ESP32 Code Example

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker - Use your server's local IP address
const char* mqtt_server = "192.168.1.100";  // Find with: ipconfig (Windows) or ifconfig (Linux)
const int mqtt_port = 1883;
const char* mqtt_topic = "factory/plc/data";

// Equipment Configuration
const char* machine_id = "ESP32_MOTOR_01";  // Match with dashboard registration
const char* equipment_name = "Assembly Line Motor";

// Sensor Pins (adjust to your setup)
#define VIBRATION_PIN 34
#define TEMP_PIN 35
#define HUMIDITY_PIN 36

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastPublish = 0;
const long publishInterval = 1000;  // Publish every 1 second

void setup() {
  Serial.begin(115200);
  
  // Initialize sensors
  pinMode(VIBRATION_PIN, INPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(HUMIDITY_PIN, INPUT);
  
  // Connect to WiFi
  setup_wifi();
  
  // Configure MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming messages if needed
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

float readVibration() {
  // Read analog sensor and convert to vibration value
  int raw = analogRead(VIBRATION_PIN);
  // Convert 0-4095 (12-bit ADC) to 0-100 vibration units
  return (raw / 4095.0) * 100.0;
}

float readTemperature() {
  // Read temperature sensor (example for LM35 or similar)
  int raw = analogRead(TEMP_PIN);
  // Convert to temperature (adjust formula for your sensor)
  return (raw / 4095.0) * 100.0;  // Example: 0-100°C range
}

float readHumidity() {
  // Read humidity sensor
  int raw = analogRead(HUMIDITY_PIN);
  // Convert to humidity percentage
  return (raw / 4095.0) * 100.0;
}

void publishSensorData() {
  // Create JSON document
  StaticJsonDocument<256> doc;
  
  // Read sensor values
  float vibration = readVibration();
  float temperature = readTemperature();
  float humidity = readHumidity();
  
  // Populate JSON
  doc["timestamp"] = millis() / 1000;  // Unix timestamp
  doc["machine_id"] = machine_id;
  doc["equipment_name"] = equipment_name;
  doc["vibration"] = round(vibration * 10) / 10.0;  // 1 decimal
  doc["temperature"] = round(temperature * 10) / 10.0;
  doc["humidity"] = round(humidity * 10) / 10.0;
  
  // Serialize to string
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  
  // Publish to MQTT
  if (client.publish(mqtt_topic, jsonBuffer)) {
    Serial.println("Published: " + String(jsonBuffer));
  } else {
    Serial.println("Publish failed");
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Publish sensor data at regular intervals
  unsigned long now = millis();
  if (now - lastPublish >= publishInterval) {
    lastPublish = now;
    publishSensorData();
  }
}
```

## PLC Integration (Modbus Example)

If reading from PLC via Modbus RTU:

```cpp
#include <ModbusMaster.h>

// Modbus RTU
#define MAX485_DE      4
#define MAX485_RE_NEG  5

ModbusMaster node;

void preTransmission() {
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);
}

void postTransmission() {
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);
}

void setup() {
  // ... existing WiFi/MQTT setup ...
  
  // Modbus setup
  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);
  
  Serial2.begin(9600, SERIAL_8N1);  // RX=16, TX=17
  node.begin(1, Serial2);  // Slave ID 1
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);
}

float readPLCRegister(uint16_t address) {
  uint8_t result = node.readHoldingRegisters(address, 1);
  
  if (result == node.ku8MBSuccess) {
    return node.getResponseBuffer(0) / 10.0;  // Adjust scaling
  }
  return -999;  // Error value
}

void publishSensorData() {
  StaticJsonDocument<256> doc;
  
  // Read from PLC registers
  float vibration = readPLCRegister(0x0000);  // Holding register 0
  float temperature = readPLCRegister(0x0001); // Holding register 1
  float humidity = readPLCRegister(0x0002);    // Holding register 2
  
  // ... rest of JSON creation and publish ...
}
```

## Dashboard Registration Steps

1. **Access Equipment Page** in the dashboard
2. **Click "Add Equipment"** button
3. **Fill in details:**
   - Equipment ID: `ESP32_MOTOR_01` (must match ESP32 code)
   - Name: `Assembly Line Motor`
   - Type: `Motor`
   - Location: `Line A`
   - MQTT Topic: `factory/plc/data`
4. **Upload ESP32 code** with matching `machine_id`
5. **Monitor** - Data will appear in real-time on Status/Prediction/Anomaly pages

## Finding Your Server's IP Address

**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" under your WiFi adapter
```

**Linux/Mac:**
```bash
ifconfig
# or
ip addr show
```

**Docker Host IP (if needed):**
```powershell
# From inside container, server is accessible at:
host.docker.internal  # or your machine's local IP
```

## Data Format

The ESP32 must publish JSON in this exact format:

```json
{
  "timestamp": 1701234567,
  "machine_id": "ESP32_MOTOR_01",
  "equipment_name": "Assembly Line Motor",
  "vibration": 45.2,
  "temperature": 62.5,
  "humidity": 55.0
}
```

## Troubleshooting

### ESP32 won't connect to WiFi
- Check SSID and password are correct
- Verify WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router

### ESP32 won't connect to MQTT
- Verify server IP with `ipconfig` or `ifconfig`
- Check server and ESP32 are on same network
- Test MQTT broker: `docker ps | grep mosquitto`
- Ping server from ESP32 network: `ping 192.168.1.100`

### Data not appearing in dashboard
- Verify `machine_id` matches dashboard registration exactly
- Check MQTT topic is `factory/plc/data`
- View AI engine logs: `docker logs iiot_ai_engine`
- Monitor MQTT traffic: `docker exec iiot_mosquitto mosquitto_sub -v -t 'factory/#'`

### Sensor readings incorrect
- Calibrate sensors using known reference values
- Adjust conversion formulas in `readVibration()`, `readTemperature()`, etc.
- Add filtering for noisy signals (moving average)

### Windows Firewall Blocking MQTT
```powershell
# Allow MQTT through Windows Firewall
New-NetFirewallRule -DisplayName "MQTT Local" -Direction Inbound `
  -LocalPort 1883 -Protocol TCP -Action Allow
```

## Advanced Features

### Multiple Sensors on One ESP32
```cpp
// Publish to different topics for different machines
const char* machine1_id = "ESP32_MOTOR_01";
const char* machine2_id = "ESP32_PUMP_01";

void loop() {
  // Read sensors for machine 1
  publishData(machine1_id, vibration1, temp1, humidity1);
  
  // Read sensors for machine 2
  publishData(machine2_id, vibration2, temp2, humidity2);
}
```

### OTA Updates
Enable Over-The-Air updates for ESP32:
```cpp
#include <ArduinoOTA.h>

void setup() {
  // ... existing setup ...
  
  ArduinoOTA.setHostname("esp32-plc-bridge");
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
  // ... rest of loop ...
}
```

## Bill of Materials (BOM)

| Component | Quantity | Purpose |
|-----------|----------|---------|
| ESP32 Dev Board | 1 | Main controller |
| ADXL345 Accelerometer | 1 | Vibration sensor |
| DHT22 | 1 | Temperature & Humidity |
| MAX485 Module | 1 | RS485 for PLC (optional) |
| 5V Power Supply | 1 | Power ESP32 |
| Jumper Wires | 10+ | Connections |

## Wiring Diagram

```
ESP32          Sensor
-----          ------
3.3V    ---    VCC
GND     ---    GND
GPIO34  ---    Vibration Sensor OUT
GPIO35  ---    Temperature Sensor OUT
GPIO36  ---    Humidity Sensor OUT

For Modbus/RS485:
GPIO16  ---    MAX485 RO (Receiver Output)
GPIO17  ---    MAX485 DI (Driver Input)
GPIO4   ---    MAX485 DE (Driver Enable)
GPIO5   ---    MAX485 RE (Receiver Enable)
```

## Support

For issues or questions:
- Check dashboard logs: `docker logs iiot_ai_engine`
- Monitor MQTT traffic: `mosquitto_sub -v -t 'factory/#'`
- Open an issue on GitHub
