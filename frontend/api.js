/**
 * LANDSLIDE GUARDIAN — Central API Client
 * The browser talks only to FastAPI. No MongoDB credentials are exposed.
 */

const API_BASE = window.LANDSLIDE_API_BASE || "/api";

const DEMO_LOCATIONS = [
  { name: "Gangtok, Sikkim", state: "Sikkim", lat: 27.3389, lon: 88.6065, slope: 36, elevation: 1650, hist_freq: 8 },
  { name: "Shillong, Meghalaya", state: "Meghalaya", lat: 25.5788, lon: 91.8933, slope: 28, elevation: 1525, hist_freq: 5 },
  { name: "Aizawl, Mizoram", state: "Mizoram", lat: 23.7271, lon: 92.7176, slope: 42, elevation: 1132, hist_freq: 9 },
  { name: "Kohima, Nagaland", state: "Nagaland", lat: 25.6740, lon: 94.1086, slope: 34, elevation: 1444, hist_freq: 6 },
  { name: "Itanagar, Arunachal Pradesh", state: "Arunachal Pradesh", lat: 27.0844, lon: 93.6053, slope: 30, elevation: 320, hist_freq: 4 },
  { name: "Guwahati, Assam", state: "Assam", lat: 26.1445, lon: 91.7362, slope: 12, elevation: 55, hist_freq: 2 },
  { name: "Imphal, Manipur", state: "Manipur", lat: 24.8170, lon: 93.9368, slope: 22, elevation: 786, hist_freq: 3 },
  { name: "Agartala, Tripura", state: "Tripura", lat: 23.8315, lon: 91.2868, slope: 8, elevation: 15, hist_freq: 1 }
];

const API = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`GET ${endpoint} failed (${response.status}): ${text}`);
    }
    return response.json();
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`POST ${endpoint} failed (${response.status}): ${text}`);
    }

    return response.json();
  }
};
