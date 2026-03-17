import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Executive Suite", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 42px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #C5A059; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Executive Suite</h1>", unsafe_allow_html=True)

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
    
    # Define the financial year months aligning with your sheet columns (1 to 12)
    months = ["March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February"]
    
    # --- EXECUTIVE UI: TIMEFRAME SELECTOR ---
    st.markdown("### 📅 Select Reporting Period")
    selected_period = st.selectbox("View Performance For:", ["Year-to-Date (YTD)"] + months)
    
    # --- CORE DATA EXTRACTION ---
    # Rows based on your matrix: 3=Room Target, 4=Room Actual, 6=Rev Target, 7=Rev Actual
    
    if selected_period == "Year-to-Date (YTD)":
        # Sum all 12 months for YTD
        room_target = sum([to_num(df.iloc[3, i]) for i in range(1, 13)])
        room_actual = sum([to_num(df.iloc[4, i]) for i in range(1, 13)])
        rev_target = sum([to_num(df.iloc[6, i]) for i in range(1, 13)])
        rev_actual = sum([to_num(df.iloc[7, i]) for i in range(1, 13)])
        period_label = "YTD"
    else:
        # Get data for the specific selected month
        col_idx = months.index(selected_period) + 1
        room_target = to_num(df.iloc[3, col_idx])
        room_actual = to_num(df.iloc[4, col_idx])
        rev_target = to_num(df.iloc[6, col_idx])
        rev_actual = to_num(df.iloc[7, col_idx])
        period_label = selected_period

    # --- MILESTONE LOGIC ---
    # Since your matrix only has one target line, we mathematically create the executive tiers.
    # Base = 100% of Sheet Target | Silver = 110% | Gold = 120%
    base_rev = rev_target if rev_target > 0 else 1000000 # Fallback so gauge doesn't break
    silver_rev = base_rev * 1.10
    gold_rev = base_rev * 1.20

    base_room = room_target if room_target > 0 else 500
    silver_room = base_room * 1.10
    gold_room = base_room * 1.20

    # --- KPI SUMMARY CARDS ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric(
            f"{period_label} REVENUE", 
            f"R{rev_actual:,.0f}", 
            f"Variance to Base: R{rev_actual - base_rev:,.0f}",
            help=f"Actual: R{rev_actual:,.0f} | Base Target: R{base_rev:,.0f}"
        )
    with k2:
        st.metric(
            f"{period_label} ROOM NIGHTS", 
            f"{room_actual:,.0f}", 
            f"Variance to Base: {room_actual - base_room:,.0f}",
            help=f"Actual: {room_actual:,.0f} | Base Target: {base_room:,.0f}"
        )
    with k3:
        pace = (rev_actual / base_rev) * 100 
        st.metric(f"{period_label} PACE TO TARGET", f"{pace:.1f}%")

    # --- INTERACTIVE GAUGES (WITH HOVER RESTORED) ---
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader(f"Revenue Pulse: {period_label}")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_actual,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'size': 35}},
            gauge = {
                'axis': {'range': [None, gold_rev * 1.05], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, base_rev], 'color': "#D6D1C4"},
                    {'range': [base_rev, silver_rev], 'color': "#E5E1D8"},
                    {'range': [silver_rev, gold_rev], 'color': "#F2EFE9"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': base_rev}
            }
        ))
        # Restored Hover Data
        fig_rev.update_traces(
            hoverinfo="text", 
            text=f"<b>Current:</b> R{rev_actual:,.0f}<br><b>Base (Target):</b> R{base_rev:,.0f}<br><b>Silver (110%):</b> R{silver_rev:,.0f}<br><b>Gold (120%):</b> R{gold_rev:,.0f}"
        )
        fig_rev.update_layout(height=350, margin=dict(t=30, b=20, l=30, r=30), hovermode="closest")
        st.plotly_chart(fig_rev, use_container_width=True)

    with g2:
        st.subheader(f"Room Nights Pulse: {period_label}")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = room_actual,
            number = {'valueformat': ',.0f', 'font': {'size': 35}},
            gauge = {
                'axis': {'range': [None, gold_room * 1.05]},
                'bar': {'color': "#4A5D4E"},
                'steps': [
                    {'range': [0, base_room], 'color': "#D6D1C4"},
                    {'range': [base_room, silver_room], 'color': "#E5E1D8"},
                    {'range': [silver_room, gold_room], 'color': "#F2EFE9"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': base_room}
            }
        ))
        # Restored Hover Data
        fig_room.update_traces(
            hoverinfo="text", 
            text=f"<b>Current:</b> {room_actual:,.0f}<br><b>Base (Target):</b> {base_room:,.0f}<br><b>Silver (110%):</b> {silver_room:,.0f}<br><b>Gold (120%):</b> {gold_room:,.0f}"
        )
        fig_room.update_layout(height=350, margin=dict(t=30, b=20, l=30, r=30), hovermode="closest")
        st.plotly_chart(fig_room, use_container_width=True)

    # --- THE C-SUITE TREND CHART ---
    st.markdown("---")
    st.subheader("📈 Annual Revenue Curve (Seasonality & OTB)")
    
    # Extract all 12 months of data for the chart
    monthly_targets = [to_num(df.iloc[6, i]) for i in range(1, 13)]
    monthly_actuals = [to_num(df.iloc[7, i]) for i in range(1, 13)]
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(x=months, y=monthly_actuals, name='Actual / On-The-Books', marker_color='#C5A059'))
    fig_trend.add_trace(go.Scatter(x=months, y=monthly_targets, name='Base Target', line=dict(color='black', width=3, dash='dot')))
    
    fig_trend.update_layout(
        plot_bgcolor='white',
        yaxis=dict(title='Revenue (ZAR)', tickformat='R,.0s'),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

except Exception as e:
    st.error(f"Executive Data Sync Error: {e}")
