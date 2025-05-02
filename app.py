import streamlit as st
from pathlib import Path
import google.generativeai as genai
from api_key import api_key

#configuring API
client = genai.configure(api_key=api_key)
# Setting the model
generation_config = {
    'temperature': 0.4,
    'top_p': 1,
    'top_k': 32,
    # 'max_output_token': 4096,
}
# Applying safety settings
safety_settings = [
{ 
"category": "HARM_CATEGORY_HARASSMENT", 
"threshold": "BLOCK_MEDIUM_AND_ABOVE" 
}, 
{ 
"category": "HARM_CATEGORY_HATE_SPEECH", 
"threshold": "BLOCK_MEDIUM_AND_ABOVE" 
}, 
{ 
"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", 
"threshold": "BLOCK_MEDIUM_AND_ABOVE" 
}, 
{  
"category": "HARM_CATEGORY_DANGEROUS_CONTENT", 
"threshold": "BLOCK_MEDIUM_AND_ABOVE" 
},
]


# system_prompt = "Could you summarize the medical image and give precaution to the patient as a medical specialist?"

system_prompt = """
As a highly skilled medical practitioner specializing in image analysis you are tasked with examining medical images for a renowned hospital your expertise is crucial in identifying any anomalies diseases or health issues that may be present in the image.

Your Responsibilities includes:

1. Detailed analysis: Thoroughly analyze each image focusing on identifying any abnormal findings.
2. Findings report: Document all observed anomalies or signs of diseases clearly articulate these findings in a structured format.
3. Recommendations and next steps: Based on your analysis suggest potential next steps including further tests or treatments as applicable.
4. Treatment suggestions: if appropriate recommend possible treatment options or interventions.

Important Notes:

1. Scope of response: Only respond if the image pertains to human health issues.
2. Clarity of images: In cases where the image quality impedes clear analysis, note that certain aspects are "Unable to be determined based on provided image."
3. Disclaimer: Accompany your analysis with a disclaimer okay "Consult a doctor before making any decisions."
4. Your insights are valuable in guiding clinical decisions please proceed with the analysis adhering to the structure approach outline above.
"""




# Model configuration
model= genai.GenerativeModel(model_name="gemini-1.5-flash-002",
                             generation_config=generation_config,
                             safety_settings=safety_settings)


st.set_page_config(page_title="Image Analytics", page_icon=':robot:')

st.image('./images/Logo.jpg', width=180)

st.title("Medi-Mind AI")

upload_file = st.file_uploader("Upload Medical Image for Analysis", type=['png','jpg','jpeg'])

submit_button = st.button('Analyze')

if submit_button and upload_file is not None:
    image_data = upload_file.getvalue()

    image_part = [
        {
        'mime_type':'image/jpeg',
        'data': image_data
        },
    ]

    prompt_part = [
        image_part[0],
        system_prompt
    ]

    st.image(image_data, width=300)
    # generating response from prompt and image input
    response = model.generate_content(prompt_part)

    st.write(response.text)