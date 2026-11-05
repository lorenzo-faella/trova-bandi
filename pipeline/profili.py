"""Generatore di imprese fittizie, per misurare il questionario e per i test.

I codici ATECO dei profili sono presi tra le classi (NN.NN) che compaiono nei bandi in versione 2025:
codici reali, nella versione che le imprese hanno oggi.
"""
import random
from pathlib import Path

import yaml

from pipeline.normalizza import carica_comuni_istat

ROOT = Path(__file__).resolve().parent.parent
DISTRIBUZIONI = ROOT / "data" / "profili" / "distribuzioni.yaml"


def tipologie(forma, car):
    if forma == "impresa":
        t = ["Impresa"]
        t += ["Impresa - prevalenza femminile"] if car["femminile"] else []
        t += ["Impresa - prevalenza giovanile"] if car["giovanile"] else []
        t += ["Impresa - SU/PMI innovativa"] if car["innovativa"] else []
        return t
    if forma == "da_costituire":
        # "Altro" letto come "impresa da costituire generica": vale anche per quelle femminili e giovanili
        t = ["Impresa da costituire - Altro"]
        t += ["Impresa da costituire - Femminile"] if car["femminile"] else []
        t += ["Impresa da costituire - Giovanile"] if car["giovanile"] else []
        return t
    return {"professionista": ["Professionista"], "cooperativa": ["Cooperative/Associazioni Non Profit", "Impresa"],
            "consorzio": ["Consorzio"], "rete": ["Rete d'impresa"]}[forma]


class Generatore:
    def __init__(self, regole, seed):
        self.rng = random.Random(seed)
        self.d = yaml.safe_load(DISTRIBUZIONI.read_text(encoding="utf-8"))
        istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))[-1]
        self.comuni = {}
        for nome, regione in set(carica_comuni_istat(istat).values()):
            self.comuni.setdefault(regione, []).append(nome)
        for lista in self.comuni.values():
            lista.sort()
        classi = sorted({c for r in regole for q in r["requisiti"] if q["campo"] == "ateco_2025"
                         for c in q["valori"] if len(c) == 5})
        self.ateco = {}  # settore -> classi ATECO 2025 delle sue divisioni
        for settore, info in self.d["settori"].items():
            self.ateco[settore] = [c for c in classi if c[:2] in info["divisioni"]]
        # un settore senza classi note non può generare un codice: lo escludiamo invece di inventarlo
        self.settori = {s: i["peso"] for s, i in self.d["settori"].items() if self.ateco[s]}

    def scegli(self, pesi):
        return self.rng.choices(list(pesi), weights=list(pesi.values()))[0]

    def profilo(self):
        forma = self.scegli(self.d["forma"])
        car = {k: self.rng.random() < p for k, p in self.d["caratteristiche"].items()}
        if forma in ("professionista", "da_costituire"):
            # da costituire = la dimensione che avrà: 43 dei 54 bandi aperti per imprese da costituire
            # elencano solo dimensioni vere, quindi "Non classificabile" le escluderebbe per errore
            dimensione = "Microimpresa"
        else:
            dimensione = self.scegli(self.d["dimensione"])
        regione = self.scegli(self.d["regione"])
        settore = self.scegli(self.settori)
        return {
            "tipologia": tipologie(forma, car),
            "dimensione": dimensione,
            "regione": regione,
            "comune": self.rng.choice(self.comuni[regione]),
            "settore": [settore] + (["Artigianato"] if self.rng.random() < self.d["artigiana"] else []),
            "ateco_2025": self.rng.choice(self.ateco[settore]),
            "ambito": [a for a, p in self.d["ambiti"].items() if self.rng.random() < p],
        }

    def campione(self, n):
        return [self.profilo() for _ in range(n)]
