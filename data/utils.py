import os
from datetime import datetime

def log_feedback(feedback_type, feedback_details=None, document_info=None):
    """Log gebruikersfeedback voor analyse"""
    log_file = os.path.join(os.path.dirname(__file__), 'feedback_logs.csv')
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            f.write("timestamp,feedback_type,feedback_details,document_length,avatar,rag_used\n")
    
    # Add log entry
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        document_info = document_info or {}
        log_entry = f"{datetime.now().isoformat()},{feedback_type},{feedback_details},"
        log_entry += f"{document_info.get('length', 'unknown')},{document_info.get('avatar', 'unknown')},"
        log_entry += f"{document_info.get('rag_used', 'unknown')}\n"
        f.write(log_entry)