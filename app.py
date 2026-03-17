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

st.title("🐆 Mdluli Safari Lodge Executive Pulse")

# --- DATA CONNECTION ---
# We are pulling the FIRST tab of the sheet, regardless of what it is named.
sheet_id = "1FomdHZww0k2pWMS1cTzDJUss8NpAOnsaZkRXyvGjUYM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=10) 
def load_data():
    data = pd.read_csv(url)
    data.columns = data.columns.str.strip() # Remove spaces from headers
    return data

try:
    df = load_data()
    
    # We pull by row position so we don't care about typos in the names
    # Row 0 = Revenue | Row 1 = Room Nights
    rev_actual = float(df.iloc[0, 4])  # Column E
    rev_gold = float(df.iloc[0, 3])    # Column D
    rev_base = float(df.iloc[0, 1])    # Column B
    rev_silver = float(df.iloc[0, 2])  # Column C

    room_actual = float(df.iloc[1, 4])
    room_base = float(df.iloc[1, 1])
    room_gold = float(df.iloc[1, 3])

    # --- VISUALS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Revenue Performance")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_actual,
            number = {'prefix': "R", 'font': {'size': 40, 'color': '#2C2C2C'}},
            gauge = {
                'axis': {'range': [None, rev_gold]},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, rev_base], 'color': "#D6D1C4"},
                    {'range': [rev_base, rev_silver], 'color': "#E5E1D8"}
                ],
                'threshold': {
                    'line': {'color': "#2C2C2C", 'width': 4},
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
            number = {'font': {'size': 40, 'color': '#2C2C2C'}},
            gauge = {
                'axis': {'range': [None, room_gold]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, room_base], 'color': "#D6D1C4"}
                ]
            }
        ))
        st.plotly_chart(fig_room, use_container_width=True)

    st.markdown("<center>🐆 <b>Mdluli Leopard Link Active</b></center>", unsafe_allow_html=True)

except Exception as e:
    st.error("Checking Data Alignment...")
    st.info("Almost there. Make sure the 'Dashboard feed' tab is the VERY FIRST tab (far left) in your Google Sheet.")
