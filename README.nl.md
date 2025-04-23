📄 AI Document Samenvatter voor Gepersonaliseerde Beleggingscommunicatie  
Een Streamlit-webapplicatie in prototypevorm die financiële documenten samenvat op basis van gebruikersvoorkeuren, verrijkt met optionele context via RAG (Retrieval-Augmented Generation). Gebouwd met Anthropic Claude.

Nu met geïntegreerde chatbotfunctie om bijkomende vragen te stellen — in de communicatiestijl van de gekozen avatar.

---

🇧🇪 Over de maker  
Dit project werd ontwikkeld in België door Pieter De Knock, in het kader van een zelfstudietraject in Artificiële Intelligentie.  
Met meer dan 20 jaar ervaring in Asset Management, beleggingsstrategie en productcommunicatie is dit project een experiment om AI en finance op een zinvolle manier te combineren.

---
[🎥 Bekijk de demo](https://www.loom.com/share/059429e55c98405894d82d07c35771b6?sid=b2ea2b55-c120-4740-8cff-d980e54e4c16)

🚀 Belangrijkste functies
- 📥 Upload en combineer meerdere PDF- of Word-documenten  
- 🧑‍💼 Kies je gewenste stijl, toon, formaliteit, sector en risicoprofiel  
- 🧠 Gebruik avatars om de communicatiestijl te personaliseren (bv. Erin voor beeldrijke metaforen)  
- 🔍 Verwerk optioneel een kennisbank (RAG) voor extra context  
- 💬 **Chat met het document**: stel bijkomende vragen en krijg antwoorden in de stijl van je gekozen avatar  
- 🛡️ Ingebouwde veiligheid: validatie van antwoorden om advies of speculatie te vermijden  
- 📤 Download de samenvatting als PDF of Word  
- 💬 Feedbackmechanisme om de tool verder te verbeteren

---

⚙️ Technologie
- Streamlit – Webframework  
- Anthropic Claude API – Taalmodel  
- FAISS – Vector search voor RAG  
- Python, Pandas, dotenv, ReportLab, python-docx, enz.

---

🛠 Installatie

```bash
git clone https://github.com/pieterdeknock/AI-Document-Summarizer.git
cd AI-Document-Summarizer
python -m venv venv
source venv/bin/activate        # Op Windows: venv\Scripts\activate
pip install -r requirements.txt


