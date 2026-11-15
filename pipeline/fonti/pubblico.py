"""A chi si rivolge un bando raccolto: persone, imprese o enti.

Le fonti "miste" (regioni, finanziarie regionali, agenzie per il lavoro) pubblicano insieme bandi per persone, imprese
ed enti, e la raccolta non lo distingue: circa 1.400 documenti su 2.300 hanno `pubblico: null`. Serve saperlo prima di
estrarre i requisiti, perché il vocabolario dell'estrattore è quello delle persone (decisioni 56 e 61).

Il metodo, in quest'ordine (decisione 61):
1. il titolo, se dice da solo "bando per le persone" (borse di studio, alloggi, affitto, nidi...);
2. il titolo, se dice "non è un bando per qualcuno" (gare, incarichi, albi, graduatorie); il filtro di
   `pipeline/copertura.py` (decisione 54) non si usa: è tarato sulle imprese e scarta "bando di concorso" e "iscrizione",
   che per le persone sono borse di studio e nidi;
3. la sezione del testo sui destinatari ("Beneficiari", "Destinatari", "A chi è rivolto", "Chi può partecipare"):
   si leggono i primi caratteri dopo l'intestazione e vince il gruppo nominato per primo (gli altri finiscono in `anche`);
4. senza sezione, le stesse parole nel titolo;
5. altrimenti `dubbio`.
Niente LLM: una regola sbagliata si vede e si corregge, come per il filtro della decisione 54.

Il risultato va in data/pubblico/classificazione.yaml (in git: i testi no, ma questo è piccolo). Non si tocca niente in
data/raw/documenti. Un campione da controllare a mano va in data/pubblico/revisione.yaml.

Uso:
    python -m pipeline.fonti.pubblico              # classifica e scrive il file
    python -m pipeline.fonti.pubblico misura       # confronto con le fonti che hanno già `pubblico` (persone, imprese, enti)
    python -m pipeline.fonti.pubblico campione 40  # campione da rivedere a mano tra i documenti senza `pubblico`
"""
import collections
import json
import random
import re
import sys
from pathlib import Path

import yaml

from pipeline.copertura import normalizza
from pipeline.fonti import documenti as dc

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "data" / "pubblico"
FILE = DIR / "classificazione.yaml"
REVISIONE = DIR / "revisione.yaml"

# Quanti caratteri leggere dopo l'intestazione: abbastanza per l'elenco dei destinatari, non tanto da arrivare ai
# requisiti di altri articoli (che nominano spesso "imprese" o "comuni" per altri motivi).
FINESTRA = 600

# Intestazioni della sezione sui destinatari, sul testo normalizzato (minuscole, senza accenti né punteggiatura).
INTESTAZIONE = re.compile(
    r"soggetti beneficiari|beneficiari|destinatari|a chi e rivolt|chi puo (partecipare|presentare|richiedere|fare domanda)"
    r"|soggetti ammess|soggetti richiedenti|possono presentare (la )?domand|possono partecipare|requisiti di ammissibilita"
)

# Parole che dicono il gruppo, nella sezione sui destinatari o nel titolo. Volutamente strette: "lavoratori",
# "universita" o "scuole" compaiono in bandi per tutti e tre i gruppi (un'impresa che assume lavoratori svantaggiati,
# l'universita' come sede degli studi), quindi non decidono da sole.
GRUPPI = {
    "persone": r"persone fisiche|cittadin[ie]|famigli[ae]|nucle[oi] familiar|student[ie]|giovani|genitori|residenti"
               r"|disoccupat|inoccupat|anzian|persone con disabilita|minori\b|minorenni|donne|\bneet\b|laureat|diplomat"
               r"|inquilin|conduttori|single|coppie|vedov|orfan|caregiver|volontari\b",
    "imprese": r"\bimpres[ae]\b|\bpmi\b|micro piccole|aziend[ae](?! sanitari| ospedalier| per la casa| di servizi alla persona)"
               r"|liberi professionisti|lavoratori autonomi|professionist[ie]|start ?up|cooperativ[ae]|consorzi"
               r"|operatori economici|datori di lavoro|partita iva|esercizi commerciali|imprenditor|agricoltori"
               r"|commercianti|artigian",
    "enti": r"\bcomuni\b|unioni (dei|di) comuni|enti locali|enti pubblici|amministrazioni pubbliche|pubbliche amministrazioni"
            r"|associazion[ie]|terzo settore|\bets\b|organizzazioni di volontariato|universita (pubblich|statal|non statal)"
            r"|atenei|istituti (tecnici|scolastic|afam|di istruzione)|istituzioni scolastiche|fondazion[ie]"
            r"|organismi (di )?formazion|organismi formativi|enti di formazione|agenzie formative|enti accreditati"
            r"|aziende sanitarie|\basl\b|\basp\b|parrocchi|enti ecclesiastici|soggetti pubblici|ambiti territoriali",
}
RX = {g: re.compile(rx) for g, rx in GRUPPI.items()}

# Titoli che da soli dicono "bando per le persone": diritto allo studio, casa, famiglia, cura. Valgono prima della
# sezione sui destinatari, perche' le pagine delle agenzie per lo studio e delle aziende per la casa spesso non ne hanno.
PERSONE_TITOLO = re.compile(
    r"\bbors[ae]\b|posti? (letto|alloggio)|alloggi|servizio abitativo|edilizia residenziale pubblica|\berp\b|\be r p\b"
    r"|case popolari|affitt|canone (agevolato|concordato|di locazione)|locazione ad uso abitativo|morosita"
    r"|premi[o]? (di|per) (laurea|tesi)|tesi di laurea|diritto allo studio|mobilita internazionale|studio all estero"
    r"|student|famigli|\bnidi\b|asili? nido|libri di testo|buoni? scuola|dote (scuola|sport|famiglia)|centri estivi"
    r"|voucher (servizi di cura|conciliazione)|assegn[oi] (di cura|formativ)|caregiver|badant|assistenti familiari"
    r"|procreazione medicalmente assistita|servizio civile|prima casa|leva civica|sussidi|tassa regionale|spese energetiche|bonus (bebe|nuovi nati|figli)|nuovi nati|neonat"
)

# Titoli di atti che non sono bandi per qualcuno: gare, incarichi, albi, adempimenti. Volutamente stretti: "concorso"
# da solo no (le borse di studio sono "bandi di concorso"), "iscrizione" nemmeno (iscrizione ai nidi).
NON_BANDO = re.compile(
    r"^ad \d+|\bgara\b|\bgare\b|affidament|fornitur|operatori economici|consip|indagine di mercato|procedura negoziata"
    r"|assunzion|selezione (di|del) personale|concorso pubblico per (titoli|esami|\d+ post)|conferimento (di )?incaric"
    r"|\balbo\b|\belenco\b|catasto|anagrafe|rendicontazion|monitoraggio|istruttoria|variazion|graduatori|esiti?\b"
    r"|rettifica|errata corrige|\basta\b|alienazion|sponsorizzazion|\bsponsor\b|avviso ai creditori|convenzione consip"
)


def testo(doc):
    """Pagina e allegato insieme: `pagine` li contiene già tutti e due (`pagine_allegato` è solo quante sono)."""
    return " ".join(doc.get("pagine") or [])


def gruppi_in(t):
    """I gruppi nominati in t, dal primo che compare all'ultimo."""
    primi = {g: m.start() for g, rx in RX.items() if (m := rx.search(t))}
    return sorted(primi, key=primi.get)


# Intestazioni fisse dei modelli di pagina, che nominano tutti i gruppi su ogni bando (Regione Veneto: "Destinatari:
# cittadino ente impresa"). Si tolgono prima di cercare la sezione.
RUMORE = re.compile(r"cittadino ente impresa")


def sezione_destinatari(t):
    """I FINESTRA caratteri dopo la prima intestazione sui destinatari che nomina almeno un gruppo, oppure None."""
    t = RUMORE.sub(" ", t)
    for m in INTESTAZIONE.finditer(t):
        pezzo = t[m.end():m.end() + FINESTRA]
        if gruppi_in(pezzo):
            return pezzo
    return None


def classifica(doc):
    """{'pubblico': persone|imprese|enti|non_bando|dubbio, 'anche': [...], 'metodo': ..., 'motivo': ...}."""
    titolo = normalizza(doc.get("titolo") or "")
    # La scorciatoia vale solo se il titolo non nomina anche imprese o enti: "Contributi per gli enti del Terzo settore -
    # Centri estivi" è un bando per gli enti, anche se parla di centri estivi.
    if (m := PERSONE_TITOLO.search(titolo)) and not set(gruppi_in(titolo)) & {"imprese", "enti"}:
        return {"pubblico": "persone", "anche": [], "metodo": "titolo (persone)", "motivo": m.group(0)}
    if (m := NON_BANDO.search(titolo)):
        return {"pubblico": "non_bando", "anche": [], "metodo": "titolo (non bando)", "motivo": m.group(0)}
    sez = sezione_destinatari(normalizza(testo(doc)))
    if sez:
        g = gruppi_in(sez)
        return {"pubblico": g[0], "anche": g[1:], "metodo": "sezione destinatari", "motivo": sez[:160]}
    g = gruppi_in(titolo)
    if g:
        return {"pubblico": g[0], "anche": g[1:], "metodo": "titolo", "motivo": doc.get("titolo")}
    return {"pubblico": "dubbio", "anche": [], "metodo": "nessuno", "motivo": "né sezione sui destinatari né parole nel titolo"}


def carica():
    out = []
    for f in sorted(dc.USCITA.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except ValueError:
            print(f"?   {f.name}: non leggibile, salto")
    return out


def scrivi(docs):
    righe = {}
    for d in docs:
        c = classifica(d)
        righe[d["id"]] = {"fonte": d.get("fonte_elenco"), "pubblico_fonte": d.get("pubblico"), "titolo": d.get("titolo"),
                          "pubblico": c["pubblico"], "anche": c["anche"], "metodo": c["metodo"]}
    DIR.mkdir(parents=True, exist_ok=True)
    intest = ("# Generato da pipeline/fonti/pubblico.py (decisione 61): non modificare a mano.\n"
              "# pubblico_fonte: quello della fonte (null per le fonti miste); pubblico: quello stimato dal documento.\n")
    FILE.write_text(intest + yaml.safe_dump(righe, allow_unicode=True, sort_keys=True, width=200), encoding="utf-8")
    senza = [r for r in righe.values() if r["pubblico_fonte"] is None]
    print(f"{FILE.relative_to(ROOT)}: {len(righe)} documenti")
    print("senza pubblico della fonte:", len(senza), dict(collections.Counter(r["pubblico"] for r in senza).most_common()))
    print("  di cui per metodo:", dict(collections.Counter(r["metodo"] for r in senza).most_common()))
    print("  persone anche come gruppo secondario:", sum("persone" in r["anche"] for r in senza))
    return righe


def misura(docs):
    """Confronto con il pubblico delle fonti che ce l'hanno. Conta soprattutto la domanda "va all'estrazione per le
    persone?" (persone come gruppo principale o in `anche`). Il riferimento è grezzo: una fonte "persone" pubblica anche
    avvisi per enti (decisione 57) e una fonte "imprese" anche gare e servizi, quindi una parte dei disaccordi sono
    errori della fonte, non della regola. La misura vera è il campione rivisto a mano."""
    colonne = ["persone", "imprese", "enti", "non_bando", "dubbio"]
    tab, verso_persone = collections.Counter(), collections.Counter()
    for d in docs:
        r = d.get("pubblico")
        if r in ("persone", "imprese", "enti"):
            c = classifica(d)
            tab[(r, c["pubblico"])] += 1
            verso_persone[r] += c["pubblico"] == "persone" or "persone" in c["anche"]
    print("fonte \\ stima  " + "  ".join(f"{c:>9}" for c in colonne) + "   va alle persone")
    for r in ("persone", "imprese", "enti"):
        n = sum(tab[(r, c)] for c in colonne)
        print(f"{r:<14} " + "  ".join(f"{tab[(r, c)]:>9}" for c in colonne) + f"   {verso_persone[r]}/{n} = {verso_persone[r] / n:.0%}")


def campione(docs, n, seme=61):
    """n documenti senza pubblico della fonte, metà tra quelli stimati "persone" (sono quelli che andranno
    all'estrazione) e metà tra gli altri, da controllare a mano: per ciascuno `giusto` va messo a vero o falso,
    e se falso `corretto` al pubblico giusto."""
    senza = [d for d in docs if d.get("pubblico") is None]
    persone = [d for d in senza if classifica(d)["pubblico"] == "persone"]
    altri = [d for d in senza if classifica(d)["pubblico"] != "persone"]
    rnd = random.Random(seme)
    scelti = rnd.sample(persone, min(n // 2, len(persone))) + rnd.sample(altri, n - min(n // 2, len(persone)))
    voci = []
    for d in scelti:
        c = classifica(d)
        voci.append({"id": d["id"], "titolo": d.get("titolo"), "url": d.get("url"), "stima": c["pubblico"],
                     "anche": c["anche"], "metodo": c["metodo"], "motivo": c["motivo"], "giusto": None, "corretto": None})
    DIR.mkdir(parents=True, exist_ok=True)
    intest = (f"# Campione da rivedere a mano (decisione 61): {len(voci)} documenti senza pubblico della fonte, seme {seme}.\n"
              "# Aprire il link, leggere a chi si rivolge il bando e mettere giusto: true/false; se false, corretto:\n"
              "# persone, imprese, enti o non_bando. Il campione è sbilanciato apposta: metà sono stime \"persone\".\n")
    REVISIONE.write_text(intest + yaml.safe_dump(voci, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    print(f"{REVISIONE.relative_to(ROOT)}: {len(voci)} voci")


if __name__ == "__main__":
    a = sys.argv[1:]
    docs = carica()
    if a and a[0] == "misura":
        misura(docs)
    elif a and a[0] == "campione":
        campione(docs, int(a[1]) if len(a) > 1 else 40)
    else:
        scrivi(docs)
