"""Le regole da rivedere a mano per prime: quelle che compaiono più spesso alle persone di prova (decisione 97).

Per le 4 persone di `persone.yaml` e i 4 profili della demo conta in quanti casi una regola è "ti spetta", "possibile"
(nazionale o della zona, con almeno un requisito a favore) o fra le verifiche finali. Scrive docs/da-rivedere-a-mano.md:
la revisione si fa senza LLM, aprendo il link e confrontando requisiti e citazioni.

Uso: PYTHONPATH=. python prove/simulazione/da_rivedere.py [AAAA-MM-GG]
"""
import collections
import sys
from pathlib import Path

import yaml

from web import domande as d

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "prove" / "simulazione"))
import riepilogo  # noqa: E402


def main(giorno, quante=30):
    casi = [riepilogo.rispondi(p, giorno)[1] for p in
            yaml.safe_load((ROOT / "prove" / "simulazione" / "persone.yaml").read_text(encoding="utf-8"))["persone"]]
    casi += [d.passo("persone", p["profilo"], giorno, True) for p in d.profili_demo() if p.get("ramo", "persone") == "persone"]
    conta, titolo = collections.Counter(), {}
    for out in casi:
        spettano, forse = riepilogo.possibili(out)
        visti = {r["id"]: r for r in spettano + forse} | {v["id"]: v for v in out.get("verifiche", [])}
        for i, r in visti.items():
            conta[i] += 1
            titolo[i] = r["titolo"]
    regole = {r["id"]: r for r in d.regole_persone(True)}
    righe = [f"# Regole da rivedere a mano per prime ({giorno})\n",
             "*Generato da `prove/simulazione/da_rivedere.py`: le regole che compaiono più spesso alle {len(casi)} persone di prova "
             "(\"ti spetta\", possibili o verifiche finali). Per ognuna: aprire il link, controllare che requisiti e citazioni "
             "corrispondano al bando, correggere a mano e segnare l'esito qui (giusta / errori piccoli / sbagliata). "
             "Niente LLM (decisione 97).*\n",
             "| # | volte | regola | origine | file | esito |", "|---|---|---|---|---|---|"]
    for n, (i, k) in enumerate(conta.most_common(quante), 1):
        r = regole.get(i, {})
        righe.append(f"| {n} | {k}/{len(casi)} | [{titolo[i][:70]}]({r.get('link', '')}) | {r.get('_origine', '?')} | `{i}` | |")
    uscita = ROOT / "docs" / "da-rivedere-a-mano.md"
    uscita.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"{uscita.relative_to(ROOT)} scritto: {len(conta)} regole viste, prime {quante}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-11-22")
