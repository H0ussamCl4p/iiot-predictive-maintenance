import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="IIoT Predictive Maintenance",
    page_icon="🏭",
    layout="wide"
)

# Title
st.title("🏭 IIoT Predictive Maintenance Dashboard")

# Create placeholders for dynamic updates
alert_placeholder = st.empty()
metrics_placeholder = st.empty()
chart1_placeholder = st.empty()
chart2_placeholder = st.empty()

# Main loop for auto-refresh
while True:
    try:
        # Read the live data
        df = pd.read_csv('live_data.csv')
        
        # Check if data exists
        if df.empty:
            alert_placeholder.info("⏳ Waiting for data...")
            time.sleep(1)
            continue
        
        # Get the latest row
        latest = df.iloc[-1]
        latest_status = latest['status']
        latest_vibration = latest['vibration']
        latest_temperature = latest['temperature']
        latest_score = latest['score']
        
        # Display alert banners based on status
        if latest_status == "ANOMALY":
            alert_placeholder.error("🚨 CRITICAL ALERT: Anomaly Detected! Immediate maintenance required.")
        elif latest_status == "WARNING":
            alert_placeholder.warning("⚠️ WARNING: System parameters approaching critical thresholds.")
        else:
            alert_placeholder.empty()
        
        # Display metrics in top row
        with metrics_placeholder.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Vibration",
                    value=f"{latest_vibration:.2f}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Temperature",
                    value=f"{latest_temperature:.1f}°C",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="AI Health Score",
                    value=f"{latest_score:.2f}",
                    delta=None
                )
            
            with col4:
                # Visual status indicator
                if latest_status == "NORMAL":
                    status_icon = "✅"
                    status_color = "green"
                elif latest_status == "WARNING":
                    status_icon = "⚠️"
                    status_color = "orange"
                else:  # ANOMALY
                    status_icon = "🚨"
                    status_color = "red"
                
                st.metric(
                    label="System Status",
                    value=f"{status_icon} {latest_status}"
                )
        
        # Chart 1: Vibration and Temperature History
        with chart1_placeholder.container():
            st.subheader("📊 Vibration & Temperature Trends")
            
            # Prepare data for line chart
            chart_data = df[['timestamp', 'vibration', 'temperature']].copy()
            chart_data = chart_data.set_index('timestamp')
            
            st.line_chart(chart_data, use_container_width=True)
        
        # Chart 2: AI Confidence Score History
        with chart2_placeholder.container():
            st.subheader("🎯 AI Health Score History")
            
            # Prepare data for area chart
            score_data = df[['timestamp', 'score']].copy()
            score_data = score_data.set_index('timestamp')
            
            st.area_chart(score_data, use_container_width=True)
        
        # Wait 1 second before next refresh
        time.sleep(1)
        
    except FileNotFoundError:
        alert_placeholder.warning("⚠️ live_data.csv not found. Waiting for data source...")
        time.sleep(1)
        
    except pd.errors.EmptyDataError:
        alert_placeholder.info("⏳ Data file is empty. Waiting for data...")
        time.sleep(1)
        
    except Exception as e:
        alert_placeholder.error(f"❌ Error reading data: {str(e)}")
        time.sleep(1)
