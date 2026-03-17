import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Executive Dashboard", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #F2EFE9; }
    h1 { color: #C5A059; font-family: 'serif'; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦁 Mdluli Safari Lodge Performance")

# --- DATA LOADING ---
# We will connect your actual Google Sheet in the next step.
# For now, this is your "live" data structure.
data = {
    "Metric": ["Total Revenue", "Room Nights"],
    "Actual": [15585704, 2203],
    "Base": [16718370, 3174],
    "Silver": [17554246, 3426],
    "Gold": [18431959, 3597]
}
df = pd.DataFrame(data)

# --- VISUALS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Revenue YTD")
    fig_rev = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = df.loc[0, 'Actual'],
        number = {'prefix': "R", 'font': {'color': '#2C2C2C'}},
        gauge = {
            'axis': {'range': [None, df.loc[0, 'Gold' ]]},
            'bar': {'color': "#C5A059"},
            'steps': [
                {'range': [0, df.loc[0, 'Base']], 'color': "#D6D1C4"},
                {'range': [df.loc[0, 'Base'], df.loc[0, 'Silver']], 'color': "#E5E1D8"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': df.loc[0, 'Gold']}
        }
    ))
    st.plotly_chart(fig_rev, use_container_width=True)

with col2:
    st.subheader("Room Nights Sold")
    fig_room = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = df.loc[1, 'Actual'],
        number = {'font': {'color': '#2C2C2C'}},
        gauge = {
            'axis': {'range': [None, df.loc[1, 'Gold']]},
            'bar': {'color': "#4A5D4E"},
            'steps': [
                {'range': [0, df.loc[1, 'Base']], 'color': "#D6D1C4"},
                {'range': [df.loc[1, 'Base'], df.loc[1, 'Silver']], 'color': "#E5E1D8"}
            ]
        }
    ))
    st.plotly_chart(fig_room, use_container_width=True)

st.info("💡 Next Step: We will link this app to your live Google Sheet so these numbers update automatically.")
