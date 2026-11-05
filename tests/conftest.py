import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
GIORNO = "2026-10-27"


@pytest.fixture(scope="session")
def regole():
    from pipeline.regole import carica
    r = carica()
    if not r:
        pytest.skip("nessuna regola generata: eseguire prima `make dati`")
    return r


@pytest.fixture(scope="session")
def manuali():
    d = yaml.safe_load((ROOT / "data" / "profili" / "manuali.yaml").read_text(encoding="utf-8"))
    return {nome: {k: v for k, v in p.items() if k != "descrizione"} for nome, p in d.items()}


@pytest.fixture(scope="session")
def export_grezzo():
    files = sorted(f for f in (ROOT / "data" / "raw").glob("incentivi_export_*.json") if not f.name.endswith(".meta.json"))
    if not files:
        pytest.skip("manca l'export grezzo")
    return files[-1]
