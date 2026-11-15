"""A chi si rivolge un bando (pipeline/fonti/pubblico.py, decisione 61). Senza rete e senza i testi raccolti."""
from pipeline.fonti.pubblico import classifica


def doc(titolo, testo=""):
    return {"id": "x", "titolo": titolo, "pagine": [testo]}


def test_titolo_da_solo_dice_persone():
    c = classifica(doc("Borsa di studio"))
    assert c["pubblico"] == "persone" and c["metodo"] == "titolo (persone)"
    assert classifica(doc("Bando E.R.P. – comune di Dolo"))["pubblico"] == "persone"


def test_bando_di_concorso_per_borse_non_e_un_concorso_per_personale():
    assert classifica(doc("Bando di concorso per l'assegnazione di borse di studio a.a. 2026/2027"))["pubblico"] == "persone"


def test_titolo_persone_che_nomina_enti_passa_alla_sezione():
    t = "Beneficiari\nPossono presentare domanda gli enti del terzo settore con sede in regione."
    c = classifica(doc("Contributi per gli enti del Terzo settore - Centri estivi 2026", t))
    assert c["pubblico"] == "enti" and c["metodo"] == "sezione destinatari"


def test_gare_e_albi_non_sono_bandi():
    assert classifica(doc("AD 106/2025 - Fornitura e consegna di gadget"))["pubblico"] == "non_bando"
    assert classifica(doc("Elenco commissari ITS - Iscrizione"))["pubblico"] == "non_bando"


def test_sezione_destinatari_vince_il_gruppo_nominato_per_primo():
    t = ("Art. 2 Beneficiari\nUniversità pubbliche statali con sede in Toscana, in partenariato con imprese. "
         "I progetti si rivolgono a giovani laureati.")
    c = classifica(doc("Cosa fare dopo la laurea, progetti di orientamento", t))
    assert c["pubblico"] == "enti"
    assert c["anche"] == ["imprese", "persone"]


def test_intestazione_fissa_del_veneto_non_conta():
    t = "Destinatari cittadino ente impresa Materie agricoltura. Testo senza altri destinatari."
    assert classifica(doc("Utilizzo beni del Demanio Idrico", t))["pubblico"] == "dubbio"


def test_senza_indizi_resta_dubbio():
    assert classifica(doc("Prova di pubblicazione"))["pubblico"] == "dubbio"
