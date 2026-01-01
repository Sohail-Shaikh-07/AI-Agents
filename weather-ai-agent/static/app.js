const API_BASE = "http://127.0.0.1:8000";

// --- UI Init ---
const COLUMNS_DEF = [
  { id: "temp", label: "Temperature" },
  { id: "humidity", label: "Humidity" },
  { id: "pressure", label: "Pressure" },
  { id: "wind", label: "Wind Speed" },
  { id: "aqi", label: "AQI & Pollutants" },
  { id: "visibility", label: "Visibility" },
];

window.onload = function () {
  initCheckboxes();
  // Set default dates
  document.getElementById("startDate").valueAsDate = new Date();
  document.getElementById("endDate").valueAsDate = new Date();
};

function initCheckboxes() {
  const grid = document.getElementById("checkboxGrid");
  grid.innerHTML = "";

  COLUMNS_DEF.forEach((col) => {
    const div = document.createElement("div");
    div.className = "checkbox-card selected";
    div.innerHTML = `
            <input type="checkbox" value="${col.id}" checked>
            <span>${col.label}</span>
        `;
    div.onclick = function (e) {
      // Prevent double toggle if clicking direct on checkbox
      if (e.target.tagName === "INPUT") return;

      this.classList.toggle("selected");
      const cb = this.querySelector("input");
      cb.checked = !cb.checked;
    };
    grid.appendChild(div);
  });
}

// --- Logic ---

async function searchLocation() {
  const query = document.getElementById("cityInput").value;
  if (!query) return log("Please enter a city name.", "error");

  const btn = document.getElementById("searchBtn");
  const originalIcon = btn.innerHTML;
  btn.innerHTML = "⏳";

  log(`Searching global database for: "${query}"...`);

  try {
    const res = await fetch(
      `https://geocoding-api.open-meteo.com/v1/search?name=${query}&count=5&language=en&format=json`
    );
    const data = await res.json();

    const resultsDiv = document.getElementById("searchResults");
    resultsDiv.innerHTML = "";
    resultsDiv.classList.remove("hidden");

    if (data.results) {
      data.results.forEach((loc) => {
        const div = document.createElement("div");
        div.className = "dropdown-item";
        div.innerText = `${loc.name}, ${loc.country} (${loc.admin1 || ""})`;
        div.onclick = () => selectLocation(loc);
        resultsDiv.appendChild(div);
      });
      log(`Found ${data.results.length} matches.`);
    } else {
      resultsDiv.innerHTML =
        '<div class="dropdown-item">No results found</div>';
      log("No location matches found.", "error");
    }
  } catch (e) {
    log(`Error searching location: ${e.message}`, "error");
  } finally {
    btn.innerHTML = originalIcon;
  }
}

function selectLocation(loc) {
  document.getElementById("lat").value = loc.latitude;
  document.getElementById("lon").value = loc.longitude;
  document.getElementById("cityInput").value = loc.name;

  document.getElementById("searchResults").classList.add("hidden");
  log(
    `Target Locked: ${loc.name} [Lat: ${loc.latitude.toFixed(
      2
    )}, Lon: ${loc.longitude.toFixed(2)}]`,
    "success"
  );
}

async function startJob() {
  const lat = document.getElementById("lat").value;
  const lon = document.getElementById("lon").value;
  const city = document.getElementById("cityInput").value;
  const start = document.getElementById("startDate").value;
  const end = document.getElementById("endDate").value;
  // We can capture interval too if backend needs it later
  const interval = document.getElementById("intervalSelect").value;

  if (!lat || !start || !end) {
    log(
      "OPERATION ABORTED: Missing Target Coordinates or Date Range.",
      "error"
    );
    return;
  }

  // Collect columns
  const columns = [];
  document.querySelectorAll("#checkboxGrid input:checked").forEach((cb) => {
    columns.push(cb.value);
  });

  const payload = {
    location_name: city,
    latitude: parseFloat(lat),
    longitude: parseFloat(lon),
    start_date: start,
    end_date: end,
    interval: parseInt(interval),
    columns: columns,
  };

  setRunning(true);
  log("Initializing Agent Protocol...", "info");

  try {
    const res = await fetch(`${API_BASE}/api/start-job`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (data.status === "error") {
      log(data.message, "error");
      setRunning(false);
    } else {
      log(data.message, "success");
      pollLogs();
    }
  } catch (e) {
    log(`Connection Failed: ${e.message}`, "error");
    setRunning(false);
  }
}

let logInterval;

function pollLogs() {
  if (logInterval) clearInterval(logInterval);

  logInterval = setInterval(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/logs`);
      const logs = await res.json();

      if (logs.lines && logs.lines.length > 0) {
        logs.lines.forEach((line) => {
          // Detect error lines for red color
          const type = line.toLowerCase().includes("error")
            ? "error"
            : "success";
          log(line, type);
        });
      }

      if (
        logs.status === "completed" ||
        logs.status === "idle" ||
        logs.status === "error"
      ) {
        if (logs.status === "completed")
          log("Data Collection Sequence Complete.", "success");
        clearInterval(logInterval);
        setRunning(false);
      }
    } catch (e) {
      // ignore network errors
    }
  }, 1500);
}

function log(msg, type = "info") {
  const consoleBox = document.getElementById("consoleOutput");
  const entry = document.createElement("div");
  entry.className = `log-entry ${type}`;
  const time = new Date().toLocaleTimeString();
  entry.innerHTML = `<span class="timestamp">[${time}]</span> <span>${msg}</span>`;
  consoleBox.appendChild(entry);
  consoleBox.scrollTop = consoleBox.scrollHeight;
}

function setRunning(isRunning) {
  const btn = document.getElementById("startBtn");
  if (isRunning) {
    btn.disabled = true;
    btn.innerText = "Processing Data Stream...";
    btn.style.opacity = "0.7";
  } else {
    btn.disabled = false;
    btn.innerText = "Initialize Agent Protocol";
    btn.style.opacity = "1";
  }
}
