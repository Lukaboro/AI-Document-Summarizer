import os
import faiss
import numpy as np
import json
import pickle
from sentence_transformers import SentenceTransformer
from data.knowledge_base import KB_PATH, KB_CATEGORIES

# Pad voor vectordatabase opslag
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), 'vector_db')
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Embeddings model
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'  # Een licht maar effectief model
model = SentenceTransformer(MODEL_NAME)

class VectorStore:
    def __init__(self):
        self.index_path = os.path.join(VECTOR_DB_PATH, 'faiss_index.bin')
        self.mapping_path = os.path.join(VECTOR_DB_PATH, 'id_mapping.pkl')
        self.embedding_dim = 384  # Dimensie van het gekozen model
        
        # Probeer bestaande index te laden of maak een nieuwe
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.mapping_path, 'rb') as f:
                self.id_to_path = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.id_to_path = {}
    
    def add_document(self, doc_text, doc_path, chunk_size=512):
        """Voeg een document toe aan de vectorstore, opgesplitst in chunks"""
        # Eenvoudige chunking op basis van lengte (kun je verfijnen)
        chunks = []
        for i in range(0, len(doc_text), chunk_size):
            chunk = doc_text[i:i+chunk_size]
            if len(chunk.strip()) > 50:  # Minimale grootte om ruis te vermijden
                chunks.append(chunk)
        
        # Genereer embeddings voor chunks
        embeddings = model.encode(chunks)
        
        # Voeg toe aan index
        start_id = len(self.id_to_path)
        for i, embedding in enumerate(embeddings):
            idx = start_id + i
            self.id_to_path[idx] = {
                'path': doc_path,
                'chunk': chunks[i],
                'chunk_id': i
            }
        
        # Voeg embeddings toe aan FAISS index
        faiss.normalize_L2(embeddings)  # Normalisatie voor betere resultaten
        self.index.add(embeddings)
        
        # Sla de bijgewerkte index op
        self.save()
        
        return len(chunks)
    
    def index_knowledge_base(self):
        """Index alle documenten in de kennisbank"""
        indexed_files = 0
        
        for category, path in KB_CATEGORIES.items():
            for filename in os.listdir(path):
                if filename.endswith('.json'):
                    file_path = os.path.join(path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Hier slaan we ook de metadata en originele id op
                    self.add_document_with_metadata(
                        doc_text=data['content'],
                        doc_path=file_path,
                        doc_id=data['id'],
                        metadata=data.get('metadata', {})
                    )
                    indexed_files += 1
        
        return indexed_files
    
    def add_document_with_metadata(self, doc_text, doc_path, doc_id, metadata=None, chunk_size=512):
        """Voeg een document toe met behoud van metadata"""
        # Eenvoudige chunking op basis van lengte (kun je verfijnen)
        chunks = []
        for i in range(0, len(doc_text), chunk_size):
            chunk = doc_text[i:i+chunk_size]
            if len(chunk.strip()) > 50:  # Minimale grootte om ruis te vermijden
                chunks.append(chunk)
        
        # Genereer embeddings voor chunks
        embeddings = model.encode(chunks)
        
        # Voeg toe aan index
        start_id = len(self.id_to_path)
        for i, embedding in enumerate(embeddings):
            idx = start_id + i
            self.id_to_path[idx] = {
                'path': doc_path,
                'chunk': chunks[i],
                'chunk_id': i,
                'doc_id': doc_id,
                'metadata': metadata or {}
            }
        
        # Voeg embeddings toe aan FAISS index
        faiss.normalize_L2(embeddings)  # Normalisatie voor betere resultaten
        self.index.add(embeddings)
        
        # Sla de bijgewerkte index op
        self.save()
        
        return len(chunks)
    
    def search(self, query, top_k=5):
        """Zoek relevante documenten voor een query"""
        # Genereer embedding voor query
        query_embedding = model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Zoek dichtstbijzijnde buren
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Haal resultaten op
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.id_to_path):
                continue  # Buiten bereik
            
            item = self.id_to_path[idx]
            
            # Bepaal de titel op basis van metadata (als dat beschikbaar is)
            title = None
            metadata = item.get('metadata', {})
            
            # Eerste keuze: term uit metadata
            if metadata and 'term' in metadata:
                title = metadata['term']
            # Tweede keuze: document id
            elif 'doc_id' in item:
                title = item['doc_id']
            # Laatste keuze: genereer een titel uit pad
            else:
                file_name = os.path.basename(item['path'])
                title = os.path.splitext(file_name)[0]
            
            # Resultaat samenstellen met meer informatie
            result = {
                'chunk': item['chunk'],
                'distance': float(distances[0][i]),
                'path': item['path'],
                'title': title,  # Voeg de titel toe aan het resultaat
                'metadata': metadata  # Voeg alle metadata toe
            }
            
            results.append(result)
        
        return results
    
    def save(self):
        """Sla index en mapping op"""
        faiss.write_index(self.index, self.index_path)
        with open(self.mapping_path, 'wb') as f:
            pickle.dump(self.id_to_path, f)
    
    def load(self):
        """Laad index en mapping"""
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.mapping_path, 'rb') as f:
                self.id_to_path = pickle.load(f)
            return True
        return False
    
    def add_pension_data_to_vectorstore(self, pension_data=None):
        """Voeg alleen algemene pensioentoelichtingen toe aan vector database voor semantisch zoeken."""

        if pension_data is None:
            try:
                pension_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'pensioenspaardata.json')
                with open(pension_data_path, 'r', encoding='utf-8') as f:
                    pension_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                print("Geen pensioendata gevonden om toe te voegen aan vectorstore.")
                return

        documents_added = 0

        # Enkel de algemene toelichtingen toevoegen
        if pension_data.get("metadata", {}).get("algemene_toelichtingen"):
            for idx, toelichting in enumerate(pension_data["metadata"]["algemene_toelichtingen"]):
                doc_text = f"Pensioenspaartoelichting #{idx+1}:\n{toelichting}"

                self.add_document_with_metadata(
                    doc_text=doc_text.strip(),
                    doc_path='pensioenspaardata.json',
                    doc_id=f"toelichting_{idx+1}",
                    metadata={"type": "algemene_toelichting", "source": "pensioenspaardata"}
                )
                documents_added += 1

        print(f"Pensioenspaardata: {documents_added} toelichtingen succesvol toegevoegd aan vectorstore.")

        return self