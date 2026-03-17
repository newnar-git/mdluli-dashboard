import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Master Command", layout="wide")

# --- BRANDING ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 42px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Executive Command Center</h1>", unsafe_allow_html=True)

# --- DATA CONNECTION (Master Sheet) ---
SHEET_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"

@st.cache_data(ttl=60)
def get_tab_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def clean_val(val):
    try:
        return float(str(val).replace('R', '').replace(',', '').replace('%', '').strip())
    except:
        return 0.0

# --- APP LOGIC ---
try:
    # GID for 'Target v Actual FY25/26' is usually the first one or we use the specific one from your URL
    # Pulling Finance Data
    df_finance = get_tab_data("1602025819") 
    
    # Sidebar Navigation for Execs
    st.sidebar.image("https://www.mdlulisafarilodge.co.za/wp-content/uploads/2019/08/Mdluli-Logo-Gold.png", width=150)
    view = st.sidebar.selectbox("Select Department View", ["Executive Summary", "Financial Depth", "Marketing & Offers"])

    if view == "Executive Summary":
        st.subheader("Financial Performance vs Targets")
        
        # Pulling specific cells based on your Master Sheet layout
        # (Assuming Revenue is Row 3, Room Nights Row 5)
        rev_act = clean_val(df_finance.iloc[2, 1]) # Adjusting to look at Column B
        rev_gold = clean_val(df_finance.iloc[2, 5]) # Column F
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("YTD Revenue", f"R{rev_act:,.0f}")
        with c2:
            st.metric("Gold Target", f"R{rev_gold:,.0f}")
        with c3:
            st.metric("Pace to Gold", f"{(rev_act/rev_gold)*100:.1f}%")

        # Visual Gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_act,
            number = {'prefix': "R", 'valueformat': ',.0f'},
            gauge = {
                'axis': {'range': [None, rev_gold]},
                'bar': {'color': "#C5A059"},
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': rev_gold}
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

    elif view == "Marketing & Offers":
        st.subheader("2025 Offers Insights")
        st.info("Pulling live from '2025 Offers insights' tab...")
        # We would add marketing-specific charts here
        st.write("Current Focus: Getaway Offer - 15% (-30 Days booking Window)")

    st.markdown("---")
    st.write("### 🔍 Raw Master Data Explorer")
    st.dataframe(df_finance.style.highlight_max(axis=0), use_container_width=True)

except Exception as e:
    st.error(f"Master Connection Error: {e}")
    st.info("Check: Is the Master Sheet still set to 'Anyone with the link can view'?")
