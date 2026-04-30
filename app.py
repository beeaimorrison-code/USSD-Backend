import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --- UI CUSTOMIZATION (Maroon & White) ---
st.set_page_config(page_title="Security Intelligence Backend", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p { color: #800000 !important; }
    [data-testid="stSidebar"] { background-color: #800000; }
    [data-testid="stSidebar"] * { color: white !important; }
    div.stButton > button:first-child {
        background-color: #800000;
        color: white;
        border: 2px solid white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LANDMARK DATABASE ---
LANDMARKS = {
    "Sector A-1 (Market)": [6.5244, 3.3792],
    "Sector B-4 (Power Plant)": [6.4550, 3.3841],
    "Sector C-2 (Transport Hub)": [6.5000, 3.3670]
}

if 'reports' not in st.session_state:
    st.session_state.reports = pd.DataFrame(columns=["Location", "Type", "Weight", "Time"])

# --- SIDEBAR: USSD INPUT ---
st.sidebar.title("📡 USSD Input")
with st.sidebar.form("ussd_report"):
    loc = st.selectbox("Select Landmark", list(LANDMARKS.keys()))
    danger = st.selectbox("Threat Type", ["Suspicious Activity", "Vandalism", "Armed Conflict"])
    weight = {"Suspicious Activity": 1.2, "Vandalism": 2.5, "Armed Conflict": 5.0}[danger]
    
    if st.form_submit_button("Send Report"):
        new_data = {"Location": loc, "Type": danger, "Weight": weight, "Time": datetime.now().strftime("%H:%M")}
        st.session_state.reports = pd.concat([st.session_state.reports, pd.DataFrame([new_data])], ignore_index=True)

# --- MAIN DASHBOARD ---
st.title("🛡️ Security Personnel Command Center")
st.write("---")

if not st.session_state.reports.empty:
    summary = st.session_state.reports.groupby("Location").agg(
        Count=('Type', 'count'),
        Intensity=('Weight', 'sum')
    ).reset_index()

    m1, m2 = st.columns(2)
    m1.metric("Active Reports", len(st.session_state.reports))
    m2.metric("Critical Zones", len(summary[summary['Intensity'] > 10]))

    summary['lat'] = summary['Location'].map(lambda x: LANDMARKS[x][0])
    summary['lon'] = summary['Location'].map(lambda x: LANDMARKS[x][1])

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(latitude=6.5244, longitude=3.3792, zoom=10, pitch=45),
        layers=[
            pdk.Layer(
                'ColumnLayer',
                data=summary,
                get_position='[lon, lat]',
                get_elevation='Intensity * 100',
                elevation_scale=10,
                radius=300,
                get_fill_color='[128, 0, 0, 200]',
                pickable=True,
            ),
        ],
    ))
    st.table(st.session_state.reports.tail(5))
else:
    st.info("Awaiting incoming USSD data signals...")
