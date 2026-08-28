/**
 * LANDSLIDE GUARDIAN 
 */

document.addEventListener("DOMContentLoaded", async () => {
  loadActiveAlerts();
  
  // If redirected with broadcast query
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("trigger_sos") || urlParams.get("broadcast")) {
    triggerManualSOSBroadcast();
  }
});

async function loadActiveAlerts() {
  let alerts;
  try {
    alerts = await API.get("/alerts");
  } catch (error) {
    console.error(error);
    document.getElementById("activeCountBadge").textContent = "Backend Error";
    return;
  }

  document.getElementById("activeCountBadge").textContent = `${alerts.length} Active Warnings`;
  const container = document.getElementById("alertsFeedContainer");
  container.innerHTML = "";

  alerts.forEach(a => {
    const card = document.createElement("div");
    card.style.background = "var(--bg-card)";
    card.style.border = `1px solid ${a.risk_level === 'CRITICAL' ? 'var(--risk-critical)' : 'var(--risk-high)'}`;
    card.style.borderRadius = "8px";
    card.style.padding = "1rem";
    card.style.marginBottom = "0.75rem";

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <h4 style="color: #fff; margin: 0;">⚠ ${a.risk_level} ALERT: ${a.location}</h4>
        <span class="badge badge-${a.risk_level.toLowerCase()}">${a.risk_score}% Risk</span>
      </div>
      <p style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.5rem;">
        <strong>Reasons:</strong> ${Array.isArray(a.reasons) ? a.reasons.join(", ") : a.reasons}
      </p>
      <div style="font-size: 0.85rem; color: var(--accent-blue);">
        <strong>Action:</strong> ${a.recommendation}
      </div>
      <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.5rem;">
        Timestamp: ${new Date(a.timestamp).toLocaleString()}
      </div>
    `;
    container.appendChild(card);
  });
}

function handleCitizenRegister(e) {
  e.preventDefault();
  const name = document.getElementById("regName").value;
  const phone = document.getElementById("regPhone").value;
  const location = document.getElementById("regLocation").value;

  const citizen = { name, phone, location, registeredAt: new Date().toISOString() };
  
  // Store locally and post to backend
  const list = JSON.parse(localStorage.getItem("registered_citizens") || "[]");
  list.push(citizen);
  localStorage.setItem("registered_citizens", JSON.stringify(list));

  API.post("/sos/register", citizen);

  alert(`Citizen ${name} (${phone}) registered for emergency alerts in ${location}!`);
  document.getElementById("sosRegisterForm").reset();
}

async function triggerManualSOSBroadcast() {
  const bubble = document.getElementById("phoneBubble");
  const time = document.getElementById("phoneTimestamp");
  
  const savedPending = sessionStorage.getItem("pending_sos");
  let locName = "Gangtok, Sikkim";
  if (savedPending) {
    const parsed = JSON.parse(savedPending);
    locName = parsed.location || locName;
  }

  // Trigger backend SMS endpoint
  await API.post("/sos/dispatch", { location: locName });

  bubble.innerHTML = `
    <strong>🚨 EMERGENCY LANDSLIDE ALERT</strong><br>
    <em>"There's a Landslide in your area (${locName}) so stay alert! Heavy rainfall and slope instability detected. Avoid vulnerable cut-slopes and follow local safety advisories."</em>
    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 6px; text-align: right;">Broadcasted to registered citizens just now</div>
  `;
  time.textContent = "Just now";

  alert(`Prototype SOS dispatch completed for ${locName}. No real SMS/phone call is sent in this version.`);
}