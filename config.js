// ============================================================
//  CityGuide — Konfiguration
//  Trage hier deine API-Keys ein, bevor du die App startest.
// ============================================================

const CONFIG = {
  // Google Places API Key — hier eintragen für echte Bewertungen & Fotos
  // Leer lassen = OpenStreetMap wird verwendet (kostenlos, keine Bewertungen)
  googlePlacesApiKey: "", // DEAKTIVIERT zum Testen — Key: AIzaSyDks5kfDGILM9-mg1kY2SD-AmqD-1ibkK0

  // GetYourGuide Partner-ID (optional)
  // Leer lassen wenn nicht vorhanden — Links funktionieren trotzdem
  getYourGuidePartnerId: "",

  // Standard-Stadt beim Öffnen der App
  defaultCity: "Wien",

  // Anzahl der Ergebnisse pro Kategorie
  resultsPerCategory: 30,
};
