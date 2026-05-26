const authView = document.querySelector("#authView");
const hubView = document.querySelector("#hubView");
const mainView = document.querySelector("#mainView");

const authMessage = document.querySelector("#authMessage");
const currentUserLabel = document.querySelector("#currentUserLabel");
const hubCurrentUserLabel = document.querySelector("#hubCurrentUserLabel");
const loginBtn = document.querySelector("#loginBtn");
const registerBtn = document.querySelector("#registerBtn");
const logoutBtn = document.querySelector("#logoutBtn");
const hubLogoutBtn = document.querySelector("#hubLogoutBtn");

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

const cellIdInput = document.querySelector("#cellId");
const topKIdInput = document.querySelector("#topKId");
const queryVectorInput = document.querySelector("#queryVector");
const topKVectorInput = document.querySelector("#topKVector");
const searchByIdBtn = document.querySelector("#searchByIdBtn");
const searchByVectorBtn = document.querySelector("#searchByVectorBtn");
const queryStatus = document.querySelector("#queryStatus");

const umapLegend = document.querySelector("#umapLegend");
const resetUmapBtn = document.querySelector("#resetUmapBtn");
const umapChartElement = document.querySelector("#umapChart");

const queryModeMetric = document.querySelector("#queryModeMetric");
const resultCountMetric = document.querySelector("#resultCountMetric");
const queryTimeMetric = document.querySelector("#queryTimeMetric");
const highlightMetric = document.querySelector("#highlightMetric");
const resultsBody = document.querySelector("#resultsBody");

const UMAP_LIMIT = 10000;
const HIGHLIGHT_LIMIT = 100;
const BUILD_JOB_POLL_MS = 1200;

const state = {
  authToken: localStorage.getItem("authToken") || "",
  currentUser: parseJson(localStorage.getItem("currentUser")),
  historyIndexes: [],
  activeIndex: null,
  currentDataPath: "",
  currentDatasetInfo: null,
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
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue.toLocaleString() : String(value);
}

function formatMetric(value) {
  if (value === null || value === undefined || value === "") return "--";
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return String(value);
  return numericValue % 1 === 0 ? numericValue.toString() : numericValue.toFixed(6);
}

function formatTime(value) {
  if (value === null || value === undefined || value === "") return "--";
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? `${numericValue.toFixed(2)} ms` : String(value);
}

function formatEtaSeconds(value) {
  if (value === null || value === undefined || value === "") return "--";
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? `${numericValue.toFixed(1)}s` : String(value);
}

function trimPath(pathValue) {
  return String(pathValue || "").trim();
}

function inferFormat(pathValue) {
  const path = trimPath(pathValue);
  if (!path.includes(".")) return "-";
  return path.split(".").pop().toLowerCase();
}

function shortPath(pathValue) {
  const path = trimPath(pathValue);
  if (!path) return "--";
  const normalized = path.replaceAll("\\", "/");
  const segments = normalized.split("/");
  if (segments.length <= 2) return path;
  return `${segments.slice(-2).join("/")}`;
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

function setQueryMetrics({ mode = "未查询", resultCount = 0, queryTime = null, highlightCount = 0 } = {}) {
  queryModeMetric.textContent = mode;
  resultCountMetric.textContent = formatNumber(resultCount);
  queryTimeMetric.textContent = formatTime(queryTime);
  highlightMetric.textContent = formatNumber(highlightCount);
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
      throw new Error("服务返回了无法解析的数据");
    }
  }
  if (!response.ok) {
    throw new Error(data.error || `请求失败 (${response.status})`);
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
    ? `${state.currentUser.username} (${state.currentUser.role === "admin" ? "管理员" : "普通用户"})`
    : "--";
  hubCurrentUserLabel.textContent = userLabel;
}

function showMainView() {
  authView.classList.add("d-none");
  hubView.classList.add("d-none");
  mainView.classList.remove("d-none");
  const userLabel = state.currentUser
    ? `${state.currentUser.username} (${state.currentUser.role === "admin" ? "管理员" : "普通用户"})`
    : "--";
  currentUserLabel.textContent = userLabel;
  window.requestAnimationFrame(() => {
    initUmapChartIfNeeded();
    if (state.umapChart) {
      state.umapChart.resize();
    }
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
    ["路径", info.source_path || "-"],
    ["格式", info.format || "-"],
    ["细胞数", formatNumber(info.cell_count)],
    ["基因数", formatNumber(info.gene_count)],
    ["向量维度", formatNumber(info.vector_dim)],
    ["向量来源", info.embedding_key || "-"],
    ["可视化来源", info.visualization_source || "-"],
  ];

  datasetInfo.innerHTML = fields
    .map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`)
    .join("");
}

function setCurrentDataset(pathValue) {
  state.currentDataPath = trimPath(pathValue);
  currentDatasetLabel.textContent = shortPath(state.currentDataPath);
  if (state.currentDataPath) {
    dataPathInput.value = state.currentDataPath;
    hubDataPath.value = state.currentDataPath;
  }
}

function setIndexProgressVisible(visible) {
  indexBuildProgress.classList.toggle("d-none", !visible);
}

function updateIndexProgress(job) {
  const progress = Math.max(0, Math.min(100, Number(job.progress_pct) || 0));
  indexBuildProgressBar.style.width = `${progress.toFixed(1)}%`;
  indexBuildProgressBar.textContent = `${progress.toFixed(1)}%`;

  const metaParts = [];
  if (job.stage) metaParts.push(`阶段: ${job.stage}`);
  if (Number.isFinite(Number(job.processed_cells)) || Number.isFinite(Number(job.total_cells))) {
    metaParts.push(`进度: ${formatNumber(job.processed_cells)} / ${formatNumber(job.total_cells)}`);
  }
  if (job.eta_seconds !== null && job.eta_seconds !== undefined) {
    metaParts.push(`ETA: ${formatEtaSeconds(job.eta_seconds)}`);
  }
  indexBuildProgressMeta.textContent = metaParts.join(" · ");
}

function activeFilters() {
  const filters = {};
  const cellType = trimPath(filterCellType.value);
  const disease = trimPath(filterDisease.value);
  const ageGroup = trimPath(filterAgeGroup.value);
  if (cellType) filters.cell_type = cellType;
  if (disease) filters.disease = disease;
  if (ageGroup) filters.AgeGroup = ageGroup;
  return filters;
}

function positiveTopK(inputElement) {
  const topK = Number(inputElement.value);
  if (!Number.isInteger(topK) || topK < 1 || topK > 100) {
    throw new Error("Top-K 必须是 1 到 100 的整数");
  }
  return topK;
}

function parseVectorInput() {
  const raw = trimPath(queryVectorInput.value);
  if (!raw) {
    throw new Error("请输入查询向量");
  }
  const vector = raw
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => Number(item));
  if (!vector.length || vector.some((item) => !Number.isFinite(item))) {
    throw new Error("向量格式错误，请输入逗号分隔的数字");
  }
  return vector;
}

function ensureIndexSelected() {
  if (!state.activeIndex || !state.activeIndex.id) {
    throw new Error("请先从历史中加载索引，或先构建索引");
  }
}

function isBuildContextCurrent() {
  return trimPath(state.currentDataPath) === trimPath(state.buildJobContextPath);
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
    grid: { left: 12, right: 12, top: 12, bottom: 12, containLabel: false },
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(15,23,42,0.92)",
      borderColor: "rgba(6,182,212,0.28)",
      textStyle: { color: "#e2e8f0" },
      formatter(params) {
        if (params.seriesName === "检索命中") {
          const rank = params.data?.value?.[2] ?? "-";
          const score = params.data?.score;
          const distance = params.data?.distance;
          const scorePart = score !== undefined ? `<br>score=${escapeHtml(formatMetric(score))}` : "";
          const distancePart =
            distance !== undefined ? `<br>distance=${escapeHtml(formatMetric(distance))}` : "";
          return `命中细胞: ${escapeHtml(params.data?.cell_id || "-")}<br>排名: #${escapeHtml(rank)}${scorePart}${distancePart}`;
        }
        const metadata = params.data?.metadata || {};
        const metadataEntries = Object.entries(metadata)
          .slice(0, 3)
          .map(([key, value]) => `${escapeHtml(key)}: ${escapeHtml(value)}`)
          .join("<br>");
        const metaBlock = metadataEntries ? `<br>${metadataEntries}` : "";
        return `细胞: ${escapeHtml(params.data?.cell_id || "-")}<br>x=${params.value[0].toFixed(3)}<br>y=${params.value[1].toFixed(3)}${metaBlock}`;
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
        name: "全部细胞",
        type: "scatterGL",
        progressive: 5000,
        progressiveThreshold: 10000,
        data: baseData,
        symbolSize: 2.6,
        itemStyle: {
          color: "rgba(56,189,248,0.78)",
          opacity: 0.78,
        },
      },
      {
        name: "检索命中",
        type: "scatter",
        data: highlightData,
        symbolSize(value) {
          return 12 - Math.min((value?.[2] || 1) - 1, 7) * 0.75;
        },
        itemStyle: {
          color: "#f8fafc",
          borderColor: "#ef4444",
          borderWidth: 2,
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
    umapLegend.textContent = "暂无可视化数据";
    return;
  }
  const totalPoints = state.umapMeta.total_points ?? state.umapPoints.length;
  const returnedPoints = state.umapMeta.returned_points ?? state.umapPoints.length;
  const source = state.umapMeta.visualization_source || "unknown";
  const sampled = state.umapMeta.sampled ? " · 抽样" : "";
  umapLegend.textContent = `总点数 ${formatNumber(totalPoints)} · 显示 ${formatNumber(returnedPoints)} · ${source}${sampled}`;
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
  for (const point of state.umapPoints) {
    if (point.cell_id) {
      state.umapPointByCellId.set(point.cell_id, point);
    }
  }

  state.umapBaseSeries = state.umapPoints.map((point) => ({
    value: [point.x, point.y],
    cell_id: point.cell_id,
    metadata: point.metadata,
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
    series: [
      { data: state.umapBaseSeries },
      { data: [] },
    ],
  });
  setDefaultUmapLegend();
  highlightMetric.textContent = "0";
}

function applyUmapHighlights(results = [], modeLabel = "查询") {
  if (!state.umapChart) return 0;

  let missingCount = 0;
  const highlights = [];
  for (const [index, item] of results.slice(0, HIGHLIGHT_LIMIT).entries()) {
    const point = state.umapPointByCellId.get(item.cell_id);
    if (!point) {
      missingCount += 1;
      continue;
    }
    highlights.push({
      value: [point.x, point.y, index + 1],
      cell_id: item.cell_id,
      score: item.score,
      distance: item.distance,
    });
  }

  state.umapChart.setOption({
    series: [
      { data: state.umapBaseSeries },
      { data: highlights },
    ],
  });

  if (!state.umapMeta || state.umapPoints.length === 0) {
    umapLegend.textContent = `${modeLabel} · 高亮 ${highlights.length}`;
  } else {
    const baseTotal = state.umapMeta.total_points ?? state.umapPoints.length;
    const missingLabel = missingCount > 0 ? ` · 未定位 ${missingCount}` : "";
    umapLegend.textContent = `总点数 ${formatNumber(baseTotal)} · ${modeLabel}高亮 ${highlights.length}${missingLabel}`;
  }
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
  await setTableHtmlWithTransition(
    `<tr><td colspan="8" class="${stateClass}">${escapeHtml(message)}</td></tr>`
  );
}

async function renderResults(results = []) {
  if (!Array.isArray(results) || results.length === 0) {
    await showTableState("没有匹配结果，请调整查询条件后重试");
    return;
  }

  const html = results
    .map((item, index) => {
      const metadata = item.metadata || {};
      return `
        <tr>
          <td>${index + 1}</td>
          <td class="cell-id">${escapeHtml(item.cell_id)}</td>
          <td>${escapeHtml(formatMetric(item.distance))}</td>
          <td>${escapeHtml(formatMetric(item.score))}</td>
          <td>${escapeHtml(metadata.cell_type || "-")}</td>
          <td>${escapeHtml(metadata.disease || "-")}</td>
          <td>${escapeHtml(metadata.AgeGroup || "-")}</td>
          <td>${escapeHtml(metadata.sex || "-")}</td>
        </tr>
      `;
    })
    .join("");

  await setTableHtmlWithTransition(html);
}

function resetMainPageOutputs() {
  setQueryMetrics();
  setMessage(queryStatus, "输入细胞 ID 或向量后即可执行相似检索", "neutral");
  showTableState("暂无查询结果，请先构建索引并执行查询").catch(() => undefined);
  clearUmapHighlights();
}

async function loadHistoryIndexes() {
  setMessage(hubHistoryMessage, "正在加载历史索引...", "neutral");
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
    setMessage(hubHistoryMessage, "暂无历史索引，请先录入数据集并构建索引", "neutral");
    return;
  }

  setMessage(hubHistoryMessage, `共 ${indexes.length} 条历史记录，点击“进入”即可打开`, "success");
  historyCards.innerHTML = indexes
    .map((item) => {
      const statusLabel = item.is_active ? "当前激活" : "历史索引";
      return `
        <article class="history-card">
          <h3 class="history-card-title">${escapeHtml(item.index_name)}</h3>
          <p class="history-card-subtitle">${escapeHtml(statusLabel)} · 更新 ${escapeHtml(item.updated_at || "-")}</p>
          <dl class="history-card-meta">
            <dt>数据路径</dt><dd>${escapeHtml(item.data_path || "-")}</dd>
            <dt>索引位置</dt><dd>${escapeHtml(item.collection_name || "-")}</dd>
            <dt>格式</dt><dd>${escapeHtml(item.source_format || "-")}</dd>
            <dt>细胞数</dt><dd>${escapeHtml(formatNumber(item.cell_count))}</dd>
            <dt>向量维度</dt><dd>${escapeHtml(formatNumber(item.vector_dim))}</dd>
            <dt>构建耗时</dt><dd>${escapeHtml(formatTime(item.build_time_ms))}</dd>
          </dl>
          <button class="btn action-btn secondary-btn btn-sm mt-2" data-open-index="${item.id}">进入</button>
        </article>
      `;
    })
    .join("");

  for (const button of historyCards.querySelectorAll("[data-open-index]")) {
    button.addEventListener("click", async () => {
      const indexId = Number(button.dataset.openIndex);
      if (!Number.isInteger(indexId) || indexId <= 0) return;
      button.disabled = true;
      try {
        await openHistoryIndex(indexId);
      } finally {
        button.disabled = false;
      }
    });
  }
}

async function openHistoryIndex(indexId) {
  setMessage(hubHistoryMessage, "正在激活所选索引...", "neutral");
  const payload = {};
  const data = await postJson(`/api/indexes/${indexId}/activate`, payload);
  const indexRecord = data.index;
  state.activeIndex = indexRecord;

  const info = normalizeDatasetInfo(indexRecord, indexRecord?.data_path);
  await enterCorePage({
    dataPath: indexRecord?.data_path || "",
    info,
    indexRecord,
  });
  setMessage(hubHistoryMessage, "已进入所选索引页面", "success");
}

async function openNewDatasetFromHub() {
  const path = trimPath(hubDataPath.value);
  if (!path) {
    setMessage(hubNewDatasetMessage, "请输入数据路径", "error");
    return;
  }

  openNewDatasetBtn.disabled = true;
  setMessage(hubNewDatasetMessage, "正在检查数据集并准备进入核心页面...", "neutral");
  try {
    const infoRaw = await postJson("/api/dataset/inspect", { data_path: path });
    const info = normalizeDatasetInfo(infoRaw, path);
    state.activeIndex = null;
    await enterCorePage({
      dataPath: path,
      info,
      indexRecord: null,
    });
    setMessage(hubNewDatasetMessage, "已进入核心页面，可先查看 UMAP 再构建索引", "success");
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
    setBadgeState("is-ready", "索引已就绪", "可直接进行 Top-K 相似检索");
    setMessage(indexStatus, `已加载历史索引：${state.activeIndex.index_name}`, "success");
  } else {
    setBadgeState("is-idle", "未构建索引", "当前仅展示原始数据 UMAP，可按需构建索引");
    setMessage(indexStatus, "当前未加载索引，可先浏览 UMAP 后再构建", "neutral");
  }

  await loadUmapForCurrentDataset();
}

async function loadUmapForCurrentDataset() {
  if (!state.currentDataPath) {
    applyUmapData({ points: [], returned_points: 0, total_points: 0, visualization_source: "none" });
    setMessage(queryStatus, "缺少数据路径，无法加载 UMAP", "error");
    return;
  }

  umapLegend.textContent = "正在加载 UMAP...";
  try {
    const preview = await getJson(
      `/api/dataset/umap-preview?data_path=${encodeURIComponent(state.currentDataPath)}&limit=${UMAP_LIMIT}`
    );
    applyUmapData(preview);
    const mergedInfo = normalizeDatasetInfo(
      { ...state.currentDatasetInfo, ...preview },
      state.currentDataPath
    );
    state.currentDatasetInfo = mergedInfo;
    renderDatasetInfo(mergedInfo);
    return;
  } catch (previewError) {
    if (state.activeIndex?.id) {
      try {
        const indexed = await getJson(
          `/api/visualization/umap?index_id=${encodeURIComponent(state.activeIndex.id)}&limit=${UMAP_LIMIT}`
        );
        applyUmapData(indexed);
        setMessage(
          queryStatus,
          `原始数据预览失败，已回退到索引坐标可视化：${previewError.message}`,
          "neutral"
        );
        return;
      } catch (indexError) {
        applyUmapData({ points: [], returned_points: 0, total_points: 0, visualization_source: "none" });
        setMessage(queryStatus, `UMAP 加载失败：${indexError.message}`, "error");
        return;
      }
    }
    applyUmapData({ points: [], returned_points: 0, total_points: 0, visualization_source: "none" });
    setMessage(queryStatus, `UMAP 加载失败：${previewError.message}`, "error");
  }
}

async function inspectDatasetFromMain() {
  const path = trimPath(dataPathInput.value);
  if (!path) {
    setMessage(indexStatus, "请输入数据路径", "error");
    return;
  }

  inspectDataBtn.disabled = true;
  setMessage(indexStatus, "正在检查数据集...", "neutral");
  try {
    const raw = await postJson("/api/dataset/inspect", { data_path: path });
    const info = normalizeDatasetInfo(raw, path);
    const pathChanged = trimPath(state.activeIndex?.data_path) !== path;
    if (pathChanged) {
      state.activeIndex = null;
      setBadgeState("is-idle", "未构建索引", "数据集已切换，可先查看 UMAP 再构建索引");
    }
    setCurrentDataset(path);
    state.currentDatasetInfo = info;
    renderDatasetInfo(info);
    await loadUmapForCurrentDataset();
    setMessage(indexStatus, "数据检查完成，已刷新 UMAP", "success");
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
    // ignored
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
      setBadgeState("is-loading", "索引构建中", "正在写入向量并构建 HNSW 图");
      setMessage(indexStatus, job.message || "构建进行中...", "neutral");
    }
    return;
  }

  if (job.status === "failed") {
    clearBuildPolling();
    if (applyToCurrentView) {
      setBadgeState("is-error", "构建失败", "请检查数据格式或参数设置");
      setMessage(indexStatus, job.error || job.message || "索引构建失败", "error");
    }
    return;
  }

  if (job.status === "completed") {
    const builtIndexId = job?.result?.index_id;
    clearBuildPolling();
    const result = job.result || {};
    if (applyToCurrentView) {
      state.activeIndex = await fetchActiveIndexRecord(builtIndexId);
      const mergedInfo = normalizeDatasetInfo(
        { ...state.currentDatasetInfo, ...result },
        state.currentDataPath
      );
      state.currentDatasetInfo = mergedInfo;
      renderDatasetInfo(mergedInfo);
      setBadgeState("is-ready", "索引已就绪", "可直接进行 Top-K 相似检索");
      setMessage(
        indexStatus,
        `索引构建完成：${formatNumber(result.cell_count)} 个细胞，耗时 ${formatTime(result.build_time_ms)}`,
        "success"
      );
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
      setBadgeState("is-error", "进度查询失败", "无法获取索引构建状态");
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
  const path = trimPath(dataPathInput.value);
  if (!path) {
    setMessage(indexStatus, "请输入数据路径", "error");
    return;
  }

  buildIndexBtn.disabled = true;
  setCurrentDataset(path);
  state.activeIndex = null;
  state.buildJobContextPath = path;
  setBadgeState("is-loading", "索引构建中", "正在提交异步构建任务");
  setMessage(indexStatus, "已提交构建任务，正在启动...", "neutral");
  setIndexProgressVisible(true);
  updateIndexProgress({
    progress_pct: 0,
    stage: "queued",
    processed_cells: 0,
    total_cells: null,
    eta_seconds: null,
  });

  try {
    const response = await postJson("/api/index/build", {
      data_path: path,
      async: true,
      activate: true,
    });
    if (!response.job_id) {
      throw new Error("未返回任务 ID，无法跟踪构建进度");
    }
    await pollBuildJob(response.job_id);
  } catch (error) {
    clearBuildPolling();
    setBadgeState("is-error", "构建提交失败", "请稍后重试");
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

  const cellId = trimPath(cellIdInput.value);
  if (!cellId) {
    setMessage(queryStatus, "请输入细胞 ID", "error");
    await showTableState("查询失败：缺少细胞 ID", "error");
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
  setMessage(queryStatus, "正在按细胞 ID 查询...", "neutral");
  setQueryMetrics({ mode: "按 ID 查询", resultCount: 0, queryTime: null, highlightCount: 0 });

  try {
    const payload = {
      cell_id: cellId,
      top_k: topK,
      filters: activeFilters(),
      index_id: state.activeIndex.id,
    };
    const data = await postJson("/api/search/by-id", payload);
    await renderResults(data.results);
    const highlightCount = applyUmapHighlights(data.results, "按 ID 查询");
    setQueryMetrics({
      mode: "按 ID 查询",
      resultCount: Array.isArray(data.results) ? data.results.length : 0,
      queryTime: data.query_time_ms,
      highlightCount,
    });
    setMessage(
      queryStatus,
      `查询完成，返回 ${Array.isArray(data.results) ? data.results.length : 0} 条结果，耗时 ${formatTime(data.query_time_ms)}`,
      "success"
    );
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    clearUmapHighlights();
    setQueryMetrics({ mode: "按 ID 查询", resultCount: 0, queryTime: null, highlightCount: 0 });
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
  setMessage(queryStatus, "正在按向量查询...", "neutral");
  setQueryMetrics({ mode: "按向量查询", resultCount: 0, queryTime: null, highlightCount: 0 });

  try {
    const payload = {
      vector,
      top_k: topK,
      filters: activeFilters(),
      index_id: state.activeIndex.id,
    };
    const data = await postJson("/api/search/by-vector", payload);
    await renderResults(data.results);
    const highlightCount = applyUmapHighlights(data.results, "按向量查询");
    setQueryMetrics({
      mode: "按向量查询",
      resultCount: Array.isArray(data.results) ? data.results.length : 0,
      queryTime: data.query_time_ms,
      highlightCount,
    });
    setMessage(
      queryStatus,
      `查询完成，返回 ${Array.isArray(data.results) ? data.results.length : 0} 条结果，耗时 ${formatTime(data.query_time_ms)}`,
      "success"
    );
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    clearUmapHighlights();
    setQueryMetrics({ mode: "按向量查询", resultCount: 0, queryTime: null, highlightCount: 0 });
  } finally {
    searchByVectorBtn.disabled = false;
  }
}

function resetUmapView() {
  clearUmapHighlights();
  setMessage(queryStatus, "已恢复 UMAP 默认绘制状态", "neutral");
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
  setMessage(authMessage, "正在登录...", "neutral", "mb-3");
  authMessage.classList.remove("d-none");
  try {
    const payload = {
      username: trimPath(document.querySelector("#authUsername").value),
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
  setMessage(authMessage, "正在注册...", "neutral", "mb-3");
  authMessage.classList.remove("d-none");
  try {
    const payload = {
      username: trimPath(document.querySelector("#authUsername").value),
      password: document.querySelector("#authPassword").value,
      role: document.querySelector("input[name='authRole']:checked").value,
    };
    const data = await postJson("/api/auth/register", payload);
    setMessage(authMessage, `注册成功：${data.user.username}，请点击登录`, "success", "mb-3");
  } catch (error) {
    setMessage(authMessage, error.message, "error", "mb-3");
  } finally {
    registerBtn.disabled = false;
  }
});

logoutBtn.addEventListener("click", () => {
  clearSession();
});

hubLogoutBtn.addEventListener("click", () => {
  clearSession();
});

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

resetUmapBtn.addEventListener("click", () => {
  resetUmapView();
});

setQueryMetrics();
showTableState("暂无查询结果，请先构建索引并执行查询").catch(() => undefined);
checkAuthAndInit();
