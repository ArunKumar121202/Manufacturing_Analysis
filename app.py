import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# --- Load & Clean Data
data = pd.read_csv("Demand.csv")
data.columns = data.columns.str.strip()
Port = pd.read_csv("Port.csv")
raw_data = pd.read_csv("Raw Material Prices.csv")

# Normalize Demand data
data.rename(columns={
    "Date of requirement": "Date",
    "PET bottle capacity": "Capacity",
    "PET bottle weight (grams)": "Weight_grams",
    "Volume (Million Pieces)": "Volume_Million_Pieces"
}, inplace=True)
data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
data = data[data["Date"].dt.year == 2019].copy()
data["Month"] = data["Date"].dt.month_name()
data["Capacity"] = (
    data["Capacity"].astype(str)
    .str.replace(r"[^\w\s.]", "", regex=True)
    .str.lower()
    .str.replace(" ", "")
    .str.replace(".", "")
    .str.replace(",", "")
    .replace({...})  # your existing mappings
)
data["Type"] = data["Type"].astype(str).str.title()

# --- Sidebar Filters for Demand
region_filter = st.sidebar.multiselect(
    "Regions", sorted(data["Region"].unique()), default=sorted(data["Region"].unique())
)
capacity_filter = st.sidebar.multiselect(
    "Capacities", sorted(data["Capacity"].unique()), default=sorted(data["Capacity"].unique())
)
type_filter = st.sidebar.multiselect(
    "Types", sorted(data["Type"].unique()), default=sorted(data["Type"].unique())
)

filtered_data = data[
    data["Region"].isin(region_filter) &
    data["Capacity"].isin(capacity_filter) &
    data["Type"].isin(type_filter)
]

st.title("📦 PET Bottle Demand Dashboard")

# --- Four Tabs Setup
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Demand Analysis",
    "🔗 Raw Material Pricing Trends",
    "📊 Correlation Analysis",
    "⚙️ Comparative & Supply Chain Demand"
])

# --- Tab 1: Demand Analysis (unchanged) ---
with tab1:
    ...
    # existing code

# --- Tab 2: Raw Material Pricing Trends ---
with tab2:
    st.subheader("🔹 Raw Material Pricing Trends")

    # Clean column names
    raw_data.columns = raw_data.columns.str.replace("\n", " ").str.strip()
    for c in raw_data.columns:
        if "PET" in c and "Poly Ethylene" in c:
            raw_data.rename(columns={c: "PET_Price"}, inplace=True)
            break

    raw_data["Month_DT"] = pd.to_datetime(raw_data["Month"], errors="coerce")
    raw_data["Year"] = raw_data["Month_DT"].dt.year
    raw_data["Month_Name"] = raw_data["Month_DT"].dt.strftime('%B')
    price_cols = [c for c in raw_data.columns if "USD/MT" in c or c == "PET_Price"]

    # Convert all numeric
    raw_data[price_cols] = raw_data[price_cols].apply(pd.to_numeric, errors="coerce")

    # KPIs
    avg_pet = raw_data["PET_Price"].mean()
    recent = raw_data.dropna(subset=["PET_Price"]).sort_values("Month_DT").iloc[-1]
    max_pet = raw_data["PET_Price"].max()
    yearly_avg = raw_data.groupby("Year")["PET_Price"].mean().sort_index()
    yoy = (yearly_avg.iloc[-1] - yearly_avg.iloc[-2]) / yearly_avg.iloc[-2] * 100 if len(yearly_avg) >= 2 else None

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Avg PET Price", f"${avg_pet:.2f}")
    k2.metric("Latest PET Price", f"${recent['PET_Price']:.2f}", delta=recent["Month_Name"])
    k3.metric("Max PET Price", f"${max_pet:.2f}")
    k4.metric("YoY Change", f"{yoy:.2f}%" if yoy else "N/A")

    st.markdown("---")

    # 1. Monthly raw material trends (sum across all materials for each month)
    raw_data["Month_MonthNum"] = raw_data["Month_DT"].dt.month
    monthwise = raw_data.groupby("Month_MonthNum")[price_cols].sum().reset_index()
    monthwise["Month_Name"] = monthwise["Month_MonthNum"].apply(lambda x: pd.to_datetime(str(x), format="%m").strftime('%B'))
    fig_m = px.line(monthwise.melt(id_vars="Month_Name"), x="Month_Name", y="value", color="variable",
                    title="Total Raw Material Prices per Month")
    st.plotly_chart(fig_m, use_container_width=True)

    # 2. Yearly raw material trends (sum)
    yearly_sum = raw_data.groupby("Year")[price_cols].sum().reset_index()
    fig_y = px.line(yearly_sum.melt(id_vars="Year"), x="Year", y="value", color="variable",
                    title="Total Raw Material Prices per Year")
    st.plotly_chart(fig_y, use_container_width=True)

    # 3. Average PET price per year
    fig_py = px.bar(yearly_avg.reset_index(), x="Year", y="PET_Price",
                    title="Avg PET Price per Year", text_auto=".2f")
    st.plotly_chart(fig_py, use_container_width=True)

    # 4. Monthly average PET price
    pet_month_avg = raw_data.groupby("Month_Name")["PET_Price"].mean().reindex([
        'January','February','March','April','May','June',
        'July','August','September','October','November','December'
    ]).reset_index()
    fig_pm = px.bar(pet_month_avg, x="Month_Name", y="PET_Price",
                    title="Avg PET Price per Month", text_auto=".2f")
    st.plotly_chart(fig_pm, use_container_width=True)

# --- Tab 3: Correlation Analysis ---
with tab3:
    st.subheader("🔄 Correlation Matrix")
    num = filtered_data.select_dtypes('number')
    corr = num.corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r',
                         title="Numeric Correlations (incl. Volume)")
    st.plotly_chart(fig_corr, use_container_width=True)

# --- Tab 4: Comparative & Supply Chain Demand ---
with tab4:
    st.subheader("⚙️ Supply Chain & Comparative Analysis")

    Port.columns = Port.columns.str.strip().str.title()
    Port["Blowing_Plant"] = Port["Blowing Plant"].astype(str).str.title()
    Port["Region"] = Port["Region"].astype(str).str.title()
    merged = pd.merge(filtered_data, Port[["Region", "Blowing_Plant"]].drop_duplicates(), on="Region", how="left")

    # Blowing plant filter
    plants = st.multiselect("Blowing Plant", sorted(merged["Blowing_Plant"].dropna().unique()), default=None)
    if plants:
        merged = merged[merged["Blowing_Plant"].isin(plants)]

    k1, k2, k3, k4 = st.columns(4)
    top_cap = merged.groupby("Capacity")["Volume_Million_Pieces"].sum().idxmax()
    top_w = merged.groupby("Weight_grams")["Volume_Million_Pieces"].sum().idxmax()
    k1.metric("Top Capacity", top_cap)
    k2.metric("Top Weight (g)", f"{top_w:.1f}")
    k3.metric("Total Blowing Plants", Port["Blowing_Plant"].nunique())
    k4.metric("Avg Volume Req (M)", f"{merged['Volume_Million_Pieces'].mean():.2f}")

    st.markdown("---")

    # 1. Weight by region
    fig_box = px.box(merged, x="Region", y="Weight_grams", color="Region", title="Bottle Weight by Region")
    st.plotly_chart(fig_box, use_container_width=True)

    # 2. Blowing plants per region
    plant_counts = Port.groupby("Region")["Blowing_Plant"].nunique().reset_index()
    fig_bar = px.bar(plant_counts, x="Region", y="Blowing_Plant", text_auto=True, title="Blowing Plants / Region")
    st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Volume by country
    if "Country" in merged.columns:
        cv = merged.groupby("Country")["Volume_Million_Pieces"].sum().reset_index()
        fig_map = px.choropleth(cv, locations="Country", locationmode="country names",
                                color="Volume_Million_Pieces", title="Volume by Country")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Country data not available.")

    # 4. Quarterly volume
    merged["Quarter"] = merged["Date"].dt.to_period("Q").astype(str)
    qv = merged.groupby("Quarter")["Volume_Million_Pieces"].sum().reset_index()
    fig_q = px.bar(qv, x="Quarter", y="Volume_Million_Pieces", text_auto=".2s", title="Quarterly Volume")
    fig_q.update_layout(yaxis_tickformat=".2s")
    st.plotly_chart(fig_q, use_container_width=True)
