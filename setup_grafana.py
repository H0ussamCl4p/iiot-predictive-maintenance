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
                print(f"✓ Datasource 'InfluxDB-Factory' already exists (ID: {ds['id']})")
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
        print(f"✓ Datasource 'InfluxDB-Factory' created successfully (ID: {datasource_id})")
        return datasource_id
    else:
        print(f"✗ Failed to create datasource: {response.status_code} - {response.text}")
        return None

def create_dashboard():
    """Create IIoT Production Monitor dashboard"""
    print("\nCreating dashboard...")
    
    dashboard_json = {
        "dashboard": {
            "title": "IIoT Production Monitor",
            "tags": ["iiot", "predictive-maintenance"],
            "timezone": "browser",
            "refresh": "5s",
            "time": {
                "from": "now-15m",
                "to": "now"
            },
            "panels": [
                # Panel 1: Gauge for Live Vibration
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
                            "query": "SELECT mean(\"vibration\") FROM \"machine_telemetry\" WHERE $timeFilter GROUP BY time($__interval) fill(null)",
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
                                        "color": "yellow"
                                    },
                                    {
                                        "value": 25,
                                        "color": "red"
                                    }
                                ]
                            },
                            "unit": "none",
                            "min": 0,
                            "max": 40
                        }
                    },
                    "options": {
                        "showThresholdLabels": True,
                        "showThresholdMarkers": True
                    }
                },
                # Panel 2: Graph for AI Health Trend
                {
                    "id": 2,
                    "type": "graph",
                    "title": "AI Health Trend",
                    "gridPos": {
                        "x": 8,
                        "y": 0,
                        "w": 16,
                        "h": 8
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": "InfluxDB-Factory",
                            "query": "SELECT \"ai_score\" FROM \"machine_telemetry\" WHERE $timeFilter",
                            "rawQuery": True
                        }
                    ],
                    "xaxis": {
                        "mode": "time",
                        "show": True
                    },
                    "yaxes": [
                        {
                            "format": "short",
                            "label": "AI Score",
                            "show": True
                        },
                        {
                            "format": "short",
                            "show": True
                        }
                    ],
                    "lines": True,
                    "fill": 1,
                    "linewidth": 2,
                    "pointradius": 2,
                    "points": False,
                    "tooltip": {
                        "shared": True,
                        "sort": 0,
                        "value_type": "individual"
                    },
                    "legend": {
                        "show": True,
                        "alignAsTable": False,
                        "avg": False,
                        "current": False,
                        "max": False,
                        "min": False,
                        "rightSide": False,
                        "total": False,
                        "values": False
                    }
                },
                # Panel 3: Stat panel for Latest Temperature
                {
                    "id": 3,
                    "type": "stat",
                    "title": "Latest Temperature",
                    "gridPos": {
                        "x": 0,
                        "y": 8,
                        "w": 8,
                        "h": 6
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
                            "decimals": 1
                        }
                    },
                    "options": {
                        "graphMode": "none",
                        "colorMode": "value",
                        "textMode": "value_and_name",
                        "orientation": "auto",
                        "reduceOptions": {
                            "values": False,
                            "calcs": ["lastNotNull"]
                        }
                    }
                }
            ],
            "schemaVersion": 27,
            "version": 0
        },
        "overwrite": False
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
        dashboard_url = f"{GRAFANA_URL}{result.get('url', '')}"
        print(f"✓ Dashboard created successfully!")
        print(f"Dashboard created! URL: {dashboard_url}")
        return dashboard_url
    else:
        print(f"✗ Failed to create dashboard: {response.status_code} - {response.text}")
        return None

def main():
    """Main execution function"""
    print("=" * 60)
    print("Grafana Setup Script - IIoT Predictive Maintenance")
    print("=" * 60)
    
    try:
        # Step 1: Create datasource
        datasource_id = check_and_create_datasource()
        
        if datasource_id is None:
            print("\n✗ Setup failed: Could not create datasource")
            return
        
        # Step 2: Create dashboard
        dashboard_url = create_dashboard()
        
        if dashboard_url:
            print("\n" + "=" * 60)
            print("Setup completed successfully! 🎉")
            print("=" * 60)
        else:
            print("\n✗ Setup failed: Could not create dashboard")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to Grafana at http://localhost:3000")
        print("Please ensure Grafana is running and accessible.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
