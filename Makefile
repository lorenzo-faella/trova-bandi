# Pipeline dati di trova-bandi. Ogni file si rigenera solo se cambiano i suoi ingressi.
#   make           dati + test + misura
#   make scarica   nuovo export (al massimo uno al giorno)
#   make dati      normalizzazione, regole, statistiche, versioni leggibili
#   make test      pytest
#   make controlla schema e citazioni delle regole persone e delle etichette in data/gold
#   make misura    misura del questionario (~30 s)
#   make confronta regole estratte sui benefici di sviluppo contro le regole di riferimento
#   make demo      la demo web su http://127.0.0.1:8000 (Ctrl+C per fermarla)

PY ?= $(HOME)/anaconda3/bin/python
# di default l'export più recente in data/raw
RAW ?= $(lastword $(sort $(filter-out %.meta.json,$(wildcard data/raw/incentivi_export_*.json))))
GIORNO ?= $(patsubst data/raw/incentivi_export_%.json,%,$(RAW))

BANDI = data/processed/bandi.json
REGOLE = data/regole/.generate
PROFILI = data/profili/distribuzioni.yaml data/profili/manuali.yaml

.PHONY: tutto scarica dati test controlla confronta misura demo pulisci
tutto: dati test misura

scarica:
	$(PY) -m pipeline.scarica incentivi
	$(PY) -m pipeline.scarica comuni
	$(PY) -m pipeline.fonti.inps

dati: $(BANDI) $(REGOLE) docs/fattibilita-dati.md data/leggibili/incentivi_$(GIORNO).xlsx

$(BANDI): $(RAW) pipeline/normalizza.py
	$(PY) -m pipeline.normalizza $(RAW) $(GIORNO)

$(REGOLE): $(BANDI) pipeline/regole.py schema/regola.schema.json
	$(PY) -m pipeline.regole
	touch $@

docs/fattibilita-dati.md: $(BANDI) $(REGOLE) pipeline/profila.py
	$(PY) -m pipeline.profila

data/leggibili/incentivi_$(GIORNO).xlsx: $(RAW) pipeline/leggibili.py
	$(PY) -m pipeline.leggibili $(RAW) data/leggibili $(GIORNO)

test: $(REGOLE)
	$(PY) -m pytest -q

controlla:
	$(PY) -m pipeline.citazioni data/regole_persone data/gold

confronta:
	$(PY) -m pipeline.confronta data/regole_estratte/sviluppo data/regole_persone

misura: docs/misura-questionario.md

docs/misura-questionario.md: $(REGOLE) $(PROFILI) pipeline/misura.py pipeline/questionario.py pipeline/motore.py pipeline/profili.py
	$(PY) -m pipeline.misura $(GIORNO)

demo: $(REGOLE)
	$(PY) -m uvicorn web.server:app --host 127.0.0.1 --port 8000

pulisci:
	rm -rf data/processed data/regole data/leggibili docs/fattibilita-dati.md docs/misura-questionario.md
