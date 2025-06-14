import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------- Authentication Setup -------------------
VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 PET Bottle Demand Dashboard Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

def logout():
    st.session_state.logged_in = False
    st.rerun()

if not st.session_state.logged_in:
    login()
    st.stop()

# ------------------- Page Configuration -------------------
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# ------------------- Sidebar Logout Button -------------------
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout"):
    logout()

# ------------------- Load & Clean Data -------------------
data = pd.read_csv("Demand.csv")
data.columns = data.columns.str.strip()
Port = pd.read_csv("Port.csv")
raw_data = pd.read_csv("Raw Material Prices.csv")

# Rename columns
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

data["Type"] = data["Type"].astype(str).str.strip().str.title()

Port.columns = Port.columns.str.strip().str.lower().str.replace(" ", "_")
Port["region"] = Port["region"].str.strip().str.lower()
data["Region"] = data["Region"].str.strip().str.lower()

data_with_plant = data.merge(Port, how="left", left_on="Region", right_on="region")

# ------------------- Sidebar Filters -------------------
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

    month_filter = st.multiselect(
        "Select Month(s)",
        options=[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ],
        default=[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
    )

    plant_filter = st.multiselect(
        "Select Blowing Plant(s)",
        options=sorted(data_with_plant["blowing_plant"].dropna().unique()),
        default=sorted(data_with_plant["blowing_plant"].dropna().unique())
    )

filtered_data = data[
    (data["Region"].isin(region_filter)) &
    (data["Capacity"].isin(capacity_filter)) &
    (data["Type"].isin(type_filter)) &
    (data["Month"].isin(month_filter))
]

# ------------------- Main Title -------------------
st.title("📦 PET Bottle Demand Dashboard")

# ------------------- Tabs -------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Demand Analysis",
    "🔗 Raw Material Pricing Trends",
    "📊 Correlation Analysis",
    "⚙️ Comparative & Supply Chain Demand"
])

# ------------------- TAB 1 -------------------
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

    st.subheader("📅 Monthly Demand Trend")
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    monthly_data = (
        filtered_data.groupby("Month")["Volume_Million_Pieces"]
        .sum().reindex(month_order).reset_index().dropna()
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

# ------------------- TAB 2 -------------------
with tab2:
    raw_data.columns = raw_data.columns.str.replace("\n", " ").str.strip()
    for col in raw_data.columns:
        if "PET" in col and "Poly Ethylene" in col:
            raw_data.rename(columns={col: "PET_Price"}, inplace=True)
            break

    raw_data["Month"] = pd.to_datetime(raw_data["Month"], errors="coerce")
    for col in raw_data.columns:
        if col != "Month":
            raw_data[col] = pd.to_numeric(raw_data[col], errors="coerce")
    raw_data["Year"] = raw_data["Month"].dt.year
    raw_data["Month_Name"] = raw_data["Month"].dt.strftime('%B')

    st.subheader("🔹 Key Performance Indicators")
    avg_pet = raw_data["PET_Price"].mean()
    latest_row = raw_data.dropna(subset=["PET_Price"]).sort_values("Month").iloc[-1]
    recent_pet = latest_row["PET_Price"]
    recent_pet_month = latest_row["Month"].strftime("%B %Y")
    max_pet = raw_data["PET_Price"].max()
    yoy_change = None
    yearly_avg = raw_data.groupby("Year")["PET_Price"].mean().sort_index()
    if len(yearly_avg) >= 2:
        yoy_change = ((yearly_avg.iloc[-1] - yearly_avg.iloc[-2]) / yearly_avg.iloc[-2]) * 100
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Average PET Price", f"${avg_pet:.2f}")
    k2.metric("🕒 Recent PET Price", f"${recent_pet:.2f}", delta=recent_pet_month)
    k3.metric("📈 Max Recorded PET Price", f"${max_pet:.2f}")
    k4.metric("🔁 YoY PET Price Change", f"{yoy_change:.2f}%" if yoy_change is not None else "N/A")

    st.markdown("---")
    st.subheader("📊 Raw Material Pricing Trends")

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

    yearwise_sum = raw_data.groupby("Year")[material_cols].sum().reset_index()
    fig_yearwise = px.line(
        yearwise_sum.melt(id_vars="Year"),
        x="Year", y="value", color="variable",
        title="Total Raw Material Prices by Year"
    )
    st.plotly_chart(fig_yearwise, use_container_width=True)

    pet_by_year = raw_data.groupby("Year")["PET_Price"].mean().reset_index()
    fig_pet_year = px.bar(pet_by_year, x="Year", y="PET_Price", title="Average PET Price by Year", text_auto=".2f")
    st.plotly_chart(fig_pet_year, use_container_width=True)

    pet_by_month = raw_data.groupby("Month_Name")["PET_Price"].mean().reindex([
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]).reset_index()
    fig_pet_month = px.bar(pet_by_month, x="Month_Name", y="PET_Price", title="Average PET Price by Month", text_auto=".2f")
    st.plotly_chart(fig_pet_month, use_container_width=True)

# ------------------- TAB 3 -------------------
with tab3:
    st.subheader("Correlation Analysis of the numerical columns")
    corr_data = filtered_data.select_dtypes(include='number')
    if not corr_data.empty and "Volume_Million_Pieces" in corr_data.columns:
        corr = corr_data.corr().round(2)
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("Not enough numeric data to compute correlations.")

# ------------------- TAB 4 -------------------
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
