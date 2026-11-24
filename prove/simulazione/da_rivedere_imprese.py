"""I bandi per le imprese da rivedere a mano (decisione 106): quelli che compaiono più spesso alle imprese di prova.

Per le 10 imprese di `imprese.yaml` e i 5 profili d'impresa della demo conta in quanti casi un bando risulta compatibile
o possibile nella zona dell'impresa (fuori dai gruppi a parte). Ne prende 20: i 10 più visti fra quelli dell'open data di
incentivi.gov.it e i 10 più visti fra quelli estratti dai bandi. Divisione incrociata come per le persone (decisione 97):
le regole estratte le ha fatte Edoardo e le rivede Lorenzo; quelle dell'open data vengono dal codice di Lorenzo e le
rivede Edoardo. Scrive la lista (docs/da-rivedere-a-mano-imprese.md) e le schede delle due metà. La revisione si fa
senza LLM: si apre il link e si confrontano requisiti, citazioni e date con il bando.

Uso: PYTHONPATH=. python prove/simulazione/da_rivedere_imprese.py [AAAA-MM-GG]
"""
import collections
import sys

import yaml

from web import domande as d

ROOT = d.ROOT
DOCS = ROOT / "docs"
VISTI = ("idoneo", "idoneo, salvo eccezioni", "da verificare")
QUANTE = 10  # per origine
CHI = {"estratta": "lorenzo", "open data": "edoardo"}
NOMI = {"lorenzo": "Lorenzo", "edoardo": "Edoardo"}
# i nomi dei campi delle persone non vanno bene per le imprese ("regione di residenza")
NOMI_IMPRESE = {"regione": "regione della sede", "comune": "comune della sede", "ateco_2025": "codice ATECO 2025",
                "ateco_2007": "codice ATECO 2007", "tipologia": "tipo di soggetto", "ambito": "area della sede"}
OPERATORI = {"interseca": "almeno uno fra", "in": "uno fra", "prefisso": "codice che inizia con"}


def imprese_di_prova():
    prova = yaml.safe_load((ROOT / "prove" / "simulazione" / "imprese.yaml").read_text(encoding="utf-8"))["imprese"]
    demo = [p for p in d.profili_demo() if p.get("ramo") == "imprese"]
    return [(p["id"], p["profilo"]) for p in prova + demo]


def conta_bandi(giorno):
    casi = imprese_di_prova()
    conta, regole = collections.Counter(), {}
    for _, profilo in casi:
        for r in d.passo("imprese", profilo, giorno, True)["risultati"]:
            if r["stato"] in VISTI and not r.get("gruppo"):
                conta[r["id"]] += 1
    for r in d.ramo_imprese(giorno)[0]:
        regole[r["id"]] = r
    return casi, conta, regole


def normale(titolo):
    return " ".join("".join(c if c.isalnum() else " " for c in titolo.lower()).split())


def scelti(conta, regole):
    """I più visti di ogni origine. A pari volte prima un ente non ancora in lista, poi l'ordine del titolo (così la lista
    non cambia da un giro all'altro). Si salta lo stesso bando già scelto dall'altra origine o con lo stesso titolo
    ("Quota Lombardia" c'è sia estratto sia nell'open data)."""
    out, titoli = {}, []
    for origine in CHI:
        restano = sorted((i for i in conta if regole[i]["_origine"] == origine), key=lambda i: regole[i]["titolo"])
        out[origine], enti = [], set()
        while restano and len(out[origine]) < QUANTE:
            massimo = max(conta[i] for i in restano)
            pari = [i for i in restano if conta[i] == massimo]
            i = next((i for i in pari if regole[i].get("ente") not in enti), pari[0])
            restano.remove(i)
            t = normale(regole[i]["titolo"])
            if any(t in altro or altro in t for altro in titoli):
                continue
            out[origine].append(i)
            enti.add(regole[i].get("ente"))
            titoli.append(t)
    return out


def righe_requisito(q, livello=0):
    rientro = "  " * livello
    cit = f" «{q['citazione']}»" if q.get("citazione") else ""
    for chiave, chi in (("almeno_uno_di", "almeno una di queste"), ("tutti_di", "tutte queste")):
        if chiave in q:
            out = [f"{rientro}- **{chi}:**{cit}"]
            for f in q[chiave]:
                out += righe_requisito(f, livello + 1)
            return out
    if "non_modellabile" in q:
        testo = f"*da verificare a mano:* {q['non_modellabile']}"
    else:
        valori = q.get("valori", [q.get("valore")])
        testo = f"*controllato:* {NOMI_IMPRESE.get(q['campo'], d.nome_campo(q['campo']))}, {OPERATORI.get(q.get('operatore'), q.get('operatore'))}: " \
                + ", ".join(str(v) for v in valori)
    righe = [f"{rientro}- {testo}"]
    if q.get("citazione"):
        righe.append(f"{rientro}  > «{q['citazione']}»")
    elif q.get("fonte"):
        righe.append(f"{rientro}  (fonte: {q['fonte']})")
    return righe


def scheda(n, r, volte, casi):
    date = ", ".join(x for x in [f"apertura {r['apertura']}" if r.get("apertura") else "",
                                 f"chiusura {r['chiusura']}" if r.get("chiusura") else ""] if x) or "nessuna data"
    out = [f"## {n}. {r['titolo']}", "",
           f"- **Link:** {r.get('link')}",
           f"- **Ente:** {r.get('ente') or '-'} · **origine:** {r['_origine']} · **date:** {date} · **file:** `{r['id']}`",
           f"- **Visto da:** {volte} imprese di prova su {casi} (compatibile o possibile)", ""]
    if r["_origine"] == "open data":
        out += ["*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, "
                "dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non "
                "riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "
                "\"compatibile\" in realtà non lo è?*", ""]
    out += ["**Requisiti della regola:**", ""]
    for q in r["requisiti"]:
        out += righe_requisito(q)
    if r.get("note"):
        note = r["note"] if isinstance(r["note"], list) else [r["note"]]
        out += ["", "**Note:** " + " · ".join(str(x) for x in note)]
    out += ["", "**Esito:** giusta / errori piccoli / sbagliata — nota:", "", "---", ""]
    return out


def main(giorno):
    casi, conta, regole = conta_bandi(giorno)
    scelta = scelti(conta, regole)
    numero = {}
    righe = [f"# Bandi per le imprese da rivedere a mano ({giorno})", "",
             f"*Generato da `prove/simulazione/da_rivedere_imprese.py` (decisione 106): i bandi che risultano più spesso "
             f"compatibili o possibili alle {len(casi)} imprese di prova (`prove/simulazione/imprese.yaml` più i profili "
             f"d'impresa della demo), {QUANTE} fra quelli dell'open data di incentivi.gov.it e {QUANTE} fra quelli estratti "
             "dai bandi. Divisione incrociata: le regole estratte le ha fatte Edoardo e le rivede Lorenzo "
             "(`docs/revisione-a-mano-imprese-lorenzo.md`), quelle dell'open data vengono dal codice di Lorenzo e le rivede "
             "Edoardo (`docs/revisione-a-mano-imprese-edoardo.md`). Per ognuna: aprire il link, confrontare requisiti, "
             "citazioni e date con il bando, segnare qui l'esito (giusta / errori piccoli / sbagliata) e una nota se serve. "
             "Niente LLM nel giudizio (decisione 97).*", "",
             "| # | volte | bando | origine | file | chi | esito |", "|---|---|---|---|---|---|---|"]
    n = 0
    for origine in ("estratta", "open data"):
        for i in scelta[origine]:
            n += 1
            numero[i] = n
            r = regole[i]
            righe.append(f"| {n} | {conta[i]}/{len(casi)} | [{r['titolo'][:70]}]({r.get('link', '')}) | {origine} | "
                         f"`{i}` | {NOMI[CHI[origine]]} | |")
    (DOCS / "da-rivedere-a-mano-imprese.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    for origine, chi in CHI.items():
        altro = next(c for c in NOMI if c != chi)
        out = [f"# Revisione a mano delle imprese: la metà di {NOMI[chi]} ({len(scelta[origine])} bandi, {origine})", "",
               "*Numeri della lista in `docs/da-rivedere-a-mano-imprese.md`, dove si segna l'esito. Divisione incrociata: "
               f"nessuno rivede una regola che ha prodotto. L'altra metà è in `docs/revisione-a-mano-imprese-{altro}.md`. "
               "Per ogni bando: aprire il link, confrontare requisiti, citazioni e date con il bando, segnare l'esito "
               "(giusta / errori piccoli / sbagliata) e una nota se serve. Niente LLM nel giudizio (decisione 97).*", ""]
        for i in scelta[origine]:
            out += scheda(numero[i], regole[i], conta[i], len(casi))
        (DOCS / f"revisione-a-mano-imprese-{chi}.md").write_text("\n".join(out), encoding="utf-8")
    print(f"{len(casi)} imprese di prova, {len(conta)} bandi visti; scritti la lista e le due metà "
          f"({', '.join(f'{o}: {len(v)}' for o, v in scelta.items())})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-11-22")
