const map = L.map("map").setView([55.7512, 37.6184], 13);

L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
}).addTo(map);

const routeList = document.getElementById("route-list");
const stopHint = document.getElementById("selected-stop-hint");

let activeRouteId = null;
let activeRouteLine = null;
let activeVehicleStream = null;
const vehicleMarkers = new Map();

async function apiGet(path) {
  const response = await fetch(path);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json();
}

function clearVehicleMarkers() {
  for (const marker of vehicleMarkers.values()) {
    map.removeLayer(marker);
  }
  vehicleMarkers.clear();
}

function resetActiveRouteVisuals() {
  if (activeRouteLine) {
    map.removeLayer(activeRouteLine);
    activeRouteLine = null;
  }
  clearVehicleMarkers();
}

function closeVehicleStream() {
  if (activeVehicleStream) {
    activeVehicleStream.close();
    activeVehicleStream = null;
  }
}

function collapseOtherSchedules(currentContainer) {
  const allDetails = routeList.querySelectorAll(".route-details");
  allDetails.forEach((details) => {
    if (details === currentContainer) {
      return;
    }
    details.dataset.expanded = "false";
    details.innerHTML = "";
  });
}

function setActiveRouteButton(currentButton) {
  const allButtons = routeList.querySelectorAll(".route-button");
  allButtons.forEach((button) => {
    button.classList.remove("is-active");
  });
  if (currentButton) {
    currentButton.classList.add("is-active");
  }
}

function renderSchedule(container, schedule) {
  if (!schedule.length) {
    container.innerHTML = "<div class='schedule-empty'>Нет расписания.</div>";
    return;
  }
  const list = document.createElement("ul");
  list.className = "schedule-list";
  for (const row of schedule) {
    const item = document.createElement("li");
    item.textContent = `${row.arrival_hhmm} → ${row.destination}`;
    list.appendChild(item);
  }
  container.innerHTML = "";
  container.appendChild(list);
}

function geometryToPolyline(segments) {
  if (!segments.length) {
    return [];
  }
  const points = [];
  for (const segment of segments) {
    points.push([segment.start_lat, segment.start_lon]);
  }
  const last = segments[segments.length - 1];
  points.push([last.end_lat, last.end_lon]);
  return points;
}

function openVehicleStream(routeId) {
  closeVehicleStream();
  clearVehicleMarkers();

  activeVehicleStream = new EventSource(`/api/routes/${routeId}/vehicles/stream`);
  activeVehicleStream.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const existing = vehicleMarkers.get(data.vehicle_id);
    if (existing) {
      existing.setLatLng([data.lat, data.lon]);
      return;
    }
    const marker = L.circleMarker([data.lat, data.lon], {
      radius: 7,
      color: "#374151",
      fillColor: "#2563eb",
      fillOpacity: 0.95,
      weight: 2,
    }).addTo(map);
    marker.bindTooltip(data.vehicle_id);
    vehicleMarkers.set(data.vehicle_id, marker);
  };
  activeVehicleStream.addEventListener("error", () => {
    closeVehicleStream();
  });
}

async function openRoute(route, detailsContainer, routeButton) {
  if (activeRouteId === route.id && detailsContainer.dataset.expanded === "true") {
    detailsContainer.dataset.expanded = "false";
    detailsContainer.innerHTML = "";
    setActiveRouteButton(null);
    closeVehicleStream();
    resetActiveRouteVisuals();
    activeRouteId = null;
    return;
  }

  const details = await apiGet(`/api/routes/${route.id}`);
  activeRouteId = route.id;
  resetActiveRouteVisuals();
  collapseOtherSchedules(detailsContainer);
  setActiveRouteButton(routeButton);

  const points = geometryToPolyline(details.geometry);
  activeRouteLine = L.polyline(points, {
    color: route.kind === "TROLLEYBUS" ? "#0f766e" : "#1d4ed8",
    weight: 5,
    opacity: 0.8,
  }).addTo(map);
  map.fitBounds(activeRouteLine.getBounds(), { padding: [40, 40] });

  renderSchedule(detailsContainer, details.schedule);
  detailsContainer.dataset.expanded = "true";
  openVehicleStream(route.id);
}

function routeTitle(route) {
  const icon = route.kind === "TROLLEYBUS" ? "🚎" : "🚌";
  return `${icon} ${route.display_name}`;
}

async function renderRoutes(stopId, stopName) {
  stopHint.textContent = `Выбрана остановка: ${stopName}`;
  routeList.innerHTML = "<li class='loading'>Загрузка маршрутов...</li>";
  closeVehicleStream();
  resetActiveRouteVisuals();
  activeRouteId = null;

  const data = await apiGet(`/api/stops/${stopId}/routes`);
  routeList.innerHTML = "";

  if (!data.routes.length) {
    routeList.innerHTML = "<li class='empty'>Нет маршрутов для этой остановки.</li>";
    return;
  }

  for (const route of data.routes) {
    const item = document.createElement("li");
    item.className = "route-item";

    const row = document.createElement("button");
    row.className = "route-button";
    row.textContent = routeTitle(route);

    const details = document.createElement("div");
    details.className = "route-details";
    details.dataset.expanded = "false";

    row.addEventListener("click", async () => {
      try {
        await openRoute(route, details, row);
      } catch (error) {
        details.dataset.expanded = "true";
        details.innerHTML = `<div class="schedule-empty">Ошибка: ${error.message}</div>`;
      }
    });

    item.appendChild(row);
    item.appendChild(details);
    routeList.appendChild(item);
  }
}

async function loadStops() {
  const data = await apiGet("/api/stops");
  data.stops.forEach((stop) => {
    const marker = L.circleMarker([stop.lat, stop.lon], {
      radius: 8,
      color: "#0f172a",
      fillColor: "#f59e0b",
      fillOpacity: 0.9,
      weight: 2,
    }).addTo(map);
    marker.bindTooltip(stop.name);
    marker.on("click", async () => {
      try {
        await renderRoutes(stop.id, stop.name);
      } catch (error) {
        stopHint.textContent = "Не удалось загрузить маршруты.";
        routeList.innerHTML = `<li class="empty">Ошибка: ${error.message}</li>`;
      }
    });
  });
}

loadStops().catch((error) => {
  stopHint.textContent = "Не удалось загрузить остановки.";
  routeList.innerHTML = `<li class="empty">Ошибка: ${error.message}</li>`;
});
