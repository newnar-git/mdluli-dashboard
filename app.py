import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Commercial Insight", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 42px; margin-bottom: 0; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #2C2C2C; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🐆 Mdluli Safari Lodge | Commercial Insights</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>FY 26/27 Channel & Business Mix Analysis</p>", unsafe_allow_html=True)

# --- DATA CONNECTION ---
MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
GID_CURRENT = "1602025819" # FY 26/27 Tab

@st.cache_data(ttl=30)
def load_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={GID_CURRENT}"
    return pd.read_csv(url, header=None) 

def to_num(val):
    try:
        if pd.isna(val) or val == 'None': return 0.0
        clean = str(val).replace('R', '').replace(',', '').replace('%', '').replace(' ', '').strip()
        return float(clean)
    except:
        return 0.0

try:
    df = load_sheet()
    months = ["March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February"]
    
    # --- EXECUTIVE UI: FILTER ---
    st.markdown("### 📅 Select Reporting Period")
    selected_period = st.selectbox("Analyze Performance For:", ["Year-to-Date (YTD)"] + months)
    
    # --- EXACT MATRIX MAPPING ---
    # STAY ROWS: 0=Domestic Web, 1=Enquiry, 2=Intl Web, 3=OTA, 4=Total Rooms
    # BOOKED ROWS: 6=Domestic, 7=Enquiry, 8=Intl, 9=OTA, 10=Total Booked
    # ADR: Row 5

    def extract_data(row_idx, period):
        if period == "Year-to-Date (YTD)":
            return sum([to_num(df.iloc[row_idx, i]) for i in range(1, 13)])
        else:
            col_idx = months.index(period) + 1
            return to_num(df.iloc[row_idx, col_idx])

    # Extract Totals
    total_stay = extract_data(4, selected_period)
    total_booked = extract_data(10, selected_period)
    
    # For ADR, we don't sum YTD directly, we average it or calculate from totals
    if selected_period == "Year-to-Date (YTD)":
        adr = total_booked / total_stay if total_stay > 0 else 0
    else:
        adr = extract_data(5, selected_period)

    # Extract STAY Channels
    stay_dom = extract_data(0, selected_period)
    stay_enq = extract_data(1, selected_period)
    stay_intl = extract_data(2, selected_period)
    stay_ota = extract_data(3, selected_period)

    # Extract BOOKED Channels
    booked_dom = extract_data(6, selected_period)
    booked_enq = extract_data(7, selected_period)
    booked_intl = extract_data(8, selected_period)
    booked_ota = extract_data(9, selected_period)

    # --- TOP LINE: KPI METRICS ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.metric(f"{selected_period} TOTAL REVENUE", f"R{total_booked:,.0f}")
    with k2:
        st.metric(f"{selected_period} ROOM NIGHTS", f"{total_stay:,.0f}")
    with k3:
        st.metric(f"{selected_period} ADR (Avg Daily Rate)", f"R{adr:,.0f}")

    # --- MIDDLE ROW: THE BUSINESS MIX (DONUT CHARTS) ---
    st.markdown("### 📊 Channel Mix Breakdown")
    c1, c2 = st.columns(2)
    
    # Custom colors for the lodge brand
    colors = ['#4A5D4E', '#C5A059', '#2C2C2C', '#D6D1C4'] 

    with c1:
        st.subheader("Revenue by Channel")
        rev_labels = ['Domestic', 'Enquiries', 'International', 'OTA']
        rev_values = [booked_dom, booked_enq, booked_intl, booked_ota]
        
        fig_rev_pie = go.Figure(data=[go.Pie(labels=rev_labels, values=rev_values, hole=.4, marker_colors=colors)])
        fig_rev_pie.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+value+percent')
        fig_rev_pie.update_layout(height=400, margin=dict(t=30, b=30, l=0, r=0), showlegend=False)
        st.plotly_chart(fig_rev_pie, use_container_width=True)

    with c2:
        st.subheader("Room Nights by Channel")
        stay_labels = ['Domestic Web', 'Enquiries', 'Intl Web', 'OTA']
        stay_values = [stay_dom, stay_enq, stay_intl, stay_ota]
        
        fig_stay_pie = go.Figure(data=[go.Pie(labels=stay_labels, values=stay_values, hole=.4, marker_colors=colors)])
        fig_stay_pie.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+value+percent')
        fig_stay_pie.update_layout(height=400, margin=dict(t=30, b=30, l=0, r=0), showlegend=False)
        st.plotly_chart(fig_stay_pie, use_container_width=True)

    # --- BOTTOM ROW: THE DATA TABLE ---
    st.markdown("---")
    with st.expander("📂 View Detailed Channel Data"):
        st.write("Live feed from FY 26/27 Spreadsheet")
        channel_df = pd.DataFrame({
            "Channel": ["Domestic", "Enquiries", "International", "OTA"],
            "Revenue (ZAR)": [f"R{booked_dom:,.0f}", f"R{booked_enq:,.0f}", f"R{booked_intl:,.0f}", f"R{booked_ota:,.0f}"],
            "Room Nights": [f"{stay_dom:,.0f}", f"{stay_enq:,.0f}", f"{stay_intl:,.0f}", f"{stay_ota:,.0f}"]
        })
        st.dataframe(channel_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Mapping Error: {e}")
    st.info("Ensure the rows in your Google Sheet match the expected matrix layout.")
