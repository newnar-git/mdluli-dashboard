import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Executive Dashboard", layout="wide")

# --- BRANDING & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 45px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge Executive Pulse</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Financial Year 2025/26 Performance</p>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
sheet_id = "1FomdHZww0k2pWMS1cTzDJUss8NpAOnsaZkRXyvGjUYM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60) 
def load_data():
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

def to_num(val):
    try:
        return float(str(val).replace('R', '').replace(',', '').replace(' ', '').strip())
    except:
        return 0.0

try:
    df = load_data()
    
    # Extract Values
    rev_actual = to_num(df.iloc[0]['Actual'])
    rev_base   = to_num(df.iloc[0]['Base Target'])
    rev_silver = to_num(df.iloc[0]['Silver Target'])
    rev_gold   = to_num(df.iloc[0]['Gold Target'])

    room_actual = to_num(df.iloc[1]['Actual'])
    room_base   = to_num(df.iloc[1]['Base Target'])
    room_gold   = to_num(df.iloc[1]['Gold Target'])

    # --- VISUALS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Revenue Status")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_actual,
            number = {'prefix': "R", 'font': {'size': 45, 'color': '#2C2C2C'}, 'valueformat': ',.0f'},
            gauge = {
                'axis': {'range': [None, rev_gold], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, rev_base], 'color': "#D6D1C4"},
                    {'range': [rev_base, rev_silver], 'color': "#E5E1D8"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': rev_gold}
            }
        ))
        st.plotly_chart(fig_rev, use_container_width=True)
        st.caption(f"Gold Target: R{rev_gold:,.0f}")

    with col2:
        st.subheader("Room Nights Status")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = room_actual,
            number = {'font': {'size': 45, 'color': '#2C2C2C'}, 'valueformat': ',.0f'},
            gauge = {
                'axis': {'range': [None, room_gold]},
                'bar': {'color': "#4A5D4E"},
                'steps': [{'range': [0, room_base], 'color': "#D6D1C4"}]
            }
        ))
        st.plotly_chart(fig_room, use_container_width=True)
        st.caption(f"Gold Target: {room_gold:,.0f} Nights")

    st.markdown("---")
    st.markdown("<center>✅ <b>Mdluli Intelligence System Active</b> | Data synced with Google Sheets</center>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"System Check: {e}")
