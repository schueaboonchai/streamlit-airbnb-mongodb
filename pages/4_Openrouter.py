from openai import OpenAI
import streamlit as st

st.title("Chat with AI.")
@st.cache_resource
def init_connection():
    api = st.secrets["openrouter"]["api"]
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api,
        )

client = init_connection()

p = st.text_input("Your prompt here","")

if st.button("Press here"):
    completion = client.chat.completions.create(
      extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-OpenRouter-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
      },
      extra_body={},
      model="liquid/lfm-2.5-1.2b-instruct:free",
      messages=[
        {
          "role": "user",
          "content": "What is the meaning of life?"
        }
      ]
    )
    
    st.write(completion.choices[0].message.content)