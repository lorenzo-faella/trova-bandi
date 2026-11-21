"""Validazione dei fatti forniti dall'utente, prima delle inferenze del questionario.

La validazione non aggiunge requisiti ai bandi: rifiuta dati malformati e
contraddizioni, senza convertire un dato sconosciuto in una risposta negativa.
"""
import datetime as dt
import math
import unicodedata

from pipeline.motore import NON_SO
from pipeline.regole import SCHEMA


def noto(v):
    return v is not None and v != NON_SO


def chiave_comune(s):
    return unicodedata.normalize("NFKD", s.strip().casefold()).encode("ascii", "ignore").decode()


def comune_riconosciuto(valore, sedi, regione=None):
    corrispondenze = [c for c in sedi if chiave_comune(c) == chiave_comune(valore)
                     and (not noto(regione) or any(s[1] == regione for s in sedi[c]))]
    if len(corrispondenze) != 1 or (not noto(regione) and len(sedi.get(corrispondenze[0], [])) != 1):
        raise ValueError("comune: scegli un comune dell'elenco nella regione indicata, oppure Non lo so")
    return corrispondenze[0]


def valida(profilo, domande, sedi, regioni, giorno):
    p = {k: v for k, v in profilo.items() if v is not None}
    nucleo = p.get("nucleo")
    if noto(nucleo) and (not isinstance(nucleo, list) or not 1 <= len(nucleo) <= 100
                        or not all(isinstance(c, dict) for c in nucleo)):
        raise ValueError("nucleo: indica da 1 a 100 persone, oppure Non lo so")
    numeri = set(SCHEMA["$defs"]["numero"]["properties"]["campo"]["enum"])
    booleani = set(SCHEMA["$defs"]["booleano"]["properties"]["campo"]["enum"]) | {"sempre_in_italia"}
    interi = {"eta", "numero_figli", "numero_componenti", "anno_di_corso", "mesi_validita_permesso",
              "giorni_da_cessazione_lavoro", "giorni_da_evento_figlio", "mesi_da_evento_figlio", "settimane_da_dimissioni"}
    elenchi = {k.split(".")[-1]: d for k, d in domande.items() if d.get("valori")}
    ammessi = numeri | booleani | set(elenchi) | {"nucleo", "data_evento_figlio", "comune", "comune_domicilio",
               "comune_ateneo", "regione", "regione_domicilio", "regione_ateneo", "provincia_ateneo"}
    ammessi.add("conferme")  # risposte alle verifiche finali sugli aiuti possibili (decisione 93)
    ammessi.discard("reddito_rilevante_successiva_inabilita")  # somma calcolata, non input dell'API
    componenti = [dict(c) for c in nucleo] if isinstance(nucleo, list) else []
    if componenti:
        p["nucleo"] = componenti
    campi_componente = {k.split(".")[1] for k in domande if k.startswith("nucleo.")}
    for dati, campi in [(p, ammessi), *((c, campi_componente) for c in componenti)]:
        for campo, v in dati.items():
            if campo not in campi:
                raise ValueError(f"{campo}: campo non previsto")
            if not noto(v) or campo == "nucleo":
                continue
            if campo == "conferme":
                if not isinstance(v, dict) or not all(isinstance(k, str) and (x is True or x is False or x == "non lo so")
                                                       for k, x in v.items()):
                    raise ValueError("conferme: servono risposte sì, no o non lo so")
                continue
            if campo in booleani and type(v) is not bool:
                raise ValueError(f"{campo}: serve sì o no")
            if campo in numeri:
                if type(v) not in (int, float) or not math.isfinite(v) or v < 0:
                    raise ValueError(f"{campo}: serve un numero finito non negativo")
                if campo in interi and v != int(v):
                    raise ValueError(f"{campo}: serve un numero intero")
                if (campo == "eta" and v > 120) or (campo == "percentuale_invalidita" and v > 100):
                    raise ValueError(f"{campo}: valore oltre il limite consentito")
                if campo == "anno_di_corso" and v < 1:
                    raise ValueError("anno_di_corso: il primo anno è 1")
            if campo in elenchi:
                valori = v if isinstance(v, list) else [v]  # compatibilità con i profili precedenti
                d = elenchi[campo]
                if not valori or any(type(x) is not str or x not in d["valori"] for x in valori):
                    raise ValueError(f"{campo}: scegli una risposta tra quelle proposte")
                if d["tipo"] != "elenco multiplo" and isinstance(v, list):
                    raise ValueError(f"{campo}: scegli una sola risposta")
                if len(set(valori)) != len(valori) or ("nessuna" in valori and len(valori) > 1):
                    raise ValueError(f"{campo}: risposte incompatibili o ripetute")
    condizioni = p.get("condizione_lavorativa")
    if noto(condizioni):
        selezionate = set(condizioni if isinstance(condizioni, list) else [condizioni])
        if len(selezionate & {"occupato", "disoccupato", "inattivo"}) > 1:
            raise ValueError("condizione_lavorativa: scegli una sola tra lavoro, senza lavoro e non cerco lavoro")
    for campo, regione in (("comune", "regione"), ("comune_domicilio", "regione_domicilio"),
                           ("comune_ateneo", "regione_ateneo")):
        if noto(p.get(campo)):
            if not isinstance(p[campo], str):
                raise ValueError(f"{campo}: serve il nome di un comune")
            p[campo] = comune_riconosciuto(p[campo], sedi, p.get(regione))
    for campo in ("regione", "regione_domicilio", "regione_ateneo"):
        if noto(p.get(campo)) and p[campo] not in regioni:
            raise ValueError(f"{campo}: regione sconosciuta")
    for campo in ("comune_ateneo",):
        if noto(p.get(campo)):
            scelte = [s for s in sedi[p[campo]] if not noto(p.get("regione_ateneo")) or s[1] == p["regione_ateneo"]]
            if noto(p.get("provincia_ateneo")) and not any(p["provincia_ateneo"] == s[0] for s in scelte):
                raise ValueError("provincia_ateneo: non corrisponde al comune del corso")
    data = p.get("data_evento_figlio")
    if noto(data) and data != "nessuno":
        if not isinstance(data, str) or dt.date.fromisoformat(data) > dt.date.fromisoformat(giorno):
            raise ValueError("data_evento_figlio: indica una data valida non futura")
    eta = componenti[0].get("eta") if componenti else p.get("eta")
    if componenti:
        for campo in ("eta", "disabile"):
            a, b = p.get(campo), componenti[0].get(campo)
            if noto(a) and noto(b) and a != b:
                raise ValueError(f"{campo}: le risposte del richiedente e di Tu devono coincidere")
        if componenti[0].get("figlio") is True:
            raise ValueError("nucleo: chi risponde non può essere figlio di sé stesso")
    anni = ["anni_residenza_italia", "anni_residenza_continuativa_italia", "anni_residenza_regione"]
    for campo in anni:
        if noto(eta) and noto(p.get(campo)) and p[campo] > eta:
            raise ValueError(f"{campo}: non può superare l'età")
    totale, continuo = p.get(anni[0]), p.get(anni[1])
    if noto(totale) and noto(continuo) and continuo > totale:
        raise ValueError("anni_residenza_continuativa_italia: non possono superare gli anni totali")
    if p.get("disabile") is False and noto(p.get("percentuale_invalidita")) and p["percentuale_invalidita"] > 0:
        raise ValueError("disabile: percentuale di invalidità e risposta sulla disabilità non coincidono")
    if componenti:
        if noto(p.get("numero_componenti")) and p["numero_componenti"] != len(componenti):
            raise ValueError("numero_componenti: non coincide con il nucleo indicato")
        figli = [c.get("figlio") for c in componenti[1:]]
        if all(type(v) is bool for v in figli) and noto(p.get("numero_figli")) and p["numero_figli"] != sum(figli):
            raise ValueError("numero_figli: non coincide con i figli indicati nel nucleo")
    if p.get("lavoro_terminato") is False and (p.get("ultimo_lavoro_subordinato") is True or any(noto(p.get(k)) for k in ("causa_fine_lavoro", "giorni_da_cessazione_lavoro"))):
        raise ValueError("lavoro_terminato: i dettagli della cessazione contraddicono la risposta No")
    condizioni = condizioni if isinstance(condizioni, list) else [condizioni]
    if any(c in {"disoccupato", "inattivo"} for c in condizioni):
        if p.get("lavora_in_italia") is True or noto(p.get("tipo_lavoro")):
            raise ValueError("condizione_lavorativa: il lavoro attuale contraddice l'assenza di lavoro")
    if p.get("solo_veicoli_agevolati") is True and any(p.get(k) is True for k in ("auto_moto_non_agevolati", "barche_aerei")):
        raise ValueError("solo_veicoli_agevolati: hai indicato anche beni non agevolati o barche/aerei")
    for c in componenti:
        if c.get("figlio") is False and c.get("figlio_a_carico") is True:
            raise ValueError("figlio_a_carico: la stessa persona è stata indicata come non figlio")
    return p


def valida_impresa(profilo, opzioni, sedi):
    """Perimetro API dei filtri imprese: tipi, valori e geografia prima del motore."""
    import re
    p = {k: v for k, v in profilo.items() if v is not None}
    for campo, v in p.items():
        if campo not in {*opzioni, 'comune', 'ateco_2025'}:
            raise ValueError(f'{campo}: campo non previsto per le imprese')
        if not noto(v):
            continue
        if campo in opzioni:
            multiplo = campo in {'tipologia', 'settore', 'ambito'}
            valori = v if isinstance(v, list) else [v]
            if not multiplo and isinstance(v, list):
                raise ValueError(f'{campo}: scegli una sola risposta')
            if not valori and campo != 'ambito':
                raise ValueError(f'{campo}: scegli una risposta oppure Non lo so')
            if any(type(x) is not str or x not in opzioni[campo] for x in valori):
                raise ValueError(f'{campo}: valore non previsto')
            if len(set(valori)) != len(valori):
                raise ValueError(f'{campo}: risposte ripetute')
        elif campo == 'ateco_2025' and (type(v) is not str or not re.fullmatch(r'\d{2}(?:\.?\d){0,4}', v)):
            raise ValueError('ateco_2025: indica da 2 a 6 cifre del codice, oppure Non lo so')
    if noto(p.get('comune')):
        if type(p['comune']) is not str:
            raise ValueError('comune: serve il nome di un comune')
        p['comune'] = comune_riconosciuto(p['comune'], sedi, p.get('regione'))
    return p
