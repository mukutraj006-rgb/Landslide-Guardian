/**
 * LANDSLIDE GUARDIAN — Full Map Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
  const map = L.map("fullMap").setView([26.1158, 91.7086], 7); // Center of NER

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  // Fetch all assessments from API or fallback list
  let locations = await API.get("/risk/all");
  
  if (!locations || locations.length === 0) {
    locations = DEMO_LOCATIONS.map(d => API.generateFallbackRisk(d.name, d.lat, d.lon));
  }

  const colors = { LOW: "#10b981", MODERATE: "#eab308", HIGH: "#f97316", CRITICAL: "#ef4444" };

  locations.forEach(loc => {
    const lat = loc.latitude || loc.lat;
    const lon = loc.longitude || loc.lon;
    const score = loc.risk_score || 50;
    const level = loc.risk_level || "MODERATE";
    const name = loc.location || loc.name;

    const marker = L.circleMarker([lat, lon], {
      radius: 12,
      color: colors[level] || "#38bdf8",
      fillColor: colors[level] || "#38bdf8",
      fillOpacity: 0.75,
      weight: 2
    }).addTo(map);

    const popupHtml = `
      <div style="font-family: sans-serif; min-width: 180px;">
        <h4 style="margin: 0 0 4px 0; color: #fff;">${name}</h4>
        <div style="font-size: 0.85rem; margin-bottom: 4px;">
          Risk Level: <strong style="color: ${colors[level]}">${level} (${score}%)</strong>
        </div>
        <div style="font-size: 0.75rem; color: #cbd5e1;">
          Rainfall: ${loc.environmental_data?.rainfall_24h || 'N/A'} mm<br>
          Slope: ${loc.environmental_data?.slope || 'N/A'}°
        </div>
        <div style="margin-top: 8px;">
          <a href="assessment.html?loc=${encodeURIComponent(name)}" style="color: #38bdf8; font-size: 0.8rem; text-decoration: underline;">
            Run Full Assessment &rarr;
          </a>
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml);
  });
});