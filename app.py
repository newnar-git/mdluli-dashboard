import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Mdluli Leopard Dashboard", layout="wide")

st.title("🐆 Mdluli Executive Pulse")

# --- DATA CONNECTION ---
sheet_id = "1FomdHZww0k2pWMS1cTzDJUss8NpAOnsaZkRXyvGjUYM"
# Direct export link
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=0) # FORCE REFRESH - NO CACHING
def load_data():
    df = pd.read_csv(url)
    return df

try:
    df = load_data()
    
    # Show the raw data at the bottom for debugging
    st.write("### 🔍 What the Leopard sees in your sheet:")
    st.dataframe(df)

    # Simple logic to pull the numbers
    rev_actual = df.iloc[0, 4]
    rev_gold = df.iloc[0, 3]
    room_actual = df.iloc[1, 4]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Revenue", f"R{rev_actual:,.0f}")
        st.write("*(Gauge will appear once data is confirmed below)*")
    with col2:
        st.metric("Room Nights", f"{room_actual}")

except Exception as e:
    st.error(f"Error reading data: {e}")
