
# 📄 AI Document Summarizer for Personalized Investment Communication

**A prototype Streamlit web app that summarizes financial documents based on user preferences, enriched with optional contextual knowledge via RAG. Built using Anthropic Claude.**

---

## 🇧🇪 About the Creator

This project was developed in Belgium by Pieter De Knock as part of a self-study trajectory in Artificial Intelligence.  
With 20+ years of experience in **Asset Management**, **Investment Strategy**, and **Product Communication**, this tool is an experiment to combine **AI** and **finance** into a meaningful application.

---

🚀 Key Features
- 📥 Upload and combine multiple PDF or Word documents  
- 🧑‍💼 Choose your preferred style, tone, formality, industry, and risk profile  
- 🧠 Use avatars to personalize the communication style (e.g. Erin for metaphor-rich storytelling)  
- 🔍 Integrate a Retrieval-Augmented Generation (RAG) knowledge base for deeper context  
- 💬 Chat: Ask follow-up questions and get answers in your selected avatar’s tone  
- 🛡️ Guardrails and validation: Responses are checked to avoid speculation or advice  
- 📤 Download the summary as PDF or Word  
- 💬 Built-in feedback capture for user evaluation  

---

## ⚙️ Tech Stack

- [Streamlit](https://streamlit.io/) – Web app framework  
- [Anthropic Claude API](https://www.anthropic.com/) – Language model  
- [FAISS](https://github.com/facebookresearch/faiss) – Vector search for RAG  
- Python, Pandas, dotenv, ReportLab, docx, etc.

---

## 🛠 Installation

```bash
git clone https://github.com/pieterdeknock/AI-Document-Summarizer.git
cd AI-Document-Summarizer
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your Claude API key in a `.env` file:

```
ANTHROPIC_API_KEY=your_api_key_here
```

---

## ▶️ Run Locally

```bash
streamlit run app/app.py
```

App runs at `http://localhost:8501`

---

## 🧠 Optional: RAG Knowledge Base

The app supports a simple vector database (FAISS) to enhance summarization with contextual data:

- Add definitions, FAQs, product info, regulations…
- Use `data/populate_kb.py` to load structured `.csv` files
- Results are filtered and matched dynamically during summarization

---

## 🧪 Status & Roadmap

✅ Functional prototype  
🚧 Layout, UX and knowledge base still under development  
📌 Future ideas include chatbot integration, API endpoint version, or multi-user setup

---

## 🔒 Disclaimer

This app is an **educational and experimental prototype**.  
It is **not intended as financial advice** or a commercial tool.

---

## 📫 Contact

Feel free to connect or follow my journey:

- 🔗 [LinkedIn – Pieter De Knock](https://www.linkedin.com/in/pieterdeknock)  
- 🌍 [oudeschoolkaarten.be](https://www.oudeschoolkaarten.be)

---
🇳🇱 Op zoek naar de Nederlandstalige versie?  
Bekijk [README.nl.md](README.nl.md)

---

💬 _Exploring AI in financial wellbeing, education or communication? I'd love to exchange ideas._
