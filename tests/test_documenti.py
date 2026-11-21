"""Fonte generica (pagine web e PDF di regioni e comuni) ed estrattore per documenti, senza rete e senza modello."""
import json
import yaml
import urllib.error

import pytest

from pipeline import estrai_documenti as ed
from pipeline.fonti import documenti as dc

PAGINA = b"""<html><head><title>Bando affitti 2026</title><script>var x = 'non leggere';</script></head>
<body><nav>Home | Contatti</nav><header>Comune di Prova</header>
<main><h1>Contributo affitti 2026</h1><p>Possono partecipare i residenti nel Comune di Prova
con ISEE non superiore a 15.000&nbsp;euro.</p><ul><li>contratto registrato</li></ul></main>
<footer>Copyright</footer></body></html>"""

DOC = {"id": "comune-prova-affitti-2026", "titolo": "Contributo affitti 2026", "ente": "Comune di Prova",
       "url": "https://comune.prova.it/affitti", "tipo": "pdf",
       "pagine": ["Possono partecipare i residenti con ISEE non", "superiore a 15.000 euro."]}
ISEE = {"campo": "isee", "operatore": "<=", "valore": 15000, "fonte": "Comune di Prova, pagina 1",
        "citazione": "ISEE non superiore a 15.000 euro"}


def test_html_tiene_solo_il_contenuto_principale():
    d = dc.testo_html(PAGINA)
    testo = d["pagine"][0]
    assert d["titolo_pagina"] == "Bando affitti 2026"
    assert "ISEE non superiore a 15.000 euro" in testo  # &nbsp; diventa uno spazio normale
    assert "contratto registrato" in testo
    for fuori in ("Home | Contatti", "Copyright", "non leggere"):
        assert fuori not in testo
    assert testo.startswith("Contributo affitti 2026")  # l'intestazione del sito resta fuori


def test_html_senza_main_tiene_tutto_tranne_menu_e_script():
    testo = dc.testo_html(b"<body><nav>menu</nav><p>Requisito: essere residenti.</p><script>x</script></body>")["pagine"][0]
    assert testo == "Requisito: essere residenti."


def test_riconosce_i_pdf_dal_contenuto_anche_con_tipo_sbagliato():
    assert dc.e_pdf(b"%PDF-1.7 ...", "application/octet-stream")
    assert dc.e_pdf(b"xxxx", "application/pdf")
    assert not dc.e_pdf(b"<html>", "text/html; charset=utf-8")


class Risposta:
    def __init__(self, dati, tipo="text/html"):
        self.dati, self.headers = dati, {"Content-Type": tipo}

    def read(self, *a):
        return self.dati

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def rete(monkeypatch, tmp_path):
    """Finta rete: conta le richieste e risponde con robots.txt e pagine date."""
    monkeypatch.setattr(dc, "CACHE", tmp_path)
    monkeypatch.setattr(dc, "_robots", {})
    chiamate = []

    def imposta(robots=b"User-agent: *\nAllow: /\n", pagina=PAGINA, codice_robots=None, rete_giu=False):
        def urlopen(req, timeout=None):
            chiamate.append(req.full_url)
            if req.full_url.endswith("/robots.txt"):
                if rete_giu:
                    raise urllib.error.URLError("nome a dominio non risolto")
                if codice_robots:
                    raise urllib.error.HTTPError(req.full_url, codice_robots, "x", {}, None)
                return Risposta(robots, "text/plain")
            return Risposta(pagina)
        monkeypatch.setattr(dc.urllib.request, "urlopen", urlopen)
        return chiamate
    return imposta


def test_una_sola_richiesta_al_giorno_per_documento(rete):
    chiamate = rete()
    dc.scarica("https://comune.prova.it/affitti", "2026-11-07")
    dati, _, nota = dc.scarica("https://comune.prova.it/affitti", "2026-11-07")
    assert dati == PAGINA and nota == "dalla copia di oggi"
    assert chiamate == ["https://comune.prova.it/robots.txt", "https://comune.prova.it/affitti"]


def test_rispetta_robots(rete):
    rete(robots=b"User-agent: *\nDisallow: /\n")
    with pytest.raises(PermissionError):
        dc.scarica("https://regione.vieta.it/bandi", "2026-11-07")


def test_robots_protetto_vale_come_divieto_e_assente_come_permesso(rete):
    rete(codice_robots=403)
    with pytest.raises(PermissionError):
        dc.scarica("https://a.it/bando", "2026-11-07")
    rete(codice_robots=404)
    _, _, nota = dc.scarica("https://b.it/bando", "2026-11-07")
    assert nota == "robots.txt assente"


@pytest.mark.parametrize("guasto", [{"rete_giu": True}, {"codice_robots": 503}])
def test_robots_irraggiungibile_vale_come_divieto(rete, guasto):
    """RFC 9309: se robots.txt non si raggiunge (rete o 5xx) si considera tutto vietato. Prima si scaricava lo stesso."""
    chiamate = rete(**guasto)
    with pytest.raises(PermissionError, match="irraggiungibile"):
        dc.scarica("https://sito.giu.it/bando", "2026-11-07")
    assert chiamate == ["https://sito.giu.it/robots.txt"]  # la pagina non viene chiesta


@pytest.mark.parametrize("guasto", [{"rete_giu": True}, {"codice_robots": 503}, {"codice_robots": 403}, {"codice_robots": 404}])
def test_attesa_regge_ogni_stato_di_robots(rete, guasto):
    """elenchi.py chiama attesa() anche sui siti senza un robots.txt leggibile: lì vale la nostra pausa, senza errori."""
    rete(**guasto)
    assert dc.attesa("https://sito.prova.it/bando") == dc.PAUSA


def test_richiesta_numera_le_pagine():
    r = ed.richiesta(DOC)
    assert r.startswith('<documento titolo="Contributo affitti 2026" ente="Comune di Prova">')
    assert "[pagina 1]\nPossono partecipare" in r and "[pagina 2]\nsuperiore" in r


def test_prompt_contiene_istruzioni_vocabolario_e_aggiunta():
    p = ed.prompt(DOC)
    assert "## Vocabolario" in p and ed.AGGIUNTA in p and p.rstrip().endswith("</documento>")


def test_citazione_a_cavallo_di_due_pagine_e_valida():
    regola = ed.componi(DOC, {"requisiti": [ISEE], "apertura": "2026-11-01", "chiusura": "2026-12-15"}, "test")
    assert ed.errori(regola, DOC) == []
    assert (regola["apertura"], regola["chiusura"], regola["pubblico"]) == ("2026-11-01", "2026-12-15", "persone")


def test_citazione_inventata_e_data_sbagliata_rifiutate():
    inventata = {**ISEE, "citazione": "ISEE inferiore a 20.000 euro"}
    assert any("citazione assente" in e for e in ed.errori(ed.componi(DOC, {"requisiti": [inventata]}, "t"), DOC))
    assert ed.errori(ed.componi(DOC, {"requisiti": [ISEE], "chiusura": "15/12/2026"}, "t"), DOC)


def test_scansione_non_si_estrae():
    doc = {**DOC, "ocr_necessario": True}
    assert ed.errori(ed.componi(doc, {"requisiti": [ISEE]}, "t"), doc) == ["il documento è una scansione: serve l'OCR prima di estrarre"]


def test_importa_salva_solo_le_regole_accettate(tmp_path, monkeypatch):
    docs = tmp_path / "documenti"
    docs.mkdir()
    altro = {**DOC, "id": "comune-prova-altro"}
    for d in (DOC, altro):
        (docs / f"{d['id']}.json").write_text(json.dumps(d), encoding="utf-8")
    monkeypatch.setattr(ed, "DIR_DOCUMENTI", docs)
    lavoro, uscita = tmp_path / "lavoro", tmp_path / "uscita"
    lavoro.mkdir()
    (lavoro / f"{DOC['id']}.risposta.json").write_text(json.dumps({"requisiti": [ISEE]}), encoding="utf-8")
    sbagliata = {"requisiti": [{**ISEE, "citazione": "non c'è"}]}
    (lavoro / "comune-prova-altro.risposta.json").write_text(json.dumps(sbagliata), encoding="utf-8")
    assert ed.comando_importa(lavoro, uscita, [], "test") == 1
    assert sorted(f.name for f in uscita.iterdir()) == [f"{DOC['id']}.fonte.json", f"{DOC['id']}.yaml"]
    salvata = yaml.safe_load((uscita / f"{DOC['id']}.yaml").read_text())
    assert salvata['provenienza']['revisione_umana'] is None
    assert json.loads((uscita / f"{DOC['id']}.fonte.json").read_text()) == DOC
    assert (lavoro / "comune-prova-altro.errori.txt").exists()


def test_controlla_trova_le_regole_salvate_e_quelle_senza_documento(tmp_path, monkeypatch):
    docs = tmp_path / "documenti"
    docs.mkdir()
    (docs / f"{DOC['id']}.json").write_text(json.dumps(DOC), encoding="utf-8")
    monkeypatch.setattr(ed, "DIR_DOCUMENTI", docs)
    regole = tmp_path / "regole"
    ed.salva(ed.componi(DOC, {"requisiti": [ISEE]}, "t"), regole)
    assert ed.comando_controlla(regole) == 0
    orfana = {**ed.componi(DOC, {"requisiti": [ISEE]}, "t"), "id": "orfana", "link": "https://altro.it"}
    ed.salva(orfana, regole)
    assert ed.comando_controlla(regole) == 1


def test_indirizzi_con_caratteri_non_ascii(rete):
    chiamate = rete()
    dc.scarica("https://alfa.it/avviso-dell’art-50.html", "2026-11-07")
    assert chiamate[-1] == "https://alfa.it/avviso-dell%E2%80%99art-50.html"


def test_pdf_con_caratteri_spezzati_si_puo_salvare(monkeypatch):
    import json, sys, types
    from pipeline.fonti import documenti as dc
    pagina = types.SimpleNamespace(extract_text=lambda: "Bando \udd00 imprese " * 20)
    monkeypatch.setitem(sys.modules, "pypdf", types.SimpleNamespace(PdfReader=lambda f: types.SimpleNamespace(pages=[pagina])))
    testo = dc.testo_pdf(b"%PDF-")["pagine"][0]
    assert "\udd00" not in testo and "Bando ? imprese" in testo
    json.dumps(testo, ensure_ascii=False).encode("utf-8")  # prima qui: UnicodeEncodeError


def test_attesa_rispetta_crawl_delay_e_pausa_della_fonte(monkeypatch):
    import urllib.robotparser
    lento, normale = urllib.robotparser.RobotFileParser(), urllib.robotparser.RobotFileParser()
    lento.parse(["User-agent: *", "Crawl-delay: 10", "Disallow: /api/"])
    normale.parse(["User-agent: *", "Disallow: /api/"])
    monkeypatch.setattr(dc, "_robots", {"https://lento.it": lento, "https://normale.it": normale, "https://muto.it": None})
    assert dc.attesa("https://lento.it/bando") == 10
    assert dc.attesa("https://normale.it/bando") == dc.PAUSA
    assert dc.attesa("https://muto.it/bando") == dc.PAUSA  # robots.txt non leggibile: la nostra pausa
    assert dc.attesa("https://normale.it/bando", minimo=8) == 8  # `pausa` della fonte
