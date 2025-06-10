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

    # Clean column names and rename for clarity
    raw_data.columns = raw_data.columns.str.strip()
    raw_data.rename(columns={
        "Month": "Date",
        "PET : Poly Ethylene Terephthalate USD/MT": "PET Price",
        "PTA : Pure Terephthalic Acid USD/MT": "PTA Price",
        "MEG: MonoEthylene Glycol USD/MT": "MEG Price",
        "PX : Paraxylene USD/MT": "PX Price",
        "Naphtha USD/MT": "Naphtha Price",
        "Ethylene USD/MT": "Ethylene Price"
    }, inplace=True)

    # Convert 'Date' to datetime and extract Year and Month
    raw_data["Date"] = pd.to_datetime(raw_data["Date"], errors='coerce')
    raw_data.dropna(subset=["Date"], inplace=True)
    raw_data["Year"] = raw_data["Date"].dt.year
    raw_data["Month"] = raw_data["Date"].dt.month_name()

    # KPIs
    st.markdown("### 🔹 Key Price Indicators")
    col1, col2, col3, col4 = st.columns(4)

    if "PET Price" in raw_data.columns:
        avg_price = raw_data["PET Price"].mean()
        latest_price = raw_data.sort_values("Date", ascending=False)["PET Price"].iloc[0]
        max_price = raw_data["PET Price"].max()

        # YoY price change
        yearly_avg = raw_data.groupby("Year")["PET Price"].mean().sort_index()
        if len(yearly_avg) >= 2:
            yoy_change = ((yearly_avg.iloc[-1] - yearly_avg.iloc[-2]) / yearly_avg.iloc[-2]) * 100
        else:
            yoy_change = None

        col1.metric("Avg. PET Price", f"${avg_price:.2f}")
        col2.metric("Latest PET Price", f"${latest_price:.2f}")
        col3.metric("Highest PET Price", f"${max_price:.2f}")
        col4.metric("YoY Price Change", f"{yoy_change:.2f}%" if yoy_change is not None else "N/A")
    else:
        st.error("❌ 'PET Price' column not found in raw material data.")

    st.markdown("---")

    # 1. All Raw Material Prices Over Months
    st.markdown("### 📈 All Raw Material Prices Over Time")
    price_columns = ["PET Price", "PTA Price", "MEG Price", "PX Price", "Naphtha Price", "Ethylene Price"]
    fig_all_months = px.line(
        raw_data, x="Date", y=price_columns,
        title="All Raw Material Prices Over Time"
    )
    st.plotly_chart(fig_all_months, use_container_width=True)

    # 2. All Raw Material Prices by Year
    st.markdown("### 📆 Raw Material Prices by Year")
    yearly_data = raw_data.groupby("Year")[price_columns].mean().reset_index()
    fig_yearly = px.line(
        yearly_data, x="Year", y=price_columns,
        markers=True, title="Yearly Average Raw Material Prices"
    )
    st.plotly_chart(fig_yearly, use_container_width=True)

    # 3. Average PET Prices by Year
    st.markdown("### 📊 Average PET Price by Year")
    pet_by_year = raw_data.groupby("Year")["PET Price"].mean().reset_index()
    fig_pet_year = px.bar(
        pet_by_year, x="Year", y="PET Price",
        text_auto=".2f", title="Average PET Price per Year",
        color="PET Price", color_continuous_scale="viridis"
    )
    st.plotly_chart(fig_pet_year, use_container_width=True)

    # 4. Monthly Average PET Prices
    st.markdown("### 🗓️ Monthly Average PET Price")
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    pet_by_month = (
        raw_data.groupby("Month")["PET Price"]
        .mean()
        .reindex(month_order)
        .reset_index()
        .dropna()
    )
    fig_pet_month = px.line(
        pet_by_month, x="Month", y="PET Price",
        title="Monthly Average PET Price",
        markers=True
    )
    st.plotly_chart(fig_pet_month, use_container_width=True)

