"""Demo web di trova-bandi: un'API FastAPI sopra il motore e una pagina HTML (web/static/).

Il server non salva niente: il profilo vive nel browser e arriva intero a ogni passo (vocabolario delle persone,
scelta 2: ISEE, redditi e disabilità sono dati sensibili). Nessun log del contenuto delle richieste.

Uso: make demo    oppure    python -m uvicorn web.server:app --port 8000
Variabile TROVA_BANDI_GIORNO (AAAA-MM-GG): il giorno per decidere quali bandi sono aperti; di default oggi.
"""
import datetime as dt
from contextlib import asynccontextmanager
import os
import threading
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field, StrictBool, ConfigDict

from web import domande

STATIC = Path(__file__).resolve().parent / "static"

@asynccontextmanager
async def avvio(app):
    """Il confronto dei profili costa qualche secondo: lo si calcola subito, in un thread, così la pagina iniziale non
    aspetta (decisione 104). Se fallisce, lo rifà la prima richiesta."""
    threading.Thread(target=lambda: (domande.confronto_profili(giorno()), domande.percorsi_profili(giorno())), daemon=True).start()
    yield


app = FastAPI(title="trova-bandi", description="Demo del motore di idoneità (progetto 20875, Bocconi)", lifespan=avvio)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


def giorno():
    return os.environ.get("TROVA_BANDI_GIORNO") or dt.date.today().isoformat()



class Passo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ramo: Literal["persone", "imprese"]
    profilo: dict[str, Any] = Field(default_factory=dict)
    modifica: str | None = None
    estratte: StrictBool = True  # persone: anche le regole estratte dall'LLM e non ancora riviste (con un badge; decisione 68)


@app.post("/api/passo")
def passo(richiesta: Passo):
    """Esiti per il profilo di adesso e prossima domanda."""
    try:
        return domande.passo(richiesta.ramo, richiesta.profilo, giorno(), richiesta.estratte, richiesta.modifica)
    except (TypeError, ValueError) as e:
        # una risposta di tipo sbagliato (testo dove serve un numero): errore di chi chiama, non del server
        raise HTTPException(status_code=422, detail=f"profilo non valido: {e}")


@app.get("/api/statistiche")
def statistiche():
    """I numeri della pagina iniziale."""
    return domande.statistiche(giorno())


@app.get("/api/profili")
def profili():
    """Le persone tipo del caro vita, per provare la demo in pochi secondi."""
    return domande.profili_demo()


@app.get("/api/confronto")
def confronto():
    """Cosa vede ogni profilo d'esempio: aiuti compatibili, possibili e i primi nomi (decisione 104)."""
    return domande.confronto_profili(giorno())


@app.get("/api/percorsi")
def percorsi():
    """Per il grafico dei percorsi: la risposta di ogni profilo a ogni passo, gli aiuti in vista e quelli all'arrivo."""
    return domande.percorsi_profili(giorno())


@app.get("/api/comuni")
def comuni(regione: str | None = None):
    """I comuni di una regione; senza regione (o con "non lo so") tutti i comuni d'Italia."""
    if not regione or regione == domande.NON_SO:
        return sorted({c for elenco in domande.comuni_per_regione().values() for c in elenco})
    elenco = domande.comuni_per_regione().get(regione)
    if elenco is None:
        raise HTTPException(status_code=404, detail="regione sconosciuta")
    return elenco


app.mount("/", StaticFiles(directory=STATIC, html=True), name="pagina")
