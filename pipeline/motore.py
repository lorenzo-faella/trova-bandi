"""Stadio 4a: valutazione di un profilo d'impresa rispetto alle regole, con logica a tre valori.

Ogni requisito vale True (soddisfatto), False (non soddisfatto) o None (non si può dire: dato mancante,
codice ATECO troppo generico, comune fuori da un elenco che contiene comuni soppressi).
Profilo: dict campo -> valore. tipologia, settore e ambito sono liste (un'impresa può essere sia
"Impresa" sia "Impresa - prevalenza femminile"); gli altri campi sono stringhe. Campo assente = non risposto.
"""
from dataclasses import dataclass, field

IDONEO, QUASI, NON_IDONEO, MANCANO_DATI = "idoneo", "quasi idoneo", "non idoneo", "mancano dati"
# "Quasi idoneo" ha senso solo se il requisito mancato si può cambiare (aggiungere un codice ATECO,
# costituire l'impresa); la sede no: altrimenti metà dei bandi regionali d'Italia risulterebbe "quasi".
MODIFICABILI = {"tipologia", "settore", "ateco_2025", "ateco_2007"}


def cifre(codice):
    return codice.replace(".", "")


def verifica(req, profilo):
    v = profilo.get(req["campo"])
    if v is None:
        return None
    valori = req["valori"]
    op = req["operatore"]
    if op == "in":
        if v in valori:
            return True
        return None if req.get("incerto_fuori_elenco") else False
    if op == "interseca":
        return bool(set(v) & set(valori))
    if op == "prefisso":
        # ATECO è gerarchico sulle cifre: 56 > 56.1 > 56.10 > 56.10.1
        mio = cifre(v)
        if any(mio.startswith(cifre(c)) for c in valori):
            return True
        if any(cifre(c).startswith(mio) for c in valori):
            return None  # il profilo dice "56", il bando chiede "56.10": serve il codice completo
        return False
    raise ValueError(f"operatore sconosciuto: {op}")


@dataclass
class Esito:
    regola: dict
    stato: str
    falliti: list = field(default_factory=list)
    mancanti: list = field(default_factory=list)


def valuta(regola, profilo):
    falliti, mancanti = [], []
    for req in regola["requisiti"]:
        r = verifica(req, profilo)
        if r is False:
            falliti.append(req)
        elif r is None:
            mancanti.append(req)
    if not falliti:
        stato = MANCANO_DATI if mancanti else IDONEO
    else:
        # "quasi" solo se tutto il resto è verificato: con dati mancanti non sappiamo se manca uno solo
        quasi = len(falliti) == 1 and not mancanti and falliti[0]["campo"] in MODIFICABILI
        stato = QUASI if quasi else NON_IDONEO
    return Esito(regola, stato, falliti, mancanti)


def aperta(regola, giorno):
    return (not regola["apertura"] or regola["apertura"] <= giorno) and \
        (not regola["chiusura"] or regola["chiusura"] >= giorno)


def valuta_tutte(regole, profilo, giorno=None):
    return [valuta(r, profilo) for r in regole if giorno is None or aperta(r, giorno)]
