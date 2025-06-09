import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# ---------- Load and Clean Data ----------
data = pd.read_csv("Demand.csv")
data.columns = data.columns.str.strip()

# Rename for convenience
data.rename(columns={
    "Date of requirement": "Date",
    "PET bottle capacity": "Capacity",
    "PET bottle weight (grams)": "Weight_grams",
    "Volume (Million Pieces)": "Volume_Million_Pieces"
}, inplace=True)

# Convert date and filter for 2019 only
data["Date"] = pd.to_datetime(data["Date"], errors='coerce')
data = data[data["Date"].dt.year == 2019].copy()

# Extract Month
data["Month"] = data["Date"].dt.month_name()

# Clean Capacity and Type
data["Capacity"] = (
    data["Capacity"]
    .astype(str)
    .str.replace(r"[^\w\s.]", "", regex=True)
    .str.lower()
    .str.replace("oz", "oz", regex=False)
    .str.replace(" ", "")
    .str.replace(".", "")
    .str.replace(",", "")
    .str.replace("sleek", "ozsleek")
    .replace({
        "12ozsleek": "12 oz sleek", "8ozsleek": "8 oz sleek", "16oz": "16 oz",
        "10oz": "10 oz", "25oz": "25 oz", "12oz": "12 oz", "11oz": "11 oz", 
        "9oz": "9 oz", "19oz": "19 oz", "24oz": "24 oz", "32oz": "32 oz", 
        "44cl": "44 cl", "50cl": "50 cl", "33cl": "33 cl", "25cl": "25 cl", 
        "270ml": "270 ml", "310ml": "310 ml", "330ml": "330 ml", "355ml": "355 ml", 
        "500ml": "500 ml", "10.5oz": "10.5 oz", "16oz": "16 oz", "15cl": "15 cl"
    })
)

data["Type"] = (
    data["Type"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.title("🔍 Filters")

    region_filter = st.multiselect(
        "Select Region(s)", options=sorted(data["Region"].dropna().unique()),
        default=sorted(data["Region"].dropna().unique())
    )

    capacity_filter = st.multiselect(
        "Select Capacity", options=sorted(data["Capacity"].dropna().unique()),
        default=sorted(data["Capacity"].dropna().unique())
    )

    type_filter = st.multiselect(
        "Select Type", options=sorted(data["Type"].dropna().unique()),
        default=sorted(data["Type"].dropna().unique())
    )

# ---------- Apply Filters ----------
filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["Capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter))
]

# ---------- Main Content ----------
st.title("📦 PET Bottle Demand Dashboard - 2019")

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
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    monthly_data = (
        filtered_data.groupby("Month")["Volume_Million_Pieces"]
        .sum()
        .reindex(month_order)
        .reset_index()
        .dropna()
    )

    fig_line = px.line(
        monthly_data,
        x="Month",
        y="Volume_Million_Pieces",
        markers=True,
        title="Monthly PET Bottle Demand"
    )
    fig_line.update_layout(
        yaxis_tickformat=".2s"
    )
    fig_line.update_traces(
        text=[f"{v/1000:.2f}k" for v in monthly_data["Volume_Million_Pieces"]],
        textposition="top center",
        mode="lines+markers+text"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("🌍 Region vs Month Heatmap")
    heatmap_data = filtered_data.groupby(["Region", "Month"])["Volume_Million_Pieces"].sum().reset_index()
    heatmap_data["Month"] = pd.Categorical(heatmap_data["Month"], categories=month_order, ordered=True)
    pivot = heatmap_data.pivot(index="Region", columns="Month", values="Volume_Million_Pieces")
    fig_heatmap = px.imshow(
        pivot,
        text_auto=True,
        aspect="auto",
        labels=dict(color="Volume (Million Pieces)"),
        title="Heatmap: Region vs Month"
    )
    fig_heatmap.update_layout(coloraxis_colorbar_tickformat=".2s")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader("🧪 Capacity-wise Demand")
    cap_data = filtered_data.groupby("Capacity")["Volume_Million_Pieces"].sum().reset_index()
    fig_cap = px.bar(
        cap_data.sort_values("Volume_Million_Pieces", ascending=False),
        x="Capacity", y="Volume_Million_Pieces",
        title="Demand by PET Bottle Capacity",
        text=cap_data.sort_values("Volume_Million_Pieces", ascending=False)["Volume_Million_Pieces"].apply(lambda x: f"{x/1000:.2f}k"),
        color="Capacity"
    )
    fig_cap.update_layout(yaxis_tickformat=".2s")
    st.plotly_chart(fig_cap, use_container_width=True)

    st.subheader("🧱 Type-wise Demand")
    type_data = filtered_data.groupby("Type")["Volume_Million_Pieces"].sum().reset_index()
    fig_type = px.bar(
        type_data.sort_values("Volume_Million_Pieces", ascending=False),
        x="Type", y="Volume_Million_Pieces",
        title="Demand by PET Bottle Type",
        text=type_data.sort_values("Volume_Million_Pieces", ascending=False)["Volume_Million_Pieces"].apply(lambda x: f"{x/1000:.2f}k"),
        color="Type"
    )
    fig_type.update_layout(yaxis_tickformat=".2s")
    st.plotly_chart(fig_type, use_container_width=True)

with tab2:
    st.info("This section will include future analysis like port & raw material trends.")
