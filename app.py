import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Executive Command", layout="wide")

# --- BRANDING & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 45px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Executive Command</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Live Master Data Feed: FY25/26 Performance</p>", unsafe_allow_html=True)

# --- DATA CONNECTION (Direct to Master) ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"

@st.cache_data(ttl=60)
def get_master_tab(gid):
    url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def to_num(val):
    try:
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    # Pulling 'Target v Actual FY25/26' (GID 1602025819)
    df = get_master_tab("1602025819")
    
    # --- MAPPING DATA ---
    # Revenue is Row 3 (Index 2), Room Nights Row 5 (Index 4)
    # Col B (Index 1) is Actual | Col D (Index 3) is Base | Col F (Index 5) is Gold
    
    rev_act  = to_num(df.iloc[2, 1])
    rev_base = to_num(df.iloc[2, 3])
    rev_gold = to_num(df.iloc[2, 5])
    
    room_act  = to_num(df.iloc[4, 1])
    room_base = to_num(df.iloc[4, 3])
    room_gold = to_num(df.iloc[4, 5])

    # --- TOP ROW: KPI CARDS ---
    st.markdown("### 📊 Key Performance Indicators")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric("YTD Revenue", f"R{rev_act:,.0f}", f"Target: R{rev_base:,.0f}")
    with k2:
        st.metric("Room Nights", f"{room_act:,.0f}", f"Target: {room_base:,.0f}")
    with k3:
        pace = (rev_act / rev_gold) * 100 if rev_gold > 0 else 0
        st.metric("Pace to Gold", f"{pace:.1f}%", "Overall Progress")

    st.markdown("---")

    # --- MIDDLE ROW: THE PULSE ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Revenue Status vs Gold")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_act,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'color': '#2C2C2C'}},
            gauge = {
                'axis': {'range': [None, rev_gold], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, rev_base], 'color': "#D6D1C4"},
                    {'range': [rev_base, rev_gold], 'color': "#E5E1D8"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': rev_gold}
            }
        ))
        st.plotly_chart(fig_rev, use_container_width=True)
        st.caption(f"**Gold Target Milestone:** R{rev_gold:,.0f}")

    with c2:
        st.subheader("Room Nights Status vs Gold")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = room_act,
            number = {'valueformat': ',.0f', 'font': {'color': '#2C2C2C'}},
            gauge = {
                'axis': {'range': [None, room_gold]},
                'bar': {'color': "#4A5D4E"},
                'steps': [{'range': [0, room_base], 'color': "#D6D1C4"}]
            }
        ))
        st.plotly_chart(fig_room, use_container_width=True)
        st.caption(f"**Gold Target Milestone:** {room_gold:,.0f} Nights")

    st.markdown("---")
    
    # --- BOTTOM ROW: THE DATA EXPLORER ---
    with st.expander("📂 View Master Financial Table"):
        st.write("This is a live look at your 'Target v Actual FY25/26' spreadsheet tab.")
        # Cleaning up the display table for the CFO
        clean_df = df.fillna("")
        st.dataframe(clean_df, use_container_width=True)

    st.markdown("<center>🐆 <b>Mdluli Intelligence System Active</b> | No Manual Input Required</center>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Sync Error: {e}")
    st.info("The system is having trouble reading the Master Sheet. Ensure the tab 'Target v Actual FY25/26' is correctly shared.")
