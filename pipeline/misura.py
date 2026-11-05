"""Stadio 5: quanto presto il questionario decide i bandi? -> docs/misura-questionario.md

Confronta, su imprese fittizie diverse da quelle usate per stimare le risposte:
  - modulo fisso nell'ordine del portale;
  - miglior ordine fisso: la permutazione delle 7 domande che, sul campione di stima, decide più bandi
    in media lungo tutto il percorso (ricerca esaustiva sulle 5.040 permutazioni);
  - questionario adattivo (greedy);
  - oracolo: per ogni k, le k domande migliori per quella specifica impresa (conosce già le risposte).
Uso: python -m pipeline.misura AAAA-MM-GG
"""
import sys
import time
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

import numpy as np
import yaml

from pipeline.motore import aperta, valuta_tutte
from pipeline.profili import Generatore
from pipeline.questionario import DOMANDE, Questionario
from pipeline.regole import carica

ROOT = Path(__file__).resolve().parent.parent
N_STIMA, N_VALUTAZIONE, N_ORDINE = 1000, 300, 200
SOTTOINSIEMI = [A for k in range(len(DOMANDE) + 1) for A in combinations(DOMANDE, k)]


def decisi_per_sottoinsieme(Q, utenti):
    """[utenti x sottoinsiemi]: bandi determinati sapendo le risposte a quel sottoinsieme di domande."""
    out = np.zeros((len(utenti), len(SOTTOINSIEMI)))
    for i, u in enumerate(utenti):
        Mu = Q.matrici([u])
        out[i] = [Q.stato(Mu, A)[0].sum() for A in SOTTOINSIEMI]
    return out


def curva_ordine(D, ordine):
    pos = {frozenset(A): j for j, A in enumerate(SOTTOINSIEMI)}
    return np.stack([D[:, pos[frozenset(ordine[:k])]] for k in range(len(DOMANDE) + 1)], axis=1)


def curva_simulata(Q, u, ordine):
    Mu = Q.matrici([u])
    c = [Q.stato(Mu, ordine[:k])[0].sum() for k in range(len(ordine) + 1)]
    return c + [c[-1]] * (len(DOMANDE) + 1 - len(c))


def main(giorno):
    regole = [r for r in carica() if aperta(r, giorno)]
    B = len(regole)
    t = time.time()
    Q = Questionario(regole, Generatore(regole, seed=1).campione(N_STIMA))
    t_init = time.time() - t
    utenti = Generatore(regole, seed=2).campione(N_VALUTAZIONE)

    # miglior ordine fisso, scelto sul campione di stima e non su quello di valutazione
    D_stima = decisi_per_sottoinsieme(Q, Q.campione[:N_ORDINE])
    migliore = max(permutations(DOMANDE), key=lambda o: curva_ordine(D_stima, o).sum(axis=1).mean())

    D = decisi_per_sottoinsieme(Q, utenti)
    curve = {
        "modulo fisso (ordine del portale)": curva_ordine(D, DOMANDE),
        "miglior ordine fisso": curva_ordine(D, migliore),
    }
    t = time.time()
    percorsi = [Q.simula(u, "adattivo") for u in utenti]
    t_adattivo = (time.time() - t) / sum(len(p) for p in percorsi)
    curve["questionario adattivo"] = np.array([curva_simulata(Q, u, p) for u, p in zip(utenti, percorsi)])
    curve["oracolo (conosce le risposte)"] = np.stack(
        [D[:, [j for j, A in enumerate(SOTTOINSIEMI) if len(A) == k]].max(axis=1) for k in range(len(DOMANDE) + 1)],
        axis=1)
    per_tutto = {
        "modulo fisso (ordine del portale)": [len(Q.simula(u, "fisso")) for u in utenti],
        "questionario adattivo": [len(p) for p in percorsi],
        "oracolo (conosce le risposte)": [len(Q.minimo(u)) for u in utenti],
    }
    esiti = Counter(e.stato for u in utenti for e in valuta_tutte(regole, u))
    manuali = yaml.safe_load((ROOT / "data" / "profili" / "manuali.yaml").read_text(encoding="utf-8"))

    righe = [
        "# Misura del questionario adattivo",
        "",
        f"*Generato da `pipeline/misura.py` il {time.strftime('%Y-%m-%d')}: non modificare a mano.*",
        "",
        f"- Bandi aperti il {giorno} e accessibili a imprese: **{B}**.",
        f"- Risposte stimate su {N_STIMA} imprese fittizie (seed 1); misura su altre {N_VALUTAZIONE} (seed 2).",
        f"- Un bando è *deciso* quando sappiamo già se l'impresa è idonea o no.",
        "",
        "## Bandi decisi dopo k domande (media, % dei bandi)",
        "",
        "| strategia | " + " | ".join(f"k={k}" for k in range(1, len(DOMANDE) + 1)) + " |",
        "|---|" + "---|" * len(DOMANDE),
    ]
    for nome, C in curve.items():
        righe.append(f"| {nome} | " + " | ".join(f"{100 * x / B:.1f}" for x in C.mean(axis=0)[1:]) + " |")
    righe += [
        "",
        f"Miglior ordine fisso trovato: {' → '.join(migliore)}.",
        f"Ordine del portale: {' → '.join(DOMANDE)}.",
        "",
        "## Domande necessarie per decidere tutto ciò che si può decidere",
        "",
        "| strategia | media | massimo |",
        "|---|---|---|",
    ]
    righe += [f"| {nome} | {np.mean(v):.2f} | {max(v)} |" for nome, v in per_tutto.items()]
    righe += [
        "",
        "## Esiti medi per impresa",
        "",
        "| esito | bandi per impresa |",
        "|---|---|",
    ]
    righe += [f"| {s} | {n / N_VALUTAZIONE:.1f} |" for s, n in esiti.most_common()]
    righe += [
        "",
        "## Imprese scritte a mano",
        "",
        "| impresa | domande (ordine adattivo) | idoneo | quasi | mancano dati |",
        "|---|---|---|---|---|",
    ]
    for nome, p in manuali.items():
        c = Counter(e.stato for e in valuta_tutte(regole, p))
        righe.append(f"| {nome} | {', '.join(Q.simula(p, 'adattivo'))} | {c['idoneo']} | {c['quasi idoneo']} "
                     f"| {c['mancano dati']} |")
    righe += [
        "",
        "## Tempi",
        "",
        f"- Preparazione delle matrici: {t_init:.1f} s (una volta all'avvio).",
        f"- Scelta di una domanda: {1000 * t_adattivo:.0f} ms in media.",
    ]
    out = ROOT / "docs" / "misura-questionario.md"
    out.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"{out.relative_to(ROOT)} scritto ({B} bandi, {N_VALUTAZIONE} imprese)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("uso: python -m pipeline.misura AAAA-MM-GG")
    main(sys.argv[1])
