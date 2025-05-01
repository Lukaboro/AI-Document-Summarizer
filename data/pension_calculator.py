import os
from .load_pension_data import load_pensioen_data
import pandas as pd

# Laad DataFrame één keer bij opstarten van de module
# Absoluut pad relatief aan dit bestand
bestandspad = os.path.join(os.path.dirname(__file__), "pensioenspaardata.json")

pension_df = load_pensioen_data(bestandspad)

def format_extra_info(row) -> str:
    info = ""
    for col in ["uitgever", "instapkosten", "lopende kosten min", "lopende kosten max", "rendement_5jaar", "rendement_10jaar", "rendement_20jaar", "duurzaam"]:
        if col in row and pd.notna(row[col]):
            info += f"\n   - {col.capitalize()}: {row[col]}"
    if "toelichting" in row and row["toelichting"]:
        info += f"\n   - Toelichting: {row['toelichting']}"
    return info

def bereken_op_kolom(veld: str, berekening: str) -> str:
    if veld not in pension_df.columns:
        return None
    try:
        series = pd.to_numeric(pension_df[veld], errors="coerce").dropna()
        if series.empty:
            return f"Er zijn geen gegevens beschikbaar voor '{veld}'."

        if berekening == "min":
            min_waarde = series.min()
            matches = pension_df[pd.to_numeric(pension_df[veld], errors="coerce") == min_waarde]
            resultaat = f"De laagste waarde voor '{veld}' is {min_waarde:.2f}%, gevonden bij:"
            for _, row in matches.iterrows():
                resultaat += f"\n\n• {row.get('Fonds Naam', '[naam onbekend]')}"
                resultaat += format_extra_info(row)
            return resultaat.strip()

        elif berekening == "max":
            max_waarde = series.max()
            matches = pension_df[pd.to_numeric(pension_df[veld], errors="coerce") == max_waarde]
            resultaat = f"De hoogste waarde voor '{veld}' is {max_waarde:.2f}%, gevonden bij:"
            for _, row in matches.iterrows():
                resultaat += f"\n\n• {row.get('Fonds Naam', '[naam onbekend]')}"
                resultaat += format_extra_info(row)
            return resultaat.strip()

        elif berekening == "average":
            return f"Het gemiddelde voor '{veld}' is {series.mean():.2f}%."

        elif berekening == "top_3":
            top = series.nlargest(3)
            rows = pension_df[pd.to_numeric(pension_df[veld], errors="coerce").isin(top)]
            resultaat = f"Top 3 hoogste waarden voor '{veld}':"
            for _, row in rows.iterrows():
                resultaat += f"\n\n• {row.get('Fonds Naam', '[naam onbekend]')} ({row[veld]}%)"
                resultaat += format_extra_info(row)
            return resultaat.strip()

        elif berekening == "top_5":
            top = series.nlargest(5)
            rows = pension_df[pd.to_numeric(pension_df[veld], errors="coerce").isin(top)]
            resultaat = f"Top 5 hoogste waarden voor '{veld}':"
            for _, row in rows.iterrows():
                resultaat += f"\n\n• {row.get('Fonds Naam', '[naam onbekend]')} ({row[veld]}%)"
                resultaat += format_extra_info(row)
            return resultaat.strip()

        elif berekening == "top_rendement_bij_lage_kost":
            df = pension_df.dropna(subset=["instapkosten", veld])
            df["instapkosten"] = pd.to_numeric(df["instapkosten"], errors="coerce")
            df[veld] = pd.to_numeric(df[veld], errors="coerce")
            if df.empty:
                return "Er zijn onvoldoende gegevens voor rendement en kosten."
            gefilterd = df[df["instapkosten"] <= 0.1]
            if gefilterd.empty:
                return "Er zijn geen fondsen met 0% instapkosten."
            beste = gefilterd.sort_values(by=veld, ascending=False).head(1)
            resultaat = "Het beste rendement bij 0% instapkosten is gevonden bij:"
            for _, row in beste.iterrows():
                resultaat += f"\n\n• {row.get('Fonds Naam', '[naam onbekend]')} ({row[veld]:.2f}%)"
                resultaat += format_extra_info(row)
            return resultaat.strip()

        elif berekening == "top_duurzaam":
            df = pension_df[pension_df["duurzaam"].str.lower() == "ja"]
            df[veld] = pd.to_numeric(df[veld], errors="coerce")
            if df.empty:
                return "Er zijn geen duurzame fondsen in de dataset."
            if veld not in df.columns:
                return "Het gevraagde veld komt niet voor bij duurzame fondsen."
            top = df.dropna(subset=[veld]).sort_values(by=veld, ascending=False).head(3)
            if top.empty:
                return "Geen bruikbare cijfers bij duurzame fondsen."
            resultaat = f"Top 3 duurzame fondsen op basis van '{veld}':"
            for _, row in top.iterrows():
                resultaat += f"\n\n• {row.get('Fonds Naam', '[naam onbekend]')} ({row[veld]:.2f}%)"
                resultaat += format_extra_info(row)
            return resultaat.strip()

        else:
            return None

    except Exception as e:
        return f"Fout bij berekening: {e}"