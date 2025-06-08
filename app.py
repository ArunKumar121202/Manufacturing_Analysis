import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Demand.csv", parse_dates=["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df

demand_data = load_data()

# ---------------------- SIDEBAR ----------------------
st.sidebar.title("🔍 Filters")

# Filters
region_filter = st.sidebar.multiselect(
    "Select Region(s)", options=demand_data["Region"].unique(),
    default=demand_data["Region"].unique()
)

capacity_filter = st.sidebar.multiselect(
    "Select Capacity", options=demand_data["Capacity"].unique(),
    default=demand_data["Capacity"].unique()
)

type_filter = st.sidebar.multiselect(
    "Select Type", options=demand_data["Type"].unique(),
    default=demand_data["Type"].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [demand_data["Date"].min(), demand_data["Date"].max()]
)

# Navigation
section = st.sidebar.radio("📂 Navigation", ["Demand Analysis", "Other Analysis"])

# Apply filters
filtered_data = demand_data[
    (demand_data["Region"].isin(region_filter)) &
    (demand_data["Capacity"].isin(capacity_filter)) &
    (demand_data["Type"].isin(type_filter)) &
    (demand_data["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# ---------------------- MAIN: DEMAND ANALYSIS ----------------------
if section == "Demand Analysis":
    st.title("📦 PET Bottle Demand Analysis")
    st.markdown("Explore trends in PET bottle demand across regions, capacities, and types.")
    st.markdown("---")

    # KPIs
    st.subheader("🔹 Demand KPIs")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", filtered_data.shape[0])
    with col2:
        st.metric("Regions", filtered_data["Region"].nunique())
    with col3:
        st.metric("Capacities", filtered_data["Capacity"].nunique())
    with col4:
        st.metric("Types", filtered_data["Type"].nunique())

    # Line Chart: Demand Over Time
    st.subheader("📈 Demand Over Time (Monthly)")
    monthly_data = filtered_data.groupby("Month")["Volume (Million Pieces)"].sum().reset_index()
    fig_line = px.line(
        monthly_data, x="Month", y="Volume (Million Pieces)",
        title="Monthly PET Bottle Demand", markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Heatmap: Region vs Month
    st.subheader("🌍 Region-Wise Demand Heatmap")
    heatmap_data = filtered_data.groupby(["Region", "Month"])["Volume (Million Pieces)"].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="Region", columns="Month", values="Volume (Million Pieces)")
    fig_heatmap = px.imshow(
        heatmap_pivot, text_auto=True, aspect="auto",
        labels=dict(color="Volume (Million Pieces)"),
        title="Demand Heatmap by Region and Month"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Column Chart: Capacity-wise
    st.subheader("🧪 Demand by PET Bottle Capacity")
    cap_summary = filtered_data.groupby("Capacity")["Volume (Million Pieces)"].sum().reset_index()
    fig_capacity = px.bar(
        cap_summary.sort_values("Volume (Million Pieces)", ascending=False),
        x="Capacity", y="Volume (Million Pieces)",
        title="Total Demand by Bottle Capacity", text_auto=True, color="Capacity"
    )
    st.plotly_chart(fig_capacity, use_container_width=True)

    # Bar Chart: Type-wise
    st.subheader("🧱 Demand by PET Bottle Type")
    type_summary = filtered_data.groupby("Type")["Volume (Million Pieces)"].sum().reset_index()
    fig_type = px.bar(
        type_summary.sort_values("Volume (Million Pieces)", ascending=False),
        x="Type", y="Volume (Million Pieces)",
        title="Total Demand by Bottle Type", text_auto=True, color="Type"
    )
    st.plotly_chart(fig_type, use_container_width=True)

# ---------------------- MAIN: PLACEHOLDER FOR FUTURE ----------------------
elif section == "Other Analysis":
    st.title("🛠️ Future Analysis")
    st.markdown("Other analyses (like prediction, port data, raw material pricing) will be added here.")
