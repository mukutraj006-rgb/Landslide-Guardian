/**
 * LANDSLIDE GUARDIAN — Assessment Page Logic
 */

let currentAssessment = null;

document.addEventListener("DOMContentLoaded", () => {
  renderPresets();

  const urlParams = new URLSearchParams(window.location.search);
  const locQuery = urlParams.get("loc");

  if (locQuery) {
    const match = DEMO_LOCATIONS.find(
      d => d.name.toLowerCase().includes(locQuery.toLowerCase())
    );
    if (match) evaluateLocation(match);
  }
});

function renderPresets() {
  const container = document.getElementById("presetChips");
  container.innerHTML = "";

  DEMO_LOCATIONS.forEach(loc => {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.textContent = loc.name;
    chip.onclick = () => evaluateLocation(loc);
    container.appendChild(chip);
  });
}

async function evaluateLocation(loc) {
  document.getElementById("inputLat").value = loc.lat;
  document.getElementById("inputLon").value = loc.lon;
  document.getElementById("inputName").value = loc.name;

  try {
    const result = await API.post("/risk/predict", {
      location_name: loc.name,
      latitude: loc.lat,
      longitude: loc.lon
    });

    displayAssessment(result);
  } catch (error) {
    console.error(error);
    alert(
      "Risk assessment failed. Check that FastAPI is running and MongoDB Atlas is connected."
    );
  }
}

function runCustomAssessment() {
  const lat = parseFloat(document.getElementById("inputLat").value);
  const lon = parseFloat(document.getElementById("inputLon").value);
  const name = document.getElementById("inputName").value.trim()
    || `Lat: ${lat}, Lon: ${lon}`;

  if (
    Number.isNaN(lat) || Number.isNaN(lon) ||
    lat < -90 || lat > 90 ||
    lon < -180 || lon > 180
  ) {
    alert("Enter valid coordinates: latitude -90..90, longitude -180..180.");
    return;
  }

  evaluateLocation({ name, lat, lon });
}

function displayAssessment(res) {
  currentAssessment = res;

  document.getElementById("resPlaceholder").style.display = "none";
  document.getElementById("resBody").style.display = "block";
  document.getElementById("resLocTitle").textContent = res.location;
  document.getElementById("resScoreText").textContent = `${res.risk_score}%`;

  const colors = {
    LOW: "#10b981",
    MODERATE: "#eab308",
    HIGH: "#f97316",
    CRITICAL: "#ef4444"
  };
  document.getElementById("resScoreText").style.color =
    colors[res.risk_level] || "#fff";

  const badge = document.getElementById("resBadge");
  badge.textContent = `${res.risk_level} RISK`;
  badge.className = `badge badge-${res.risk_level.toLowerCase()}`;

  document.getElementById("resRecommendation").textContent =
    res.recommendation;

  const env = res.environmental_data || {};
  const dataMode = env.data_source || "UNKNOWN";

  const factorsContainer = document.getElementById("resFactorsList");
  factorsContainer.innerHTML = "";

  for (const [key, value] of Object.entries(res.factors || {})) {
    const pill = document.createElement("div");
    pill.className = "factor-pill";
    pill.innerHTML =
      `<span>• ${key.replace(/_/g, " ").toUpperCase()}</span> ` +
      `<strong>${value}</strong>`;
    factorsContainer.appendChild(pill);
  }

  const sourcePill = document.createElement("div");
  sourcePill.className = "factor-pill";
  sourcePill.innerHTML =
    `<span>• WEATHER DATA</span> <strong>${dataMode}</strong>`;
  factorsContainer.appendChild(sourcePill);

  const sosBox = document.getElementById("resSosOption");
  sosBox.style.display = res.risk_score >= 61 ? "block" : "none";
}

function dispatchDirectSOS() {
  if (!currentAssessment) return;
  sessionStorage.setItem("pending_sos", JSON.stringify(currentAssessment));
  window.location.href = "alerts.html?broadcast=now";
}
