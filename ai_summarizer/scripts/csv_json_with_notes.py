import csv
import json
import os

def csv_to_json_with_notes(products_csv, notes_csv, output_json):
    """Converteer CSV-bestanden naar een gecombineerd JSON-bestand"""
    
    fondsen = {}
    verzekeringen = {}
    metadata = {"algemene_toelichtingen": [], "laatste_update": "2025-04-15"}

    # Detecteer het scheidingsteken in het producten CSV
    product_delimiter = detect_delimiter(products_csv)
    print(f"Gedetecteerd scheidingsteken voor producten: '{product_delimiter}'")
    
    # Debug informatie tonen
    print(f"Verwerken van producten CSV: {products_csv}")
    if not os.path.exists(products_csv):
        print(f"FOUT: Bestand niet gevonden: {products_csv}")
        return None
    
    # Eerst de kolomnamen lezen om te zien wat beschikbaar is
    with open(products_csv, 'r', encoding='utf-8-sig') as csvfile:  # utf-8-sig voor BOM-detectie
        reader = csv.reader(csvfile, delimiter=product_delimiter)
        headers = next(reader)  # Eerste rij met kolomnamen
        print(f"Gevonden kolomnamen in {products_csv}:")
        for idx, header in enumerate(headers):
            print(f"  {idx+1}. '{header}'")
    
    # Productgegevens inlezen
    with open(products_csv, 'r', encoding='utf-8-sig') as csvfile:  # utf-8-sig voor BOM-detectie
        reader = csv.DictReader(csvfile, delimiter=product_delimiter)
        
        # Verkrijg de veldnamen zonder BOM
        fieldnames = [name.replace('\ufeff', '') for name in reader.fieldnames]
        
        # Verificatie van verplichte kolommen
        required_columns = ['naam', 'type']
        for col in required_columns:
            if col not in fieldnames:
                print(f"FOUT: Verplichte kolom '{col}' ontbreekt in CSV. Beschikbare kolommen: {fieldnames}")
                return None
        
        # Reset bestandspositie en lees opnieuw
        csvfile.seek(0)
        next(csvfile)  # Skip header
        
        for row in reader:
            # Verwijder BOM uit sleutels
            clean_row = {k.replace('\ufeff', ''): v for k, v in row.items()}
            
            # Alle kolommen mappen naar product_data
            product_data = {}
            for key, value in clean_row.items():
                if key not in ['naam', 'type'] and key.strip():
                    # Zorg ervoor dat er geen None-waardes zijn
                    product_data[key] = value.strip() if value else ""
            
            # Bepaal producttype en voeg toe aan juiste categorie
            product_type = clean_row['type'].lower().strip()
            product_name = clean_row['naam'].strip()
            
            if not product_name:
                continue  # Sla lege rijen over
                
            # Bepaal de categorie op basis van type
            if 'fonds' in product_type or 'bank' in product_type:
                print(f"Fonds gevonden: {product_name}")
                fondsen[product_name] = product_data
            elif 'verzekering' in product_type or 'verzekeraar' in product_type:
                print(f"Verzekering gevonden: {product_name}")
                verzekeringen[product_name] = product_data
            else:
                print(f"Waarschuwing: Onbekend producttype '{product_type}' voor '{product_name}'. Toegevoegd als fonds.")
                fondsen[product_name] = product_data

    # Detecteer het scheidingsteken in het toelichtingen CSV
    notes_delimiter = detect_delimiter(notes_csv)
    print(f"Gedetecteerd scheidingsteken voor toelichtingen: '{notes_delimiter}'")
    
    # Debug informatie tonen
    print(f"Verwerken van toelichtingen CSV: {notes_csv}")
    if not os.path.exists(notes_csv):
        print(f"FOUT: Bestand niet gevonden: {notes_csv}")
        return None
    
    # Eerst de kolomnamen van toelichtingen lezen
    with open(notes_csv, 'r', encoding='utf-8-sig') as csvfile:  # utf-8-sig voor BOM-detectie
        reader = csv.reader(csvfile, delimiter=notes_delimiter)
        headers = next(reader)  # Eerste rij met kolomnamen
        print(f"Gevonden kolomnamen in {notes_csv}:")
        for idx, header in enumerate(headers):
            print(f"  {idx+1}. '{header}'")
    
    # Toelichtingen inlezen - dit is een aparte CSV met een andere structuur
    with open(notes_csv, 'r', encoding='utf-8-sig') as toelichtingfile:  # utf-8-sig voor BOM-detectie
        reader = csv.DictReader(toelichtingfile, delimiter=notes_delimiter)
        
        # Zoek de juiste kolomnaam voor toelichtingen
        fieldnames = [name.replace('\ufeff', '') for name in reader.fieldnames]
        toelichting_column = None
        possible_columns = ['Toelichting', 'toelichting', 'opmerking', 'Opmerking', 'tekst', 'Tekst']
        
        for col in possible_columns:
            if col in fieldnames:
                toelichting_column = col
                break
        
        if not toelichting_column:
            print(f"Waarschuwing: Geen herkenbare toelichting kolom gevonden. Eerste kolom wordt gebruikt.")
            toelichting_column = fieldnames[0]
        
        print(f"Toelichtingen worden gelezen uit kolom: '{toelichting_column}'")
        
        # Reset bestandspositie en lees opnieuw
        toelichtingfile.seek(0)
        next(toelichtingfile)  # Skip header
        reader = csv.DictReader(toelichtingfile, delimiter=notes_delimiter)
        
        for row in reader:
            # Verwijder BOM uit sleutels
            clean_row = {k.replace('\ufeff', ''): v for k, v in row.items()}
            
            if toelichting_column in clean_row and clean_row[toelichting_column].strip():
                toelichting_tekst = clean_row[toelichting_column].strip()
                print(f"Toelichting gevonden: {toelichting_tekst[:50]}...")
                metadata["algemene_toelichtingen"].append(toelichting_tekst)

    # Structuur opbouwen
    pensioenspaardata = {
        "fondsen": fondsen,
        "verzekeringen": verzekeringen,
        "metadata": metadata
    }

    # Debug informatie tonen
    print(f"Gevonden data:")
    print(f"  {len(fondsen)} fondsen")
    print(f"  {len(verzekeringen)} verzekeringen")
    print(f"  {len(metadata['algemene_toelichtingen'])} toelichtingen")

    # JSON schrijven
    with open(output_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(pensioenspaardata, jsonfile, indent=4, ensure_ascii=False)
    
    print(f"JSON-bestand succesvol geschreven naar: {output_json}")
    return pensioenspaardata

def detect_delimiter(csv_file):
    """Detecteer het scheidingsteken in een CSV-bestand"""
    with open(csv_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig voor BOM-detectie
        first_line = f.readline().strip()
        
        # Controleer mogelijke scheidingstekens
        delimiters = [';', ',', '\t', '|']
        counts = {d: first_line.count(d) for d in delimiters}
        
        # Kies het scheidingsteken met de meeste voorkomens
        max_count = 0
        chosen_delimiter = ','  # Standaard
        
        for d, count in counts.items():
            if count > max_count:
                max_count = count
                chosen_delimiter = d
        
        return chosen_delimiter

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Gebruik: python csv_to_json_with_notes.py <producten_csv> <toelichtingen_csv> <output_json>")
        sys.exit(1)
    
    products_csv = sys.argv[1]
    notes_csv = sys.argv[2]
    output_json = sys.argv[3]
    
    print(f"Converteren van CSV-bestanden naar JSON:")
    print(f"- Producten: {products_csv}")
    print(f"- Toelichtingen: {notes_csv}")
    print(f"- Output: {output_json}")
    
    result = csv_to_json_with_notes(products_csv, notes_csv, output_json)
    
    if result:
        print(f"Conversie voltooid!")
    else:
        print(f"Conversie mislukt. Controleer de fouten hierboven.")
        sys.exit(1)