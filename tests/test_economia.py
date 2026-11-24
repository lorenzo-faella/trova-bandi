"""Esclusioni reddituali riprodotte: soglie versionate, periodi e definizioni distinti."""
import copy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pipeline.citazioni import nodi, problemi, fonti_aggiuntive
from pipeline.motore import DA_VERIFICARE, MANCANO_DATI, NON_IDONEO, NON_SO, valuta, verifica
from pipeline.regole import VALIDATORE
from web import domande as d
from web.server import app

G='2026-11-21'
ISCRO='inps-indennita-straordinaria-di-continuita-redditu'
PENSIONE='inps-pensione-inabilita-invalidi-civili'
BASE=dict(eta=45,residente_italia=True,regione='Lombardia',comune='Milano',cittadinanza='italiana',
          condizione_lavorativa=['occupato'],tipo_lavoro=['autonomo'])

def regola(id):return next(r for r in d.regole_persone(True) if r['id']==id)
def stato(id,p,giorno=G):return valuta(regola(id),d.completa(p,giorno)).stato

def pensione(**extra):
    return dict(eta=45,residente_italia=True,cittadinanza='italiana',disabile=True,percentuale_invalidita=100) | extra

@pytest.mark.parametrize('valore,atteso',[(0,DA_VERIFICARE),(12000,DA_VERIFICARE),(12500,DA_VERIFICARE),
 (12749.18,DA_VERIFICARE),(12749.19,NON_IDONEO),(NON_SO,MANCANO_DATI)])
def test_iscro_soglia_ufficiale_2026_e_centesimi(valore,atteso):
    assert stato(ISCRO,dict(BASE,reddito_autonomo_precedente_iscro=valore))==atteso

@pytest.mark.parametrize('vecchio',[0,12500,30000])
def test_iscro_non_confonde_irpef_complessivo_con_reddito_autonomo(vecchio):
    assert stato(ISCRO,dict(BASE,reddito_richiedente=vecchio))==MANCANO_DATI
    assert stato(ISCRO,dict(BASE,reddito_richiedente=vecchio,reddito_autonomo_precedente_iscro=12500))==DA_VERIFICARE

@pytest.mark.parametrize('giorno',['2025-11-21','2027-01-02'])
def test_parametro_annuale_non_esteso_ad_altri_anni(giorno):
    assert stato(ISCRO,dict(BASE,reddito_autonomo_precedente_iscro=30000),giorno)==DA_VERIFICARE
    assert stato(PENSIONE,pensione(prima_liquidazione_inabilita=True,reddito_presunto_corrente_inabilita=30000),giorno)==DA_VERIFICARE

@pytest.mark.parametrize('scorso,corrente,atteso',[(30000,0,DA_VERIFICARE),(0,30000,NON_IDONEO),
 (30000,20029.54,DA_VERIFICARE),(0,20029.55,NON_IDONEO),(30000,NON_SO,MANCANO_DATI)])
def test_prima_liquidazione_usa_reddito_corrente(scorso,corrente,atteso):
    assert stato(PENSIONE,pensione(reddito_richiedente=scorso,prima_liquidazione_inabilita=True,
           reddito_presunto_corrente_inabilita=corrente))==atteso

@pytest.mark.parametrize('pensioni,altri,atteso',[(12000,8000,DA_VERIFICARE),(12000,9000,NON_IDONEO),
 (0,0,DA_VERIFICARE),(12000,8029.54,DA_VERIFICARE),(12000,8029.55,NON_IDONEO),(NON_SO,0,MANCANO_DATI),(0,NON_SO,MANCANO_DATI)])
def test_successive_sommano_periodi_corretti_senza_zero_presunto(pensioni,altri,atteso):
    p=pensione(prima_liquidazione_inabilita=False,reddito_pensioni_corrente_inabilita=pensioni,
               altri_redditi_precedente_inabilita=altri,reddito_richiedente=999999)
    assert stato(PENSIONE,p)==atteso
    completo=d.completa(p,G)
    assert completo['reddito_rilevante_successiva_inabilita']==(NON_SO if NON_SO in (pensioni,altri) else pensioni+altri)

def test_nessuna_presunzione_su_prima_liquidazione_o_reddito_mancante():
    assert stato(PENSIONE,pensione(reddito_richiedente=30000))==MANCANO_DATI
    p=d.completa(pensione(prima_liquidazione_inabilita=False,reddito_pensioni_corrente_inabilita=0),G)
    assert 'reddito_rilevante_successiva_inabilita' not in p
    assert d.da_porre('reddito_rilevante_successiva_inabilita',p)=='altri_redditi_precedente_inabilita'

@pytest.mark.parametrize('primo',[True,False])
def test_questionario_raccoglie_solo_i_periodi_pertinenti(monkeypatch,primo):
    r=copy.deepcopy(regola(PENSIONE));monkeypatch.setattr(d,'regole_persone',lambda estratte=False:[r])
    p=pensione(residente_italia=True,regione='Lombardia',comune='Milano',domicilio_diverso=False)
    answers={'prima_liquidazione_inabilita':primo,'reddito_presunto_corrente_inabilita':0,
             'reddito_pensioni_corrente_inabilita':0,'altri_redditi_precedente_inabilita':0}
    chieste=[]
    for _ in range(8):
        out=d.passo('persone',p,G,True)
        if out['domanda'] is None:break
        q=out['domanda'];chieste.append(q['campo']);p[q['campo']]=answers[q['campo']]
    else:raise AssertionError('questionario ripete le domande')
    assert chieste==(['prima_liquidazione_inabilita','reddito_presunto_corrente_inabilita'] if primo else
                     ['prima_liquidazione_inabilita','reddito_pensioni_corrente_inabilita','altri_redditi_precedente_inabilita'])
    assert out['risultati'][0]['stato']==DA_VERIFICARE

@pytest.mark.parametrize('campo,valore',[('reddito_autonomo_precedente_iscro',-1),('reddito_presunto_corrente_inabilita',True),
 ('reddito_pensioni_corrente_inabilita',-1),('reddito_rilevante_successiva_inabilita',0),('_anno_valutazione',2026)])
def test_api_rifiuta_valori_errati_e_derivati_iniettati(campo,valore):
    assert TestClient(app).post('/api/passo',json={'ramo':'persone','profilo':{campo:valore}}).status_code==422

@pytest.mark.parametrize('id,profilo',[(ISCRO,dict(BASE,reddito_richiedente=12500,reddito_autonomo_precedente_iscro=12500)),
 (PENSIONE,pensione(reddito_richiedente=30000,prima_liquidazione_inabilita=True,reddito_presunto_corrente_inabilita=0))])
def test_api_non_riproduce_le_due_false_esclusioni(monkeypatch,id,profilo):
    monkeypatch.setenv('TROVA_BANDI_GIORNO',G)
    out=TestClient(app).post('/api/passo',json={'ramo':'persone','profilo':profilo}).json()
    r=next(r for r in out['risultati'] if r['id']==id)
    assert r['stato']==DA_VERIFICARE
    # una prestazione INPS senza date è permanente (decisione 95): nessuna scadenza da mettere in calendario
    assert r['stato_temporale'] in ('non verificato','permanente') and not r['calendario_ammesso']

@pytest.mark.parametrize('tipo,soglia',[('inquilini',30987.41),('giovani',15493.71)])
def test_detrazioni_non_usano_irpef_generico_o_eta_odierna(tipo,soglia):
    id='entrate-detrazioni-affitto-2026-'+tipo
    p={'eta':31,'abitazione':'affitto','reddito_richiedente':999999,'reddito_locazione_2025':soglia,'eta_giovani_locazione_2025':True}
    assert stato(id,p)==DA_VERIFICARE
    assert stato(id,dict(p,reddito_locazione_2025=soglia+.01))==NON_IDONEO
    assert stato(id,{k:v for k,v in p.items() if k!='reddito_locazione_2025'})==MANCANO_DATI

def test_genova_usa_canone_2025_isee_2026_e_imu():
    r=regola('genova-fondo-sociale-affitti-2026')
    mapping={'canone_2025_genova':6000,'isee_2026_genova':9000,'patrimonio_imu_genova':103741.56}
    for q in r['requisiti']:
        if q.get('campo') in mapping:
            c=q['campo'];v=mapping[c]
            assert verifica(q,{c:v,'canone_annuo':100000,'isee':100000,'patrimonio_immobiliare':1e6}) is True
            assert verifica(q,{c:v+.01}) is False
            assert verifica(q,{'canone_annuo':0,'isee':0,'patrimonio_immobiliare':0}) is None

def test_fvg_confronta_isee_minorenni_conservando_esenzioni():
    r=regola('fvg-previdenza-complementare-famiglia-e-infa-791782')
    q=r['requisiti'][1]
    assert verifica(q,{'isee':50000,'isee_minorenni':9000}) is True
    assert verifica(q,{'isee':9000,'isee_minorenni':50000}) is None  # esenzioni non rappresentate
    assert verifica(q,{'isee':0}) is None

def test_schemi_citazioni_e_gold_originale_preservati():
    import yaml
    ids=[ISCRO,PENSIONE,'entrate-detrazioni-affitto-2026-giovani','entrate-detrazioni-affitto-2026-inquilini']
    from pipeline.citazioni import carica_testi_inps
    from pipeline.estrai_documenti import documenti
    testi=carica_testi_inps()
    testi.update({doc['url']:' '.join(doc['pagine']) for doc in documenti()})
    gold=yaml.safe_load((d.ROOT/'data/gold/lorenzo'/f'{ISCRO}.yaml').read_text())
    assert next(q['valore'] for q in gold['requisiti'] if q.get('campo')=='reddito_richiedente')==12000
    assert regola(ISCRO)['_versioni_precedenti'][0]['sha256']
    for id in ids:
        r=regola(id);VALIDATORE.validate({k:v for k,v in r.items() if not k.startswith('_')})
    mancanti=[id for id in ids if regola(id)['link'] not in testi]
    if mancanti:  # data/raw/documenti non è in git: su un'altra macchina servono i testi scaricati
        pytest.skip(f"testi delle fonti non scaricati: {', '.join(mancanti)}")
    for id in ids:
        r=regola(id);assert not problemi(r, testi[r['link']])

def test_domande_e_importi_esplicitano_anni_e_centesimi():
    p=d.completa({},G)
    q=d.domanda_persone('reddito_autonomo_precedente_iscro',1,p)
    assert '2026' in q['testo'] and '2025' in q['testo']
    assert '12.749,18' in d.descrivi({'campo':'reddito_autonomo_precedente_iscro','operatore':'<=','valore':12749.18})
    assert d.leggibile('reddito_autonomo_precedente_iscro',12749.18)=='12.749,18 euro'

@pytest.mark.parametrize('id,campo,limite',[
 ('lombardia-nidi-gratis-plus-2026-27-adesione-famigl-3942cb','isee_nidi_gratis_2026',25000),
 ('comune-pescara-avviso-pubblico-bando-libri-fornitura-gr-e0d466','isee_libri_pescara_2026',15493.71)])
def test_isee_specifico_non_sostituito_da_quello_generico(id,campo,limite):
    q=next(n for req in regola(id)['requisiti'] for n in nodi(req) if n.get('campo')==campo)
    assert verifica(q,{campo:limite,'isee':999999}) is True
    assert verifica(q,{campo:limite+.01,'isee':0}) is False
    assert verifica(q,{'isee':0,'isee_minorenni':0}) is None


def test_palermo_proprieta_non_dedotta_da_patrimonio_isee():
    r=regola('palermo-contributo-affitto-2026')
    assert not any(n.get('campo')=='patrimonio_immobiliare' for q in r['requisiti'] for n in nodi(q))
    q=next(q for q in r['requisiti'] if 'Assenza di diritti' in q.get('non_modellabile',''))
    assert verifica(q,{'patrimonio_immobiliare':0}) is None
    assert verifica(q,{'patrimonio_immobiliare':1000000}) is None


def test_catania_non_inventa_soglia_26000():
    r=regola('ersu-catania-metadata-3871-0-r-viewerpreferences-3872-6fb5d2')
    q=next(q for q in r['requisiti'] if q.get('citazione','').startswith('ISEE -'))
    assert verifica(q,{'isee_universitario':25000}) is True
    assert verifica(q,{'isee_universitario':26000}) is None
    assert not any(n.get('valore')==26000 for n in nodi(q))

@pytest.mark.parametrize('id,limite',[('inps-adi',10140),('inps-supporto-per-la-formazione-e-il-lavoro-sfl',10140),('inps-bonus-nuovi-nati',40000)])
def test_isee_familiare_2026_non_dedotto_dall_ordinario(id,limite):
    q=next(n for req in regola(id)['requisiti'] for n in nodi(req) if n.get('campo')=='isee_prestazioni_familiari_2026')
    assert verifica(q,{'_anno_valutazione':2026,'isee':limite+10000,'isee_prestazioni_familiari_2026':limite}) is True
    assert verifica(q,{'_anno_valutazione':2026,'isee':0,'isee_prestazioni_familiari_2026':limite+.01}) is False
    assert verifica(q,{'_anno_valutazione':2026,'isee':0}) is None


@pytest.mark.parametrize('id,limite',[('fvg-dote-famiglia-famiglia-e-infanzia-carta-db9572',35000),('fvg-servizi-per-la-prima-infanzia-abbattimen-cfd78a',50000)])
def test_altri_servizi_fvg_richiedono_isee_minorenni(id,limite):
    q=regola(id)['requisiti'][1]
    assert verifica(q,{'isee':999999,'isee_minorenni':limite}) is True
    assert verifica(q,{'isee':0}) is None

@pytest.mark.parametrize('campo,limite',[('isee_sociosanitario_badanti_2026',35000),('isee_babysitter_filse_2026',35000),('isee_gravissima_filse_2026',65000)])
def test_filse_indicatore_diverso_per_ciascun_bonus(campo,limite):
    r=regola('filse-bonus-badanti-edizione-2026-prestazioni-8be91b')
    q=next(n for req in r['requisiti'] for n in nodi(req) if n.get('campo')==campo and n.get('valore')==limite)
    assert verifica(q,{'isee':999999,campo:limite}) is True
    assert verifica(q,{'isee':0,campo:limite+.01}) is False
    assert verifica(q,{'isee':0}) is None

def test_perugia_non_sostituisce_attestazione_del_modulo_con_generica():
    r=regola('comune-perugia-integrazione-avviso-pubblico-per-lerogaz-fac64f')
    q=next(n for req in r['requisiti'] for n in nodi(req) if n.get('campo')=='isee_voucher_perugia_2026')
    assert verifica(q,{'isee':0}) is None
    assert verifica(q,{'isee_voucher_perugia_2026':14999.99}) is True
    assert verifica(q,{'isee_voucher_perugia_2026':15000}) is False
