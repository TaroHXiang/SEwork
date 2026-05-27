const authView = document.querySelector("#authView");
const hubView = document.querySelector("#hubView");
const mainView = document.querySelector("#mainView");

const authMessage = document.querySelector("#authMessage");
const loginBtn = document.querySelector("#loginBtn");
const registerBtn = document.querySelector("#registerBtn");
const logoutBtn = document.querySelector("#logoutBtn");
const hubLogoutBtn = document.querySelector("#hubLogoutBtn");
const currentUserLabel = document.querySelector("#currentUserLabel");
const hubCurrentUserLabel = document.querySelector("#hubCurrentUserLabel");

const historyCards = document.querySelector("#historyCards");
const hubHistoryMessage = document.querySelector("#hubHistoryMessage");
const hubDataPath = document.querySelector("#hubDataPath");
const openNewDatasetBtn = document.querySelector("#openNewDatasetBtn");
const hubNewDatasetMessage = document.querySelector("#hubNewDatasetMessage");

const backToHubBtn = document.querySelector("#backToHubBtn");
const currentDatasetLabel = document.querySelector("#currentDatasetLabel");
const dataPathInput = document.querySelector("#dataPath");
const inspectDataBtn = document.querySelector("#inspectDataBtn");
const buildIndexBtn = document.querySelector("#buildIndexBtn");
const indexStatus = document.querySelector("#indexStatus");
const healthBadge = document.querySelector("#healthBadge");
const healthText = document.querySelector("#healthText");
const datasetInfo = document.querySelector("#datasetInfo");
const indexBuildProgress = document.querySelector("#indexBuildProgress");
const indexBuildProgressBar = document.querySelector("#indexBuildProgressBar");
const indexBuildProgressMeta = document.querySelector("#indexBuildProgressMeta");

const filterCellType = document.querySelector("#filterCellType");
const filterDisease = document.querySelector("#filterDisease");
const filterAgeGroup = document.querySelector("#filterAgeGroup");
const filterSex = document.querySelector("#filterSex");
const filterTissue = document.querySelector("#filterTissue");
const filterDonorId = document.querySelector("#filterDonorId");

const cellIdInput = document.querySelector("#cellId");
const topKIdInput = document.querySelector("#topKId");
const queryVectorInput = document.querySelector("#queryVector");
const topKVectorInput = document.querySelector("#topKVector");
const searchByIdBtn = document.querySelector("#searchByIdBtn");
const searchByVectorBtn = document.querySelector("#searchByVectorBtn");
const queryStatus = document.querySelector("#queryStatus");
const evaluateToggle = document.querySelector("#evaluateToggle");
const evaluationSummary = document.querySelector("#evaluationSummary");

const umapLegend = document.querySelector("#umapLegend");
const resetUmapBtn = document.querySelector("#resetUmapBtn");
const umapChartElement = document.querySelector("#umapChart");

const queryModeMetric = document.querySelector("#queryModeMetric");
const resultCountMetric = document.querySelector("#resultCountMetric");
const queryTimeMetric = document.querySelector("#queryTimeMetric");
const highlightMetric = document.querySelector("#highlightMetric");
const precisionMetric = document.querySelector("#precisionMetric");
const recallMetric = document.querySelector("#recallMetric");
const annTimeMetric = document.querySelector("#annTimeMetric");
const exactTimeMetric = document.querySelector("#exactTimeMetric");
const resultsBody = document.querySelector("#resultsBody");

const UMAP_LIMIT = 10000;
const HIGHLIGHT_LIMIT = 100;
const BUILD_JOB_POLL_MS = 1200;

const METADATA_FILTER_FIELDS = [
  { key: "cell_type", element: filterCellType, label: "Cell Type" },
  { key: "disease", element: filterDisease, label: "Disease" },
  { key: "AgeGroup", element: filterAgeGroup, label: "Age Group" },
  { key: "sex", element: filterSex, label: "Sex" },
  { key: "tissue", element: filterTissue, label: "Tissue" },
  { key: "donor_id", element: filterDonorId, label: "Donor ID" },
];

const state = {
  authToken: localStorage.getItem("authToken") || "",
  currentUser: parseJson(localStorage.getItem("currentUser")),
  historyIndexes: [],
  activeIndex: null,
  currentDataPath: "",
  currentDatasetInfo: null,
  metadataOptions: {},
  umapChart: null,
  umapPoints: [],
  umapBaseSeries: [],
  umapPointByCellId: new Map(),
  umapMeta: null,
  buildJobId: null,
  buildPollTimer: null,
  buildJobContextPath: "",
};

function parseJson(raw) {
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function escapeHtml(value) {
  return String(value ?? "-")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "--";
  const num = Number(value);
  return Number.isFinite(num) ? num.toLocaleString() : String(value);
}

function formatMetric(value) {
  if (value === null || value === undefined || value === "") return "--";
  const num = Number(value);
  if (!Number.isFinite(num)) return String(value);
  return num % 1 === 0 ? num.toString() : num.toFixed(6);
}

function formatTime(value) {
  if (value === null || value === undefined || value === "") return "--";
  const num = Number(value);
  return Number.isFinite(num) ? `${num.toFixed(2)} ms` : String(value);
}

function formatRate(value) {
  if (value === null || value === undefined || value === "") return "--";
  const num = Number(value);
  return Number.isFinite(num) ? `${(num * 100).toFixed(2)}%` : "--";
}

function formatEtaSeconds(value) {
  if (value === null || value === undefined || value === "") return "--";
  const num = Number(value);
  return Number.isFinite(num) ? `${num.toFixed(1)} s` : String(value);
}

function trimText(value) {
  return String(value || "").trim();
}

function inferFormat(pathValue) {
  const path = trimText(pathValue);
  if (!path.includes(".")) return "-";
  return path.split(".").pop().toLowerCase();
}

function shortPath(pathValue) {
  const path = trimText(pathValue);
  if (!path) return "--";
  const normalized = path.replaceAll("\\", "/");
  const segments = normalized.split("/");
  if (segments.length <= 2) return path;
  return segments.slice(-2).join("/");
}

function setMessage(element, message, tone = "neutral", classSuffix = "") {
  if (!element) return;
  const className =
    tone === "success"
      ? "status-message success-message"
      : tone === "error"
        ? "status-message error-message"
        : "status-message neutral-message";
  element.className = `${className}${classSuffix ? ` ${classSuffix}` : ""}`;
  element.textContent = message;
}

function setBadgeState(mode, text, note) {
  healthBadge.className = `status-badge ${mode}`;
  healthBadge.textContent = text;
  healthText.textContent = note;
}

function setQueryMetrics({ mode = "Idle", resultCount = 0, queryTime = null, highlightCount = 0 } = {}) {
  queryModeMetric.textContent = mode;
  resultCountMetric.textContent = formatNumber(resultCount);
  queryTimeMetric.textContent = formatTime(queryTime);
  highlightMetric.textContent = formatNumber(highlightCount);
}

function clearEvaluationMetrics() {
  if (precisionMetric) precisionMetric.textContent = "--";
  if (recallMetric) recallMetric.textContent = "--";
  if (annTimeMetric) annTimeMetric.textContent = "--";
  if (exactTimeMetric) exactTimeMetric.textContent = "--";
}

function setEvaluationIdleMessage(enabled) {
  if (!evaluationSummary) return;
  if (enabled) {
    setMessage(
      evaluationSummary,
      "Exact evaluation enabled. Query will run ANN + exact baseline.",
      "neutral"
    );
    return;
  }
  setMessage(evaluationSummary, "Exact evaluation is off. Query runs ANN only.", "neutral");
}

function setEvaluationMetrics(evaluation = null) {
  if (!evaluation) {
    clearEvaluationMetrics();
    return;
  }

  if (precisionMetric) precisionMetric.textContent = formatRate(evaluation.precision_at_k);
  if (recallMetric) recallMetric.textContent = formatRate(evaluation.recall_at_k);
  if (annTimeMetric) annTimeMetric.textContent = formatTime(evaluation.ann_query_time_ms);
  if (exactTimeMetric) exactTimeMetric.textContent = formatTime(evaluation.exact_query_time_ms);
}

function refreshEvaluationUI(evaluation = null, enabledOverride = null) {
  const enabled = enabledOverride === null ? Boolean(evaluateToggle?.checked) : Boolean(enabledOverride);
  if (evaluation) {
    setEvaluationMetrics(evaluation);
    if (evaluationSummary) {
      setMessage(
        evaluationSummary,
        `Evaluation done: P@K ${formatRate(evaluation.precision_at_k)}, R@K ${formatRate(evaluation.recall_at_k)}, overlap ${formatNumber(evaluation.overlap_count)}`,
        "success"
      );
    }
    return;
  }

  clearEvaluationMetrics();
  setEvaluationIdleMessage(enabled);
}

function setEvaluationRunningMessage() {
  if (!evaluationSummary) return;
  clearEvaluationMetrics();
  setMessage(evaluationSummary, "Running ANN + exact evaluation...", "neutral");
}

function clearBuildPolling() {
  if (state.buildPollTimer) {
    window.clearInterval(state.buildPollTimer);
    state.buildPollTimer = null;
  }
  state.buildJobId = null;
  state.buildJobContextPath = "";
}

async function requestJson(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (state.authToken) {
    headers.Authorization = `Bearer ${state.authToken}`;
  }

  const response = await fetch(url, { ...options, headers });
  const rawText = await response.text();
  let data = {};
  if (rawText) {
    try {
      data = JSON.parse(rawText);
    } catch {
      throw new Error("Failed to parse server response");
    }
  }
  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

function getJson(url) {
  return requestJson(url);
}

function postJson(url, payload) {
  return requestJson(url, {
    method: "POST",
    body: JSON.stringify(payload || {}),
  });
}

function showAuthView() {
  authView.classList.remove("d-none");
  hubView.classList.add("d-none");
  mainView.classList.add("d-none");
}

function showHubView() {
  authView.classList.add("d-none");
  hubView.classList.remove("d-none");
  mainView.classList.add("d-none");
  const userLabel = state.currentUser
    ? `${state.currentUser.username} (${state.currentUser.role})`
    : "--";
  hubCurrentUserLabel.textContent = userLabel;
}

function showMainView() {
  authView.classList.add("d-none");
  hubView.classList.add("d-none");
  mainView.classList.remove("d-none");
  const userLabel = state.currentUser
    ? `${state.currentUser.username} (${state.currentUser.role})`
    : "--";
  currentUserLabel.textContent = userLabel;
  window.requestAnimationFrame(() => {
    initUmapChartIfNeeded();
    if (state.umapChart) state.umapChart.resize();
  });
}

function saveSession(token, user) {
  state.authToken = token;
  state.currentUser = user;
  localStorage.setItem("authToken", token);
  localStorage.setItem("currentUser", JSON.stringify(user));
}

function clearSession() {
  clearBuildPolling();
  state.authToken = "";
  state.currentUser = null;
  state.activeIndex = null;
  state.currentDataPath = "";
  state.currentDatasetInfo = null;
  localStorage.removeItem("authToken");
  localStorage.removeItem("currentUser");
  showAuthView();
}

function normalizeDatasetInfo(raw = {}, fallbackPath = "") {
  return {
    source_path: raw.source_path || raw.data_path || fallbackPath || "-",
    format: raw.format || raw.source_format || inferFormat(raw.source_path || raw.data_path || fallbackPath),
    cell_count: raw.cell_count ?? raw.total_points ?? null,
    gene_count: raw.gene_count ?? null,
    vector_dim: raw.vector_dim ?? null,
    embedding_key: raw.embedding_key || "-",
    visualization_source: raw.visualization_source || "-",
    metadata_columns: raw.metadata_columns || raw.metadata_keys || [],
  };
}

function renderDatasetInfo(info = {}) {
  const fields = [
    ["Path", info.source_path || "-"],
    ["Format", info.format || "-"],
    ["Cells", formatNumber(info.cell_count)],
    ["Genes", formatNumber(info.gene_count)],
    ["Vector Dim", formatNumber(info.vector_dim)],
    ["Embedding", info.embedding_key || "-"],
    ["Viz Source", info.visualization_source || "-"],
  ];
  datasetInfo.innerHTML = fields
    .map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`)
    .join("");
}

function setCurrentDataset(pathValue) {
  state.currentDataPath = trimText(pathValue);
  currentDatasetLabel.textContent = shortPath(state.currentDataPath);
  if (state.currentDataPath) {
    dataPathInput.value = state.currentDataPath;
    hubDataPath.value = state.currentDataPath;
  }
}

function setSelectOptions(selectElement, values, label) {
  if (!selectElement) return;

  const previousValue = selectElement.value;
  const normalizedValues = Array.from(new Set((values || []).map((v) => trimText(v)).filter(Boolean)));

  selectElement.innerHTML = "";
  const allOption = document.createElement("option");
  allOption.value = "";
  allOption.textContent = "All";
  selectElement.appendChild(allOption);

  for (const value of normalizedValues) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    selectElement.appendChild(option);
  }

  selectElement.value = previousValue && normalizedValues.includes(previousValue) ? previousValue : "";
  selectElement.title =
    normalizedValues.length === 0
      ? `${label}: no options in current dataset`
      : `${label}: ${normalizedValues.length} options`;
}

function resetMetadataFilters() {
  for (const field of METADATA_FILTER_FIELDS) {
    setSelectOptions(field.element, [], field.label);
  }
  state.metadataOptions = {};
}

async function loadMetadataOptionsForCurrentDataset() {
  if (!state.currentDataPath) {
    resetMetadataFilters();
    return;
  }

  const fieldNames = METADATA_FILTER_FIELDS.map((item) => item.key).join(",");
  const indexQuery = state.activeIndex?.id ? `&index_id=${encodeURIComponent(state.activeIndex.id)}` : "";
  try {
    const data = await getJson(
      `/api/dataset/metadata-options?data_path=${encodeURIComponent(state.currentDataPath)}&fields=${encodeURIComponent(fieldNames)}&max_values=200${indexQuery}`
    );

    state.metadataOptions = data.options || {};
    for (const field of METADATA_FILTER_FIELDS) {
      setSelectOptions(field.element, state.metadataOptions[field.key] || [], field.label);
    }

    const truncatedFields = Array.isArray(data.truncated_fields) ? data.truncated_fields : [];
    if (truncatedFields.length) {
      setMessage(
        queryStatus,
        `Metadata options are large, truncated to first 200 values: ${truncatedFields.join(", ")}`,
        "neutral"
      );
    }
  } catch (error) {
    resetMetadataFilters();
    setMessage(queryStatus, `Metadata options load failed: ${error.message}`, "neutral");
  }
}

function setIndexProgressVisible(visible) {
  indexBuildProgress.classList.toggle("d-none", !visible);
}

function updateIndexProgress(job) {
  const progress = Math.max(0, Math.min(100, Number(job.progress_pct) || 0));
  indexBuildProgressBar.style.width = `${progress.toFixed(1)}%`;
  indexBuildProgressBar.textContent = `${progress.toFixed(1)}%`;

  const meta = [];
  if (job.stage) meta.push(`stage: ${job.stage}`);
  if (job.total_cells !== null && job.total_cells !== undefined) {
    meta.push(`processed: ${formatNumber(job.processed_cells)} / ${formatNumber(job.total_cells)}`);
  }
  if (job.eta_seconds !== null && job.eta_seconds !== undefined) {
    meta.push(`eta: ${formatEtaSeconds(job.eta_seconds)}`);
  }
  indexBuildProgressMeta.textContent = meta.join(" | ");
}

function activeFilters() {
  const filters = {};
  for (const field of METADATA_FILTER_FIELDS) {
    const value = trimText(field.element?.value);
    if (value) filters[field.key] = value;
  }
  return filters;
}

function positiveTopK(inputElement) {
  const topK = Number(inputElement.value);
  if (!Number.isInteger(topK) || topK < 1 || topK > 100) {
    throw new Error("Top-K must be an integer between 1 and 100");
  }
  return topK;
}

function parseVectorInput() {
  const raw = trimText(queryVectorInput.value);
  if (!raw) throw new Error("Query vector is required");
  const vector = raw
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean)
    .map((v) => Number(v));
  if (!vector.length || vector.some((v) => !Number.isFinite(v))) {
    throw new Error("Invalid vector format");
  }
  return vector;
}

function ensureIndexSelected() {
  if (!state.activeIndex || !state.activeIndex.id) {
    throw new Error("No active index. Build or activate an index first.");
  }
}

function isBuildContextCurrent() {
  return trimText(state.currentDataPath) === trimText(state.buildJobContextPath);
}

function initUmapChartIfNeeded() {
  if (state.umapChart || !window.echarts || !umapChartElement) return;
  state.umapChart = window.echarts.init(umapChartElement, null, { renderer: "canvas" });
  state.umapChart.setOption(buildUmapOption([], []));
  window.addEventListener("resize", () => {
    if (state.umapChart) state.umapChart.resize();
  });
}

function buildUmapOption(baseData, highlightData) {
  return {
    animation: false,
    grid: { left: 12, right: 34, top: 12, bottom: 36, containLabel: false },
    dataZoom: [
      {
        type: "inside",
        xAxisIndex: 0,
        filterMode: "none",
        zoomOnMouseWheel: "ctrl",
        moveOnMouseWheel: true,
        moveOnMouseMove: true,
      },
      {
        type: "inside",
        yAxisIndex: 0,
        filterMode: "none",
        zoomOnMouseWheel: "ctrl",
        moveOnMouseWheel: true,
        moveOnMouseMove: true,
      },
      {
        type: "slider",
        xAxisIndex: 0,
        height: 16,
        left: 12,
        right: 34,
        bottom: 8,
      },
      {
        type: "slider",
        yAxisIndex: 0,
        width: 16,
        top: 12,
        right: 8,
        bottom: 36,
      },
    ],
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(15,23,42,0.92)",
      borderColor: "rgba(6,182,212,0.28)",
      textStyle: { color: "#e2e8f0" },
      formatter(params) {
        if (params.seriesName === "Hits") {
          const rank = params.data?.value?.[2] ?? "-";
          const score = params.data?.score;
          const distance = params.data?.distance;
          const scorePart = score !== undefined ? `<br>score=${escapeHtml(formatMetric(score))}` : "";
          const distancePart =
            distance !== undefined ? `<br>distance=${escapeHtml(formatMetric(distance))}` : "";
          return `cell_id: ${escapeHtml(params.data?.cell_id || "-")}<br>rank: #${escapeHtml(rank)}${scorePart}${distancePart}`;
        }
        const metadata = params.data?.metadata || {};
        const metadataText = Object.entries(metadata)
          .slice(0, 3)
          .map(([k, v]) => `${escapeHtml(k)}: ${escapeHtml(v)}`)
          .join("<br>");
        return `cell_id: ${escapeHtml(params.data?.cell_id || "-")}<br>x=${params.value[0].toFixed(3)}<br>y=${params.value[1].toFixed(3)}${metadataText ? `<br>${metadataText}` : ""}`;
      },
    },
    xAxis: {
      type: "value",
      scale: true,
      axisLine: { lineStyle: { color: "rgba(148,163,184,0.28)" } },
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
      name: "UMAP-1",
      nameLocation: "middle",
      nameGap: 22,
      nameTextStyle: { color: "#94a3b8" },
    },
    yAxis: {
      type: "value",
      scale: true,
      axisLine: { lineStyle: { color: "rgba(148,163,184,0.28)" } },
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
      name: "UMAP-2",
      nameLocation: "middle",
      nameGap: 30,
      nameRotate: 90,
      nameTextStyle: { color: "#94a3b8" },
    },
    series: [
      {
        name: "All Cells",
        type: "scatter",
        large: true,
        largeThreshold: 4000,
        progressive: 6000,
        progressiveThreshold: 10000,
        data: baseData,
        symbolSize: 3.8,
        itemStyle: {
          color: "rgba(125,211,252,0.70)",
          opacity: 0.7,
        },
      },
      {
        name: "Hits",
        type: "scatter",
        data: highlightData,
        symbolSize(value) {
          return 12 - Math.min((value?.[2] || 1) - 1, 7) * 0.75;
        },
        itemStyle: {
          color: "#ef4444",
          borderWidth: 0,
          shadowBlur: 12,
          shadowColor: "rgba(239,68,68,0.45)",
        },
        z: 20,
      },
    ],
  };
}

function setDefaultUmapLegend() {
  if (!state.umapMeta || state.umapPoints.length === 0) {
    umapLegend.textContent = "No visualization data";
    return;
  }
  const total = state.umapMeta.total_points ?? state.umapPoints.length;
  const returned = state.umapMeta.returned_points ?? state.umapPoints.length;
  const source = state.umapMeta.visualization_source || "unknown";
  const sampled = state.umapMeta.sampled ? " | sampled" : "";
  umapLegend.textContent = `total ${formatNumber(total)} | shown ${formatNumber(returned)} | ${source}${sampled}`;
}

function applyUmapData(payload = {}) {
  const rawPoints = Array.isArray(payload.points) ? payload.points : [];
  state.umapPoints = rawPoints.map((item) => ({
    cell_id: String(item.cell_id ?? ""),
    x: Number(item.x) || 0,
    y: Number(item.y) || 0,
    metadata: item.metadata || {},
  }));

  state.umapPointByCellId.clear();
  for (const p of state.umapPoints) {
    if (p.cell_id) state.umapPointByCellId.set(p.cell_id, p);
  }

  state.umapBaseSeries = state.umapPoints.map((p) => ({
    value: [p.x, p.y],
    cell_id: p.cell_id,
    metadata: p.metadata,
  }));

  state.umapMeta = {
    total_points: payload.total_points,
    returned_points: payload.returned_points ?? state.umapPoints.length,
    sampled: Boolean(payload.sampled),
    visualization_source: payload.visualization_source || "unknown",
  };

  initUmapChartIfNeeded();
  if (state.umapChart) {
    state.umapChart.setOption(buildUmapOption(state.umapBaseSeries, []), true);
  }
  setDefaultUmapLegend();
}

function clearUmapHighlights() {
  if (!state.umapChart) return;
  state.umapChart.setOption({
    series: [{ data: state.umapBaseSeries }, { data: [] }],
  });
  setDefaultUmapLegend();
  highlightMetric.textContent = "0";
}

function applyUmapHighlights(results = [], modeLabel = "Query") {
  if (!state.umapChart) return 0;
  let missingCount = 0;
  const highlights = [];

  for (const [index, item] of results.slice(0, HIGHLIGHT_LIMIT).entries()) {
    const base = state.umapPointByCellId.get(item.cell_id);
    const viz = item?.viz || {};
    let x = base?.x;
    let y = base?.y;
    if ((x === undefined || y === undefined) && viz && viz.x !== undefined && viz.y !== undefined) {
      const vx = Number(viz.x);
      const vy = Number(viz.y);
      if (Number.isFinite(vx) && Number.isFinite(vy)) {
        x = vx;
        y = vy;
      }
    }

    if (x === undefined || y === undefined) {
      missingCount += 1;
      continue;
    }

    highlights.push({
      value: [x, y, index + 1],
      cell_id: item.cell_id,
      score: item.score,
      distance: item.distance,
    });
  }

  state.umapChart.setOption({
    series: [{ data: state.umapBaseSeries }, { data: highlights }],
  });

  const total = state.umapMeta?.total_points ?? state.umapPoints.length;
  umapLegend.textContent =
    missingCount > 0
      ? `total ${formatNumber(total)} | ${modeLabel} highlights ${highlights.length} | missing ${missingCount}`
      : `total ${formatNumber(total)} | ${modeLabel} highlights ${highlights.length}`;
  return highlights.length;
}

async function setTableHtmlWithTransition(html) {
  resultsBody.classList.add("is-updating");
  await sleep(160);
  resultsBody.innerHTML = html;
  const rows = resultsBody.querySelectorAll("tr");
  rows.forEach((row) => row.classList.add("row-enter"));
  window.requestAnimationFrame(() => {
    resultsBody.classList.remove("is-updating");
  });
}

async function showTableState(message, tone = "neutral") {
  const stateClass = tone === "error" ? "table-state is-error" : "table-state";
  await setTableHtmlWithTransition(`<tr><td colspan="8" class="${stateClass}">${escapeHtml(message)}</td></tr>`);
}

async function renderResults(results = []) {
  if (!Array.isArray(results) || results.length === 0) {
    await showTableState("No results. Adjust query or filters.");
    return;
  }

  const html = results
    .map((item, idx) => {
      const md = item.metadata || {};
      return `
        <tr>
          <td>${idx + 1}</td>
          <td class="cell-id">${escapeHtml(item.cell_id)}</td>
          <td>${escapeHtml(formatMetric(item.distance))}</td>
          <td>${escapeHtml(formatMetric(item.score))}</td>
          <td>${escapeHtml(md.cell_type || "-")}</td>
          <td>${escapeHtml(md.disease || "-")}</td>
          <td>${escapeHtml(md.AgeGroup || "-")}</td>
          <td>${escapeHtml(md.sex || "-")}</td>
        </tr>
      `;
    })
    .join("");

  await setTableHtmlWithTransition(html);
}

function resetMainPageOutputs() {
  setQueryMetrics();
  setMessage(queryStatus, "Ready for query", "neutral");
  refreshEvaluationUI();
  showTableState("No query results yet. Build/activate an index then query.").catch(() => undefined);
  clearUmapHighlights();
}

async function loadHistoryIndexes() {
  setMessage(hubHistoryMessage, "Loading history indexes...", "neutral");
  historyCards.innerHTML = "";
  try {
    const data = await getJson("/api/indexes");
    state.historyIndexes = Array.isArray(data.indexes) ? data.indexes : [];
    renderHistoryCards(state.historyIndexes);
  } catch (error) {
    setMessage(hubHistoryMessage, error.message, "error");
  }
}

function renderHistoryCards(indexes) {
  if (!indexes.length) {
    historyCards.innerHTML = "";
    setMessage(hubHistoryMessage, "No history index. Build one first.", "neutral");
    return;
  }

  setMessage(hubHistoryMessage, `${indexes.length} history indexes found`, "success");
  historyCards.innerHTML = indexes
    .map((item) => {
      const statusLabel = item.is_active ? "Active" : "History";
      return `
        <article class="history-card">
          <h3 class="history-card-title">${escapeHtml(item.index_name)}</h3>
          <p class="history-card-subtitle">${escapeHtml(statusLabel)} | updated ${escapeHtml(item.updated_at || "-")}</p>
          <dl class="history-card-meta">
            <dt>Data Path</dt><dd>${escapeHtml(item.data_path || "-")}</dd>
            <dt>Collection</dt><dd>${escapeHtml(item.collection_name || "-")}</dd>
            <dt>Format</dt><dd>${escapeHtml(item.source_format || "-")}</dd>
            <dt>Cells</dt><dd>${escapeHtml(formatNumber(item.cell_count))}</dd>
            <dt>Vector Dim</dt><dd>${escapeHtml(formatNumber(item.vector_dim))}</dd>
            <dt>Build Time</dt><dd>${escapeHtml(formatTime(item.build_time_ms))}</dd>
          </dl>
          <button class="btn action-btn secondary-btn btn-sm mt-2" data-open-index="${item.id}">Open</button>
        </article>
      `;
    })
    .join("");

  for (const btn of historyCards.querySelectorAll("[data-open-index]")) {
    btn.addEventListener("click", async () => {
      const indexId = Number(btn.dataset.openIndex);
      if (!Number.isInteger(indexId) || indexId <= 0) return;
      btn.disabled = true;
      try {
        await openHistoryIndex(indexId);
      } finally {
        btn.disabled = false;
      }
    });
  }
}

async function openHistoryIndex(indexId) {
  setMessage(hubHistoryMessage, "Activating selected index...", "neutral");
  const data = await postJson(`/api/indexes/${indexId}/activate`, {});
  const indexRecord = data.index;
  state.activeIndex = indexRecord;

  await enterCorePage({
    dataPath: indexRecord?.data_path || "",
    info: normalizeDatasetInfo(indexRecord, indexRecord?.data_path),
    indexRecord,
  });

  setMessage(hubHistoryMessage, "Index opened", "success");
}

async function openNewDatasetFromHub() {
  const path = trimText(hubDataPath.value);
  if (!path) {
    setMessage(hubNewDatasetMessage, "Please input data path", "error");
    return;
  }

  openNewDatasetBtn.disabled = true;
  setMessage(hubNewDatasetMessage, "Checking dataset...", "neutral");
  try {
    const infoRaw = await postJson("/api/dataset/inspect", { data_path: path });
    state.activeIndex = null;
    await enterCorePage({
      dataPath: path,
      info: normalizeDatasetInfo(infoRaw, path),
      indexRecord: null,
    });
    setMessage(hubNewDatasetMessage, "Opened core page", "success");
  } catch (error) {
    setMessage(hubNewDatasetMessage, error.message, "error");
  } finally {
    openNewDatasetBtn.disabled = false;
  }
}

async function enterCorePage({ dataPath, info, indexRecord }) {
  setCurrentDataset(dataPath);
  state.currentDatasetInfo = normalizeDatasetInfo(info || {}, state.currentDataPath);
  state.activeIndex = indexRecord || null;
  renderDatasetInfo(state.currentDatasetInfo);

  showMainView();
  resetMainPageOutputs();
  setIndexProgressVisible(false);
  indexBuildProgressBar.style.width = "0%";
  indexBuildProgressBar.textContent = "0%";
  indexBuildProgressMeta.textContent = "";

  if (state.activeIndex?.id) {
    setBadgeState("is-ready", "Index Ready", "Top-K query available");
    setMessage(indexStatus, `Loaded index: ${state.activeIndex.index_name}`, "success");
  } else {
    setBadgeState("is-idle", "No Index", "UMAP available, build index when needed");
    setMessage(indexStatus, "No active index for current dataset", "neutral");
  }

  await Promise.all([
    loadUmapForCurrentDataset(),
    loadMetadataOptionsForCurrentDataset(),
  ]);
}

async function loadUmapForCurrentDataset() {
  if (!state.currentDataPath) {
    applyUmapData({ points: [], returned_points: 0, total_points: 0, visualization_source: "none" });
    setMessage(queryStatus, "No data path for UMAP", "error");
    return;
  }

  umapLegend.textContent = "Loading UMAP...";
  try {
    const preview = await getJson(
      `/api/dataset/umap-preview?data_path=${encodeURIComponent(state.currentDataPath)}&limit=${UMAP_LIMIT}`
    );
    applyUmapData(preview);
    state.currentDatasetInfo = normalizeDatasetInfo(
      { ...state.currentDatasetInfo, ...preview },
      state.currentDataPath
    );
    renderDatasetInfo(state.currentDatasetInfo);
    return;
  } catch (previewError) {
    if (state.activeIndex?.id) {
      try {
        const indexed = await getJson(
          `/api/visualization/umap?index_id=${encodeURIComponent(state.activeIndex.id)}&limit=${UMAP_LIMIT}`
        );
        applyUmapData(indexed);
        setMessage(queryStatus, `Dataset preview failed, fallback to index payload: ${previewError.message}`, "neutral");
        return;
      } catch (indexError) {
        applyUmapData({ points: [], returned_points: 0, total_points: 0, visualization_source: "none" });
        setMessage(queryStatus, `UMAP load failed: ${indexError.message}`, "error");
        return;
      }
    }
    applyUmapData({ points: [], returned_points: 0, total_points: 0, visualization_source: "none" });
    setMessage(queryStatus, `UMAP load failed: ${previewError.message}`, "error");
  }
}

async function inspectDatasetFromMain() {
  const path = trimText(dataPathInput.value);
  if (!path) {
    setMessage(indexStatus, "Please input data path", "error");
    return;
  }

  inspectDataBtn.disabled = true;
  setMessage(indexStatus, "Inspecting dataset...", "neutral");
  try {
    const raw = await postJson("/api/dataset/inspect", { data_path: path });
    const info = normalizeDatasetInfo(raw, path);
    const pathChanged = trimText(state.activeIndex?.data_path) !== path;
    if (pathChanged) {
      state.activeIndex = null;
      setBadgeState("is-idle", "No Index", "Dataset changed, build/activate index if needed");
    }
    setCurrentDataset(path);
    state.currentDatasetInfo = info;
    renderDatasetInfo(info);
    await Promise.all([
      loadUmapForCurrentDataset(),
      loadMetadataOptionsForCurrentDataset(),
    ]);
    setMessage(indexStatus, "Dataset inspected and UMAP refreshed", "success");
  } catch (error) {
    setMessage(indexStatus, error.message, "error");
  } finally {
    inspectDataBtn.disabled = false;
  }
}

async function fetchActiveIndexRecord(preferredId = null) {
  try {
    const active = await getJson("/api/indexes/active");
    if (active.index) return active.index;
  } catch {
    // ignore
  }

  try {
    const list = await getJson("/api/indexes");
    const indexes = Array.isArray(list.indexes) ? list.indexes : [];
    if (preferredId) {
      const matched = indexes.find((item) => Number(item.id) === Number(preferredId));
      if (matched) return matched;
    }
    return indexes.find((item) => item.is_active) || null;
  } catch {
    return null;
  }
}

async function handleBuildJobUpdate(job) {
  const applyToCurrentView = isBuildContextCurrent();
  if (applyToCurrentView) {
    setIndexProgressVisible(true);
    updateIndexProgress(job);
  }

  if (job.status === "queued" || job.status === "running") {
    if (applyToCurrentView) {
      setBadgeState("is-loading", "Building Index", "Writing vectors and creating HNSW");
      setMessage(indexStatus, job.message || "Build running...", "neutral");
    }
    return;
  }

  if (job.status === "failed") {
    clearBuildPolling();
    if (applyToCurrentView) {
      setBadgeState("is-error", "Build Failed", "Check data format or parameters");
      setMessage(indexStatus, job.error || job.message || "Index build failed", "error");
    }
    return;
  }

  if (job.status === "completed") {
    const builtIndexId = job?.result?.index_id;
    clearBuildPolling();
    const result = job.result || {};
    if (applyToCurrentView) {
      state.activeIndex = await fetchActiveIndexRecord(builtIndexId);
      state.currentDatasetInfo = normalizeDatasetInfo(
        { ...state.currentDatasetInfo, ...result },
        state.currentDataPath
      );
      renderDatasetInfo(state.currentDatasetInfo);
      setBadgeState("is-ready", "Index Ready", "Top-K query available");
      setMessage(
        indexStatus,
        `Index built: ${formatNumber(result.cell_count)} cells, ${formatTime(result.build_time_ms)}`,
        "success"
      );
      await loadMetadataOptionsForCurrentDataset();
    }
    await loadHistoryIndexes();
  }
}

async function pollBuildJob(jobId) {
  clearBuildPolling();
  state.buildJobId = jobId;

  const pollOnce = async () => {
    if (!state.buildJobId) return;
    try {
      const data = await getJson(`/api/index/build/jobs/${encodeURIComponent(jobId)}`);
      const job = data.job || {};
      await handleBuildJobUpdate(job);
      if (job.status === "completed" || job.status === "failed") {
        clearBuildPolling();
      }
    } catch (error) {
      clearBuildPolling();
      setBadgeState("is-error", "Progress Error", "Failed to get build progress");
      setMessage(indexStatus, error.message, "error");
    }
  };

  await pollOnce();
  if (!state.buildJobId) return;
  state.buildPollTimer = window.setInterval(() => {
    pollOnce().catch(() => undefined);
  }, BUILD_JOB_POLL_MS);
}

async function buildIndexFromMain() {
  const path = trimText(dataPathInput.value);
  if (!path) {
    setMessage(indexStatus, "Please input data path", "error");
    return;
  }

  buildIndexBtn.disabled = true;
  setCurrentDataset(path);
  state.activeIndex = null;
  state.buildJobContextPath = path;
  setBadgeState("is-loading", "Building Index", "Submitting async build task");
  setMessage(indexStatus, "Build job submitted...", "neutral");
  setIndexProgressVisible(true);
  updateIndexProgress({
    progress_pct: 0,
    stage: "queued",
    processed_cells: 0,
    total_cells: null,
    eta_seconds: null,
  });

  loadMetadataOptionsForCurrentDataset().catch(() => undefined);

  try {
    const response = await postJson("/api/index/build", {
      data_path: path,
      async: true,
      activate: true,
    });
    if (!response.job_id) {
      throw new Error("Build job id missing");
    }
    await pollBuildJob(response.job_id);
  } catch (error) {
    clearBuildPolling();
    setBadgeState("is-error", "Submit Failed", "Could not submit build task");
    setMessage(indexStatus, error.message, "error");
  } finally {
    buildIndexBtn.disabled = false;
  }
}

async function searchById() {
  try {
    ensureIndexSelected();
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    return;
  }

  const cellId = trimText(cellIdInput.value);
  if (!cellId) {
    setMessage(queryStatus, "cell_id is required", "error");
    await showTableState("Query failed: missing cell_id", "error");
    return;
  }

  let topK;
  try {
    topK = positiveTopK(topKIdInput);
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    return;
  }

  searchByIdBtn.disabled = true;
  setMessage(queryStatus, "Searching by ID...", "neutral");
  const evaluate = Boolean(evaluateToggle?.checked);
  if (evaluate) {
    setEvaluationRunningMessage();
  } else {
    refreshEvaluationUI(null, false);
  }
  setQueryMetrics({ mode: "Search by ID", resultCount: 0, queryTime: null, highlightCount: 0 });

  try {
    const data = await postJson("/api/search/by-id", {
      cell_id: cellId,
      top_k: topK,
      filters: activeFilters(),
      index_id: state.activeIndex.id,
      evaluate,
    });
    await renderResults(data.results);
    const highlightCount = applyUmapHighlights(data.results, "ID query");
    setQueryMetrics({
      mode: "Search by ID",
      resultCount: Array.isArray(data.results) ? data.results.length : 0,
      queryTime: data.query_time_ms,
      highlightCount,
    });
    setMessage(
      queryStatus,
      `Done: ${Array.isArray(data.results) ? data.results.length : 0} results, ${formatTime(data.query_time_ms)}`,
      "success"
    );
    refreshEvaluationUI(data.evaluation || null, evaluate);
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    clearUmapHighlights();
    setQueryMetrics({ mode: "Search by ID", resultCount: 0, queryTime: null, highlightCount: 0 });
    refreshEvaluationUI(null, evaluate);
  } finally {
    searchByIdBtn.disabled = false;
  }
}

async function searchByVector() {
  try {
    ensureIndexSelected();
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    return;
  }

  let vector;
  let topK;
  try {
    vector = parseVectorInput();
    topK = positiveTopK(topKVectorInput);
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    return;
  }

  searchByVectorBtn.disabled = true;
  setMessage(queryStatus, "Searching by vector...", "neutral");
  const evaluate = Boolean(evaluateToggle?.checked);
  if (evaluate) {
    setEvaluationRunningMessage();
  } else {
    refreshEvaluationUI(null, false);
  }
  setQueryMetrics({ mode: "Search by Vector", resultCount: 0, queryTime: null, highlightCount: 0 });

  try {
    const data = await postJson("/api/search/by-vector", {
      vector,
      top_k: topK,
      filters: activeFilters(),
      index_id: state.activeIndex.id,
      evaluate,
    });
    await renderResults(data.results);
    const highlightCount = applyUmapHighlights(data.results, "Vector query");
    setQueryMetrics({
      mode: "Search by Vector",
      resultCount: Array.isArray(data.results) ? data.results.length : 0,
      queryTime: data.query_time_ms,
      highlightCount,
    });
    setMessage(
      queryStatus,
      `Done: ${Array.isArray(data.results) ? data.results.length : 0} results, ${formatTime(data.query_time_ms)}`,
      "success"
    );
    refreshEvaluationUI(data.evaluation || null, evaluate);
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    clearUmapHighlights();
    setQueryMetrics({ mode: "Search by Vector", resultCount: 0, queryTime: null, highlightCount: 0 });
    refreshEvaluationUI(null, evaluate);
  } finally {
    searchByVectorBtn.disabled = false;
  }
}

function resetUmapView() {
  clearUmapHighlights();
  setMessage(queryStatus, "UMAP reset to default", "neutral");
}

async function checkAuthAndInit() {
  if (!state.authToken) {
    showAuthView();
    return;
  }
  try {
    const data = await getJson("/api/auth/me");
    state.currentUser = data.user;
    localStorage.setItem("currentUser", JSON.stringify(state.currentUser));
    showHubView();
    await loadHistoryIndexes();
  } catch {
    clearSession();
  }
}

loginBtn.addEventListener("click", async () => {
  loginBtn.disabled = true;
  setMessage(authMessage, "Logging in...", "neutral", "mb-3");
  authMessage.classList.remove("d-none");
  try {
    const payload = {
      username: trimText(document.querySelector("#authUsername").value),
      password: document.querySelector("#authPassword").value,
    };
    const data = await postJson("/api/auth/login", payload);
    saveSession(data.token, data.user);
    showHubView();
    await loadHistoryIndexes();
  } catch (error) {
    setMessage(authMessage, error.message, "error", "mb-3");
  } finally {
    loginBtn.disabled = false;
  }
});

registerBtn.addEventListener("click", async () => {
  registerBtn.disabled = true;
  setMessage(authMessage, "Registering...", "neutral", "mb-3");
  authMessage.classList.remove("d-none");
  try {
    const payload = {
      username: trimText(document.querySelector("#authUsername").value),
      password: document.querySelector("#authPassword").value,
      role: document.querySelector("input[name='authRole']:checked").value,
    };
    const data = await postJson("/api/auth/register", payload);
    setMessage(authMessage, `Registered: ${data.user.username}. Please login.`, "success", "mb-3");
  } catch (error) {
    setMessage(authMessage, error.message, "error", "mb-3");
  } finally {
    registerBtn.disabled = false;
  }
});

logoutBtn.addEventListener("click", clearSession);
hubLogoutBtn.addEventListener("click", clearSession);

openNewDatasetBtn.addEventListener("click", () => {
  openNewDatasetFromHub().catch((error) => {
    setMessage(hubNewDatasetMessage, error.message, "error");
  });
});

backToHubBtn.addEventListener("click", async () => {
  showHubView();
  await loadHistoryIndexes();
});

inspectDataBtn.addEventListener("click", () => {
  inspectDatasetFromMain().catch((error) => {
    setMessage(indexStatus, error.message, "error");
  });
});

buildIndexBtn.addEventListener("click", () => {
  buildIndexFromMain().catch((error) => {
    setMessage(indexStatus, error.message, "error");
  });
});

searchByIdBtn.addEventListener("click", () => {
  searchById().catch((error) => {
    setMessage(queryStatus, error.message, "error");
  });
});

searchByVectorBtn.addEventListener("click", () => {
  searchByVector().catch((error) => {
    setMessage(queryStatus, error.message, "error");
  });
});

resetUmapBtn.addEventListener("click", resetUmapView);

if (evaluateToggle) {
  evaluateToggle.addEventListener("change", () => {
    refreshEvaluationUI();
  });
}

setQueryMetrics();
refreshEvaluationUI();
showTableState("No query results yet. Build/activate an index then query.").catch(() => undefined);
checkAuthAndInit();
