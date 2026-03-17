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
    th { color: #666; font-size: 14px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    td { padding: 8px 0; border-bottom: 1px solid #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Executive Command</h1>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
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
        try: sheets[year] = pd.read_csv(url, header=None)
        except: sheets[year] = None
    return sheets

def to_num(val):
    try:
        if pd.isna(val) or val == 'None': return 0.0
        return float(str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip())
    except: return 0.0

# --- SMART ROW FINDER ---
def smart_find(df, possible_names):
    if df is None: return None
    for name in possible_names:
        mask = df.iloc[:, 0].astype(str).str.strip().str.lower() == name.lower()
        if mask.any(): return df[mask].index[0]
    for name in possible_names:
        mask = df.iloc[:, 0].astype(str).str.contains(name, case=False, na=False)
        if mask.any(): return df[mask].index[0]
    return None

try:
    data = load_all_sheets()
    months = ["March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February"]
    
    # --- EXECUTIVE UI: GLOBAL FILTERS ---
    st.markdown("### ⚙️ Global Financial Filters")
    f1, f2 = st.columns(2)
    with f1: selected_year = st.selectbox("1. Select Financial Year:", list(YEAR_MAP.keys()))
    with f2: selected_period = st.selectbox("2. Select Reporting Period:", ["March (Month 1)", "Year-to-Date (YTD)"] + months)

    calc_period = "March" if "March (Month 1)" in selected_period else selected_period
    df_curr = data[selected_year]

    if "26/27" in selected_year:
        prev_year_label, df_prev = "FY 25/26", data["FY 25/26 (Previous)"]
    elif "25/26" in selected_year:
        prev_year_label, df_prev = "FY 24/25", data["FY 24/25 (Historical)"]
    else:
        prev_year_label, df_prev = "N/A", None 

    # --- DYNAMIC ROW MAPPING ---
    idx_room_hdr_curr = smart_find(df_curr, ["ROOM NIGHTS"])
    curr_room_tgt_idx = idx_room_hdr_curr + 1 if idx_room_hdr_curr is not None else None
    curr_room_act_idx = idx_room_hdr_curr + 2 if idx_room_hdr_curr is not None else None
    
    idx_room_hdr_prev = smart_find(df_prev, ["ROOM NIGHTS"])
    prev_room_act_idx = idx_room_hdr_prev + 2 if idx_room_hdr_prev is not None else None

    curr_rev_tgt_idx = smart_find(df_curr, ["Booked target", "Revenue Target"])
    curr_rev_act_idx = smart_find(df_curr, ["Booked total", "Total Revenue"])
    prev_rev_act_idx = smart_find(df_prev, ["Booked total", "Total Revenue"])
    adr_idx = smart_find(df_curr, ["ADR", "Average Daily Rate"])

    # Channel Metrics
    stay_names = [("DOMESTIC", ["DOMESTIC WEBSITE (STAY)", "DOMESTIC WEBSITE", "DOMESTIC (STAY)"]),
                  ("ENQUIRY", ["ENQUIRY TOTAL (STAY)", "ENQUIRY TOTAL"]),
                  ("INTL", ["INTERNATIONAL WEBSITE (STAY)", "INTERNATIONAL WEBSITE", "INTERNATIONAL (STAY)"]),
                  ("OTA", ["OTA (STAY)", "OTA"])]
    
    book_names = [("DOMESTIC", ["DOMESTIC (Booked)", "DOMESTIC"]),
                  ("ENQUIRY", ["ENQUIRY TOTAL (Booked)", "ENQUIRY TOTAL"]),
                  ("INTL", ["INTERNATIONAL (Booked)", "INTERNATIONAL"]),
                  ("OTA", ["OTA (Booked)", "OTA"])]

    # --- DATA EXTRACTION ---
    def get_val(df, row_idx, is_ytd):
        if df is None or row_idx is None: return 0
        try:
            if is_ytd: return sum([to_num(df.iloc[row_idx, i]) for i in range(1, 13)])
            else: return to_num(df.iloc[row_idx, months.index(calc_period) + 1])
        except: return 0

    is_ytd = (calc_period == "Year-to-Date (YTD)")
    
    # Core Metrics
    curr_room_tgt = get_val(df_curr, curr_room_tgt_idx, is_ytd)
    curr_room_act = get_val(df_curr, curr_room_act_idx, is_ytd)
    curr_rev_tgt  = get_val(df_curr, curr_rev_tgt_idx, is_ytd)
    curr_rev_act  = get_val(df_curr, curr_rev_act_idx, is_ytd)
    prev_room_act = get_val(df_prev, prev_room_act_idx, is_ytd)
    prev_rev_act  = get_val(df_prev, prev_rev_act_idx, is_ytd)

    adr_val = get_val(df_curr, adr_idx, is_ytd) if adr_idx is not None else (curr_rev_act / curr_room_act if curr_room_act > 0 else 0)

    # Channel Dictionaries for easy iteration
    stay_curr = {key: get_val(df_curr, smart_find(df_curr, names), is_ytd) for key, names in stay_names}
    stay_prev = {key: get_val(df_prev, smart_find(df_prev, names), is_ytd) for key, names in stay_names}
    book_curr = {key: get_val(df_curr, smart_find(df_curr, names), is_ytd) for key, names in book_names}
    book_prev = {key: get_val(df_prev, smart_find(df_prev, names), is_ytd) for key, names in book_names}

    # --- TOP LINE SUMMARY ---
    st.markdown("---")
    st.markdown(f"### 📈 Performance Summary: {calc_period} ({selected_year.split(' ')[0]})")
    
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

    # --- DYNAMIC CHANNEL GRID (YOY COMPARISON) ---
    st.markdown("---")
    st.markdown(f"### 🏨 Business & Channel Mix: {calc_period}")
    st.write("Dynamic Variance calculated against the exact period selected in the Global Filters.")

    def format_row(name, curr, prev, prefix=""):
        if prev == 0 and curr > 0: growth_html = "<span style='color:green;'>+100%</span>"
        elif prev == 0 and curr == 0: growth_html = "<span style='color:gray;'>0%</span>"
        else:
            growth = ((curr / prev) - 1) * 100
            color, sign = ("green", "+") if growth >= 0 else ("red", "")
            growth_html = f"<span style='color:{color};'>{sign}{growth:.1f}%</span>"
        
        return f"""
        <tr>
            <td>{name}</td>
            <td style="text-align:right; font-weight:bold; color:#2C2C2C;">{prefix}{curr:,.0f}</td>
            <td style="text-align:right; color:#888;">{prefix}{prev:,.0f}</td>
            <td style="text-align:right;">{growth_html}</td>
        </tr>
        """

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**BOOKED REVENUE CHANNELS (ZAR)**")
        st.markdown(f"""
        <div class='channel-box'>
            <table style="width:100%; text-align:left; border-collapse: collapse;">
                <tr><th>Channel</th><th style="text-align:right;">{selected_year[:8]} Actual</th><th style="text-align:right;">{prev_year_label} Actual</th><th style="text-align:right;">YoY Variance</th></tr>
                {format_row("🇿🇦 Domestic", book_curr["DOMESTIC"], book_prev["DOMESTIC"], "R")}
                {format_row("✉️ Enquiry Total", book_curr["ENQUIRY"], book_prev["ENQUIRY"], "R")}
                {format_row("🌍 International", book_curr["INTL"], book_prev["INTL"], "R")}
                {format_row("💻 OTA", book_curr["OTA"], book_prev["OTA"], "R")}
            </table>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("**STAY CHANNELS (ROOM NIGHTS)**")
        st.markdown(f"""
        <div class='channel-box'>
            <table style="width:100%; text-align:left; border-collapse: collapse;">
                <tr><th>Channel</th><th style="text-align:right;">{selected_year[:8]} Actual</th><th style="text-align:right;">{prev_year_label} Actual</th><th style="text-align:right;">YoY Variance</th></tr>
                {format_row("🇿🇦 Domestic", stay_curr["DOMESTIC"], stay_prev["DOMESTIC"])}
                {format_row("✉️ Enquiry Total", stay_curr["ENQUIRY"], stay_prev["ENQUIRY"])}
                {format_row("🌍 International", stay_curr["INTL"], stay_prev["INTL"])}
                {format_row("💻 OTA", stay_curr["OTA"], stay_prev["OTA"])}
            </table>
        </div>
        """, unsafe_allow_html=True)

    # --- FULLY DYNAMIC TREND CHART ---
    st.markdown("---")
    st.markdown(f"### 📊 Annual Trend Context: {selected_year[:8]} vs {prev_year_label}")
    
    chart_view = st.radio("Select Trend Metric:", ["Revenue (ZAR)", "Room Nights"], horizontal=True)
    fig_yoy = go.Figure()

    def get_12_months(df, row_idx):
        if df is None or row_idx is None: return [0]*12
        try: return [to_num(df.iloc[row_idx, i]) for i in range(1, 13)]
        except: return [0]*12

    if chart_view == "Revenue (ZAR)":
        act_curr_12 = get_12_months(df_curr, curr_rev_act_idx)
        act_prev_12 = get_12_months(df_prev, prev_rev_act_idx)
        tgt_curr_12 = get_12_months(df_curr, curr_rev_tgt_idx)
        y_title, tick_fmt = 'Revenue (ZAR)', 'R,.0s'
        color_curr = '#C5A059'
    else:
        act_curr_12 = get_12_months(df_curr, curr_room_act_idx)
        act_prev_12 = get_12_months(df_prev, prev_room_act_idx)
        tgt_curr_12 = get_12_months(df_curr, curr_room_tgt_idx)
        y_title, tick_fmt = 'Room Nights', ',.0f'
        color_curr = '#4A5D4E'

    fig_yoy.add_trace(go.Bar(x=months, y=act_prev_12, name=f'{prev_year_label} Actual', marker_color='#E5E1D8'))
    fig_yoy.add_trace(go.Bar(x=months, y=act_curr_12, name=f'{selected_year.split(" ")[0]} Actual', marker_color=color_curr))
    fig_yoy.add_trace(go.Scatter(x=months, y=tgt_curr_12, name=f'{selected_year.split(" ")[0]} Target', line=dict(color='black', width=3, dash='dot')))
    
    # Dynamic Visual Highlight based on selected period
    if not is_ytd:
        fig_yoy.add_vline(x=calc_period, line_width=2, line_dash="dash", line_color="red", annotation_text=f"Looking at: {calc_period}", annotation_position="top right")

    fig_yoy.update_layout(
        barmode='group', plot_bgcolor='white', yaxis=dict(title=y_title, tickformat=tick_fmt),
        hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

except Exception as e:
    st.error(f"Logic Sync Error: Ensure your spreadsheet rows match the names required. Detail: {e}")
