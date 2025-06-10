import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page Configuration ----------
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# ---------- Load & Clean Data ----------
data = pd.read_csv("Demand.csv")
data.columns = data.columns.str.strip()
raw_data=pd.read_csv("Raw Material Prices.csv")
# Rename for convenience
data.rename(columns={
    "Date of requirement": "Date",
    "PET bottle capacity": "Capacity",
    "PET bottle weight (grams)": "Weight_grams",
    "Volume (Million Pieces)": "Volume_Million_Pieces"
}, inplace=True)

# Parse Date and filter only 2019
data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
data = data[data["Date"].dt.year == 2019].copy()
data["Month"] = data["Date"].dt.month_name()

# Clean Capacity column
data["Capacity"] = (
    data["Capacity"].astype(str)
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
        "500ml": "500 ml", "10.5oz": "10.5 oz", "15cl": "15 cl"
    })
)

# Clean Type column
data["Type"] = data["Type"].astype(str).str.strip().str.title()

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.title("🔍 Filters")

    region_filter = st.multiselect(
        "Select Region(s)",
        options=sorted(data["Region"].dropna().unique()),
        default=sorted(data["Region"].dropna().unique())
    )

    capacity_filter = st.multiselect(
        "Select Capacity",
        options=sorted(data["Capacity"].dropna().unique()),
        default=sorted(data["Capacity"].dropna().unique())
    )

    type_filter = st.multiselect(
        "Select Type",
        options=sorted(data["Type"].dropna().unique()),
        default=sorted(data["Type"].dropna().unique())
    )

# ---------- Filtered Data ----------
filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["Capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter))
]

# ---------- Main Title ----------
st.title("📦 PET Bottle Demand Dashboard")

# ---------- Tabs ----------
tab1, tab2 = st.tabs(["📈 Demand Analysis", "🔗 Raw Material Pricing Trends"])

# ---------- TAB 1: Demand Analysis ----------
with tab1:
    st.subheader("🔹 Key Performance Indicators")

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    total_volume = filtered_data["Volume_Million_Pieces"].sum()
    avg_volume = filtered_data.groupby("Month")["Volume_Million_Pieces"].sum().mean()
    unique_capacities = filtered_data["Capacity"].nunique()
    unique_types = filtered_data["Type"].nunique()
    unique_countries = filtered_data["Country"].nunique() if "Country" in filtered_data.columns else "N/A"
    unique_regions = filtered_data["Region"].nunique()

    col1.metric("Total Volume", f"{total_volume / 1000:.2f} K")
    col2.metric("Avg. Monthly Volume", f"{avg_volume / 1000:.2f} K")
    col3.metric("Total Capacities", unique_capacities)
    col4.metric("Total Types", unique_types)
    col5.metric("Total Countries", unique_countries)
    col6.metric("Total Regions", unique_regions)

    st.markdown("---")

    # Monthly Trend
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

    fig_month = px.line(
        monthly_data, x="Month", y="Volume_Million_Pieces",
        markers=True, title="Monthly PET Bottle Demand"
    )
    fig_month.update_layout(yaxis_tickformat=".2s")
    fig_month.update_traces(
        text=[f"{v/1000:.2f}k" for v in monthly_data["Volume_Million_Pieces"]],
        textposition="top center", mode="lines+markers+text"
    )
    st.plotly_chart(fig_month, use_container_width=True)

    # Heatmap
    st.subheader("🌍 Region vs Month Heatmap")
    heatmap_data = filtered_data.groupby(["Region", "Month"])["Volume_Million_Pieces"].sum().reset_index()
    heatmap_data["Month"] = pd.Categorical(heatmap_data["Month"], categories=month_order, ordered=True)
    pivot = heatmap_data.pivot(index="Region", columns="Month", values="Volume_Million_Pieces")
    fig_heatmap = px.imshow(
        pivot, text_auto=True, aspect="auto",
        labels=dict(color="Volume (Million Pieces)"),
        title="Heatmap: Region vs Month"
    )
    fig_heatmap.update_layout(coloraxis_colorbar_tickformat=".2s")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Capacity-wise
    st.subheader("🧪 Capacity-wise Demand")
    cap_data = filtered_data.groupby("Capacity")["Volume_Million_Pieces"].sum().reset_index()
    fig_cap = px.bar(
        cap_data.sort_values("Volume_Million_Pieces", ascending=False),
        x="Capacity", y="Volume_Million_Pieces",
        title="Demand by PET Bottle Capacity",
        text_auto=".2s", color="Capacity"
    )
    fig_cap.update_layout(yaxis_tickformat=".2s")
    st.plotly_chart(fig_cap, use_container_width=True)

    # Type-wise
    st.subheader("🧱 Type-wise Demand")
    type_data = filtered_data.groupby("Type")["Volume_Million_Pieces"].sum().reset_index()
    fig_type = px.bar(
        type_data.sort_values("Volume_Million_Pieces", ascending=False),
        x="Type", y="Volume_Million_Pieces",
        title="Demand by PET Bottle Type",
        text_auto=".2s", color="Type"
    )
    fig_type.update_layout(yaxis_tickformat=".2s")
    st.plotly_chart(fig_type, use_container_width=True)

# ---------- TAB 2: Raw Material Pricing Trends ----------
with tab2:
    st.subheader("📊 Raw Material Pricing Trends")

    # Clean column names
    raw_data.columns = raw_data.columns.str.replace("\n", " ").str.strip()

    # Dynamically rename PET price column
    for col in raw_data.columns:
        if "PET" in col and "Poly Ethylene" in col:
            raw_data.rename(columns={col: "PET_Price"}, inplace=True)
            break

    # Convert Month to datetime
    raw_data["Month"] = pd.to_datetime(raw_data["Month"], errors="coerce")

    # Convert PET_Price and other material prices to numeric
    for col in raw_data.columns:
        if col != "Month":
            raw_data[col] = pd.to_numeric(raw_data[col], errors="coerce")

    # Add Year and Month_Name columns
    raw_data["Year"] = raw_data["Month"].dt.year
    raw_data["Month_Name"] = raw_data["Month"].dt.strftime('%B')

    # KPI 1: Average PET price
    avg_pet = raw_data["PET_Price"].mean()

    # KPI 2: Most recent PET price (based on latest month)
    latest_row = raw_data.dropna(subset=["PET_Price"]).sort_values("Month").iloc[-1]
    recent_pet = latest_row["PET_Price"]
    recent_pet_month = latest_row["Month"].strftime("%B %Y")

    # KPI 3: Max PET price ever recorded
    max_pet = raw_data["PET_Price"].max()

    # KPI 4: YoY % change
    yoy_change = None
    yearly_avg = raw_data.groupby("Year")["PET_Price"].mean().sort_index()
    if len(yearly_avg) >= 2:
        yoy_change = ((yearly_avg.iloc[-1] - yearly_avg.iloc[-2]) / yearly_avg.iloc[-2]) * 100

    # Display KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Average PET Price", f"${avg_pet:.2f}")
    k2.metric("🕒 Recent PET Price", f"${recent_pet:.2f}", delta=recent_pet_month)
    k3.metric("📈 Max Recorded PET Price", f"${max_pet:.2f}")
    k4.metric("🔁 YoY PET Price Change", f"{yoy_change:.2f}%" if yoy_change is not None else "N/A")

    st.markdown("---")

    # --- 1. Raw Material Prices Summed by Month Name ---
    st.subheader("📉 Monthly Raw Material Price Trends")
    material_cols = [col for col in raw_data.columns if col not in ["Month", "Year", "Month_Name", "PET_Price"]]
    monthwise_sum = raw_data.groupby("Month_Name")[material_cols].sum().reindex([
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    fig_monthwise = px.line(
        monthwise_sum.reset_index().melt(id_vars="Month_Name"),
        x="Month_Name", y="value", color="variable",
        title="Total Raw Material Prices by Month"
    )
    st.plotly_chart(fig_monthwise, use_container_width=True)

    # --- 2. Raw Material Prices Summed by Year ---
    st.subheader("📈 Yearly Raw Material Price Trends")
    yearwise_sum = raw_data.groupby("Year")[material_cols].sum().reset_index()
    fig_yearwise = px.line(
        yearwise_sum.melt(id_vars="Year"),
        x="Year", y="value", color="variable",
        title="Total Raw Material Prices by Year"
    )
    st.plotly_chart(fig_yearwise, use_container_width=True)

    # --- 3. Average PET Price by Year ---
    st.subheader("📊 Average PET Prices by Year")
    pet_by_year = raw_data.groupby("Year")["PET_Price"].mean().reset_index()
    fig_pet_year = px.bar(
        pet_by_year, x="Year", y="PET_Price",
        title="Average PET Price by Year",
        text_auto=".2f"
    )
    st.plotly_chart(fig_pet_year, use_container_width=True)

    # --- 4. Monthly Average PET Prices ---
    st.subheader("🗓️ Monthly Average PET Prices")
    pet_by_month = raw_data.groupby("Month_Name")["PET_Price"].mean().reindex([
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]).reset_index()
    fig_pet_month = px.bar(
        pet_by_month, x="Month_Name", y="PET_Price",
        title="Average PET Price by Month",
        text_auto=".2f"
    )
    st.plotly_chart(fig_pet_month, use_container_width=True)

