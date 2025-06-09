import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# ---------- Load and Clean Data ----------
data = pd.read_csv("Demand.csv")
data.columns = data.columns.str.strip()

# Rename columns
data.rename(columns={
    "Date of requirement": "Date",
    "PET bottle capacity": "Capacity",
    "PET bottle weight (grams)": "Weight_grams",
    "Volume (Million Pieces)": "Volume_Million_Pieces"
}, inplace=True)

# Convert Date and extract Month
data["Date"] = pd.to_datetime(data["Date"], errors='coerce')
data["Month"] = data["Date"].dt.month_name()

# ---------- Normalize Capacity ----------
capacity_map = {
    "44cl": "44cl", "12Oz": "12 oz", "56,8cl": "56.8cl", "19Oz": "19 oz",
    "50cl": "50cl", "355ml": "355ml", "8oz Sleek": "8 oz sleek", "10 OZ": "10 oz",
    "25oz": "25 oz", "8 OZ": "8 oz", "11Oz": "11 oz", "11 OZ": "11 oz",
    "24 OZ": "24 oz", "25cl": "25cl", "10.5Oz": "10.5 oz", "9Oz": "9 oz",
    "33cl": "33cl", "310ml": "310ml", "16 OZ": "16 oz", "32oz": "32 oz",
    "500ml": "500ml", "16Oz": "16 oz", "330ml": "330ml", "25 OZ": "25 oz",
    "12oz Sleek": "12 oz sleek", "15cl": "15cl", "270ml": "270ml", 
    "12 OZ": "12 oz", "12oz": "12 oz", "16oz": "16 oz"
}
data["Capacity"] = data["Capacity"].str.strip().map(capacity_map).fillna(data["Capacity"].str.strip().str.lower())

# ---------- Normalize Type ----------
type_map = {
    "Standard": "Standard", "SLEEK": "Sleek", "BIG CAN": "Big Can",
    "Big Can": "Big Can", "Slim": "Slim", "Sleek": "Sleek", 
    "STANDARD": "Standard", "Embossed": "Embossed"
}
data["Type"] = data["Type"].str.strip().map(type_map).fillna(data["Type"].str.strip().str.title())

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.title("🔍 Filters")

    region_filter = st.multiselect(
        "Select Region(s)", options=sorted(data["Region"].unique()),
        default=sorted(data["Region"].unique())
    )

    capacity_filter = st.multiselect(
        "Select Capacity", options=sorted(data["Capacity"].unique()),
        default=sorted(data["Capacity"].unique())
    )

    type_filter = st.multiselect(
        "Select Type", options=sorted(data["Type"].unique()),
        default=sorted(data["Type"].unique())
    )

    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    month_filter = st.multiselect(
        "Select Month(s)", options=month_order,
        default=month_order
    )

# ---------- Apply Filters ----------
filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["Capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter)) &
    (data["Month"].isin(month_filter))
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
    st.subheader("📅 Monthly Demand Trend")
    monthly_data = (
        filtered_data.groupby("Month")["Volume_Million_Pieces"]
        .sum()
        .reindex(month_order)
        .reset_index()
        .dropna()
    )
    fig_line = px.line(monthly_data, x="Month", y="Volume_Million_Pieces", markers=True,
                       title="Monthly PET Bottle Demand")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("🌍 Region vs Month Heatmap")
    heatmap_data = filtered_data.groupby(["Region", "Month"])["Volume_Million_Pieces"].sum().reset_index()
    heatmap_data["Month"] = pd.Categorical(heatmap_data["Month"], categories=month_order, ordered=True)
    pivot = heatmap_data.pivot(index="Region", columns="Month", values="Volume_Million_Pieces")
    fig_heatmap = px.imshow(pivot, text_auto=True, aspect="auto",
                            labels=dict(color="Volume (Million Pieces)"),
                            title="Heatmap: Region vs Month")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader("🧪 Capacity-wise Demand")
    cap_data = filtered_data.groupby("Capacity")["Volume_Million_Pieces"].sum().reset_index()
    fig_cap = px.bar(cap_data.sort_values("Volume_Million_Pieces", ascending=False),
                     x="Capacity", y="Volume_Million_Pieces",
                     title="Demand by PET Bottle Capacity", text_auto=True, color="Capacity")
    st.plotly_chart(fig_cap, use_container_width=True)

    st.subheader("🧱 Type-wise Demand")
    type_data = filtered_data.groupby("Type")["Volume_Million_Pieces"].sum().reset_index()
    fig_type = px.bar(type_data.sort_values("Volume_Million_Pieces", ascending=False),
                      x="Type", y="Volume_Million_Pieces",
                      title="Demand by PET Bottle Type", text_auto=True, color="Type")
    st.plotly_chart(fig_type, use_container_width=True)

with tab2:
    st.info("This section will include future analysis like port & raw material trends.")
