"""Inventario degli enti che pubblicano bandi, regione per regione, e di quanti ne copriamo.

Non è un elenco scritto a memoria: parte dall'export completo di incentivi.gov.it (tutti gli anni), dove ogni incentivo
ha l'ente che lo concede e il link al sito dove è pubblicato. Per ogni regione: gli enti, il loro tipo, quanti bandi
hanno sul portale (in tutto e aperti) e i loro siti. Un ente è "coperto" se raccogliamo già da almeno uno dei suoi siti
(data/raw/documenti/, solo pagine di fonti regolari, non allegati né prove). Limite: il portale riguarda soprattutto le imprese (art. 18-ter D.L. 34/2019), quindi gli enti
che fanno bandi solo per le persone (diritto allo studio, casa, sociale) qui mancano: sono elencati a parte, da cercare.

Uso: python -m pipeline.fonti.inventario            scrive docs/enti-per-regione.md
"""
import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from pipeline.fonti import documenti as dc

ROOT = dc.ROOT
USCITA = ROOT / "docs" / "enti-per-regione.md"
NOMI = {"Trentino-Alto Adige/Südtirol": "Trentino-Alto Adige", "Valle d'Aosta/Vallée d'Aoste": "Valle d'Aosta"}
# Tipo di ente dal nome, nell'ordine: la prima regola che corrisponde vince.
TIPI = [("Camera di commercio", r"camer[ae] di commercio|unioncamere|unione regionale delle camere"),
        ("Comune o unione di comuni", r"^comune|unione (dei |di )?comuni|comunit[aà] montana|citt[aà] metropolitana|provincia di "),
        ("GAL (sviluppo rurale)", r"\bgal\b|gruppo di azione locale"),
        ("Agricoltura (organismo pagatore, PSR)", r"pagament[oi] in agricoltura|avepa|artea|agrea|arcea|organismo pagatore|sviluppo rurale"),
        ("Finanziaria o agenzia di sviluppo", r"svilupp|finanziari|finlombarda|finpiemonte|gepafin|friulia|irfis|filse|finmolise|"
                                             r"fira\b|innova|sardegna ricerche|invitalia|confidi|garanzia|credito"),
        ("Lavoro e formazione", r"lavoro|formazione|arti\b|arpal|alfa\b|anpal|occupazion"),
        ("Diritto allo studio", r"diritto allo studio|adisu|erdis|dsu|er\.go|disco"),
        ("Cultura, cinema, turismo", r"film commission|cultura|turismo|teatr|spettacol"),
        ("Ente parco o ambiente", r"parco|ambient|forest"),
        ("Regione o Provincia autonoma", r"^regione|provincia autonoma|giunta regionale|consiglio regionale"),
        ("Ente nazionale", r"ministero|inail|inps|agenzia delle entrate|presidenza del consiglio|dipartimento|gse\b|simest|sace")]
# Enti tipici dei bandi per le persone, che il portale (per legge sulle imprese) non elenca: da cercare in ogni regione.
PER_LE_PERSONE = ["Ente per il diritto allo studio universitario (borse, alloggi)", "Edilizia residenziale pubblica / casa (ATER, ACER, ALER…)",
                  "Politiche sociali e ambiti territoriali sociali (non autosufficienza, disabilità, famiglie)",
                  "Agenzia regionale per il lavoro (incentivi alle persone, formazione)", "Comuni capoluogo (contributi affitto, bonus locali)"]


def lista(v):
    return v if isinstance(v, list) else [v] if v else []


def tipo(ente):
    e = ente.lower()
    return next((t for t, rx in TIPI if re.search(rx, e)), "Altro")


def dominio(url):
    return urlparse(url or "").netloc.lower().removeprefix("www.")


def aperto(x, giorno):
    a, c = (x.get("Data_apertura") or "")[:10], (x.get("Data_chiusura") or "")[:10]
    return (not a or a <= giorno) and (not c or c >= giorno)


def inventario(export, documenti, giorno):
    """{regione: [{ente, tipo, totale, aperti, siti, coperto}]} e i domini che copriamo per regione."""
    nostri = collections.defaultdict(set)
    for d in documenti:
        # Solo le pagine raccolte da una fonte regolare: un PDF ospitato altrove o un documento di prova non bastano a
        # dire che sorvegliamo quel sito (es. un allegato su regione.marche.it, che è dietro un captcha).
        if d.get("fonte_elenco"):
            nostri[d.get("regione")].add(dominio(d.get("url")))
    enti = collections.defaultdict(lambda: {"totale": 0, "aperti": 0, "siti": collections.Counter(), "siti_aperti": collections.Counter()})
    for x in export:
        regioni = lista(x.get("Regioni"))
        if len(regioni) != 1:  # bandi nazionali o pluriregionali: non sono di un ente regionale
            continue
        regione = NOMI.get(regioni[0], regioni[0])
        for ente in lista(x.get("Soggetto_Concedente")):
            e = enti[(regione, ente.strip())]
            e["totale"] += 1
            e["aperti"] += aperto(x, giorno)
            if dominio(x.get("Link_istituzionale")):
                e["siti"][dominio(x.get("Link_istituzionale"))] += 1
                if aperto(x, giorno):
                    e["siti_aperti"][dominio(x.get("Link_istituzionale"))] += 1
    out = collections.defaultdict(list)
    for (regione, ente), e in enti.items():
        siti = [s for s, _ in e["siti"].most_common()]
        # Bando per bando: un bando aperto è coperto se il suo sito è tra quelli che raccogliamo.
        aperti_coperti = sum(n for s, n in e["siti_aperti"].items() if s in nostri[regione])
        stato = ("sì" if aperti_coperti == e["aperti"] else "in parte" if aperti_coperti else "no") if e["aperti"] else \
                ("sito sì" if any(s in nostri[regione] for s in siti) else "—")
        out[regione].append({"ente": ente, "tipo": tipo(ente), "totale": e["totale"], "aperti": e["aperti"], "siti": siti,
                             "aperti_coperti": aperti_coperti, "coperto": stato in ("sì", "in parte", "sito sì"), "stato": stato})
    for regione in out:
        out[regione].sort(key=lambda e: (-e["aperti"], -e["totale"], e["ente"]))
    return dict(out), nostri


def scrivi(inv, giorno_export):
    righe = [f"# Enti che pubblicano bandi, regione per regione",
             "",
             f"*Generato da `pipeline/fonti/inventario.py` dall'export di incentivi.gov.it del {giorno_export}: non modificare a mano.*",
             "",
             "Per ogni regione, gli enti che hanno pubblicato almeno un bando regionale sul portale (tutti gli anni), con quanti "
             "ne hanno in tutto e aperti, i siti dove li pubblicano e se raccogliamo già da uno di quei siti. "
             "**Limite:** il portale riguarda soprattutto le imprese, quindi gli enti che fanno bandi solo per le persone qui non ci "
             "sono; la lista da cercare è in fondo.",
             "",
             "## Riepilogo",
             "",
             "| regione | enti | con almeno un sito coperto | bandi aperti sul portale | di cui con il sito coperto | enti con bandi aperti scoperti |",
             "|---|---|---|---|---|---|"]
    for regione in sorted(inv):
        e = inv[regione]
        aperti = sum(x["aperti"] for x in e)
        coperti_aperti = sum(x["aperti_coperti"] for x in e)
        scoperti = sum(1 for x in e if x["aperti"] and x["aperti_coperti"] < x["aperti"])
        righe.append(f"| {regione} | {len(e)} | {sum(x['coperto'] for x in e)} | {aperti} | {coperti_aperti} | {scoperti} |")
    righe += ["", "## Tipi di ente", "", "| tipo | enti | bandi aperti | di cui con il sito coperto |", "|---|---|---|---|"]
    per_tipo = collections.defaultdict(lambda: [0, 0, 0])
    for e in (x for v in inv.values() for x in v):
        t = per_tipo[e["tipo"]]
        t[0] += 1; t[1] += e["aperti"]; t[2] += e["aperti_coperti"]
    for t, (n, a, c) in sorted(per_tipo.items(), key=lambda kv: -kv[1][1]):
        righe.append(f"| {t} | {n} | {a} | {c} |")
    for regione in sorted(inv):
        righe += ["", f"## {regione}", "", "| ente | tipo | bandi (aperti) | siti | aperti coperti |", "|---|---|---|---|---|"]
        for x in inv[regione]:
            if not x["aperti"] and x["tipo"] in ("Comune o unione di comuni",) and x["totale"] < 3:
                continue  # comuni con pochi bandi e nessuno aperto: restano nel conteggio, non nella tabella
            siti = ", ".join(x["siti"][:3]) or "—"
            righe.append(f"| {x['ente']} | {x['tipo']} | {x['totale']} ({x['aperti']}) | {siti} | {x['stato']} |")
    righe += ["", "## Enti per le persone, da cercare in ogni regione", "",
              "Il portale non li elenca. Per ogni regione vanno trovati e aggiunti:", ""]
    righe += [f"- {p}" for p in PER_LE_PERSONE]
    USCITA.write_text("\n".join(righe) + "\n", encoding="utf-8")


def main():
    files = sorted(f for f in (ROOT / "data" / "raw").glob("incentivi_export_*.json") if not f.name.endswith(".meta.json"))
    if not files:
        sys.exit("manca l'export di incentivi.gov.it: make scarica")
    giorno = files[-1].stem.rsplit("_", 1)[-1]
    export = json.loads(files[-1].read_text(encoding="utf-8"))
    documenti = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(dc.USCITA.glob("*.json"))]
    inv, _ = inventario(export, documenti, giorno)
    scrivi(inv, giorno)
    n = sum(len(v) for v in inv.values())
    print(f"{n} enti regionali in {len(inv)} regioni, {sum(x['coperto'] for v in inv.values() for x in v)} coperti: {USCITA}")


if __name__ == "__main__":
    main()
