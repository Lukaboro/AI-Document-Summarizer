import os
import sys
import json
import logging
from pathlib import Path

# Configureer logging
logging.basicConfig(
    filename='rag_retrieval.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Zorg dat Python ook de rootmap kan vinden
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.vector_store import VectorStore
from data.knowledge_base import get_knowledge_item

# ===== PENSIOENINTEGRATIE =====
PENSION_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pensioenspaardata.json')

def load_pension_data():
    try:
        with open(PENSION_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"⚠️ Pensioenspaardata niet gevonden in {PENSION_DATA_PATH}")
        return {"fondsen": {}, "verzekeringen": {}, "metadata": {}}

def get_pension_info_with_notes(query, pension_data=None):
    if pension_data is None:
        pension_data = load_pension_data()

    pension_keywords = ["pensioen", "tak 21", "tak 23", "spaarfonds", "pensioenspaar", "verzekering", "rendement"]
    if not any(k in query.lower() for k in pension_keywords):
        return ""

    context = ""
    found = False

    for naam, f in pension_data["fondsen"].items():
        if naam.lower() in query.lower():
            context += f"Informatie over {naam} (pensioenspaarfonds):\n"
            context += f"- Uitgever: {f['uitgever']}\n"
            context += f"- Instapkosten: {f['instapkosten']}\n"
            context += f"- Lopende kosten: {f['lopende_kosten_min']} – {f['lopende_kosten_max']}\n"
            context += f"- Duurzaam: {f['duurzaam']}\n"
            context += f"- Rendement 5 jaar: {f['rendement_5jaar']}\n"
            context += f"- Rendement 10 jaar: {f['rendement_10jaar']}\n"
            context += f"- Rendement 20 jaar: {f['rendement_20jaar']}\n"
            if f.get("toelichting"):
                context += f"\nToelichting: {f['toelichting']}\n"
            found = True
            break

    if not found:
        for naam, v in pension_data["verzekeringen"].items():
            if naam.lower() in query.lower():
                context += f"Informatie over {naam} (pensioenspaarverzekering):\n"
                context += f"- Uitgever: {v['uitgever']}\n"
                context += f"- Instapkosten: {v['instapkosten']}\n"
                context += f"- Lopende kosten: {v['lopende_kosten_min']} – {v['lopende_kosten_max']}\n"
                context += f"- Duurzaam: {v['duurzaam']}\n"
                context += f"- Rendement 5 jaar: {v['rendement_5jaar']}\n"
                context += f"- Rendement 10 jaar: {v['rendement_10jaar']}\n"
                context += f"- Rendement 20 jaar: {v['rendement_20jaar']}\n"
                if v.get("toelichting"):
                    context += f"\nToelichting: {v['toelichting']}\n"
                found = True
                break

    if "metadata" in pension_data and "algemene_toelichtingen" in pension_data["metadata"]:
        context += "\nAlgemene toelichtingen:\n"
        for note in pension_data["metadata"]["algemene_toelichtingen"]:
            context += f"- {note}\n"

    return context

# ===== RAG FUNCTIE =====
def get_relevant_context(query, max_items=10, relevance_threshold=1.1, top_k=None):
    if top_k is not None:
        max_items = top_k

    logging.info(f"Zoekquery voor kennisbank: {query[:100]}...")
    print(f"Zoekquery voor kennisbank: {query[:100]}...")

    vector_store = VectorStore()
    initial_results = vector_store.search(query, top_k=max_items * 2)

    print("\nDEBUG AFSTANDEN:")
    print("Scores van de eerste 5 resultaten:")
    for i, r in enumerate(initial_results[:5]):
        print(f"Item {i}: afstand = {r.get('distance')}")

    for thresh in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        count = len([r for r in initial_results if r.get('distance', float('inf')) < thresh])
        print(f"Aantal items met afstand < {thresh}: {count}")

    filtered_results = [r for r in initial_results if r.get('distance', float('inf')) < relevance_threshold]
    final_results = filtered_results[:max_items]

    logging.info(f"Totaal gevonden: {len(initial_results)}, Na relevantiefilter: {len(filtered_results)}, Gebruikt: {len(final_results)}")
    print(f"Totaal gevonden: {len(initial_results)}, Na relevantiefilter: {len(filtered_results)}, Gebruikt: {len(final_results)}")

    context = []
    relevant_items = []

    for idx, result in enumerate(final_results):
        title = result.get('title', f"Kennisbank item #{idx+1}")
        content = result.get('chunk', '')
        score = result.get('distance', 'onbekend')

        logging.info(f"Item {idx+1}: '{title}' (score: {score})")
        print(f"Item {idx+1}: '{title}' (score: {score})")

        context.append(f"TERM: {title}\nDEFINITIE: {content}")
        relevant_items.append(title)

    return "\n\n".join(context), relevant_items

# ===== SAMENVATTING MET CONTEXT =====
def enhance_summary_with_rag(client, text, initial_summary=None, top_k=10):
    if not initial_summary:
        system_query = "Je taak is om een korte samenvatting (max. 100 woorden) te maken van dit document, gericht op de belangrijkste financiële kernpunten, termen en concepten."

        query_message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.3,
            system=system_query,
            messages=[{"role": "user", "content": f"Geef een beknopte samenvatting:\n\n{text}"}]
        )

        initial_summary = query_message.content[0].text

    relevant_context, relevant_items = get_relevant_context(initial_summary, top_k=top_k)

    enhanced_text = f"""
[RELEVANTE KENNISBANK INFORMATIE]
{relevant_context}
[EINDE RELEVANTE KENNISBANK INFORMATIE]

[ORIGINEEL DOCUMENT]
{text}
[EINDE ORIGINEEL DOCUMENT]
"""

    context_info = {
        "aantal_items": len(relevant_items),
        "relevante_items": relevant_items,
        "toelichting": "De samenvatting is verrijkt met relevante achtergrondinformatie uit de financiële kennisbank."
    }

    # Voeg extra context toe indien pensioenvraag
    pension_context = get_pension_info_with_notes(initial_summary)
    if pension_context:
        enhanced_text += f"\n\n[EXTRA CONTEXT – Pensioensparen]\n{pension_context}\n[EINDE CONTEXT]"
        context_info["relevante_items"].append("pensioenspaarbeleggingen")
        context_info["toelichting"] += "\nDe samenvatting bevat ook actuele pensioenspaarinformatie."

    return enhanced_text, context_info
