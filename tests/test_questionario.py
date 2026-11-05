import numpy as np
import pytest

from pipeline.motore import MANCANO_DATI, aperta, valuta
from pipeline.profili import Generatore
from pipeline.questionario import DOMANDE, Questionario
from tests.conftest import GIORNO
from tests.test_motore import bando, req


def test_sceglie_la_domanda_che_decide_piu_bandi():
    # 3 bandi lombardi e 1 per giovani: chi non è lombardo chiude 3 bandi con una domanda
    regole = [bando(req("regione", "in", ["Lombardia"])) for _ in range(3)]
    regole.append(bando(req("tipologia", "interseca", ["Impresa - prevalenza giovanile"])))
    campione = [{"regione": r, "tipologia": ["Impresa"]} for r in ["Lazio", "Sicilia", "Veneto", "Lombardia"]] * 10
    Q = Questionario(regole, campione)
    Mu = Q.matrici([{"regione": "Lazio", "tipologia": ["Impresa"]}])
    assert Q.prossima({}, Mu) == "regione"
    assert Q.simula({"regione": "Lazio", "tipologia": ["Impresa"]}, "adattivo") == ["regione", "tipologia"]


def test_si_ferma_quando_tutto_e_deciso():
    regole = [bando(req("regione", "in", ["Lombardia"]))]
    Q = Questionario(regole, [{"regione": "Lazio"}] * 40)
    assert Q.simula({"regione": "Lazio"}, "adattivo") == ["regione"]
    assert Q.minimo({"regione": "Lazio"}) == ["regione"]


@pytest.fixture(scope="module")
def Q(regole):
    aperte = [r for r in regole if aperta(r, GIORNO)]
    return Questionario(aperte, Generatore(aperte, seed=1).campione(300))


def test_questionario_e_motore_concordano(Q):
    """Con tutte le risposte, un bando è deciso per il questionario sse il motore non dice 'mancano dati'."""
    for u in Generatore(Q.regole, seed=3).campione(20):
        decisi = Q.stato(Q.matrici([u]), DOMANDE)[0]
        attesi = np.array([valuta(r, u).stato != MANCANO_DATI for r in Q.regole])
        assert (decisi == attesi).all()


def test_oracolo_mai_peggio_del_greedy(Q):
    for u in Generatore(Q.regole, seed=4).campione(15):
        assert len(Q.minimo(u)) <= len(Q.simula(u, "adattivo")) <= len(DOMANDE)
