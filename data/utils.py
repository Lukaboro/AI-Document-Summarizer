import os
import pandas as pd
import streamlit as st
from datetime import datetime

def log_feedback(feedback_type, feedback_details=None, document_info=None):
    """Log gebruikersfeedback voor analyse - werkt lokaal en in cloud"""
    # Maak log entry data
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "feedback_type": feedback_type,
        "feedback_details": feedback_details or "",
        "document_length": document_info.get('length', 'unknown') if document_info else 'unknown',
        "avatar": document_info.get('avatar', 'unknown') if document_info else 'unknown',
        "rag_used": document_info.get('rag_used', 'unknown') if document_info else 'unknown'
    }
    
    # 1. Bewaar in session_state (werkt altijd)
    if 'feedback_logs' not in st.session_state:
        st.session_state.feedback_logs = []
    
    st.session_state.feedback_logs.append(log_entry)
    
    # 2. Probeer naar bestand te schrijven (werkt lokaal)
    try:
        data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_folder, exist_ok=True)
        log_file = os.path.join(data_folder, 'feedback_logs.csv')
        
        # Schrijf naar bestand
        df = pd.DataFrame([log_entry])
        if not os.path.exists(log_file):
            df.to_csv(log_file, index=False)
        else:
            df.to_csv(log_file, mode='a', header=False, index=False)
    except Exception as e:
        # Stil falen bij schrijven naar bestand - we gebruiken toch session_state
        print(f"Info: Kon niet naar logbestand schrijven: {str(e)}")

# Functie voor chat geschiedenis loggen
def log_chat_interaction(question, answer, document_info=None):
    """Log chat interactions for evaluation"""
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_folder, exist_ok=True)  # <== cruciale toevoeging
    log_file = os.path.join(data_folder, 'chat_logs.csv')

    
    # Create file with headers if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            f.write("timestamp,question_length,answer_length,avatar,rag_used\n")
    
    # Add log entry
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        document_info = document_info or {}
        log_entry = f"{datetime.now().isoformat()},{len(question)},{len(answer)},"
        log_entry += f"{document_info.get('avatar', 'unknown')},{document_info.get('rag_used', True)}\n"
        f.write(log_entry)

def log_chat_interaction(question, answer, document_info=None):
    """Log chat interactions for evaluation - werkt lokaal en in cloud"""
    # Maak log entry data
    document_info = document_info or {}
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question_length": len(question),
        "answer_length": len(answer),
        "avatar": document_info.get('avatar', 'unknown'),
        "rag_used": document_info.get('rag_used', True)
    }
    
    # 1. Bewaar in session_state (werkt altijd)
    if 'chat_logs_df' not in st.session_state:
        st.session_state.chat_logs_df = pd.DataFrame(
            columns=["timestamp", "question_length", "answer_length", "avatar", "rag_used"]
        )
    
    # Voeg de nieuwe rij toe aan het bestaande DataFrame
    st.session_state.chat_logs_df = pd.concat(
        [st.session_state.chat_logs_df, pd.DataFrame([log_entry])], 
        ignore_index=True
    )
    
    # 2. Probeer naar bestand te schrijven (werkt lokaal)
    try:
        data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_folder, exist_ok=True)
        log_file = os.path.join(data_folder, 'chat_logs.csv')
        
        # Schrijf naar bestand
        df = pd.DataFrame([log_entry])
        if not os.path.exists(log_file):
            df.to_csv(log_file, index=False)
        else:
            df.to_csv(log_file, mode='a', header=False, index=False)
    except Exception as e:
        # Stil falen bij schrijven naar bestand - we gebruiken toch session_state
        print(f"Info: Kon niet naar chat logbestand schrijven: {str(e)}")