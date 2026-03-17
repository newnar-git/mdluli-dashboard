import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Master Command", layout="wide")

# --- BRANDING & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 48px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); border-top: 6px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Master Command</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>Live Executive Intelligence | Financial Year 2025/26</p>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
GID = "1602025819" 

@st.cache_data(ttl=10)
def get_master_data():
    url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url, header=None) 
    return df

def to_num(val):
    try:
        if pd.isna(val): return 0.0
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    raw_df = get_master_data()
    
    # --- FUZZY SEARCH LOGIC ---
    # We scan the sheet for the specific rows. This makes the app much more robust.
    def find_row_data(keyword):
        mask = raw_df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
        row_idx = raw_df[mask].index[0]
        return raw_df.iloc[row_idx]

    rev_data = find_row_data("Total Revenue")
    room_data = find_row_data("Room Nights")

    # Map the numbers: Col B=Actual(1), Col D=Base(3), Col E=Silver(4), Col F=Gold(5)
    actual_rev = to_num(rev_data[1])
    base_rev   = to_num(rev_data[3])
    silver_rev = to_num(rev_data[4])
    gold_rev   = to_num(rev_data[5])
    
    actual_room = to_num(room_data[1])
    base_room   = to_num(room_data[3])
    gold_room   = to_num(room_data[5])

    # --- KPI SUMMARY CARDS ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric("YTD TOTAL REVENUE", f"R{actual_rev:,.0f}", f"Target Gap: R{gold_rev-actual_rev:,.0f}")
    with k2:
        st.metric("ROOM NIGHTS SOLD", f"{actual_room:,.0f}", f"Gap to Gold: {gold_room-actual_room:,.0f}")
    with k3:
        pace = (actual_rev / gold_rev) * 100 if gold_rev > 0 else 0
        st.metric("PACE TO GOLD", f"{pace:.1f}%", "Overall Journey")

    st.markdown("---")

    # --- INTERACTIVE GAUGES ---
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Interactive Revenue Tracker")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = actual_rev,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, gold_rev * 1.1], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, base_rev], 'color': "#D6D1C4"},
                    {'range': [base_rev, silver_rev], 'color': "#E5E1D8"},
                    {'range': [silver_rev, gold_rev], 'color': "#F2EFE9"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': gold_rev}
            }
        ))
        # This adds the hover labels for the CFO
        fig_rev.update_traces(
            hoverinfo="text",
            text=f"<b>Current:</b> R{actual_rev:,.0f}<br><b>Base:</b> R{base_rev:,.0f}<br><b>Silver:</b> R{silver_rev:,.0f}<br><b>GOLD:</b> R{gold_rev:,.0f}"
        )
        fig_rev.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30), hovermode="closest")
        st.plotly_chart(fig_rev, use_container_width=True)

    with g2:
        st.subheader("Room Nights Performance")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = actual_room,
            number = {'valueformat': ',.0f', 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [None, gold_room * 1.1]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, base_room], 'color': "#D6D1C4"},
                    {'range': [base_room, gold_room], 'color': "#E5E1D8"}
                ]
            }
        ))
        fig_room.update_traces(
            hoverinfo="text",
            text=f"<b>Actual:</b> {actual_room}<br><b>Base:</b> {base_room}<br><b>Gold:</b> {gold_room}"
        )
        fig_room.update_layout(height=400, margin=dict(t=50, b=20, l=30, r=30))
        st.plotly_chart(fig_room, use_container_width=True)

    # --- THE DATA EXPLORER ---
    with st.expander("📂 Explore Full Master Data Grid"):
        st.dataframe(raw_df.fillna(""), use_container_width=True)

    st.markdown("<center>🐆 <b>Mdluli Intelligence System Active</b> | No Manual Work Required</center>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Search Logic Error: {e}")
    st.info("Ensure the Master Sheet tab is named correctly and the 'Total Revenue' text exists.")
