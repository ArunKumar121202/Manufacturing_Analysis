import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="PET Bottle Demand Dashboard", layout="wide")

# --------- Load Data with Safety Check ---------
@st.cache_data
def load_data():
    df = pd.read_csv("Demand.csv")
    
    # Fix for column name inconsistencies
    date_col = [col for col in df.columns if col.lower() == "date"]
    if not date_col:
        st.error("❌ 'Date' column not found in the uploaded data.")
        return pd.DataFrame()
    
    df.rename(columns={date_col[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df

demand_data = load_data()

if demand_data.empty:
    st.stop()

# --------- SIDEBAR: Filters & Navigation ---------
with st.sidebar:
    st.title("🔍 Filters")

    region_filter = st.multiselect(
        "Select Region(s)", options=demand_data["Region"].unique(),
        default=demand_data["Region"].unique()
    )

    capacity_filter = st.multiselect(
        "Select Capacity", options=demand_data["Capacity"].unique(),
        default=demand_data["Capacity"].unique()
    )

    type_filter = st.multiselect(
        "Select Type", options=demand_data["Type"].unique(),
        default=demand_data["Type"].unique()
    )

    date_range = st.date_input(
        "Select Date Range",
        [demand_data["Date"].min(), demand_data["Date"].max()]
    )

    section = st.radio("📂 Navigation", ["Demand Analysis", "Other Analysis"])

# --------- Filter Data ---------
filtered_data = demand_data[
    (demand_data["Region"].isin(region_filter)) &
    (demand_data["Capacity"].isin(capacity_filter)) &
    (demand_data["Type"].isin(type_filter)) &
    (demand_data["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
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
    col3.metric("Capacities", filtered_data["Capacity"].nunique())
    col4.metric("Types", filtered_data["Type"].nunique())

    st.markdown("---")

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
