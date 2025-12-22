import streamlit as st
import os
import requests
import json
import base64
from PIL import Image
from dotenv import load_dotenv

# NEW: Import functions from your database.py file
from database import init_db, save_analysis, get_all_history

load_dotenv()

# Initialize the DB at startup
init_db()

# 1. Setup Configuration
api_key = os.environ.get('OPENROUTER_API_KEY')
if not api_key:
    st.error("Please set the OPENROUTER_API_KEY environment variable.")
    st.stop()

# Define your OpenRouter model
MODEL_ID = "google/gemini-2.0-flash-001" 

def encode_image(image_file):
    """Convert the uploaded file to a base64 string."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# 2. OpenRouter Generation Function
def generate_content(image_file, prompt=None):
    try:
        base64_image = encode_image(image_file)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501", 
            "X-Title": "Streamlit Analyzer",
        }

        payload = {
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt if prompt else "Describe this image."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error during generation: {str(e)}"

# 3. Streamlit Interface
st.set_page_config(
    page_title="OpenRouter Vision",
    page_icon="🚀",
    layout="wide"
)

st.sidebar.title("Configuration")
st.sidebar.info(f"Model: {MODEL_ID}")

st.title("🚀 OpenRouter Image Analyzer")
st.write("Upload an image and ask any AI model via OpenRouter.")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_image is not None:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

    with col2:
        prompt = st.text_input("What would you like to know?", "Describe this image in detail.")
        
        if st.button("Generate Content", type="primary"):
            with st.spinner(f"Analyzing with {MODEL_ID}..."):
                generated_text = generate_content(uploaded_image, prompt)
                
                # NEW: Save the result to SQLite database if generation didn't error out
                if not generated_text.startswith("Error:"):
                    save_analysis(prompt, generated_text)
                    st.success("Analysis Complete and Saved to Database!")
                else:
                    st.error("Analysis failed. Not saved.")
                
            st.markdown("### Result")
            st.write(generated_text)

# --- NEW: History Section ---
st.divider()
st.subheader("📜 Analysis History")

if st.checkbox("Show History"):
    history_data = get_all_history()
    if history_data:
        # We use a dataframe for a cleaner look
        import pandas as pd
        df = pd.DataFrame(history_data, columns=["ID", "Timestamp", "Prompt", "Result"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No history found in database.")