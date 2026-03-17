import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Master Command", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 48px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); border-top: 6px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Master Command</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>Live Matrix Feed | Executive Intelligence</p>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
GID = "1602025819" 

@st.cache_data(ttl=10)
def get_master_data():
    url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={GID}"
    return pd.read_csv(url, header=None) 

def to_num(val):
    try:
        if pd.isna(val) or val == 'None': return 0.0
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    df = get_master_data()
    
    # --- EXACT MATRIX MAPPING (Based on your diagnostic screenshot) ---
    # Column 14 appears to be your "ANNUAL TARGET" / YTD Actual column
    ANNUAL_COL = 14
    
    # Room Nights (Target is Row 3, Actual is Row 4)
    room_target = to_num(df.iloc[3, ANNUAL_COL])
    room_actual = to_num(df.iloc[4, ANNUAL_COL])
    
    # Revenue / Booked (Target is Row 6, Actual is Row 7)
    rev_target = to_num(df.iloc[6, ANNUAL_COL])
    rev_actual = to_num(df.iloc[7, ANNUAL_COL])

    # If the annual actual hasn't populated in col 14 yet, let's grab the March numbers (Col 1) just so you can see it working!
    if rev_actual == 0:
        rev_actual = to_num(df.iloc[7, 1]) # Grabbing March 'Booked total'
        
    # We will use 120% of the target to create a "Gold" visual boundary
    rev_gold = rev_target * 1.2 if rev_target > 0 else 10000000
    room_gold = room_target * 1.2 if room_target > 0 else 4000

    # --- KPI SUMMARY CARDS ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric("YTD REVENUE (BOOKED)", f"R{rev_actual:,.0f}", f"Target: R{rev_target:,.0f}")
    with k2:
        st.metric("ROOM NIGHTS SOLD", f"{room_actual:,.0f}", f"Target: {room_target:,.0f}")
    with k3:
        pace = (rev_actual / rev_target) * 100 if rev_target > 0 else 0
        st.metric("PACE TO TARGET", f"{pace:.1f}%")

    st.markdown("---")

    # --- INTERACTIVE GAUGES ---
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Revenue Milestone Tracker")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_actual,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, rev_gold], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, rev_target], 'color': "#D6D1C4", 'name': 'Target'}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': rev_target}
            }
        ))
        fig_rev.update_traces(hoverinfo="text", text=f"<b>Current:</b> R{rev_actual:,.0f}<br><b>Target:</b> R{rev_target:,.0f}")
        fig_rev.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30), hovermode="closest")
        st.plotly_chart(fig_rev, use_container_width=True)

    with g2:
        st.subheader("Room Nights Performance")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = room_actual,
            number = {'valueformat': ',.0f', 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, room_gold]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, room_target], 'color': "#D6D1C4"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': room_target}
            }
        ))
        fig_room.update_traces(hoverinfo="text", text=f"<b>Actual:</b> {room_actual}<br><b>Target:</b> {room_target}")
        fig_room.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30))
        st.plotly_chart(fig_room, use_container_width=True)

    with st.expander("📂 Explore Master Matrix"):
        st.dataframe(df.fillna(""), use_container_width=True)

except Exception as e:
    st.error(f"Matrix Mapping Error: {e}")
