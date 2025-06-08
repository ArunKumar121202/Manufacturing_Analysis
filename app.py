import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# --------- Load Data ---------
data = pd.read_csv("Demand.csv")  # Update this if needed

# Clean column names
data.columns = data.columns.str.strip()

# Convert date column
data["Date"] = pd.to_datetime(data["Date_of_requirement"])
data["Month"] = data["Date"].dt.to_period("M").astype(str)

# --------- SIDEBAR: Filters & Navigation ---------
with st.sidebar:
    st.title("🔍 Filters")

    region_filter = st.multiselect(
        "Select Region(s)", options=data["Region"].unique(),
        default=data["Region"].unique()
    )

    capacity_filter = st.multiselect(
        "Select Capacity", options=data["PET_bottle_capacity"].unique(),
        default=data["PET_bottle_capacity"].unique()
    )

    type_filter = st.multiselect(
        "Select Type", options=data["Type"].unique(),
        default=data["Type"].unique()
    )

    date_range = st.date_input(
        "Select Date Range",
        [data["Date"].min(), data["Date"].max()]
    )

    section = st.radio("📂 Navigation", ["Demand Analysis", "Other Analysis"])

# --------- Filter Data ---------
filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["PET_bottle_capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter)) &
    (data["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# --------- DEMAND ANALYSIS ---------
if section == "Demand Analysis":
    st.title("📦 PET Bottle Demand Analysis")
    st.markdown("Explore trends in PET bottle demand across regions, capacities, and types.")
    st.markdown("---")

    # KPIs
    st.subheader("🔹 Demand KPIs")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", filtered_data.shape[0])
    col2.metric("Regions", filtered_data["Region"].nunique())
    col3.metric("Capacities", filtered_data["PET_bottle_capacity"].nunique())
    col4.metric("Types", filtered_data["Type"].nunique())

    st.markdown("---")

    # Line Chart: Demand Over Time
    st.subheader("📈 Demand Over Time (Monthly)")
    monthly_data = filtered_data.groupby("Month")["Volume_Million_Pieces"].sum().reset_index()
    fig_line = px.line(
        monthly_data, x="Month", y="Volume_Million_Pieces",
        title="Monthly PET Bottle Demand", markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Heatmap: Region vs Month
    st.subheader("🌍 Region-Wise Demand Heatmap")
    heatmap_data = filtered_data.groupby(["Region", "Month"])["Volume_Million_Pieces"].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="Region", columns="Month", values="Volume_Million_Pieces")
    fig_heatmap = px.imshow(
        heatmap_pivot, text_auto=True, aspect="auto",
        labels=dict(color="Volume (Million Pieces)"),
        title="Demand Heatmap by Region and Month"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Column Chart: Capacity-wise
    st.subheader("🧪 Demand by PET Bottle Capacity")
    cap_summary = filtered_data.groupby("PET_bottle_capacity")["Volume_Million_Pieces"].sum().reset_index()
    fig_capacity = px.bar(
        cap_summary.sort_values("Volume_Million_Pieces", ascending=False),
        x="PET_bottle_capacity", y="Volume_Million_Pieces",
        title="Total Demand by Bottle Capacity", text_auto=True, color="PET_bottle_capacity"
    )
    st.plotly_chart(fig_capacity, use_container_width=True)

    # Bar Chart: Type-wise
    st.subheader("🧱 Demand by PET Bottle Type")
    type_summary = filtered_data.groupby("Type")["Volume_Million_Pieces"].sum().reset_index()
    fig_type = px.bar(
        type_summary.sort_values("Volume_Million_Pieces", ascending=False),
        x="Type", y="Volume_Million_Pieces",
        title="Total Demand by Bottle Type", text_auto=True, color="Type"
    )
    st.plotly_chart(fig_type, use_container_width=True)

# --------- OTHER ANALYSIS ---------
elif section == "Other Analysis":
    st.title("🛠️ Future Analysis Placeholder")
    st.markdown("""
    This section will include future analysis such as:
    - 📊 Port Data Analysis  
    - 💰 Raw Material Price Trends  
    - 🤖 Forecasting and Predictive Modeling  
    - 🌐 Regional Supply Chain Insights
    """)
