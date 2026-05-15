/*
 * BioClima viewer
 * ----------------
 * Reads layers.json (a small index of available bblocks) and renders any
 * combination of CoverageJSON or GeoJSON layers on a Leaflet map.
 *
 * The viewer is GENERIC: a new EBV or indicator just needs to be added to
 * layers.json with a path to its example file. No source edits required.
 */

const state = {
  lang: "en",
  layers: [],          // descriptors from layers.json
  active: null,        // currently-loaded layer descriptor
  raster: null,        // CovjsonRaster instance (if applicable)
  leafletLayer: null,
  tIndex: 0,
  playing: false,
  playTimer: null,
  ontologyCache: new Map()
};

const map = L.map("map").setView([65, 26], 5);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "© OpenStreetMap"
}).addTo(map);

map.on("click", e => onMapClick(e.latlng));

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------
(async function init() {
  document.getElementById("lang-select").addEventListener("change", e => {
    state.lang = e.target.value;
    applyTranslations(state.lang);
    refreshActiveLegend();
  });
  document.getElementById("info-close").addEventListener("click", () => {
    document.getElementById("info-panel").hidden = true;
  });
  document.getElementById("btn-play").addEventListener("click", togglePlay);
  document.getElementById("time-slider").addEventListener("input", e => {
    state.tIndex = parseInt(e.target.value, 10);
    updateTimeLabel();
    redrawRaster();
  });

  applyTranslations(state.lang);

  const layers = await fetch("data/layers.json").then(r => r.json());
  state.layers = layers;
  renderLayerList();

  // Activate the first layer by default
  if (layers.length) activateLayer(layers[0].id);
})();

// ---------------------------------------------------------------------------
// Layer list (sidebar)
// ---------------------------------------------------------------------------
function renderLayerList() {
  const list = document.getElementById("layer-list");
  list.innerHTML = "";
  for (const layer of state.layers) {
    const div = document.createElement("div");
    div.className = "layer-item";
    div.dataset.id = layer.id;
    div.innerHTML = `
      <input type="radio" name="layer" id="lyr-${layer.id}" ${state.active?.id === layer.id ? "checked" : ""}>
      <div class="layer-meta">
        <div class="layer-title">${layer.title[state.lang] || layer.title.en}</div>
        <div class="layer-kind">${layer.kind} · ${layer.bblock}</div>
      </div>`;
    div.addEventListener("click", () => activateLayer(layer.id));
    list.appendChild(div);
  }
}

// ---------------------------------------------------------------------------
// Activate / load
// ---------------------------------------------------------------------------
async function activateLayer(id) {
  const layer = state.layers.find(l => l.id === id);
  if (!layer) return;
  state.active = layer;

  if (state.leafletLayer) { map.removeLayer(state.leafletLayer); state.leafletLayer = null; }
  if (state.raster) state.raster = null;

  // Highlight in sidebar
  document.querySelectorAll(".layer-item").forEach(el => el.classList.toggle("active", el.dataset.id === id));

  if (layer.kind === "coverage") {
    const cov = await fetch(layer.dataUrl).then(r => r.json());
    state.raster = new CovjsonRaster(cov);
    state.tIndex = state.raster.hasTime ? state.raster.t.length - 1 : 0;
    setupTimeControls();
    renderLegend(layer);
    redrawRaster();
    map.fitBounds(state.raster.bounds());
  } else if (layer.kind === "geojson") {
    const fc = await fetch(layer.dataUrl).then(r => r.json());
    state.leafletLayer = L.geoJSON(fc, {
      style: feature => ({
        color: "#444",
        weight: 0.3,
        fillColor: categoryColor(feature.properties.categoryKey),
        fillOpacity: 0.7
      }),
      onEachFeature: (feature, lyr) => lyr.on("click", evt => onFeatureClick(feature, evt.latlng))
    }).addTo(map);
    document.getElementById("time-controls").hidden = true;
    renderCategoryLegend();
    map.fitBounds(state.leafletLayer.getBounds());
  }
}

// ---------------------------------------------------------------------------
// Time controls
// ---------------------------------------------------------------------------
function setupTimeControls() {
  const tc = document.getElementById("time-controls");
  if (!state.raster.hasTime) { tc.hidden = true; return; }
  tc.hidden = false;

  const slider = document.getElementById("time-slider");
  slider.min = 0;
  slider.max = state.raster.t.length - 1;
  slider.value = state.tIndex;
  updateTimeLabel();
}

function updateTimeLabel() {
  if (!state.raster?.hasTime) return;
  const t = state.raster.t[state.tIndex];
  document.getElementById("time-label").textContent = t.substring(0, 4);
}

function togglePlay() {
  state.playing = !state.playing;
  document.getElementById("btn-play").textContent = state.playing ? "⏸" : "▶";
  if (state.playing) {
    state.playTimer = setInterval(() => {
      if (!state.raster?.hasTime) return;
      state.tIndex = (state.tIndex + 1) % state.raster.t.length;
      document.getElementById("time-slider").value = state.tIndex;
      updateTimeLabel();
      redrawRaster();
    }, 600);
  } else {
    clearInterval(state.playTimer);
  }
}

// ---------------------------------------------------------------------------
// Raster drawing
// ---------------------------------------------------------------------------
function redrawRaster() {
  if (!state.raster) return;
  if (state.leafletLayer) map.removeLayer(state.leafletLayer);
  const layer = state.active;
  const scale = chroma.scale(layer.colorRamp || ["#3B8BD4", "#FCDE5A", "#E85D24"]).domain(layer.range);
  state.leafletLayer = state.raster.toCanvasLayer(state.tIndex, scale, layer.range);
  state.leafletLayer.addTo(map);
}

// ---------------------------------------------------------------------------
// Legend
// ---------------------------------------------------------------------------
function renderLegend(layer) {
  const el = document.getElementById("legend");
  el.innerHTML = "";
  const [lo, hi] = layer.range;
  const stops = 5;
  const scale = chroma.scale(layer.colorRamp || ["#3B8BD4", "#FCDE5A", "#E85D24"]).domain(layer.range);
  for (let i = 0; i < stops; i++) {
    const v = lo + (hi - lo) * (i / (stops - 1));
    const div = document.createElement("div");
    div.className = "legend-item";
    div.innerHTML = `<span class="legend-swatch" style="background:${scale(v).hex()}"></span><span>${v.toFixed(2)} ${layer.unit?.symbol || ""}</span>`;
    el.appendChild(div);
  }
}

function renderCategoryLegend() {
  const el = document.getElementById("legend");
  el.innerHTML = "";
  for (const [key, color] of Object.entries(CATEGORY_COLORS)) {
    const label = CATEGORY_LABELS[key]?.[state.lang] || key;
    const div = document.createElement("div");
    div.className = "legend-item";
    div.innerHTML = `<span class="legend-swatch" style="background:${color}"></span><span>${label}</span>`;
    el.appendChild(div);
  }
}

function refreshActiveLegend() {
  if (!state.active) return;
  if (state.active.kind === "coverage") renderLegend(state.active);
  else renderCategoryLegend();
  renderLayerList();
}

// ---------------------------------------------------------------------------
// Click handling
// ---------------------------------------------------------------------------
async function onMapClick(latlng) {
  if (!state.raster) return; // GeoJSON layers use their own click handler
  const v = state.raster.valueAt(state.tIndex, latlng.lng, latlng.lat);
  showInfo({
    title:  state.active.title[state.lang] || state.active.title.en,
    iri:    state.active.observedPropertyIri,
    value:  isNaN(v) ? UI_STRINGS[state.lang].noData : `${v} ${state.active.unit?.symbol || ""}`,
    coord:  `${latlng.lat.toFixed(3)}, ${latlng.lng.toFixed(3)}`,
    time:   state.raster.hasTime ? state.raster.t[state.tIndex].substring(0, 4) : null,
    policy: state.active.policyAlignment || []
  });
}

async function onFeatureClick(feature, latlng) {
  const p = feature.properties;
  showInfo({
    title:  p.categoryLabel?.[state.lang] || p.categoryLabel?.en || p.categoryKey,
    iri:    p.category,
    value:  p.pci_value !== undefined ? `${p.pci_value.toFixed(3)} d/yr` : "",
    coord:  `${latlng.lat.toFixed(3)}, ${latlng.lng.toFixed(3)}`,
    policy: p.policyRelevance || []
  });
}

async function showInfo({ title, iri, value, coord, time, policy }) {
  const panel = document.getElementById("info-panel");
  panel.hidden = false;
  document.getElementById("info-title").textContent = title;
  document.getElementById("info-iri").href = iri;
  document.getElementById("info-iri").textContent = "▸ " + iri;

  // Properties
  const dl = document.getElementById("info-properties");
  dl.innerHTML = "";
  const T = UI_STRINGS[state.lang];
  addProperty(dl, T.value, value);
  addProperty(dl, T.cell, coord);
  if (time) addProperty(dl, T.time || "Year", time);

  // Resolve ontology definition
  const concept = await resolveConcept(iri);
  document.getElementById("info-definition").textContent =
    concept?.definition?.[state.lang] || concept?.definition?.en || "";

  // Policy list
  const ul = document.getElementById("info-policy");
  ul.innerHTML = "";
  for (const pi of policy) {
    const li = document.createElement("li");
    const policyConcept = await resolveConcept(pi);
    const text = policyConcept?.label?.[state.lang] || policyConcept?.label?.en || pi;
    li.innerHTML = `<a href="${pi}" target="_blank">${text}</a>`;
    ul.appendChild(li);
  }
}

function addProperty(dl, key, value) {
  const dt = document.createElement("dt"); dt.textContent = key;
  const dd = document.createElement("dd"); dd.textContent = value;
  dl.appendChild(dt); dl.appendChild(dd);
}

// ---------------------------------------------------------------------------
// Ontology resolution (with caching)
// ---------------------------------------------------------------------------
async function resolveConcept(iri) {
  if (!iri) return null;
  if (state.ontologyCache.has(iri)) return state.ontologyCache.get(iri);

  // The IRI points to a SKOS concept; locally the TTL files are not directly
  // dereferenceable, so we use a side-car JSON file 'data/concepts.json' that
  // mirrors them. The build pipeline regenerates it.
  if (!window._conceptIndex) {
    window._conceptIndex = await fetch("data/concepts.json").then(r => r.json()).catch(() => ({}));
  }
  const found = window._conceptIndex[iri] || null;
  state.ontologyCache.set(iri, found);
  return found;
}

// ---------------------------------------------------------------------------
// Category styling
// ---------------------------------------------------------------------------
const CATEGORY_COLORS = {
  stable:         "#3B8BD4",
  mild_advance:   "#F2A623",
  strong_advance: "#E85D24",
  delay:          "#7F77DD"
};

const CATEGORY_LABELS = {
  stable: {
    en: "Stable", es: "Estable", zh: "稳定", ro: "Stabilă"
  },
  mild_advance: {
    en: "Mild advance", es: "Adelanto leve", zh: "轻微提前", ro: "Avans ușor"
  },
  strong_advance: {
    en: "Strong advance", es: "Adelanto fuerte", zh: "强烈提前", ro: "Avans puternic"
  },
  delay: {
    en: "Delay", es: "Retraso", zh: "延迟", ro: "Întârziere"
  }
};

function categoryColor(key) { return CATEGORY_COLORS[key] || "#888"; }
