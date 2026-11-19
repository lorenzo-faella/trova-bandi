# Demo di trova-bandi online (decisione 68): il server FastAPI con le regole generate dall'export già in git.
# Locale:  docker build -t trova-bandi . && docker run -p 8000:8000 trova-bandi   ->  http://127.0.0.1:8000
# Render:  render.yaml (il servizio gratuito passa la porta in $PORT)
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Come `make dati`, ma solo ciò che serve alla demo: bandi normalizzati e regole delle imprese (circa 10 secondi).
RUN set -e; \
    RAW=$(ls data/raw/incentivi_export_*.json | grep -v meta | sort | tail -1); \
    GIORNO=$(basename "$RAW" .json | sed 's/incentivi_export_//'); \
    python -m pipeline.normalizza "$RAW" "$GIORNO"; \
    python -m pipeline.regole

EXPOSE 8000
CMD ["sh", "-c", "uvicorn web.server:app --host 0.0.0.0 --port ${PORT}"]
