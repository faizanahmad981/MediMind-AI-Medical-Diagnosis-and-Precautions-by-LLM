import streamlit as st
import base64
from pathlib import Path
from google import genai
from api_key import api_key

client = genai.Client(api_key=api_key)


st.set_page_config(page_title="Image Analytics", page_icon=':robot:')

st.image('./images/Logo.jpg', width=180)

st.title("Medi-Mind AI")

upload_file = st.file_uploader("Upload Medical Image for Analysis", type=['png','jpg','jpeg'])

prompt = "Could you summarize the medical image and give precaution to the patient as a medical specialist?"

# print(response.text)


submit_button = st.button('Analyze')

if submit_button:

    # file = client.files.upload(file='a11.txt')
    image_data = upload_file.getvalue()

    image_part = [
        {
        'mime_type':'image/jpeg',
        'data': image_data
        },
    ]

    prompt_part = [
        image_part[0],
        prompt
    ]

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=[prompt_part]
    )
    st.write(response.text)
    # pass