import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli CFO Command", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 42px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #2C2C2C; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | CFO Command Center</h1>", unsafe_allow_html=True)

# --- DATA CONNECTION (TRIPLE SYNC) ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
YEAR_MAP = {
    "FY 26/27 (Current)": "1602025819",
    "FY 25/26 (Previous)": "2009161338",
    "FY 24/25 (Historical)": "0"
}

@st.cache_data(ttl=30)
def load_all_sheets():
    # Downloads all 3 years into memory so filtering is instant
    sheets = {}
    for year, gid in YEAR_MAP.items():
        url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={gid}"
        try:
            sheets[year] = pd.read_csv(url, header=None)
        except:
            sheets[year] = None
    return sheets

def to_num(val):
    try:
        if pd.isna(val) or val == 'None': return 0.0
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    data = load_all_sheets()
    months = ["March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February"]
    
    # --- EXECUTIVE UI: GLOBAL FILTERS ---
    st.markdown("### ⚙️ Global Financial Filters")
    f1, f2 = st.columns(2)
    with f1:
        selected_year = st.selectbox("1. Select Financial Year:", list(YEAR_MAP.keys()))
    with f2:
        selected_period = st.selectbox("2. Select Reporting Period:", ["March (Month 1)", "Year-to-Date (YTD)"] + months)

    calc_period = "March" if "March (Month 1)" in selected_period else selected_period

    # --- DYNAMIC YEAR ROUTING ---
    df_curr = data[selected_year]
    
    # Determine the comparison year automatically
    if "26/27" in selected_year:
        prev_year_label = "FY 25/26"
        df_prev = data["FY 25/26 (Previous)"]
    elif "25/26" in selected_year:
        prev_year_label = "FY 24/25"
        df_prev = data["FY 24/25 (Historical)"]
    else:
        prev_year_label = "No Prior Data"
        df_prev = None # No 23/24 data provided

    # --- DATA EXTRACTION LOGIC ---
    if calc_period == "Year-to-Date (YTD)":
        curr_room_tgt = sum([to_num(df_curr.iloc[3, i]) for i in range(1, 13)])
        curr_room_act = sum([to_num(df_curr.iloc[4, i]) for i in range(1, 13)])
        curr_rev_tgt = sum([to_num(df_curr.iloc[6, i]) for i in range(1, 13)])
        curr_rev_act = sum([to_num(df_curr.iloc[7, i]) for i in range(1, 13)])
        
        prev_room_act = sum([to_num(df_prev.iloc[4, i]) for i in range(1, 13)]) if df_prev is not None else 0
        prev_rev_act = sum([to_num(df_prev.iloc[7, i]) for i in range(1, 13)]) if df_prev is not None else 0
        period_label = "YTD"
    else:
        col_idx = months.index(calc_period) + 1
        curr_room_tgt = to_num(df_curr.iloc[3, col_idx])
        curr_room_act = to_num(df_curr.iloc[4, col_idx])
        curr_rev_tgt = to_num(df_curr.iloc[6, col_idx])
        curr_rev_act = to_num(df_curr.iloc[7, col_idx])
        
        prev_room_act = to_num(df_prev.iloc[4, col_idx]) if df_prev is not None else 0
        prev_rev_act = to_num(df_prev.iloc[7, col_idx]) if df_prev is not None else 0
        period_label = calc_period

    # --- MILSTONE TARGETS ---
    base_rev = curr_rev_tgt if curr_rev_tgt > 0 else 100000 
    silver_rev = base_rev * 1.10
    gold_rev = base_rev * 1.20

    base_room = curr_room_tgt if curr_room_tgt > 0 else 100
    silver_room = base_room * 1.10
    gold_room = base_room * 1.20

    # YoY Calculations
    yoy_rev_variance = curr_rev_act - prev_rev_act
    yoy_rev_growth = ((curr_rev_act / prev_rev_act) - 1) * 100 if prev_rev_act > 0 else 0
    yoy_room_growth = ((curr_room_act / prev_room_act) - 1) * 100 if prev_room_act > 0 else 0

    # --- TOP LINE: KPI METRICS ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric(
            f"{period_label} REVENUE", 
            f"R{curr_rev_act:,.0f}", 
            delta=f"{yoy_rev_growth:+.1f}% (vs {prev_year_label})" if df_prev is not None else "No historical data",
            help=f"Target: R{base_rev:,.0f} | Last Year: R{prev_rev_act:,.0f}"
        )
    with k2:
        st.metric(
            f"{period_label} ROOM NIGHTS", 
            f"{curr_room_act:,.0f}", 
            delta=f"{yoy_room_growth:+.1f}% (vs {prev_year_label})" if df_prev is not None else "No historical data",
            help=f"Target: {base_room:,.0f} | Last Year: {prev_room_act:,.0f}"
        )
    with k3:
        curr_adr = curr_rev_act / curr_room_act if curr_room_act > 0 else 0
        prev_adr = prev_rev_act / prev_room_act if prev_room_act > 0 else 0
        adr_growth = ((curr_adr / prev_adr) - 1) * 100 if prev_adr > 0 else 0
        st.metric(
            f"{period_label} EST. ADR", 
            f"R{curr_adr:,.0f}", 
            f"{adr_growth:+.1f}% (vs {prev_year_label})" if df_prev is not None else "No historical data"
        )

    # --- MIDDLE ROW: INTERACTIVE PACING GAUGES ---
    st.markdown(f"### 🎯 {period_label} Budget Pacing")
    g1, g2 = st.columns(2)
    
    with g1:
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = curr_rev_act,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'size': 35}},
            gauge = {
                'axis': {'range': [None, max(gold_rev, curr_rev_act * 1.1)], 'tickformat': '.2s'},
                'bar': {'color': "#2C2C2C"},
                'steps': [
                    {'range': [0, base_rev], 'color': "#E5E1D8"},
                    {'range': [base_rev, silver_rev], 'color': "#D6D1C4"},
                    {'range': [silver_rev, gold_rev], 'color': "#C5A059"}
                ],
                'threshold': {'line': {'color': "green", 'width': 4}, 'value': base_rev}
            }
        ))
        fig_rev.update_traces(
            hoverinfo="text",
            text=f"<b>Current:</b> R{curr_rev_act:,.0f}<br><br><b>Base:</b> R{base_rev:,.0f}<br><b>Silver:</b> R{silver_rev:,.0f}<br><b>Gold:</b> R{gold_rev:,.0f}"
        )
        fig_rev.update_layout(height=350, margin=dict(t=30, b=20, l=30, r=30))
        st.plotly_chart(fig_rev, use_container_width=True)

    with g2:
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = curr_room_act,
            number = {'valueformat': ',.0f', 'font': {'size': 35}},
            gauge = {
                'axis': {'range': [None, max(gold_room, curr_room_act * 1.1)]},
                'bar': {'color': "#2C2C2C"},
                'steps': [
                    {'range': [0, base_room], 'color': "#E5E1D8"},
                    {'range': [base_room, silver_room], 'color': "#D6D1C4"},
                    {'range': [silver_room, gold_room], 'color': "#C5A059"}
                ],
                'threshold': {'line': {'color': "green", 'width': 4}, 'value': base_room}
            }
        ))
        fig_room.update_traces(
            hoverinfo="text",
            text=f"<b>Current:</b> {curr_room_act:,.0f}<br><br><b>Base:</b> {base_room:,.0f}<br><b>Silver:</b> {silver_room:,.0f}<br><b>Gold:</b> {gold_room:,.0f}"
        )
        fig_room.update_layout(height=350, margin=dict(t=30, b=20, l=30, r=30))
        st.plotly_chart(fig_room, use_container_width=True)

    # --- BOTTOM ROW: 3-YEAR MULTI-CHART ---
    st.markdown("---")
    st.markdown("### 📊 Multi-Year Annual Trend Comparison")
    
    chart_view = st.radio("Select View:", ["Revenue (ZAR)", "Room Nights"], horizontal=True)
    
    fig_yoy = go.Figure()

    # Helper function to get 12-month array safely
    def get_12_months(df, row_idx):
        if df is None: return [0]*12
        return [to_num(df.iloc[row_idx, i]) for i in range(1, 13)]

    if chart_view == "Revenue (ZAR)":
        act_24 = get_12_months(data["FY 24/25 (Historical)"], 7)
        act_25 = get_12_months(data["FY 25/26 (Previous)"], 7)
        act_26 = get_12_months(data["FY 26/27 (Current)"], 7)
        tgt_26 = get_12_months(data["FY 26/27 (Current)"], 6)
        
        fig_yoy.add_trace(go.Bar(x=months, y=act_24, name='FY 24/25 Actual', marker_color='#E5E1D8'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_25, name='FY 25/26 Actual', marker_color='#D6D1C4'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_26, name='FY 26/27 OTB', marker_color='#C5A059'))
        fig_yoy.add_trace(go.Scatter(x=months, y=tgt_26, name='FY 26/27 Target', line=dict(color='black', width=3, dash='dot')))
        y_title, tick_fmt = 'Revenue (ZAR)', 'R,.0s'
        
    else:
        act_24 = get_12_months(data["FY 24/25 (Historical)"], 4)
        act_25 = get_12_months(data["FY 25/26 (Previous)"], 4)
        act_26 = get_12_months(data["FY 26/27 (Current)"], 4)
        tgt_26 = get_12_months(data["FY 26/27 (Current)"], 3)
        
        fig_yoy.add_trace(go.Bar(x=months, y=act_24, name='FY 24/25 Actual', marker_color='#E5E1D8'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_25, name='FY 25/26 Actual', marker_color='#D6D1C4'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_26, name='FY 26/27 OTB', marker_color='#4A5D4E'))
        fig_yoy.add_trace(go.Scatter(x=months, y=tgt_26, name='FY 26/27 Target', line=dict(color='black', width=3, dash='dot')))
        y_title, tick_fmt = 'Room Nights', ',.0f'

    fig_yoy.update_layout(
        barmode='group',
        plot_bgcolor='white',
        yaxis=dict(title=y_title, tickformat=tick_fmt),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

except Exception as e:
    st.error(f"Engine Error: {e}")
