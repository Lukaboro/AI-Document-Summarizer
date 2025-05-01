# data/question_classifier.py

import anthropic
import json

def classificeer_vraag_met_llm(vraag: str, api_key: str = None) -> tuple[str, str]:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    """
    Gebruikt Claude om te bepalen:
    - welk pensioengegeven bedoeld wordt (veld)
    - welke analysevorm hoort bij de vraag
    """

    prompt = f"""
Je helpt een applicatie bij het interpreteren van gebruikersvragen over pensioenspaarproducten.

De gebruiker stelt de volgende vraag:
"{vraag}"

Bepaal:
1. Welk veld in de dataset bedoeld wordt.
2. Welke berekening of selectie het best past bij de vraag.

Kies de berekening uit deze lijst:
- "min" → Laagste waarde
- "max" → Hoogste waarde
- "average" → Gemiddelde
- "top_3" → Top 3 laagste
- "top_5" → Top 5 laagste
- "top_rendement_bij_lage_kost" → Beste rendement bij 0% instapkosten
- "top_duurzaam" → Beste waarde bij duurzame fondsen
- "none" → Geen berekening nodig

Kies het veld uit deze lijst (exact zoals geschreven):
- "instapkosten"
- "lopende kosten min"
- "lopende kosten max"
- "rendement_5jaar"
- "rendement_10jaar"
- "rendement_20jaar"
- "duurzaam"

Geef je antwoord als exact JSON-object met deze structuur:
{{
  "veld": "...",
  "berekening": "..."
}}

Gebruik geen extra uitleg.
"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            temperature=0.0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        content = response.content[0].text
        parsed = json.loads(content)
        veld = parsed.get("veld", "").strip()
        berekening = parsed.get("berekening", "").strip()
        return veld, berekening

    except Exception as e:
        print(f"Fout bij classificatie van vraag: {e}")
        return "", "none"
