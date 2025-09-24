#!/usr/bin/env python
import os
import json
import time
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from google import genai
from datetime import datetime, timedelta
import logging

# -------------------------- Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------- Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ML_API_URL = os.getenv("ML_API_URL", "http://scm_ml-api:8001")

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------- Helper functions
def get_recent_data(df, months=3):
    if df.empty or 'requested_date' not in df.columns:
        return pd.DataFrame()
    df['requested_date'] = pd.to_datetime(df['requested_date'], errors='coerce')
    cutoff = datetime.now() - timedelta(days=30*months)
    return df[df['requested_date'] >= cutoff]

def ensure_column(df, col):
    if col not in df.columns:
        df[col] = None
    return df

# ... keep your chatbot, forecast, analysis, and inventory functions here unchanged ...

# -------------------------- Streamlit App
st.set_page_config(page_title="SCM Dashboard (CSV)", page_icon="📊", layout="wide")

def call_prediction_api(project_name, item_name):
    try:
        payload = {
            "project_name": project_name,
            "item_name": item_name,
            "requested_date": datetime.now().strftime("%Y-%m-%d"),
            "in_use": 1
        }
        response = requests.post(f"{ML_API_URL}/predict", json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("predicted_quantity", None)
        else:
            st.error(f"Prediction API error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to call ML API: {e}")
        return None

def main():
    st.markdown("""
        <div style="background-color:#16a34a;color:white;padding:1rem;border-radius:0.5rem;margin-bottom:1rem;">
            <h1 style="margin:0;">📦 SCM Dashboard (CSV Mode)</h1>
            <p style="margin:0;">Monitor inventory and transactions using static CSVs</p>
        </div>
    """, unsafe_allow_html=True)

    # ---------------- Load CSVs
    requests_csv = "requests.csv"
    inventory_csv = "inventory.csv"

    if not os.path.exists(requests_csv) or not os.path.exists(inventory_csv):
        st.error("❌ Missing CSV files. Please place `requests.csv` and `inventory.csv` in the app directory.")
        return

    requests_df = pd.read_csv(requests_csv)
    inventory_df = pd.read_csv(inventory_csv)

    # Handle project_display
    if 'requested_project_name' in requests_df.columns:
        requests_df['project_display'] = requests_df['requested_project_name'].fillna('').astype(str).str.strip()
    else:
        requests_df['project_display'] = pd.Series([''] * len(requests_df))

    if 'department_id' in inventory_df.columns:
        inventory_df['project_display'] = inventory_df['department_id'].fillna('').astype(str).str.strip()
    else:
        inventory_df['project_display'] = pd.Series([''] * len(inventory_df))

    # Ensure extra fields
    new_fields = ['returned_date', 'is_requester_received', 'requester_received_date',
                  'current_consumed_amount', 'consumed_amount', 'is_approved', 'approved_date']
    for col in new_fields:
        requests_df = ensure_column(requests_df, col)
        inventory_df = ensure_column(inventory_df, col)

    # ---------------- Sidebar filters
    with st.sidebar:
        st.markdown("## Project Filters")
        selected_project_inventory = st.selectbox(
            "Inventory Project",
            ["All Projects"] + sorted(inventory_df['project_display'].unique().tolist())
        )
        selected_project_usage = st.selectbox(
            "Usage Project",
            ["All Projects"] + sorted(requests_df['project_display'].unique().tolist())
        )

    # ---------------- Main Layout
    # ✅ inventory, usage, prediction, chatbot stay the same as in your original script
    # just use `requests_df` and `inventory_df` (already loaded from CSV)

    st.success("✅ Loaded data from static CSV files")

    # (insert your existing sections: inventory display, usage analytics, alerts, predictions, chatbot...)

if __name__ == "__main__":
    main()
