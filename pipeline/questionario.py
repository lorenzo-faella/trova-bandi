"""Stadio 4b: questionario adattivo.

Un bando è "determinato" quando sappiamo già se l'impresa è idonea: un requisito fallito basta per il no,
per il sì servono tutti. A ogni passo scegliamo la domanda che in media determina più bandi, stimando
le risposte possibili da un campione di imprese fittizie coerenti con le risposte già date.
Costruire l'albero di domande ottimo è NP-difficile; questa è la scelta greedy, un passo alla volta.

Tutto lavora su matrici bandi x profili, una per domanda: 1 requisito soddisfatto (o assente), 0 no, -1 incerto.
"""
from itertools import combinations

import numpy as np

from pipeline.motore import verifica

# Ordine del modulo fisso, lo stesso dei filtri del portale.
DOMANDE = ["tipologia", "dimensione", "regione", "comune", "settore", "ateco_2025", "ambito"]
# Con meno profili coerenti di così la stima è rumorosa: si ignorano le condizioni più recenti.
MIN_CAMPIONE = 30


def chiave(v):
    return tuple(sorted(v)) if isinstance(v, list) else v


class Questionario:
    def __init__(self, regole, campione):
        self.regole = regole
        B = len(regole)
        self.ha_req = {c: np.zeros(B, bool) for c in DOMANDE}
        # ATECO 2007 non si chiede: un'impresa oggi conosce il suo codice 2025 (manca la tavola di raccordo)
        self.bloccati = np.array([any(q["campo"] == "ateco_2007" for q in r["requisiti"]) for r in regole])
        for b, r in enumerate(regole):
            for q in r["requisiti"]:
                if q["campo"] in self.ha_req:
                    self.ha_req[q["campo"]][b] = True
        self.campione = campione
        self.ids, self.vocab = {}, {}
        for c in DOMANDE:
            self.vocab[c] = {}
            self.ids[c] = np.array([self.vocab[c].setdefault(chiave(p.get(c)), len(self.vocab[c]))
                                    for p in campione])
        self.M = self.matrici(campione)

    def matrici(self, profili):
        """Valuta ogni requisito una sola volta per valore distinto, non per profilo."""
        B, N = len(self.regole), len(profili)
        M = {c: np.ones((B, N), np.int8) for c in DOMANDE}
        for c in DOMANDE:
            valori = {}
            for p in profili:
                valori.setdefault(chiave(p.get(c)), p.get(c))
            pos = {k: i for i, k in enumerate(valori)}
            idx = np.array([pos[chiave(p.get(c))] for p in profili])
            for b in np.flatnonzero(self.ha_req[c]):
                req = next(q for q in self.regole[b]["requisiti"] if q["campo"] == c)
                esiti = np.array([{True: 1, False: 0, None: -1}[verifica(req, {c: v})] for v in valori.values()],
                                 np.int8)
                M[c][b] = esiti[idx]
        return M

    def stato(self, Mu, chieste):
        """Mu: matrici dell'utente (B x 1). Restituisce (determinati, ancora risolvibili, mancanti per bando)."""
        B = len(self.regole)
        fallito, incerto = np.zeros(B, bool), np.zeros(B, bool)
        for c in chieste:
            fallito |= Mu[c][:, 0] == 0
            incerto |= Mu[c][:, 0] == -1
        mancanti = sum(self.ha_req[c].astype(int) for c in DOMANDE if c not in chieste)
        determinati = fallito | ((mancanti == 0) & ~incerto & ~self.bloccati)
        return determinati, ~determinati & (mancanti > 0), mancanti, incerto

    def coerenti(self, risposte):
        maschera = np.ones(len(self.campione), bool)
        for c, v in risposte.items():  # nell'ordine in cui sono state date
            m = maschera & (self.ids[c] == self.vocab[c].get(chiave(v), -1))
            if m.sum() >= MIN_CAMPIONE:
                maschera = m
        return maschera

    def prossima(self, risposte, Mu):
        det, aperti, mancanti, incerto = self.stato(Mu, risposte)
        if not aperti.any():
            return None
        cols = self.coerenti(risposte)
        migliore, punteggio = None, (-1, -1)
        for c in DOMANDE:
            if c in risposte:
                continue
            rel = aperti & self.ha_req[c]
            if not rel.any():
                continue
            ultima = (mancanti[rel] == 1) & ~incerto[rel] & ~self.bloccati[rel]  # c è l'unico dato che manca
            S = self.M[c][np.ix_(rel, cols)]
            risolti = (S == 0) | ((S == 1) & ultima[:, None])
            p = (risolti.sum(0).mean(), rel.sum())  # a parità di guadagno, la domanda che tocca più bandi
            if p > punteggio:
                migliore, punteggio = c, p
        return migliore

    def simula(self, utente, strategia):
        """Domande fatte a `utente` (profilo completo, che risponde sempre) fino a determinare ciò che si può."""
        Mu = self.matrici([utente])
        risposte = {}
        while True:
            if strategia == "adattivo":
                c = self.prossima(risposte, Mu)
            else:  # ordine fisso, saltando solo le domande che non servono più a nessun bando
                _, aperti, _, _ = self.stato(Mu, risposte)
                c = next((c for c in DOMANDE if c not in risposte and (aperti & self.ha_req[c]).any()), None)
            if c is None:
                return list(risposte)
            risposte[c] = utente.get(c)

    def minimo(self, utente):
        """Limite inferiore: il minimo numero di domande se conoscessimo già le risposte (128 sottoinsiemi)."""
        Mu = self.matrici([utente])
        for k in range(len(DOMANDE) + 1):
            for A in combinations(DOMANDE, k):
                if not self.stato(Mu, A)[1].any():
                    return list(A)
