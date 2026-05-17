# CityGuide — Reiseführer App

Moderne, mobile-optimierte Web-App für Stadtentdeckungen.

## Setup

### 1. Google API Key (optional, für echte Daten)
1. Gehe zu https://console.cloud.google.com/
2. Neues Projekt erstellen → "APIs & Dienste" → "Bibliothek"
3. Aktiviere: **Maps JavaScript API** + **Places API**
4. "Anmeldedaten" → API-Schlüssel erstellen
5. Key in `config.js` eintragen: `googlePlacesApiKey: "DEIN_KEY"`

Ohne Key: Demo-Daten werden angezeigt — App funktioniert vollständig.

### 2. GetYourGuide Partner-ID (optional)
- Falls du ein Affiliate-Konto hast, Partner-ID in `config.js` eintragen
- Ohne ID: Links zu GetYourGuide funktionieren trotzdem (ohne Provision)

---

## Deployment auf Netlify (kostenlos)

1. Gehe zu https://app.netlify.com/drop
2. Ziehe den Ordner `travel-guide/` per Drag & Drop rein
3. Fertig — du bekommst einen Link wie `https://random-name.netlify.app`
4. Link per WhatsApp mit der Familie teilen!

---

## Features
- Stadtsuche mit OpenStreetMap Geocoding (kostenlos)
- Restaurants, Bars, Sehenswürdigkeiten via Google Places
- Google Maps Navigation für jeden Ort
- ÖPNV-Routen direkt in Google Maps
- GetYourGuide Buchungslinks
- Vollständig mobile-optimiert (iOS & Android)
- Dark Mode Design
