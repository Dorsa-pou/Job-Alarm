# 🔔 Job-Alarm-Bot

Ein Telegram-Bot, der jeden Morgen automatisch nach passenden IT-Teilzeitstellen und Praktika in der Zentralschweiz und in Bern sucht und mir neue Treffer direkt aufs Handy schickt.

Ich habe ihn für meine eigene Jobsuche neben dem Studium gebaut, damit ich nicht täglich mehrere Portale durchsuchen muss.

## Funktionen

- **Tägliche automatische Suche** über GitHub Actions, auch wenn mein Computer ausgeschaltet ist
- **Mehrere Regionen:** Luzern (+55 km) und Bern (+25 km)
- **Intelligente Filter:**
  - nur Stellen in erlaubten Kantonen (LU, ZG, SZ, NW, OW, UR, BE)
  - nur IT-Stellen (erkannt anhand von Fachbegriffen im Titel)
  - Pensum zwischen 40 und 60 % **oder** Praktikum
- **Gedächtnis:** Jede Stelle wird nur einmal gemeldet
- **Benachrichtigung per Telegram** mit Titel, Firma, Ort und Link

## So funktioniert es

```
⏰ GitHub Actions startet den Bot jeden Morgen
        ↓
🔍 Abfrage der Adzuna-API (mehrere Suchbegriffe und Orte)
        ↓
🧹 Filtern nach Region, Fachgebiet und Pensum
        ↓
📓 Abgleich mit bereits gesendeten Stellen (gesendet.json)
        ↓
📱 Versand neuer Stellen über die Telegram-Bot-API
        ↓
💾 Gedächtnis wird ins Repository zurückgeschrieben
```

## Technologien

- **Python 3** mit `requests` und `python-dotenv`
- **Adzuna-API**: Abruf von Stellenangeboten (REST, JSON)
- **Telegram-Bot-API**: Versand von Nachrichten
- **GitHub Actions**: zeitgesteuerte Ausführung in der Cloud
- **GitHub Secrets**: sichere Speicherung der Zugangsdaten
- **Git & GitHub**: Versionskontrolle

## Herausforderungen und Lösungen

**Ungenaue Suchergebnisse**
Die API liefert viele unpassende Treffer (falscher Ort, keine IT-Stelle, Vollzeit). Lösung: breit suchen und anschliessend mit eigenen Filterfunktionen genau aussortieren. Jeder Filter ist eine eigene Funktion mit einer klaren Aufgabe.

**Pensum richtig erkennen**
Ein erster Filter hat alle Titel mit „100%“ ausgeschlossen. Über eine Debug-Ausgabe habe ich gemerkt, dass dadurch auch passende Stellen wie „ICT-Supporter 60–100%“ verloren gingen. Lösung: Mit regulären Ausdrücken wird die Pensum-Spanne aus dem Titel gelesen und geprüft, ob sie sich mit 40–60 % überschneidet.

**„IT“ als Wort erkennen**
Eine einfache Textsuche nach „it“ hätte auch Wörter wie „Mitarbeiter“ gefunden. Lösung: der reguläre Ausdruck `\bIT\b`, der nur das eigenständige Wort erkennt.

**Doppelte Treffer**
Dieselbe Stelle erscheint bei mehreren Suchbegriffen. Lösung: Speicherung in einem Dictionary mit der Stellen-ID als Schlüssel, wodurch Duplikate automatisch entfallen.

**Gedächtnis in der Cloud**
Der Cloud-Computer von GitHub Actions wird nach jedem Lauf gelöscht. Lösung: Die IDs bereits gesendeter Stellen werden in `gesendet.json` gespeichert und vom Workflow automatisch ins Repository committet.

**Sichere Zugangsdaten**
Das Repository ist öffentlich, die API-Schlüssel dürfen aber nicht sichtbar sein. Lösung: lokal in einer `.env`-Datei (durch `.gitignore` ausgeschlossen), in der Cloud als GitHub Secrets. Derselbe Code funktioniert in beiden Umgebungen.

## Projektstruktur

```
Job_Alarm.py                     Hauptprogramm
test_adzuna.py                   Testskript mit Debug-Ausgabe zum Anpassen der Filter
bot.py                           Erster Test der Telegram-Verbindung
gesendet.json                    Gedächtnis: IDs bereits gesendeter Stellen
requirements.txt                 Benötigte Python-Bibliotheken
.github/workflows/job-alarm.yml  Zeitplan und Ablauf für GitHub Actions
```

## Lokal ausführen

1. Repository herunterladen
2. Bibliotheken installieren: `pip install -r requirements.txt`
3. Eine Datei `.env` mit eigenen Zugangsdaten erstellen:

```
TELEGRAM_TOKEN=...
CHAT_ID=...
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...
```

4. Starten: `python Job_Alarm.py`

## Was ich gelernt habe

- Mit REST-APIs arbeiten und JSON-Daten verarbeiten
- Daten filtern und bereinigen
- Ein Programm modular in Funktionen aufbauen
- Fehler systematisch finden: Debug-Ausgaben, Tracebacks und Cloud-Logs lesen
- Zugangsdaten sicher verwalten
- Abläufe mit GitHub Actions automatisieren

## Über mich

**Dorsa Pourmoghaddam** - Studentin BSc Artificial Intelligence & Machine Learning an der Hochschule Luzern
