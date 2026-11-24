"""Schede per la revisione a mano (decisione 97): per ogni regola di docs/da-rivedere-a-mano.md, cosa dice la regola in
parole semplici (requisiti, citazioni, date, note), da confrontare con il bando aperto dal link. Non giudica niente:
l'esito lo segna chi rivede, nella colonna "esito" di docs/da-rivedere-a-mano.md.
Uso: PYTHONPATH=. python prove/simulazione/schede_revisione.py  ->  docs/revisione-a-mano-schede.md"""
import re

from pipeline.citazioni import nodi
from web import domande as d

LISTA = d.ROOT / "docs" / "da-rivedere-a-mano.md"
USCITA = d.ROOT / "docs" / "revisione-a-mano-schede.md"


def righe_requisito(q, livello=0):
    rientro = "  " * livello
    if "almeno_uno_di" in q or "tutti_di" in q:
        chi = "almeno una di queste" if "almeno_uno_di" in q else "tutte queste"
        out = [f"{rientro}- **{chi}:**" + (f" «{q['citazione']}»" if q.get("citazione") else "")]
        for f in q.get("almeno_uno_di") or q.get("tutti_di"):
            out += righe_requisito(f, livello + 1)
        return out
    if "almeno_un_componente" in q:
        out = [f"{rientro}- **almeno una persona del nucleo:**" + (f" «{q['citazione']}»" if q.get("citazione") else "")]
        for f in q["almeno_un_componente"]:
            out += righe_requisito(f, livello + 1)
        return out
    testo = d.descrivi(q)
    tipo = "da verificare a mano" if "non_modellabile" in q else "controllato"
    rara = " (eccezione rara)" if q.get("portata") == "rara" else ""
    cit = f"\n{rientro}  > «{q['citazione']}»" if q.get("citazione") else ""
    return [f"{rientro}- *{tipo}{rara}:* {testo}{cit}"]


def main():
    ids = re.findall(r"\| `([^`]+)` \|", LISTA.read_text(encoding="utf-8"))
    regole = {r["id"]: r for r in d.regole_persone(True)}
    out = ["# Schede per la revisione a mano",
           "",
           "*Generato da `prove/simulazione/schede_revisione.py`. Per ogni regola: cosa dice la regola, da confrontare con il "
           "bando aperto dal link. L'esito (giusta / errori piccoli / sbagliata) si segna in `docs/da-rivedere-a-mano.md`. "
           "Niente LLM nel giudizio (decisione 97).*", ""]
    for n, i in enumerate(ids, 1):
        r = regole.get(i)
        if not r:
            out += [f"## {n}. `{i}`", "", "Regola non trovata fra quelle caricate dalla demo.", ""]
            continue
        date = ", ".join(x for x in [f"apertura {r['apertura']}" if r.get("apertura") else "",
                                     f"chiusura {r['chiusura']}" if r.get("chiusura") else ""] if x) or "nessuna data"
        out += [f"## {n}. {r['titolo']}", "",
                f"- **Link:** {r.get('link')}",
                f"- **Ente:** {r.get('ente') or '-'} · **origine:** {r.get('_origine')} · **date:** {date} · **file:** `{i}`",
                "", "**Requisiti della regola:**", ""]
        for q in r["requisiti"]:
            out += righe_requisito(q)
        if r.get("note"):
            note = r["note"] if isinstance(r["note"], list) else [r["note"]]
            out += ["", "**Note:** " + " · ".join(str(x) for x in note)]
        out += ["", "**Esito:** giusta / errori piccoli / sbagliata — nota:", "", "---", ""]
    USCITA.write_text("\n".join(out), encoding="utf-8")
    print(f"{USCITA.relative_to(d.ROOT)} scritto: {len(ids)} schede")


if __name__ == "__main__":
    main()
