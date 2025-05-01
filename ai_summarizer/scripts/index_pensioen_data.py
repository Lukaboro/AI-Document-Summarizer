# ai_summarizer/scripts/index_pensioen_data.py
import sys
import os
import json

# Bepaal de absolute paden en voeg toe aan systeempad
script_dir = os.path.dirname(os.path.abspath(__file__))  # ai_summarizer/scripts
app_dir = os.path.dirname(script_dir)  # ai_summarizer
project_root = os.path.dirname(app_dir)  # project root

# Voeg beide mogelijke locaties toe aan de systeempath
sys.path.append(project_root)  # Voor 'data' in de hoofdmap
sys.path.append(app_dir)  # Voor 'data' in de ai_summarizer map

# Debug info
print(f"Script directory: {script_dir}")
print(f"App directory: {app_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

# Probeer beide mogelijke imports
try:
    # Optie 1: data is in de hoofdmap
    from data.vector_store import VectorStore
    print("Import succesvol vanuit project root")
except ImportError:
    try:
        # Optie 2: data is in de ai_summarizer map
        from ai_summarizer.data.vector_store import VectorStore
        print("Import succesvol vanuit ai_summarizer module")
    except ImportError:
        print("Zoeken naar vector_store.py...")
        # Zoek naar het bestand in beide mogelijke locaties
        possible_locations = [
            os.path.join(project_root, 'data', 'vector_store.py'),
            os.path.join(app_dir, 'data', 'vector_store.py')
        ]
        for loc in possible_locations:
            if os.path.exists(loc):
                print(f"vector_store.py gevonden op: {loc}")
            else:
                print(f"Niet gevonden op: {loc}")
        
        # Als we hier zijn, konden we het niet importeren
        raise ImportError("Kon VectorStore niet importeren. Controleer de mappenstructuur.")

def main():
    print("Initialiseer vectorstore...")
    vectorstore = VectorStore()

    # Pad naar pensioendata (probeer beide mogelijke locaties)
    potential_paths = [
        os.path.join(project_root, 'data', 'pensioenspaardata.json'),
        os.path.join(app_dir, 'data', 'pensioenspaardata.json')
    ]
    
    json_path = None
    for path in potential_paths:
        if os.path.exists(path):
            json_path = path
            break
    
    if not json_path:
        print(f"Fout: Kan pensioenspaardata.json niet vinden.")
        print(f"Gezocht op: {potential_paths}")
        return
    
    print(f"Pensioenspaardata gevonden op: {json_path}")
    
    try:
        # Laad pensioendata
        with open(json_path, 'r', encoding='utf-8') as f:
            pension_data = json.load(f)
        
        # Tel aantal items
        fondsen_count = len(pension_data.get('fondsen', {}))
        verzekeringen_count = len(pension_data.get('verzekeringen', {}))
        toelichtingen_count = len(pension_data.get('metadata', {}).get('algemene_toelichtingen', []))
        
        print(f"Pensioendata geladen: {fondsen_count} fondsen, {verzekeringen_count} verzekeringen, {toelichtingen_count} toelichtingen")
        
        # Voeg alleen toelichtingen toe aan vectorstore
        documents_added = 0
        
        # Algemene toelichtingen toevoegen
        if toelichtingen_count > 0:
            for idx, toelichting in enumerate(pension_data['metadata']['algemene_toelichtingen']):
                doc_text = f"Pensioenspaartoelichting #{idx+1}:\n{toelichting}"
                
                # Voeg toe aan vectorstore
                chunks_added = vectorstore.add_document_with_metadata(
                    doc_text=doc_text,
                    doc_path='pensioenspaardata.json',
                    doc_id=f"toelichting_{idx+1}",
                    metadata={
                        "type": "pensioen_toelichting", 
                        "source": "pensioenspaardata"
                    }
                )
                
                documents_added += 1
                print(f"Toegevoegd toelichting #{idx+1}: {doc_text[:50]}... ({chunks_added} chunks)")
        
        # Product-specifieke toelichtingen (indien aanwezig)
        for product_type, products in [("fonds", pension_data.get('fondsen', {})), 
                                      ("verzekering", pension_data.get('verzekeringen', {}))]:
            for product_name, product_data in products.items():
                if product_data.get('toelichting'):
                    doc_text = f"Productspecifieke toelichting voor {product_name} ({product_type}):\n{product_data['toelichting']}"
                    
                    chunks_added = vectorstore.add_document_with_metadata(
                        doc_text=doc_text,
                        doc_path='pensioenspaardata.json',
                        doc_id=f"product_{product_name}",
                        metadata={
                            "type": "product_toelichting",
                            "product": product_name,
                            "product_type": product_type,
                            "source": "pensioenspaardata"
                        }
                    )
                    
                    documents_added += 1
                    print(f"Toegevoegd producttoelichting voor {product_name}: {doc_text[:50]}... ({chunks_added} chunks)")
        
        # Sla de vectorstore op
        vectorstore.save()
        
        print(f"\nKlaar: {documents_added} pensioenspaartoelichtingen succesvol geïndexeerd!")
        
    except Exception as e:
        print(f"Fout bij indexeren pensioenspaardata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()