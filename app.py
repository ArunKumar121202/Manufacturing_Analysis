import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# --------- Load Data (Uncached) ---------
data = pd.read_csv("Demand.csv")  # Replace with your file path if needed

# Convert date column
data["Date"] = pd.to_datetime(data["Date_of_requirement"])
data["Month"] = data["Date"].dt.to_period("M").astype(str)

# --------- SIDEBAR Filters ---------
with st.sidebar:
    st.title("🔍 Filter Options")

    region_filter = st.multiselect(
        "Select Region(s)", options=data["Region"].unique(),
        default=data["Region"].unique()
    )

    country_filter = st.multiselect(
        "Select Country(s)", options=data["Country"].unique(),
        default=data["Country"].unique()
    )

    capacity_filter = st.multiselect(
        "Select Capacity", options=data["PET_bottle_capacity"].unique(),
        default=data["PET_bottle_capacity"].unique()
    )

    type_filter = st.multiselect(
        "Select Bottle Type", options=data["Type"].unique(),
        default=data["Type"].unique()
    )

    date_range = st.date_input(
        "Select Date Range",
        [data["Date"].min(), data["Date"].max()]
    )

    section = st.radio("📂 Navigation", ["Demand Overview", "In-Depth Analysis"])

# --------- Filter Data ---------
filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["Country"].isin(country_filter)) &
    (data["PET_bottle_capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter)) &
    (data["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# --------- Demand Overview ---------
if section == "Demand Overview":
    st.title("📦 PET Bottle Demand Overview")
    st.markdown("Explore overall demand trends across regions, capacities, and types.")
    st.markdown("---")

    # KPIs
    st.subheader("🔹 Demand KPIs")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", filtered_data.shape[0])
    col2.metric("Total Volume (Mn)", round(filtered_data["Volume_Million_Pieces"].sum(), 2))
    col3.metric("Unique Capacities", filtered_data["PET_bottle_capacity"].nunique())
    col4.metric("Unique Countries", filtered_data["Country"].nunique())

    st.markdown("---")

    # Line Chart: Demand Over Time
    st.subheader("📈 Monthly PET Bottle Demand")
    monthly = filtered_data.groupby("Month")["Volume_Million_Pieces"].sum().reset_index()
    fig_line = px.line(monthly, x="Month", y="Volume_Million_Pieces", markers=True,
                       title="Monthly Demand (in Million Pieces)")
    st.plotly_chart(fig_line, use_container_width=True)

    # Bar Chart: Region-Wise
    st.subheader("🌍 Region-wise Demand")
    region_summary = filtered_data.groupby("Region")["Volume_Million_Pieces"].sum().reset_index()
    fig_region = px.bar(region_summary, x="Region", y="Volume_Million_Pieces", color="Region",
                        title="Total Demand by Region", text_auto=True)
    st.plotly_chart(fig_region, use_container_width=True)

    # Bar Chart: Capacity-Wise
    st.subheader("🧪 Capacity-wise Demand")
    cap_summary = filtered_data.groupby("PET_bottle_capacity")["Volume_Million_Pieces"].sum().reset_index()
    fig_capacity = px.bar(cap_summary.sort_values("Volume_Million_Pieces", ascending=False),
                          x="PET_bottle_capacity", y="Volume_Million_Pieces", color="PET_bottle_capacity",
                          title="Demand by PET Bottle Capacity", text_auto=True)
    st.plotly_chart(fig_capacity, use_container_width=True)

# --------- In-Depth Analysis ---------
elif section == "In-Depth Analysis":
    st.title("📊 Detailed Analysis")
    st.markdown("---")

    # Bottle Type Analysis
    st.subheader("🧱 Demand by Bottle Type")
    type_summary = filtered_data.groupby("Type")["Volume_Million_Pieces"].sum().reset_index()
    fig_type = px.pie(type_summary, names="Type", values="Volume_Million_Pieces",
                      title="Demand Share by Bottle Type")
    st.plotly_chart(fig_type, use_container_width=True)

    # Country-Wise Demand
    st.subheader("🗺️ Country-wise Demand")
    country_summary = filtered_data.groupby("Country")["Volume_Million_Pieces"].sum().reset_index()
    fig_country = px.bar(country_summary.sort_values("Volume_Million_Pieces", ascending=False),
                         x="Country", y="Volume_Million_Pieces", color="Country",
                         title="Total Demand by Country", text_auto=True)
    st.plotly_chart(fig_country, use_container_width=True)

    # Weight vs Volume
    st.subheader("⚖️ Bottle Weight vs Volume")
    fig_scatter = px.scatter(filtered_data, x="PET_bottle_weight_grams", y="Volume_Million_Pieces",
                             color="PET_bottle_capacity", size="Volume_Million_Pieces",
                             title="Bottle Weight vs Volume", hover_data=["Country", "Type"])
    st.plotly_chart(fig_scatter, use_container_width=True)
