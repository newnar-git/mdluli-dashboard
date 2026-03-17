import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Master Command", layout="wide")

# --- BRANDING & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 42px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Executive Command Center</h1>", unsafe_allow_html=True)

# --- DATA CONNECTION (Direct to Master) ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"

@st.cache_data(ttl=60)
def get_master_tab(gid):
    url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    return df

def to_num(val):
    try:
        # Handles Rands, Percentages, and Commas automatically
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    # Sidebar for Department Switching
    st.sidebar.title("Navigation")
    view = st.sidebar.selectbox("Select View", ["Finance (CFO/CEO)", "Marketing (CMO/GM)"])

    if view == "Finance (CFO/CEO)":
        # Pulling 'Target v Actual FY25/26' (GID 1602025819)
        df = get_master_tab("1602025819")
        
        st.subheader("Financial Performance vs Targets")
        
        # Pulling indices based on your Master Sheet layout
        rev_act = to_num(df.iloc[2, 1])  # Row 3, Col B
        rev_base = to_num(df.iloc[2, 3]) # Row 3, Col D
        rev_gold = to_num(df.iloc[2, 5]) # Row 3, Col F
        
        room_act = to_num(df.iloc[4, 1]) # Row 5, Col B
        room_gold = to_num(df.iloc[4, 5]) # Row 5, Col F

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Revenue", f"R{rev_act:,.0f}", f"Target: R{rev_base:,.0f}", delta_color="off")
        with c2:
            st.metric("Room Nights", f"{room_act:,.0f}", f"Target: {room_gold:,.0f}", delta_color="off")
        with c3:
            st.metric("Pace to Gold", f"{(rev_act/rev_gold)*100:.1f}%")

        # Revenue Gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_act,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, rev_gold], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': rev_gold}
            }
        ))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    elif view == "Marketing (CMO/GM)":
        # Pulling '2025 Offers insights' (Using a guess at GID, we can refine this)
        st.subheader("Marketing & Special Offers Pulse")
        st.info("Direct Feed from '2025 Offers insights' tab")
        st.write("### Active Campaigns")
        st.markdown("- **Getaway Offer:** 15% Discount")
        st.markdown("- **Early Year Deal:** Closing March end")

    st.markdown("---")
    st.write("### 🔍 Live Data Explorer")
    # Clean up display: replaces NaNs with empty space for the execs
    st.dataframe(df.fillna(""), use_container_width=True)

except Exception as e:
    st.error(f"Master Sync Error: {e}")
    st.info("Ensure the Master Sheet is set to 'Anyone with the link can view'.")
