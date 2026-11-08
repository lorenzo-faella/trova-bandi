"""Inventario degli enti: tipo dal nome e copertura contata bando per bando, non ente per ente."""
from pipeline.fonti import inventario as inv


def test_tipo_dal_nome():
    assert inv.tipo("Camera di Commercio Industria Artigianato e Agricoltura di Foggia") == "Camera di commercio"
    assert inv.tipo("Comune di Pistoia") == "Comune o unione di comuni"
    assert inv.tipo("Regione Puglia") == "Regione o Provincia autonoma"
    assert inv.tipo("Puglia Sviluppo S.p.A.") == "Finanziaria o agenzia di sviluppo"
    assert inv.tipo("Agenzia veneta per i pagamenti in agricoltura - AVEPA") == "Agricoltura (organismo pagatore, PSR)"


def test_copertura_bando_per_bando():
    export = [{"Regioni": ["Marche"], "Soggetto_Concedente": ["Regione Marche"], "Link_istituzionale": u,
               "Data_apertura": "2026-01-01", "Data_chiusura": "2026-12-31"}
              for u in ["https://www.regione.marche.it/a", "https://www.regione.marche.it/b", "https://www.fondazionemarchecultura.it/c"]]
    documenti = [{"regione": "Marche", "url": "https://www.fondazionemarchecultura.it/bandi/x/", "fonte_elenco": "marche-fmc"},
                 {"regione": "Marche", "url": "https://www.regione.marche.it/prova", "fonte_elenco": None}]  # una prova non conta
    [e] = inv.inventario(export, documenti, "2026-11-07")[0]["Marche"]
    assert (e["aperti"], e["aperti_coperti"], e["stato"]) == (3, 1, "in parte")


def test_i_bandi_presi_dal_portale_si_contano_a_parte():
    export = [{"Regioni": ["Trentino-Alto Adige/Südtirol"], "Soggetto_Concedente": ["Provincia Autonoma di Trento"],
               "Link_istituzionale": u, "Data_apertura": "2026-01-01", "Data_chiusura": "2026-12-31"}
              for u in ["https://www.provincia.tn.it/Servizi/A#accedere", "https://www.provincia.tn.it/Servizi/B"]]
    documenti = [{"regione": "Trentino-Alto Adige", "url": "https://www.provincia.tn.it/Servizi/A", "fonte_elenco": "trento-portale"}]
    [e] = inv.inventario(export, documenti, "2026-11-08", {"trento-portale"})[0]["Trentino-Alto Adige"]
    # il sito non è sorvegliato (non vediamo i bandi nuovi), ma il bando A lo abbiamo, anche col "#..." nel link
    assert (e["aperti"], e["aperti_coperti"], e["aperti_dal_portale"], e["stato"]) == (2, 0, 1, "no")
