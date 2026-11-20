"""Domande della demo e scelta della prossima, per i due rami (decisione 22), più gli esiti in forma leggibile.

- Imprese: il questionario greedy di pipeline/questionario.py, così com'è (decisione 10).
- Persone: quel questionario lavora su matrici di requisiti piatti e non regge gli alberi delle regole per le persone
  (decisione 17) né il nucleo familiare. Le domande e le loro condizioni (`solo_se`) stanno in data/domande_persone.yaml
  (decisione 50); quale fare per prima lo decide prossima_persone(). Va misurata come quella delle imprese
  (docs/da-fare.md, sezione 4).

Il profilo ha la stessa forma che usa il motore: campo -> valore, "nucleo" = lista dei componenti.
"non lo so" (NON_SO) è una risposta: il campo non si richiede, e l'esito resta "mancano dati".
"""
import datetime as dt
import json
from functools import lru_cache
from pathlib import Path

import yaml

from pipeline.motore import (CONFRONTI, DA_VERIFICARE, IDONEO, IDONEO_SALVO, MANCANO_DATI, NON_IDONEO, NON_SO, QUASI,
                             aperta, figli, valuta, valuta_tutte, verifica)
from pipeline.citazioni import nodi
from pipeline.fonti.elenchi import tutte_le_fonti
from pipeline.normalizza import REGIONI, carica_comuni_istat
from pipeline.profili import Generatore
from pipeline.questionario import DOMANDE, Questionario
from pipeline.regole import DIR_PERSONE, LOADER, ROOT, carica

FILE_DOMANDE = ROOT / "data" / "domande_persone.yaml"
DIR_ESTRATTE = [ROOT / "data" / "regole_estratte" / "lotto-1", ROOT / "data" / "regole_estratte" / "lotto-2",
                ROOT / "data" / "regole_estratte" / "documenti"]
# Campione di imprese fittizie per stimare le risposte, come in pipeline/misura.py.
N_CAMPIONE = 1000
# Chi non ha avuto figli di recente: un numero di giorni e mesi che nessun termine raggiunge (i termini sono di mesi).
NESSUN_EVENTO = {"giorni_da_evento_figlio": 99999, "mesi_da_evento_figlio": 9999}
ORDINE_ESITI = [IDONEO, IDONEO_SALVO, QUASI, DA_VERIFICARE, MANCANO_DATI, NON_IDONEO]


def scelte(*coppie):
    return [{"valore": v, "etichetta": e} for v, e in coppie]


# Le domande delle persone stanno in data/domande_persone.yaml (decisione 50). Qui solo ciò che serve a mostrarle.
ETICHETTE = {
    "cittadinanza": {"italiana": "Italiana", "ue": "Di un altro Paese dell'Unione europea",
                     "familiare_con_diritto_soggiorno": "Familiare di un cittadino UE, con diritto di soggiorno",
                     "extra_ue_lungo_periodo": "Extra UE, con permesso di lungo periodo",
                     "protezione_internazionale": "Protezione internazionale (rifugiato o sussidiaria)",
                     "apolide": "Apolide", "altro_titolo": "Extra UE, con un altro permesso",
                     "nessun_titolo": "Nessun titolo di soggiorno"},
    "condizione_lavorativa": {"occupato": "Lavoro", "disoccupato": "Sono senza lavoro", "studente": "Studio",
                              "pensionato": "Sono in pensione", "inattivo": "Non lavoro e non cerco lavoro"},
    "causa_fine_lavoro": {"licenziamento": "Licenziamento", "fine_contratto": "Fine del contratto a termine",
                          "dimissioni": "Dimissioni", "dimissioni_giusta_causa": "Dimissioni per giusta causa",
                          "dimissioni_periodo_tutelato": "Dimissioni durante la maternità o paternità tutelata",
                          "risoluzione_consensuale": "Accordo con il datore di lavoro",
                          "risoluzione_consensuale_tutelata": "Accordo nella procedura di conciliazione"},
    "attivita": {"studio": "Studia", "tirocinio_o_lavoro": "Tirocinio o lavoro a basso reddito",
                 "disoccupato_cpi": "Disoccupato, iscritto al centro per l'impiego",
                 "servizio_civile": "Servizio civile", "nessuna": "Nessuna di queste"},
    "tipo_lavoro": {"dipendente": "Dipendente", "autonomo": "Autonomo", "parasubordinato": "Collaboratore (Gestione Separata)"},
    "titolo_di_studio": {"nessuno": "Nessuno", "licenza_media": "Licenza media", "diploma": "Diploma",
                         "laurea_triennale": "Laurea triennale", "laurea_magistrale": "Laurea magistrale",
                         "master": "Master", "dottorato": "Dottorato"},
    "iscrizione": {"universita": "Università", "afam": "AFAM (accademie e conservatori)", "its": "ITS",
                   "scuola_superiore": "Scuola superiore", "nessuna": "Nessuno"},
    "abitazione": {"affitto": "In affitto", "proprieta": "Di proprietà", "altro": "Altro"},
    "livello_corso": {"laurea_triennale": "Laurea triennale", "laurea_magistrale": "Laurea magistrale",
                      "ciclo_unico": "Laurea magistrale a ciclo unico", "dottorato": "Dottorato di ricerca",
                      "specializzazione": "Scuola di specializzazione", "master": "Master",
                      "its": "ITS Academy", "afam_primo_livello": "AFAM, diploma di primo livello",
                      "afam_secondo_livello": "AFAM, diploma di secondo livello"},
    "situazioni_particolari": {
        "dipendente_pubblico": "Sono dipendente o pensionato pubblico",
        "genitore_dipendente_pubblico": "Un mio genitore è (o era) dipendente o pensionato pubblico",
        "poste_ipost": "Io o un mio familiare lavoriamo (o lavoravamo) in Poste Italiane / ex IPOST",
        "gestione_magistrale": "Io o un mio familiare siamo iscritti alla Gestione Assistenza Magistrale",
        "superstite": "Sono vedovo/a od orfano/a di un lavoratore o pensionato",
        "forze_ordine": "Lavoro (o ho lavorato) in forze armate, polizia o vigili del fuoco",
        "lavoro_domestico": "Sono lavoratore domestico (colf, badante)",
        "lavoro_agricolo": "Sono coltivatore diretto o lavoratore agricolo",
        "malattia_tbc": "Ho una malattia tubercolare riconosciuta",
        "nessuna": "Nessuna di queste"},
}
TIPI_PERSONE = {"sì/no": "si_no", "numero": "numero", "elenco": "scelta", "elenco multiplo": "multipla", "elenco di persone": "nucleo"}
UNITA = {"anni_residenza_regione": "anni", "anni_residenza_italia": "anni", "anni_residenza_continuativa_italia": "anni",
         "giorni_da_cessazione_lavoro": "giorni", "settimane_contributi_4_anni": "settimane", "isee": "euro",
         "patrimonio_immobiliare": "euro", "reddito_annuo": "euro", "reddito_richiedente": "euro", "canone_annuo": "euro",
         "isee_universitario": "euro", "ispe": "euro", "mesi_validita_permesso": "mesi", "crediti_conseguiti": "CFU",
         "percentuale_invalidita": "%", "eta": "anni"}
AIUTI = {"settimane_contributi_4_anni": "Si leggono nell'estratto conto contributivo, sul sito INPS.",
         "isee": "È nell'attestazione ISEE. Se non l'hai, rispondi \"non lo so\".",
         "nucleo": "Il nucleo è quello dell'ISEE: di solito chi vive con te. Te compreso: indica l'età di ognuno."}
# La data del figlio è una domanda sola, da cui si ricavano giorni e mesi (vocabolario, scelta 4).
DERIVATI = {"giorni_da_evento_figlio": "data_evento_figlio", "mesi_da_evento_figlio": "data_evento_figlio"}
# Risposta a una domanda che non si fa perché non riguarda la persona (decisione 64): non è in nessun elenco di valori
# ammessi, quindi un requisito "tipo_lavoro in [dipendente]" risulta falso invece di restare senza dati.
NON_APPLICABILE = "non_applicabile"
# I numeri hanno un valore ovvio solo in pochi casi: chi non ha una disabilità ha invalidità 0, chi non ha perso il
# lavoro non ha una cessazione recente (come NESSUN_EVENTO). Gli altri (reddito, contributi, ISPE) restano senza dati.
NUMERI_NON_APPLICABILI = {"percentuale_invalidita": 0, "giorni_da_cessazione_lavoro": 99999}
# Campi calcolati: per conoscerli serve la domanda indicata. L'età di chi fa domanda è quella del primo componente
# del nucleo ("Tu"): non si chiede due volte.
RICAVATI = {"numero_figli": "nucleo.figlio", "eta": "nucleo.eta", "regione_ateneo": "comune_ateneo", "provincia_ateneo": "comune_ateneo"}


@lru_cache(maxsize=None)
def domande():
    """chiave -> domanda, nell'ordine del file. "nucleo.x" = una risposta per ogni componente."""
    out = {}
    for d in yaml.safe_load(FILE_DOMANDE.read_text(encoding="utf-8"))["domande"]:
        if d["campo"] == "mesi_da_evento_figlio" or d.get("ricavato"):
            continue
        campo = DERIVATI.get(d["campo"], d["campo"])
        out[("nucleo." if d.get("chi") == "componente" else "") + campo] = dict(d, campo=campo)
    return out


ETICHETTE_IMPRESE = {"tipologia": "Che tipo di soggetto sei?", "dimensione": "Quanto è grande l'impresa?",
                     "regione": "In quale regione ha sede (operativa) l'impresa?", "comune": "In quale comune?",
                     "settore": "In quali settori lavora?", "ateco_2025": "Qual è il codice ATECO 2025 dell'attività principale?",
                     "ambito": "La sede è in una di queste aree?"}
TIPI_IMPRESE = {"tipologia": "multipla", "dimensione": "scelta", "regione": "scelta", "comune": "comune",
                "settore": "multipla", "ateco_2025": "testo", "ambito": "multipla"}
AIUTO_IMPRESE = {"ateco_2025": "Per esempio 56.10 (ristorazione). È nella visura camerale; bastano le prime cifre.",
                 "ambito": "Se nessuna, conferma senza scegliere.",
                 "dimensione": "Micro: meno di 10 addetti; piccola: meno di 50; media: meno di 250."}


# --- Regole -----------------------------------------------------------------------------------------------------------

def leggi_cartella(cartella, origine):
    out = []
    for f in sorted(Path(cartella).glob("*.yaml")):
        r = yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER)
        r["_origine"] = origine
        out.append(r)
    return out


@lru_cache(maxsize=None)
def regole_persone(estratte=False):
    regole = leggi_cartella(DIR_PERSONE, "riferimento")
    if estratte:
        regole += [r for d in DIR_ESTRATTE for r in leggi_cartella(d, "estratta")]
    return regole


@lru_cache(maxsize=None)
def ramo_imprese(giorno):
    """Regole aperte quel giorno e questionario con il suo campione: si costruiscono una volta (meno di 2 secondi)."""
    regole = [dict(r, _origine="open data") for r in carica() if aperta(r, giorno)]
    if not regole:
        raise RuntimeError("nessuna regola delle imprese: eseguire prima `make dati`")
    return regole, Questionario(regole, Generatore(regole, seed=1).campione(N_CAMPIONE))


@lru_cache(maxsize=None)
def sedi_istat():
    """Nome del comune -> (provincia, regione), dall'elenco ISTAT: per ricavare la sede del corso (decisione 73)."""
    import csv
    import io
    istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))[-1]
    righe = csv.DictReader(io.StringIO(istat.read_bytes().decode("latin-1")), delimiter=";")
    prov = next(k for k in righe.fieldnames if k.startswith("Denominazione dell'Unità territoriale sovracomunale"))
    return {r["Denominazione in italiano"]: (r[prov], r["Denominazione Regione"]) for r in righe}


@lru_cache(maxsize=None)
def comuni_per_regione():
    istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))[-1]
    out = {}
    for nome, regione in set(carica_comuni_istat(istat).values()):
        out.setdefault(regione, set()).add(nome)
    return {r: sorted(v) for r, v in out.items()}


@lru_cache(maxsize=None)
def opzioni_imprese(giorno):
    regole, _ = ramo_imprese(giorno)
    valori = {c: set() for c in ("tipologia", "dimensione", "settore", "ambito")}
    for r in regole:
        for q in r["requisiti"]:
            if q["campo"] in valori:
                valori[q["campo"]].update(q["valori"])
    valori = {c: sorted(v) for c, v in valori.items()}
    valori["dimensione"] = [d for d in ["Microimpresa", "Piccola Impresa", "Media Impresa", "Grande Impresa",
                                        "Non classificabile/classificato"] if d in valori["dimensione"]]
    valori["regione"] = REGIONI
    return valori


# --- Profilo ----------------------------------------------------------------------------------------------------------

def mesi_interi(da, a):
    """Mesi interi già compiuti tra due date: dal 10/01 al 9/03 è 1, dal 10/01 al 10/03 è 2."""
    mesi = (a.year - da.year) * 12 + a.month - da.month
    return mesi - (a.day < da.day)


def completa(profilo, giorno):
    """Profilo per il motore: ciò che si ricava dalle risposte, senza chiedere e senza tirare a indovinare.

    Dalla data del figlio i giorni e i mesi; dai componenti il numero dei figli; dal primo componente l'età di chi fa
    domanda. Chi fa domanda non è figlio di sé stesso;
    chi non è figlio non è un figlio a carico; le domande che non riguardano la persona hanno una risposta ovvia
    (`non_applicabili`).
    """
    p = dict(profilo)
    nucleo = p.get("nucleo")
    if isinstance(nucleo, list):
        p["nucleo"] = nucleo = [dict(c) for c in nucleo]
        if nucleo:
            nucleo[0].setdefault("figlio", False)
            if nucleo[0].get("eta") is not None:
                p.setdefault("eta", nucleo[0]["eta"])
        for c in nucleo:
            if c.get("figlio") is False:
                c.setdefault("figlio_a_carico", False)
        risposte = [c.get("figlio") for c in nucleo]
        if None not in risposte:
            n = sum(r is True for r in risposte)
            p["numero_figli"] = NON_SO if n == 0 and NON_SO in risposte else n
    elif nucleo == NON_SO:
        p["numero_figli"] = NON_SO
        p.setdefault("eta", NON_SO)
    sede = p.get("comune_ateneo")
    if sede == NON_SO:
        p.setdefault("provincia_ateneo", NON_SO); p.setdefault("regione_ateneo", NON_SO)
    elif sede and sede in sedi_istat():
        p.setdefault("provincia_ateneo", sedi_istat()[sede][0]); p.setdefault("regione_ateneo", sedi_istat()[sede][1])
    if p.get("domicilio_diverso") is False:
        p.setdefault("regione_domicilio", p.get("regione"))
        p.setdefault("comune_domicilio", p.get("comune"))
        p = {k: v for k, v in p.items() if v is not None}
    non_applicabili(p)
    data = p.pop("data_evento_figlio", None)
    if data == "nessuno" or (data is None and p.get("numero_figli") == 0):
        p.update(NESSUN_EVENTO)
    elif data == NON_SO:
        p.update({k: NON_SO for k in NESSUN_EVENTO})
    elif data:
        d, oggi = dt.date.fromisoformat(data), dt.date.fromisoformat(giorno)
        p.update({"giorni_da_evento_figlio": (oggi - d).days, "mesi_da_evento_figlio": mesi_interi(d, oggi)})
    return p


DOMICILIO = ("regione_domicilio", "comune_domicilio")  # chi vive dove risiede: si ricavano dalla residenza, non sono "non applicabili"


def non_applicabili(p):
    """Le domande chiuse da una risposta vera (non da "non lo so"): la demo non le farà mai, e lasciarle vuote terrebbe
    su "mancano dati" un requisito che per questa persona è già deciso. Un disoccupato non ha un tipo di lavoro, chi non
    affitta non ha un contratto registrato, chi è italiano non ha un permesso per casi speciali (decisione 64)."""
    for chiave, d in domande().items():
        if chiave.startswith("nucleo.") or chiave in p or chiave in DERIVATI.values() or chiave in DOMICILIO:
            continue
        if not any(p.get(c) not in (None, NON_SO) and condizione(r, p.get(c)) is False
                   for c, r in (d.get("solo_se") or {}).items()):
            continue
        if d["tipo"] == "sì/no":
            p[chiave] = False
        elif d["tipo"] in ("elenco", "elenco multiplo"):
            p[chiave] = NON_APPLICABILE
        elif chiave in NUMERI_NON_APPLICABILI:
            p[chiave] = NUMERI_NON_APPLICABILI[chiave]


# --- Prossima domanda: persone --------------------------------------------------------------------------------------

def da_chiedere(req, profilo, prefisso=""):
    """Domande ancora senza risposta da cui dipende un requisito che oggi vale "non si sa".
    Un requisito già deciso (sì o no) non chiede niente, e nemmeno un non modellabile: nessuna domanda lo risolve."""
    if "non_modellabile" in req or verifica(req, profilo) is not None:
        return set()
    if "almeno_un_componente" in req:
        nucleo = profilo.get("nucleo")
        if nucleo is None:
            return {"nucleo"}
        if nucleo == NON_SO:
            return set()
        return {c for comp in nucleo for q in req["almeno_un_componente"] for c in da_chiedere(q, comp, "nucleo.")}
    if "campo" in req:
        if profilo.get(req["campo"]) is not None:
            return set()  # anche "non lo so": è una risposta
        return {prefisso + DERIVATI.get(req["campo"], req["campo"])}
    return {c for q in figli(req) for c in da_chiedere(q, profilo, prefisso)}


def condizione(richiesta, valore):
    """Una condizione di `solo_se` su una risposta: True, False, o None se la risposta non c'è ancora.
    "non lo so" non apre niente: una domanda di dettaglio su qualcosa che la persona non sa non servirebbe."""
    if valore is None:
        return None
    if valore == NON_SO:
        return False
    if isinstance(richiesta, list):
        # una risposta multipla (studio e lavoro) apre la domanda se una delle scelte la apre
        return any(v in richiesta for v in valore) if isinstance(valore, list) else valore in richiesta
    if isinstance(richiesta, bool):
        return valore is richiesta
    return all(CONFRONTI[op](valore, soglia) for op, soglia in richiesta.items())


def cancello(d, dati):
    """(aperta?, campo da conoscere prima). Su `dati`: il profilo, o il singolo componente per le domande sul nucleo."""
    for campo, richiesta in (d.get("solo_se") or {}).items():
        esito = condizione(richiesta, dati.get(campo))
        if esito is False:
            return False, None
        if esito is None:
            return None, campo
    return True, None


def da_porre(chiave, profilo):
    """La domanda da fare davvero per conoscere `chiave`: lei stessa, quella da cui dipende, o None se resta chiusa."""
    if chiave in RICAVATI:
        return da_porre(RICAVATI[chiave], profilo)
    d = domande().get(chiave)
    prima = {"comune": "regione", "comune_domicilio": "regione_domicilio"}.get(chiave)
    if prima and profilo.get(prima) is None and da_porre(prima, profilo) is not None:
        return da_porre(prima, profilo)
    if d is None and chiave.startswith("nucleo."):
        return None  # un campo del richiedente messo per errore dentro un componente: nessuna domanda lo risolve
    if d is None:  # un campo senza domanda nel file: la si fa comunque, con il nome leggibile
        return chiave
    if chiave.startswith("nucleo."):
        nucleo = profilo.get("nucleo")
        if not isinstance(nucleo, list):
            return "nucleo" if nucleo is None else None
        for c in nucleo:
            if c.get(d["campo"]) is not None:
                continue
            aperta_, prima = cancello(d, c)
            if aperta_:
                return chiave
            if prima:
                return da_porre("nucleo." + prima, profilo)
        return None
    aperta_, prima = cancello(d, profilo)
    if prima:
        return da_porre(prima, profilo)
    return chiave if aperta_ else None


def prossima_persone(esiti, profilo):
    """La domanda che avvicina di più gli esiti ancora aperti ("mancano dati").

    Ogni beneficio aperto dà a ognuna delle sue domande mancanti 1/k punti, dove k è quante gliene mancano: un beneficio
    a cui manca una sola risposta pesa di più, perché quella risposta lo decide. È la stessa idea del questionario
    delle imprese (decisione 10), senza il campione di profili fittizi: per le persone non c'è ancora una popolazione
    realistica (docs/da-fare.md). Una domanda chiusa dal suo `solo_se` non si fa; se dipende da una risposta che manca,
    si fa prima quella. Restituisce (campo, quanti benefici la usano) o (None, 0).
    """
    # Il domicilio si chiede sempre, appena nota la residenza: anche se nessuna regola lo usa, decide quali bandi locali
    # sono "vicini" (decisione 71). Prima il sì/no, poi regione e comune se la persona vive altrove.
    if profilo.get("regione") is not None:
        for chiave in ("domicilio_diverso", "regione_domicilio", "comune_domicilio"):
            if profilo.get(chiave) is None and da_porre(chiave, profilo) == chiave:
                return chiave, 0
    punti, usi = {}, {}
    for e in esiti:
        if e.stato != MANCANO_DATI:
            continue
        mancanti = {c for q in e.regola["requisiti"] for c in da_chiedere(q, profilo)}
        reali = {r for r in (da_porre(c, profilo) for c in mancanti) if r}
        for c in reali:
            punti[c] = punti.get(c, 0) + 1 / len(reali)
            usi[c] = usi.get(c, 0) + 1
    if not punti:
        return None, 0
    ordine = list(domande())
    noti = [c for c in ordine if c in punti] + sorted(c for c in punti if c not in ordine)
    campo = max(noti, key=lambda c: (round(punti[c], 9), -noti.index(c)))
    return campo, usi[campo]


def opzioni_persona(d):
    if d["campo"] in ("regione", "regione_ateneo", "regione_domicilio"):
        return scelte(*((r, r) for r in REGIONI))
    etichette = ETICHETTE.get(d["campo"], {})
    return scelte(*((v, etichette.get(v, str(v).replace("_", " ").capitalize())) for v in d.get("valori") or []))


def domanda_persone(chiave, usi, profilo):
    d = domande().get(chiave) or {"campo": chiave.split(".")[-1], "domanda": nome_campo(chiave).capitalize() + "?", "tipo": "numero"}
    campo = d["campo"]
    q = {"campo": chiave, "testo": d["domanda"], "tipo": TIPI_PERSONE.get(d["tipo"], "testo"), "bandi_interessati": usi}
    if campo in UNITA:
        q["unita"] = UNITA[campo]
    if campo in AIUTI:
        q["aiuto"] = AIUTI[campo]
    if q["tipo"] == "multipla":  # per le persone serve almeno una risposta: chi studia e lavora le sceglie tutte e due
        q.update(opzioni=opzioni_persona(d), almeno_una=True)
    if q["tipo"] == "scelta":
        q["opzioni"] = opzioni_persona(d)
        if campo in ("comune", "comune_domicilio", "comune_ateneo"):
            regione = {"comune": "regione", "comune_domicilio": "regione_domicilio"}.get(campo)
            q.update(tipo="comune", regione=profilo.get(regione) if regione else None)
    if campo == "data_evento_figlio":
        q.update(testo="Quando è nato (o entrato in famiglia) l'ultimo figlio?", tipo="data",
                 opzioni=scelte(("nessuno", "Nessun figlio nato o adottato negli ultimi due anni")))
    if chiave.startswith("nucleo."):
        q["per_componente"] = True
        q["componenti"] = [{"indice": i, "eta": c.get("eta")} for i, c in enumerate(profilo.get("nucleo") or [])
                           if c.get(campo) is None and cancello(d, c)[0]]
    return q


# --- Prossima domanda: imprese --------------------------------------------------------------------------------------

def domanda_imprese(profilo, giorno):
    regole, Q = ramo_imprese(giorno)
    risposte = {c: profilo[c] for c in DOMANDE if c in profilo}
    campo = Q.prossima(risposte, Q.matrici([risposte]))
    if campo is None:
        return None
    det, aperti, _, _ = Q.stato(Q.matrici([risposte]), risposte)
    d = {"campo": campo, "testo": ETICHETTE_IMPRESE[campo], "tipo": TIPI_IMPRESE[campo],
         "bandi_interessati": int((aperti & Q.ha_req[campo]).sum())}
    if campo in AIUTO_IMPRESE:
        d["aiuto"] = AIUTO_IMPRESE[campo]
    opzioni = opzioni_imprese(giorno)
    if campo in opzioni:
        d["opzioni"] = scelte(*((v, v) for v in opzioni[campo]))
    if campo == "comune":
        d["regione"] = profilo.get("regione")
    return d


# --- Esiti leggibili --------------------------------------------------------------------------------------------------

OPERATORI = {"<=": "al massimo", "<": "meno di", ">=": "almeno", ">": "più di"}


NOMI = {"eta": "età", "isee": "ISEE", "ateco_2025": "codice ATECO 2025", "ateco_2007": "codice ATECO 2007",
        "anni_residenza_italia": "anni di residenza in Italia",
        "anni_residenza_continuativa_italia": "anni di residenza continuativa in Italia",
        "settimane_contributi_4_anni": "settimane di contributi negli ultimi 4 anni",
        "giorni_da_evento_figlio": "giorni dalla nascita o dall'ingresso del figlio",
        "mesi_da_evento_figlio": "mesi dalla nascita o dall'ingresso del figlio",
        "giorni_da_cessazione_lavoro": "giorni dalla fine del lavoro", "residente_italia": "residenza in Italia",
        "lavora_in_italia": "lavoro in Italia", "soggetto_irpef_italia": "imposte sul reddito pagate in Italia",
        "permesso_casi_speciali": "permesso per casi speciali", "ultimo_lavoro_subordinato": "ultimo lavoro da dipendente",
        "veicoli_esclusi": "auto, moto, barche o aerei recenti", "disabile": "disabilità",
        "svantaggio_certificato": "seguito dai servizi socio-sanitari", "figlio_a_carico": "figlio a carico",
        "reddito_annuo": "reddito annuo", "attivita": "attività", "causa_fine_lavoro": "fine del lavoro",
        "condizione_lavorativa": "situazione lavorativa", "patrimonio_immobiliare": "valore degli immobili",
        "anni_residenza_regione": "anni di residenza nella regione", "reddito_richiedente": "reddito personale IRPEF",
        "canone_annuo": "affitto annuo", "numero_figli": "numero di figli", "anno_di_corso": "anno di corso",
        "crediti_conseguiti": "crediti conseguiti", "isee_universitario": "ISEE per il diritto allo studio", "ispe": "ISPE",
        "percentuale_invalidita": "percentuale di invalidità", "mesi_validita_permesso": "mesi di validità del permesso",
        "tipo_lavoro": "tipo di lavoro", "abitazione": "abitazione", "iscrizione": "iscrizione a un corso",
        "titolo_di_studio": "titolo di studio", "figlio": "figlio", "cittadinanza": "cittadinanza",
        "contratto_locazione_registrato": "contratto di affitto registrato", "mutuo_prima_casa": "mutuo per la prima casa",
        "proprieta_altra_abitazione": "proprietà di un'altra casa", "situazioni_particolari": "situazioni particolari",
        "regione_ateneo": "regione dell'università", "provincia_ateneo": "provincia dell'università",
        "comune_ateneo": "comune della sede del corso", "livello_corso": "corso frequentato", "tempo_parziale": "iscrizione a tempo parziale", "domicilio_diverso": "domicilio in un altro comune",
        "regione_domicilio": "regione del domicilio", "comune_domicilio": "comune del domicilio",
        "data_evento_figlio": "nascita o adozione dell'ultimo figlio", "regione": "regione di residenza",
        "comune": "comune di residenza", "fuori_corso_o_ripetente": "fuori corso o ripetente"}
# I codici delle risposte con le stesse parole delle domande: "disoccupato_cpi" -> "disoccupato, iscritto al centro…".
VALORI = {campo: {v: e.lower() for v, e in etichette.items()} for campo, etichette in ETICHETTE.items()}


def nome_campo(campo):
    campo = campo.split(".")[-1]
    return NOMI.get(campo, campo.replace("_", " "))


def elenco(valori, massimo=6, campo=None):
    etichette = VALORI.get(campo, {})  # campi delle imprese (settore, tipologia): nessuna etichetta, restano come sono
    valori = [etichette.get(v, str(v).replace("_", " ")) for v in valori]
    if len(valori) <= massimo:
        return ", ".join(valori)
    return f"uno dei {len(valori)} elencati (per esempio {', '.join(valori[:3])})"


def descrivi(req):
    """Il requisito in una frase, per chi usa la demo. La prova resta la citazione."""
    if "non_modellabile" in req:
        return req["non_modellabile"]
    if "almeno_uno_di" in req:
        return "almeno una di queste: " + "; ".join(descrivi(q) for q in req["almeno_uno_di"])
    if "tutti_di" in req:
        return "tutte queste: " + "; ".join(descrivi(q) for q in req["tutti_di"])
    if "almeno_un_componente" in req:
        return "qualcuno nel nucleo con: " + "; ".join(descrivi(q) for q in req["almeno_un_componente"])
    campo, op = nome_campo(req["campo"]), req["operatore"]
    if op in ("vero", "falso"):
        return f"{campo}: {'sì' if op == 'vero' else 'no'}"
    if op == "tra":
        return f"{campo} tra {req['valore'][0]} e {req['valore'][1]}"
    if op in OPERATORI:
        return f"{campo} {OPERATORI[op]} {req['valore']:,}".replace(",", ".")
    if op == "prefisso":
        return f"{campo} che inizia con {elenco(req['valori'])}"
    return f"{campo}: {elenco(req['valori'], campo=req['campo'])}"


def voce(req):
    return {"testo": descrivi(req), "citazione": req.get("citazione"), "fonte": req.get("fonte")}


@lru_cache(maxsize=None)
def territori():
    """id della fonte o del documento -> (regione, livello): per dire dove vale un bando locale."""
    from pipeline.fonti.api_regioni import FONTI as FONTI_API  # bandi raccolti dalle API regionali: non in elenchi.yaml
    out = {f["id"]: (f.get("regione"), f.get("livello")) for f in FONTI_API.values()}
    out.update({f["id"]: (f.get("regione"), f.get("livello")) for f in tutte_le_fonti()})
    documenti = yaml.safe_load((ROOT / "data" / "fonti" / "documenti.yaml").read_text(encoding="utf-8"))["documenti"]
    out.update({d["id"]: (d.get("regione"), d.get("livello")) for d in documenti})
    return out


def regione_ufficiale(nome):
    """Il nome di una regione come nell'elenco ISTAT (REGIONI): alcune fonti scrivono "Valle d'Aosta" o
    "Trentino-Alto Adige" senza la parte bilingue, e il confronto con la regione della persona fallirebbe."""
    if not nome or nome in REGIONI:
        return nome
    return next((r for r in REGIONI if r.split("/")[0] == nome.split("/")[0]), nome)


def territorio(regola):
    """Regione dell'ente che pubblica il bando, o None se è nazionale (INPS, incentivi.gov.it). Non cambia l'esito: molte
    regole estratte non scrivono il vincolo territoriale (un contributo comunale vale per i residenti, una borsa DSU per
    chi studia in quella regione), e la demo usa questa informazione solo per raggruppare (decisione 68)."""
    if regola["id"].startswith("inps-"):
        return None
    t = territori()
    chiave = max((k for k in t if regola["id"] == k or regola["id"].startswith(k + "-")), key=len, default=None)
    return regione_ufficiale(t[chiave][0]) if chiave and t[chiave][1] != "nazionale" else None


def risultato(e, profilo=None):
    r = e.regola
    if e.stato in (NON_IDONEO, QUASI):
        perche = e.falliti
    elif e.stato in (MANCANO_DATI, DA_VERIFICARE):
        perche = e.mancanti
    elif e.stato == IDONEO_SALVO:
        perche = e.eccezioni
    else:
        perche = r["requisiti"]
    return {"id": r["id"], "titolo": r["titolo"], "ente": r.get("ente"), "link": r.get("link"),
            "chiusura": r.get("chiusura"), "stato": e.stato, "origine": r.get("_origine"),
            "regione": territorio(r) if r.get("_origine") != "open data" else None,
            # requisiti già soddisfatti: un "da verificare" senza nessuno vuol dire "non sappiamo dirlo" (decisione 70)
            "a_favore": sum(verifica(q, profilo) is True for q in r["requisiti"]) if profilo is not None else None,
            "perche": [voce(q) for q in perche],
            # chi è idoneo, anche salvo eccezioni, vede tutti i requisiti con la loro citazione
            "requisiti": [voce(q) for q in r["requisiti"]] if e.stato in (IDONEO, IDONEO_SALVO) else []}


def maiuscola(s):
    return s[:1].upper() + s[1:]


def leggibile(campo, valore):
    """Una risposta come la vede chi l'ha data."""
    if valore == NON_SO:
        return "non lo so"
    if isinstance(valore, list):
        return ", ".join(leggibile(campo, v) for v in valore)
    if isinstance(valore, bool):
        return "sì" if valore else "no"
    if campo == "data_evento_figlio":
        return "nessun figlio negli ultimi due anni" if valore == "nessuno" else dt.date.fromisoformat(valore).strftime("%d/%m/%Y")
    if isinstance(valore, (int, float)):
        testo = f"{valore:,.0f}".replace(",", ".") if campo in UNITA and UNITA[campo] == "euro" else f"{valore:g}"
        return f"{testo} {UNITA[campo]}" if campo in UNITA else testo
    etichette = ETICHETTE.get(campo, {})
    return etichette.get(valore, str(valore).replace("_", " "))


def riepilogo(profilo):
    """Le risposte date, nell'ordine del questionario: compaiono nel report stampato (decisione 71)."""
    righe = []
    for chiave in domande():
        campo = chiave.split(".")[-1]
        if chiave == "nucleo" and isinstance(profilo.get("nucleo"), list):
            persone = profilo["nucleo"]
            righe.append({"voce": "Nucleo familiare", "valore": f"{len(persone)} {'persona' if len(persone) == 1 else 'persone'}"})
            for i, c in enumerate(persone):
                dettagli = [f"{nome_campo(k)}: {leggibile(k, v)}" for k, v in c.items() if k != "eta" and v is not None]
                eta = c.get("eta")
                righe.append({"voce": "Tu" if i == 0 else f"Persona {i + 1}",
                              "valore": "; ".join([f"{leggibile('eta', eta)}" if eta is not None else "età non indicata", *dettagli])})
        elif chiave == "nucleo" and profilo.get("nucleo") == NON_SO:
            righe.append({"voce": "Nucleo familiare", "valore": "non lo so"})
        elif not chiave.startswith("nucleo") and profilo.get(campo) is not None:
            righe.append({"voce": maiuscola(nome_campo(campo)), "valore": leggibile(campo, profilo[campo])})
    return righe


CAMPI_ISEE = {"isee", "isee_universitario", "ispe"}
LINK_ISEE = ("https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi."
             "Portale-unico-ISEE.html")
FILE_PROFILI = ROOT / "web" / "profili_demo.yaml"


def dipende_da_isee(regola):
    return any(n.get("campo") in CAMPI_ISEE for req in regola["requisiti"] for n in nodi(req))


@lru_cache(maxsize=None)
def profili_demo():
    """Persone tipo del caro vita (docs/contesto.md, idea 2): profili di esempio, non casi reali."""
    return yaml.safe_load(FILE_PROFILI.read_text(encoding="utf-8"))["profili"]


@lru_cache(maxsize=None)
def statistiche(giorno):
    """I numeri della pagina iniziale, calcolati dai dati e non scritti a mano."""
    persone = regole_persone(True)
    try:
        imprese = len(ramo_imprese(giorno)[0])
    except RuntimeError:  # senza `make dati` il ramo imprese non c'è
        imprese = None
    schede = sorted(f for f in (ROOT / "data" / "raw").glob("inps_schede_*.json") if not f.name.endswith(".meta.json"))
    classificati = ROOT / "data" / "pubblico" / "classificazione.yaml"
    return {
        "giorno": giorno,
        "persone": len(persone),
        "persone_aperte": sum(aperta(r, giorno) for r in persone),
        "persone_riviste": sum(r["_origine"] == "riferimento" for r in persone),
        "imprese_aperte": imprese,
        "schede_inps": len(json.loads(schede[-1].read_text(encoding="utf-8"))) if schede else None,
        "documenti": len(yaml.safe_load(classificati.read_text(encoding="utf-8"))) if classificati.exists() else None,
        "fonti": len(tutte_le_fonti()),
    }


def passo(ramo, profilo, giorno, estratte=False):
    """Un passo della demo: esiti con il profilo di adesso e prossima domanda (None quando non serve altro)."""
    if ramo == "imprese":
        regole, _ = ramo_imprese(giorno)
        esiti = valuta_tutte(regole, profilo)
        domanda = domanda_imprese(profilo, giorno)
    else:
        completo = completa(profilo, giorno)
        esiti = valuta_tutte(regole_persone(estratte), completo, giorno)
        campo, usi = prossima_persone(esiti, completo)
        domanda = domanda_persone(campo, usi, completo) if campo else None
    esiti.sort(key=lambda e: (ORDINE_ESITI.index(e.stato), e.regola["titolo"]))
    conteggi = {s: sum(e.stato == s for e in esiti) for s in ORDINE_ESITI}
    out = {"riepilogo": riepilogo(profilo) if ramo == "persone" else [], "domanda": domanda, "conteggi": conteggi, "risultati": [risultato(e, completo if ramo == "persone" else profilo) for e in esiti], "giorno": giorno}
    if ramo == "persone":
        # Le regioni "vicine" alla persona: residenza, domicilio e sede del corso (anche ricavata dal comune; decisione 73)
        vicine = [completo.get(k) for k in ("regione", "regione_domicilio", "regione_ateneo")]
        out["regioni_vicine"] = list(dict.fromkeys(r for r in vicine if r in REGIONI))
        # Bandi chiusi negli ultimi 12 mesi: di solito riaprono ogni anno (borse DSU, contributi affitto). Si mostrano a
        # parte, fuori dai conteggi, per chi usa il servizio fuori stagione (decisione 72).
        un_anno_fa = (dt.date.fromisoformat(giorno) - dt.timedelta(days=365)).isoformat()
        chiusi = [valuta(r, completo) for r in regole_persone(estratte)
                  if r.get("chiusura") and un_anno_fa <= r["chiusura"] < giorno]
        out["chiusi_di_recente"] = [risultato(e, completo) for e in sorted(chiusi, key=lambda e: e.regola["chiusura"], reverse=True)
                                    if e.stato != NON_IDONEO]
    if ramo == "persone" and completo.get("isee") == NON_SO:
        # chi non sa il proprio ISEE: quanti benefici restano in sospeso per quello (docs/contesto.md, idea 1)
        n = sum(e.stato == MANCANO_DATI and dipende_da_isee(e.regola) for e in esiti)
        if n:
            out["isee"] = {"decide": n, "link": LINK_ISEE}
    return out
