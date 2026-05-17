// ============================================================
//  CityGuide — Konfiguration
//  Trage hier deine API-Keys ein, bevor du die App startest.
// ============================================================

const CONFIG = {
  // Google Maps / Places API Key
  // Erstellen unter: https://console.cloud.google.com/
  // Benötigte APIs: Maps JavaScript API + Places API
  googlePlacesApiKey: "DEIN_GOOGLE_API_KEY_HIER",

  // GetYourGuide Partner-ID (optional)
  // Leer lassen wenn nicht vorhanden — Links funktionieren trotzdem
  getYourGuidePartnerId: "",

  // Standard-Stadt beim Öffnen der App
  defaultCity: "Wien",

  // Anzahl der Ergebnisse pro Kategorie (max. 20 mit Places API)
  resultsPerCategory: 12,
};
