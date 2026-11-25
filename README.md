
# 🧠 Medi-Mind AI
##
**Medi-Mind AI** is an intelligent web application that leverages Google's Generative AI (`gemini-1.5-flash-002`) to analyze medical images and provide structured diagnostic insights. Built with [Streamlit](https://streamlit.io), this app empowers medical professionals and patients with fast, AI-driven image analysis — while clearly stating its role as a supportive tool, not a replacement for clinical judgment.

---

## 🚀 Features

- 📷 **Medical Image Upload:** Upload medical images in `.png`, `.jpg`, or `.jpeg` formats.
- 🤖 **AI Analysis:** Analyze the uploaded image using Gemini's advanced vision-language capabilities.
- 📝 **Structured Report:** Get insights including:
  - Identified anomalies or diseases
  - Recommendations for follow-up tests or treatments
  - Suggested treatments if appropriate
- ⚠️ **Safety & Disclaimers:** Configured safety thresholds and explicit medical disclaimers to ensure ethical usage.

---

## 🏗️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io)
- **AI Backend:** Google Generative AI (`gemini-1.5-flash-002`)
- **Language:** Python 3.x
- **Image Input:** Base64 encoded via Streamlit uploader
- **Security:** Uses safety filters to block inappropriate or unsafe outputs

---

## 📂 Project Structure

```
medi-mind-ai/
│
├── images/
│   └── Logo.jpg              # App logo
│
├── api_key.py                # Contains your API key (excluded from version control)
├── app.py                    # Main Streamlit app file
└── README.md                 # Project documentation
```

---

## 🔐 Setup & Run Locally

1. **Clone the Repository**
```bash
git clone https://github.com/Shah621/MediMind-AI-Medical-Diagnosis-and-Precautions-by-LLM.git
cd medi-mind-ai
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Add API Key**
In `api_key.py` include the following field:
```python
api_key = "YOUR_API_KEY"
```

4. **Run the App**
```bash
streamlit run app.py
```

---

## ⚠️ Disclaimer

> This tool is intended for **informational and educational purposes only**. The AI-generated analysis should **not be used as a substitute for professional medical advice, diagnosis, or treatment**. Always consult a licensed medical professional before making any medical decisions.

---

## 📌 Future Improvements

- ✅ Drag-and-drop image upload
- ✅ Multi-image support
- 📊 Integration with patient databases for history-based context
- 🧪 Support for other diagnostic imaging types (X-ray, CT scan, MRI)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
