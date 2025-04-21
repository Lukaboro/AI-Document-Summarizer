import os
import sys
import anthropic
import logging

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

def get_relevant_context(query, max_items=10, relevance_threshold=1.1, top_k=None):
    """
    Haal relevante context op uit de kennisbank voor een query, 
    beperkt door zowel aantal als relevantie.
    
    Args:
        query: De zoekopdracht/vraag
        max_items: Maximum aantal items om terug te geven
        relevance_threshold: Drempelwaarde voor relevantie (lagere waarde = strengere filter)
        top_k: Voor backward compatibility, wordt gebruikt als max_items als het gegeven is
    """
    # Gebruik top_k als het gegeven is (backward compatibility)
    if top_k is not None:
        max_items = top_k
        
    # Log de zoekquery
    logging.info(f"Zoekquery voor kennisbank: {query[:100]}...")
    print(f"Zoekquery voor kennisbank: {query[:100]}...")
    
    vector_store = VectorStore()
    # Haal meer items op dan we uiteindelijk zullen gebruiken
    initial_results = vector_store.search(query, top_k=max_items * 2)
    
        # VOEG HIER DE DEBUG CODE TOE:
    print("\nDEBUG AFSTANDEN:")
    print("Scores van de eerste 5 resultaten:")
    for i, r in enumerate(initial_results[:5]):
        print(f"Item {i}: afstand = {r.get('distance')}")

    # Tel het aantal resultaten bij verschillende drempelwaarden
    for thresh in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        count = len([r for r in initial_results if r.get('distance', float('inf')) < thresh])
        print(f"Aantal items met afstand < {thresh}: {count}")

    print()  # Extra regel voor leesbaarheid

    # Filter op basis van relevance_threshold
    # Voor FAISS met L2-afstand zijn lagere waarden beter (dichterbij = relevanter)
    filtered_results = [r for r in initial_results if r.get('distance', float('inf')) < relevance_threshold]
    
    # Beperk tot het maximum aantal
    final_results = filtered_results[:max_items]
    
    # Log statistieken over de resultaten
    logging.info(f"Totaal gevonden: {len(initial_results)}, " 
                f"Na relevantiefilter: {len(filtered_results)}, "
                f"Gebruikt: {len(final_results)}")
    print(f"Totaal gevonden: {len(initial_results)}, " 
         f"Na relevantiefilter: {len(filtered_results)}, "
         f"Gebruikt: {len(final_results)}")
    
    context = []
    relevant_items = []
    
    for idx, result in enumerate(final_results):
        # Gebruik de titel uit het resultaat
        title = result.get('title', f"Kennisbank item #{idx+1}")
        
        # Haal de content uit de chunk
        content = result.get('chunk', '')
        
        # Gebruik distance als score
        score = result.get('distance', 'onbekend')
        
        # Log item info met titel en score
        item_info = f"Item {idx+1}: '{title}' (score: {score})"
        logging.info(item_info)
        print(item_info)
        
        # Voeg toe aan context en relevante items
        context.append(f"TERM: {title}\nDEFINITIE: {content}")
        relevant_items.append(title)
    
    return "\n\n".join(context), relevant_items

def enhance_summary_with_rag(client, text, initial_summary=None, top_k=10):
    """
    Voegt relevante context uit de kennisbank toe aan het document.
    Dit wijzigt niet je bestaande prompt-structuur, maar verrijkt de input.
    
    Args:
        client: De Anthropic client
        text: De originele documenttekst
        initial_summary: Een optionele initiële samenvatting om de relevante context te bepalen
        top_k: Aantal relevante context-items om op te halen
    
    Returns:
        Een tuple van (verrijkte_tekst, context_info_dict)
    """
    # Als er geen initiële samenvatting is gegeven, genereer er een om relevante context te vinden
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
    
    # Vind relevante context op basis van de samenvatting
    relevant_context, relevant_items = get_relevant_context(initial_summary, top_k=top_k)
    
    # Bereid de verrijkte tekst voor
    enhanced_text = f"""
[RELEVANTE KENNISBANK INFORMATIE]
{relevant_context}
[EINDE RELEVANTE KENNISBANK INFORMATIE]

[ORIGINEEL DOCUMENT]
{text}
[EINDE ORIGINEEL DOCUMENT]
"""
    
    # Maak een context info dictionary voor betere transparantie
    context_info = {
        "aantal_items": len(relevant_items),
        "relevante_items": relevant_items,
        "toelichting": "De samenvatting is verrijkt met relevante achtergrondinformatie uit de financiële kennisbank, waaronder definities, veelgestelde vragen of marktdata die relevant zijn voor dit document."
    }
    
    return enhanced_text, context_info