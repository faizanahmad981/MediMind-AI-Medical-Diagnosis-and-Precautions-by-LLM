import streamlit as st
import os
from google import genai
from google.generativeai import genai
from api_key import api_key

client = genai.Client(api_key=api_key)

st.set_page_config(page_title="Image Analytics", page_icon=':robot:')

st.image('./images/Logo.jpg', width=180)

st.title("Medi-Mind AI")

upload_file = st.file_uploader("Upload Medical Image for Analysis", type=['png','jpg','jpeg'])

prompt = "Could you summarize the medical image and give precaution to the patient as a medical specialist?"

submit_button = st.button('Analyze')

if submit_button and upload_file is not None:
    pass