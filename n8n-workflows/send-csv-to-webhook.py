#!/usr/bin/env python3
"""
CSV aus Instant Data Scraper an den n8n Webhook senden.

Verwendung:
    python3 send-csv-to-webhook.py deine-datei.csv

Vorher anpassen:
    WEBHOOK_URL = Deine n8n Webhook-URL
"""

import csv
import json
import sys
import requests

# === HIER ANPASSEN ===
WEBHOOK_URL = "https://deine-n8n-url.com/webhook/google-maps-leads"
# =====================


def read_csv(filepath):
    """CSV-Datei einlesen und als Liste von Dicts zurückgeben."""
    leads = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Leere Werte filtern
            clean_row = {k: v.strip() for k, v in row.items() if v and v.strip()}
            if clean_row:
                leads.append(clean_row)
    return leads


def send_to_webhook(leads):
    """Leads an den n8n Webhook senden."""
    payload = {"body": leads}

    print(f"Sende {len(leads)} Leads an n8n...")

    response = requests.post(
        WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        print(f"Erfolgreich! {len(leads)} Leads gesendet.")
        try:
            print(f"Antwort: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except Exception:
            print(f"Antwort: {response.text}")
    else:
        print(f"Fehler! Status: {response.status_code}")
        print(f"Antwort: {response.text}")


def main():
    if len(sys.argv) < 2:
        print("Verwendung: python3 send-csv-to-webhook.py <csv-datei>")
        print("Beispiel:   python3 send-csv-to-webhook.py google_maps_doener_berlin.csv")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        leads = read_csv(filepath)
    except FileNotFoundError:
        print(f"Datei nicht gefunden: {filepath}")
        sys.exit(1)

    if not leads:
        print("Keine Daten in der CSV gefunden.")
        sys.exit(1)

    print(f"\nGefunden: {len(leads)} Einträge")
    print(f"Spalten: {', '.join(leads[0].keys())}")
    print(f"Erster Eintrag: {json.dumps(leads[0], indent=2, ensure_ascii=False)}\n")

    send_to_webhook(leads)


if __name__ == "__main__":
    main()
