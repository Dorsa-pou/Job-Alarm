import os
import requests
from dotenv import load_dotenv

# 1. Geheimnisse aus der .env-Datei laden
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# 2. Funktion: schickt eine Nachricht an Telegram
def nachricht_senden(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    daten = {"chat_id": CHAT_ID, "text": text}
    antwort = requests.post(url, data=daten)

    if antwort.status_code == 200:
        print("Nachricht gesendet! ✅")
    else:
        print("Fehler:", antwort.text)


# 3. Programm starten
nachricht_senden("Hallo! 👋 Dein Job-Alarm-Bot funktioniert.")