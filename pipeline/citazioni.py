"""Controllo delle citazioni: ogni requisito di una regola per persone deve citare la fonte parola per parola.

È la difesa principale contro le regole inventate da un LLM: un requisito che cita un testo inesistente viene scartato
senza bisogno di leggerlo. Non dimostra che la regola sia giusta, solo che il testo citato esiste.

Uso: python -m pipeline.citazioni [cartella ...]    controlla schema e citazioni dei file YAML, anche nelle sottocartelle
"""
import json
import re
import sys
from pathlib import Path

import yaml

from pipeline.motore import figli
from pipeline.regole import DIR_PERSONE, LOADER, ROOT, VALIDATORE


def normalizza(testo):
    return re.sub(r"\s+", " ", testo).strip()


def nodi(req):
    yield req
    for q in figli(req):
        yield from nodi(q)


def rare_in_alternativa(req, dentro=False):
    """Le eccezioni rare scritte dentro almeno_uno_di: lì il motore non le presume (decisione 52), quindi sono un errore."""
    if "non_modellabile" in req and req.get("portata") == "rara" and dentro:
        yield req
    for q in figli(req):
        yield from rare_in_alternativa(q, dentro or "almeno_uno_di" in req)


def problemi(regola, testo_fonte):
    """Lista vuota se la regola è a posto. Un requisito non modellabile può non citare: spesso segnala un'assenza.
    Un'eccezione rara invece deve citare: è proprio il passaggio che la persona leggerà nella lista finale."""
    fonte = normalizza(testo_fonte)
    out = []
    for i, req in enumerate(regola["requisiti"]):
        if "citazione" not in req and "non_modellabile" not in req:
            out.append(f"requisito {i}: manca la citazione")
        for nodo in nodi(req):
            citata = nodo.get("citazione")
            if citata and normalizza(citata) not in fonte:
                out.append(f"requisito {i}: citazione assente dalla fonte: {citata!r}")
            if nodo.get("portata") == "rara" and not citata:
                out.append(f"requisito {i}: un'eccezione rara deve avere la sua citazione")
        for nodo in rare_in_alternativa(req):
            out.append(f"requisito {i}: eccezione rara dentro almeno_uno_di, dove non vale: {nodo['non_modellabile'][:60]!r}")
    return out


UNITA = ["", "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove", "dieci", "undici", "dodici",
         "tredici", "quattordici", "quindici", "sedici", "diciassette", "diciotto", "diciannove"]
DECINE = ["", "", "venti", "trenta", "quaranta", "cinquanta", "sessanta", "settanta", "ottanta", "novanta"]


def in_lettere(n):
    """Fino a 99, come si scrivono nelle schede: "sessantotto giorni", "tredici settimane"."""
    if n < 20:
        return UNITA[n]
    decina, unita = DECINE[n // 10], n % 10
    if unita in (1, 8):  # ventuno, sessantotto: la vocale cade
        decina = decina[:-1]
    return decina + ("tré" if unita == 3 else UNITA[unita])


def forme(valore):
    """Come può comparire un numero in un testo italiano."""
    if float(valore) != int(valore):  # 19837.92 -> "19837,92", "19.837,92"
        semplice = str(valore).replace(".", ",")
        decimali = len(str(valore).split(".")[1])
        return {semplice} | {f"{valore:,.{k}f}".replace(",", "_").replace(".", ",").replace("_", ".")
                             for k in {decimali, 2}}  # 77010.6 si scrive anche "77.010,60"
    n = int(valore)
    out = {str(n), f"{n:,}".replace(",", ".")}
    if n % 1000 == 0 and n:
        out |= {f"{n // 1000}mila", f"{n // 1000} mila"}
    if 0 < n < 100:
        out.add(in_lettere(n))
    return out


def soglie_non_trovate(regola, testo_fonte):
    """Soglie che nella scheda non compaiono in nessuna forma: una citazione vera può accompagnare un numero inventato.

    È un avviso per chi rivede, non un errore: "minorenne" giustifica 18 senza scriverlo.
    """
    testo = normalizza(testo_fonte).lower()
    out = []
    for req in regola["requisiti"]:
        for nodo in nodi(req):
            if "valore" not in nodo:
                continue
            valori = nodo["valore"] if isinstance(nodo["valore"], list) else [nodo["valore"]]
            for v in valori:
                if not any(re.search(rf"(?<![\d.,]){re.escape(f)}(?![\d])", testo) for f in forme(v)):
                    out.append(f"{nodo['campo']} {nodo['operatore']} {v}")
    return out


def carica_testi_inps():
    """URL della scheda -> testo, dall'ultimo scarico."""
    files = sorted(f for f in (ROOT / "data" / "raw").glob("inps_schede_*.json") if not f.name.endswith(".meta.json"))
    if not files:
        sys.exit("manca lo scarico: python -m pipeline.fonti.inps")
    schede = json.loads(files[-1].read_text(encoding="utf-8"))
    return {s["url"]: "\n".join(s["sezioni"].values()) for s in schede}


def main(cartelle):
    testi = carica_testi_inps()
    buoni, vuoti, cattivi = 0, 0, 0
    for cartella in cartelle:
        for f in sorted(Path(cartella).rglob("*.yaml")):
            r = yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER)
            errori = [e.message[:150] for e in VALIDATORE.iter_errors(r)]
            if r.get("link") not in testi:
                errori.append("la fonte non è tra le schede scaricate")
            elif not errori:
                errori = problemi(r, testi[r["link"]])
            if errori:
                cattivi += 1
                print(f"ERRORE {f}")
                for e in errori:
                    print(f"  {e}")
            elif not r["requisiti"]:
                vuoti += 1
            else:
                buoni += 1
    print(f"{buoni} regole valide, {vuoti} ancora da compilare, {cattivi} con errori")
    return cattivi


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:] or [DIR_PERSONE]) else 0)
