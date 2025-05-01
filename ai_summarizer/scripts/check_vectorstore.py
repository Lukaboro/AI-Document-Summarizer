# scripts/check_vectorstore.py
import os
import sys

# Bepaal de absolute paden
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))  # Ga twee niveaus omhoog

# Voeg de projectroot toe aan het systeempad
sys.path.append(project_root)

# Debug output om paden te controleren
print(f"Script directory: {script_dir}")
print(f"Project root: {project_root}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Nu proberen we te importeren zonder 'ai_summarizer' prefix
try:
    from data.vector_store import VectorStore
    print("Import succesvol!")
except ImportError as e:
    print(f"Import error: {e}")
    
    # Probeer alternatieve paden
    try:
        from ai_summarizer.data.vector_store import VectorStore
        print("Alternatieve import succesvol!")
    except ImportError as e:
        print(f"Alternatieve import error: {e}")
        
        # Laat zien welke bestanden er in de data directory zitten (als die bestaat)
        data_dir = os.path.join(project_root, 'data')
        alt_data_dir = os.path.join(project_root, 'ai_summarizer', 'data')
        
        if os.path.exists(data_dir):
            print(f"Bestanden in {data_dir}:")
            print(os.listdir(data_dir))
        
        if os.path.exists(alt_data_dir):
            print(f"Bestanden in {alt_data_dir}:")
            print(os.listdir(alt_data_dir))
        
        print("Kan vectorstore module niet vinden. Script wordt afgebroken.")
        sys.exit(1)

def main():
    """Controleer de vector store en toon inhoud"""
    try:
        # Maak een instantie van VectorStore
        vectorstore = VectorStore()
        
        # Tel het aantal documenten in de vectorstore
        print(f"Aantal chunks in de vectorstore: {len(vectorstore.id_to_path)}")
        
        # Toon enkele documenten ter controle
        for idx in range(min(5, len(vectorstore.id_to_path))):
            item = vectorstore.id_to_path[idx]
            print(f"\n=== Document #{idx} ===")
            print(f"Path: {item.get('path')}")
            print(f"Chunk ID: {item.get('chunk_id')}")
            print(f"Metadata: {item.get('metadata', {})}")
            content = item.get('chunk', '')
            print(f"Content snippet: {content[:200]}...")
        
        # Zoek naar pensioengerelateerde chunks
        print("\n=== Zoeken naar pensioengerelateerde documenten ===")
        pensioen_keywords = ["pensioen", "pensioenfonds", "tak 21", "tak 23"]
        found_pension_docs = False
        
        for idx, (key, item) in enumerate(vectorstore.id_to_path.items()):
            chunk_content = item.get('chunk', '').lower()
            if any(keyword in chunk_content for keyword in pensioen_keywords):
                found_pension_docs = True
                print(f"\n--- Pensioendocument gevonden (Document #{idx}) ---")
                print(f"Path: {item.get('path')}")
                print(f"Content snippet: {chunk_content[:200]}...")
        
        if not found_pension_docs:
            print("Geen pensioengerelateerde documenten gevonden in de vectorstore.")
        
        # Zoek met de search functie
        print("\n=== Zoekresultaten voor 'pensioensparen' ===")
        results = vectorstore.search("pensioensparen", top_k=3)
        if results:
            for i, result in enumerate(results):
                print(f"\nResultaat {i+1}:")
                print(f"Titel: {result.get('title', 'Geen titel')}")
                print(f"Afstand: {result.get('distance', 'Onbekend')}")
                print(f"Inhoud: {result.get('chunk', '')[:150]}...")
        else:
            print("Geen zoekresultaten gevonden.")
        
        print("\n=== Controle voltooid ===")
        
    except Exception as e:
        print(f"Error bij uitvoeren van vectorstore checks: {e}")
        import traceback
        traceback.print_exc()

# Deze regel zorgt ervoor dat main() wordt uitgevoerd
if __name__ == "__main__":
    main()       