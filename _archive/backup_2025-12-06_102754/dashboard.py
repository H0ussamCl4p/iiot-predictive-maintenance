import streamlit as st
import pandas as pd
import time
import os

# --- 1. PAGE CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="IIoT Monitor",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (To clean up the look) ---
st.markdown("""
    <style>
    /* Hide Streamlit Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Adjust top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FILES & CONSTANTS ---
LOG_FILE = "live_data.csv"

# --- 4. SIDEBAR (The Control Center) ---
with st.sidebar:
    st.title("🏭 Plant Monitor")
    st.markdown("---")
    st.caption("System Status")
    
    # Placeholder for status indicator
    sidebar_status = st.empty()
    
    st.markdown("---")
    st.caption("Controls")
    
    # "Clear History" Button
    # This is great for restarting your demo without deleting files manually
    if st.button("🗑️ Clear History"):
        if os.path.exists(LOG_FILE):
            # Keep header, delete rows
            with open(LOG_FILE, "w") as f:
                f.write("timestamp,vibration,temperature,score,status\n")
            st.success("History cleared!")
            time.sleep(1)
            st.rerun()

    st.markdown("### 🛠️ Debug Info")
    st.info("Listening on: live_data.csv")

# --- 5. MAIN FUNCTIONS ---
def load_data():
    if os.path.exists(LOG_FILE):
        try:
            # Read CSV with pandas
            # on_bad_lines='skip' prevents crashing if the file is being written to
            df = pd.read_csv(LOG_FILE, on_bad_lines='skip')
            return df.tail(200) # Limit to last 200 rows for performance
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# --- 6. DASHBOARD LAYOUT ---

# Header
st.markdown("## 📊 Machine Predictive Maintenance")

# Create Layout Containers
top_row = st.container()
middle_row = st.container()

# Metric Placeholders (Define them once)
with top_row:
    col1, col2, col3, col4 = st.columns(4)
    metric_vib = col1.empty()
    metric_temp = col2.empty()
    metric_score = col3.empty()
    metric_status = col4.empty()

# Tabs for Charts vs Data
tab1, tab2 = st.tabs(["📈 Live Telemetry", "📋 Raw Data Log"])

with tab1:
    col_chart_1, col_chart_2 = st.columns(2)
    with col_chart_1:
        st.caption("Sensor Readings (Vibration & Temp)")
        chart_sensors = st.empty()
    with col_chart_2:
        st.caption("AI Health Score (Prediction)")
        chart_score = st.empty()
    
    # Alert Banner Placeholder
    alert_banner = st.empty()

with tab2:
    st.caption("Streaming Data Log")
    dataframe_placeholder = st.empty()

# --- 7. MAIN LOOP ---
while True:
    df = load_data()
    
    if not df.empty:
        latest = df.iloc[-1]
        
        # --- UPDATE METRICS ---
        metric_vib.metric("Vibration", f"{latest['vibration']:.2f} Hz")
        metric_temp.metric("Temperature", f"{latest['temperature']:.2f} °C")
        
        # Score Color Logic
        score = latest['score']
        metric_score.metric("AI Health", f"{score:.4f}")
        
        # Status Logic
        status = latest['status']
        if status == "NORMAL":
            metric_status.success("NORMAL")
            sidebar_status.success("System Online")
            alert_banner.empty() # Clear alerts
        elif status == "WARNING":
            metric_status.warning("WARNING")
            sidebar_status.warning("Maintenance Needed")
            alert_banner.warning("⚠️ PREDICTIVE ALERT: Machine drift detected.")
        else:
            metric_status.error("ANOMALY")
            sidebar_status.error("CRITICAL FAILURE")
            alert_banner.error("🚨 CRITICAL FAILURE! STOP MACHINE IMMEDIATELY.")

        # --- UPDATE CHARTS ---
        # 1. Sensor Chart (Line)
        # We rename columns to make the legend look nicer
        sensor_data = df[["vibration", "temperature"]].copy()
        chart_sensors.line_chart(sensor_data)
        
        # 2. Score Chart (Area)
        # An area chart looks better for "Health"
        chart_score.area_chart(df["score"], color="#FF4B4B" if status == "ANOMALY" else "#0068C9")

        # --- UPDATE RAW DATA TAB ---
        # Show newest data first
        dataframe_placeholder.dataframe(df.sort_index(ascending=False).head(10), use_container_width=True)

    time.sleep(1) # Refresh rate