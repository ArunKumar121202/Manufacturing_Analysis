import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page Configuration ----------
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# ---------- Load & Clean Data ----------
data = pd.read_csv("Demand.csv")
data.columns = data.columns.str.strip()
Port = pd.read_csv("Port.csv")
raw_data = pd.read_csv("Raw Material Prices.csv")

# Rename columns for convenience
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

# ---------- Clean Port Data ----------
Port.columns = Port.columns.str.strip().str.lower().str.replace(" ", "_")
Port["region"] = Port["region"].str.strip().str.lower()
data["Region"] = data["Region"].str.strip().str.lower()

# Merge Demand with Port data to get blowing plant info (used later, not in Tab 1)
data_with_plant = data.merge(Port, how="left", left_on="Region", right_on="region")

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

    plant_filter = st.multiselect(
        "Select Blowing Plant(s)",
        options=sorted(data_with_plant["blowing_plant"].dropna().unique()),
        default=sorted(data_with_plant["blowing_plant"].dropna().unique())
    )

# ---------- Filtered Data for Tab 1 (unaltered) ----------
filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["Capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter))
]

# ---------- Main Title ----------
st.title("📦 PET Bottle Demand Dashboard")

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Demand Analysis",
    "🔗 Raw Material Pricing Trends",
    "📊 Correlation Analysis",
    "⚙️ Comparative & Supply Chain Demand"
])

# Tab 1 ... (unchanged)
# Tab 2 ... (unchanged)
# Tab 3 ... (unchanged)

# ----------------------------- TAB 4 -----------------------------
with tab4:
    st.subheader("🔹 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    top_capacity = filtered_data.groupby("Capacity")["Volume_Million_Pieces"].sum().idxmax()
    top_weight = filtered_data.groupby("Weight_grams")["Volume_Million_Pieces"].sum().idxmax()
    total_plants = Port["blowing_plant"].nunique()
    avg_volume_required = filtered_data["Volume_Million_Pieces"].mean()

    col1.metric("🏆 Top Capacity", f"{top_capacity}")
    col2.metric("⚖️ Top Bottle Weight", f"{top_weight} g")
    col3.metric("🏭 Total Blowing Plants", f"{total_plants}")
    col4.metric("📦 Avg. Volume Required", f"{avg_volume_required:.2f} M")

    st.markdown("---")
    st.subheader("📊 Comparative & Supply Chain Analysis")

    st.subheader("⚖️ Average PET Bottle Weight by Region")
    avg_weight_region = (
        filtered_data.groupby("Region")["Weight_grams"].mean().reset_index().sort_values(by="Weight_grams", ascending=False)
    )
    fig_avg_weight = px.bar(avg_weight_region, x="Region", y="Weight_grams", color="Region", text_auto=".2f")
    st.plotly_chart(fig_avg_weight, use_container_width=True)

    st.subheader("🏭 Blowing Plants per Region")
    region_plant_counts = Port.groupby("region")["blowing_plant"].nunique().reset_index()
    fig_plant = px.bar(region_plant_counts, x="region", y="blowing_plant", text_auto=True)
    st.plotly_chart(fig_plant, use_container_width=True)

    st.subheader("🗺️ Volume by Country")
    if "Country" in filtered_data.columns:
        country_volume = filtered_data.groupby("Country")["Volume_Million_Pieces"].sum().reset_index()
        fig_map = px.choropleth(country_volume, locations="Country", locationmode="country names", color="Volume_Million_Pieces", color_continuous_scale="Blues")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No 'Country' column found in the demand data to display map.")

    st.subheader("📆 Quarterly Volume Analysis")
    filtered_data["Quarter"] = filtered_data["Date"].dt.to_period("Q").astype(str)
    quarterly_volume = filtered_data.groupby("Quarter")["Volume_Million_Pieces"].sum().reset_index()
    fig_quarter = px.bar(quarterly_volume, x="Quarter", y="Volume_Million_Pieces", text_auto=".2s")
    st.plotly_chart(fig_quarter, use_container_width=True)

    # Volume Supplied by Each Blowing Plant
    st.subheader("🏭 Volume Supplied by Each Blowing Plant")
    merged_filtered = filtered_data.merge(Port, how="left", left_on="Region", right_on="region")
    plant_volume = (
        merged_filtered.groupby("blowing_plant")["Volume_Million_Pieces"]
        .sum().reset_index().sort_values(by="Volume_Million_Pieces", ascending=False)
    )
    fig_plant_volume = px.bar(
        plant_volume, x="blowing_plant", y="Volume_Million_Pieces", text_auto=".2s",
        title="Volume Supplied by Each Blowing Plant",
        labels={"blowing_plant": "Blowing Plant", "Volume_Million_Pieces": "Volume (Million Pieces)"}
    )
    fig_plant_volume.update_layout(yaxis_tickformat=".2s")
    st.plotly_chart(fig_plant_volume, use_container_width=True)
