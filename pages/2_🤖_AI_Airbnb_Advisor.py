import streamlit as st
from pymongo import MongoClient
from openai import OpenAI
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Airbnb Advisor",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# OPENROUTER
# =====================================================

@st.cache_resource
def init_ai():

    api = st.secrets["openrouter"]["api"]

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api
    )

    return client

client_ai = init_ai()

MODEL_NAME = "deepseek/deepseek-v4-flash:free"

# =====================================================
# MONGODB
# =====================================================

@st.cache_resource
def init_connection():

    uri = st.secrets["mongo"]["uri"]

    return MongoClient(uri)

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
            "property_type": 1,
            "room_type": 1,
            "address": 1,
            "review_scores": 1
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

st.title("🤖 AI Airbnb Advisor")

st.write(f"""
This page uses OpenRouter API with:

✅ Model: `{MODEL_NAME}`  
✅ Free LLM Model  
✅ AI-powered Airbnb analytics and recommendations
""")

st.markdown("---")

# =====================================================
# FILTER
# =====================================================

country_options = ["All"] + sorted(
    df["country"].dropna().unique()
)

selected_country = st.selectbox(
    "🌍 Filter Country",
    country_options
)

filtered_df = df.copy()

if selected_country != "All":

    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

# =====================================================
# SELECT LISTING
# =====================================================

listing_names = sorted(
    filtered_df["name"].dropna().unique()
)

selected_listing = st.selectbox(
    "🏠 Select Airbnb Listing",
    listing_names
)

selected_df = filtered_df[
    filtered_df["name"] == selected_listing
].iloc[0]

# =====================================================
# PROPERTY INFO
# =====================================================

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

review = (
    round(selected_df["review_score"],1)
    if pd.notnull(selected_df["review_score"])
    else "N/A"
)

col4.metric(
    "Review Score",
    review
)

# =====================================================
# DESCRIPTION
# =====================================================

description = ""

if pd.notnull(selected_df.get("summary")):
    description += str(selected_df["summary"]) + "\n\n"

if pd.notnull(selected_df.get("space")):
    description += str(selected_df["space"]) + "\n\n"

if pd.notnull(selected_df.get("description")):
    description += str(selected_df["description"])

if description.strip() == "":
    description = "No description available."

st.markdown("---")

st.subheader("📄 Listing Description")

st.write(description)

# =====================================================
# AI ANALYSIS
# =====================================================

st.markdown("---")

if st.button("🚀 Generate AI Executive Analysis"):

    with st.spinner("AI is analyzing this property..."):

        prompt = f"""
        You are an Airbnb business consultant.

        Analyze this Airbnb listing.

        Property Name:
        {selected_listing}

        Property Type:
        {selected_df['property_type']}

        Room Type:
        {selected_df['room_type']}

        Price:
        {selected_df['price']}

        Review Score:
        {selected_df['review_score']}

        Description:
        {description}

        Please provide:

        1. Executive Summary
        2. Target Customer
        3. Pricing Strategy
        4. Listing Strengths
        5. Weaknesses
        6. Marketing Recommendations
        7. Suggested Improvements
        """

        completion = client_ai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response = completion.choices[0].message.content

    st.subheader("🧠 AI Executive Analysis")

    st.write(response)

# =====================================================
# CUSTOM AI CHAT
# =====================================================

st.markdown("---")

st.header("💬 Ask AI About Airbnb")

user_prompt = st.text_area(
    "Ask anything about Airbnb analytics, pricing, or travel"
)

if st.button("Ask AI"):

    with st.spinner("Thinking..."):

        completion = client_ai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        answer = completion.choices[0].message.content

    st.write(answer)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "AI Airbnb Advisor • OpenRouter + DeepSeek V4 Flash Free"
)