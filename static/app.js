const authView = document.querySelector("#authView");
const mainView = document.querySelector("#mainView");
const authMessage = document.querySelector("#authMessage");
const currentUserLabel = document.querySelector("#currentUserLabel");
const loginBtn = document.querySelector("#loginBtn");
const registerBtn = document.querySelector("#registerBtn");
const logoutBtn = document.querySelector("#logoutBtn");

const inspectDataBtn = document.querySelector("#inspectDataBtn");
const buildIndexBtn = document.querySelector("#buildIndexBtn");
const searchByIdBtn = document.querySelector("#searchByIdBtn");
const searchByVectorBtn = document.querySelector("#searchByVectorBtn");
const indexStatus = document.querySelector("#indexStatus");
const healthBadge = document.querySelector("#healthBadge");
const healthText = document.querySelector("#healthText");
const resultsBody = document.querySelector("#resultsBody");
const datasetInfo = document.querySelector("#datasetInfo");
const queryStatus = document.querySelector("#queryStatus");
const queryModeMetric = document.querySelector("#queryModeMetric");
const resultCountMetric = document.querySelector("#resultCountMetric");
const queryTimeMetric = document.querySelector("#queryTimeMetric");
const highlightMetric = document.querySelector("#highlightMetric");
const umapLegend = document.querySelector("#umapLegend");
const umapChartElement = document.querySelector("#umapChart");

const MOCK_UMAP_SIZE = 10000;
const HIGHLIGHT_LIMIT = 50;

let authToken = localStorage.getItem("authToken") || "";
let currentUser = JSON.parse(localStorage.getItem("currentUser") || "null");
let umapChart = null;
let baseUmapData = [];

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
  return numericValue % 1 === 0 ? numericValue.toString() : numericValue.toFixed(3);
}

function formatTime(value) {
  if (value === null || value === undefined || value === "") return "--";
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? `${numericValue.toFixed(2)} ms` : String(value);
}

function hashString(input) {
  let hash = 0;
  const text = String(input || "");
  for (let index = 0; index < text.length; index += 1) {
    hash = (hash << 5) - hash + text.charCodeAt(index);
    hash |= 0;
  }
  return Math.abs(hash);
}

function getFileFormat(path) {
  if (!path || !path.includes(".")) return "-";
  return path.split(".").pop();
}

function setBadgeState(mode, text, note) {
  healthBadge.textContent = text;
  healthBadge.className = `status-badge ${mode}`;
  healthText.textContent = note;
}

function setMessage(element, message, tone = "neutral") {
  const className =
    tone === "success"
      ? "status-message success-message"
      : tone === "error"
        ? "status-message error-message"
        : "status-message neutral-message";
  element.className = className;
  element.textContent = message;
}

function setQueryMetrics({ mode = "未查询", resultCount = 0, queryTime = null, highlightCount = 0 } = {}) {
  queryModeMetric.textContent = mode;
  resultCountMetric.textContent = formatNumber(resultCount);
  queryTimeMetric.textContent = formatTime(queryTime);
  highlightMetric.textContent = formatNumber(highlightCount);
}

function dataPath() {
  return document.querySelector("#dataPath").value.trim();
}

async function requestJson(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  const response = await fetch(url, { ...options, headers });
  const rawText = await response.text();
  let data = {};

  if (rawText) {
    try {
      data = JSON.parse(rawText);
    } catch (error) {
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
    body: JSON.stringify(payload),
  });
}

function showAuthView() {
  authView.classList.remove("d-none");
  mainView.classList.add("d-none");
}

function initUmapChartIfNeeded() {
  if (umapChart || !window.echarts || !umapChartElement) return;

  baseUmapData = generateMockUmapData(MOCK_UMAP_SIZE);
  umapChart = window.echarts.init(umapChartElement, null, { renderer: "canvas" });
  umapChart.setOption(buildUmapOption(baseUmapData, []));
  window.addEventListener("resize", () => {
    if (umapChart) {
      umapChart.resize();
    }
  });
}

function showMainView() {
  authView.classList.add("d-none");
  mainView.classList.remove("d-none");
  currentUserLabel.textContent = currentUser
    ? `${currentUser.username} (${currentUser.role === "admin" ? "管理员" : "普通用户"})`
    : "--";
  window.requestAnimationFrame(() => {
    initUmapChartIfNeeded();
    if (umapChart) {
      umapChart.resize();
    }
  });
  refreshHealth();
}

function saveSession(token, user) {
  authToken = token;
  currentUser = user;
  localStorage.setItem("authToken", token);
  localStorage.setItem("currentUser", JSON.stringify(user));
  showMainView();
}

function clearSession() {
  authToken = "";
  currentUser = null;
  localStorage.removeItem("authToken");
  localStorage.removeItem("currentUser");
  showAuthView();
}

function renderDatasetInfo(info = {}) {
  const fields = [
    ["文件", info.source_path || "-"],
    ["格式", info.format || "-"],
    ["细胞数", formatNumber(info.cell_count)],
    ["基因数", formatNumber(info.gene_count)],
    ["向量维度", formatNumber(info.vector_dim)],
    ["向量来源", info.embedding_key || "-"],
  ];

  datasetInfo.innerHTML = fields
    .map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`)
    .join("");
}

function normalizeDatasetInfo(info = {}, pathOverride) {
  return {
    source_path: info.source_path || pathOverride || "-",
    format: info.format || getFileFormat(pathOverride) || "-",
    cell_count: info.cell_count,
    gene_count: info.gene_count,
    vector_dim: info.vector_dim,
    embedding_key: info.embedding_key || "-",
  };
}

function positiveTopK(selector) {
  const value = Number(document.querySelector(selector).value);
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error("Top-K 必须是大于 0 的整数");
  }
  return value;
}

function parseVectorInput() {
  const rawValue = document.querySelector("#queryVector").value.trim();
  if (!rawValue) {
    throw new Error("请输入查询向量");
  }

  const vector = rawValue
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean)
    .map((value) => Number(value));

  if (!vector.length || vector.some((value) => !Number.isFinite(value))) {
    throw new Error("向量格式错误，请输入逗号分隔的数字");
  }

  return vector;
}

function activeFilters() {
  const filters = {};
  const cellType = document.querySelector("#filterCellType").value.trim();
  const disease = document.querySelector("#filterDisease").value.trim();
  const ageGroup = document.querySelector("#filterAgeGroup").value.trim();

  if (cellType) filters.cell_type = cellType;
  if (disease) filters.disease = disease;
  if (ageGroup) filters.AgeGroup = ageGroup;
  return filters;
}

function generateMockUmapData(size) {
  const clusters = [
    { x: -14, y: 8, spread: 2.4, label: 0 },
    { x: -6, y: -10, spread: 2.8, label: 1 },
    { x: 4, y: -3, spread: 2.2, label: 2 },
    { x: 13, y: 10, spread: 2.6, label: 3 },
    { x: 10, y: -11, spread: 2.1, label: 4 },
    { x: -12, y: -2, spread: 1.8, label: 5 },
  ];

  const points = [];
  for (let index = 0; index < size; index += 1) {
    const cluster = clusters[index % clusters.length];
    const angle = Math.random() * Math.PI * 2;
    const radius = Math.sqrt(Math.random()) * cluster.spread * (0.55 + Math.random());
    const x = cluster.x + Math.cos(angle) * radius;
    const y = cluster.y + Math.sin(angle) * radius;
    points.push([x, y, cluster.label, 1.8 + Math.random() * 1.8]);
  }
  return points;
}

function createHighlightPoint(cellId, rank) {
  const hash = hashString(cellId);
  const angle = (hash % 360) * (Math.PI / 180);
  const radius = 4 + (hash % 90) / 18;
  const ring = rank % 5;
  const x = Math.cos(angle) * radius + ring * 1.1 - 2.2;
  const y = Math.sin(angle) * radius + ((hash >> 3) % 7) * 0.55 - 1.8;
  return {
    value: [x, y, rank + 1],
    cellId,
  };
}

function buildUmapOption(baseData, highlightData) {
  return {
    animation: false,
    grid: { left: 10, right: 10, top: 10, bottom: 10, containLabel: false },
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(15,23,42,0.92)",
      borderColor: "rgba(6,182,212,0.28)",
      textStyle: { color: "#e2e8f0" },
      formatter(params) {
        if (params.seriesName === "检索命中") {
          return `命中细胞: ${escapeHtml(params.data.cellId)}<br>排名: #${params.data.value[2]}`;
        }
        return `Mock Cell<br>x=${params.value[0].toFixed(2)}<br>y=${params.value[1].toFixed(2)}`;
      },
    },
    xAxis: {
      type: "value",
      min: -22,
      max: 22,
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
      min: -18,
      max: 18,
      axisLine: { lineStyle: { color: "rgba(148,163,184,0.28)" } },
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
      name: "UMAP-2",
      nameLocation: "middle",
      nameGap: 30,
      nameRotate: 90,
      nameTextStyle: { color: "#94a3b8" },
    },
    visualMap: {
      show: false,
      min: 0,
      max: 5,
      dimension: 2,
      inRange: {
        color: ["#1d4ed8", "#06b6d4", "#8b5cf6", "#f59e0b", "#10b981", "#ef4444"],
      },
    },
    series: [
      {
        name: "全部细胞",
        type: "scatterGL",
        data: baseData,
        progressive: 5000,
        progressiveThreshold: 10000,
        symbolSize(value) {
          return value[3];
        },
        itemStyle: {
          opacity: 0.78,
        },
        emphasis: {
          itemStyle: {
            borderColor: "#fff",
            borderWidth: 0.5,
          },
        },
      },
      {
        name: "检索命中",
        type: "scatter",
        data: highlightData,
        symbolSize(value) {
          return 12 - Math.min(value[2] - 1, 7) * 0.7;
        },
        itemStyle: {
          color: "#f8fafc",
          borderColor: "#ef4444",
          borderWidth: 2,
          shadowBlur: 12,
          shadowColor: "rgba(239,68,68,0.45)",
        },
        z: 10,
      },
    ],
  };
}

function updateUmapHighlights(results = [], mode = "未查询") {
  initUmapChartIfNeeded();
  if (!umapChart) return;

  const highlightData = results
    .slice(0, HIGHLIGHT_LIMIT)
    .map((item, index) => createHighlightPoint(item.cell_id || `result_${index + 1}`, index));

  umapChart.setOption({
    series: [
      { data: baseUmapData },
      { data: highlightData },
    ],
  });

  umapLegend.textContent = highlightData.length
    ? `${mode} · 高亮 ${highlightData.length} 个命中点`
    : "Mock 10,000 点";
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

async function refreshHealth() {
  try {
    const data = await getJson("/api/health");
    const ready = Boolean(data.indexed);
    setBadgeState(
      ready ? "is-ready" : "is-idle",
      ready ? "索引已就绪" : "未构建索引",
      ready ? "系统可直接执行相似检索" : "请先检查数据并构建索引"
    );

    if (data.dataset) {
      renderDatasetInfo(normalizeDatasetInfo(data.dataset));
    }
  } catch (error) {
    setBadgeState("is-error", "状态检查失败", error.message);
  }
}

async function checkAuthAndInit() {
  if (!authToken) {
    showAuthView();
    return;
  }

  try {
    const data = await getJson("/api/auth/me");
    currentUser = data.user;
    localStorage.setItem("currentUser", JSON.stringify(currentUser));
    showMainView();
  } catch (error) {
    clearSession();
  }
}

loginBtn.addEventListener("click", async () => {
  loginBtn.disabled = true;
  authMessage.className = "status-message neutral-message mb-3";
  authMessage.textContent = "正在登录...";
  authMessage.classList.remove("d-none");

  try {
    const payload = {
      username: document.querySelector("#authUsername").value.trim(),
      password: document.querySelector("#authPassword").value,
    };
    const data = await postJson("/api/auth/login", payload);
    saveSession(data.token, data.user);
  } catch (error) {
    authMessage.className = "status-message error-message mb-3";
    authMessage.textContent = error.message;
  } finally {
    loginBtn.disabled = false;
  }
});

registerBtn.addEventListener("click", async () => {
  registerBtn.disabled = true;
  authMessage.className = "status-message neutral-message mb-3";
  authMessage.textContent = "正在注册...";
  authMessage.classList.remove("d-none");

  try {
    const payload = {
      username: document.querySelector("#authUsername").value.trim(),
      password: document.querySelector("#authPassword").value,
      role: document.querySelector("input[name='authRole']:checked").value,
    };
    const data = await postJson("/api/auth/register", payload);
    authMessage.className = "status-message success-message mb-3";
    authMessage.textContent = `注册成功：${data.user.username}，请点击登录`;
  } catch (error) {
    authMessage.className = "status-message error-message mb-3";
    authMessage.textContent = error.message;
  } finally {
    registerBtn.disabled = false;
  }
});

logoutBtn.addEventListener("click", () => {
  clearSession();
});

inspectDataBtn.addEventListener("click", async () => {
  const path = dataPath();
  if (!path) {
    setMessage(indexStatus, "请先输入数据路径", "error");
    return;
  }

  inspectDataBtn.disabled = true;
  setMessage(indexStatus, "正在检查数据集，请稍候...", "neutral");
  setBadgeState("is-loading", "检查数据中", "正在验证数据集路径和向量信息");

  try {
    const info = await postJson("/api/dataset/inspect", { data_path: path });
    const normalizedInfo = normalizeDatasetInfo(info, path);
    renderDatasetInfo(normalizedInfo);
    setMessage(indexStatus, "数据检查完成，可以继续构建索引", "success");
    setBadgeState("is-idle", "数据已检查", "数据集读取成功，等待构建索引");
  } catch (error) {
    setMessage(indexStatus, error.message, "error");
    setBadgeState("is-error", "检查失败", error.message);
  } finally {
    inspectDataBtn.disabled = false;
  }
});

buildIndexBtn.addEventListener("click", async () => {
  const path = dataPath();
  if (!path) {
    setMessage(indexStatus, "请先输入数据路径", "error");
    return;
  }

  buildIndexBtn.disabled = true;
  setMessage(indexStatus, "正在构建索引，首次加载真实数据可能需要较长时间...", "neutral");
  setBadgeState("is-loading", "索引构建中", "正在加载向量并初始化 HNSW 索引");

  try {
    const data = await postJson("/api/index/build", { data_path: path });
    const normalizedInfo = normalizeDatasetInfo(data, path);
    renderDatasetInfo(normalizedInfo);
    setMessage(
      indexStatus,
      `索引构建成功：${formatNumber(data.cell_count)} 个细胞，${formatNumber(data.vector_dim)} 维，耗时 ${formatTime(data.build_time_ms)}`,
      "success"
    );
    setBadgeState("is-ready", "索引已就绪", "已完成构建，可执行 Top-K 相似检索");
  } catch (error) {
    setMessage(indexStatus, error.message, "error");
    setBadgeState("is-error", "构建失败", error.message);
  } finally {
    buildIndexBtn.disabled = false;
  }
});

searchByIdBtn.addEventListener("click", async () => {
  const cellId = document.querySelector("#cellId").value.trim();
  if (!cellId) {
    setMessage(queryStatus, "请输入细胞 ID", "error");
    await showTableState("查询失败：缺少细胞 ID", "error");
    return;
  }

  let topK;
  try {
    topK = positiveTopK("#topKId");
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    return;
  }

  searchByIdBtn.disabled = true;
  setMessage(queryStatus, "正在按细胞 ID 查询相似细胞...", "neutral");
  setQueryMetrics({ mode: "按 ID 查询", resultCount: 0, queryTime: null, highlightCount: 0 });

  try {
    const data = await postJson("/api/search/by-id", {
      cell_id: cellId,
      top_k: topK,
      filters: activeFilters(),
    });
    await renderResults(data.results);
    updateUmapHighlights(data.results, "按 ID 查询");
    setQueryMetrics({
      mode: "按 ID 查询",
      resultCount: data.results.length,
      queryTime: data.query_time_ms,
      highlightCount: Math.min(data.results.length, HIGHLIGHT_LIMIT),
    });
    setMessage(
      queryStatus,
      `查询完成，返回 ${data.results.length} 条结果，耗时 ${formatTime(data.query_time_ms)}`,
      "success"
    );
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    updateUmapHighlights([], "按 ID 查询");
    setQueryMetrics({ mode: "按 ID 查询", resultCount: 0, queryTime: null, highlightCount: 0 });
  } finally {
    searchByIdBtn.disabled = false;
  }
});

searchByVectorBtn.addEventListener("click", async () => {
  let vector;
  let topK;

  try {
    vector = parseVectorInput();
    topK = positiveTopK("#topKVector");
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    return;
  }

  searchByVectorBtn.disabled = true;
  setMessage(queryStatus, "正在按向量执行相似检索...", "neutral");
  setQueryMetrics({ mode: "按向量查询", resultCount: 0, queryTime: null, highlightCount: 0 });

  try {
    const data = await postJson("/api/search/by-vector", {
      vector,
      top_k: topK,
      filters: activeFilters(),
    });
    await renderResults(data.results);
    updateUmapHighlights(data.results, "按向量查询");
    setQueryMetrics({
      mode: "按向量查询",
      resultCount: data.results.length,
      queryTime: data.query_time_ms,
      highlightCount: Math.min(data.results.length, HIGHLIGHT_LIMIT),
    });
    setMessage(
      queryStatus,
      `查询完成，返回 ${data.results.length} 条结果，耗时 ${formatTime(data.query_time_ms)}`,
      "success"
    );
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    updateUmapHighlights([], "按向量查询");
    setQueryMetrics({ mode: "按向量查询", resultCount: 0, queryTime: null, highlightCount: 0 });
  } finally {
    searchByVectorBtn.disabled = false;
  }
});

setQueryMetrics();
checkAuthAndInit();
