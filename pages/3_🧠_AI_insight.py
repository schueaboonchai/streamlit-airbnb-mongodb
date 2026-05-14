import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from transformers import pipeline
import random

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Airbnb Insights",
    page_icon="🧠",
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
# LOAD MODEL
# =====================================================

@st.cache_resource
def load_model():

    return pipeline(
        "text-classification",
        model="tabularisai/multilingual-sentiment-analysis"
    )

model = load_model()

# =====================================================
# LOAD DATA
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
            "summary": 1,
            "description": 1,
            "space": 1,
            "price": 1,
            "room_type": 1,
            "property_type": 1,
            "review_scores": 1,
            "address": 1
        }
    ))

    return pd.DataFrame(data)

df = load_data()

# =====================================================
# CLEAN DATA
# =====================================================

df["price"] = df["price"].apply(
    lambda x: float(x.to_decimal())
    if hasattr(x, "to_decimal")
    else x
)

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)

df = df.dropna(subset=["price"])

# =====================================================
# EXTRACT FIELDS
# =====================================================

df["country"] = df["address"].apply(
    lambda x: x.get("country", "Unknown")
)

df["review_score"] = df["review_scores"].apply(
    lambda x: x.get("review_scores_rating")
    if isinstance(x, dict) else None
)

# =====================================================
# TITLE
# =====================================================

st.title("🧠 AI Airbnb Insights")

st.write("""
This AI dashboard analyzes Airbnb property descriptions using NLP (Natural Language Processing).

The AI model can:

- Analyze sentiment from Airbnb descriptions
- Predict customer impressions
- Generate executive-level insights
- Detect emotional marketing language
- Recommend listing improvements
- Compare pricing with market averages
""")

st.markdown("---")

# =====================================================
# FILTER SECTION
# =====================================================

st.subheader("🌍 Search & Filter")

filter_col1, filter_col2 = st.columns([1, 2])

# =====================================================
# COUNTRY FILTER
# =====================================================

country_list = sorted(
    df["country"].dropna().unique()
)

country_options = ["All Countries"] + country_list

selected_country = filter_col1.selectbox(
    "Select Country",
    country_options
)

# =====================================================
# APPLY COUNTRY FILTER
# =====================================================

filtered_df = df.copy()

if selected_country != "All Countries":

    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

# =====================================================
# SEARCHABLE LISTING DROPDOWN
# =====================================================

listing_names = sorted(
    filtered_df["name"]
    .dropna()
    .unique()
)

selected_listing = filter_col2.selectbox(
    "🔎 Search Airbnb Listing",
    listing_names
)

# =====================================================
# SELECTED ROW
# =====================================================

selected_df = filtered_df[
    filtered_df["name"] == selected_listing
].iloc[0]

# =====================================================
# PROPERTY OVERVIEW
# =====================================================

st.markdown("---")

st.subheader("🏠 Property Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Property Type",
    selected_df["property_type"]
)

col2.metric(
    "Room Type",
    selected_df["room_type"]
)

col3.metric(
    "Price",
    f"${round(selected_df['price'],2)}"
)

review_value = (
    round(selected_df["review_score"],1)
    if pd.notnull(selected_df["review_score"])
    else "N/A"
)

col4.metric(
    "Review Score",
    review_value
)

# =====================================================
# DESCRIPTION
# =====================================================

st.markdown("---")

st.subheader("📄 Property Description")

description = ""

if pd.notnull(selected_df.get("summary")):
    description += str(selected_df["summary"]) + "\n\n"

if pd.notnull(selected_df.get("space")):
    description += str(selected_df["space"]) + "\n\n"

if pd.notnull(selected_df.get("description")):
    description += str(selected_df["description"])

if description.strip() == "":
    description = "No description available."

st.write(description)

# =====================================================
# AI ANALYSIS
# =====================================================

st.markdown("---")

st.header("🤖 AI Sentiment Analysis")

if st.button("Analyze Listing"):

    with st.spinner("AI is analyzing property description..."):

        short_text = description[:1200]

        result = model(short_text)[0]

        label = result["label"]
        score = result["score"]

    # =================================================
    # AI RESULT
    # =================================================

    st.subheader("📌 AI Prediction")

    result_col1, result_col2 = st.columns(2)

    with result_col1:

        if "positive" in label.lower():

            st.success(f"""
            Positive Sentiment Detected ✅

            Confidence Score: {round(score * 100,2)}%
            """)

        elif "negative" in label.lower():

            st.error(f"""
            Negative Sentiment Detected ❌

            Confidence Score: {round(score * 100,2)}%
            """)

        else:

            st.warning(f"""
            Neutral Sentiment Detected ⚠️

            Confidence Score: {round(score * 100,2)}%
            """)

    # =================================================
    # EXECUTIVE INSIGHT
    # =================================================

    with result_col2:

        st.info("""
        🧠 Executive Insight

        AI detected emotional tone from the listing description.

        Listings with positive wording often:
        - attract more bookings
        - improve customer trust
        - support premium pricing
        - receive stronger reviews

        High-quality descriptions improve Airbnb conversion rates.
        """)

    # =================================================
    # AI RECOMMENDATIONS
    # =================================================

    st.markdown("---")

    st.subheader("💡 AI Recommendations")

    recommendations = []

    if selected_df["price"] > 400:

        recommendations.append(
            "High pricing detected. Consider emphasizing luxury amenities and premium experiences."
        )

    if selected_df["room_type"] == "Entire home/apt":

        recommendations.append(
            "Entire home listings generally perform well for families and long stays."
        )

    if pd.notnull(selected_df["review_score"]):

        if selected_df["review_score"] < 80:

            recommendations.append(
                "Low review score detected. Improving cleanliness and communication may increase guest satisfaction."
            )

        else:

            recommendations.append(
                "Strong review score detected. This property has positive customer satisfaction."
            )

    keywords = [
        "luxury",
        "beautiful",
        "spacious",
        "comfortable",
        "modern"
    ]

    positive_keywords = [
        word for word in keywords
        if word.lower() in description.lower()
    ]

    if len(positive_keywords) > 0:

        recommendations.append(
            f"Positive marketing keywords detected: {', '.join(positive_keywords)}"
        )

    else:

        recommendations.append(
            "Consider adding stronger emotional keywords to improve listing attractiveness."
        )

    for rec in recommendations:

        st.write(f"• {rec}")

    # =================================================
    # AI SCORE
    # =================================================

    st.markdown("---")

    st.subheader("⭐ AI Listing Quality Score")

    ai_score = 0

    if pd.notnull(selected_df["review_score"]):

        ai_score += selected_df["review_score"] * 0.5

    ai_score += score * 50

    ai_score += min(len(description) / 100, 20)

    ai_score = round(min(ai_score, 100), 1)

    st.progress(ai_score / 100)

    st.metric(
        "AI Listing Score",
        f"{ai_score}/100"
    )

    # =================================================
    # MARKET COMPARISON
    # =================================================

    st.markdown("---")

    st.subheader("📊 Market Comparison")

    country_df = df[
        df["country"] == selected_df["country"]
    ]

    avg_country_price = round(
        country_df["price"].mean(),
        2
    )

    compare_col1, compare_col2 = st.columns(2)

    compare_col1.metric(
        "Selected Property Price",
        f"${round(selected_df['price'],2)}"
    )

    compare_col2.metric(
        "Average Country Price",
        f"${avg_country_price}"
    )

    if selected_df["price"] > avg_country_price:

        st.warning("""
        This property is priced ABOVE the country average.
        """)

    else:

        st.success("""
        This property is priced BELOW the country average.
        """)

# =====================================================
# CUSTOM TEXT ANALYSIS
# =====================================================

st.markdown("---")

st.header("✍️ Analyze Your Own Text")

custom_text = st.text_area(
    "Enter any Airbnb review or description"
)

if st.button("Run Custom AI Analysis"):

    if custom_text.strip() != "":

        result = model(custom_text)[0]

        label = result["label"]

        score = result["score"]

        st.subheader("📌 AI Result")

        st.write(f"Sentiment: {label}")

        st.write(f"Confidence: {round(score * 100,2)}%")

        if "positive" in label.lower():

            st.success("""
            Positive language detected.
            This text sounds attractive and customer-friendly.
            """)

        elif "negative" in label.lower():

            st.error("""
            Negative language detected.
            Consider improving wording and emotional tone.
            """)

        else:

            st.warning("""
            Neutral language detected.
            Consider adding more emotional and descriptive wording.
            """)

# =====================================================
# BONUS INSIGHTS
# =====================================================

st.markdown("---")

st.header("🔥 AI Smart Insights")

insight_examples = [

    "Listings with emotional wording usually achieve higher engagement.",

    "Properties described as 'spacious' and 'comfortable' often receive stronger reviews.",

    "High review scores strongly correlate with repeat bookings.",

    "Luxury keywords may support higher pricing strategies.",

    "Detailed descriptions improve customer trust and booking conversion."
]

random_insight = random.choice(insight_examples)

st.info(random_insight)

# =====================================================
# VISUALIZATION
# =====================================================

st.markdown("---")

st.header("📈 AI Data Visualization")

chart_df = df.dropna(
    subset=["review_score"]
)

fig = px.scatter(
    chart_df,
    x="review_score",
    y="price",
    color="room_type",
    hover_data=["name"],
    title="Review Score vs Price"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "AI Airbnb Insights • Streamlit + MongoDB Atlas + HuggingFace Transformers"
)