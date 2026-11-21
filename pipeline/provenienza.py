"""Provenienza delle nuove estrazioni; il passato non riceve metadati ricostruiti."""
import datetime as dt
import hashlib
import json
from pathlib import Path


_PROMPT = {}


def serializza(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, default=str).encode('utf-8')


def registra(regola, fonte, prompt, autore):
    from pipeline.regole import ROOT
    schema = (ROOT / 'schema/regola.schema.json').read_bytes()
    impronta_prompt = hashlib.sha256(prompt.encode('utf-8')).hexdigest() if prompt is not None else None
    if impronta_prompt:
        _PROMPT[impronta_prompt] = prompt
    regola['provenienza'] = {
        'acquisizione_fonte': fonte.get('acquisizione_utc') or fonte.get('scaricato_il'),
        'estrazione_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'versione_documento': fonte.get('versione'),
        'sha256_fonte': hashlib.sha256(serializza(fonte)).hexdigest(),
        'sha256_prompt': impronta_prompt,
        'sha256_schema': hashlib.sha256(schema).hexdigest(),
        'autore_o_modello_dichiarato': autore,
        'revisione_umana': None,
    }
    return regola


def salva_snapshot(regola, fonte, cartella):
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    nome = f"{regola['id']}.fonte.json"
    (cartella / nome).write_bytes(serializza(fonte))
    regola['provenienza']['snapshot_fonte'] = nome

    if (impronta := regola['provenienza'].get('sha256_prompt')) in _PROMPT:
        prompt_nome = f"{regola['id']}.prompt.md"
        (cartella / prompt_nome).write_text(_PROMPT[impronta], encoding='utf-8')
        regola['provenienza']['snapshot_prompt'] = prompt_nome
