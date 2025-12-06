"""
AI Admin Dashboard - Streamlit Interface
Allows administrators to train/retrain models, view accuracy, and manage AI engine
"""

import streamlit as st
import sys
import os
import pickle
from datetime import datetime
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import training module
try:
    from train_model import train_model
except ImportError:
    st.error("Could not import train_model. Make sure train_model.py is in the src/ directory.")
    train_model = None

# Page config
st.set_page_config(
    page_title="AI Engine Admin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:50px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="big-font">🤖 AI Engine Admin</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎛️ Control Panel")
    st.markdown("**Model Management**")
    
    # Get model info
    model_path = "/app/models/anomaly_model.pkl"
    model_exists = os.path.exists(model_path)
    
    if model_exists:
        model_info = os.stat(model_path)
        model_date = datetime.fromtimestamp(model_info.st_mtime)
        st.success(f"✅ Model Active")
        st.caption(f"Last trained: {model_date.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.warning("⚠️ No model found")
        st.caption("Train a model to get started")

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Model Status")
    if model_exists:
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            model_type = type(model).__name__
            st.metric("Model Type", model_type)
            
            # Check if model has n_estimators (for IsolationForest)
            if hasattr(model, 'n_estimators'):
                st.metric("Estimators", model.n_estimators)
            
            # Check contamination
            if hasattr(model, 'contamination'):
                st.metric("Contamination", f"{model.contamination:.2%}")
                
        except Exception as e:
            st.error(f"Error loading model: {e}")
    else:
        st.info("No model loaded")

with col2:
    st.markdown("### 🎯 Training Status")
    
    # Check training data
    training_data_path = "/app/data/training_data.csv"
    if os.path.exists(training_data_path):
        try:
            df = pd.read_csv(training_data_path)
            st.metric("Training Samples", len(df))
            st.caption(f"Features: {', '.join(df.columns[:3])}...")
        except Exception as e:
            st.warning(f"Could not read training data: {e}")
    else:
        st.warning("No training data found")

with col3:
    st.markdown("### ⚡ System Info")
    st.metric("AI Engine", "Running")
    st.metric("API Port", "8000")
    st.metric("Dashboard Port", "8501")

st.markdown("---")

# Training Section
st.header("🚀 Model Training")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Train New Model")
    st.info("Training will use the data in /app/data/training_data.csv")
    
    # Training options
    with st.expander("⚙️ Training Options"):
        n_estimators = st.slider("Number of Estimators", 50, 300, 100, 50)
        contamination = st.slider("Contamination Factor", 0.01, 0.5, 0.1, 0.01)
        random_state = st.number_input("Random State", 0, 1000, 42)

with col2:
    st.markdown("### Quick Actions")
    
    if st.button("🎯 Train Model", use_container_width=True, type="primary"):
        with st.spinner("Training model... This may take a few minutes."):
            try:
                if train_model:
                    # Call training function
                    result = train_model()
                    st.success("✅ Model trained successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Training function not available")
            except Exception as e:
                st.error(f"❌ Training failed: {e}")
    
    if st.button("🔄 Retrain Model", use_container_width=True):
        if model_exists:
            with st.spinner("Retraining model..."):
                try:
                    if train_model:
                        result = train_model()
                        st.success("✅ Model retrained successfully!")
                        st.rerun()
                    else:
                        st.error("Training function not available")
                except Exception as e:
                    st.error(f"❌ Retraining failed: {e}")
        else:
            st.warning("No existing model to retrain. Use 'Train Model' instead.")
    
    if st.button("🗑️ Reset Model", use_container_width=True):
        if model_exists:
            if st.button("⚠️ Confirm Reset"):
                try:
                    os.remove(model_path)
                    st.success("Model deleted successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete model: {e}")
        else:
            st.info("No model to reset")

st.markdown("---")

# Logs Section
st.header("📜 Recent Logs")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### FastAPI Logs")
    fastapi_log = "/app/logs/fastapi.out.log"
    if os.path.exists(fastapi_log):
        try:
            with open(fastapi_log, 'r') as f:
                logs = f.readlines()[-20:]  # Last 20 lines
            st.code('\n'.join(logs), language='text')
        except Exception as e:
            st.warning(f"Could not read logs: {e}")
    else:
        st.info("No logs available yet")

with col2:
    st.markdown("### AI Consumer Logs")
    ai_log = "/app/logs/ai_consumer.out.log"
    if os.path.exists(ai_log):
        try:
            with open(ai_log, 'r') as f:
                logs = f.readlines()[-20:]  # Last 20 lines
            st.code('\n'.join(logs), language='text')
        except Exception as e:
            st.warning(f"Could not read logs: {e}")
    else:
        st.info("No logs available yet")

# Footer
st.markdown("---")
st.markdown("**IIoT Predictive Maintenance** | AI Engine Administration Dashboard")
st.caption("Access API at http://localhost:8000 | API Docs at http://localhost:8000/docs")
