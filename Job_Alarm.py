import os
import re
import json
import requests
from dotenv import load_dotenv

# ==========================================
# 1. Schlüssel aus der .env laden
# ==========================================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/ch/search/1"
GEDAECHTNIS_DATEI = "gesendet.json"

# ==========================================
# 2. Einstellungen
# ==========================================
ORTE = [
    ("Luzern", 55),
    ("Bern", 25),
]

SUCHBEGRIFFE = [
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
PRAKTIKUM_WOERTER = ["praktikum", "praktikant", "internship"]

MIN_PENSUM = 40
MAX_PENSUM = 60


# ==========================================
# 3. Filter-Funktionen
# ==========================================
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
    """Gibt (kleinstes, grösstes) Pensum aus dem Titel zurück, oder None."""
    angaben = re.findall(r"\d{2,3}(?:\s*[-–]\s*\d{2,3})?\s*%", titel)
    zahlen = []
    for angabe in angaben:
        for zahl in re.findall(r"\d{2,3}", angabe):
            zahlen.append(int(zahl))
    if len(zahlen) == 0:
        return None
    return (min(zahlen), max(zahlen))


def ist_passend(job):
    """Prüft alle Filter. Gibt True zurück, wenn die Stelle zu dir passt."""
    if not ist_in_erlaubter_region(job):
        return False
    if not ist_it_stelle(job):
        return False
    if hat_ausschluss_wort(job):
        return False
    if ist_praktikum(job):
        return True

    bereich = pensum_bereich(job["title"])
    if bereich is None:
        return False
    kleinste, groesste = bereich
    return kleinste <= MAX_PENSUM and groesste >= MIN_PENSUM


# ==========================================
# 4. Stellen bei Adzuna suchen
# ==========================================
def stellen_suchen():
    alle_jobs = {}
    for ort, umkreis in ORTE:
        for begriff in SUCHBEGRIFFE:
            parameter = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "what": begriff,
                "where": ort,
                "distance": umkreis,
                "results_per_page": 50,
            }
            antwort = requests.get(ADZUNA_URL, params=parameter)
            if antwort.status_code != 200:
                print(f"Fehler bei '{begriff}' in {ort}: {antwort.status_code}")
                continue
            for job in antwort.json()["results"]:
                alle_jobs[job["id"]] = job
    return list(alle_jobs.values())


# ==========================================
# 5. Gedächtnis: schon gesendete Stellen
# ==========================================
def gedaechtnis_laden():
    """Liest die IDs der schon gesendeten Stellen aus der Datei."""
    if not os.path.exists(GEDAECHTNIS_DATEI):
        return set()
    with open(GEDAECHTNIS_DATEI, "r", encoding="utf-8") as datei:
        return set(json.load(datei))


def gedaechtnis_speichern(ids):
    """Schreibt alle gesendeten IDs in die Datei."""
    with open(GEDAECHTNIS_DATEI, "w", encoding="utf-8") as datei:
        json.dump(sorted(ids), datei, indent=2)


# ==========================================
# 6. Telegram-Nachricht senden
# ==========================================
def nachricht_senden(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    daten = {"chat_id": CHAT_ID, "text": text}
    antwort = requests.post(url, data=daten)
    if antwort.status_code != 200:
        print("Telegram-Fehler:", antwort.text)


def job_als_text(job):
    """Macht aus einer Stelle eine schöne Nachricht."""
    firma = job.get("company", {}).get("display_name", "Unbekannt")
    ort = job.get("location", {}).get("display_name", "Unbekannt")
    return (
        f"📌 {job['title']}\n"
        f"🏢 {firma}\n"
        f"📍 {ort}\n"
        f"🔗 {job['redirect_url']}"
    )


# ==========================================
# 7. Hauptprogramm
# ==========================================
def main():
    print("Suche Stellen...")
    alle_jobs = stellen_suchen()
    schon_gesendet = gedaechtnis_laden()

    neue_jobs = []
    for job in alle_jobs:
        if ist_passend(job) and job["id"] not in schon_gesendet:
            neue_jobs.append(job)

    print(f"{len(alle_jobs)} gefunden, {len(neue_jobs)} neue passende.")

    if len(neue_jobs) == 0:
        nachricht_senden("🔍 Job-Alarm: Heute keine neuen passenden Stellen.")
        return

    nachricht_senden(f"🔔 Job-Alarm: {len(neue_jobs)} neue Stellen!")
    for job in neue_jobs:
        nachricht_senden(job_als_text(job))
        schon_gesendet.add(job["id"])

    gedaechtnis_speichern(schon_gesendet)
    print("Nachrichten gesendet und gemerkt! ✅")


main()