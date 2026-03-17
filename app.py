import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Executive Dashboard", layout="wide")

# --- BRANDING & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🦁 Mdluli Safari Lodge Executive Pulse")

# --- DATA CONNECTION ---
# This is the link to your "Shadow Sheet"
sheet_id = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
sheet_name = "DASHBOARD_FEED"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=600) # Refresh every 10 mins
def load_data():
    return pd.read_csv(url)

try:
    df = load_data()
    
    # Extracting the values from your DASHBOARD_FEED rows
    rev_actual = df.iloc[0]['Actual']
    rev_base = df.iloc[0]['Base Target']
    rev_silver = df.iloc[0]['Silver Target']
    rev_gold = df.iloc[0]['Gold Target']
    
    room_actual = df.iloc[1]['Actual']
    room_base = df.iloc[1]['Base Target']
    room_gold = df.iloc[1]['Gold Target']

    # --- VISUALS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Revenue Performance")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_actual,
            number = {'prefix': "R", 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, rev_gold]},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, rev_base], 'color': "#D6D1C4"},
                    {'range': [rev_base, rev_silver], 'color': "#E5E1D8"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 3},
                    'thickness': 0.75,
                    'value': rev_gold}
            }
        ))
        st.plotly_chart(fig_rev, use_container_width=True)

    with col2:
        st.subheader("Room Nights Performance")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = room_actual,
            gauge = {
                'axis': {'range': [None, room_gold]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, room_base], 'color': "#D6D1C4"}
                ]
            }
        ))
        st.plotly_chart(fig_room, use_container_width=True)

    st.success(f"✅ Live Data Synced from Google Sheets")

except Exception as e:
    st.error("Connection Pending: We need to make the Google Sheet 'Shareable' in the next step.")
