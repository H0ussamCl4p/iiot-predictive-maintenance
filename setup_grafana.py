import requests
import json
from requests.auth import HTTPBasicAuth

# Grafana configuration
GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"

# Authentication
auth = HTTPBasicAuth(GRAFANA_USER, GRAFANA_PASSWORD)

def check_and_create_datasource():
    """Check if InfluxDB datasource exists, create if not"""
    print("Checking for existing datasources...")
    
    # Get all datasources
    response = requests.get(
        f"{GRAFANA_URL}/api/datasources",
        auth=auth
    )
    
    if response.status_code == 200:
        datasources = response.json()
        for ds in datasources:
            if ds.get('name') == 'InfluxDB-Factory':
                print(f"[OK] Datasource 'InfluxDB-Factory' already exists (ID: {ds['id']})")
                return ds['id']
    
    # Create new datasource
    print("Creating new InfluxDB datasource...")
    datasource_payload = {
        "name": "InfluxDB-Factory",
        "type": "influxdb",
        "access": "proxy",
        "url": "http://influxdb:8086",
        "database": "factory_data",
        "isDefault": True,
        "jsonData": {
            "httpMode": "GET"
        }
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/datasources",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json=datasource_payload
    )
    
    if response.status_code == 200:
        datasource_id = response.json().get('id')
        print(f"[OK] Datasource 'InfluxDB-Factory' created successfully (ID: {datasource_id})")
        return datasource_id
    else:
        print(f"[ERROR] Failed to create datasource: {response.status_code} - {response.text}")
        return None

def create_monitor_dashboard():
    """Create Live Monitor dashboard (Dashboard B) - Data visualization"""
    print("\nCreating 'Live Monitor' dashboard...")
    
    dashboard_json = {
        "dashboard": {
            "title": "01 - Live Monitor",
            "tags": ["iiot", "predictive-maintenance", "monitor"],
            "timezone": "browser",
            "refresh": "1s",
            "time": {
                "from": "now-15m",
                "to": "now"
            },
            "editable": False,
            "hideControls": True,
            "graphTooltip": 0,
            "panels": [
                # TOP ROW - Panel 1: Gauge for Live Vibration (Left)
                {
                    "id": 1,
                    "type": "gauge",
                    "title": "Live Vibration",
                    "gridPos": {
                        "x": 0,
                        "y": 0,
                        "w": 8,
                        "h": 8
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": "InfluxDB-Factory",
                            "query": "SELECT last(\"vibration\") FROM \"machine_telemetry\" WHERE $timeFilter",
                            "rawQuery": True
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {
                                        "value": 0,
                                        "color": "green"
                                    },
                                    {
                                        "value": 15,
                                        "color": "red"
                                    }
                                ]
                            },
                            "unit": "none",
                            "min": 0,
                            "max": 50,
                            "decimals": 2
                        }
                    },
                    "options": {
                        "showThresholdLabels": False,
                        "showThresholdMarkers": True,
                        "orientation": "auto"
                    }
                },
                # TOP ROW - Panel 2: Stat Panel for Temperature (Center)
                {
                    "id": 2,
                    "type": "stat",
                    "title": "Temperature",
                    "gridPos": {
                        "x": 8,
                        "y": 0,
                        "w": 8,
                        "h": 8
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": "InfluxDB-Factory",
                            "query": "SELECT last(\"temperature\") FROM \"machine_telemetry\" WHERE $timeFilter",
                            "rawQuery": True
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "celsius",
                            "decimals": 1,
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {
                                        "value": 0,
                                        "color": "blue"
                                    },
                                    {
                                        "value": 50,
                                        "color": "green"
                                    },
                                    {
                                        "value": 70,
                                        "color": "orange"
                                    },
                                    {
                                        "value": 85,
                                        "color": "red"
                                    }
                                ]
                            }
                        }
                    },
                    "options": {
                        "graphMode": "area",
                        "colorMode": "background",
                        "textMode": "value_and_name",
                        "orientation": "auto",
                        "reduceOptions": {
                            "values": False,
                            "calcs": ["lastNotNull"]
                        }
                    }
                },
                # TOP ROW - Panel 3: Stat Panel for Latest AI Score (Right)
                {
                    "id": 3,
                    "type": "stat",
                    "title": "Latest AI Score",
                    "gridPos": {
                        "x": 16,
                        "y": 0,
                        "w": 8,
                        "h": 8
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": "InfluxDB-Factory",
                            "query": "SELECT last(\"ai_score\") FROM \"machine_telemetry\" WHERE $timeFilter",
                            "rawQuery": True
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "decimals": 3,
                            "mappings": [
                                {
                                    "type": "range",
                                    "options": {
                                        "from": -999,
                                        "to": 0,
                                        "result": {
                                            "text": "CRITICAL",
                                            "color": "red"
                                        }
                                    }
                                },
                                {
                                    "type": "range",
                                    "options": {
                                        "from": 0,
                                        "to": 999,
                                        "result": {
                                            "text": "NORMAL",
                                            "color": "green"
                                        }
                                    }
                                }
                            ],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {
                                        "value": -999,
                                        "color": "red"
                                    },
                                    {
                                        "value": 0,
                                        "color": "green"
                                    }
                                ]
                            }
                        }
                    },
                    "options": {
                        "graphMode": "none",
                        "colorMode": "background",
                        "textMode": "value_and_name",
                        "orientation": "auto",
                        "reduceOptions": {
                            "values": False,
                            "calcs": ["lastNotNull"]
                        }
                    }
                },
                # BOTTOM ROW - Panel 4: Time Series Graph (Full Width)
                {
                    "id": 4,
                    "type": "timeseries",
                    "title": "Vibration & AI Health Score Trend",
                    "gridPos": {
                        "x": 0,
                        "y": 8,
                        "w": 24,
                        "h": 12
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": "InfluxDB-Factory",
                            "query": "SELECT \"vibration\" FROM \"machine_telemetry\" WHERE $timeFilter",
                            "rawQuery": True,
                            "alias": "Vibration"
                        },
                        {
                            "refId": "B",
                            "datasource": "InfluxDB-Factory",
                            "query": "SELECT \"ai_score\" FROM \"machine_telemetry\" WHERE $timeFilter",
                            "rawQuery": True,
                            "alias": "AI Score"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {
                                "drawStyle": "line",
                                "lineInterpolation": "smooth",
                                "lineWidth": 2,
                                "fillOpacity": 20,
                                "showPoints": "never",
                                "spanNulls": True
                            }
                        },
                        "overrides": [
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "Vibration"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "mode": "fixed",
                                            "fixedColor": "yellow"
                                        }
                                    },
                                    {
                                        "id": "custom.fillOpacity",
                                        "value": 0
                                    },
                                    {
                                        "id": "custom.axisPlacement",
                                        "value": "left"
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "AI Score"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "mode": "fixed",
                                            "fixedColor": "green"
                                        }
                                    },
                                    {
                                        "id": "custom.fillOpacity",
                                        "value": 20
                                    },
                                    {
                                        "id": "custom.axisPlacement",
                                        "value": "right"
                                    }
                                ]
                            }
                        ]
                    },
                    "options": {
                        "tooltip": {
                            "mode": "multi",
                            "sort": "none"
                        },
                        "legend": {
                            "showLegend": True,
                            "displayMode": "list",
                            "placement": "bottom",
                            "calcs": ["mean", "lastNotNull", "max"]
                        }
                    }
                }
            ],
            "schemaVersion": 38,
            "version": 0,
            "templating": {
                "list": []
            }
        },
        "overwrite": True
    }
    
    # Send dashboard to Grafana
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json=dashboard_json
    )
    
    if response.status_code == 200:
        result = response.json()
        dashboard_uid = result.get('uid', '')
        dashboard_slug = result.get('slug', '01-live-monitor')
        
        print(f"[OK] Live Monitor dashboard created (UID: {dashboard_uid})")
        
        return dashboard_uid
    else:
        print(f"[ERROR] Failed to create Live Monitor dashboard: {response.status_code} - {response.text}")
        return None


def create_home_dashboard(monitor_uid):
    """Create Home dashboard (Dashboard A) - Landing page with link to monitor"""
    print("\nCreating 'Home' landing page dashboard...")
    
    # Construct the link to the monitor dashboard
    monitor_link = f"/d/{monitor_uid}/01-live-monitor"
    
    # HTML/Markdown content for the hero section
    hero_content = f"""
<div style="text-align: center; padding: 80px 20px; background: transparent;">
  <h1 style="font-size: 48px; font-weight: 300; margin-bottom: 20px; color: #33B5E5;">
    IIoT Predictive Maintenance System
  </h1>
  
  <h2 style="font-size: 28px; font-weight: 300; margin-bottom: 30px; color: #B0BEC5;">
    Real-time AI Anomaly Detection Engine
  </h2>
  
  <p style="font-size: 18px; line-height: 1.8; max-width: 700px; margin: 0 auto 50px; color: #90A4AE;">
    Monitoring <strong>Press_001</strong> for vibration drift and thermal anomalies 
    using <strong>Isolation Forest</strong> machine learning algorithm.
  </p>
  
  <a href="{monitor_link}" style="display: inline-block; padding: 15px 40px; 
     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
     color: white; text-decoration: none; font-size: 18px; font-weight: 500; 
     border-radius: 30px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
     transition: all 0.3s ease;">
    📊 View Live Data
  </a>
  
  <div style="margin-top: 80px; padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);">
    <div style="display: flex; justify-content: center; gap: 60px; flex-wrap: wrap;">
      <div style="text-align: center;">
        <div style="font-size: 36px; font-weight: 600; color: #4CAF50;">✓</div>
        <div style="font-size: 14px; color: #90A4AE; margin-top: 10px;">Real-time Monitoring</div>
      </div>
      <div style="text-align: center;">
        <div style="font-size: 36px; font-weight: 600; color: #FFC107;">🧠</div>
        <div style="font-size: 14px; color: #90A4AE; margin-top: 10px;">AI-Powered Detection</div>
      </div>
      <div style="text-align: center;">
        <div style="font-size: 36px; font-weight: 600; color: #2196F3;">📈</div>
        <div style="font-size: 14px; color: #90A4AE; margin-top: 10px;">Predictive Analytics</div>
      </div>
    </div>
  </div>
</div>
"""
    
    dashboard_json = {
        "dashboard": {
            "title": "00 - Home",
            "tags": ["iiot", "home", "landing"],
            "timezone": "browser",
            "refresh": False,
            "time": {
                "from": "now-6h",
                "to": "now"
            },
            "editable": False,
            "hideControls": True,
            "graphTooltip": 0,
            "panels": [
                {
                    "id": 1,
                    "type": "text",
                    "title": "",
                    "gridPos": {
                        "x": 0,
                        "y": 0,
                        "w": 24,
                        "h": 20
                    },
                    "options": {
                        "mode": "html",
                        "content": hero_content
                    },
                    "transparent": True
                }
            ],
            "schemaVersion": 38,
            "version": 0,
            "templating": {
                "list": []
            }
        },
        "overwrite": True
    }
    
    # Send dashboard to Grafana
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json=dashboard_json
    )
    
    if response.status_code == 200:
        result = response.json()
        dashboard_uid = result.get('uid', '')
        
        print(f"[OK] Home dashboard created (UID: {dashboard_uid})")
        
        return dashboard_uid
    else:
        print(f"[ERROR] Failed to create Home dashboard: {response.status_code} - {response.text}")
        return None


def set_home_dashboard(home_uid):
    """Set the Home dashboard as the organization's default home dashboard"""
    print("\nSetting Home dashboard as default...")
    
    preferences = {
        "homeDashboardUID": home_uid
    }
    
    response = requests.put(
        f"{GRAFANA_URL}/api/org/preferences",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json=preferences
    )
    
    if response.status_code == 200:
        print(f"[OK] Home dashboard set as default")
        return True
    else:
        print(f"[ERROR] Failed to set home dashboard: {response.status_code} - {response.text}")
        return False

def main():
    """Main execution function"""
    print("=" * 70)
    print("Grafana Setup Script - IIoT Predictive Maintenance")
    print("Multi-Dashboard Professional Structure")
    print("=" * 70)
    
    try:
        # Step 1: Create datasource
        datasource_id = check_and_create_datasource()
        
        if datasource_id is None:
            print("\n[ERROR] Setup failed: Could not create datasource")
            return
        
        # Step 2: Create Monitor dashboard (Dashboard B) first - get its UID
        monitor_uid = create_monitor_dashboard()
        
        if not monitor_uid:
            print("\n[ERROR] Setup failed: Could not create Monitor dashboard")
            return
        
        # Step 3: Create Home dashboard (Dashboard A) with link to Monitor
        home_uid = create_home_dashboard(monitor_uid)
        
        if not home_uid:
            print("\n[ERROR] Setup failed: Could not create Home dashboard")
            return
        
        # Step 4: Set Home as the default dashboard
        set_home_dashboard(home_uid)
        
        # Success summary
        print("\n" + "=" * 70)
        print("[SUCCESS] Multi-Dashboard Setup Complete!")
        print("=" * 70)
        
        print("\n[Dashboard Structure]")
        print(f"  1. Home Page:    {GRAFANA_URL}/d/{home_uid}/00-home")
        print(f"  2. Live Monitor: {GRAFANA_URL}/d/{monitor_uid}/01-live-monitor")
        
        print("\n[Kiosk Mode Links] (No sidebar, fullscreen)")
        print(f"  Home:    {GRAFANA_URL}/d/{home_uid}/00-home?kiosk")
        print(f"  Monitor: {GRAFANA_URL}/d/{monitor_uid}/01-live-monitor?kiosk")
        
        print("\n" + "=" * 70)
        print("[ACCESS YOUR DASHBOARD]")
        print("=" * 70)
        print(f"\n  Login URL: {GRAFANA_URL}/login")
        print(f"\n  Username: admin")
        print(f"  Password: admin")
        print(f"\n  After login, you'll be redirected to the Home dashboard automatically.")
        print("\n" + "=" * 70)
        print("\nTip: Press 'F11' in your browser for true fullscreen mode!")
        print("=" * 70)
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to Grafana at http://localhost:3000")
        print("Please ensure Grafana is running and accessible.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
