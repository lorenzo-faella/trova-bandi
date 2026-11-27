"""Proprietà emerse dall'audit: ignoto non è falso, eccezioni e selezione condivisa."""
import copy
import json
import math

import pytest
from fastapi.testclient import TestClient
from pipeline.motore import NON_SO, NON_IDONEO, IDONEO, IDONEO_SALVO, DA_VERIFICARE, MANCANO_DATI, stato_temporale, valuta, verifica
from pipeline.regole import carica, DIR_PERSONE
from web import domande as d
from web.server import app

G = '2026-11-21'
NASPI = dict(contributi_agricoli_presenti=False, lavoro_terminato=True, ultimo_lavoro_subordinato=True, esclusione_naspi=False,
             altri_lavori_in_essere=False, disponibilita_lavoro_naspi=True,
             dimissioni_indeterminato_12_mesi=False, termine_naspi_particolare=False,
             causa_fine_lavoro='licenziamento', settimane_contributi_4_anni=20, giorni_da_cessazione_lavoro=30)

@pytest.fixture(scope='module')
def regole(): return {r['id']:r for r in carica(DIR_PERSONE)}

@pytest.mark.parametrize('attuale', [['studente'],['disoccupato'],['occupato'],['studente','occupato']])
def test_rapporto_passato_indipendente_dalla_situazione_attuale(attuale,regole):
    p=d.completa(dict(NASPI,condizione_lavorativa=attuale),G)
    assert p['ultimo_lavoro_subordinato'] is True
    assert valuta(regole['inps-naspi'],p).stato == IDONEO
    assert d.da_porre('ultimo_lavoro_subordinato',dict(condizione_lavorativa=attuale))=='lavoro_terminato'


def test_part_time_rimasto_ha_riserva_sul_reddito(regole):
    p=d.completa(dict(NASPI,condizione_lavorativa=['occupato'],altri_lavori_in_essere=True,lavori_rimasti_naspi="solo_part_time"),G)
    e=valuta(regole['inps-naspi'],p)
    assert e.stato==DA_VERIFICARE and not e.falliti
    assert any('reddito' in str(q) for q in e.mancanti)

@pytest.mark.parametrize('fatto', ['lavoro_terminato','ultimo_lavoro_subordinato','esclusione_naspi', 'settimane_contributi_4_anni','altri_lavori_in_essere'])
def test_ignoranza_non_diventa_esclusione(fatto,regole):
    for ignoto in (None,NON_SO):
        p=dict(NASPI);p[fatto]=ignoto
        assert valuta(regole['inps-naspi'],p).stato!=NON_IDONEO


def test_nessun_lavoro_precedente_esclude_senza_data_fittizia(regole):
    p=d.completa({'lavoro_terminato':False,'condizione_lavorativa':['studente']},G)
    assert 'giorni_da_cessazione_lavoro' not in p
    assert valuta(regole['inps-naspi'],p).stato==NON_IDONEO

@pytest.mark.parametrize('giorni', [67,68,69,80])
@pytest.mark.parametrize('particolare', [True,False,NON_SO])
def test_termine_naspi_soglie_e_fattispecie(giorni,particolare,regole):
    e=valuta(regole['inps-naspi'],dict(NASPI,giorni_da_cessazione_lavoro=giorni,termine_naspi_particolare=particolare))
    assert (e.stato==NON_IDONEO) == (giorni>68 and particolare is False)
    if giorni>68 and particolare is True: assert e.stato==DA_VERIFICARE
    if giorni>68 and particolare==NON_SO: assert e.stato==MANCANO_DATI

@pytest.mark.parametrize('settimane,eccezione,atteso',[(12,False,NON_IDONEO),(13,False,IDONEO),(12,True,IDONEO),(NON_SO,False,MANCANO_DATI)])
def test_dimissioni_precedenti_e_nuovo_requisito(settimane,eccezione,atteso,regole):
    assert valuta(regole['inps-naspi'],dict(NASPI,dimissioni_indeterminato_12_mesi=True,eccezione_dimissioni_precedenti=eccezione,settimane_da_dimissioni=settimane)).stato==atteso


def test_esclusioni_e_risoluzione_consensuale(regole):
    assert valuta(regole['inps-naspi'],dict(NASPI,esclusione_naspi=True)).stato==NON_IDONEO
    for causa in ['risoluzione_consensuale','risoluzione_consensuale_tutelata']:
        assert valuta(regole['inps-naspi'],dict(NASPI,causa_fine_lavoro=causa)).stato==DA_VERIFICARE

@pytest.mark.parametrize('auto,barche,esclude',[(False,False,False),(True,False,True),(False,True,True),(True,True,True),(NON_SO,False,False),(False,NON_SO,False)])
def test_adi_beni_indipendenti(auto,barche,esclude,regole):
    p={'auto_moto_non_agevolati':auto,'barche_aerei':barche}
    e=valuta(regole['inps-adi'],p)
    assert (e.stato==NON_IDONEO)==esclude
    if NON_SO in p.values(): assert e.stato==MANCANO_DATI


def test_compatibilita_vecchia_domanda_veicoli_e_ignoto():
    assert d.completa({'veicoli_esclusi':True},G).get('auto_moto_non_agevolati') is None
    assert d.completa({'veicoli_esclusi':True,'solo_veicoli_agevolati':False},G).get('auto_moto_non_agevolati') is None  # Non sappiamo quale categoria: niente fatti inventati.
    p=d.completa({'veicoli_esclusi':True,'solo_veicoli_agevolati':True},G)
    assert p['auto_moto_non_agevolati'] is False and p['barche_aerei'] is False
    with pytest.raises(ValueError):d.completa({'veicoli_esclusi':True,'solo_veicoli_agevolati':True,'barche_aerei':True},G)


def test_identita_non_url_e_ruolo():
    regole=d.regole_persone(True);ids={r['id'] for r in regole}
    assert 'toscana-buoni-scuola-infanzia-2026' not in ids
    assert 'trento-portale-provincia-autonoma-di-trento-contributo-d28e23' not in ids
    r=next(r for r in regole if r['id']=='toscana-contributi-per-la-frequenza-delle-scuole-9bae68')
    assert r['_identita']['edizione']=='2026' and r['_versioni_precedenti'][0]['sha256']
    # Un figlio di due anni non è escluso dal solo titolo; iscrizione e ISEE minorenni restano da verificare.
    assert valuta(r,{'nucleo':[{'eta':40,'figlio':False},{'eta':2,'figlio':True}],'isee_minorenni':9000}).stato==MANCANO_DATI
    assert len([r for r in regole if r['id'].startswith('entrate-detrazioni-affitto-2026-')])==3
    assert valuta(r,{'nucleo':[{'eta':40,'figlio':False}],'isee_minorenni':9000}).stato==MANCANO_DATI  # Anche un tutore: nessun no dalla sola parentela.

@pytest.mark.parametrize('extra,stato',[({},'non verificato'),({'chiusura':'2050-01-01'},'non verificato'),({'apertura':'2026-12-01'},'futuro'),({'chiusura':'2026-11-20'},'chiuso'),({'chiusura':G},'aperto'),({'disponibilita':'permanente'},'permanente')])
def test_date_non_dedotte(extra,stato):assert stato_temporale(dict(apertura=None,chiusura=None,**{k:v for k,v in extra.items() if k not in ('apertura','chiusura')})|extra,G)==stato

@pytest.mark.parametrize('ramo,profilo',[
 ('persone',{'isee':True}),('persone',{'nucleo':[{'eta':True}]}),('persone',{'nucleo':[]}),
 ('persone',{'cittadinanza':'marziana'}),('persone',{'comune':'Milnao'}),('persone',{'regione':'Lazio','comune':'Milano'}),
 ('persone',{'condizione_lavorativa':['occupato','inattivo']}),('persone',{'eta':20,'anni_residenza_italia':21}),
 ('persone',{'data_evento_figlio':'2999-01-01'}),('persone',{'eta':23.5}),('persone',{'percentuale_invalidita':101}),
 ('persone',{'disabile':True,'nucleo':[{'disabile':False}]}),('persone',{'lavoro_terminato':False,'causa_fine_lavoro':'licenziamento'}),
 ('imprese',{'dimensione':True}),('imprese',{'regione':['Lombardia']}),('imprese',{'comune':'Milnao'}),
 ('imprese',{'ateco_2025':True}),('imprese',{'tipologia':['banana']}),('imprese',{'isee':100}),
])
def test_api_non_valuta_input_malformati(ramo,profilo,monkeypatch):
    monkeypatch.setenv('TROVA_BANDI_GIORNO',G)
    r=TestClient(app).post('/api/passo',json={'ramo':ramo,'profilo':profilo})
    assert r.status_code==422 and r.json()['detail']


def test_api_normalizza_senza_indovinare_e_ammette_frazioni():
    p=d.completa({'comune':'  MILANO ','regione':'Lombardia','eta':30,'anni_residenza_italia':12.5,'isee':1020.5},G)
    assert p['comune']=='Milano' and p['anni_residenza_italia']==12.5
    for v in [float('nan'),float('inf'),-float('inf')]:
        with pytest.raises(ValueError):d.completa({'isee':v},G)

@pytest.mark.parametrize('a,b,atteso',[(True,NON_SO,True),(NON_SO,False,False),(None,True,True),(False,None,False)])
def test_unica_persona_anche_con_ignoto(a,b,atteso):
    p=d.completa({'disabile':a,'nucleo':[{'eta':40,'disabile':b}]},G)
    assert p['disabile'] is atteso and p['nucleo'][0]['disabile'] is atteso
    assert not d.domanda_persone('nucleo.disabile',1,p)['componenti']


def test_nucleo_parziale_non_perde_eta_o_parentela():
    p=d.completa({'nucleo':[{'eta':40},{'eta':NON_SO,'figlio':True}]},G)
    assert p['eta']==40 and p['numero_figli']==1 and p['nucleo'][1]['eta']==NON_SO
    assert 'figlio' not in d.completa({'nucleo':[{'eta':40},{'eta':39}]},G)['nucleo'][1]


def test_estratta_non_certificata_e_filtri_imprese():
    for origine in ['estratta','open data']:
        r=dict(id='prova',titolo='Prova',requisiti=[],_origine=origine,apertura=None,chiusura=None)
        out=d.risultato(valuta(r,{}),{},G)
        assert out['revisione_umana'] is None and out['avvertenze']
        if origine=='estratta':assert out['stato']==DA_VERIFICARE
        else:assert any('soltanto i filtri' in t for t in out['avvertenze'])


def test_territorio_requisito_prevale_sulla_sola_provenienza():
    r={'stato':DA_VERIFICARE,'regione':'Toscana','stato_temporale':'aperto','a_favore':1,'territorio':{'esito':'compatibile'}}
    assert d.gruppo_risultato(r,['Lombardia']) is None
    r['territorio']['esito']='da verificare'
    assert d.gruppo_risultato(r,['Lombardia'])=='lontano'


def test_pagina_saltata_non_ripete_regione_e_comune():
    p=d.completa({'residente_italia':NON_SO,'regione':NON_SO,'comune':NON_SO,'domicilio_diverso':NON_SO},G)
    assert d.prossima_persone([],p)==(None,0)
    assert d.da_chiedere({'campo':'comune','operatore':'in','valori':['Milano']},p)==set()


def test_fatti_noti_superano_segnaposto_ignoti_di_pagine_composte():
    p=d.completa({'residente_italia':True,'sempre_in_italia':True,'anni_residenza_italia':NON_SO,'anni_residenza_continuativa_italia':NON_SO,'nucleo':[{'eta':35}],'regione':'Lombardia','comune':'Milano','domicilio_diverso':False,'comune_domicilio':NON_SO},G)
    assert p['anni_residenza_italia']==p['anni_residenza_continuativa_italia']==35
    assert p['comune_domicilio']=='Milano'


def test_provenienza_reale_con_snapshot_e_senza_revisione_inventata(tmp_path):
    import hashlib
    from pipeline.provenienza import registra,salva_snapshot,serializza
    r={'id':'prova'};fonte={'url':'https://example.org','testo':'Fonte originale'}
    registra(r,fonte,'prompt originale','test')
    salva_snapshot(r,fonte,tmp_path)
    p=r['provenienza']
    assert p['revisione_umana'] is None and p['acquisizione_fonte'] is None
    assert hashlib.sha256((tmp_path/p['snapshot_fonte']).read_bytes()).hexdigest()==p['sha256_fonte']
    assert (tmp_path/p['snapshot_prompt']).read_text()=='prompt originale'
    assert p['sha256_fonte']==hashlib.sha256(serializza(fonte)).hexdigest()


@pytest.mark.parametrize('regione',['Lombardia','Puglia'])
def test_comuni_omonimi_rispettano_regione_e_codice_istat(regione):
    p=d.completa({'comune':'Castro','regione':regione},G)
    assert p['comune']=='Castro'
    assert d.codici_comuni()[('Castro','Lombardia')]!=d.codici_comuni()[('Castro','Puglia')]
    assert d.codici_comuni()[('Castro',regione)].isdigit() and len(d.codici_comuni()[('Castro',regione)])==6


def test_comune_omonimo_senza_regione_non_viene_indovinato():
    with pytest.raises(ValueError):d.completa({'comune':'Castro'},G)


def fino_alla_fine_senza_sapere():
    """Il questionario delle persone fino in fondo, rispondendo "non so" a tutto."""
    p = {}
    for _ in range(160):
        out = d.passo('persone', p, G, True)
        q = out['domanda']
        if q is None:
            return out
        prima = copy.deepcopy(p)
        if q['tipo'] == 'pagina':
            for parte in q['parti']:
                p[parte['campo']] = NON_SO
        elif q.get('per_componente'):
            k = q['campo'].split('.')[1]
            for c in q['componenti']:
                p['nucleo'][c['indice']][k] = NON_SO
        else:
            p[q['campo']] = NON_SO
        assert p != prima, f"Domanda ripetuta: {q['campo']}"
    raise AssertionError('questionario non termina')


def test_calendario_esclude_ignoti_date_non_verificate_e_altre_aree(monkeypatch):
    out = fino_alla_fine_senza_sapere()
    assert not any(r['calendario_ammesso'] for r in out['risultati'])
    # Una misura compatibile di un'altra area resta visibile e non viene esportata automaticamente.
    r=dict(id='prova',titolo='Prova',requisiti=[{'campo':'isee','operatore':'<=','valore':20000}],apertura='2026-01-01',chiusura='2026-12-31',_origine='riferimento')
    monkeypatch.setattr(d,'regole_persone',lambda estratte=False:[r])
    monkeypatch.setattr(d,'territorio',lambda r:'Toscana')
    fuori=d.passo('persone',{'regione':'Lombardia','isee':10000},G,True)['risultati'][0]
    assert fuori['stato']==IDONEO and fuori['gruppo']=='lontano' and not fuori['calendario_ammesso']
    dentro=d.passo('persone',{'regione':'Toscana','isee':10000},G,True)['risultati'][0]
    assert dentro['calendario_ammesso']
