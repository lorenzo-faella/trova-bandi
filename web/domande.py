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
import re
import json
import hashlib
from functools import lru_cache
from pathlib import Path

import yaml

from pipeline.motore import (CONFRONTI, DA_VERIFICARE, IDONEO, IDONEO_SALVO, MANCANO_DATI, NON_IDONEO, NON_SO, QUASI,
                             aperta, contiene_non_modellabile, figli, valuta, valuta_tutte, verifica, stato_temporale)
from pipeline.citazioni import nodi
from pipeline.fonti.elenchi import tutte_le_fonti
from pipeline.normalizza import REGIONI, carica_comuni_istat
from pipeline.profili import Generatore
from pipeline.questionario import DOMANDE, Questionario
from pipeline.regole import DIR_PERSONE, LOADER, ROOT, carica
from web.validazione import valida

FILE_DOMANDE = ROOT / "data" / "domande_persone.yaml"
DIR_ESTRATTE = [ROOT / "data" / "regole_estratte" / "lotto-1", ROOT / "data" / "regole_estratte" / "lotto-2",
                ROOT / "data" / "regole_estratte" / "documenti"]
# Le etichette scritte a mano (data/gold) sono regole riviste da una persona, per 12 dei 14 benefici tenuti fuori dalle estrazioni
# apposta: senza di loro la demo non mostrava mai bonus nido, bonus psicologo, SFL, assegno sociale, congedi (decisione 78).
# Dove ci sono le due etichette si usa quella di Lorenzo. Fuori le due ancora da correggere: la discontinuità senza il
# requisito "lavoratore dello spettacolo" e la maternità degli autonomi con il "caso per caso" nelle note.
DIR_GOLD = ROOT / "data" / "gold"
ETICHETTE_ESCLUSE = {"inps-indennita-di-discontinuita-a-favore-dei-lavor", "inps-indennita-di-maternita-paternita-per-lavoratr",
                     # chiede solo "disabilità: sì" e dava "ti spetta" anche con un'invalidità del 33% (decisione 83)
                     "inps-carta-europea-della-disabilita-disability-car"}
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
         "isee_universitario": "euro", "isee_minorenni": "euro", "ispe": "euro", "mesi_validita_permesso": "mesi", "crediti_conseguiti": "CFU",
         "percentuale_invalidita": "%", "eta": "anni"}
AIUTI = {"settimane_contributi_4_anni": "Si leggono nell'estratto conto contributivo, sul sito INPS.",
         "isee": "È nell'attestazione ISEE. Se non l'hai, rispondi \"non lo so\".",
         "nucleo": "Indica il nucleo riportato nell'ISEE, che può includere familiari non conviventi. Tu sei la prima persona. Puoi non conoscere l'età di un singolo componente.",
         "ispe": "ISPE = ISP diviso parametro della scala di equivalenza: entrambi si trovano nell'attestazione ISEE. Esempio: ISP 30.000 e scala 2 danno ISPE 15.000. Usa i dati per il diritto allo studio universitario.",
         "patrimonio_immobiliare": "Indica il valore ai fini ISEE degli immobili in Italia e all'estero, esclusa la casa di abitazione: non il prezzo di mercato. Se non lo conosci, scegli Non lo so.",
         "reddito_richiedente": "Il reddito complessivo IRPEF della dichiarazione relativa all'anno scorso; non lo stipendio netto. Se non hai il documento, scegli Non lo so.",
         "anni_residenza_continuativa_italia": "Considera la residenza anagrafica, non una permanenza per vacanza o studio. Le eccezioni previste da ciascun beneficio restano da verificare.",
         "nucleo.figlio_a_carico": "Considera la situazione del figlio nel nucleo e le condizioni previste dal beneficio. Se il carico non è chiaro, scegli Non lo so."}
# La data del figlio è una domanda sola, da cui si ricavano giorni e mesi (vocabolario, scelta 4).
DERIVATI = {"giorni_da_evento_figlio": "data_evento_figlio", "mesi_da_evento_figlio": "data_evento_figlio"}
# Risposta a una domanda che non si fa perché non riguarda la persona (decisione 64): non è in nessun elenco di valori
# ammessi, quindi un requisito "tipo_lavoro in [dipendente]" risulta falso invece di restare senza dati.
NON_APPLICABILE = "non_applicabile"
ANNI_ITALIA = ("anni_residenza_italia", "anni_residenza_continuativa_italia")
# I numeri hanno un valore ovvio solo in pochi casi: chi non ha una disabilità ha invalidità 0, chi non ha perso il
# lavoro non ha una cessazione recente (come NESSUN_EVENTO). Gli altri (reddito, contributi, ISPE) restano senza dati.
# Campi calcolati: per conoscerli serve la domanda indicata. L'età di chi fa domanda è quella del primo componente
# del nucleo ("Tu"): non si chiede due volte.
RICAVATI = {"numero_figli": "nucleo.figlio", "numero_componenti": "nucleo", "eta": "nucleo.eta", "regione_ateneo": "comune_ateneo", "provincia_ateneo": "comune_ateneo"}


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


def dipendenze():
    """Dipendenze per la modifica: solo fatti condizionati, non l'intero percorso."""
    return {k: d["solo_se"] for k, d in domande().items() if d.get("solo_se")}


def prossimo_passo(r):
    specifici = {
        "inps-naspi": "Con INPS o patronato: estratto contributivo dei 4 anni e ultimi 12 mesi, lettera/verbale di cessazione, eventuali precedenti dimissioni/accordi nei 12 mesi, contratti rimasti e redditi annui presunti. Verifica settimane utili, termine effettivo e comunicazioni NASpI-COM anche con reddito zero.",
        "toscana-contributi-per-la-frequenza-delle-scuole-9bae68": "Al Comune dove si trova la scuola: chiedi l'avviso Buoni scuola 2026/27 per le famiglie e il termine locale; porta iscrizione con posto disponibile, retta e attestazione ISEE minorenni valida senza omissioni/difformità. Domanda da un solo genitore/tutore al Comune, non alla Regione.",
        "ergo-assegni-formativi-3220ed": "A ER.GO: verifica bando completo e allegati, tipo/anno di ISEE e ISPE, titolo conseguito in Emilia-Romagna e certificato del corso postlaurea all'estero (durata e titolo finale). Il solo comune del corso non identifica l'ateneo ammesso.",
    }
    if r["id"] in specifici:
        return specifici[r["id"]]
    if "psicologo" in r["id"]:
        return "Controlla sulla scheda INPS il messaggio con le date dell'annualità corrente: le acquisizioni ufficiali del 21/11/2026 documentano ancora il 2025. Prepara l'ISEE valido, senza dedurre che la domanda sia aperta."
    if r["stato"] == NON_IDONEO:
        return "Confronta il requisito non soddisfatto con i tuoi documenti; correggi la risposta se errata."
    if r["stato_temporale"] == "non verificato":
        return "Chiedi all'ente indicato se esiste una finestra corrente per il tuo ruolo; la pagina generale non prova l'apertura."
    if r["stato_temporale"] == "futuro":
        return "Controlla sulla fonte la data di apertura e prepara i documenti richiesti."
    return "Apri la fonte e verifica con l'ente i dubbi elencati prima di presentare domanda. Per ISEE rivolgiti a un CAF; per contributi e NASpI a INPS o patronato."


# --- Regole -----------------------------------------------------------------------------------------------------------

def leggi_cartella(cartella, origine):
    out = []
    for f in sorted(Path(cartella).glob("*.yaml")):
        r = yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER)
        from pipeline.regole import VALIDATORE
        VALIDATORE.validate(r)
        r["_origine"] = origine
        r["_hash_regola"] = hashlib.sha256(f.read_bytes()).hexdigest()
        out.append(r)
    return out


def etichette():
    lorenzo = leggi_cartella(DIR_GOLD / "lorenzo", "riferimento")
    gia = {r["id"] for r in lorenzo} | ETICHETTE_ESCLUSE
    return lorenzo + [r for r in leggi_cartella(DIR_GOLD / "edo", "riferimento") if r["id"] not in gia]


def permanente_se_nazionale(r):
    """Le misure nazionali senza date (prestazioni INPS, bonus luce e gas, detrazioni, Fondo prima casa) sono
    strutturali: si chiedono tutto l'anno. Senza questa indicazione finivano nel gruppo "date da verificare" e sparivano
    dai possibili e da "ti spetta" proprio gli aiuti principali (decisione 95). I bandi locali senza date restano da
    verificare."""
    if r.get("disponibilita") or r.get("apertura") or r.get("chiusura") or r.get("finestre"):
        return
    if r["id"].startswith("inps-") or territorio(r) is None:
        r["disponibilita"] = "permanente"


@lru_cache(maxsize=None)
def regole_persone(estratte=False):
    regole = leggi_cartella(DIR_PERSONE, "riferimento") + etichette()
    if estratte:
        regole += [r for d in DIR_ESTRATTE for r in leggi_cartella(d, "estratta")]
    for r in regole:
        permanente_se_nazionale(r)
    # Rettifiche operative versionate separatamente: i riferimenti gold restano originali.
    corrette = {r["id"]: r for r in leggi_cartella(ROOT / "data/regole_revisionate", "riferimento")}
    for i, r in enumerate(regole):
        if r["id"] in corrette:
            nuova = corrette[r["id"]]
            nuova["_versioni_precedenti"] = [{"id": r["id"], "sha256": r["_hash_regola"],
                                            "motivo": "Rettifica economica documentata; etichetta gold originale conservata."}]
            regole[i] = nuova
    # Le due versioni toscane descrivono la stessa misura. Si usa la più recente,
    # mantenendo visibili le note che segnalano limiti e dubbi della precedente.
    revisioni = yaml.safe_load((ROOT / "data" / "revisioni_demo.yaml").read_text(encoding="utf-8"))
    sostituite = revisioni["sostituite"]
    presenti = {r["id"]: r for r in regole}
    for vecchia, nuova in sostituite.items():
        if vecchia in presenti and nuova in presenti:
            nuova_regola = presenti[nuova]
            nuova_regola["_versioni_precedenti"] = [{"id": vecchia, "sha256": presenti[vecchia]["_hash_regola"], "motivo": "Stessa misura ed edizione; fascia d'età dal titolo ritirata: iscrizione e ISEE minorenni richiedono verifica comunale."}]
            fonte_buoni = "Allegato A decreto Toscana 14880/2026, art. 1; data/fonti_verificate/buoni-allegato.txt"
            nuova_regola["requisiti"] = [
                {"campo": c, "operatore": "vero", "fonte": fonte_buoni, "citazione": cit}
                for c, cit in [
                    ("genitore_tutore_buoni_toscana", "genitore/tutore"),
                    ("bambino_residente_toscana_buoni", "residente in un Comune della Toscana"),
                    ("iscrizione_effettiva_buoni_toscana", "iscritti e abbiano disponibilità di un posto"),
                    ("retta_buoni_toscana", "tariffa/retta")]] + [
                {"campo": "isee_minorenni", "operatore": "<=", "valore": 30000,
                 "fonte": fonte_buoni, "citazione": "30.000,00 euro"},
                {"non_modellabile": "Attestazione ISEE minorenni in corso di validità e senza omissioni/difformità al momento della domanda. Chiedere al Comune dove si trova la scuola il suo avviso per le famiglie, i termini e la disponibilità di risorse: la scadenza regionale per i Comuni non è quella delle famiglie. Solo un genitore/tutore può fare domanda; sconto sulla retta, non un pagamento libero alla famiglia. Verificare mensilità di iscrizione e altri rimborsi sulle stesse spese.",
                 "fonte": fonte_buoni}]
            nuova_regola["note"] = [t for t in nuova_regola.get("note", []) if "approssimazione" not in t]
            nuova_regola["_identita"] = {"misura": "toscana-buoni-scuola-infanzia", "edizione": "2026"}
            nuova_regola["ultimo_controllo"] = "2026-11-21"
            nuova_regola["provenienza"] = {**nuova_regola.get("provenienza", {}), "rettifica_demo": {
                "data": "2026-11-21", "fascicolo": "docs/completamento-2026-11-21",
                "base": "Allegato A decreto 14880/2026; manifest fonti, acquisizioni e hash nel fascicolo",
                "revisione_umana": None}}
    # Indicazione esplicita dell'utente: il caso co.co.co senza partita IVA resta
    # da verificare nella demo. Le etichette gold restano immutate e non si attribuisce
    # una revisione normativa alla risposta ricevuta in chat.
    for r in regole:
        if r["id"] == "inps-indennita-straordinaria-di-continuita-redditu":
            for i, q in enumerate(r["requisiti"]):
                if q.get("campo") == "tipo_lavoro":
                    r["requisiti"][i] = {"almeno_uno_di": [q, {"tutti_di": [
                        {"campo": "tipo_lavoro", "operatore": "in", "valori": ["parasubordinato"]},
                        {"campo": "iscro_cococo_senza_iva", "operatore": "vero"},
                        {"non_modellabile": "Caso co.co.co senza partita IVA: da verificare su indicazione dell'utente del 21/11/2026. Portare contratto e posizione previdenziale a INPS/patronato; fonte e revisore per l'adjudicazione normativa non ancora indicati."}]}],
                        "fonte": q["fonte"], "citazione": q.get("citazione", "Gestione Separata")}
            r["note"] = r.get("note", []) + ["Indicazione per la demo conservata in data/indicazioni_autori_demo.yaml; non è una modifica delle etichette gold né un diritto riconosciuto."]
            r["ultimo_controllo"] = "2026-11-21"
            r["provenienza"] = {**r.get("provenienza", {}), "indicazione_demo": {
                "data": "2026-11-21", "registro": "data/indicazioni_autori_demo.yaml",
                "adjudicazione_normativa": "in attesa di fonte e revisore", "revisione_umana": None}}
    for r in regole:
        if "psicologo" in r["id"]:
            r["note"] = r.get("note", []) + ["La scheda ufficiale consultata il 21/11/2026 documenta il 15/09–14/11/2025. Una finestra 2026 non è verificata; nessun invito a presentare domanda oggi."]
    escluse = set(revisioni["escluse"]) | {k for k, v in sostituite.items() if v in presenti}
    return [r for r in regole if r["id"] not in escluse]


DIR_IMPRESE_DOCUMENTI = ROOT / "data" / "regole_imprese_documenti"


def regole_imprese_documenti():
    """Conserva i requisiti documentati. La provenienza dell'ente serve solo a ordinare.

    Rettifica della decisione 88: non prova una sede obbligatoria, neppure per le imprese.
    """
    return leggi_cartella(DIR_IMPRESE_DOCUMENTI, "estratta")


def solo_campi(regola):
    """Per il questionario delle imprese, costruito sui filtri del portale: solo i requisiti su un campo. Le condizioni
    non modellabili e le alternative restano nella regola intera, che decide l'esito."""
    return dict(regola, requisiti=[q for q in regola["requisiti"] if "campo" in q])


@lru_cache(maxsize=None)
def ramo_imprese(giorno):
    """Regole aperte quel giorno e questionario con il suo campione: si costruiscono una volta (meno di 2 secondi)."""
    regole = [dict(r, _origine="open data") for r in carica() if aperta(r, giorno)]
    if not regole:
        raise RuntimeError("nessuna regola delle imprese: eseguire prima `make dati`")
    regole += [r for r in regole_imprese_documenti() if stato_temporale(r, giorno) != "chiuso"]
    semplici = [solo_campi(r) for r in regole]
    return regole, Questionario(semplici, Generatore(semplici, seed=1).campione(N_CAMPIONE))


@lru_cache(maxsize=None)
def sedi_istat():
    """Nome -> tutte le coppie provincia/regione ISTAT, senza perdere gli omonimi."""
    import csv
    import io
    istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))[-1]
    righe = csv.DictReader(io.StringIO(istat.read_bytes().decode("latin-1")), delimiter=";")
    prov = next(k for k in righe.fieldnames if k.startswith("Denominazione dell'Unità territoriale sovracomunale"))
    out = {}
    for r in righe:
        out.setdefault(r["Denominazione in italiano"], []).append((r[prov], r["Denominazione Regione"]))
    return out


@lru_cache(maxsize=None)
def codici_comuni():
    istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))[-1]
    import csv
    import io
    righe = csv.DictReader(io.StringIO(istat.read_bytes().decode("latin-1")), delimiter=";")
    return {(r["Denominazione in italiano"], r["Denominazione Regione"]): r["Codice Comune formato alfanumerico"] for r in righe}


def comuni_del_profilo(profilo):
    out = {}
    for campo, campo_regione in (("comune", "regione"), ("comune_domicilio", "regione_domicilio"), ("comune_ateneo", "regione_ateneo")):
        nome = profilo.get(campo)
        if nome not in sedi_istat():
            continue
        regione = profilo.get(campo_regione)
        if regione not in REGIONI and len(sedi_istat()[nome]) == 1:
            regione = sedi_istat()[nome][0][1]
        out[campo] = {"nome": nome, "codice": codici_comuni().get((nome, regione))}
    return out


@lru_cache(maxsize=None)
def comuni_per_regione():
    istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))[-1]
    out = {}
    for nome, sedi in sedi_istat().items():
        for provincia, regione in sedi:
            out.setdefault(regione, set()).add(nome)
    return {r: sorted(v) for r, v in out.items()}


@lru_cache(maxsize=None)
def opzioni_imprese(giorno):
    regole, _ = ramo_imprese(giorno)
    valori = {c: set() for c in ("tipologia", "dimensione", "settore", "ambito")}
    for r in regole:
        for q in (n for req in r["requisiti"] for n in nodi(req)):
            if q.get("campo") in valori:  # le regole dai documenti hanno anche condizioni non modellabili (decisione 88)
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


def ricava_doppioni(p):
    """Domande specifiche che una risposta generale decide con certezza (decisione 93): l'età nel 2025 per la detrazione
    affitto giovani (20-30 anni) è sì per chi oggi ha da 21 a 30 anni, no da 32 in su o sotto 20; a 31 anni si chiede.
    Il reddito per le detrazioni (con la cedolare secca) e l'ISEE per le prestazioni familiari (diverso con genitori non
    conviventi) non si ricavano: non coincidono sempre con il reddito IRPEF e con l'ISEE ordinario."""
    eta = p.get("eta")
    if isinstance(eta, (int, float)) and "eta_giovani_locazione_2025" not in p:
        if 21 <= eta <= 30:
            p["eta_giovani_locazione_2025"] = True
        elif eta >= 32 or eta < 20:
            p["eta_giovani_locazione_2025"] = False


def completa(profilo, giorno):
    """Profilo per il motore: ciò che si ricava dalle risposte, senza chiedere e senza tirare a indovinare.

    Dalla data del figlio i giorni e i mesi; dai componenti il numero dei figli; dal primo componente l'età di chi fa
    domanda. Chi fa domanda non è figlio di sé stesso;
    chi non è figlio non è un figlio a carico. Le inferenze ammesse sono esplicite in `non_applicabili`.
    Né la situazione attuale né la composizione attuale del nucleo dimostrano l'assenza di eventi passati.
    """
    p = valida(profilo, domande(), sedi_istat(), REGIONI, giorno)
    p["_anno_valutazione"] = dt.date.fromisoformat(giorno).year
    from web.economia import completa_economia
    completa_economia(p)
    # Compatibilità dei vecchi fatti aggregati: un sì senza dettaglio resta ignoto.
    if p.get("veicoli_esclusi") is False or (p.get("veicoli_esclusi") is True and p.get("solo_veicoli_agevolati") is True):
        p.setdefault("auto_moto_non_agevolati", False)
        p.setdefault("barche_aerei", False)
    # Compatibilità dei vecchi profili che contengono già un evento esplicito.
    # La situazione attuale (studente/occupato) non dice se un lavoro è terminato.
    if "lavoro_terminato" not in p and any(p.get(k) not in (None, NON_SO) for k in
            ("causa_fine_lavoro", "giorni_da_cessazione_lavoro")):
        p["lavoro_terminato"] = True
    nucleo = p.get("nucleo")
    if isinstance(nucleo, list):
        p["nucleo"] = nucleo = [dict(c) for c in nucleo]
        if nucleo:
            p["numero_componenti"] = len(nucleo)  # "nuclei di almeno 3 componenti" (Carta Dedicata a te, decisione 80)
            nucleo[0].setdefault("figlio", False)
            eta = next((v for v in (p.get("eta"), nucleo[0].get("eta")) if v not in (None, NON_SO)),
                       p.get("eta", nucleo[0].get("eta")))
            if eta is not None:
                p["eta"] = nucleo[0]["eta"] = eta
            # Il richiedente e "Tu" sono la stessa persona. L'età non dimostra
            # invece la parentela degli altri (adozione e affidamento inclusi).
            disabilita = next((v for v in (p.get("disabile"), nucleo[0].get("disabile")) if v not in (None, NON_SO)),
                              p.get("disabile", nucleo[0].get("disabile")))
            if disabilita is not None:
                p["disabile"] = nucleo[0]["disabile"] = disabilita
        for c in nucleo:
            if c.get("figlio") is False:
                c.setdefault("figlio_a_carico", False)
        risposte = [c.get("figlio") for c in nucleo]
        if None not in risposte:
            n = sum(r is True for r in risposte)
            # con un "non lo so" il numero vero può essere più alto: "almeno 4 figli" resta in sospeso, non è un no (decisione 83)
            p["numero_figli"] = NON_SO if NON_SO in risposte else n
    elif nucleo == NON_SO:
        p["numero_figli"] = p["numero_componenti"] = NON_SO
        p.setdefault("eta", NON_SO)
    # Pagina della residenza (decisione 80): chi non risiede in Italia non ha regione né comune di residenza; chi è nato
    # in Italia e ci ha sempre vissuto ci risiede da quando è nato, senza interruzioni.
    if p.get("residente_italia") is False:
        p.setdefault("regione", NON_APPLICABILE); p.setdefault("comune", NON_APPLICABILE)
    if p.get("sempre_in_italia") is True and isinstance(p.get("eta"), (int, float)):
        for campo in ANNI_ITALIA:
            if p.get(campo) in (None, NON_SO):
                p[campo] = p["eta"]
    sede = p.get("comune_ateneo")
    if sede == NON_SO:
        p.setdefault("provincia_ateneo", NON_SO); p.setdefault("regione_ateneo", NON_SO)
    elif sede and sede in sedi_istat():
        scelte = [s for s in sedi_istat()[sede] if p.get("regione_ateneo") in (None, NON_SO, s[1])]
        if len(scelte) == 1:
            for campo, valore in (("provincia_ateneo", scelte[0][0]), ("regione_ateneo", scelte[0][1])):
                if p.get(campo) in (None, NON_SO):
                    p[campo] = valore
    if p.get("domicilio_diverso") is False:
        for campo, base in (("regione_domicilio", "regione"), ("comune_domicilio", "comune")):
            if p.get(campo) in (None, NON_SO):
                p[campo] = p.get(base)
        p = {k: v for k, v in p.items() if v is not None}
    non_applicabili(p)
    data = p.pop("data_evento_figlio", None)
    if data == "nessuno":
        p.update(NESSUN_EVENTO)
    elif data == NON_SO:
        p.update({k: NON_SO for k in NESSUN_EVENTO})
    elif data:
        d, oggi = dt.date.fromisoformat(data), dt.date.fromisoformat(giorno)
        p.update({"giorni_da_evento_figlio": (oggi - d).days, "mesi_da_evento_figlio": mesi_interi(d, oggi)})
    ricava_doppioni(p)
    return p


DOMICILIO = ("regione_domicilio", "comune_domicilio")  # chi vive dove risiede: si ricavano dalla residenza, non sono "non applicabili"


def non_applicabili(p):
    """Sole inferenze giustificate dai fatti; un cancello chiuso non prova mai falso.

    Le altre domande restano assenti/ignote. NON_APPLICABILE è distinto da NON_SO.
    """
    if p.get("disabile") is False:
        p.setdefault("percentuale_invalidita", 0)
    if p.get("lavoro_terminato") is False:
        p.setdefault("ultimo_lavoro_subordinato", False)
    if p.get("cittadinanza") in {"italiana", "ue", "apolide", "protezione_internazionale", "extra_ue_lungo_periodo"}:
        p.setdefault("permesso_casi_speciali", False)
    occupazione = p.get("condizione_lavorativa")
    if isinstance(occupazione, str):
        occupazione = [occupazione]
    if isinstance(occupazione, list) and set(occupazione) & {"disoccupato", "inattivo"}:
        p.setdefault("lavora_in_italia", False)
        p.setdefault("tipo_lavoro", NON_APPLICABILE)


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
    if chiave == "reddito_rilevante_successiva_inabilita":
        for campo in ("reddito_pensioni_corrente_inabilita", "altri_redditi_precedente_inabilita"):
            if profilo.get(campo) is None:
                return da_porre(campo, profilo)
        return None
    if chiave in RICAVATI:
        return da_porre(RICAVATI[chiave], profilo)
    if chiave in ANNI_ITALIA and profilo.get("sempre_in_italia") is True:
        return da_porre("eta", profilo)  # gli anni in Italia sono la sua età
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
        for i, c in enumerate(nucleo):
            if d["campo"] == "disabile" and i == 0 and c.get("disabile") is None:
                return "disabile"
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


MIN_USI = 3


def regioni_vicine(profilo):
    return {profilo.get(k) for k in ("regione", "regione_domicilio", "regione_ateneo")} & set(REGIONI)


def senza_spiegazione(testo):
    """"Condizione X: manca un campo …" → "Condizione X": la spiegazione serve a noi, non a chi risponde."""
    return re.split(r":\s*(?=mancan?o?\b|manca\b|il vocabolario|nel vocabolario|il sito non|è un dato|non c'è un campo)", testo)[0].strip()


# Chi deve esserci nel nucleo perché una condizione scritta a parole (non modellabile) abbia senso (decisione 101).
# Solo segnali che non lasciano dubbi: un nido o una scuola vogliono un bambino o un ragazzo, "anziano" una persona
# anziana, una frase che comincia con "il figlio" o "il minore" un figlio o un minore, l'assistenza a una persona non
# autosufficiente qualcuno con disabilità. "Figli" da solo no: compare anche
# nelle esclusioni ("non spetta ai nuclei con figli") e nelle alternative; "asilo" nemmeno, per il diritto d'asilo.
PERSONA_RICHIESTA = [
    (re.compile(r"\bnid[oi]\b|micro-?nid|prima infanzia|sezion[ei] primavera|scuol[ae] dell'infanzia", re.I),
     lambda c: c["eta"] <= 6),
    (re.compile(r"scuol[ae] (statal[ei] )?(primari|secondari|medi[ae]\b|elementar|paritari|di ogni ordine)|\balunn[oi]\b|"
                r"carriera scolastica|frequenza scolastica", re.I), lambda c: c["eta"] <= 20),
    (re.compile(r"^(il|la) (figli[oa]|minore|bambin[oa])\b", re.I), lambda c: c["eta"] < 18 or c.get("figlio") is True),
    (re.compile(r"\banzian[oaie]\b|\bover ?65\b|\bultra ?65|ultrasessantacinquenn", re.I), lambda c: c["eta"] >= 60),
    # una persona non autosufficiente: nel nucleo serve qualcuno con disabilità, o di cui non si sa
    (re.compile(r"non autosufficien", re.I), lambda c: c.get("disabile") is not False),
]
TERRITORIO = {"regione", "comune", "regione_domicilio", "comune_domicilio"}
CITTADINANZA = {"cittadinanza", "mesi_validita_permesso", "permesso_casi_speciali"}


def contraddetto(req, profilo, rivista=False):
    """Una condizione ancora aperta che i dati già noti rendono impossibile o fuori luogo: una scuola o un nido senza
    nessun bambino o ragazzo nel nucleo, un'alternativa con tutte le vie già escluse. Serve solo a non proporla fra le
    verifiche finali: il motore non la esclude, perché il testo a parole non è una prova.
    In una regola estratta, anche un'alternativa la cui via descritta con i dati del profilo è già esclusa e resta aperta
    solo per un'eccezione scritta a parole: chi vive solo e la Carta per i nuclei di almeno 3 persone, chi abita in un
    altro comune e le case popolari "per i residenti, o per chi lavora lì". Nelle regole riviste a mano le vie a parole
    sono alternative vere (l'assegno unico per chi ha un permesso di soggiorno), quindi restano."""
    if "non_modellabile" in req:
        nucleo = profilo.get("nucleo")
        if not isinstance(nucleo, list) or not nucleo:
            return False
        if not all(isinstance(c, dict) and isinstance(c.get("eta"), (int, float)) for c in nucleo):
            return False  # un'età non nota: potrebbe essere proprio il bambino
        return any(segnale.search(req["non_modellabile"]) and not any(adatta(c) for c in nucleo)
                   for segnale, adatta in PERSONA_RICHIESTA)
    if "almeno_uno_di" in req:
        vie = req["almeno_uno_di"]
        if all(verifica(q, profilo) is False or contraddetto(q, profilo, rivista) for q in vie):
            return True
        # le vie sulla cittadinanza e sul permesso no: il vocabolario non ha tutti i titoli di soggiorno, e la via
        # "stranieri con permesso" scritta a parole è vera (assegno di maternità dei Comuni per una famiglia extra UE)
        con_dati = [q for q in vie if not contiene_non_modellabile(q)
                    and not {n.get("campo") for n in nodi(q)} & CITTADINANZA]
        return not rivista and bool(con_dati) and all(verifica(q, profilo) is False for q in con_dati)
    if "tutti_di" in req:
        return any(verifica(q, profilo) is None and contraddetto(q, profilo, rivista) for q in req["tutti_di"])
    return False


def ancora_aperto(req, profilo):
    """Il requisito senza le parti già decise, per la domanda di verifica: in un'alternativa si tolgono le vie già
    escluse, in un "tutte queste" le parti già soddisfatte. Chi vive solo non legge "almeno 3 componenti"."""
    for chiave, via in (("almeno_uno_di", False), ("tutti_di", True)):
        if chiave in req:
            resto = [ancora_aperto(q, profilo) for q in req[chiave] if verifica(q, profilo) is not via]
            if len(resto) == 1:
                return dict(resto[0], citazione=resto[0].get("citazione") or req.get("citazione"))
            return dict(req, **{chiave: resto}) if resto else req
    return req


def verifiche(esiti, profilo, massimo=10):
    """Le verifiche finali (decisione 93): per gli aiuti possibili della zona della persona, con almeno un requisito a
    favore e al massimo 2 requisiti ancora aperti, una domanda sì/no per ciascuno. Prima quelli a cui manca una sola
    risposta, poi le regole riviste. Chi conferma tutto ottiene "ti spetta", chi risponde no lo vede escluso.
    Restano fuori (decisione 101) gli aiuti che hanno a favore solo il territorio, che vale per tutti i residenti, e
    quelli con una condizione aperta che i dati già noti contraddicono (`contraddetto`)."""
    out = []
    for e in esiti:
        r = e.regola
        if e.stato not in (DA_VERIFICARE, MANCANO_DATI) or not 1 <= len(e.mancanti) <= 2:
            continue
        principale = r.get("_origine") == "riferimento"  # regole riviste: verificabili anche senza niente a favore (decisione 94)
        # il territorio è a favore di tutti i residenti: non dice quanto l'aiuto è pertinente (decisioni 96, 101)
        favore = sum(a_favore(q, profilo, conta_territorio=False) for q in r["requisiti"])
        if fuori_zona(r, profilo) or not (principale or favore):
            continue
        if any(contraddetto(m, profilo, principale) for m in e.mancanti):
            continue
        indici = [i for i, q in enumerate(r["requisiti"]) if any(q is m for m in e.mancanti)]
        aperti = {i: ancora_aperto(r["requisiti"][i], profilo) for i in indici}
        out.append({"id": r["id"], "titolo": r["titolo"], "ente": r.get("ente"), "rivista": principale, "favore": favore,
                    "domande": [{"chiave": f"{r['id']}#{i}", "testo": senza_spiegazione(descrivi(aperti[i])),
                                 "citazione": aperti[i].get("citazione") or r["requisiti"][i].get("citazione")}
                                for i in indici]})
    # prima gli aiuti più vicini (una sola risposta), poi quelli con più requisiti già a favore (più pertinenti per la
    # persona: un aiuto per studenti universitari batte uno per orfani di femminicidio), poi le regole riviste (decisione 96)
    out.sort(key=lambda v: (len(v["domande"]), -v["favore"], not v["rivista"], v["titolo"]))
    return out[:massimo]


def risposte_vere(verifiche_, profilo_vero, giorno, sconosciute=True):
    """Per le prove: le risposte alle verifiche date da chi conosce tutto il profilo. Un requisito su un dato si risponde
    con il dato; uno non modellabile vale `sconosciute` (sì, per misurare il massimo)."""
    pieno, regole = completa(profilo_vero, giorno), {r["id"]: r for r in regole_persone(True)}
    out = {}
    for v in verifiche_:
        for q in v["domande"]:
            rid, _, i = q["chiave"].rpartition("#")
            esito = verifica(regole[rid]["requisiti"][int(i)], pieno) if rid in regole else None
            out[q["chiave"]] = sconosciute if esito is None else esito
    return out


def applica_conferme(regole, profilo):
    """Le risposte alle verifiche finali: un requisito confermato vale sì, uno negato vale no (decisione 93)."""
    conferme = {k: v for k, v in (profilo.get("conferme") or {}).items() if v in (True, False)}
    if not conferme:
        return regole
    per_regola = {}
    for k, v in conferme.items():
        rid, _, i = k.rpartition("#")
        if i.isdigit():
            per_regola.setdefault(rid, {})[int(i)] = (k, v)
    out = []
    for r in regole:
        if r["id"] in per_regola:
            req = list(r["requisiti"])
            for i, (k, v) in per_regola[r["id"]].items():
                if 0 <= i < len(req):
                    req[i] = {"campo": "conferma:" + k, "operatore": "vero", "verifica": senza_spiegazione(descrivi(r["requisiti"][i])),
                              "citazione": r["requisiti"][i].get("citazione"), "fonte": r["requisiti"][i].get("fonte")}
            r = dict(r, requisiti=req, _confermata=True)
        out.append(r)
    return out


def prossima_persone(esiti, profilo):
    """La domanda che avvicina di più gli esiti ancora aperti ("mancano dati").

    Ogni beneficio aperto dà a ognuna delle sue domande mancanti 1/k punti, dove k è quante gliene mancano: un beneficio
    a cui manca una sola risposta pesa di più, perché quella risposta lo decide. È la stessa idea del questionario
    delle imprese (decisione 10), senza il campione di profili fittizi: per le persone non c'è ancora una popolazione
    realistica (docs/da-fare.md). Una domanda chiusa dal suo `solo_se` non si fa; se dipende da una risposta che manca,
    si fa prima quella. Restituisce (campo, quanti benefici la usano) o (None, 0).
    """
    # Residenza e domicilio si chiedono per primi, ognuno in una pagina sola: decidono quali bandi locali sono "vicini"
    # anche se nessuna regola li usa (decisioni 71 e 80).
    if profilo.get("residente_italia") is None or (profilo["residente_italia"] is True and profilo.get("regione") is None):
        return "residenza", 0
    if profilo.get("domicilio_diverso") is None:
        return "domicilio", 0
    punti, usi, probabili = {}, {}, set()
    for e in esiti:
        if e.stato != MANCANO_DATI:
            continue
        if fuori_zona(e.regola, profilo):
            continue  # i bandi di altre regioni o di altri Comuni non fanno domande (decisioni 93, 104)
        mancanti = {c for q in e.regola["requisiti"] for c in da_chiedere(q, profilo)}
        reali = {r for r in (da_porre(c, profilo) for c in mancanti) if r}
        # le domande specifiche solo per gli aiuti che hanno già qualcosa a favore; le altre condizioni degli aiuti
        # principali arrivano alla fine, fra le verifiche (decisione 94)
        probabile = any(a_favore(q, profilo) for q in e.regola["requisiti"])
        for c in reali:
            punti[c] = punti.get(c, 0) + 1 / len(reali)
            usi[c] = usi.get(c, 0) + 1
            if probabile:
                probabili.add(c)
    # Una domanda che serve a meno di MIN_USI aiuti è specifica di un bando: si fa solo se quel bando ha già qualcosa a
    # favore, cioè è probabile. Se no, resta fuori dal questionario; se il bando diventa possibile, la sua domanda arriva
    # alla fine, fra le verifiche sugli aiuti possibili (`verifiche`, decisione 93).
    punti = {c: v for c, v in punti.items() if usi[c] >= MIN_USI or c in probabili}
    if not punti:
        return None, 0
    # prima le domande generali, poi quelle specifiche dei bandi probabili
    generali = {c: v for c, v in punti.items() if usi[c] >= MIN_USI}
    punti = generali or punti
    ordine = list(domande())
    noti = [c for c in ordine if c in punti] + sorted(c for c in punti if c not in ordine)
    campo = max(noti, key=lambda c: (round(punti[c], 9), -noti.index(c)))
    return campo, usi[campo]


def opzioni_persona(d):
    if d["campo"] in ("regione", "regione_ateneo", "regione_domicilio"):
        return scelte(*((r, r) for r in REGIONI))
    etichette = ETICHETTE.get(d["campo"], {})
    return scelte(*((v, etichette.get(v, str(v).replace("_", " ").capitalize())) for v in d.get("valori") or []))


def pagina_persone(chiave):
    """Più domande in una pagina, ognuna mostrata solo se la risposta indicata in `se` è stata data (decisione 80)."""
    regioni = [o for o in opzioni_persona({"campo": "regione"})]
    if chiave == "residenza":
        return {"campo": "residenza", "tipo": "pagina", "bandi_interessati": 0, "testo": "Dove hai la residenza?", "parti": [
            {"campo": "residente_italia", "testo": "Hai la residenza in Italia?", "tipo": "si_no"},
            {"campo": "regione", "testo": "Regione", "tipo": "scelta", "opzioni": regioni, "se": {"residente_italia": True}},
            {"campo": "comune", "testo": "Comune", "tipo": "comune", "regione_da": "regione", "se": {"residente_italia": True}},
            {"campo": "sempre_in_italia", "testo": "Sei nato in Italia e ci hai sempre vissuto?", "tipo": "si_no", "non_so": True,
             "se": {"residente_italia": True}},
            {"campo": "anni_residenza_continuativa_italia", "testo": "Da quanti anni hai residenza anagrafica continuativa in Italia?",
             "tipo": "numero", "unita": "anni", "se": {"sempre_in_italia": False}}]}
    return {"campo": "domicilio", "tipo": "pagina", "bandi_interessati": 0, "testo": "Dove vivi abitualmente?", "parti": [
        {"campo": "domicilio_diverso", "testo": "Vivi in un comune diverso da quello di residenza, per esempio per studio o lavoro?",
         "tipo": "si_no"},
        {"campo": "regione_domicilio", "testo": "Regione", "tipo": "scelta", "opzioni": regioni, "se": {"domicilio_diverso": True}},
        {"campo": "comune_domicilio", "testo": "Comune", "tipo": "comune", "regione_da": "regione_domicilio",
         "se": {"domicilio_diverso": True}}]}


def domanda_persone(chiave, usi, profilo):
    if chiave == "comune_ateneo":
        return {"campo": chiave, "tipo": "pagina", "bandi_interessati": usi,
                "testo": "Dove si svolge il corso?",
                "aiuto": "Scegli regione e comune della sede didattica. Non identifica l'ateneo, la sua sede legale o l'ammissione dello specifico corso al bando: controlla certificato di iscrizione e allegati con l'ente per il diritto allo studio.",
                "valori_attuali": {k: profilo.get(k) for k in ("regione_ateneo", "comune_ateneo")},
                "parti": [{"campo": "regione_ateneo", "testo": "Regione del corso", "tipo": "scelta", "opzioni": opzioni_persona({"campo": "regione_ateneo"})},
                          {"campo": "comune_ateneo", "testo": "Comune del corso", "tipo": "comune", "regione_da": "regione_ateneo"}]}
    if chiave in ("residenza", "domicilio"):
        q = pagina_persone(chiave)
        q["valori_attuali"] = {p["campo"]: profilo.get(p["campo"]) for p in q["parti"]}
        return q
    d = domande().get(chiave) or {"campo": chiave.split(".")[-1], "domanda": nome_campo(chiave).capitalize() + "?", "tipo": "numero"}
    campo = d["campo"]
    q = {"campo": chiave, "testo": d["domanda"], "tipo": TIPI_PERSONE.get(d["tipo"], "testo"), "bandi_interessati": usi}
    if campo in UNITA:
        q["unita"] = UNITA[campo]
    if campo in AIUTI or chiave in AIUTI:
        q["aiuto"] = AIUTI.get(chiave, AIUTI.get(campo))
    anno = profilo.get("_anno_valutazione", dt.date.today().year)
    for k in ("testo", "aiuto"):
        if k in q:
            q[k] = q[k].replace("{anno}", str(anno)).replace("{precedente}", str(anno - 1))
    if q["tipo"] == "numero":
        q.update(minimo=1 if campo == "anno_di_corso" else 0,
                 massimo=120 if campo == "eta" else 100 if campo == "percentuale_invalidita" else None,
                 intero=campo in {"eta", "anno_di_corso", "mesi_validita_permesso", "giorni_da_cessazione_lavoro"})
    q["valore_attuale"] = profilo.get(chiave)
    q["dipendenze"] = dipendenze()
    if q["tipo"] == "multipla":  # per le persone serve almeno una risposta: chi studia e lavora le sceglie tutte e due
        q.update(opzioni=opzioni_persona(d), almeno_una=True)
        if campo == "condizione_lavorativa":
            q["incompatibili"] = [["occupato", "disoccupato", "inattivo"]]
    if q["tipo"] == "scelta":
        q["opzioni"] = opzioni_persona(d)
        if campo in ("comune", "comune_domicilio", "comune_ateneo"):
            regione = {"comune": "regione", "comune_domicilio": "regione_domicilio"}.get(campo)
            q.update(tipo="comune", regione=profilo.get(regione) if regione else None)
    if campo == "data_evento_figlio":
        q.update(testo="Quando è nato (o entrato in famiglia) l'ultimo figlio?", tipo="data",
                 opzioni=scelte(("nessuno", "Nessun evento di nascita o adozione")))
    if chiave.startswith("nucleo."):
        q["per_componente"] = True
        q["componenti"] = [{"indice": i, "eta": c.get("eta")} for i, c in enumerate(profilo.get("nucleo") or [])
                           if (c.get(campo) is None or (campo == "disabile" and i == 0)) and cancello(d, c)[0]]
        if campo == "disabile":
            q["componenti"] = [c for c in q["componenti"] if c["indice"] != 0]
            # "Tu" usa la domanda individuale e la stessa fonte di verità.
        if q.get("modifica"):
            q["componenti"] = [{"indice": i, "eta": c.get("eta"), "valore": c.get(campo)} for i, c in enumerate(profilo.get("nucleo") or [])]
    return q


# --- Prossima domanda: imprese --------------------------------------------------------------------------------------

def domanda_imprese(profilo, giorno):
    regole, Q = ramo_imprese(giorno)
    risposte = {c: profilo[c] for c in DOMANDE if c in profilo}
    campo = Q.prossima(risposte, Q.matrici([risposte]))
    # Le matrici storiche stimano i filtri piatti; la regola intera decide quali
    # fatti sono ancora utili, comprese alternative e più vincoli sullo stesso campo.
    usi = {}
    for r in regole:
        if stato_temporale(r, giorno) == "futuro":
            continue
        if valuta(r, profilo).stato != MANCANO_DATI:
            continue
        for c in {c for q in r["requisiti"] for c in da_chiedere(q, profilo)} & set(DOMANDE):
            usi[c] = usi.get(c, 0) + 1
    if campo not in usi:
        campo = max(usi, key=lambda c: (usi[c], -DOMANDE.index(c)), default=None)
    if campo == "comune" and profilo.get("regione") is None:
        campo = "regione"  # disambiguazione ISTAT, anche se non è un requisito del bando
    if campo is None:
        return None
    det, aperti, _, _ = Q.stato(Q.matrici([risposte]), risposte)
    d = {"campo": campo, "testo": ETICHETTE_IMPRESE[campo], "tipo": TIPI_IMPRESE[campo],
         "bandi_interessati": usi.get(campo, usi.get("comune", 0))}
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
        "lavora_in_italia": "lavoro in Italia", "soggetto_irpef_italia": "soggetto alle imposte sul reddito in Italia",
        "permesso_casi_speciali": "permesso per casi speciali", "ultimo_lavoro_subordinato": "ultimo lavoro da dipendente",
        "veicoli_esclusi": "auto, moto, barche o aerei recenti", "disabile": "disabilità",
        "svantaggio_certificato": "seguito dai servizi socio-sanitari", "figlio_a_carico": "figlio a carico",
        "reddito_annuo": "reddito annuo", "attivita": "attività", "causa_fine_lavoro": "fine del lavoro",
        "condizione_lavorativa": "situazione lavorativa", "patrimonio_immobiliare": "valore degli immobili",
        "anni_residenza_regione": "anni di residenza nella regione", "reddito_richiedente": "reddito personale IRPEF",
        "canone_annuo": "affitto annuo", "numero_figli": "numero di figli", "numero_componenti": "componenti del nucleo",
        "sempre_in_italia": "nato in Italia e sempre vissuto qui", "anno_di_corso": "anno di corso",
        "crediti_conseguiti": "crediti conseguiti", "isee_universitario": "ISEE per il diritto allo studio", "ispe": "ISPE",
        "percentuale_invalidita": "percentuale di invalidità", "mesi_validita_permesso": "mesi di validità del permesso",
        "tipo_lavoro": "tipo di lavoro", "abitazione": "abitazione", "iscrizione": "iscrizione a un corso",
        "titolo_di_studio": "titolo di studio", "figlio": "figlio", "cittadinanza": "cittadinanza",
        "contratto_locazione_registrato": "contratto di affitto registrato", "mutuo_prima_casa": "mutuo per la prima casa",
        "proprieta_altra_abitazione": "proprietà di un'altra casa", "situazioni_particolari": "situazioni particolari",
        "regione_ateneo": "regione della sede del corso", "provincia_ateneo": "provincia della sede del corso",
        "comune_ateneo": "comune della sede del corso", "livello_corso": "corso frequentato", "tempo_parziale": "iscrizione a tempo parziale", "domicilio_diverso": "domicilio in un altro comune",
        "regione_domicilio": "regione del domicilio", "comune_domicilio": "comune del domicilio",
        "data_evento_figlio": "nascita o adozione dell'ultimo figlio", "regione": "regione di residenza",
        "comune": "comune di residenza", "fuori_corso_o_ripetente": "fuori corso o ripetente",
        "lavoro_terminato": "rapporto di lavoro terminato",
        "solo_veicoli_agevolati": "solo auto o moto con agevolazioni per disabilità, senza barche o aerei"}
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
    if str(req.get("campo", "")).startswith("conferma:"):
        return f"{req['verifica']} (tua risposta alla verifica)"
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
        return f"{campo} {OPERATORI[op]} {numero_italiano(req['valore'])}"
    if op == "prefisso":
        return f"{campo} che inizia con {elenco(req['valori'])}"
    return f"{campo}: {elenco(req['valori'], campo=req['campo'])}"


def voce(req, profilo=None):
    gruppo = next((k for k in ("almeno_uno_di", "tutti_di", "almeno_un_componente") if k in req), None)
    out = {"testo": descrivi(req) if not gruppo else {
        "almeno_uno_di": "È sufficiente una delle seguenti alternative:",
        "tutti_di": "Devono essere soddisfatte tutte queste condizioni:",
        "almeno_un_componente": "Una stessa persona del nucleo deve soddisfare:"}[gruppo],
        "citazione": req.get("citazione"), "fonte": req.get("fonte")}
    if gruppo:
        if gruppo == "almeno_un_componente" and isinstance((profilo or {}).get("nucleo"), list):
            out["figli"] = [{"testo": "Tu" if i == 0 else f"Persona {i + 1}", "figli": [voce(q, c) for q in req[gruppo]]} for i, c in enumerate(profilo["nucleo"])]
        else:
            out["figli"] = [voce(q, profilo if gruppo != "almeno_un_componente" else None) for q in req[gruppo]]
    elif profilo is not None and "campo" in req:
        valore = profilo.get(req["campo"])
        out["risposta"] = leggibile(req["campo"], valore) if valore is not None else "non ancora indicata"
        out["verificato"] = verifica(req, profilo)
        if req.get("anno_soglia") is not None and profilo.get("_anno_valutazione") != req["anno_soglia"]:
            out["come_verificare"] = f"Soglia verificata solo per il {req['anno_soglia']}: consultare il parametro ufficiale dell'anno della domanda."
        if valore in (None, NON_SO):
            out["come_verificare"] = AIUTI.get(req["campo"], "Consulta il requisito e i documenti richiesti dalla fonte; chiedi all'ente indicato se il dato non è chiaro.")
    return out


@lru_cache(maxsize=None)
def territori():
    """id della fonte o del documento -> (regione, livello): per dire dove vale un bando locale."""
    from pipeline.fonti.api_regioni import FONTI as FONTI_API  # bandi raccolti dalle API regionali: non in elenchi.yaml
    out = {f["id"]: (f.get("regione"), f.get("livello"), f.get("comune")) for f in FONTI_API.values()}
    out.update({f["id"]: (f.get("regione"), f.get("livello"), f.get("comune")) for f in tutte_le_fonti()})
    documenti = yaml.safe_load((ROOT / "data" / "fonti" / "documenti.yaml").read_text(encoding="utf-8"))["documenti"]
    # anche i bandi salvati a mano (Comune di Milano, Milano Abitare): senza, sarebbero trattati come nazionali (decisione 81)
    documenti += yaml.safe_load((ROOT / "data" / "fonti" / "manuali.yaml").read_text(encoding="utf-8")).get("documenti") or []
    out.update({d["id"]: (d.get("regione"), d.get("livello"), d.get("comune")) for d in documenti})
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


ALIAS_COMUNI = {"Reggio Calabria": "Reggio di Calabria"}  # nome della fonte -> nome ISTAT


def comune_ente(regola):
    """Il comune di un bando pubblicato da un Comune, o None per gli altri enti (decisione 104). Come la regione, serve
    solo a raggruppare: un contributo del Comune di Perugia che non scrive il vincolo di residenza non è "vicino" a chi
    vive a Terni."""
    if regola["id"].startswith("inps-"):
        return None
    t = territori()
    chiave = max((k for k in t if regola["id"] == k or regola["id"].startswith(k + "-")), key=len, default=None)
    if not chiave or t[chiave][1] != "comunale" or not t[chiave][2]:
        return None
    return ALIAS_COMUNI.get(t[chiave][2], t[chiave][2])


def comuni_vicini(profilo):
    """Residenza, domicilio e sede del corso: i comuni i cui bandi sono "vicini" alla persona."""
    return {profilo.get(k) for k in ("comune", "comune_domicilio", "comune_ateneo")} - {None, NON_SO}


def fuori_zona(regola, profilo):
    """Bando locale di un'altra regione, o di un altro Comune della stessa regione (decisioni 93, 104): non fa domande e
    non entra nelle verifiche finali. Non cambia l'esito."""
    regione, vicine = territorio(regola), regioni_vicine(profilo)
    if regione and vicine and regione not in vicine:
        return True
    comune, comuni = comune_ente(regola), comuni_vicini(profilo)
    return bool(comune and comuni and comune not in comuni)


# Requisiti che valgono per metà della popolazione: soddisfatti da soli non rendono un beneficio "possibile". Senza questo
# filtro bastava "sei occupato" perché la maternità della Gestione Separata comparisse a un ventiduenne senza figli: nelle
# schede INPS la condizione che definisce il gruppo (gravidanza, fondo del credito, richiamo alle armi) è spesso non
# modellabile, e l'unico requisito verificato è quello generico (decisione 78).
GENERICI = {"condizione_lavorativa", "tipo_lavoro", "ultimo_lavoro_subordinato", "eta", "cittadinanza", "residente_italia",
            "anni_residenza_italia", "anni_residenza_continuativa_italia", "mesi_validita_permesso", "soggetto_irpef_italia"}


def eta_che_decide(req):
    """L'età conta a favore quando sceglie un gruppo (almeno 60 anni, al massimo 36), non quando dice solo "maggiorenne":
    "almeno 67 anni" è il requisito che decide l'Assegno sociale (decisione 83)."""
    op, v = req["operatore"], req.get("valore")
    if op == "tra":
        return v[1] <= 36 or v[0] >= 60
    return (op in (">=", ">") and v >= 60) or (op in ("<=", "<") and v <= 36)


def a_favore(req, profilo, conta_territorio=True):
    """Soddisfatto grazie ad almeno un requisito che distingue la persona da chiunque altro. Con conta_territorio=False non
    conta nemmeno la residenza nella regione o nel comune, che vale per tutti i residenti (decisioni 96, 101)."""
    if verifica(req, profilo) is not True:
        return False
    if "campo" in req:
        if not conta_territorio and req["campo"] in TERRITORIO:
            return False
        if req["campo"] == "eta":
            return eta_che_decide(req)
        # "disoccupato", "studente", "pensionato" e "autonomo" distinguono una minoranza; "occupato" e "dipendente" no
        if req["campo"] == "condizione_lavorativa":
            return "occupato" not in req.get("valori", [])
        if req["campo"] == "tipo_lavoro":
            return "dipendente" not in req.get("valori", [])
        return req["campo"] not in GENERICI
    if "almeno_un_componente" in req:
        return True
    return any(a_favore(q, profilo, conta_territorio) for q in req.get("almeno_uno_di", []) + req.get("tutti_di", []))


def quanti_a_favore(e, profilo):
    """I requisiti già soddisfatti che distinguono la persona: con zero, un "da verificare" va in "Non sappiamo dirlo"
    invece che fra i possibili (decisioni 70, 78). Per le persone non conta la residenza nella regione o nel comune, che
    vale per tutti i residenti, e non conta niente se una condizione ancora aperta è contraddetta dai dati già noti,
    come il buono scuola per chi non ha figli in età scolare: le stesse regole delle verifiche finali (decisione 101)."""
    r = e.regola
    if r.get("_origine") == "open data" or r.get("pubblico") == "imprese":
        return sum(a_favore(q, profilo) for q in r["requisiti"])
    if any(contraddetto(m, profilo, r.get("_origine") == "riferimento") for m in e.mancanti):
        return 0
    return sum(a_favore(q, profilo, conta_territorio=False) for q in r["requisiti"])


def risultato(e, profilo=None, giorno=None):
    r = e.regola
    finestre = sorted((f for f in r.get("finestre", []) if not giorno or f["chiusura"] >= giorno), key=lambda f: f["apertura"])
    chiusura = finestre[0]["chiusura"] if finestre else r.get("chiusura")
    if e.stato in (NON_IDONEO, QUASI):
        perche = e.falliti
    elif e.stato in (MANCANO_DATI, DA_VERIFICARE):
        perche = e.mancanti
    elif e.stato == IDONEO_SALVO:
        perche = e.eccezioni
    else:
        perche = r["requisiti"]
    stato = e.stato
    avvertenze = []
    if r.get("_origine") == "estratta":
        avvertenze.append("Regola estratta automaticamente: completezza e interpretazione dei requisiti devono essere confermate.")
        if stato in (IDONEO, IDONEO_SALVO) and not r.get("_confermata"):  # confermata dalla persona: decisione 93
            stato = DA_VERIFICARE
            perche = perche + [{"non_modellabile": avvertenze[-1]}]
    if r.get("note"):
        avvertenze.append("Le note riportano ulteriori condizioni e limiti: leggerle prima di agire; non sono tutte valutate automaticamente.")
    if r.get("_origine") == "open data":
        avvertenze.append("Sono verificati soltanto i filtri del catalogo. I requisiti economici e quelli nel testo del bando restano da controllare.")
    else:
        avvertenze.append("La compatibilità con le regole non garantisce l'ammissione, la posizione in graduatoria o il pagamento.")
    return {"id": r["id"], "titolo": r["titolo"], "ente": r.get("ente"), "link": r.get("link"),
            "chiusura": chiusura, "finestre": r.get("finestre", []), "stato": stato, "origine": r.get("_origine"),
            "stato_temporale": stato_temporale(r, giorno) if giorno else "non verificato",
            "aggiornamento_regola": r.get("ultimo_controllo"),
            "revisione_umana": r.get("provenienza", {}).get("revisione_umana"),
            "perimetro": "filtri del catalogo imprese" if r.get("_origine") == "open data" else
                         "filtri estratti dal documento imprese/enti; ruoli e condizioni fuori vocabolario richiedono verifica" if r.get("pubblico") == "imprese" else
                         "requisiti rappresentati nella regola, con i limiti indicati",
            "provenienza": r.get("provenienza"),
            "versioni_precedenti": r.get("_versioni_precedenti", []),
            "identita_misura": r.get("_identita", {"misura": r["id"], "edizione": "non identificata"}), "versione_regola": hashlib.sha256(json.dumps({k: v for k, v in r.items() if not k.startswith("_")}, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "hash_file_originale": r.get("_hash_regola"),
            "note": r.get("note", []), "avvertenze": avvertenze,
            "territorio": verifica_territorio(r, profilo or {}),
            "regione": territorio(r) if r.get("_origine") != "open data" else None,
            "comune": comune_ente(r) if r.get("_origine") != "open data" else None,
            # requisiti già soddisfatti, esclusi i generici: un "da verificare" senza nessuno vuol dire "non sappiamo
            # dirlo" (decisioni 70 e 78)
            "a_favore": quanti_a_favore(e, profilo) if profilo is not None else None,
            "perche": [voce(q, profilo) for q in perche],
            # chi è idoneo, anche salvo eccezioni, vede tutti i requisiti con la loro citazione
            "requisiti": [voce(q, profilo) for q in r["requisiti"]]}


def verifica_territorio(regola, profilo):
    campi = {"regione", "comune", "regione_domicilio", "comune_domicilio", "regione_ateneo", "comune_ateneo", "provincia_ateneo"}
    requisiti = [n for q in regola["requisiti"] for n in nodi(q) if n.get("campo") in campi]
    from pipeline.motore import tutti, almeno_uno
    def proietta(q):
        if "campo" in q:
            return (verifica(q, profilo), True) if q["campo"] in campi else (None, False)
        parti = [proietta(f) for f in figli(q)]
        if not any(ha for _, ha in parti):
            return None, False
        # In OR una via non geografica non dimostra compatibilità geografica.
        if "almeno_uno_di" in q:
            return almeno_uno(v for v, _ in parti), True
        return tutti(v for v, ha in parti if ha), True
    esiti = [v for q in regola["requisiti"] for v, ha in [proietta(q)] if ha]
    return {"base": "requisiti rappresentati" if requisiti else "sola provenienza dell'ente",
            "esito": "compatibile" if esiti and tutti(esiti) is True else "da verificare",
            "campi": sorted({q["campo"] for q in requisiti}),
            "limite": "Il territorio dell'ente è un indizio di pertinenza. Non dimostra esclusione; lavoro, immobile, futura sede o corso specifico possono richiedere dati aggiuntivi."}


def gruppo_risultato(r, regioni, comuni=()):
    """Un'unica classificazione per lista, conteggi ed esportazioni.

    La provenienza dell'ente serve a ordinare; non è una prova di esclusione.
    """
    if r["stato"] == NON_IDONEO:
        return None
    compatibile = r.get("territorio", {}).get("esito") == "compatibile"
    if regioni and r["regione"] and r["regione"] not in regioni and not compatibile:
        return "lontano"
    if comuni and r.get("comune") and r["comune"] not in comuni and not compatibile:
        return "lontano"  # un altro Comune della stessa regione (decisione 104)
    if r["stato_temporale"] == "futuro":
        return "futuri"
    if r["stato_temporale"] == "non verificato":
        return "date"
    if r["stato"] == DA_VERIFICARE and r["a_favore"] == 0:
        return "ignoto"
    return None


def maiuscola(s):
    return s[:1].upper() + s[1:]


def numero_italiano(v):
    if float(v).is_integer():
        v = int(v)
    return f"{v:,}".replace(",", "_").replace(".", ",").replace("_", ".")


def leggibile(campo, valore):
    """Una risposta come la vede chi l'ha data."""
    if valore == NON_SO:
        return "non lo so"
    if isinstance(valore, list):
        return ", ".join(leggibile(campo, v) for v in valore)
    if isinstance(valore, bool):
        return "sì" if valore else "no"
    if campo == "data_evento_figlio":
        return "nessun evento di nascita o adozione dichiarato" if valore == "nessuno" else dt.date.fromisoformat(valore).strftime("%d/%m/%Y")
    if isinstance(valore, (int, float)):
        testo = numero_italiano(valore) if UNITA.get(campo) in ("euro", "euro/anno") else f"{valore:g}"
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
    for r in righe:
        if r["voce"] == "Nucleo familiare":
            r["campo"] = "nucleo"
        elif r["voce"] == "Tu" or r["voce"].startswith("Persona "):
            r["campi_modifica"] = [{"campo": k, "etichetta": nome_campo(k.split(".")[-1])} for k in domande() if k.startswith("nucleo.") and k != "nucleo.eta" and (r["voce"] != "Tu" or k not in {"nucleo.figlio", "nucleo.figlio_a_carico", "nucleo.disabile"})]
        else:
            r["campo"] = next((k for k in domande() if not k.startswith("nucleo.") and maiuscola(nome_campo(k)) == r["voce"]), None)
    return righe

NOMI.update({"isee_minorenni": "ISEE minorenni",
    "esclusione_naspi": "categoria esclusa dalla NASpI", "altri_lavori_in_essere": "altri lavori rimasti",
    "disponibilita_lavoro_naspi": "disponibilità immediata al lavoro (DID)",
    "dimissioni_indeterminato_12_mesi": "precedenti dimissioni da un indeterminato nei 12 mesi",
    "eccezione_dimissioni_precedenti": "eccezione alle precedenti dimissioni",
    "settimane_da_dimissioni": "settimane contributive dopo le dimissioni",
    "termine_naspi_particolare": "decorrenza o sospensione particolare NASpI",
    "auto_moto_non_agevolati": "auto/moto oltre soglia senza agevolazioni per disabilità", "barche_aerei": "barche o aeromobili"})
AIUTI.update({"isee_minorenni": "Usa l’ISEE minorenni relativo al bambino interessato, in corso di validità e senza omissioni/difformità. Può differire dall’ordinario con genitori non coniugati e non conviventi; un CAF può chiarire quale attestazione usare.",
    "isee": "Usa l'ISEE ordinario o corrente in corso di validità; importo in euro, non reddito. Per benefici a minori può servire ISEE minorenni: non è sempre uguale. La scheda segnala le verifiche specifiche.",
    "isee_universitario": "Usa l'ISEE per prestazioni agevolate per il diritto allo studio universitario relativo allo studente e all'anno richiesto dal bando. Non sostituirlo con quello ordinario.",
    "settimane_contributi_4_anni": "Numero di settimane di contribuzione contro la disoccupazione nei quattro anni prima della cessazione. Consulta l'estratto conto INPS e fai verificare i periodi utili a un patronato. Non usare gli anni lavorati moltiplicati automaticamente per 52.",
    "settimane_da_dimissioni": "Settimane utili tra la precedente cessazione volontaria e quella involontaria: estratto conto INPS, con verifica del patronato.",
    "comune_ateneo": "Indica la sede effettiva del corso. Questo dato non identifica l'ateneo, la sede legale o il corso ammesso dal singolo bando: tali condizioni richiedono una verifica separata.",
    "termine_naspi_particolare": "Rispondi No solo se hai verificato che nessuna delle fattispecie elencate si applica. Se non conosci le date o le indennità, scegli Non lo so; oltre 68 giorni non segue un'esclusione automatica.",
    "esclusione_naspi": "Il pubblico a termine non è escluso per il solo datore pubblico; gli operai agricoli a tempo indeterminato di determinate cooperative/consorzi sono inclusi dal 2022. Assegno ordinario di invalidità e pensione di vecchiaia/anticipata sono situazioni diverse. In dubbio, patronato/INPS."})


CAMPI_ISEE = {"isee", "isee_universitario", "isee_minorenni", "ispe"}
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
        regole_imprese = ramo_imprese(giorno)[0]
        imprese = sum(stato_temporale(r, giorno) in ("aperto", "permanente") for r in regole_imprese)
    except RuntimeError:  # senza `make dati` il ramo imprese non c'è
        imprese = None
    schede = sorted(f for f in (ROOT / "data" / "raw").glob("inps_schede_*.json") if not f.name.endswith(".meta.json"))
    classificati = ROOT / "data" / "pubblico" / "classificazione.yaml"
    return {
        "giorno": giorno,
        "persone": len(persone),
        "persone_aperte": sum(stato_temporale(r, giorno) in ("aperto", "permanente") for r in persone),
        "persone_date_non_verificate": sum(stato_temporale(r, giorno) == "non verificato" for r in persone),
        "persone_riferimento": sum(r["_origine"] == "riferimento" for r in persone),
        "revisioni_umane_documentate": sum(bool(r.get("provenienza", {}).get("revisione_umana")) for r in persone),
        "imprese_aperte": imprese,
        "imprese_catalogo": len(regole_imprese) if imprese is not None else None,
        "imprese_date_non_verificate": sum(stato_temporale(r, giorno) == "non verificato" for r in regole_imprese) if imprese is not None else None,
        "imprese_future": sum(stato_temporale(r, giorno) == "futuro" for r in regole_imprese) if imprese is not None else None,
        "schede_inps": len(json.loads(schede[-1].read_text(encoding="utf-8"))) if schede else None,
        "documenti": len(yaml.safe_load(classificati.read_text(encoding="utf-8"))) if classificati.exists() else None,
        "fonti": len(tutte_le_fonti()),
        "export_imprese": next((f.stem.removeprefix("incentivi_export_") for f in sorted((ROOT / "data" / "raw").glob("incentivi_export_*.json"), reverse=True) if not f.name.endswith(".meta.json")), None),
    }


def passo(ramo, profilo, giorno, estratte=False, modifica=None):
    """Un passo della demo: esiti con il profilo di adesso e prossima domanda (None quando non serve altro)."""
    if ramo == "imprese":
        from web.validazione import valida_impresa
        profilo = valida_impresa(profilo, opzioni_imprese(giorno), sedi_istat())
        regole, _ = ramo_imprese(giorno)
        esiti = valuta_tutte(regole, profilo)
        domanda = domanda_imprese(profilo, giorno)
    else:
        completo = completa(profilo, giorno)
        completo.update({"conferma:" + k: v for k, v in (profilo.get("conferme") or {}).items() if v in (True, False)})
        esiti = [valuta(r, completo) for r in applica_conferme(regole_persone(estratte), profilo)
                 if stato_temporale(r, giorno) != "chiuso"]
        campo, usi = prossima_persone([e for e in esiti if stato_temporale(e.regola, giorno) != "futuro"], completo)
        domanda = domanda_persone(campo, usi, completo) if campo else None
    if modifica and ramo == "persone":
        if modifica not in domande() and modifica not in {"residenza", "domicilio"}:
            raise ValueError("modifica: campo sconosciuto")
        domanda = domanda_persone(modifica, 0, completo)
        if modifica.startswith("nucleo."):
            campo = modifica.split(".")[1]
            domanda["componenti"] = [{"indice": i, "eta": c.get("eta"), "valore": c.get(campo)} for i, c in enumerate(completo.get("nucleo") or []) if (i != 0 or campo not in {"disabile", "figlio", "figlio_a_carico"}) and (campo != "figlio_a_carico" or c.get("figlio") is True)]
    esiti.sort(key=lambda e: (ORDINE_ESITI.index(e.stato), e.regola["titolo"]))
    risultati = [risultato(e, completo if ramo == "persone" else profilo, giorno) for e in esiti]
    conteggi = {s: sum(r["stato"] == s for r in risultati) for s in ORDINE_ESITI}
    out = {"riepilogo": riepilogo(profilo) if ramo == "persone" else [], "domanda": domanda, "conteggi": conteggi, "risultati": risultati, "giorno": giorno, "dipendenze": dipendenze()}
    if ramo == "persone":
        out["verifiche"] = verifiche(esiti, completo)  # la pagina le mostra quando le domande sono finite
        # Le regioni "vicine" alla persona: residenza, domicilio e sede del corso (anche ricavata dal comune; decisione 73)
        vicine = [completo.get(k) for k in ("regione", "regione_domicilio", "regione_ateneo")]
        out["regioni_vicine"] = list(dict.fromkeys(r for r in vicine if r in REGIONI))
        out["comuni_istat"] = comuni_del_profilo(completo)
        # Archivio: nessuna previsione su nuove edizioni.
        un_anno_fa = (dt.date.fromisoformat(giorno) - dt.timedelta(days=365)).isoformat()
        chiusi = [valuta(r, completo) for r in regole_persone(estratte)
                  if r.get("chiusura") and un_anno_fa <= r["chiusura"] < giorno]
        out["chiusi_di_recente"] = [risultato(e, completo, giorno) for e in sorted(chiusi, key=lambda e: e.regola["chiusura"], reverse=True)
                                    if e.stato != NON_IDONEO]
        for r in out["chiusi_di_recente"]:  # solo la zona: altre regioni o altri Comuni restano fuori (decisione 104)
            r["gruppo"] = "lontano" if gruppo_risultato(r, out["regioni_vicine"], comuni_vicini(completo)) == "lontano" else None
    else:
        out["regioni_vicine"] = [profilo["regione"]] if profilo.get("regione") in REGIONI else []
    for r in risultati:
        r["gruppo"] = gruppo_risultato(r, out.get("regioni_vicine", []), comuni_vicini(completo) if ramo == "persone" else ())
        # Nessun invito al calendario con fatti ignoti, area da controllare o date incerte.
        r["calendario_ammesso"] = (r["gruppo"] is None and r["stato"] in (IDONEO, IDONEO_SALVO, DA_VERIFICARE)
                                   and r["stato_temporale"] == "aperto" and r["a_favore"] > 0
                                   and (not r["regione"] or r["territorio"]["esito"] == "compatibile"
                                        or r["regione"] in out.get("regioni_vicine", [])))
        r["prossimo_passo"] = prossimo_passo(r)
    if ramo == "persone":
        out["catalogo_esclusioni"] = yaml.safe_load((ROOT / "data" / "revisioni_demo.yaml").read_text(encoding="utf-8"))["escluse"]
    if ramo == "persone" and completo.get("isee") == NON_SO:
        # chi non sa il proprio ISEE: quanti benefici restano in sospeso per quello (docs/contesto.md, idea 1)
        n = sum(e.stato == MANCANO_DATI and dipende_da_isee(e.regola) for e in esiti)
        if n:
            out["isee"] = {"decide": n, "link": LINK_ISEE}
    return out

# Definizioni per le domande mirate; non sostituiscono le attestazioni della singola misura.
UNITA['reddito_autonomo_presunto_naspi'] = 'euro/anno'
AIUTI.update({
    'contributi_agricoli_presenti': 'Usa l’estratto conto contributivo INPS per i quattro anni prima della cessazione; non basta il lavoro attuale. In caso di dubbi chiedi a INPS o patronato.',
    'prevalenza_non_agricola_4_anni': 'Non confrontare importi di reddito: occorre la contribuzione utile alla NASpI. Fai verificare conversioni delle giornate agricole, settimane e periodi neutralizzabili a INPS/patronato.',
    'prevalenza_non_agricola_12_mesi': 'Periodo: i 12 mesi prima della cessazione. È il controllo alternativo quando nel quadriennio prevale l’agricolo; non dichiarare No senza l’estratto verificato.',
    'reddito_autonomo_presunto_naspi': 'Reddito annuo previsto dell’attività autonoma rimasta per l’anno in corso, anche zero: non ISEE, fatturato o netto mensile. Usa una previsione fiscale con il consulente; il termine di comunicazione a INPS e la riduzione della prestazione restano da verificare.',
    'lavori_rimasti_naspi': 'Solo autonomo esclude collaborazioni parasubordinate e rapporti dipendenti. Se convivono più tipi, scegli altri o misti; per il part-time occorre verificare il limite reddituale dell’anno e la comunicazione entro un mese.',
    'ispe': 'ISPE = ISP / parametro della scala di equivalenza, in euro. Usa l’attestazione prevista dal bando per l’anno della domanda. Per ER.GO assegni formativi non assumere il tipo universitario senza leggere il bando; chiedi a ER.GO/CAF se il dato manca.',
    'iscrizione_postlaurea_ergo': 'Consulta certificato di iscrizione e programma, con durata e titolo rilasciato. La sede all’estero e il titolo precedente conseguito in Emilia-Romagna richiedono verifiche separate con ER.GO.',
    'nucleo.reddito_annuo': 'Importo annuo in euro del singolo componente, non la somma familiare né lo stipendio netto mensile. Il periodo e le voci incluse dipendono dalla misura: consulta dichiarazione/CU e la fonte prima di usare lo stesso importo per più benefici.',
    'canone_annuo': 'Euro per 12 mesi di locazione, escluse spese condominiali e utenze; consulta contratto registrato e ricevute. Verifica nel bando l’anno e le mensilità ammesse.',
})
NOMI.update({
    'contributi_agricoli_presenti': 'presenza di contribuzione agricola nel quadriennio',
    'prevalenza_non_agricola_4_anni': 'prevalenza non agricola nei quattro anni prima della cessazione',
    'prevalenza_non_agricola_12_mesi': 'prevalenza non agricola nei 12 mesi prima della cessazione',
    'reddito_autonomo_presunto_naspi': 'reddito annuo presunto dell’attività autonoma rimasta',
    'lavori_rimasti_naspi': 'tipo di lavori rimasti per NASpI',
    'genitore_tutore_buoni_toscana': 'genitore o tutore per Buoni scuola Toscana',
    'bambino_residente_toscana_buoni': 'residenza del bambino in Toscana',
    'iscrizione_effettiva_buoni_toscana': 'iscrizione effettiva con posto per Buoni scuola Toscana',
    'retta_buoni_toscana': 'retta di frequenza per Buoni scuola Toscana',
    'iscrizione_postlaurea_ergo': 'iscrizione al corso postlaurea per assegni formativi ER.GO',
})
ETICHETTE['lavori_rimasti_naspi'] = {'solo_autonomo': 'Solo attività autonoma', 'solo_part_time': 'Solo rapporti dipendenti part-time', 'altri_o_misti': 'Altri tipi o più tipi di lavoro'}

NOMI["iscro_cococo_senza_iva"] = "caso ISCRO co.co.co senza partita IVA"

AIUTI['eccezione_dimissioni_precedenti'] = 'Consulta lettera di dimissioni, accordo/verbale di conciliazione e provvedimento di trasferimento con INPS/patronato. La circolare 98/2025 esclude dal nuovo requisito anche le fattispecie di trasferimento protette: non basta chiamare genericamente consensuale l’accordo.'
AIUTI['settimane_da_dimissioni'] = 'Conta dall’ultimo evento volontario rilevante fino alla cessazione involontaria, non dall’inizio del nuovo contratto. Le settimane devono essere utili e rispettare il minimale; eventuali giornate agricole richiedono conversione (6 giornate = una settimana) e la verifica distinta della prevalenza.'

NOMI.update({
    'reddito_autonomo_precedente_iscro': 'reddito da lavoro autonomo dell’anno precedente per ISCRO',
    'prima_liquidazione_inabilita': 'prima liquidazione della pensione di inabilità',
    'reddito_presunto_corrente_inabilita': 'reddito personale IRPEF presunto dell’anno corrente per inabilità',
    'reddito_pensioni_corrente_inabilita': 'redditi da pensione dell’anno corrente per inabilità',
    'altri_redditi_precedente_inabilita': 'altri redditi personali IRPEF dell’anno precedente per inabilità',
    'reddito_rilevante_successiva_inabilita': 'pensioni correnti più altri redditi personali dell’anno precedente',
    'reddito_locazione_2025': 'reddito complessivo 2025 inclusa cedolare secca per detrazioni affitto',
    'eta_giovani_locazione_2025': 'età fra 20 e 30 anni nel periodo di locazione 2025',
    'canone_2025_genova': 'canone annuo 2025 per Fondo affitti Genova 2026',
    'patrimonio_imu_genova': 'valore immobiliare ai fini IMU per Fondo affitti Genova 2026',
    'isee_2026_genova': 'ISEE richiesto dal Fondo affitti Genova 2026, redditi 2024',
})
for _campo in ('reddito_autonomo_precedente_iscro', 'reddito_presunto_corrente_inabilita',
               'reddito_pensioni_corrente_inabilita', 'altri_redditi_precedente_inabilita',
               'reddito_rilevante_successiva_inabilita', 'reddito_locazione_2025',
               'canone_2025_genova', 'patrimonio_imu_genova', 'isee_2026_genova'):
    UNITA[_campo] = 'euro'
AIUTI.update({
    'reddito_autonomo_precedente_iscro': 'Usa il reddito prodotto nell’esercizio dell’attività autonoma nel {precedente}, rilevante per ISCRO {anno}, dalla dichiarazione fiscale: non il fatturato o il reddito complessivo IRPEF comprensivo di altre fonti. Con il consulente/INPS verifica le voci ammesse; se non lo conosci scegli Non lo so. La soglia 12.749,18 è verificata per il 2026.',
    'prima_liquidazione_inabilita': 'Per prima liquidazione INPS usa i redditi dell’anno in corso presunti; per quelle successive combina pensioni dell’anno corrente e altre tipologie di reddito dell’anno precedente. Se non sai quale caso applicare, scegli Non lo so e verifica con INPS/patronato.',
    'reddito_presunto_corrente_inabilita': 'Importo personale annuo soggetto a IRPEF previsto nel {anno}; non il reddito del nucleo, l’ISEE o quello del {precedente}. Consulta previsione reddituale, CU e dichiarazioni con INPS/patronato. Se non puoi stimarlo, scegli Non lo so.',
    'reddito_pensioni_corrente_inabilita': 'Solo redditi personali da pensione del {anno} rilevanti per la verifica INPS. Gli altri redditi sono chiesti separatamente per il {precedente}; non ripetere il totale IRPEF in entrambi i campi. Zero deve essere una risposta esplicita.',
    'altri_redditi_precedente_inabilita': 'Redditi personali IRPEF diversi dalle pensioni percepiti nel {precedente}, secondo la scheda INPS. Non il reddito del coniuge, non ISEE. Consulta CU/dichiarazione con INPS/patronato; escludi le pensioni già indicate nell’altra domanda.',
    'reddito_locazione_2025': 'Per la dichiarazione 730/2026 il periodo d’imposta è il 2025. Consulta il prospetto fiscale: l’Agenzia richiede il reddito complessivo aumentato dei redditi dei fabbricati in cedolare secca. Non sostituire con reddito corrente 2026, fatturato o ISEE; chiedi al CAF se il valore non è chiaro.',
    'eta_giovani_locazione_2025': 'Si valuta il periodo fiscale delle spese, non l’età alla data odierna. Giorni di detrazione, primi quattro anni di contratto e compimento dei 31 anni vanno verificati con il CAF; questo confronto non calcola l’importo.',
    'canone_2025_genova': 'Consulta contratto e documenti del 2025: non usare automaticamente l’affitto pagato oggi. Il bando tratta separatamente canone annuo e pagamenti effettivi documentati con ricevute/bonifici.',
    'patrimonio_imu_genova': 'Non è il patrimonio immobiliare ISEE al netto della casa di abitazione. Porta visure e calcoli IMU al Comune/CAF per applicare il punto f) del bando a tutti i componenti residenti; se manca il calcolo, scegli Non lo so.',
    'isee_2026_genova': 'Leggi l’attestazione e i requisiti del bando FSA 2026: anno dei redditi 2024 e presentazione entro il termine previsto. Non copiare un ISEE di altra annualità soltanto perché il valore è disponibile.',
    'nucleo.reddito_annuo': 'Per AUU indica il reddito complessivo IRPEF annuo del figlio nell’anno di riferimento {anno}, non quello di due anni prima usato nell’ISEE. Comprende le voci imponibili indicate da INPS (anche locazione), al lordo degli oneri deducibili. Per figli maggiorenni attratti in un altro nucleo e casi particolari verifica i periodi con INPS/CAF.',
})
NOMI.update({'isee_nidi_gratis_2026':'ISEE previsto dal Comune per Nidi Gratis Plus 2026/27',
             'isee_libri_pescara_2026':'ISEE pertinente per Libri Pescara 2026/27'})
UNITA.update({'isee_nidi_gratis_2026':'euro','isee_libri_pescara_2026':'euro'})
AIUTI.update({
 'isee_nidi_gratis_2026':'Il bando richiede ISEE minorenni o ISEE per specifiche prestazioni familiari e inclusione secondo la scelta del Comune, con le ulteriori casistiche nazionali. Controlla avviso del Comune e attestazione protocollata valida: non assumere che coincidano con l’ISEE ordinario già indicato. Se il tipo richiesto non è noto, scegli Non lo so e chiedi al Comune/CAF.',
 'isee_libri_pescara_2026':'L’avviso richiede ISEE ordinario o ISEE minorenni in caso di genitori non coniugati/non conviventi, valido alla presentazione della domanda. Usa l’attestazione pertinente al figlio: CAF/INPS possono verificarne il tipo. Non ricaviamo questa scelta dalla sola presenza dei genitori nel nucleo.',
})
NOMI['isee_2026_palermo']='ISEE per contributo affitto Palermo 2026, redditi 2024'
UNITA['isee_2026_palermo']='euro'
AIUTI['isee_2026_palermo']='Usa l’attestazione pertinente all’avviso 2026 e ai redditi 2024, da verificare con Comune/CAF; non un ISEE di altra annualità. La pagina non basta a chiarire ogni requisito dell’avviso allegato.'
NOMI['isee_prestazioni_familiari_2026']='ISEE 2026 per specifiche prestazioni familiari e inclusione'
UNITA['isee_prestazioni_familiari_2026']='euro'
AIUTI['isee_prestazioni_familiari_2026']='Dal 2026 ADI, SFL e Bonus nuovi nati usano questo indicatore specifico (messaggio INPS 102/2026), che può essere diverso e più favorevole dell’ISEE ordinario. Leggi il valore indicato nel Portale unico ISEE per specifiche prestazioni o fallo verificare a INPS/CAF. Non calcolarlo sottraendo importi e non copiare automaticamente l’ISEE ordinario. Se manca, scegli Non lo so.'
CAMPI_ISEE.update({'isee_prestazioni_familiari_2026','isee_nidi_gratis_2026','isee_libri_pescara_2026','isee_2026_genova','isee_2026_palermo'})

NOMI.update({'isee_voucher_perugia_2026': 'ISEE dell’attestazione richiesta per voucher sportivi Perugia 2026', 'isee_sociosanitario_badanti_2026': 'ISEE sociosanitario ordinario per bonus badanti FILSE 2026', 'isee_babysitter_filse_2026': 'ISEE ordinario o minorenni pertinente per bonus baby sitter FILSE 2026', 'isee_gravissima_filse_2026': 'ISEE pertinente alla persona assistita per gravissima disabilità FILSE 2026'})
UNITA.update({'isee_voucher_perugia_2026': 'euro', 'isee_sociosanitario_badanti_2026': 'euro', 'isee_babysitter_filse_2026': 'euro', 'isee_gravissima_filse_2026': 'euro'})
AIUTI.update({'isee_voucher_perugia_2026': 'Il modulo richiede ISEE minorenni, mentre i beneficiari hanno 14–35 anni. Verifica con Comune/CAF quale attestazione si applica al singolo richiedente; se non è chiaro scegli Non lo so. Non ricaviamo il tipo dalla sola età.', 'isee_sociosanitario_badanti_2026': 'Importo dell’ISEE sociosanitario ordinario pertinente alla persona non autosufficiente assistita. Non ISEE ordinario del nucleo. Verifica attestazione valida alla domanda con FILSE/CAF.', 'isee_babysitter_filse_2026': 'Importo dell’ISEE ordinario del nucleo o minorenni pertinente al figlio secondo avviso 2026. Verifica il tipo con FILSE/CAF; non basta conoscere un ISEE generico.', 'isee_gravissima_filse_2026': 'Importo dell’attestazione pertinente alla persona assistita secondo il Bando 2026 FILSE, distinto dai due bonus badanti/baby sitter. La pagina riassuntiva non chiarisce ogni definizione: conferma tipo e nucleo con FILSE/CAF o scegli Non lo so.'})
CAMPI_ISEE.update({'isee_voucher_perugia_2026', 'isee_babysitter_filse_2026', 'isee_gravissima_filse_2026', 'isee_sociosanitario_badanti_2026'})
