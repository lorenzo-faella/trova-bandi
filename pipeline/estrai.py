"""Estrazione dei requisiti con un LLM: testo della scheda -> regola candidata -> controlli automatici.

Una regola esce da qui solo se rispetta lo schema e se ogni citazione esiste nella scheda; altrimenti il modello riceve
gli errori e riprova. Non vuol dire che sia giusta: resta in data/regole_estratte/ finché una persona non l'ha riletta.

Lo schema è ricorsivo, quindi non si può imporre con gli structured output dell'API (che non ammettono schemi ricorsivi):
il JSON si controlla qui, ed è lo stesso controllo che vale per le etichette scritte a mano.

Uso:
  python -m pipeline.estrai api <cartella obiettivi> <cartella uscita>         con l'API (serve una chiave)
  python -m pipeline.estrai prepara <cartella obiettivi> <cartella lavoro>     scrive i prompt, per usarli senza API
  python -m pipeline.estrai importa <cartella obiettivi> <cartella lavoro> <cartella uscita>
                                                                               controlla le risposte <id>.risposta.json
Gli obiettivi sono file YAML con id, titolo e link: data/regole_persone o una cartella di data/gold.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml

from pipeline.provenienza import registra, salva_snapshot
from pipeline.citazioni import problemi
from pipeline.regole import DIR_PERSONE, DUMPER, LOADER, ROOT, SCHEMA, VALIDATORE

MODELLO = os.environ.get("TROVABANDI_MODELLO", "claude-opus-5-5")
PROMPT = Path(__file__).with_name("prompt_estrazione.md")
VOCABOLARIO = ROOT / "docs" / "vocabolario-persone.md"
TENTATIVI = 3
# Esempi, in ordine di preferenza. Il primo copre alternative annidate e famiglia, il secondo le scelte da elenco.
ESEMPI = ["inps-adi", "inps-assegno-unico", "inps-naspi"]
NOMI_SEZIONI = {"cosa": "Cos'è", "destinatari": "A chi è rivolto", "funzionamento": "Come funziona", "domanda": "Domanda"}


def vocabolario():
    """Il vocabolario senza la colonna "Usato da" e senza le scelte da discutere: la colonna dice quali campi servono
    a quali benefici, e nelle prove sui 5 benefici di esempio sarebbe un suggerimento sulla risposta."""
    testo = VOCABOLARIO.read_text(encoding="utf-8").split("## Scelte da discutere")[0]
    righe = []
    for riga in testo.splitlines():
        if riga.startswith("|"):
            celle = riga.strip("|").split("|")
            riga = "|" + "|".join(celle[:-1]) + "|"
        righe.append(riga)
    return "\n".join(righe).strip()


def esempi(escludi):
    """Due regole scritte a mano; mai quella del beneficio da estrarre, sarebbe la soluzione."""
    scelti = [i for i in ESEMPI if i != escludi][:2]
    return "\n\n".join((DIR_PERSONE / f"{i}.yaml").read_text(encoding="utf-8").strip() for i in scelti)


def istruzioni(escludi):
    schema = json.dumps(SCHEMA["$defs"], ensure_ascii=False, indent=1)
    return "\n\n".join([
        PROMPT.read_text(encoding="utf-8").strip(),
        "## Vocabolario\n\n" + vocabolario(),
        f"## Schema JSON dei requisiti\n\n```json\n{schema}\n```",
        "## Esempi di regole complete\n\nSono in YAML per leggibilità; tu rispondi in JSON e solo con `requisiti` e `note`.\n\n"
        f"```yaml\n{esempi(escludi)}\n```",
    ])


def testo_scheda(scheda):
    return "\n\n".join(f"## {NOMI_SEZIONI[k]}\n\n{v}" for k, v in scheda["sezioni"].items())


def richiesta(scheda):
    return f"<scheda titolo={json.dumps(scheda['titolo'], ensure_ascii=False)}>\n\n{testo_scheda(scheda)}\n\n</scheda>"


def leggi_risposta(testo):
    """L'oggetto JSON della risposta, anche se il modello lo ha chiuso in un blocco di codice."""
    m = re.search(r"```(?:json)?\s*\n(.*?)\n```", testo, re.S)
    return json.loads(m.group(1) if m else testo)


def componi(obiettivo, risposta, autore):
    regola = {"id": obiettivo["id"], "titolo": obiettivo["titolo"], "ente": obiettivo.get("ente", "INPS"),
              "link": obiettivo["link"], "apertura": None, "chiusura": None,
              "fonte": f"scheda INPS, estratta con LLM ({autore}), non rivista", "pubblico": "persone",
              "ultimo_controllo": time.strftime("%Y-%m-%d"), "requisiti": risposta.get("requisiti", [])}
    if risposta.get("note"):
        regola["note"] = risposta["note"]
    return regola


def errori(regola, scheda):
    """Prima lo schema: su una regola malformata il controllo delle citazioni non ha senso."""
    trovati = [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:200]}" for e in VALIDATORE.iter_errors(regola)]
    return trovati or problemi(regola, "\n".join(scheda["sezioni"].values()))


def estrai(obiettivo, scheda, chiama, autore, tentativi=TENTATIVI):
    """Restituisce (regola, numero di tentativi, errori dell'ultimo tentativo). chiama(system, messaggi) -> testo."""
    system = istruzioni(obiettivo["id"])
    messaggi = [{"role": "user", "content": richiesta(scheda)}]
    regola, trovati = None, []
    for n in range(1, tentativi + 1):
        testo = chiama(system, messaggi)
        try:
            regola = registra(componi(obiettivo, leggi_risposta(testo), autore), scheda, system + "\n" + richiesta(scheda), autore)
            trovati = errori(regola, scheda)
        except (json.JSONDecodeError, AttributeError) as e:
            regola, trovati = None, [f"la risposta non è un oggetto JSON: {e}"]
        if not trovati:
            registra(regola, scheda, json.dumps({"system": system, "messaggi": messaggi}, ensure_ascii=False), autore)
            return regola, n, []
        messaggi += [{"role": "assistant", "content": testo},
                     {"role": "user", "content": "La regola è stata rifiutata:\n- " + "\n- ".join(trovati) +
                      "\n\nCorreggi e rispondi di nuovo con l'intero oggetto JSON."}]
    return regola, tentativi, trovati


def chiama_api(system, messaggi):
    import anthropic  # solo per questo comando: il resto del progetto gira senza
    risposta = anthropic.Anthropic().beta.messages.create(
        model=MODELLO, max_tokens=16000, output_config={"effort": "high"},
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],  # istruzioni uguali per ogni scheda
        messages=messaggi, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    if risposta.stop_reason != "end_turn":
        raise RuntimeError(f"risposta interrotta: {risposta.stop_reason}")
    return "".join(b.text for b in risposta.content if b.type == "text")


def obiettivi(cartella):
    return [yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER) for f in sorted(Path(cartella).glob("*.yaml"))]


def carica_schede():
    files = sorted(f for f in (ROOT / "data" / "raw").glob("inps_schede_*.json") if not f.name.endswith(".meta.json"))
    if not files:
        sys.exit("manca lo scarico: python -m pipeline.fonti.inps")
    return {s["url"]: s for s in json.loads(files[-1].read_text(encoding="utf-8"))}


def salva(regola, cartella, fonte=None):
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    if fonte is not None:
        salva_snapshot(regola, fonte, cartella)
    testo = yaml.dump(regola, Dumper=DUMPER, allow_unicode=True, sort_keys=False, width=120)
    (cartella / f"{regola['id']}.yaml").write_text(testo, encoding="utf-8")


def comando_api(dir_obiettivi, uscita):
    schede = carica_schede()
    rifiutate = 0
    for o in obiettivi(dir_obiettivi):
        regola, n, trovati = estrai(o, schede[o["link"]], chiama_api, MODELLO)
        if trovati:
            rifiutate += 1
            print(f"RIFIUTATA {o['id']} dopo {n} tentativi:\n  " + "\n  ".join(trovati))
        else:
            salva(regola, uscita, schede[o["link"]])
            print(f"ok {o['id']} al tentativo {n}")
    return rifiutate


def comando_prepara(dir_obiettivi, lavoro):
    schede, lavoro = carica_schede(), Path(lavoro)
    lavoro.mkdir(parents=True, exist_ok=True)
    for o in obiettivi(dir_obiettivi):
        testo = f"{istruzioni(o['id'])}\n\n---\n\n{richiesta(schede[o['link']])}\n"
        (lavoro / f"{o['id']}.prompt.md").write_text(testo, encoding="utf-8")
    print(f"prompt scritti in {lavoro}")
    return 0


def comando_importa(dir_obiettivi, lavoro, uscita, autore):
    schede, lavoro = carica_schede(), Path(lavoro)
    rifiutate = 0
    for o in obiettivi(dir_obiettivi):
        f = lavoro / f"{o['id']}.risposta.json"
        if not f.exists():
            print(f"manca {f.name}")
            rifiutate += 1
            continue
        try:
            prompt_file = lavoro / f"{o['id']}.prompt.md"
            regola = registra(componi(o, leggi_risposta(f.read_text(encoding="utf-8")), autore), schede[o["link"]], prompt_file.read_text(encoding="utf-8") if prompt_file.exists() else None, autore)
            trovati = errori(regola, schede[o["link"]])
        except (json.JSONDecodeError, AttributeError) as e:
            regola, trovati = None, [f"la risposta non è un oggetto JSON: {e}"]
        if trovati:
            rifiutate += 1
            (lavoro / f"{o['id']}.errori.txt").write_text("\n".join(trovati) + "\n", encoding="utf-8")
            print(f"RIFIUTATA {o['id']}:\n  " + "\n  ".join(trovati))
        else:
            salva(regola, uscita, schede[o["link"]])
            print(f"ok {o['id']}: {len(regola['requisiti'])} requisiti")
    return rifiutate


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "api":
        sys.exit(1 if comando_api(a[1], a[2]) else 0)
    if len(a) == 3 and a[0] == "prepara":
        sys.exit(comando_prepara(a[1], a[2]))
    if len(a) == 4 and a[0] == "importa":
        sys.exit(1 if comando_importa(a[1], a[2], a[3], "Claude Code, " + MODELLO) else 0)
    sys.exit(__doc__)
