import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli CFO Command", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 38px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #2C2C2C; }
    .channel-box { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Comprehensive Executive Command</h1>", unsafe_allow_html=True)

# --- DATA CONNECTION (TRIPLE SYNC) ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
YEAR_MAP = {
    "FY 26/27 (Current)": "1602025819",
    "FY 25/26 (Previous)": "2009161338",
    "FY 24/25 (Historical)": "0"
}

@st.cache_data(ttl=30)
def load_all_sheets():
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
    df_curr = data[selected_year]

    # Dynamic Historical Routing
    if "26/27" in selected_year:
        prev_year_label = "FY 25/26"
        df_prev = data["FY 25/26 (Previous)"]
    elif "25/26" in selected_year:
        prev_year_label = "FY 24/25"
        df_prev = data["FY 24/25 (Historical)"]
    else:
        prev_year_label = "N/A"
        df_prev = None 

    # --- DATA EXTRACTION LOGIC ---
    def get_val(df, row_idx, is_ytd):
        if df is None: return 0
        if is_ytd:
            return sum([to_num(df.iloc[row_idx, i]) for i in range(1, 13)])
        else:
            col_idx = months.index(calc_period) + 1
            return to_num(df.iloc[row_idx, col_idx])

    is_ytd = (calc_period == "Year-to-Date (YTD)")
    
    # Core Financials (Based on your diagnostic layout)
    curr_room_tgt = get_val(df_curr, 3, is_ytd)
    curr_room_act = get_val(df_curr, 4, is_ytd)
    curr_rev_tgt  = get_val(df_curr, 6, is_ytd)
    curr_rev_act  = get_val(df_curr, 7, is_ytd)
    
    prev_room_act = get_val(df_prev, 4, is_ytd)
    prev_rev_act  = get_val(df_prev, 7, is_ytd)

    # Granular Channels (Based on your list)
    stay_dom  = get_val(df_curr, 0, is_ytd)
    stay_enq  = get_val(df_curr, 1, is_ytd)
    stay_intl = get_val(df_curr, 2, is_ytd)
    stay_ota  = get_val(df_curr, 3, is_ytd)

    adr_val     = get_val(df_curr, 5, is_ytd) if not is_ytd else (curr_rev_act / curr_room_act if curr_room_act > 0 else 0)
    
    book_dom  = get_val(df_curr, 6, is_ytd)
    book_enq  = get_val(df_curr, 7, is_ytd)
    book_intl = get_val(df_curr, 8, is_ytd)
    book_ota  = get_val(df_curr, 9, is_ytd)

    # --- TOP LINE: EXECUTIVE SUMMARY (YoY & vs Target) ---
    st.markdown("---")
    st.markdown(f"### 📈 {calc_period} Performance Summary")
    
    yoy_rev_growth = ((curr_rev_act / prev_rev_act) - 1) * 100 if prev_rev_act > 0 else 0
    yoy_room_growth = ((curr_room_act / prev_room_act) - 1) * 100 if prev_room_act > 0 else 0
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Revenue", f"R{curr_rev_act:,.0f}", f"{yoy_rev_growth:+.1f}% vs {prev_year_label}")
        st.caption(f"Target: R{curr_rev_tgt:,.0f} | Variance: R{curr_rev_act - curr_rev_tgt:,.0f}")
    with k2:
        st.metric("Room Nights", f"{curr_room_act:,.0f}", f"{yoy_room_growth:+.1f}% vs {prev_year_label}")
        st.caption(f"Target: {curr_room_tgt:,.0f} | Variance: {curr_room_act - curr_room_tgt:,.0f}")
    with k3:
        st.metric("ADR (Avg Daily Rate)", f"R{adr_val:,.0f}")
    with k4:
        pace = (curr_rev_act / curr_rev_tgt) * 100 if curr_rev_tgt > 0 else 0
        st.metric("Revenue Pace to Target", f"{pace:.1f}%")

    # --- THE BUSINESS MIX (CHANNEL INFO-GRID) ---
    st.markdown("---")
    st.markdown(f"### 🏨 {calc_period} Business & Channel Mix")
    st.write("Granular breakdown of Booked Revenue and Stay Nights by source.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**BOOKED REVENUE CHANNELS (ZAR)**")
        st.markdown(f"""
        <div class='channel-box'>
            <table style="width:100%; text-align:left;">
                <tr><th>Channel</th><th style="text-align:right;">Revenue Generated</th></tr>
                <tr><td>🇿🇦 Domestic</td><td style="text-align:right; font-weight:bold; color:#C5A059;">R{book_dom:,.0f}</td></tr>
                <tr><td>✉️ Enquiry Total</td><td style="text-align:right; font-weight:bold; color:#C5A059;">R{book_enq:,.0f}</td></tr>
                <tr><td>🌍 International</td><td style="text-align:right; font-weight:bold; color:#C5A059;">R{book_intl:,.0f}</td></tr>
                <tr><td>💻 OTA</td><td style="text-align:right; font-weight:bold; color:#C5A059;">R{book_ota:,.0f}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("**STAY CHANNELS (ROOM NIGHTS)**")
        st.markdown(f"""
        <div class='channel-box'>
            <table style="width:100%; text-align:left;">
                <tr><th>Channel</th><th style="text-align:right;">Nights Sold</th></tr>
                <tr><td>🇿🇦 Domestic Website</td><td style="text-align:right; font-weight:bold; color:#4A5D4E;">{stay_dom:,.0f}</td></tr>
                <tr><td>✉️ Enquiry Total</td><td style="text-align:right; font-weight:bold; color:#4A5D4E;">{stay_enq:,.0f}</td></tr>
                <tr><td>🌍 Intl Website</td><td style="text-align:right; font-weight:bold; color:#4A5D4E;">{stay_intl:,.0f}</td></tr>
                <tr><td>💻 OTA</td><td style="text-align:right; font-weight:bold; color:#4A5D4E;">{stay_ota:,.0f}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # --- BOTTOM ROW: 3-YEAR MULTI-CHART ---
    st.markdown("---")
    st.markdown("### 📊 Multi-Year Annual Trend & Pacing Comparison")
    
    chart_view = st.radio("Select Historical View:", ["Revenue (ZAR)", "Room Nights"], horizontal=True)
    fig_yoy = go.Figure()

    def get_12_months(df, row_idx):
        if df is None: return [0]*12
        try: return [to_num(df.iloc[row_idx, i]) for i in range(1, 13)]
        except: return [0]*12

    if chart_view == "Revenue (ZAR)":
        act_24 = get_12_months(data["FY 24/25 (Historical)"], 7)
        act_25 = get_12_months(data["FY 25/26 (Previous)"], 7)
        act_26 = get_12_months(data["FY 26/27 (Current)"], 7)
        tgt_sel = get_12_months(df_curr, 6) # Target of currently selected year
        
        fig_yoy.add_trace(go.Bar(x=months, y=act_24, name='FY 24/25 Actual', marker_color='#E5E1D8'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_25, name='FY 25/26 Actual', marker_color='#D6D1C4'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_26, name='FY 26/27 Actual', marker_color='#C5A059'))
        fig_yoy.add_trace(go.Scatter(x=months, y=tgt_sel, name=f'{selected_year} Target', line=dict(color='black', width=3, dash='dot')))
        y_title, tick_fmt = 'Revenue (ZAR)', 'R,.0s'
        
    else:
        act_24 = get_12_months(data["FY 24/25 (Historical)"], 4)
        act_25 = get_12_months(data["FY 25/26 (Previous)"], 4)
        act_26 = get_12_months(data["FY 26/27 (Current)"], 4)
        tgt_sel = get_12_months(df_curr, 3) 
        
        fig_yoy.add_trace(go.Bar(x=months, y=act_24, name='FY 24/25 Actual', marker_color='#E5E1D8'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_25, name='FY 25/26 Actual', marker_color='#D6D1C4'))
        fig_yoy.add_trace(go.Bar(x=months, y=act_26, name='FY 26/27 Actual', marker_color='#4A5D4E'))
        fig_yoy.add_trace(go.Scatter(x=months, y=tgt_sel, name=f'{selected_year} Target', line=dict(color='black', width=3, dash='dot')))
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
    st.error(f"Engine Error: Make sure your Google Sheet rows perfectly match the extraction logic. Detail: {e}")
