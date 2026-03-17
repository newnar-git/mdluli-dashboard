import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mdluli Diagnostics", layout="wide")

st.markdown("<h1>🔍 Leopard Diagnostic Mode</h1>", unsafe_allow_html=True)
st.write("We are testing exactly what Google is allowing the app to see.")

MASTER_ID = "1xtchBzmRdvP0Uir8gIIQ7MO3Tj9EgV5uc_oqdsm3FwQ"
GID = "1602025819"
url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/export?format=csv&gid={GID}"

st.info(f"**Pinging URL:** {url}")

try:
    # Attempt to load the raw data
    raw_df = pd.read_csv(url, header=None)
    
    st.success("✅ Ping successful! Here is the raw data Google handed to the app:")
    st.dataframe(raw_df, use_container_width=True)
    
    # Check if the words actually exist in what was downloaded
    found = raw_df.astype(str).str.contains("Total Revenue", case=False).any().any()
    if found:
        st.success("🎯 I CAN see the words 'Total Revenue' in this data.")
    else:
        st.error("❌ The words 'Total Revenue' DO NOT EXIST anywhere in the table above.")

except Exception as e:
    st.error(f"CRITICAL BLOCK: {e}")
    st.write("Google is completely blocking the connection.")
