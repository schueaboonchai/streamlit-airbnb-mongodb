import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide"
)

# =====================================================
# CACHE CONNECTION
# =====================================================

@st.cache_resource
def init_connection():

    uri = st.secrets["mongo"]["uri"]

    client = MongoClient(uri)

    return client

# =====================================================
# CACHE DATA
# =====================================================

@st.cache_data
def load_data():

    client = init_connection()

    db = client["sample_airbnb"]

    collection = db["listingsAndReviews"]

    data = list(collection.find(
        {},
        {
            "name": 1,
            "price": 1,
            "room_type": 1,
            "property_type": 1,
            "bed_type": 1,
            "accommodates": 1,
            "bathrooms": 1,
            "bedrooms": 1,
            "beds": 1,
            "minimum_nights": 1,
            "maximum_nights": 1,
            "address": 1,
            "host": 1,
            "review_scores": 1,
            "availability": 1
        }
    ))

    return pd.DataFrame(data)

# =====================================================
# LOAD DATA
# =====================================================

df = load_data()

# =====================================================
# CLEAN DATA
# =====================================================

numeric_columns = [
    "price",
    "bathrooms",
    "bedrooms",
    "beds",
    "accommodates",
    "minimum_nights",
    "maximum_nights"
]

# Convert Decimal128 -> float

for col in numeric_columns:

    df[col] = df[col].apply(
        lambda x: float(x.to_decimal())
        if hasattr(x, "to_decimal")
        else x
    )

# Convert safely

df[numeric_columns] = df[numeric_columns].apply(
    pd.to_numeric,
    errors="coerce"
)

# Fill missing values

df["bathrooms"] = df["bathrooms"].fillna(1)
df["bedrooms"] = df["bedrooms"].fillna(1)
df["beds"] = df["beds"].fillna(1)

# Remove missing price

df = df.dropna(subset=["price"])

# Remove outliers

df = df[df["price"] < 1000]

# =====================================================
# EXTRACT NESTED FIELDS
# =====================================================

df["country"] = df["address"].apply(
    lambda x: x.get("country", "Unknown")
)

df["market"] = df["address"].apply(
    lambda x: x.get("market", "Unknown")
)

df["street"] = df["address"].apply(
    lambda x: x.get("street", "Unknown")
)

df["host_name"] = df["host"].apply(
    lambda x: x.get("host_name", "Unknown")
    if isinstance(x, dict) else "Unknown"
)

df["review_score"] = df["review_scores"].apply(
    lambda x: x.get("review_scores_rating")
    if isinstance(x, dict) else None
)

df["availability_365"] = df["availability"].apply(
    lambda x: x.get("availability_365")
    if isinstance(x, dict) else None
)

# =====================================================
# DASHBOARD TITLE
# =====================================================

st.title("🏠 Airbnb Analytics Dashboard")

st.write("""
Interactive dashboard built with:

- Streamlit
- MongoDB Atlas
- Plotly Express
- sample_airbnb dataset
""")

st.markdown("---")

# =====================================================
# FILTER SECTION
# =====================================================

st.subheader("🌍 Dashboard Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

# Country Filter

country_list = sorted(df["country"].unique())

country_options = ["All"] + country_list

selected_country = filter_col1.selectbox(
    "Select Country",
    country_options
)

# Room Type Filter

room_list = sorted(df["room_type"].dropna().unique())

room_options = ["All"] + room_list

selected_room = filter_col2.selectbox(
    "Select Room Type",
    room_options
)

# Property Type Filter

property_list = sorted(
    df["property_type"].dropna().unique()
)

property_options = ["All"] + property_list

selected_property = filter_col3.selectbox(
    "Select Property Type",
    property_options
)

# Price Slider

min_price = int(df["price"].min())

max_price = int(df["price"].max())

price_range = st.slider(
    "Select Price Range",
    min_price,
    max_price,
    (50, 500)
)

# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = df.copy()

if selected_country != "All":

    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

if selected_room != "All":

    filtered_df = filtered_df[
        filtered_df["room_type"] == selected_room
    ]

if selected_property != "All":

    filtered_df = filtered_df[
        filtered_df["property_type"] == selected_property
    ]

filtered_df = filtered_df[
    (filtered_df["price"] >= price_range[0]) &
    (filtered_df["price"] <= price_range[1])
]

st.markdown("---")

# =====================================================
# KPI METRICS
# =====================================================

st.subheader("📌 KPI Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Listings",
    len(filtered_df)
)

col2.metric(
    "Average Price",
    f"${round(filtered_df['price'].mean(), 2)}"
)

col3.metric(
    "Maximum Price",
    f"${round(filtered_df['price'].max(), 2)}"
)

col4.metric(
    "Average Review",
    round(filtered_df["review_score"].mean(), 1)
)

st.markdown("---")

# =====================================================
# INSIGHTS
# =====================================================

most_common_room = (
    filtered_df["room_type"]
    .mode()[0]
)

avg_guest = round(
    filtered_df["accommodates"].mean(),
    1
)

st.info(f"""
📌 Dashboard Insights

• Most common room type: {most_common_room}

• Average accommodates: {avg_guest} guests

• Listings with higher accommodates usually have higher prices

• Dataset contains properties from multiple countries
""")

# =====================================================
# DATA PREVIEW
# =====================================================

st.subheader("📄 Airbnb Listings Preview")

preview_columns = [
    "name",
    "property_type",
    "room_type",
    "bed_type",
    "accommodates",
    "bedrooms",
    "beds",
    "bathrooms",
    "price",
    "minimum_nights",
    "maximum_nights",
    "country",
    "market",
    "street",
    "host_name",
    "review_score"
]

# Default Preview

st.dataframe(
    filtered_df[preview_columns].head(20),
    use_container_width=True
)

# =====================================================
# TOGGLE FULL DATA
# =====================================================

show_all_data = st.toggle(
    "Show Full Dataset"
)

if show_all_data:

    st.markdown("### 📂 Full Airbnb Dataset")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# =====================================================
# CHARTS SECTION
# =====================================================

st.markdown("---")

st.header("📊 Data Visualization")

chart_col1, chart_col2 = st.columns(2)

# Histogram

with chart_col1:

    fig1 = px.histogram(
        filtered_df,
        x="price",
        nbins=30,
        color="room_type",
        title="Price Distribution"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# Scatter Plot

with chart_col2:

    scatter_df = filtered_df.dropna(
        subset=[
            "accommodates",
            "price",
            "bathrooms"
        ]
    )

    fig2 = px.scatter(
        scatter_df,
        x="accommodates",
        y="price",
        color="room_type",
        size="bathrooms",
        hover_data=["name"],
        title="Price vs Accommodates"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =====================================================
# SECOND ROW
# =====================================================

chart_col3, chart_col4 = st.columns(2)

# Bar Chart

with chart_col3:

    property_count = (
        filtered_df["property_type"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    property_count.columns = [
        "Property Type",
        "Count"
    ]

    fig3 = px.bar(
        property_count,
        x="Property Type",
        y="Count",
        color="Count",
        title="Top Property Types"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# Pie Chart

with chart_col4:

    room_count = (
        filtered_df["room_type"]
        .value_counts()
        .reset_index()
    )

    room_count.columns = [
        "Room Type",
        "Count"
    ]

    fig4 = px.pie(
        room_count,
        names="Room Type",
        values="Count",
        title="Room Type Distribution"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# =====================================================
# BOX PLOT
# =====================================================

st.markdown("---")

fig5 = px.box(
    filtered_df,
    x="room_type",
    y="price",
    color="room_type",
    title="Room Type vs Price"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# =====================================================
# TOP 10
# =====================================================

st.markdown("---")

st.subheader("💎 Top 10 Most Expensive Listings")

top10 = filtered_df.sort_values(
    by="price",
    ascending=False
)[
    [
        "name",
        "price",
        "property_type",
        "room_type",
        "country",
        "market"
    ]
].head(10)

st.dataframe(
    top10,
    use_container_width=True
)

# =====================================================
# MAP SECTION
# =====================================================

st.markdown("---")

st.header("🗺️ Airbnb Listings Map")

filtered_df["longitude"] = filtered_df["address"].apply(
    lambda x: x["location"]["coordinates"][0]
    if "location" in x else None
)

filtered_df["latitude"] = filtered_df["address"].apply(
    lambda x: x["location"]["coordinates"][1]
    if "location" in x else None
)

map_df = filtered_df.dropna(
    subset=["latitude", "longitude"]
)

fig6 = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    color="price",
    size="price",
    hover_name="name",
    hover_data=[
        "property_type",
        "room_type",
        "price"
    ],
    zoom=2,
    height=700,
    title="Airbnb Property Locations"
)

fig6.update_layout(
    mapbox_style="open-street-map"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# =====================================================
# DOWNLOAD CSV
# =====================================================

st.markdown("---")

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="airbnb_filtered_data.csv",
    mime="text/csv"
)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "Created with Streamlit + MongoDB Atlas + Plotly Express 🚀"
)