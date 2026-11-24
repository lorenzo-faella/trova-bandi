"""La folla simulata del grafico dei percorsi (decisione 104): 95 persone inventate, con proporzioni plausibili ma
approssimate (regioni pesate per abitanti; lavoro secondo l'età; famiglia, casa e ISEE coerenti con età e lavoro).
Non è un campione della popolazione: serve a far vedere come le stesse domande portano persone diverse ad aiuti diversi.
Per ognuna il motore calcola gli aiuti in vista (compatibili più possibili, come li conta la pagina) alla data indicata.
Uso: PYTHONPATH=. python prove/simulazione/folla.py [AAAA-MM-GG]   ->  web/folla_demo.json  (circa un minuto)"""
import json
import random
import sys

from web import domande as d

SEME, QUANTI = 22112026, 95
# regione -> (capoluogo, abitanti in milioni, circa)
REGIONI = {"Lombardia": ("Milano", 10.0), "Lazio": ("Roma", 5.7), "Campania": ("Napoli", 5.6), "Sicilia": ("Palermo", 4.8),
           "Veneto": ("Venezia", 4.8), "Emilia-Romagna": ("Bologna", 4.4), "Piemonte": ("Torino", 4.2),
           "Puglia": ("Bari", 3.9), "Toscana": ("Firenze", 3.7), "Calabria": ("Catanzaro", 1.8),
           "Sardegna": ("Cagliari", 1.6), "Liguria": ("Genova", 1.5), "Marche": ("Ancona", 1.5),
           "Abruzzo": ("L'Aquila", 1.3), "Friuli-Venezia Giulia": ("Trieste", 1.2),
           "Trentino-Alto Adige/Südtirol": ("Trento", 1.1), "Umbria": ("Perugia", .9), "Basilicata": ("Potenza", .5),
           "Molise": ("Campobasso", .3)}


def scegli(r, pesi):
    return r.choices(list(pesi), weights=list(pesi.values()))[0]


def persona(r):
    regione = scegli(r, {k: v[1] for k, v in REGIONI.items()})
    fascia = scegli(r, {"18-29": 18, "30-49": 33, "50-64": 27, "65+": 22})
    eta = {"18-29": r.randint(19, 29), "30-49": r.randint(30, 49), "50-64": r.randint(50, 64), "65+": r.randint(65, 86)}[fascia]
    lavoro = scegli(r, {"18-29": {"studente": 45, "dipendente": 34, "autonomo": 6, "disoccupato": 15},
                        "30-49": {"dipendente": 64, "autonomo": 17, "disoccupato": 12, "inattivo": 7},
                        "50-64": {"dipendente": 54, "autonomo": 18, "disoccupato": 11, "pensionato": 12, "inattivo": 5},
                        "65+": {"pensionato": 94, "autonomo": 6}}[fascia])
    famiglia = scegli(r, {"18-29": {"solo": 50, "coppia": 25, "figli": 20, "genitore": 5},
                          "30-49": {"solo": 20, "coppia": 15, "figli": 55, "genitore": 10},
                          "50-64": {"solo": 20, "coppia": 30, "figli": 42, "genitore": 8},
                          "65+": {"solo": 45, "coppia": 55}}[fascia])
    if lavoro == "studente":
        famiglia = "solo" if r.random() < .8 else famiglia
    affitto = r.random() < {"18-29": .7, "30-49": .4, "50-64": .25, "65+": .2}[fascia]
    reddito = {"dipendente": r.randint(14, 34) * 1000, "autonomo": r.randint(8, 40) * 1000,
               "pensionato": r.randint(8, 24) * 1000}.get(lavoro, 0)
    base = {"dipendente": 18000, "autonomo": 16000, "disoccupato": 6000, "inattivo": 7000, "studente": 14000,
            "pensionato": 12000}[lavoro]
    isee = max(1000, min(60000, round(base * r.lognormvariate(0, .55) * (.8 if famiglia in ("figli", "genitore") else 1) / 500) * 500))
    disabile = r.random() < (.15 if eta >= 65 else .05)
    nucleo = [{"eta": eta, "disabile": disabile, "svantaggio_certificato": False, "reddito_annuo": reddito,
               "attivita": "studio" if lavoro == "studente" else "tirocinio_o_lavoro" if lavoro in ("dipendente", "autonomo") else "nessuna"}]
    if famiglia in ("coppia", "figli"):
        nucleo.append({"eta": max(19, eta + r.randint(-4, 4)), "figlio": False, "disabile": False, "svantaggio_certificato": False,
                       "reddito_annuo": r.choice([0, 12000, 20000]), "attivita": r.choice(["tirocinio_o_lavoro", "nessuna"])})
    figli = []
    if famiglia in ("figli", "genitore"):
        for _ in range(r.choice([1, 1, 2, 2, 3])):
            e = r.randint(0, max(0, min(24, eta - 20)))
            figli.append(e)
            nucleo.append({"eta": e, "figlio": True, "figlio_a_carico": e < 21, "disabile": False, "svantaggio_certificato": False,
                           "reddito_annuo": 0, "attivita": "studio" if 3 <= e <= 24 else "nessuna"})
    cittadinanza = scegli(r, {"italiana": 90, "extra_ue_lungo_periodo": 7, "ue": 3})
    profilo = {
        "residente_italia": True, "regione": regione, "comune": REGIONI[regione][0], "domicilio_diverso": False,
        "anni_residenza_regione": min(eta, r.randint(3, 40)), "anni_residenza_italia": eta,
        "anni_residenza_continuativa_italia": eta, "cittadinanza": cittadinanza, "disabile": disabile,
        "condizione_lavorativa": ["occupato" if lavoro in ("dipendente", "autonomo") else lavoro],
        "reddito_richiedente": reddito, "soggetto_irpef_italia": True, "situazioni_particolari": ["nessuna"],
        "lavoro_terminato": False, "titolo_di_studio": r.choice(["diploma", "diploma", "laurea_triennale", "licenza_media"]),
        "iscrizione": "universita" if lavoro == "studente" else "nessuna",
        "abitazione": "affitto" if affitto else "proprieta", "proprieta_altra_abitazione": False,
        "isee": isee, "isee_prestazioni_familiari_2026": isee, "patrimonio_immobiliare": 0 if affitto else r.randint(60, 250) * 1000,
        "veicoli_esclusi": False, "reddito_locazione_2025": reddito, "nucleo": nucleo,
        "data_evento_figlio": "2026-05-15" if 0 in figli else "nessuno",
    }
    if cittadinanza == "extra_ue_lungo_periodo":
        profilo["mesi_validita_permesso"] = 60
    if disabile:
        profilo["percentuale_invalidita"] = r.choice([50, 75, 100])
    if lavoro in ("dipendente", "autonomo"):
        profilo.update(lavora_in_italia=True, tipo_lavoro=[lavoro], settimane_contributi_4_anni=r.randint(80, 208))
    if lavoro == "studente":
        profilo.update(livello_corso="laurea_triennale", comune_ateneo=REGIONI[regione][0], tempo_parziale=False,
                       anno_di_corso=r.randint(1, 3), fuori_corso_o_ripetente=False, crediti_conseguiti=60, isee_universitario=isee)
    if affitto:
        profilo.update(contratto_locazione_registrato=True, canone_annuo=r.randint(45, 110) * 100)
    else:
        profilo["mutuo_prima_casa"] = r.random() < .3
    return profilo


def main(giorno):
    r = random.Random(SEME)
    persone = []
    for n in range(QUANTI):
        p = persona(r)
        si, forse = d.aiuti_in_vista("persone", p, giorno)
        aiuti = len(si) + len(forse)
        persone.append({"porte": d.porte_di(p), "aiuti": aiuti, "arrivo": d.arrivo_di(aiuti)})
        print(f"{n + 1}/{QUANTI}", d.porte_di(p), aiuti, flush=True)
    d.FILE_FOLLA.write_text(json.dumps({"giorno": giorno, "seme": SEME, "persone": persone}, ensure_ascii=False, indent=0),
                            encoding="utf-8")
    print(f"{d.FILE_FOLLA.relative_to(d.ROOT)} scritto: {len(persone)} persone alla data {giorno}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-11-22")
