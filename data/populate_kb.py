import sys
import os

# Voeg rootdirectory toe aan sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.knowledge_base import bulk_add_from_csv
from data.vector_store import VectorStore

# Bepaal het pad naar de map waarin dit script staat
BASE_DIR = os.path.dirname(__file__)
CSV_IMPORTS_PATH = os.path.join(BASE_DIR, 'csv_imports')

def import_definities():
    print("📥 Importeren van definities...")
    csv_path = os.path.join(CSV_IMPORTS_PATH, 'definities.csv')
    added = bulk_add_from_csv(
        category="definities",
        csv_path=csv_path,
        content_col="definitie",
        id_col="id",
        metadata_cols=["term", "bron"]
    )
    print(f"✅ {len(added)} definities toegevoegd.")
    return len(added)

def indexeer_vectordatabase():
    print("🔄 Indexeren van de kennisbank in FAISS...")
    vector_store = VectorStore()
    count = vector_store.index_knowledge_base()
    print(f"📚 {count} documenten geïndexeerd.")
    return count

if __name__ == "__main__":
    totaal_toegevoegd = import_definities()
    totaal_indexed = indexeer_vectordatabase()
    print("🎉 Kennisbank succesvol bijgewerkt en geïndexeerd.")
