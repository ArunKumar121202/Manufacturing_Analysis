import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottles Analysis Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    demand = pd.read_csv("Demand.csv", parse_dates=["Date"])
    port = pd.read_csv("Port.csv")
    raw_material = pd.read_csv("RawMaterial Prices.csv", parse_dates=["Date"])
    return demand, port, raw_material

demand_data, port_data, raw_material_data = load_data()

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
section = st.sidebar.radio(
    "Go to",
    ("Demand Analysis", "Port Activity", "Raw Material Prices", "Integrated Trends")
)

# Title and description
st.title("📦 PET Bottle Market Dashboard")
st.markdown("Insights from demand, logistics, and raw material pricing data.")
st.markdown("---")

# ---------------------- 1. DEMAND ANALYSIS ----------------------
if section == "Demand Analysis":
    st.header("📈 Demand Analysis")

    st.subheader("🔹 Key Demand KPIs")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Records", demand_data.shape[0])
    with col2:
        st.metric("Regions", demand_data['Region'].nunique())

    st.subheader("🔸 Demand Over Time")
    fig_demand_time = px.line(
        demand_data, x="Date", y="Volume (Million Pieces)", color="Region",
        title="Demand Over Time by Region"
    )
    st.plotly_chart(fig_demand_time, use_container_width=True)

    st.subheader("🔸 Region-Wise Demand Distribution")
    demand_summary = demand_data.groupby("Region")["Volume (Million Pieces)"].sum().reset_index()
    fig_region_demand = px.bar(
        demand_summary, x="Region", y="Volume (Million Pieces)", text_auto=True,
        color="Region", title="Cumulative Demand by Region"
    )
    st.plotly_chart(fig_region_demand, use_container_width=True)

# ---------------------- 2. PORT ACTIVITY ----------------------
elif section == "Port Activity":
    st.header("🚢 Port Activity Analysis")

    st.subheader("🔹 Key Port KPIs")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Port Entries", port_data.shape[0])
    with col2:
        st.metric("Unique Ports", port_data['Region'].nunique())

    st.subheader("🔸 Port Volume Over Time")
    fig_port_time = px.line(
        port_data, x="Date", y="Port Volume (MT)", color="Region",
        title="Port Volume Over Time by Region"
    )
    st.plotly_chart(fig_port_time, use_container_width=True)

    st.subheader("🔸 Region-Wise Port Activity")
    port_summary = port_data.groupby("Region")["Port Volume (MT)"].sum().reset_index()
    fig_port_summary = px.bar(
        port_summary, x="Region", y="Port Volume (MT)", text_auto=True,
        color="Region", title="Total Port Volume by Region"
    )
    st.plotly_chart(fig_port_summary, use_container_width=True)

# ---------------------- 3. RAW MATERIAL PRICES ----------------------
elif section == "Raw Material Prices":
    st.header("🛢️ Raw Material Prices")

    st.subheader("🔹 Key Price KPIs")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Records", raw_material_data.shape[0])
    with col2:
        st.metric("Materials", raw_material_data['Material'].nunique())

    st.subheader("🔸 Price Trend Over Time")
    fig_price_trend = px.line(
        raw_material_data, x="Date", y="Price", color="Material",
        title="Raw Material Prices Over Time"
    )
    st.plotly_chart(fig_price_trend, use_container_width=True)

    st.subheader("🔸 Material-Wise Price Comparison")
    latest_prices = raw_material_data.sort_values("Date").groupby("Material").tail(1)
    fig_latest_prices = px.bar(
        latest_prices, x="Material", y="Price", text_auto=True,
        title="Latest Recorded Prices by Material", color="Material"
    )
    st.plotly_chart(fig_latest_prices, use_container_width=True)

# ---------------------- 4. INTEGRATED TRENDS ----------------------
elif section == "Integrated Trends":
    st.header("📊 Integrated Trend Analysis")

    st.subheader("🔸 Demand vs Port Volume (Merged)")

    merged = pd.merge(demand_data, port_data, on=["Date", "Region"], how="inner")
    fig_demand_vs_port = px.scatter(
        merged, x="Volume (Million Pieces)", y="Port Volume (MT)", color="Region",
        title="Demand vs Port Volume by Region", opacity=0.6
    )
    st.plotly_chart(fig_demand_vs_port, use_container_width=True)

    st.subheader("🔸 Demand & Price Time Series")
    fig_demand_price = px.line(
        raw_material_data, x="Date", y="Price", color="Material",
        title="Raw Material Prices Over Time"
    )
    fig_demand_price.add_traces(
        list(px.line(demand_data, x="Date", y="Volume (Million Pieces)", color="Region").data)
    )
    st.plotly_chart(fig_demand_price, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Crafted with 💡 using Streamlit and Plotly")

