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
    
    # --- EXACT MATRIX MAPPING ---
    ANNUAL_COL = 14
    
    # Room Nights (Target is Row 3, Actual is Row 4)
    room_target = to_num(df.iloc[3, ANNUAL_COL])
    room_actual = to_num(df.iloc[4, ANNUAL_COL])
    
    # Revenue / Booked (Target is Row 6, Actual is Row 7)
    rev_target = to_num(df.iloc[6, ANNUAL_COL])
    rev_actual = to_num(df.iloc[7, ANNUAL_COL])

    # Let's ensure a visual target exists even if the sheet is blank for now
    visual_rev_target = rev_target if rev_target > 0 else 10000000
    rev_gold = visual_rev_target * 1.2 
    
    visual_room_target = room_target if room_target > 0 else 4000
    room_gold = visual_room_target * 1.2 

    # --- KPI SUMMARY CARDS ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        # Added native tooltips directly to the metric cards
        st.metric(
            "YTD REVENUE (BOOKED)", 
            f"R{rev_actual:,.0f}", 
            f"Target: R{rev_target:,.0f}" if rev_target > 0 else "No Target in Sheet",
            help=f"Actual: R{rev_actual:,.0f} | Target: R{rev_target:,.0f}"
        )
    with k2:
        st.metric(
            "ROOM NIGHTS SOLD", 
            f"{room_actual:,.0f}", 
            f"Target: {room_target:,.0f}",
            help=f"Actual: {room_actual:,.0f} | Target: {room_target:,.0f}"
        )
    with k3:
        pace = (rev_actual / visual_rev_target) * 100 
        st.metric("PACE TO TARGET", f"{pace:.1f}%")

    st.markdown("---")

    # --- INTERACTIVE GAUGES ---
    g1, g2 = st.columns(2)
    
    with g1:
        # Added the tooltip (?) to the subheader so execs can hover for details
        st.subheader("Revenue Milestone Tracker", help=f"Current: R{rev_actual:,.0f} \nTarget: R{rev_target:,.0f}")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_actual,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, rev_gold], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, visual_rev_target], 'color': "#D6D1C4"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': visual_rev_target}
            }
        ))
        fig_rev.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30))
        st.plotly_chart(fig_rev, use_container_width=True)

    with g2:
        st.subheader("Room Nights Performance", help=f"Actual: {room_actual:,.0f} \nTarget: {room_target:,.0f}")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = room_actual,
            number = {'valueformat': ',.0f', 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, room_gold]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, visual_room_target], 'color': "#D6D1C4"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': visual_room_target}
            }
        ))
        fig_room.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30))
        st.plotly_chart(fig_room, use_container_width=True)

    with st.expander("📂 Explore Master Matrix"):
        st.dataframe(df.fillna(""), use_container_width=True)

except Exception as e:
    st.error(f"Matrix Mapping Error: {e}")
