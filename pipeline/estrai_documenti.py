"""Estrazione dei requisiti dai bandi di regioni, comuni e altri enti (data/raw/documenti/), con un LLM.

È l'estrattore di pipeline/estrai.py applicato a documenti che non sono schede INPS: stesse istruzioni, stesso
vocabolario, stesso schema e stesso controllo delle citazioni, che qui si fa su tutte le pagine del documento.
Cambiano tre cose, scritte in AGGIUNTA: come si indica la fonte (ente e pagina), le date del bando e i bandi
non rivolti alle persone. pipeline/estrai.py non viene modificato: se ne usano le funzioni.

Uso, come per le schede INPS senza API:
  python -m pipeline.estrai_documenti prepara <cartella lavoro> [id ...]     scrive i prompt
  python -m pipeline.estrai_documenti importa <cartella lavoro> <cartella uscita> [id ...]
                                                                     controlla le risposte <id>.risposta.json
  python -m pipeline.estrai_documenti controlla <cartella regole>    schema e citazioni di regole già salvate
Le regole accettate vanno di solito in data/regole_estratte/documenti/, separate da quelle riviste.
"""
import json
import sys
import time
from pathlib import Path

from pipeline.citazioni import problemi
from pipeline.estrai import MODELLO, istruzioni, leggi_risposta, salva
from pipeline.fonti.documenti import USCITA as DIR_DOCUMENTI, testo_completo
from pipeline.regole import VALIDATORE

AGGIUNTA = """## Per questo documento

Il testo non è una scheda INPS ma un bando o un avviso di un ente (regione, comune, ministero…). Arriva dentro `<documento>`, diviso in pagine segnate `[pagina N]`. Le regole sopra valgono tutte, con queste differenze:

- `fonte`: `<ente>, pagina <N>`; per una pagina web, `<ente>, pagina web`.
- `citazione`: sempre parola per parola, senza il segno `[pagina N]`. Un PDF può spezzare le parole a fine riga: scegli un passaggio che sta su una riga sola.
- Residenza o sede: usa `regione` (il nome della regione, es. `Lombardia`, `Emilia-Romagna`) e `comune` (il nome del comune) con l'operatore `in`.
- Se il documento indica il periodo per presentare le domande, aggiungi alla risposta `"apertura"` e `"chiusura"` nel formato `AAAA-MM-GG`; se non li indica, `null`.
- Se il bando è rivolto solo a enti, comuni, scuole, associazioni o imprese, e non a persone, restituisci `"requisiti": []` e spiegalo nelle note."""


def documenti(ids=()):
    files = sorted(DIR_DOCUMENTI.glob("*.json"))
    docs = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    return [d for d in docs if not ids or d["id"] in ids]


def richiesta(doc):
    pagine = "\n\n".join(f"[pagina {i}]\n{p}" for i, p in enumerate(doc["pagine"], 1))
    attributi = f"titolo={json.dumps(doc['titolo'], ensure_ascii=False)} ente={json.dumps(doc['ente'], ensure_ascii=False)}"
    return f"<documento {attributi}>\n\n{pagine}\n\n</documento>"


def prompt(doc):
    return f"{istruzioni(doc['id'])}\n\n{AGGIUNTA}\n\n---\n\n{richiesta(doc)}\n"


def componi(doc, risposta, autore):
    regola = {"id": doc["id"], "titolo": doc["titolo"], "ente": doc["ente"], "link": doc["url"],
              "apertura": risposta.get("apertura"), "chiusura": risposta.get("chiusura"),
              "fonte": f"documento {doc['ente']}, estratto con LLM ({autore}), non rivisto", "pubblico": "persone",
              "ultimo_controllo": time.strftime("%Y-%m-%d"), "requisiti": risposta.get("requisiti", [])}
    if risposta.get("note"):
        regola["note"] = risposta["note"]
    return regola


def errori(regola, doc):
    """Prima lo schema, poi le citazioni su tutto il testo. Un PDF scansionato non ha testo da citare."""
    if doc.get("ocr_necessario"):
        return ["il documento è una scansione: serve l'OCR prima di estrarre"]
    trovati = [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:200]}" for e in VALIDATORE.iter_errors(regola)]
    return trovati or problemi(regola, testo_completo(doc))


def comando_prepara(lavoro, ids):
    lavoro = Path(lavoro)
    lavoro.mkdir(parents=True, exist_ok=True)
    for doc in documenti(ids):
        if doc.get("ocr_necessario"):
            print(f"salto {doc['id']}: scansione, serve l'OCR")
            continue
        (lavoro / f"{doc['id']}.prompt.md").write_text(prompt(doc), encoding="utf-8")
    print(f"prompt scritti in {lavoro}")
    return 0


def comando_importa(lavoro, uscita, ids, autore):
    lavoro, rifiutate = Path(lavoro), 0
    for doc in documenti(ids):
        f = lavoro / f"{doc['id']}.risposta.json"
        if not f.exists():
            continue
        try:
            regola = componi(doc, leggi_risposta(f.read_text(encoding="utf-8")), autore)
            trovati = errori(regola, doc)
        except (json.JSONDecodeError, AttributeError) as e:
            regola, trovati = None, [f"la risposta non è un oggetto JSON: {e}"]
        if trovati:
            rifiutate += 1
            (lavoro / f"{doc['id']}.errori.txt").write_text("\n".join(trovati) + "\n", encoding="utf-8")
            print(f"RIFIUTATA {doc['id']}:\n  " + "\n  ".join(trovati))
        else:
            salva(regola, uscita)
            print(f"ok {doc['id']}: {len(regola['requisiti'])} requisiti")
    return rifiutate


def comando_controlla(cartella):
    """Come `make controlla`, ma per le regole tratte dai documenti: pipeline/citazioni.py conosce solo le schede INPS."""
    import yaml
    per_link = {d["url"]: d for d in documenti()}
    con_errori = 0
    for f in sorted(Path(cartella).rglob("*.yaml")):
        regola = yaml.safe_load(f.read_text(encoding="utf-8"))
        doc = per_link.get(regola.get("link"))
        trovati = errori(regola, doc) if doc else ["il link non corrisponde a nessun documento in data/raw/documenti"]
        if trovati:
            con_errori += 1
            print(f"ERRORE {f}\n  " + "\n  ".join(trovati))
    print(f"{len(list(Path(cartella).rglob('*.yaml'))) - con_errori} regole valide, {con_errori} con errori")
    return con_errori


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "controlla":
        sys.exit(1 if comando_controlla(a[1]) else 0)
    if len(a) >= 2 and a[0] == "prepara":
        sys.exit(comando_prepara(a[1], a[2:]))
    if len(a) >= 3 and a[0] == "importa":
        sys.exit(1 if comando_importa(a[1], a[2], a[3:], "Claude Code, " + MODELLO) else 0)
    sys.exit(__doc__)
