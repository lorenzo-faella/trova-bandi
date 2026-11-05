"""Versioni leggibili a mano dell'export (l'originale è una riga sola da 22 MB):
Excel con fogli "Aperti oggi" e "Tutti", e JSON indentato dei soli bandi aperti.
Uso: python -m pipeline.leggibili <export.json> <cartella di uscita> AAAA-MM-GG
"""
import json, sys
from pathlib import Path
import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.utils import get_column_letter

if len(sys.argv) != 4:
    sys.exit("uso: python -m pipeline.leggibili <export.json> <cartella> AAAA-MM-GG")
src, out, oggi = Path(sys.argv[1]), Path(sys.argv[2]), pd.Timestamp(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
docs = json.load(open(src, encoding="utf-8"))
df = pd.DataFrame(docs)

ORDINE = ["ID_Incentivo", "Titolo", "Stato", "Data_apertura", "Data_chiusura", "Note_di_apertura_chiusura",
          "Regioni", "Tipologia_Soggetto", "Dimensioni", "Forma_agevolazione", "Agevolazione_Concedibile_min",
          "Agevolazione_Concedibile_max", "Spesa_Ammessa_min", "Spesa_Ammessa_max", "Stanziamento_incentivo",
          "Obiettivo_Finalita", "Settore_Attivita", "Codici_ATECO", "Costi_Ammessi", "Comuni", "Ambito_territoriale",
          "Soggetto_Concedente", "Link_istituzionale", "Descrizione", "Altre_caratteristiche", "Base_normativa_primaria",
          "Base_normativa_secondaria", "Provvedimento_attuativo", "Gazzetta_ufficiale", "Data_ultimo_aggiornamento"]

ap = pd.to_datetime(df.Data_apertura, errors="coerce")
ch = pd.to_datetime(df.Data_chiusura, errors="coerce")
aperto = (ap.isna() | (ap <= oggi)) & (ch.isna() | (ch >= oggi))
df["Stato"] = "chiuso"
df.loc[aperto, "Stato"] = "aperto"
df.loc[aperto & ch.isna(), "Stato"] = "aperto (senza scadenza)"
df.loc[ap > oggi, "Stato"] = "non ancora aperto"

tab = df.copy()
for c in tab.columns:  # liste -> testo "a; b; c"
    tab[c] = tab[c].map(lambda v: "; ".join(map(str, v)) if isinstance(v, list) else v)
    tab[c] = tab[c].map(lambda v: ILLEGAL_CHARACTERS_RE.sub(" ", v) if isinstance(v, str) else v)  # Excel rifiuta i caratteri di controllo
for c in ("Data_apertura", "Data_chiusura"):
    tab[c] = pd.to_datetime(tab[c], errors="coerce").dt.date
tab = tab[[c for c in ORDINE if c in tab.columns]].sort_values(["Stato", "Data_chiusura"], na_position="last")
aperti = tab[tab.Stato.str.startswith("aperto")]

LARGH = {"Titolo": 60, "Descrizione": 80, "Link_istituzionale": 40, "Regioni": 30, "Tipologia_Soggetto": 40}
xlsx = out / f"incentivi_{oggi.date()}.xlsx"
with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
    for nome, t in (("Aperti oggi", aperti), ("Tutti", tab)):
        t.to_excel(w, sheet_name=nome, index=False)
        ws = w.sheets[nome]
        ws.freeze_panes = "C2"
        ws.auto_filter.ref = ws.dimensions
        for i, c in enumerate(t.columns, 1):
            ws.column_dimensions[get_column_letter(i)].width = LARGH.get(c, 18)

js = out / f"incentivi_aperti_{oggi.date()}.json"
json.dump([d for d, a in zip(docs, aperto) if a], open(js, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{xlsx.name}: {len(aperti)} aperti, {len(tab)} totali | {js.name}: {int(aperto.sum())} schede")
