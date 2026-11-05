"""Prova di download automatico dalle fonti dei bandi (ramo persone fisiche, più un controllo).

Domanda: un programma, senza nessuno che clicca, riesce a scaricare pagine e PDF da INPS,
Agenzia delle Entrate, siti regionali e comunali, e ne ottiene testo leggibile?

Per ogni indirizzo:
  1. legge robots.txt del sito e controlla che i programmi siano ammessi su quella pagina;
  2. scarica la pagina (una richiesta, con pausa di qualche secondo tra un sito e l'altro);
  3. controlla che il contenuto sia leggibile da un programma (testo HTML vero, o PDF con testo).

Scrive il risultato a schermo e in docs/prova-download.md.
Uso (dalla cartella del progetto): python prove/prova_download.py
Solo libreria standard: non serve installare niente.
"""
import datetime as dt
import html
import re
import time
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

UA = "trova-bandi (progetto universitario Bocconi 20875)"
PAUSA = 3      # secondi tra una richiesta e l'altra, per non pesare sui siti
TIMEOUT = 30   # secondi massimi di attesa per una risposta
ROOT = Path(__file__).resolve().parent.parent

# (livello, descrizione, indirizzo). Il "controllo" è una fonte che sappiamo già funzionare (scarica.py).
FONTI = [
    ("controllo", "incentivi.gov.it (già usato da scarica.py)",
     "https://www.incentivi.gov.it/it"),
    ("nazionale", "INPS, home page",
     "https://www.inps.it/"),
    ("nazionale", "INPS, pagina open data",
     "https://www.inps.it/dati-ricerche-e-bilanci/open-data"),
    ("nazionale", "Agenzia delle Entrate, portale",
     "https://www.agenziaentrate.gov.it/portale/"),
    ("regionale", "Regione Siciliana, elenco bandi",
     "https://www.regione.sicilia.it/istituzioni/servizi-informativi/bandi"),
    ("regionale", "Regione Lombardia, PDF Dote Scuola 2026",
     "https://www.regione.lombardia.it/content/dam/rl/canali-tematici-servizi/03-istruzione-formazione-e-lavoro/"
     "02-dote-scuola/red-dote-scuola-2026/allegati/dgr-5707-2_02_2026-allegato-a.pdf"),
    ("comunale", "Comune di Genova, PDF fondo affitti 2026",
     "https://www.comune.genova.it/sites/default/files/2026-02/REQUISITI%20E%20CRITERI%20BANDO%20FSA%202026.pdf"),
    ("comunale", "Comune di Cassano d'Adda (piattaforma municipiumapp), PDF Dote Scuola",
     "https://cassano-d-adda-api.municipiumapp.it/s3/1553/allegati/notizie/dote-scuola-2026-2027.pdf"),
]

PAROLE_BANDI = re.compile(r"bando|bandi|avviso|contribut|bonus|agevolazion", re.I)
SEGNI_DI_BLOCCO = re.compile(r"captcha|access denied|accesso negato|request rejected|are you a robot|"
                             r"attention required|bot detection", re.I)


def richiesta(url):
    """Una GET con il nostro User-Agent. Restituisce (codice HTTP, tipo di contenuto, byte) oppure solleva."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def permesso_robots(url):
    """True/False se robots.txt ammette o vieta la pagina; None se robots.txt non è leggibile."""
    p = urlparse(url)
    try:
        _, _, dati = richiesta(f"{p.scheme}://{p.netloc}/robots.txt")
    except urllib.error.HTTPError as e:
        # robots.txt assente (404) = nessun divieto; 401/403 = il sito blocca già qui
        return True if e.code == 404 else None
    except Exception:
        return None
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(dati.decode("utf-8", errors="replace").splitlines())
    return rp.can_fetch(UA, url)


def analizza(tipo, dati):
    """Il contenuto è leggibile da un programma? Restituisce (leggibile, spiegazione)."""
    if dati[:4] == b"%PDF" or "pdf" in tipo.lower():
        # Un PDF con testo contiene font; una scansione di solo immagini di solito no.
        if b"/Font" in dati:
            return True, f"PDF con testo ({len(dati) // 1024} KB)"
        return False, "PDF senza font: probabilmente una scansione, servirebbe l'OCR"
    testo_html = dati.decode("utf-8", errors="replace")
    if SEGNI_DI_BLOCCO.search(testo_html[:20000]) and len(testo_html) < 50000:
        return False, "pagina di blocco anti-robot"
    senza_script = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", testo_html)
    testo = html.unescape(re.sub(r"(?s)<[^>]+>", " ", senza_script))
    testo = re.sub(r"\s+", " ", testo).strip()
    link = len(re.findall(r"(?i)<a\s[^>]*href=", testo_html))
    parole = len(PAROLE_BANDI.findall(testo))
    if len(testo) < 500:
        return False, f"quasi nessun testo ({len(testo)} caratteri): probabilmente serve JavaScript"
    return True, f"{len(testo):,} caratteri di testo, {link} link, {parole} parole tipo 'bando/bonus/contributo'"


def prova(url):
    """Esito per un indirizzo: (verdetto, codice HTTP, spiegazione)."""
    robots = permesso_robots(url)
    if robots is False:
        return "VIETATO", "-", "robots.txt vieta questa pagina ai programmi: non scaricata"
    try:
        codice, tipo, dati = richiesta(url)
    except urllib.error.HTTPError as e:
        bloccato = e.code in (401, 403, 429, 503)
        return ("BLOCCATO" if bloccato else "ERRORE"), e.code, f"il sito ha risposto con errore HTTP {e.code}"
    except Exception as e:
        return "ERRORE", "-", f"nessuna risposta: {type(e).__name__}: {e}"
    leggibile, spiegazione = analizza(tipo, dati)
    nota = "" if robots else " (robots.txt non leggibile)"
    return ("OK" if leggibile else "NON LEGGIBILE"), codice, spiegazione + nota


def main():
    oggi = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    risultati = []
    for i, (livello, descrizione, url) in enumerate(FONTI):
        if i:
            time.sleep(PAUSA)
        verdetto, codice, spiegazione = prova(url)
        risultati.append((livello, descrizione, url, verdetto, codice, spiegazione))
        print(f"[{verdetto:13}] {livello:9} {descrizione}\n                {spiegazione}")

    # Per la mail conta che ogni livello abbia almeno una fonte scaricabile e leggibile.
    livelli = ["controllo", "nazionale", "regionale", "comunale"]
    riepilogo = {lv: any(r[0] == lv and r[3] == "OK" for r in risultati) for lv in livelli}
    righe = [
        "# Prova di download automatico",
        "",
        f"*Generato da `prove/prova_download.py` il {oggi}: non modificare a mano.*",
        "",
        "| esito | livello | fonte | HTTP | dettaglio |",
        "|---|---|---|---|---|",
    ]
    righe += [f"| {v} | {lv} | [{d}]({u}) | {c} | {s} |" for lv, d, u, v, c, s in risultati]
    righe += ["", "## Riepilogo per livello (almeno una fonte OK)", ""]
    righe += [f"- {lv}: {'sì' if ok else '**no**'}" for lv, ok in riepilogo.items()]
    if not riepilogo["controllo"]:
        esito = ("NON VALIDA: anche incentivi.gov.it fallisce, quindi il problema è la connessione di questo "
                 "computer, non i siti. Riprovare da un'altra rete.")
    elif all(riepilogo.values()):
        esito = "FATTIBILE: ogni livello ha almeno una fonte scaricabile e leggibile da un programma."
    else:
        mancanti = ", ".join(lv for lv, ok in riepilogo.items() if not ok)
        esito = f"DA APPROFONDIRE: nessuna fonte OK per {mancanti}. Guardare il dettaglio nella tabella."
    righe += ["", f"**Esito: {esito}**", ""]
    uscita = ROOT / "docs" / "prova-download.md"
    uscita.write_text("\n".join(righe), encoding="utf-8")
    print(f"\nESITO: {esito}\nReport scritto in {uscita}")


if __name__ == "__main__":
    main()
