import streamlit as st

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Airbnb Analytics Platform",
    page_icon="🏠",
    layout="wide"
)

# =====================================================
# HERO SECTION
# =====================================================

st.title("🏠 Airbnb Analytics Platform")

st.write("""
Interactive Airbnb analytics platform powered by:

- MongoDB Atlas
- Streamlit
- Plotly
- OpenRouter AI
""")

st.markdown("---")

# =====================================================
# OVERVIEW
# =====================================================

st.subheader("📌 Project Overview")

st.write("""
This project analyzes Airbnb listings from the MongoDB Atlas
`sample_airbnb` dataset.

The platform combines:

✅ Interactive dashboard analytics  
✅ Data visualization  
✅ AI-generated business insights  
✅ Executive recommendation systems  
✅ Natural language AI analysis
""")

# =====================================================
# FEATURES
# =====================================================

st.subheader("🚀 Platform Features")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:

    st.markdown("""
    ### 📊 Analytics Dashboard

    - KPI Metrics
    - Price Distribution
    - Property Insights
    - Country Filters
    - Interactive Charts
    - Geographic Map Visualization
    - CSV Export
    """)

with feature_col2:

    st.markdown("""
    ### 🤖 AI Airbnb Advisor

    - AI Executive Analysis
    - Pricing Recommendations
    - Listing Evaluation
    - Marketing Suggestions
    - Customer Targeting
    - Airbnb Strategy Assistant
    """)

# =====================================================
# TECHNOLOGIES
# =====================================================

st.markdown("---")

st.subheader("🛠️ Technologies Used")

tech1, tech2, tech3 = st.columns(3)

with tech1:

    st.info("""
    ### Frontend

    - Streamlit
    - Plotly Express
    - Python
    """)

with tech2:

    st.info("""
    ### Database

    - MongoDB Atlas
    - PyMongo
    - sample_airbnb
    """)

with tech3:

    st.info("""
    ### Artificial Intelligence

    - OpenRouter API
    - DeepSeek V4 Flash
    - Free LLM Model
    """)

# =====================================================
# AI MODEL
# =====================================================

st.markdown("---")

st.subheader("🧠 AI Model Information")

st.success("""
Current AI Provider: OpenRouter

Model Used:
deepseek/deepseek-v4-flash:free

Purpose:
- Airbnb listing analysis
- Executive insight generation
- AI recommendation engine
- Pricing and marketing strategy
""")

# =====================================================
# DATASET
# =====================================================

st.markdown("---")

st.subheader("📂 Dataset Information")

st.write("""
Dataset Source:
MongoDB Atlas → `sample_airbnb`

Included Data:
- Listing name
- Property type
- Room type
- Prices
- Reviews
- Locations
- Availability
- Host information
""")

# =====================================================
# APPLICATION PAGES
# =====================================================

st.markdown("---")

st.subheader("📄 Application Pages")

page1, page2 = st.columns(2)

with page1:

    st.markdown("""
    ### 📊 Dashboard Page

    Explore Airbnb data through:
    - Interactive charts
    - Filters
    - Maps
    - KPI metrics
    """)

with page2:

    st.markdown("""
    ### 🤖 AI Advisor Page

    Generate:
    - AI executive summaries
    - Pricing recommendations
    - Marketing analysis
    - Listing improvement suggestions
    """)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "Airbnb Analytics Platform • Streamlit + MongoDB Atlas + OpenRouter AI 🚀"
)