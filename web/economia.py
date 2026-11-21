"""Sole derivazioni economiche con periodo e definizione documentati."""
import math
from pipeline.motore import NON_SO


def completa_economia(p):
    # INPS: dopo la prima liquidazione, pensioni dell'anno corrente e altri redditi
    # dell'anno precedente. Mai il reddito IRPEF generico né zero dal salto.
    if p.get('prima_liquidazione_inabilita') is False:
        valori = [p.get(c) for c in ('reddito_pensioni_corrente_inabilita', 'altri_redditi_precedente_inabilita')]
        if NON_SO in valori:
            p['reddito_rilevante_successiva_inabilita'] = NON_SO
        elif all(v is not None for v in valori):
            totale = sum(valori)
            if not math.isfinite(totale):
                raise ValueError('redditi_inabilita: la somma deve essere finita')
            p['reddito_rilevante_successiva_inabilita'] = totale
