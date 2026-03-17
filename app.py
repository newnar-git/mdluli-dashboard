import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Command Center", layout="wide")

# --- BRANDING ---
st.markdown("""
    <style>
    .main { background-color: #F4F1EA; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 50px; margin-bottom: 0; }
    .card { background-color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #C5A059; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Executive Command Center</h1>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
sheet_id = "1FomdHZww0k2pWMS1cTzDJUss8NpAOnsaZkRXyvGjUYM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

def to_num(val):
    try: return float(str(val).replace('R', '').replace(',', '').replace(' ', '').strip())
    except: return 0.0

try:
    df = load_data()
    
    # 1. REVENUE DATA
    rev_act = to_num(df.iloc[0]['Actual'])
    rev_base = to_num(df.iloc[0]['Base Target'])
    rev_gold = to_num(df.iloc[0]['Gold Target'])
    rev_gap = rev_gold - rev_act

    # 2. ROOM NIGHTS DATA
    room_act = to_num(df.iloc[1]['Actual'])
    room_base = to_num(df.iloc[1]['Base Target'])
    room_gold = to_num(df.iloc[1]['Gold Target'])
    room_gap = room_gold - room_act

    # --- TOP ROW: KPI CARDS ---
    st.markdown("### 📊 Key Performance Indicators")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.markdown(f"<div class='card'><h4>Total Revenue</h4><h2>R{rev_act:,.0f}</h2><p style='color:red;'>Gap to Gold: R{rev_gap:,.0f}</p></div>", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"<div class='card'><h4>Room Nights</h4><h2>{room_act:,.0f}</h2><p style='color:red;'>Gap to Gold: {room_gap:,.0f} Nights</p></div>", unsafe_allow_html=True)
    with kpi3:
        occ = (room_act / 3650) * 100 # Assuming a rough capacity for visual
        st.markdown(f"<div class='card'><h4>Est. Occupancy</h4><h2>{occ:.1f}%</h2><p>YTD Average</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- MIDDLE ROW: THE PERFORMANCE TRACKER ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Revenue vs Milestone Targets")
        # Visualizing the distance between milestones
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=['Current Performance'], x=[rev_act],
            name='Actual Revenue', orientation='h', marker=dict(color='#C5A059')
        ))
        # Adding target lines
        fig.add_vline(x=rev_base, line_dash="dash", line_color="orange", annotation_text="Base")
        fig.add_vline(x=rev_gold, line_dash="dash", line_color="green", annotation_text="GOLD")
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 The green dashed line is your **Gold Target**. Your mission is to push the gold bar to meet that line.")

    with col_right:
        st.subheader("Target Breakdown")
        st.write(f"**Base:** R{rev_base:,.0f}")
        st.write(f"**Silver:** R{to_num(df.iloc[0]['Silver Target']):,.0f}")
        st.write(f"**Gold:** R{rev_gold:,.0f}")
        
    st.markdown("---")
    st.markdown("### 🛠️ Detailed Analysis")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for full data stream... {e}")
