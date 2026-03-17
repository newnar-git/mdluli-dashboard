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
st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>Live Year-on-Year (YoY) Intelligence</p>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
GID_CURRENT = "2009161338" # FY 25/26
GID_PREVIOUS = "0"         # FY 24/25

@st.cache_data(ttl=30)
def load_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url, header=None) 

def to_num(val):
    try:
        if pd.isna(val) or val == 'None': return 0.0
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    # Load both years
    df_curr = load_sheet(GID_CURRENT)
    df_prev = load_sheet(GID_PREVIOUS)
    
    months = ["March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February"]
    
    # --- EXECUTIVE UI: TIMEFRAME SELECTOR ---
    st.markdown("### 📅 Select Reporting Period")
    selected_period = st.selectbox("Analyze Performance For:", ["Year-to-Date (YTD)"] + months)
    
    # --- DATA EXTRACTION (CURRENT YEAR) ---
    if selected_period == "Year-to-Date (YTD)":
        curr_room_tgt = sum([to_num(df_curr.iloc[3, i]) for i in range(1, 13)])
        curr_room_act = sum([to_num(df_curr.iloc[4, i]) for i in range(1, 13)])
        curr_rev_tgt = sum([to_num(df_curr.iloc[6, i]) for i in range(1, 13)])
        curr_rev_act = sum([to_num(df_curr.iloc[7, i]) for i in range(1, 13)])
        
        prev_room_act = sum([to_num(df_prev.iloc[4, i]) for i in range(1, 13)])
        prev_rev_act = sum([to_num(df_prev.iloc[7, i]) for i in range(1, 13)])
        period_label = "YTD"
    else:
        col_idx = months.index(selected_period) + 1
        curr_room_tgt = to_num(df_curr.iloc[3, col_idx])
        curr_room_act = to_num(df_curr.iloc[4, col_idx])
        curr_rev_tgt = to_num(df_curr.iloc[6, col_idx])
        curr_rev_act = to_num(df_curr.iloc[7, col_idx])
        
        prev_room_act = to_num(df_prev.iloc[4, col_idx])
        prev_rev_act = to_num(df_prev.iloc[7, col_idx])
        period_label = selected_period

    # --- MATH & VARIANCES ---
    base_rev = curr_rev_tgt if curr_rev_tgt > 0 else 1000000 
    base_room = curr_room_tgt if curr_room_tgt > 0 else 500

    # YoY Calculations
    yoy_rev_growth = ((curr_rev_act / prev_rev_act) - 1) * 100 if prev_rev_act > 0 else 0
    yoy_room_growth = ((curr_room_act / prev_room_act) - 1) * 100 if prev_room_act > 0 else 0

    # --- KPI SUMMARY CARDS ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric(
            f"{period_label} REVENUE (FY25/26)", 
            f"R{curr_rev_act:,.0f}", 
            delta=f"{yoy_rev_growth:+.1f}% vs Last Year",
            help=f"Target: R{base_rev:,.0f} | Last Year: R{prev_rev_act:,.0f}"
        )
    with k2:
        st.metric(
            f"{period_label} ROOM NIGHTS (FY25/26)", 
            f"{curr_room_act:,.0f}", 
            delta=f"{yoy_room_growth:+.1f}% vs Last Year",
            help=f"Target: {base_room:,.0f} | Last Year: {prev_room_act:,.0f}"
        )
    with k3:
        pace = (curr_rev_act / base_rev) * 100 if base_rev > 0 else 0
        st.metric(f"{period_label} REVENUE PACE TO TARGET", f"{pace:.1f}%")

    # --- PACING GAUGES ---
    st.markdown("### 🎯 Current Year Target Pacing")
    g1, g2 = st.columns(2)
    
    with g1:
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = curr_rev_act,
            number = {'prefix': "R", 'valueformat': ',.0f', 'font': {'size': 35}},
            gauge = {
                'axis': {'range': [None, max(base_rev * 1.2, curr_rev_act * 1.1)], 'tickformat': '.2s'},
                'bar': {'color': "#C5A059"},
                'steps': [{'range': [0, base_rev], 'color': "#D6D1C4"}],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': base_rev}
            }
        ))
        fig_rev.update_layout(height=300, margin=dict(t=30, b=20, l=30, r=30))
        st.plotly_chart(fig_rev, use_container_width=True)

    with g2:
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = curr_room_act,
            number = {'valueformat': ',.0f', 'font': {'size': 35}},
            gauge = {
                'axis': {'range': [None, max(base_room * 1.2, curr_room_act * 1.1)]},
                'bar': {'color': "#4A5D4E"},
                'steps': [{'range': [0, base_room], 'color': "#D6D1C4"}],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': base_room}
            }
        ))
        fig_room.update_layout(height=300, margin=dict(t=30, b=20, l=30, r=30))
        st.plotly_chart(fig_room, use_container_width=True)

    # --- INTERACTIVE YOY CHARTS ---
    st.markdown("---")
    st.markdown("### 📊 Year-on-Year Trend Analysis")
    
    # Interactive Toggle
    chart_view = st.radio("Select Metric to Compare:", ["Total Revenue", "Room Nights Sold"], horizontal=True)
    
    fig_yoy = go.Figure()

    if chart_view == "Total Revenue":
        curr_vals = [to_num(df_curr.iloc[7, i]) for i in range(1, 13)]
        prev_vals = [to_num(df_prev.iloc[7, i]) for i in range(1, 13)]
        tgt_vals = [to_num(df_curr.iloc[6, i]) for i in range(1, 13)]
        
        fig_yoy.add_trace(go.Bar(x=months, y=prev_vals, name='FY 24/25 Actual', marker_color='#E5E1D8'))
        fig_yoy.add_trace(go.Bar(x=months, y=curr_vals, name='FY 25/26 Actual (OTB)', marker_color='#C5A059'))
        fig_yoy.add_trace(go.Scatter(x=months, y=tgt_vals, name='FY 25/26 Target', line=dict(color='black', width=3, dash='dot')))
        y_title = 'Revenue (ZAR)'
        tick_fmt = 'R,.0s'
        
    else:
        curr_vals = [to_num(df_curr.iloc[4, i]) for i in range(1, 13)]
        prev_vals = [to_num(df_prev.iloc[4, i]) for i in range(1, 13)]
        tgt_vals = [to_num(df_curr.iloc[3, i]) for i in range(1, 13)]
        
        fig_yoy.add_trace(go.Bar(x=months, y=prev_vals, name='FY 24/25 Actual', marker_color='#D6D1C4'))
        fig_yoy.add_trace(go.Bar(x=months, y=curr_vals, name='FY 25/26 Actual (OTB)', marker_color='#4A5D4E'))
        fig_yoy.add_trace(go.Scatter(x=months, y=tgt_vals, name='FY 25/26 Target', line=dict(color='black', width=3, dash='dot')))
        y_title = 'Room Nights'
        tick_fmt = ',.0f'

    fig_yoy.update_layout(
        barmode='group',
        plot_bgcolor='white',
        yaxis=dict(title=y_title, tickformat=tick_fmt),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

except Exception as e:
    st.error(f"Dual-Sync Error: Please ensure both sheets share the exact same row structure. Detail: {e}")
