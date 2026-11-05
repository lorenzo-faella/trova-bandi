from pipeline.fonti.inps import estrai, sembra_beneficio

SCHEDA = """<html><body><h1>Bonus&nbsp;di prova</h1>
<h2>Fuori dal main</h2><p>menu</p>
<main>
  <h2>Condividi</h2><p>da ignorare</p>
  <h2 class="h3">Cos’è</h2><p>Un   bonus.</p>
  <h2>A chi è rivolto</h2>
  <p>Spetta a chi ha:</p><ul><li>figli;</li><li>ISEE &le; 10 &amp; altro.</li></ul>
  <script>var x = "non testo";</script>
  <p><a>Leggi di più</a></p>
  <div class="collapse"><p>Testo <b>nascosto</b> a scomparsa.</p></div>
  <button>Leggi meno</button>
  <h2>Domanda</h2><p>Online.</p>
  <h2>Ti potrebbero interessare</h2><p>altro</p>
</main>
<h2>Footer</h2><p>piede</p></body></html>"""


def test_estrai_tiene_solo_le_sezioni_note():
    s = estrai(SCHEDA)
    assert s["titolo"] == "Bonus di prova"
    assert set(s["sezioni"]) == {"cosa", "destinatari", "domanda"}
    assert s["sezioni"]["cosa"] == "Un bonus."
    assert s["sezioni"]["domanda"] == "Online."


def test_estrai_mantiene_liste_e_blocchi_a_scomparsa():
    d = estrai(SCHEDA)["sezioni"]["destinatari"]
    assert d.split("\n") == ["Spetta a chi ha:", "figli;", "ISEE ≤ 10 & altro.", "Testo nascosto a scomparsa."]


def test_scheda_senza_sezioni_non_rompe():
    assert estrai("<html><main><p>vuota</p></main></html>")["sezioni"] == {}


def test_sembra_beneficio():
    assert sembra_beneficio("Bonus nuovi nati")
    assert sembra_beneficio("NASpI: indennità mensile di disoccupazione")
    assert not sembra_beneficio("Assegno unico - simulazione")
    assert not sembra_beneficio("Accredito dei contributi figurativi per il servizio civile")
    assert not sembra_beneficio("Portale unico ISEE")
    assert sembra_beneficio("Borse di studio per la frequenza di Istituti Tecnici Superiori (ITS)")
    assert not sembra_beneficio("Avviso di addebito: informativa, sospensione, annullamento e rateazione")
    assert not sembra_beneficio("Il Casellario delle pensioni")
