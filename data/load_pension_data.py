import os
import json
import pandas as pd

def load_pensioen_data(bestandsnaam: str) -> pd.DataFrame:
    # Zorg dat je pad werkt, ongeacht de werkdirectory van Streamlit
    base_dir = os.path.dirname(__file__)  # map waarin load_pension_data.py staat
    full_path = os.path.join(base_dir, bestandsnaam)  # dus: ../data/pensioenspaardata.json

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Pensioendatabestand niet gevonden: {full_path}")

    with open(full_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fondsen_dict = data.get("fondsen", {})
    records = []

    for fonds_naam, kenmerken in fondsen_dict.items():
        flat = {"Fonds Naam": fonds_naam}
        flat.update(kenmerken)
        records.append(flat)

    df = pd.DataFrame(records)

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('%', '', regex=False).str.replace('€', '', regex=False).str.replace(',', '.', regex=False)
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass

    return df

