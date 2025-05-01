
import json
from datetime import datetime
import os
import csv

def update_pension_data(new_data, filename="data/pensioenspaardata.json"):
    """Werk pensioenspaardata bij en behoud geschiedenis"""

    # Maak het pad als het niet bestaat
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Laad bestaande data als die bestaat
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {"history": []}
    
    # Voeg huidige data toe aan geschiedenis
    if "fondsen" in existing_data:
        history_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "data": existing_data
        }
        if "history" not in existing_data:
            existing_data["history"] = []
        existing_data["history"].append(history_entry)
    
    # Update met nieuwe data
    new_data["metadata"]["laatste_update"] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Schrijf bijgewerkte data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    return new_data

def log_feedback(feedback_type, feedback_details, document_info=None):
    """Log feedback over samenvattingen voor evaluatie"""
    log_file = os.path.join(os.path.dirname(__file__), 'feedback_logs.csv')
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            f.write("timestamp,feedback_type,feedback_details,doc_length,avatar,rag_used\n")
    
    # Add log entry
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        document_info = document_info or {}
        doc_length = document_info.get('length', 'unknown')
        avatar = document_info.get('avatar', 'unknown')
        rag_used = document_info.get('rag_used', True)
        
        log_entry = f"{datetime.now().isoformat()},{feedback_type},{feedback_details},{doc_length},{avatar},{rag_used}\n"
        f.write(log_entry)

def log_chat_interaction(question, answer, document_info=None):
    """Log chat interactions for evaluation"""
    log_file = os.path.join(os.path.dirname(__file__), 'chat_logs.csv')
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            f.write("timestamp,question_length,answer_length,avatar,rag_used\n")
    
    # Add log entry
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        document_info = document_info or {}
        avatar = document_info.get('avatar', 'unknown')
        rag_used = document_info.get('rag_used', True)
        
        log_entry = f"{datetime.now().isoformat()},{len(question)},{len(answer)},{avatar},{rag_used}\n"
        f.write(log_entry)