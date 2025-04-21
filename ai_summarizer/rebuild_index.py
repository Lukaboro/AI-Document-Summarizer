# rebuild_index.py
import os
import shutil
from data.vector_store import VectorStore

# Verwijder oude indexbestanden
vector_db_path = os.path.join(os.path.dirname(__file__), 'data', 'vector_db')
if os.path.exists(vector_db_path):
    print(f"Verwijderen oude index in {vector_db_path}")
    shutil.rmtree(vector_db_path)
    os.makedirs(vector_db_path)

# Maak nieuwe index met metadata
print("Opnieuw indexeren van kennisbank...")
vs = VectorStore()
count = vs.index_knowledge_base()
print(f"{count} documenten geïndexeerd met metadata")