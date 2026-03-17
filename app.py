import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Executive Dashboard", layout="wide")

# --- BRANDING & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 45px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦁 Mdluli Safari Lodge Executive Pulse")

# --- DATA CONNECTION ---
sheet_id = "1FomdHZww0k2pWMS1cTzDJUss8NpAOnsaZkRXyvGjUYM"
# We use '0' to pull the first tab if the name is tricky
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60) 
def load_data():
    # Pulling data and cleaning up any accidental spaces in headers
    data = pd.read_csv(url)
    data.columns = data.columns.str.strip()
    return data

try:
    df = load_data()
    
    # Mapping the data by looking for keywords rather than exact matches
    # This makes it much harder for the app to fail
    rev_row = df[df['Metric'].str.contains('Revenue', na=False)].iloc[0]
    room_row = df[df['Metric'].str.contains('Room', na=False)].iloc[0]

    # --- VISUALS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Revenue Performance")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = float(rev_row['Actual']),
            number = {'prefix': "R", 'font': {'size': 40, 'color': '#2C2C2C'}},
            gauge = {
                'axis': {'range': [None, float(rev_row['Gold Target'])]},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, float(rev_row['Base Target'])], 'color': "#D6D1C4"},
                    {'range': [float(rev_row['Base Target']), float(rev_row['Silver Target'])], 'color': "#E5E1D8"}
                ],
                'threshold': {
                    'line': {'color': "#2C2C2C", 'width': 4},
                    'thickness': 0.75,
                    'value': float(rev_row['Gold Target'])}
            }
        ))
        st.plotly_chart(fig_rev, use_container_width=True)

    with col2:
        st.subheader("Room Nights Performance")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = float(room_row['Actual']),
            number = {'font': {'size': 40, 'color': '#2C2C2C'}},
            gauge = {
                'axis': {'range': [None, float(room_row['Gold Target'])]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, float(room_row['Base Target'])], 'color': "#D6D1C4"}
                ]
            }
        ))
        st.plotly_chart(fig_room, use_container_width=True)

    st.markdown("<center>✅ <b>Mdluli Live Link Active</b></center>", unsafe_allow_html=True)

except Exception as e:
    st.error("Data Alignment: I can see the sheet, but I'm checking the rows.")
    st.info("Make sure 'Total Revenue' is in cell A2 and 'Room Nights' is in cell A3.")
