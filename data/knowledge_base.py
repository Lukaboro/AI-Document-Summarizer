import os
import json
import pandas as pd

# Basispad voor kennisbank
KB_PATH = os.path.join(os.path.dirname(__file__), 'kb_data')
os.makedirs(KB_PATH, exist_ok=True)

# Structuur voor kennisbank onderdelen
KB_CATEGORIES = {
    'definities': os.path.join(KB_PATH, 'definities'),
    'veelgestelde_vragen': os.path.join(KB_PATH, 'faq'),
    'marktdata': os.path.join(KB_PATH, 'marktdata'),
    'beleggingsproducten': os.path.join(KB_PATH, 'producten'),
    'regelgeving': os.path.join(KB_PATH, 'regelgeving')
}

# Maak directories voor elke categorie
for path in KB_CATEGORIES.values():
    os.makedirs(path, exist_ok=True)

def add_knowledge_item(category, item_id, content, metadata=None):
    """Voeg een kennisitem toe aan de database"""
    if category not in KB_CATEGORIES:
        raise ValueError(f"Ongeldige categorie: {category}")
    
    item = {
        'id': item_id,
        'content': content,
        'metadata': metadata or {}
    }
    
    file_path = os.path.join(KB_CATEGORIES[category], f"{item_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=2)
    return file_path

def get_knowledge_item(category, item_id):
    """Haal een kennisitem op uit de database"""
    file_path = os.path.join(KB_CATEGORIES[category], f"{item_id}.json")
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def bulk_add_from_csv(category, csv_path, content_col, id_col=None, metadata_cols=None):
    """Voeg meerdere kennisitems toe vanuit een CSV-bestand"""
    df = pd.read_csv(csv_path, sep=";")
    added_items = []
    
    for _, row in df.iterrows():
        content = row[content_col]
        item_id = row[id_col] if id_col else f"item_{len(added_items) + 1}"
        
        metadata = {}
        if metadata_cols:
            for col in metadata_cols:
                if col in row:
                    metadata[col] = row[col]
        
        file_path = add_knowledge_item(category, item_id, content, metadata)
        added_items.append(file_path)
    
    return added_items