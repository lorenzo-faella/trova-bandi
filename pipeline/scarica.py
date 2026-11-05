"""Stadio 1: scarica le fonti open data in data/raw/.

  incentivi  catalogo di incentivi.gov.it (licenza IODL 2.0). È la stessa richiesta che fa il pulsante
             "Esporta" del portale: una GET all'indice Solr pubblico, con i campi dell'export ufficiale.
  comuni     elenco dei comuni italiani ISTAT (CC BY 4.0), per collegare comune e regione.

Un file per giorno: se esiste già non riscarica, così il portale viene interrogato al massimo una volta al giorno.
Uso: python -m pipeline.scarica incentivi|comuni
"""
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
UA = {"User-Agent": "trova-bandi (progetto universitario Bocconi 20875)"}

SOLR = "https://www.incentivi.gov.it/solr/coredrupal/select"
# nome nell'export ufficiale -> campo Solr (lista aliases_file nel JavaScript del portale)
CAMPI = {
    "ID_Incentivo": "zs_nid", "Titolo": "zs_title", "Descrizione": "zs_body",
    "Obiettivo_Finalita": "zm_field_scopes_value", "Data_apertura": "zs_field_open_date",
    "Data_chiusura": "zs_field_close_date", "Note_di_apertura_chiusura": "zs_field_close_date_descriptor",
    "Dimensioni": "zm_field_dimensions_value", "Tipologia_Soggetto": "zm_field_subject_type_value",
    "Forma_agevolazione": "zm_field_support_form_value", "Costi_Ammessi": "zm_field_granted_costs_value",
    "Spesa_Ammessa_min": "zs_field_cost_min", "Spesa_Ammessa_max": "zs_field_cost_max",
    "Agevolazione_Concedibile_min": "zs_field_support_grant_type_min",
    "Agevolazione_Concedibile_max": "zs_field_support_grant_type_max",
    "Settore_Attivita": "zm_field_activity_sector_value", "Codici_ATECO": "zs_field_ateco",
    "Regioni": "zm_field_regions_value", "Comuni": "zs_field_comuni",
    "Ambito_territoriale": "zm_field_special_territory_value", "Soggetto_Concedente": "zs_field_subject_grant",
    "Base_normativa_primaria": "zs_field_primary_ruleset", "Base_normativa_secondaria": "zs_field_secondary_ruleset",
    "Provvedimento_attuativo": "zs_field_implementation_ruleset", "Gazzetta_ufficiale": "zs_field_official_references",
    "Stanziamento_incentivo": "zs_field_budget_allocation", "Link_istituzionale": "zs_field_link",
    "Altre_caratteristiche": "zs_field_other_characteristic", "Data_ultimo_aggiornamento": "ds_last_update",
}
ISTAT_COMUNI = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"


def get(url, timeout):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def scarica_incentivi(oggi):
    out = RAW / f"incentivi_export_{oggi}.json"
    if out.exists():
        return out, "già presente"
    params = {"q.op": "OR", "wt": "json", "rows": "8000", "q": "index_id:incentivi ",
              "fl": ",".join(f"{k}:{v}" for k, v in CAMPI.items()) + ","}
    url = f"{SOLR}?{urllib.parse.urlencode(params)}"
    risposta = json.loads(get(url, timeout=180))["response"]
    docs = risposta["docs"]
    if len(docs) < risposta["numFound"]:  # rows troppo basso: l'export sarebbe troncato senza avvisi
        raise RuntimeError(f"scaricati {len(docs)} incentivi su {risposta['numFound']}: alzare rows")
    out.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
    meta = {"fonte": SOLR, "parametri": params, "scaricato": dt.datetime.now().isoformat(timespec="seconds"),
            "incentivi": len(docs), "licenza": "IODL 2.0"}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return out, f"{len(docs)} incentivi"


def scarica_comuni(oggi):
    out = RAW / f"istat_comuni_{oggi}.csv"
    if out.exists():
        return out, "già presente"
    out.write_bytes(get(ISTAT_COMUNI, timeout=60))
    meta = {"fonte": ISTAT_COMUNI, "scaricato": dt.datetime.now().isoformat(timespec="seconds"), "licenza": "CC BY 4.0"}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return out, f"{out.stat().st_size // 1024} KB"


if __name__ == "__main__":
    fonti = {"incentivi": scarica_incentivi, "comuni": scarica_comuni}
    if len(sys.argv) != 2 or sys.argv[1] not in fonti:
        sys.exit(f"uso: python -m pipeline.scarica {'|'.join(fonti)}")
    RAW.mkdir(parents=True, exist_ok=True)
    percorso, esito = fonti[sys.argv[1]](dt.date.today().isoformat())
    print(f"{percorso.name}: {esito}")
