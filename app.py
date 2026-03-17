import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mdluli Leopard Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F6F2; }
    h1 { color: #C5A059; font-family: 'serif'; text-align: center; font-size: 45px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐆 Mdluli Safari Lodge Executive Pulse")

# --- DATA CONNECTION ---
sheet_id = "1FomdHZww0k2pWMS1cTzDJUss8NpAOnsaZkRXyvGjUYM"
# We'll use a more direct CSV export link
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

@st.cache_data(ttl=5) 
def load_data():
    df = pd.read_csv(url)
    # Clean headers and data
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # Helper to turn "R15,000" into 15000
    def clean_num(val):
        if isinstance(val, str):
            return float(val.replace('R', '').replace(',', '').replace(' ', '').strip())
        return float(val)

    # Grabbing data by column order to avoid naming issues
    # Row 1 (Total Revenue)
    rev_actual = clean_num(df.iloc[0, 4])
    rev_base   = clean_num(df.iloc[0, 1])
    rev_silver = clean_num(df.iloc[0, 2])
    rev_gold   = clean_num(df.iloc[0, 3])

    # Row 2 (Room Nights)
    room_actual = clean_num(df.iloc[1, 4])
    room_base   = clean_num(df.iloc[1, 1])
    room_gold   = clean_num(df.iloc[1, 3])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Revenue")
        fig_rev = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rev_actual,
            number = {'prefix': "R", 'font': {'color': '#2C2C2C'}},
            gauge = {
                'axis': {'range': [None, rev_gold]},
                'bar': {'color': "#C5A059"},
                'steps': [
                    {'range': [0, rev_base], 'color': "#D6D1C4"},
                    {'range': [rev_base, rev_silver], 'color': "#E5E1D8"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': rev_gold}
            }
        ))
        st.plotly_chart(fig_rev, use_container_width=True)

    with col2:
        st.subheader("Room Nights")
        fig_room = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = room_actual,
            gauge = {
                'axis': {'range': [None, room_gold]},
                'bar': {'color': "#4A5D4E"},
                'steps': [{'range': [0, room_base], 'color': "#D6D1C4"}]
            }
        ))
        st.plotly_chart(fig_room, use_container_width=True)

    st.success("🐆 Leopard Link Active")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("I am seeing the sheet, but the data format inside is unexpected. Please check Row 2 and 3 of your sheet.")
