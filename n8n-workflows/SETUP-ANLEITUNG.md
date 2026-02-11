# Google Maps Leads → HubSpot | Einrichtungsanleitung

## Übersicht

Dieser n8n-Workflow importiert Geschäftsdaten aus Google Maps (via Instant Data Scraper) automatisch in HubSpot CRM.

**Ablauf:**
```
Google Maps → Instant Data Scraper (CSV) → Webhook → n8n → Duplikat-Check → HubSpot (Firma + Kontakt)
```

---

## Voraussetzungen

- n8n (Cloud oder Self-hosted)
- HubSpot Account mit API-Zugang
- Chrome mit [Instant Data Scraper](https://chrome.google.com/webstore/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah) Extension
- Tool zum Senden von HTTP-Requests (z.B. Postman, curl, oder ein weiterer n8n-Workflow)

---

## Schritt 1: HubSpot API Key erstellen

1. Gehe zu [HubSpot](https://app.hubspot.com) → Einstellungen (Zahnrad oben rechts)
2. Links: **Integrationen → Private Apps**
3. Klick **Private App erstellen**
4. Name: `n8n Lead Import`
5. Unter **Scopes** diese Berechtigungen aktivieren:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.companies.read`
   - `crm.objects.companies.write`
6. **App erstellen** klicken → Access Token kopieren

---

## Schritt 2: n8n Workflow importieren

1. Öffne n8n
2. Klick **Workflows → Import from File**
3. Wähle die Datei `google-maps-leads-to-hubspot.json`
4. Der Workflow wird mit allen Nodes geladen

---

## Schritt 3: HubSpot Credentials in n8n einrichten

1. In n8n: **Settings → Credentials → Add Credential**
2. Suche nach **HubSpot API**
3. Füge den Access Token aus Schritt 1 ein
4. Speichern
5. Öffne den Workflow → klick auf jeden HubSpot-Node → wähle die neue Credential aus

---

## Schritt 4: Workflow aktivieren

1. Klick oben rechts auf **Active** (Toggle)
2. Der Webhook ist jetzt erreichbar unter:
   ```
   https://deine-n8n-url.com/webhook/google-maps-leads
   ```
3. Kopiere diese URL – du brauchst sie in Schritt 6

---

## Schritt 5: Google Maps Daten scrapen

1. Öffne [Google Maps](https://www.google.com/maps)
2. Suche z.B. nach `Döner Laden Berlin`
3. Scrolle in der Ergebnisliste nach unten, um mehr Ergebnisse zu laden
4. Klick auf das **Instant Data Scraper** Icon in Chrome
5. Der Scraper erkennt die Tabelle automatisch
6. Klick **Start Crawling**
7. Wenn fertig: **Download as CSV**

### Typische Spalten vom Scraper:
| Spalte | Beispiel |
|--------|---------|
| Name | Istanbul Döner |
| Address | Hauptstr. 12, 10115 Berlin |
| Phone | 030 12345678 |
| Website | www.istanbul-doener.de |
| Rating | 4.5 |
| Reviews | 234 |

---

## Schritt 6: CSV an den Webhook senden

### Option A: Per curl (Terminal)

```bash
curl -X POST \
  https://deine-n8n-url.com/webhook/google-maps-leads \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "body": [
    {
      "Name": "Istanbul Döner",
      "Phone": "030 12345678",
      "Address": "Hauptstr. 12, 10115 Berlin",
      "Website": "www.istanbul-doener.de",
      "Email": "info@istanbul-doener.de",
      "Rating": "4.5",
      "Reviews": "234",
      "Category": "Döner Restaurant"
    }
  ]
}
EOF
```

### Option B: CSV-Datei per curl senden

```bash
# CSV zu JSON konvertieren und senden
python3 -c "
import csv, json, sys
with open('deine-datei.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)
print(json.dumps({'body': data}))
" | curl -X POST \
  https://deine-n8n-url.com/webhook/google-maps-leads \
  -H 'Content-Type: application/json' \
  -d @-
```

### Option C: Python-Script

```python
import csv
import json
import requests

# CSV einlesen
with open('google_maps_export.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    leads = list(reader)

# An n8n Webhook senden
response = requests.post(
    'https://deine-n8n-url.com/webhook/google-maps-leads',
    json={'body': leads}
)

print(f'Status: {response.status_code}')
print(f'Antwort: {response.json()}')
```

---

## Schritt 7: Ergebnis prüfen

Nach dem Senden:
1. Öffne n8n → **Executions** → prüfe ob der Workflow erfolgreich lief
2. Öffne HubSpot → **Kontakte** und **Unternehmen** → neue Einträge sollten sichtbar sein
3. Prüfe ob Kontakt und Firma korrekt verknüpft sind

---

## Felder-Mapping

Der Workflow erkennt automatisch verschiedene Spaltennamen:

| Dein CSV | Wird erkannt als |
|----------|-----------------|
| Name, name, Title | Firmenname |
| Phone, phone, Telefon, Phone number | Telefon |
| Address, address, Adresse, Full address | Adresse |
| Website, website, Web, URL | Website |
| Email, email, E-Mail | E-Mail |
| City, Stadt | Stadt |
| Rating, Bewertung | Bewertung |
| Category, Kategorie | Kategorie |

---

## Duplikat-Erkennung

Der Workflow prüft vor dem Anlegen:
- **Telefonnummer** wird in HubSpot gesucht
- Existiert die Nummer bereits → Lead wird übersprungen
- Existiert die Nummer nicht → Firma + Kontakt werden angelegt und verknüpft

---

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| Webhook antwortet nicht | Prüfe ob der Workflow **aktiv** ist |
| HubSpot Fehler 401 | Access Token prüfen / neu erstellen |
| Keine Leads importiert | Prüfe die Spaltennamen in deiner CSV |
| Duplikate werden nicht erkannt | Telefonnummern-Format prüfen (mit/ohne Vorwahl) |
| "Keine gültigen Leads" Fehler | CSV muss eine "Name" Spalte haben |

---

## Erweiterte Optionen

### Custom Fields in HubSpot
Um eigene Felder zu nutzen, bearbeite den Node **"HubSpot - Firma anlegen"** und füge unter `additionalFields` weitere Properties hinzu.

### Rate Limiting
HubSpot erlaubt max. 100 API-Calls pro 10 Sekunden (Private App). Bei großen Imports (>50 Leads) empfohlen:
- In n8n unter **Settings → Workflow Settings** ein **Batch-Limit** setzen
- Oder den Import in kleinere Teile aufteilen
