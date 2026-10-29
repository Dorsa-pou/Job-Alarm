import os
import re
import requests
from dotenv import load_dotenv

# 1. Schlüssel aus der .env laden
load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

URL = "https://api.adzuna.com/v1/api/jobs/ch/search/1"

# 2. Unsere Einstellungen
ORTE = [
    ("Luzern", 55),
    ("Bern", 25),
]

suchbegriffe = [
    "Werkstudent",
    "Werkstudentin",
    "Praktikum",
    "Informatik",
    "Software",
    "ICT",
]

KANTONE = ["Luzern", "Lucerne", "Zug", "Schwyz", "Nidwalden", "Obwalden", "Uri", "Bern", "Berne"]

IT_WOERTER = [
    "informatik", "software", "developer", "entwickler", "data", "daten",
    "system", "support", "web", "machine learning", "applikation",
    "cloud", "netzwerk", "cyber", "devops", "programm", "ict",
]

AUSSCHLUSS_WOERTER = ["sales", "verkauf", "business development"]

# Diese Stellen werden immer angezeigt, egal welches Pensum
PRAKTIKUM_WOERTER = ["praktikum", "praktikant", "internship"]

# Gewünschtes Pensum in Prozent
MIN_PENSUM = 40
MAX_PENSUM = 60

DEBUG = False  # True = zeigt auch aussortierte Stellen mit Grund an


# 3. Filter-Funktionen
def ist_in_erlaubter_region(job):
    ort = job.get("location", {})
    ort_text = ort.get("display_name", "") + " " + " ".join(ort.get("area", []))
    for kanton in KANTONE:
        if kanton in ort_text:
            return True
    return False


def ist_it_stelle(job):
    titel = job["title"]
    if re.search(r"\bIT\b", titel):
        return True
    for wort in IT_WOERTER:
        if wort in titel.lower():
            return True
    return False


def hat_ausschluss_wort(job):
    titel = job["title"].lower()
    for wort in AUSSCHLUSS_WOERTER:
        if wort in titel:
            return True
    return False


def ist_praktikum(job):
    titel = job["title"].lower()
    for wort in PRAKTIKUM_WOERTER:
        if wort in titel:
            return True
    return False


def pensum_bereich(titel):
    """Findet Prozentangaben wie '60%' oder '60-100%' im Titel.
    Gibt (kleinste Zahl, grösste Zahl) zurück, oder None, wenn kein Pensum steht."""
    angaben = re.findall(r"\d{2,3}(?:\s*[-–]\s*\d{2,3})?\s*%", titel)
    zahlen = []
    for angabe in angaben:
        for zahl in re.findall(r"\d{2,3}", angabe):
            zahlen.append(int(zahl))
    if len(zahlen) == 0:
        return None
    return (min(zahlen), max(zahlen))


def grund_fuer_ausschluss(job):
    """Gibt zurück, warum eine Stelle nicht passt (oder None, wenn sie passt)."""
    if not ist_in_erlaubter_region(job):
        return "Ort nicht erlaubt"
    if not ist_it_stelle(job):
        return "Keine IT-Stelle"
    if hat_ausschluss_wort(job):
        return "Ausschluss-Wort im Titel"

    # Praktikum: immer anzeigen
    if ist_praktikum(job):
        return None

    # Sonst: Pensum muss sich mit 40-60% überschneiden
    bereich = pensum_bereich(job["title"])
    if bereich is None:
        return "Kein Pensum angegeben (und kein Praktikum)"

    kleinste, groesste = bereich
    if kleinste <= MAX_PENSUM and groesste >= MIN_PENSUM:
        return None
    return f"Pensum passt nicht ({kleinste}-{groesste}%)"


# 4. Alle Orte und Suchbegriffe abfragen
alle_jobs = {}

for ort, umkreis in ORTE:
    print(f"--- Suche in {ort} (+{umkreis} km) ---")

    for begriff in suchbegriffe:
        parameter = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "what": begriff,
            "where": ort,
            "distance": umkreis,
            "results_per_page": 50,
        }
        antwort = requests.get(URL, params=parameter)

        if antwort.status_code != 200:
            print(f"Fehler bei '{begriff}': Status {antwort.status_code}")
            print(antwort.text)
            continue

        daten = antwort.json()
        print(f"'{begriff}': {daten['count']} Treffer")

        for job in daten["results"]:
            alle_jobs[job["id"]] = job

# 5. Filtern
passende_jobs = []
aussortierte_jobs = []

for job in alle_jobs.values():
    grund = grund_fuer_ausschluss(job)
    if grund is None:
        passende_jobs.append(job)
    else:
        aussortierte_jobs.append((job, grund))

print()
print("Verschiedene Stellen gefunden:", len(alle_jobs))
print("Davon passend für dich:       ", len(passende_jobs))
print()

# 6. Passende Stellen anzeigen
print("========== PASSENDE STELLEN ==========")
for job in passende_jobs:
    firma = job.get("company", {}).get("display_name", "Unbekannt")
    ort = job.get("location", {}).get("display_name", "Unbekannt")
    print("📌", job["title"])
    print("   Firma:", firma)
    print("   Ort:  ", ort)
    print("   Link: ", job["redirect_url"])
    print()

# 7. Debug: aussortierte Stellen mit Grund anzeigen
if DEBUG:
    print("========== AUSSORTIERT (Debug) ==========")
    for job, grund in aussortierte_jobs:
        ort = job.get("location", {})
        print("❌", job["title"])
        print("   Grund:", grund)
        print("   Ort:  ", ort.get("display_name", "?"), "|", ort.get("area", []))
        print()