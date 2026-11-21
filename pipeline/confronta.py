"""Confronto tra regole estratte e regole di riferimento -> docs/test-estrazione.md o il file indicato (generato).

Due misure, perché una sola inganna:
- struttura: le condizioni elementari coincidono? Due regole scritte in modo diverso possono però essere equivalenti.
- comportamento: sulle stesse persone fittizie danno lo stesso esito? È ciò che conta per chi usa il servizio.

Il comportamento si misura sui casi non banali: se entrambe le regole dicono "non idoneo" il caso non conta, altrimenti
una regola che esclude sempre tutti sembrerebbe quasi perfetta (la maggior parte dei profili casuali non ha i requisiti).

Si confrontano solo i benefici presenti in entrambe le cartelle; un'etichetta ancora da compilare (`requisiti: []`) non
conta. Con due cartelle di etichette (Lorenzo contro Edoardo) misura l'accordo tra persone: il tetto realistico.

Uso: python -m pipeline.confronta <cartella estratte> <cartella riferimento> [<file di uscita> [<titolo> [<anno di valutazione>]]]
"""
import random
import sys
import time
from collections import Counter
from pathlib import Path

import yaml

from pipeline.citazioni import nodi, soglie_non_trovate
from pipeline.motore import DA_VERIFICARE, IDONEO, IDONEO_SALVO, MANCANO_DATI, NON_IDONEO, tutti, valuta, verifica
from pipeline.regole import LOADER, ROOT
from pipeline.sospette import testi_fonte

# Su questi campi "< 18" e "<= 17" sono la stessa condizione. Sugli euro no.
INTERI = {"eta", "anni_residenza_italia", "anni_residenza_continuativa_italia", "settimane_contributi_4_anni",
          "giorni_da_evento_figlio", "mesi_da_evento_figlio", "giorni_da_cessazione_lavoro",
          "anni_residenza_regione", "numero_figli", "anno_di_corso", "crediti_conseguiti", "percentuale_invalidita",
          "mesi_validita_permesso"}
ALTRO = "__altro__"  # un valore che nessun elenco contiene


def chiave(n):
    """La condizione in forma confrontabile."""
    campo, op = n["campo"], n["operatore"]
    if "valori" in n:
        return campo, op, tuple(sorted(n["valori"]))
    v = n.get("valore")
    if isinstance(v, list):
        return campo, op, tuple(v)
    if campo in INTERI and op == "<":
        return campo, "<=", v - 1
    if campo in INTERI and op == ">":
        return campo, ">=", v + 1
    return campo, op, v


def foglie(regola):
    """Le condizioni elementari, senza doppioni: l'ADI ripete la stessa esenzione in cinque requisiti."""
    return {chiave(n) for req in regola["requisiti"] for n in nodi(req) if "campo" in n}


def non_modellabili(regola):
    return sum("non_modellabile" in n for req in regola["requisiti"] for n in nodi(req))


def struttura(riferimento, estratta):
    rif, est = foglie(riferimento), foglie(estratta)
    campi_rif, campi_est = {k[0] for k in rif}, {k[0] for k in est}
    giuste = rif & est
    return {
        "giuste": giuste,
        "sbagliate": {k for k in est - rif if k[0] in campi_rif},  # campo giusto, soglia o valori diversi
        "in_piu": {k for k in est - rif if k[0] not in campi_rif},
        "mancate": {k for k in rif - est if k[0] not in campi_est},
        "diverse_nel_riferimento": {k for k in rif - est if k[0] in campi_est},
        "precisione": len(giuste) / len(est) if est else None,
        "richiamo": len(giuste) / len(rif) if rif else None,
        "non_modellabili": (non_modellabili(riferimento), non_modellabili(estratta)),
    }


def raccogli(req, componente, out):
    if "campo" in req:
        out[componente].setdefault(req["campo"], []).append(req)
    dentro = componente or "almeno_un_componente" in req
    for q in req.get("almeno_uno_di") or req.get("tutti_di") or req.get("almeno_un_componente") or []:
        raccogli(q, dentro, out)


def valori_di_prova(n):
    """(valori che soddisfano la condizione, valori che non la soddisfano), a ridosso delle soglie."""
    op = n["operatore"]
    if op == "vero":
        return [True], [False]
    if op == "falso":
        return [False], [True]
    if op == "in":
        return list(n["valori"]), [ALTRO]
    if op == "interseca":
        return [[v] for v in n["valori"]], [[ALTRO]]
    if op == "prefisso":
        return list(n["valori"]), ["00"]
    v = n["valore"]
    if op == "<=":
        return [v], [v + 1]
    if op == "<":
        return [v - 1], [v]
    if op == ">=":
        return [v], [v - 1]
    if op == ">":
        return [v + 1], [v]
    return [v[0], v[1]], [v[0] - 1, v[1] + 1]  # tra


def rendi_vera(req, p, rng):
    """Assegna i campi ancora liberi perché il requisito sia vero. Le alternative non scelte vengono rese false:
    se fossero vere anche loro, un errore nell'alternativa scelta non si vedrebbe mai."""
    if "campo" in req:
        p.setdefault(req["campo"], rng.choice(valori_di_prova(req)[0]))
    elif "tutti_di" in req:
        for q in req["tutti_di"]:
            rendi_vera(q, p, rng)
    elif "almeno_uno_di" in req:
        scelta = rng.choice([q for q in req["almeno_uno_di"] if verifica(q, p) is not False] or req["almeno_uno_di"])
        rendi_vera(scelta, p, rng)
        for q in req["almeno_uno_di"]:
            if q is not scelta:
                rendi_falsa(q, p, rng)
    elif "almeno_un_componente" in req:
        nucleo = p.setdefault("nucleo", [])
        libero = next((c for c in nucleo if tutti(verifica(q, c) for q in req["almeno_un_componente"]) is not False), None)
        if libero is None:
            libero = {}
            nucleo.append(libero)
        for q in req["almeno_un_componente"]:
            rendi_vera(q, libero, rng)


def rendi_falsa(req, p, rng):
    if "campo" in req:
        p.setdefault(req["campo"], rng.choice(valori_di_prova(req)[1]))
    elif "tutti_di" in req:
        rendi_falsa(rng.choice(req["tutti_di"]), p, rng)
    elif "almeno_uno_di" in req:
        for q in req["almeno_uno_di"]:
            rendi_falsa(q, p, rng)
    elif "almeno_un_componente" in req:
        nucleo = p.setdefault("nucleo", [])
        if not nucleo:
            nucleo.append({})
        for c in nucleo:
            rendi_falsa(rng.choice(req["almeno_un_componente"]), c, rng)


LAVORI = ["dipendente", "autonomo", "parasubordinato"]
NON_OCCUPATO = ["disoccupato", "studente", "pensionato", "inattivo"]


def intero(v):
    return isinstance(v, int) and not isinstance(v, bool)


def rendi_coerente(p, rng):
    """Toglie le combinazioni che nessuna persona reale può avere, perché il confronto conti solo differenze vere
    (decisione 63). Ogni campo è scelto per provare una soglia; quando due campi dicono la stessa cosa in modi diversi
    se ne tiene uno a caso e l'altro si ricava, così le soglie di entrambi restano provate.

    - Lavoro: `tipo_lavoro` e `lavora_in_italia: vero` hanno senso solo per chi è occupato (nel questionario si
      chiedono solo a lui).
    - Figli: giorni e mesi dall'ultima nascita o adozione vengono dalla stessa data, e l'età del figlio più giovane è
      quella che corrisponde ai mesi (si assume una nascita: per le adozioni l'età può essere maggiore).
    """
    cond, tipo = p.get("condizione_lavorativa"), p.get("tipo_lavoro")
    if tipo is not None and cond is not None and (tipo in LAVORI) != (cond == "occupato"):
        if rng.random() < 0.5:
            p["condizione_lavorativa"] = "occupato" if tipo in LAVORI else rng.choice(NON_OCCUPATO)
        else:
            p["tipo_lavoro"] = rng.choice(LAVORI) if cond == "occupato" else ALTRO
    cond = p.get("condizione_lavorativa")
    if p.get("lavora_in_italia") is True and cond is not None and cond != "occupato":
        if rng.random() < 0.5:
            p["condizione_lavorativa"] = "occupato"
            if p.get("tipo_lavoro") not in (None, *LAVORI):
                p["tipo_lavoro"] = rng.choice(LAVORI)
        else:
            p["lavora_in_italia"] = False

    giorni, mesi = p.get("giorni_da_evento_figlio"), p.get("mesi_da_evento_figlio")
    figli = [c for c in p.get("nucleo") or [] if c.get("figlio") is True and intero(c.get("eta"))]
    fonti = [k for k, v in (("giorni", giorni), ("mesi", mesi)) if intero(v)] + (["eta"] if figli else [])
    if len(fonti) < 2:
        return
    primo = rng.choice(fonti)
    if primo == "giorni":
        m = giorni * 12 * 100 // 36525
    elif primo == "mesi":
        m = mesi
    else:
        m = min(c["eta"] for c in figli) * 12 + rng.randrange(12)
    if m < 0 or m >= 12 * 30:  # nessun evento recente (o un valore fuori scala): niente da allineare
        return
    if intero(giorni) and primo != "giorni":
        p["giorni_da_evento_figlio"] = (m * 36525 + 1199) // 1200 + rng.randrange(28)
    if intero(mesi):
        p["mesi_da_evento_figlio"] = m
    if figli:
        anni = m // 12
        for c in figli:
            if c["eta"] < anni:
                c["eta"] = anni
        min(figli, key=lambda c: c["eta"])["eta"] = anni


def persone(regole, n, seed=0, ignoto=0.03, anno_valutazione=None):
    """Profili che esercitano le regole: si parte da chi le soddisfa e si spostano pochi valori a ridosso delle soglie.
    Con valori indipendenti si arriverebbe di rado oltre il primo no, e mai a provare un'alternativa da sola."""
    rng = random.Random(seed)
    condizioni = {False: {}, True: {}}
    for r in regole:
        for req in r["requisiti"]:
            raccogli(req, False, condizioni)
    richiedente, componente = [sorted(condizioni[k].items(), key=lambda x: x[0]) for k in (False, True)]
    for _ in range(n):
        p = {} if anno_valutazione is None else {"_anno_valutazione": anno_valutazione}
        for r in regole:
            for req in rng.sample(r["requisiti"], len(r["requisiti"])):
                rendi_vera(req, p, rng)
        if componente:
            p.setdefault("nucleo", [])
            if rng.random() < 0.2:
                p["nucleo"].append({})
        for dove, elenco in ((p, richiedente), *((c, componente) for c in p.get("nucleo", []))):
            for campo, ns in elenco:  # i campi non toccati: un dato assente qui darebbe "mancano dati" per caso
                si, no = valori_di_prova(rng.choice(ns))
                dove.setdefault(campo, rng.choice(si + no))
        for _ in range(rng.choice([0, 1, 1, 2, 3])):  # gli spostamenti
            dove, elenco = rng.choice([(p, richiedente)] * 2 + [(c, componente) for c in p.get("nucleo", [])])
            if elenco:
                campo, ns = rng.choice(elenco)
                si, no = valori_di_prova(rng.choice(ns))
                dove[campo] = rng.choice(si + no)
        rendi_coerente(p, rng)
        for dove in (p, *p.get("nucleo", [])):
            for campo in [c for c in dove if c not in {"nucleo", "_anno_valutazione"} and rng.random() < ignoto]:
                del dove[campo]
        if rng.random() < ignoto:
            p.pop("nucleo", None)
        elif componente and rng.random() < 0.05:
            p["nucleo"] = []
        yield p


def comportamento(riferimento, estratta, n=5000, seed=0, anno_valutazione=None):
    coppie = Counter((valuta(riferimento, p).stato, valuta(estratta, p).stato)
                     for p in persone([riferimento, estratta], n, seed, anno_valutazione=anno_valutazione))
    non_banali = {k: c for k, c in coppie.items() if k != (NON_IDONEO, NON_IDONEO)}
    tot = sum(non_banali.values())
    possibile = {IDONEO, IDONEO_SALVO, DA_VERIFICARE}
    # Dal più sicuro al più cauto: un passo verso "idoneo" senza che il riferimento lo faccia è troppa sicurezza.
    grado = {IDONEO: 0, IDONEO_SALVO: 1, DA_VERIFICARE: 2}
    return {
        "profili": n,
        "non_banali": tot,
        "accordo": sum(c for (a, b), c in non_banali.items() if a == b) / tot if tot else None,
        # dice "puoi averne diritto" a chi non ce l'ha
        "falsi_si": sum(c for (a, b), c in non_banali.items() if a == NON_IDONEO and b in possibile),
        # esclude chi poteva averne diritto: l'errore peggiore, perché la persona non controlla oltre
        "falsi_no": sum(c for (a, b), c in non_banali.items() if a in possibile and b == NON_IDONEO),
        # meno riserve del riferimento: "idoneo" dove chiede di verificare, o un'eccezione segnata rara che non lo è
        "troppo_sicura": sum(c for (a, b), c in non_banali.items() if a in grado and b in grado and grado[b] < grado[a]),
        # il contrario: nessuna decisione opposta, ma una persona in più deve controllare da sé
        "piu_cauta": sum(c for (a, b), c in non_banali.items() if a in grado and b in grado and grado[b] > grado[a]),
        # i falsi sì dovuti a un'eccezione segnata rara: è il rischio della decisione 52
        "falsi_si_da_rare": non_banali.get((NON_IDONEO, IDONEO_SALVO), 0),
        "dati_diversi": sum(c for (a, b), c in non_banali.items() if a != b and MANCANO_DATI in (a, b)),
    }


def leggi(cartella):
    return {r["id"]: r for r in (yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER)
                                 for f in sorted(Path(cartella).glob("*.yaml")))}


def compilate(cartella):
    """Le regole della cartella, senza le etichette ancora da compilare (`requisiti: []`): non dicono niente e
    falserebbero il confronto. Una regola estratta vuota invece conta (dice che il beneficio non ha requisiti)."""
    regole = {}
    for c in str(cartella).split(","):  # più cartelle insieme: "a,b"
        regole.update(leggi(c))
    if "regole_estratte" in str(cartella):
        return regole
    return {i: r for i, r in regole.items() if r["requisiti"]}


def pct(x):
    return "n/d" if x is None else f"{100 * x:.0f}%"


def scrivi(k):
    return f"`{k[0]} {k[1]} {k[2]}`" if k[2] is not None else f"`{k[0]} {k[1]}`"


def main(dir_estratte, dir_riferimento, uscita=None, titolo=None, anno_valutazione=None):
    anno_valutazione = int(anno_valutazione) if anno_valutazione is not None else None
    testo = testi_fonte()
    estratte, riferimento = compilate(dir_estratte), compilate(dir_riferimento)
    comuni = sorted(set(estratte) & set(riferimento))
    if not comuni:
        print(f"nessuna regola compilata in comune tra {dir_estratte} e {dir_riferimento}: niente da confrontare")
        return
    tra_etichette = "regole_estratte" not in str(dir_estratte)
    righe = [
        f"# {titolo}" if titolo else "# Accordo tra etichette" if tra_etichette else "# Test dell'estrazione",
        "",
        f"*Generato da `pipeline/confronta.py` il {time.strftime('%Y-%m-%d')}: non modificare a mano.*",
        "",
        f"Regole {'' if tra_etichette else 'estratte '}in `{Path(dir_estratte).as_posix()}`, confrontate con `{Path(dir_riferimento).as_posix()}`"
        f" ({len(comuni)} benefici in comune).",
        "",
        f"Anno di valutazione delle soglie annuali: {anno_valutazione if anno_valutazione is not None else 'non specificato; i vincoli annuali restano da verificare'}.",
        *(["", "**Non è la misura finale.** I 5 benefici di sviluppo hanno un riferimento scritto da Claude e sono serviti a provare l'estrattore: vedi `docs/decisioni.md`, decisione 29. La misura vera sarà sulle etichette a mano in `data/gold/`."]
          if "sviluppo" in str(dir_estratte) else []),
        "",
        "| beneficio | foglie coincidenti | precisione delle foglie | richiamo delle foglie | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | divergenze favorevoli | divergenze sfavorevoli | casi non banali |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    tot = Counter()
    dettagli = []
    for i in comuni:
        s, c = struttura(riferimento[i], estratte[i]), comportamento(riferimento[i], estratte[i], anno_valutazione=anno_valutazione)
        nb = c["non_banali"] or 1
        righe.append(f"| {riferimento[i]['titolo']} | {len(s['giuste'])}/{len(foglie(riferimento[i]))} | {pct(s['precisione'])} "
                     f"| {pct(s['richiamo'])} | {s['non_modellabili'][0]}/{s['non_modellabili'][1]} | {pct(c['accordo'])} "
                     f"| {pct(c['piu_cauta'] / nb)} | {pct(c['falsi_si'] / nb)} | {pct(c['falsi_no'] / nb)} | {c['non_banali']} |")
        tot.update(giuste=len(s["giuste"]), estratte=len(foglie(estratte[i])), rif=len(foglie(riferimento[i])),
                   nb=c["non_banali"], si=c["falsi_si"], no=c["falsi_no"], cauta=c["piu_cauta"],
                   uguali=round((c["accordo"] or 0) * c["non_banali"]))
        dettagli += [f"### {riferimento[i]['titolo']}", ""]
        for nome, chiavi in (("Sbagliate (campo giusto, valore diverso)", s["sbagliate"]),
                             ("Nel riferimento, scritte in modo diverso", s["diverse_nel_riferimento"]),
                             ("In più (campo assente dal riferimento)", s["in_piu"]),
                             ("Mancate (campo assente dall'estrazione)", s["mancate"])):
            if chiavi:
                dettagli.append(f"- {nome}: " + ", ".join(sorted(scrivi(k) for k in chiavi)))
        sospette = soglie_non_trovate(estratte[i], testo(estratte[i]))
        if sospette:
            dettagli.append("- Soglie che non compaiono nella scheda, da rileggere: " + ", ".join(f"`{x}`" for x in sospette))
        if c["troppo_sicura"]:
            dettagli.append(f"- Più sicura del riferimento in {c['troppo_sicura']} casi su {c['non_banali']}"
                            + (f", di cui {c['falsi_si_da_rare']} falsi sì dovuti a un'eccezione segnata rara"
                               if c["falsi_si_da_rare"] else "") + ".")
        if dettagli[-1] == "":
            dettagli.append("- Nessuna differenza strutturale.")
        dettagli.append("")
    righe += [
        f"| **Totale** | **{tot['giuste']}/{tot['rif']}** | **{pct(tot['giuste'] / tot['estratte'] if tot['estratte'] else None)}** "
        f"| **{pct(tot['giuste'] / tot['rif'] if tot['rif'] else None)}** | | "
        f"**{pct(tot['uguali'] / tot['nb'] if tot['nb'] else None)}** | **{pct(tot['cauta'] / tot['nb'] if tot['nb'] else None)}** | **{pct(tot['si'] / tot['nb'] if tot['nb'] else None)}** "
        f"| **{pct(tot['no'] / tot['nb'] if tot['nb'] else None)}** | **{tot['nb']}** |",
        "",
        "- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.",
        "- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.",
        "- **Più cauta:** più riserve rispetto al riferimento. **Divergenza favorevole:** estrazione idonea, salvo eccezioni o da verificare contro riferimento non idoneo; **sfavorevole:** il contrario. I contatori interni storici si chiamano falsi_si/falsi_no: senza adjudicazione questi non sono errori normativi dimostrati.",
        "- Il riferimento umano non è condiviso e stabile: occorre leggere fonti complete e allegati e risolvere i disaccordi. Non è accuratezza sui cittadini; il complemento dell'accordo non è una percentuale di errori reali. Accordo fra LLM, coincidenza delle foglie e correttezza dell'esito sono misure distinte.",
        "- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.",
        "",
        "## Differenze per beneficio",
        "",
    ] + dettagli
    out = Path(uscita) if uscita else ROOT / "docs" / "test-estrazione.md"
    out = out if out.is_absolute() else Path.cwd() / out
    out.write_text("\n".join(righe).rstrip() + "\n", encoding="utf-8")
    nome = out.resolve().relative_to(ROOT) if out.resolve().is_relative_to(ROOT) else out
    print(f"{nome} scritto: {len(comuni)} regole confrontate")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4, 5, 6):
        sys.exit(__doc__)
    main(*sys.argv[1:])
