import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Interactive Command", layout="wide")

# --- BRANDING ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 45px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Executive Suite</h1>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"

@st.cache_data(ttl=10) # Fast refresh for testing
def get_data():
    url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid=1602025819"
    df = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def to_num(val):
    try:
        if pd.isna(val): return 0.0
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    raw_df = get_data()
    
    # Precision Search for Metrics
    rev_row = raw_df[raw_df.iloc[:, 0].str.contains("Total Revenue", na=False, case=False)]
    room_row = raw_df[raw_df.iloc[:, 0].str.contains("Room Nights", na=False, case=False)]

    # Data Mapping (Col B=Actual, Col C=Silver, Col D=Base, Col F=Gold)
    # Note: I adjusted indices to match your sheet's specific layout
    actual_rev = to_num(rev_row.iloc[0, 1])
    base_rev   = to_num(rev_row.iloc[0, 3])
    silver_rev = to_num(rev_row.iloc[0, 4]) # Assuming Col E is Silver
    gold_rev   = to_num(rev_row.iloc[0, 5])
    
    actual_room = to_num(room_row.iloc[0, 1])
    base_room   = to_num(room_row.iloc[0, 3])
    gold_room   = to_num(room_row.iloc[0, 5])

    # --- KPI SUMMARY ---
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("YTD Revenue", f"R{actual_rev:,.0f}")
    with c2: st.metric("Room Nights", f"{actual_room:,.0f}")
    with c3: 
        pace = (actual_rev / gold_rev) * 100 if gold_rev > 0 else 0
        st.metric("Pace to Gold", f"{pace:.1f}%")

    st.markdown("---")

    # --- INTERACTIVE GAUGES ---
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Interactive Revenue Tracker")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = actual_rev,
            number = {'prefix': "R", 'valueformat': ',.0f'},
            gauge = {
                'axis': {'range': [None, gold_rev], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, base_rev], 'color': "#D6D1C4"},
                    {'range': [base_rev, silver_rev], 'color': "#E5E1D8"},
                    {'range': [silver_rev, gold_rev], 'color': "#F2EFE9"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': gold_rev}
            }
        ))
        # This is the "Magic" part: Setting up the Hover Text
        fig_rev.update_traces(
            hoverinfo="name+value",
            name=f"Current: R{actual_rev:,.0f}<br>Base: R{base_rev:,.0f}<br>Silver: R{silver_rev:,.0f}<br>GOLD: R{gold_rev:,.0f}"
        )
        fig_rev.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30))
        st.plotly_chart(fig_rev, use_container_width=True)

    with g2:
        st.subheader("Room Nights Performance")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = actual_room,
            number = {'valueformat': ',.0f'},
            gauge = {
                'axis': {'range': [None, gold_room]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, base_room], 'color': "#D6D1C4"},
                    {'range': [base_room, gold_room], 'color': "#E5E1D8"}
                ]
            }
        ))
        fig_room.update_traces(
            hoverinfo="name+value",
            name=f"Actual: {actual_room}<br>Base: {base_room}<br>Gold Goal: {gold_room}"
        )
        fig_room.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30))
        st.plotly_chart(fig_room, use_container_width=True)

    # --- EXPANDABLE DATA VIEW ---
    with st.expander("📂 View Master Source Data"):
        st.dataframe(raw_df.fillna(""), use_container_width=True)

except Exception as e:
    st.error(f"Logic Sync Error: {e}")
