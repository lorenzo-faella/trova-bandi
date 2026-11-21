"""Regressioni dei problemi riprodotti dopo cc097ba; data di confronto fissa."""
import copy
import gzip
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pipeline.motore import IDONEO, NON_IDONEO, MANCANO_DATI, DA_VERIFICARE, NON_SO, valuta, stato_temporale, aperta
from pipeline.regole import carica, DIR_PERSONE
from web import domande as d
from web.server import app

G = '2026-11-21'
BASE = dict(lavoro_terminato=True, ultimo_lavoro_subordinato=True, esclusione_naspi=False,
            disponibilita_lavoro_naspi=True, altri_lavori_in_essere=False,
            causa_fine_lavoro='licenziamento', settimane_contributi_4_anni=20,
            giorni_da_cessazione_lavoro=20, dimissioni_indeterminato_12_mesi=False,
            termine_naspi_particolare=False, contributi_agricoli_presenti=False)

@pytest.mark.parametrize('agricoli,quattro,dodici,atteso',[
    (False, NON_SO, NON_SO, IDONEO), (True, True, NON_SO, IDONEO),
    (True, False, True, IDONEO), (True, False, False, NON_IDONEO),
    (True, False, NON_SO, MANCANO_DATI), (NON_SO, NON_SO, NON_SO, MANCANO_DATI)])
def test_prevalenza_agricola_senza_presunzioni(agricoli,quattro,dodici,atteso):
    r = next(r for r in carica(DIR_PERSONE) if r['id']=='inps-naspi')
    p = dict(BASE, contributi_agricoli_presenti=agricoli, prevalenza_non_agricola_4_anni=quattro, prevalenza_non_agricola_12_mesi=dodici)
    assert valuta(r,p).stato == atteso

@pytest.mark.parametrize('reddito,atteso',[(0,DA_VERIFICARE),(5500,DA_VERIFICARE),(5500.01,NON_IDONEO),(NON_SO,MANCANO_DATI)])
def test_reddito_autonomo_naspi_e_comunicazione_anche_zero(reddito,atteso):
    r = next(r for r in carica(DIR_PERSONE) if r['id']=='inps-naspi')
    p=dict(BASE,altri_lavori_in_essere=True,lavori_rimasti_naspi='solo_autonomo',reddito_autonomo_presunto_naspi=reddito)
    assert valuta(r,p).stato == atteso
    assert 'reddito zero' in d.prossimo_passo({'id':'inps-naspi'})

@pytest.mark.parametrize('campo',['genitore_tutore_buoni_toscana','bambino_residente_toscana_buoni','iscrizione_effettiva_buoni_toscana','retta_buoni_toscana'])
def test_buoni_ruolo_non_derivato_da_nucleo_e_condizioni_esplicite(campo):
    r=next(r for r in d.regole_persone(True) if r['id']=='toscana-contributi-per-la-frequenza-delle-scuole-9bae68')
    p={c:True for c in ['genitore_tutore_buoni_toscana','bambino_residente_toscana_buoni','iscrizione_effettiva_buoni_toscana','retta_buoni_toscana']}
    p.update(isee_minorenni=9000,nucleo=[{'eta':40,'figlio':False},{'eta':2,'figlio':False}])
    assert valuta(r,p).stato==DA_VERIFICARE  # anche tutore, senza esclusione da età o parentela
    assert valuta(r,dict(p,**{campo:False})).stato==NON_IDONEO
    assert valuta(r,dict(p,**{campo:NON_SO})).stato==MANCANO_DATI

@pytest.mark.parametrize('regione',['Lombardia','Puglia'])
def test_comuni_omonimi_sede_corso_istat(regione):
    p=d.completa({'comune_ateneo':'Castro','regione_ateneo':regione},G)
    assert d.comuni_del_profilo(p)['comune_ateneo']['codice']==d.codici_comuni()[('Castro',regione)]
    assert p['regione_ateneo']==regione and p['provincia_ateneo']
    q=d.domanda_persone('comune_ateneo',1,p)
    assert q['tipo']=='pagina' and q['valori_attuali']['regione_ateneo']==regione

def test_omonimo_non_inventato_e_sede_non_ateneo():
    with pytest.raises(ValueError): d.completa({'comune_ateneo':'Castro'},G)
    r=next(r for r in d.regole_persone(True) if r['id'].startswith('erdis-marche-alloggi-'))
    p={'regione_ateneo':'Lombardia','iscrizione':'universita','livello_corso':'laurea_triennale'}
    assert valuta(r,p).stato==DA_VERIFICARE  # sede distaccata non prova ateneo escluso
    assert d.da_porre('ispe',{'iscrizione':'nessuna'})=='ispe'
    assert d.da_porre('iscrizione_postlaurea_ergo',{'condizione_lavorativa':['pensionato']})=='iscrizione_postlaurea_ergo'

def test_requisiti_territoriali_rispettano_alternative_e_congiunzioni():
    a={'campo':'regione','operatore':'in','valori':['Lombardia']}
    b={'campo':'comune','operatore':'in','valori':['Bergamo']}
    p={'regione':'Lombardia','comune':'Milano'}
    assert d.verifica_territorio({'requisiti':[{'tutti_di':[a,b]}]},p)['esito']=='da verificare'
    assert d.verifica_territorio({'requisiti':[{'almeno_uno_di':[a,b]}]},p)['esito']=='compatibile'

def test_regione_ente_non_esclude_impresa_e_classificazione_api(monkeypatch):
    monkeypatch.setenv('TROVA_BANDI_GIORNO',G)
    p={'tipologia':['Impresa'],'dimensione':'Microimpresa','regione':'Sicilia','comune':'Palermo'}
    out=TestClient(app).post('/api/passo',json={'ramo':'imprese','profilo':p}).json()
    r=next(r for r in out['risultati'] if r['id']=='abruzzo-coesione-dote-lavoro-giovani-c88db0')
    assert r['stato']!=NON_IDONEO and r['gruppo']=='lontano'
    assert r['territorio']['base']=="sola provenienza dell'ente" and not r['calendario_ammesso']
    assert out['conteggi'][r['stato']]==sum(x['stato']==r['stato'] for x in out['risultati'])
    assert out['regioni_vicine']==['Sicilia']

def test_alternative_imprese_generano_domande_e_opzioni(monkeypatch):
    from pipeline.questionario import Questionario
    r={'id':'esempio','titolo':'Esempio','apertura':None,'chiusura':None,'requisiti':[{'almeno_uno_di':[
       {'campo':'settore','operatore':'interseca','valori':['Commercio']},
       {'campo':'dimensione','operatore':'in','valori':['Microimpresa']}]}]}
    semplici=[d.solo_campi(r)]
    q=Questionario(semplici,[{'dimensione':'Microimpresa','settore':['Commercio']}])
    monkeypatch.setattr(d,'ramo_imprese',lambda giorno:([r],q))
    d.opzioni_imprese.cache_clear()
    try:
        assert 'Commercio' in d.opzioni_imprese(G)['settore']
        domanda=d.domanda_imprese({},G)
        assert domanda['campo'] in {'settore','dimensione'}
        # Una delle alternative è sufficiente: nessuna domanda inutile sull'altra.
        assert d.domanda_imprese({'dimensione':'Microimpresa'},G) is None
    finally: d.opzioni_imprese.cache_clear()

@pytest.mark.parametrize('giorno,stato,chiusura',[
 ('2026-10-31','aperto','2026-10-31'),('2026-11-01','futuro','2027-09-30'),
 (G,'futuro','2027-09-30'),('2027-03-02','aperto','2027-09-30'),('2027-10-01','chiuso','2027-09-30')])
def test_finestre_distinte_e_data_export(giorno,stato,chiusura):
    r=next(r for r in d.regole_imprese_documenti() if r['id'].startswith('camera-bg-bando-rinnova-'))
    assert stato_temporale(r,giorno)==stato
    assert aperta(r,giorno)==(stato=='aperto')
    assert d.risultato(valuta(r,{}),{},giorno)['chiusura']==chiusura

def test_its_chiuso_preservato_e_ruolo_non_assimilato():
    r=next(r for r in d.regole_imprese_documenti() if r['id'].startswith('camera-bs-bando-its-borse-'))
    assert stato_temporale(r,G)=='chiuso'
    assert 'ITS' in r['requisiti'][0]['non_modellabile']
    assert r['id'] not in {r['id'] for r in d.ramo_imprese(G)[0]}

def test_api_compressione_senza_perdita_di_spiegazioni(monkeypatch):
    monkeypatch.setenv('TROVA_BANDI_GIORNO',G)
    client=TestClient(app);body={'ramo':'persone','profilo':{'isee':NON_SO}}
    with client.stream('POST','/api/passo',json=body,headers={'accept-encoding':'gzip'}) as response:
        raw=b''.join(response.iter_raw())
        assert response.headers['content-encoding']=='gzip'
    compresso=json.loads(gzip.decompress(raw))
    identita=client.post('/api/passo',json=body,headers={'accept-encoding':'identity'}).json()
    assert compresso==identita and all('requisiti' in r for r in compresso['risultati'])
    assert len(raw)<len(json.dumps(identita).encode())/2


def test_indicazione_utente_iscro_separata_dalle_etichette():
    import yaml
    p=d.ROOT/'data/gold/lorenzo/inps-indennita-straordinaria-di-continuita-redditu.yaml'
    originale=yaml.safe_load(p.read_text())
    profilo={'condizione_lavorativa':['occupato'],'tipo_lavoro':['parasubordinato'],
             'iscro_cococo_senza_iva':True,'reddito_autonomo_precedente_iscro':5000}
    profilo=d.completa(profilo,G)
    demo=next(r for r in d.regole_persone(True) if r['id']==originale['id'])
    assert valuta(demo,profilo).stato==DA_VERIFICARE
    assert originale['requisiti'][1]['valori']==['autonomo']
    assert d.risultato(valuta(demo,profilo),profilo,G)['revisione_umana'] is None


def test_citazioni_buoni_canonici_sul_documento_completo():
    from pipeline.citazioni import problemi
    r=next(r for r in d.regole_persone(True) if r['id']=='toscana-contributi-per-la-frequenza-delle-scuole-9bae68')
    testo=(d.ROOT/'data/fonti_verificate/buoni-allegato.txt').read_text()
    assert not problemi(r,testo)


def test_import_imprese_nuovo_registra_fonte_ma_non_inventa_prompt(tmp_path,monkeypatch):
    from pipeline import estrai_imprese as e
    monkeypatch.setattr(e,'USCITA',tmp_path/'regole')
    monkeypatch.setattr(e,'SENZA',tmp_path/'senza')
    doc={'id':'prova','titolo':'Prova','ente':'Ente','url':'https://example.invalid',
         'pagine':['Possono partecipare le imprese.'],'scaricato':'2026-11-01'}
    monkeypatch.setattr(e,'documenti',lambda ids:[doc])
    risposta={'prova':{'requisiti':[{'campo':'tipologia','operatore':'interseca','valori':['Impresa'],
                'fonte':'Ente, pagina 1','citazione':'Possono partecipare le imprese.'}]}}
    f=tmp_path/'risposta.json';f.write_text(json.dumps(risposta))
    assert e.importa([str(f)])==0
    import yaml
    regola=yaml.safe_load((e.USCITA/'prova.yaml').read_text())
    p=regola['provenienza']
    assert p['sha256_fonte'] and p['sha256_schema'] and p['estrazione_utc']
    assert p['sha256_prompt'] is None and p['revisione_umana'] is None
    assert p['acquisizione_fonte'] is None  # scaricato storico non trasformato in acquisizione certa
    assert json.loads((e.USCITA/'fonti/prova.fonte.json').read_text())==doc
