"""Simulazione della demo con le persone di prova, senza server: domande fatte ed esiti (decisione 91).

Come rigioca.py: ogni persona risponde solo dal suo file, una domanda alla volta, come la pagina. In più i 4 profili
del caro vita della demo, già completi. Scrive docs/simulazione-<giorno>.md con, per ognuno, quante domande, quanti
"ti spetta" e "possibili" della sua zona (nazionali e regioni vicine) e quali sono, da giudicare a mano.

Uso: PYTHONPATH=. python prove/simulazione/riepilogo.py [AAAA-MM-GG]
"""
import sys
from pathlib import Path

import yaml

from web import domande as d

ROOT = Path(__file__).resolve().parent.parent.parent
NON_SO = "non lo so"


def rispondi(persona, giorno, massimo=80):
    """Il questionario della demo con le risposte del file: (domande fatte, ultimo passo)."""
    R, p, chieste = persona["risposte"], {}, []
    sempre = R.get("anni_residenza_continuativa_italia") == R["nucleo"][0]["eta"]
    for _ in range(massimo):
        out = d.passo("persone", p, giorno, True)
        q = out["domanda"]
        if not q:
            return chieste, out
        chieste.append(q["campo"])
        if q["tipo"] == "pagina":
            for parte in q["parti"]:
                if all(p.get(c) == v for c, v in (parte.get("se") or {}).items()):
                    p[parte["campo"]] = R.get(parte["campo"], sempre if parte["campo"] == "sempre_in_italia" else NON_SO)
        elif q["campo"] == "nucleo":
            p["nucleo"] = [{"eta": c["eta"]} for c in R["nucleo"]]
        elif q.get("per_componente"):
            nome = q["campo"].split(".")[1]
            for c in q["componenti"]:
                p["nucleo"][c["indice"]][nome] = R["nucleo"][c["indice"]].get(nome, NON_SO)
        else:
            v = R.get(q["campo"], NON_SO)
            p[q["campo"]] = v[0] if q["tipo"] in ("scelta", "comune", "si_no", "data") and isinstance(v, list) else v
    raise RuntimeError(f"il questionario non si ferma per {persona['id']}")


def possibili(out):
    vicine = set(out.get("regioni_vicine") or [])
    tieni = lambda r: not r.get("regione") or r["regione"] in vicine
    spettano = [r for r in out["risultati"] if r["stato"] in ("idoneo", "idoneo, salvo eccezioni") and tieni(r)]
    forse = [r for r in out["risultati"] if r["stato"] == "da verificare" and r.get("a_favore") and tieni(r)]
    return spettano, forse


def main(giorno):
    casi = []
    ultimo, vero_profilo = {}, {}
    vero = d.passo

    def spia(ramo, profilo, g, estratte=False):
        ultimo["p"] = profilo
        return vero(ramo, profilo, g, estratte)
    d.passo = spia
    for persona in yaml.safe_load((ROOT / "prove" / "simulazione" / "persone.yaml").read_text(encoding="utf-8"))["persone"]:
        chieste, out = rispondi(persona, giorno)
        casi.append((persona["id"], len(chieste), out, dict(ultimo["p"])))
        vero_profilo[persona["id"]] = persona["risposte"]
    d.passo = vero
    for profilo in d.profili_demo():
        casi.append((f"demo: {profilo['nome']}", None, d.passo("persone", profilo["profilo"], giorno, True), profilo["profilo"]))
    righe = [f"# Simulazione della demo del {giorno}\n",
             "*Generato da `prove/simulazione/riepilogo.py`: non modificare a mano. Le persone di prova sono in "
             "`prove/simulazione/persone.yaml`; i profili della demo sono già completi, quindi non fanno domande. "
             "\"Possibili\" sono quelli con almeno un requisito a favore, nazionali o delle regioni vicine (decisioni 70, 78).*\n",
             "\"Dopo le verifiche\": la persona risponde alle verifiche finali con i suoi dati veri (decisione 94); le "
             "condizioni che nessun dato dice (per esempio \"figlio al nido\") valgono sì, quindi è un massimo.\n",
             "| persona | domande | ti spetta | possibili | verifiche finali | ti spetta dopo le verifiche |",
             "|---|---|---|---|---|---|"]
    dettagli = []
    for nome, n, out, profilo in casi:
        spettano, forse = possibili(out)
        conferme = d.risposte_vere(out.get("verifiche", []), vero_profilo.get(nome, profilo), giorno)
        dopo, _ = possibili(d.passo("persone", dict(profilo, conferme=conferme), giorno, True)) if conferme else (spettano, None)
        righe.append(f"| {nome} | {n if n is not None else '-'} | {len(spettano)} | {len(forse)} | {len(out.get('verifiche', []))} | {len(dopo)} |")
        dettagli.append(f"\n### {nome}\n")
        dettagli += [f"- **ti spetta:** {r['titolo'][:90]} ({r.get('ente')})" for r in spettano]
        dettagli += [f"- possibile: {r['titolo'][:90]} ({r.get('ente')})" for r in forse]
    testo = "\n".join(righe + ["\n## Dettaglio, da giudicare a mano: pertinente sì/no"] + dettagli) + "\n"
    uscita = ROOT / "docs" / f"simulazione-{giorno}.md"
    uscita.write_text(testo, encoding="utf-8")
    print(f"{uscita.relative_to(ROOT)} scritto")
    print("\n".join(righe[3:]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else d.dt.date.today().isoformat())
