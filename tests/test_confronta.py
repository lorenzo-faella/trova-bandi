"""Il misuratore va provato prima di fidarsi dei suoi numeri: deve accorgersi degli errori che dichiara di misurare."""
import copy

import pytest

from pipeline.citazioni import forme, in_lettere, nodi, soglie_non_trovate
from pipeline.confronta import comportamento, foglie, persone, struttura
from pipeline.motore import verifica
from pipeline.regole import DIR_PERSONE, carica


@pytest.fixture(scope="module")
def R():
    return {r["id"]: r for r in carica(DIR_PERSONE)}


def regola(*requisiti):
    return {"requisiti": list(requisiti)}


ISEE = {"campo": "isee", "operatore": "<=", "valore": 40000}
ETA = {"campo": "eta", "operatore": "<", "valore": 18}


def test_regola_identica(R):
    for r in R.values():
        s, c = struttura(r, r), comportamento(r, r, n=1000)
        assert s["precisione"] == s["richiamo"] == 1 and not s["sbagliate"] and not s["mancate"] and not s["in_piu"]
        assert c["accordo"] == 1 and c["falsi_si"] == c["falsi_no"] == 0
        assert c["non_banali"] > 50, r["id"]  # altrimenti l'accordo non dice niente


def test_lo_stesso_seme_da_gli_stessi_profili(R):
    r = [R["inps-adi"]]
    assert list(persone(r, 50)) == list(persone(r, 50))


def test_interi_equivalenti_sono_la_stessa_condizione():
    assert foglie(regola(ETA)) == foglie(regola({"campo": "eta", "operatore": "<=", "valore": 17}))
    assert foglie(regola({"campo": "eta", "operatore": ">", "valore": 59})) == foglie(regola({"campo": "eta", "operatore": ">=", "valore": 60}))
    # sugli euro no: 10.000,50 distingue le due
    assert foglie(regola({"campo": "isee", "operatore": "<", "valore": 100})) != foglie(regola({"campo": "isee", "operatore": "<=", "valore": 99}))


def test_struttura_classifica_gli_errori():
    rif = regola(ISEE, ETA, {"campo": "disabile", "operatore": "vero"})
    est = regola({**ISEE, "valore": 30000}, ETA, {"campo": "residente_italia", "operatore": "vero"})
    s = struttura(rif, est)
    assert s["giuste"] == {("eta", "<=", 17)}
    assert s["sbagliate"] == {("isee", "<=", 30000)}
    assert s["in_piu"] == {("residente_italia", "vero", None)}
    assert s["mancate"] == {("disabile", "vero", None)}
    assert s["precisione"] == pytest.approx(1 / 3) and s["richiamo"] == pytest.approx(1 / 3)


def test_soglia_troppo_bassa_e_un_falso_no():
    c = comportamento(regola(ISEE), regola({**ISEE, "valore": 30000}), n=500)
    assert c["falsi_no"] > 0 and c["falsi_si"] == 0 and c["accordo"] < 1


def test_requisito_dimenticato_e_un_falso_si():
    c = comportamento(regola(ISEE, ETA), regola(ISEE), n=500)
    assert c["falsi_si"] > 0 and c["falsi_no"] == 0


def test_regola_che_esclude_tutti_non_sembra_buona():
    sempre_no = regola({"tutti_di": [{"campo": "eta", "operatore": "<=", "valore": 1}, {"campo": "eta", "operatore": ">=", "valore": 2}]})
    c = comportamento(regola(ISEE), sempre_no, n=500)
    assert c["accordo"] < 0.05  # coincidono solo i rari casi in cui mancano i dati a entrambe


def test_idoneo_senza_riserve_al_posto_di_da_verificare():
    c = comportamento(regola(ISEE, {"non_modellabile": "x"}), regola(ISEE), n=500)
    assert c["troppo_sicura"] > 0 and c["falsi_si"] == c["falsi_no"] == 0
    assert comportamento(regola(ISEE), regola(ISEE, {"non_modellabile": "x"}), n=500)["piu_cauta"] > 0


def test_ogni_soglia_alterata_viene_notata(R):
    """Mutazione: si raddoppia ogni soglia delle 5 regole, una alla volta; il confronto deve vedere ogni modifica."""
    provate = 0
    for r in R.values():
        for i, req in enumerate(r["requisiti"]):
            for j, n in enumerate(nodi(req)):
                if not isinstance(n.get("valore"), (int, float)):
                    continue
                mutata = copy.deepcopy(r)
                list(nodi(mutata["requisiti"][i]))[j]["valore"] = n["valore"] * 2 + 1
                assert comportamento(r, mutata, n=3000)["accordo"] < 1, (r["id"], n)
                assert struttura(r, mutata)["sbagliate"] or struttura(r, mutata)["in_piu"], (r["id"], n)
                provate += 1
    assert provate >= 10


def test_ogni_requisito_tolto_viene_notato(R):
    """Tranne chi non può mai escludere nessuno (permesso speciale oppure non modellabile): se resta un altro
    "da verificare", toglierlo non cambia nessun esito. Per questo la misura riporta anche i non modellabili."""
    provati = 0
    for r in R.values():
        for i, req in enumerate(r["requisiti"]):
            if not any(verifica(req, p) is False for p in persone([r], 3000)):
                continue
            senza = copy.deepcopy(r)
            del senza["requisiti"][i]
            assert comportamento(r, senza, n=3000)["accordo"] < 1, (r["id"], i)
            provati += 1
    assert provati >= 15


@pytest.mark.parametrize("n, parola", [(1, "uno"), (13, "tredici"), (18, "diciotto"), (21, "ventuno"), (23, "ventitré"),
                                       (60, "sessanta"), (68, "sessantotto"), (70, "settanta")])
def test_numeri_in_lettere(n, parola):
    assert in_lettere(n) == parola


def test_forme_dei_numeri():
    assert {"10140", "10.140"} <= forme(10140)
    assert {"40000", "40.000", "40mila", "40 mila"} <= forme(40000)
    assert "9,5" in forme(9.5)


def test_soglie_non_trovate():
    r = regola({**ISEE}, {"campo": "eta", "operatore": "<", "valore": 18}, {"campo": "settimane_contributi_4_anni", "operatore": ">=", "valore": 13})
    assert soglie_non_trovate(r, "ISEE fino a 40mila euro, almeno tredici settimane") == ["eta < 18"]
    # un numero dentro un altro numero non conta
    assert soglie_non_trovate(regola({**ISEE, "valore": 140}), "soglia di 10.140 euro") == ["isee <= 140"]


def test_la_soglia_inventata_viene_segnalata_sulle_schede_vere(R):
    from pipeline.citazioni import carica_testi_inps
    testi = carica_testi_inps()
    r = copy.deepcopy(R["inps-bonus-nuovi-nati"])
    trovate = [n for req in r["requisiti"] for n in nodi(req) if n.get("campo") == "isee"]
    assert soglie_non_trovate(r, testi[r["link"]]) == []
    trovate[0]["valore"] = 41234
    assert soglie_non_trovate(r, testi[r["link"]]) == ["isee <= 41234"]
