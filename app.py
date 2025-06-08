import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# ---------- Load and Clean Data ----------
data = pd.read_csv("Demand.csv")
data.columns = data.columns.str.strip()  # Remove unwanted spaces

# Rename for convenience
data.rename(columns={
    "Date of requirement": "Date",
    "PET bottle capacity": "Capacity",
    "PET bottle weight (grams)": "Weight_grams",
    "Volume (Million Pieces)": "Volume_Million_Pieces"
}, inplace=True)

# Convert and filter only 2019
data["Date"] = pd.to_datetime(data["Date"])
data = data[data["Date"].dt.year == 2019].copy()
data["Month"] = data["Date"].dt.to_period("M").astype(str)

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.title("🔍 Filters")

    region_filter = st.multiselect(
        "Select Region(s)", options=data["Region"].unique(),
        default=data["Region"].unique()
    )

    capacity_filter = st.multiselect(
        "Select Capacity", options=data["Capacity"].unique(),
        default=data["Capacity"].unique()
    )

    type_filter = st.multiselect(
        "Select Type", options=data["Type"].unique(),
        default=data["Type"].unique()
    )

    date_range = st.date_input(
        "Select Date Range",
        [data["Date"].min(), data["Date"].max()]
    )

# ---------- Apply Filters ----------
filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["Capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter)) &
    (data["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# ---------- Main Content ----------
st.title("📦 PET Bottle Demand Dashboard")

# ---------- KPIs ----------
st.subheader("🔹 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", filtered_data.shape[0])
col2.metric("Regions", filtered_data["Region"].nunique())
col3.metric("Capacities", filtered_data["Capacity"].nunique())
col4.metric("Types", filtered_data["Type"].nunique())

st.markdown("---")

# ---------- Analysis Tabs ----------
tab1, tab2 = st.tabs(["📈 Demand Analysis", "🛠️ Coming Soon"])

with tab1:
    st.subheader("Monthly Demand Trend")
    monthly_data = filtered_data.groupby("Month")["Volume_Million_Pieces"].sum().reset_index()
    fig_line = px.line(monthly_data, x="Month", y="Volume_Million_Pieces", markers=True,
                       title="Monthly PET Bottle Demand (2019)")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Region vs Month Heatmap")
    heatmap_data = filtered_data.groupby(["Region", "Month"])["Volume_Million_Pieces"].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="Region", columns="Month", values="Volume_Million_Pieces")
    fig_heatmap = px.imshow(heatmap_pivot, text_auto=True, aspect="auto",
                            labels=dict(color="Volume (Million Pieces)"),
                            title="Heatmap: Region vs Month")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader("Capacity-wise Demand")
    cap_data = filtered_data.groupby("Capacity")["Volume_Million_Pieces"].sum().reset_index()
    fig_cap = px.bar(cap_data.sort_values("Volume_Million_Pieces", ascending=False),
                     x="Capacity", y="Volume_Million_Pieces",
                     title="Demand by PET Bottle Capacity", text_auto=True, color="Capacity")
    st.plotly_chart(fig_cap, use_container_width=True)

    st.subheader("Type-wise Demand")
    type_data = filtered_data.groupby("Type")["Volume_Million_Pieces"].sum().reset_index()
    fig_type = px.bar(type_data.sort_values("Volume_Million_Pieces", ascending=False),
                      x="Type", y="Volume_Million_Pieces",
                      title="Demand by PET Bottle Type", text_auto=True, color="Type")
    st.plotly_chart(fig_type, use_container_width=True)

with tab2:
    st.info("This section will include future analysis like port & raw material trends.")

