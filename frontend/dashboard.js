/**
 * LANDSLIDE GUARDIAN — Dashboard Manager
 */

let dashMapInstance = null;
let trendChartInstance = null;

document.addEventListener("DOMContentLoaded", async () => {
  await initDashboard();
});

async function initDashboard() {
  const badge = document.getElementById("dataModeBadge");
  
  // Try fetching latest risk from FastAPI backend
  let assessment = await API.get("/risk/latest");
  
  if (assessment && assessment.location) {
    badge.textContent = "● Live Backend Connected";
    badge.style.borderColor = "#10b981";
  } else {
    badge.textContent = "● Demo Fallback Mode";
    assessment = API.generateFallbackRisk("Gangtok, Sikkim", 27.3389, 88.6065);
  }

  renderDashboardData(assessment);
  renderMap(assessment.latitude, assessment.longitude, assessment.location, assessment.risk_level, assessment.risk_score);
  renderCharts();
}

function renderDashboardData(data) {
  document.getElementById("dashLocation").textContent = data.location;
  document.getElementById("dashScore").textContent = `${data.risk_score}%`;
  document.getElementById("dashRecommendation").textContent = data.recommendation;

  const levelBadge = document.getElementById("dashLevelBadge");
  levelBadge.textContent = `${data.risk_level} RISK`;
  levelBadge.className = `badge badge-${data.risk_level.toLowerCase()}`;

  const env = data.environmental_data || {};
  document.getElementById("metricRain").textContent = `${env.rainfall_24h || 68.4} mm`;
  document.getElementById("metricMoisture").textContent = `${env.soil_moisture || 82.0} %`;
  document.getElementById("metricSlope").textContent = `${env.slope || 36}°`;
  document.getElementById("metricElevation").textContent = `${env.elevation || 1650} m`;

  // Render Explainability Factors
  const container = document.getElementById("explainFactors");
  container.innerHTML = "";
  
  const factors = data.factors || {
    "Recent 24h Rainfall": "HIGH",
    "Soil Saturation Index": "HIGH",
    "Slope Gradient (>35°)": "HIGH",
    "Historical Slide Frequency": "MODERATE"
  };

  for (const [key, val] of Object.entries(factors)) {
    const pill = document.createElement("div");
    pill.className = "factor-pill";
    const cleanKey = key.replace(/_/g, " ").toUpperCase();
    const color = val === "HIGH" ? "var(--risk-high)" : (val === "CRITICAL" ? "var(--risk-critical)" : "var(--risk-low)");
    pill.innerHTML = `<span>• ${cleanKey}</span> <strong style="color: ${color};">${val}</strong>`;
    container.appendChild(pill);
  }
}

function renderMap(lat, lon, name, level, score) {
  if (dashMapInstance) dashMapInstance.remove();
  
  dashMapInstance = L.map("dashMap").setView([lat, lon], 9);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(dashMapInstance);

  const colors = { LOW: "#10b981", MODERATE: "#eab308", HIGH: "#f97316", CRITICAL: "#ef4444" };
  
  L.circleMarker([lat, lon], {
    radius: 12,
    color: colors[level] || "#38bdf8",
    fillColor: colors[level] || "#38bdf8",
    fillOpacity: 0.7
  }).addTo(dashMapInstance)
    .bindPopup(`<strong>${name}</strong><br>Risk Score: ${score}% (${level})`)
    .openPopup();
}

function renderCharts() {
  const ctx = document.getElementById("trendChart").getContext("2d");
  if (trendChartInstance) trendChartInstance.destroy();

  trendChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "Now"],
      datasets: [
        {
          label: "Accumulated Rainfall (mm)",
          data: [10, 18, 32, 45, 55, 62, 68.4],
          borderColor: "#38bdf8",
          backgroundColor: "rgba(56, 189, 248, 0.1)",
          yAxisID: "y"
        },
        {
          label: "Risk Score (%)",
          data: [35, 42, 54, 65, 71, 75, 78],
          borderColor: "#f97316",
          backgroundColor: "rgba(249, 115, 22, 0.1)",
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: "linear",
          display: true,
          position: "left",
          grid: { color: "#334155" }
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          grid: { drawOnChartArea: false },
          min: 0,
          max: 100
        }
      },
      plugins: {
        legend: { labels: { color: "#94a3b8" } }
      }
    }
  });
}

function triggerSectorSOS() {
  window.location.href = "alerts.html?trigger_sos=true";
}