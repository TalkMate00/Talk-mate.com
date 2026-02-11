# TalkMate - n8n Lead Generation Workflow

Automatischer Gastro-Lead-Generator für TalkMate. Findet Döner-, Pizza-, Sushi- und Burger-Restaurants in ganz Deutschland über Google Places API und importiert sie in HubSpot.

---

## Workflow-Übersicht

```
Manueller Start
    → Städte × Kategorien Kombinationen (50 Städte × 4 Kategorien = 200 Suchen)
    → Google Places Text Search
    → Google Place Details (Telefon, Website, Öffnungszeiten etc.)
    → HubSpot Duplikat-Check (via Google Place ID)
    → Neuer Lead?
        ├── JA + Hat E-Mail → HubSpot Kontakt (Tag: "mit-email") → Erst-Kontakt E-Mail
        ├── JA + Keine E-Mail → HubSpot Kontakt (Tag: "ohne-email")
        └── NEIN (Duplikat) → Übersprungen
```

## Erfasste Lead-Daten

| Feld | Quelle |
|------|--------|
| Firmenname | Google Places |
| Adresse | Google Places |
| Telefonnummer | Google Place Details |
| Website | Google Place Details |
| E-Mail | Google Place Details |
| Google Bewertung | Google Places |
| Anzahl Bewertungen | Google Places |
| Öffnungszeiten | Google Place Details |
| Google Maps Link | Google Place Details |
| Kategorie (Döner/Pizza/Sushi/Burger) | Suchparameter |
| Stadt | Suchparameter |

---

## 1. Google Places API einrichten

Da du bereits einen Google Cloud Account hast, folge diesen Schritten:

### Schritt 1: Projekt erstellen (falls nötig)
1. Gehe zu [Google Cloud Console](https://console.cloud.google.com)
2. Klicke oben auf das Projekt-Dropdown → **"Neues Projekt"**
3. Name: z.B. `TalkMate Lead Gen`
4. **"Erstellen"** klicken

### Schritt 2: Places API aktivieren
1. Gehe zu **APIs & Dienste** → **Bibliothek**
2. Suche nach **"Places API"**
3. Klicke auf **"Places API"** → **"Aktivieren"**
4. Suche auch nach **"Geocoding API"** und aktiviere diese ebenfalls

### Schritt 3: API-Key erstellen
1. Gehe zu **APIs & Dienste** → **Anmeldedaten**
2. Klicke **"+ Anmeldedaten erstellen"** → **"API-Schlüssel"**
3. **WICHTIG:** Klicke auf **"Schlüssel einschränken"**:
   - Unter **API-Einschränkungen**: Wähle "Schlüssel einschränken" und wähle nur:
     - Places API
     - Geocoding API
4. Kopiere den API-Key und speichere ihn sicher

### Schritt 4: Abrechnung prüfen
- Google gibt dir **$200 kostenloses Guthaben/Monat**
- Text Search kostet ~$32 pro 1.000 Anfragen
- Place Details kostet ~$17 pro 1.000 Anfragen
- Für 200 Suchen × ~20 Ergebnisse = ~4.000 Detail-Anfragen → ca. **$70-75/Durchlauf**
- Mit $200 Guthaben: **~2-3 komplette Durchläufe kostenlos pro Monat**

> **Tipp:** Starte mit weniger Städten (z.B. nur die Top 10) zum Testen!

---

## 2. HubSpot einrichten

### Schritt 1: Private App erstellen
1. Gehe zu **HubSpot** → **Einstellungen** → **Integrationen** → **Private Apps**
2. Klicke **"Private App erstellen"**
3. Name: `TalkMate n8n Integration`
4. Unter **Berechtigungen (Scopes)** aktiviere:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.schemas.contacts.read`
5. **"App erstellen"** → Access Token kopieren

### Schritt 2: Benutzerdefinierte Felder anlegen
Erstelle in HubSpot unter **Einstellungen** → **Eigenschaften** → **Kontakteigenschaften** folgende Felder:

| Feldname | Interner Name | Typ |
|----------|---------------|-----|
| Google Place ID | `google_place_id` | Einzeiliger Text |
| Google Bewertung | `google_rating` | Zahl |
| Anzahl Google Bewertungen | `google_total_ratings` | Zahl |
| Google Maps URL | `google_maps_url` | Einzeiliger Text |
| Öffnungszeiten | `opening_hours` | Mehrzeiliger Text |
| Lead Kategorie | `lead_kategorie` | Dropdown (Döner, Pizza, Sushi, Burger) |
| Lead Source | `lead_source` | Einzeiliger Text |
| Lead Status | `lead_status` | Dropdown (mit-email, ohne-email) |

---

## 3. n8n Workflow importieren

### Schritt 1: JSON importieren
1. Öffne deine **n8n Cloud** Instanz
2. Klicke **"Add workflow"** → **"Import from File"**
3. Wähle die Datei `talkmate-lead-generation.json`

### Schritt 2: Credentials einrichten

#### Google Places API Key
1. In n8n gehe zu **Settings** → **Credentials**
2. Erstelle neue Credential: **"Header Auth"** oder **"Query Auth"**
   - Name: `Google Places API Key`
   - Parameter Name: `key`
   - Value: Dein Google API-Key
3. **Alternativ:** Ersetze in den HTTP Request Nodes den Credential-Verweis durch deinen API-Key direkt im URL-Parameter `key`

#### HubSpot API
1. Erstelle neue Credential: **"Header Auth"**
   - Name: `HubSpot API Token`
   - Header Name: `Authorization`
   - Header Value: `Bearer DEIN_ACCESS_TOKEN`
2. **Alternativ:** Ersetze `{{ $credentials.hubspotApi.accessToken }}` in den Nodes durch deinen Token

#### SMTP (für E-Mail-Versand)
1. Erstelle neue Credential: **"SMTP"**
   - Host: Dein E-Mail-Provider SMTP-Server
   - Port: 587 (TLS) oder 465 (SSL)
   - User: Deine E-Mail-Adresse
   - Password: Dein App-Passwort
   - SSL/TLS: Aktiviert

### Schritt 3: Nodes überprüfen
Gehe durch jeden Node und stelle sicher, dass die Credentials korrekt verknüpft sind:
- `Google Places Suche` → Google Places API Key
- `Google Place Details` → Google Places API Key
- `HubSpot Duplikat-Check` → HubSpot API Token
- `HubSpot Kontakt (mit E-Mail)` → HubSpot API Token
- `HubSpot Kontakt (ohne E-Mail)` → HubSpot API Token
- `Erst-Kontakt E-Mail senden` → SMTP Credentials

---

## 4. E-Mail-Template anpassen

Die Erst-Kontakt-E-Mail ist im Node **"Erst-Kontakt E-Mail senden"** hinterlegt. Passe folgendes an:
- **Absender-E-Mail**: Wird automatisch aus SMTP-Credentials genommen
- **Demo-Link**: Ersetze `https://talk-mate.com/demo` durch euren tatsächlichen Buchungslink
- **Website-Link**: Prüfe ob `https://talk-mate.com` korrekt ist

---

## 5. Erster Testlauf

1. **Städte reduzieren**: Ändere im Node "Konfiguration" die Städte auf nur 1-2 Städte (z.B. nur "Berlin")
2. **Workflow manuell starten**: Klicke auf "Execute Workflow"
3. **Ergebnisse prüfen**:
   - Werden Restaurants gefunden?
   - Werden Details korrekt abgerufen?
   - Werden Kontakte in HubSpot erstellt?
   - Wird die E-Mail korrekt versendet?
4. **Bei Erfolg**: Städteliste wieder auf alle Städte erweitern

---

## 6. Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| "REQUEST_DENIED" bei Google API | API-Key prüfen, Places API aktiviert? |
| "OVER_QUERY_LIMIT" | Rate Limit erreicht – Pause im Workflow erhöhen |
| HubSpot 401 Error | Access Token abgelaufen → Neuen Token erstellen |
| HubSpot "Property does not exist" | Benutzerdefinierte Felder in HubSpot anlegen (siehe Schritt 2.2) |
| Keine E-Mails werden gesendet | SMTP Credentials prüfen, Spam-Ordner checken |
| Zu wenige Ergebnisse | Google gibt max. 20 Ergebnisse pro Suche – ist normal |

---

## Kosten-Übersicht

| Service | Kosten |
|---------|--------|
| n8n Cloud | Ab $20/Monat (Starter) |
| Google Places API | ~$70-75 pro Volldurchlauf (durch $200 Free Tier gedeckt) |
| HubSpot CRM | Kostenlos (Free Plan reicht) |
| SMTP | Abhängig vom Anbieter (Gmail kostenlos bis 500/Tag) |

---

## Städte anpassen

Im Node **"Konfiguration"** kannst du die Städteliste jederzeit anpassen. Aktuell sind die 50 größten deutschen Städte hinterlegt. Du kannst:
- Städte entfernen (für schnellere/günstigere Durchläufe)
- Städte hinzufügen (kleinere Städte nachträglich)
- Kategorien erweitern (z.B. "Asiatisch", "Griechisch", "Indisch")
