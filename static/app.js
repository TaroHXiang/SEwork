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
const hubAdminBadge = document.querySelector("#hubAdminBadge");
const mainAdminBadge = document.querySelector("#mainAdminBadge");

const historyCards = document.querySelector("#historyCards");
const hubHistoryMessage = document.querySelector("#hubHistoryMessage");
const hubDataPath = document.querySelector("#hubDataPath");
const openNewDatasetBtn = document.querySelector("#openNewDatasetBtn");
const hubNewDatasetMessage = document.querySelector("#hubNewDatasetMessage");
const adminPanelSection = document.querySelector("#adminPanelSection");
const adminUserCount = document.querySelector("#adminUserCount");
const adminActiveUserCount = document.querySelector("#adminActiveUserCount");
const adminDisabledUserCount = document.querySelector("#adminDisabledUserCount");
const adminDatasetCount = document.querySelector("#adminDatasetCount");
const adminIndexCount = document.querySelector("#adminIndexCount");
const adminFailedJobCount = document.querySelector("#adminFailedJobCount");
const adminAdminCount = document.querySelector("#adminAdminCount");
const adminInProgressJobCount = document.querySelector("#adminInProgressJobCount");
const adminTabs = document.querySelector("#adminTabs");
const adminRefreshDashboardBtn = document.querySelector("#adminRefreshDashboardBtn");
const adminCreateUsername = document.querySelector("#adminCreateUsername");
const adminCreateDisplayName = document.querySelector("#adminCreateDisplayName");
const adminCreateEmail = document.querySelector("#adminCreateEmail");
const adminCreatePassword = document.querySelector("#adminCreatePassword");
const adminCreateRole = document.querySelector("#adminCreateRole");
const adminCreateUserBtn = document.querySelector("#adminCreateUserBtn");
const adminMessage = document.querySelector("#adminMessage");
const adminUsersHint = document.querySelector("#adminUsersHint");
const adminUsersBody = document.querySelector("#adminUsersBody");
const adminOverviewTab = document.querySelector("#adminOverviewTab");
const adminUsersTab = document.querySelector("#adminUsersTab");
const adminDatasetsTab = document.querySelector("#adminDatasetsTab");
const adminIndexesTab = document.querySelector("#adminIndexesTab");
const adminJobsTab = document.querySelector("#adminJobsTab");
const adminAuditTab = document.querySelector("#adminAuditTab");
const adminUserDetailHint = document.querySelector("#adminUserDetailHint");
const adminUserDetailMeta = document.querySelector("#adminUserDetailMeta");
const adminUserDatasetsList = document.querySelector("#adminUserDatasetsList");
const adminUserIndexesList = document.querySelector("#adminUserIndexesList");
const adminUserJobsList = document.querySelector("#adminUserJobsList");
const adminDatasetsBody = document.querySelector("#adminDatasetsBody");
const adminIndexesBody = document.querySelector("#adminIndexesBody");
const adminBuildJobsBody = document.querySelector("#adminBuildJobsBody");
const adminAuditLogsBody = document.querySelector("#adminAuditLogsBody");
const adminIndexTypeChartElement = document.querySelector("#adminIndexTypeChart");
const adminMetricChartElement = document.querySelector("#adminMetricChart");
const adminBuildTrendChartElement = document.querySelector("#adminBuildTrendChart");
const adminTopUsersChartElement = document.querySelector("#adminTopUsersChart");
const adminUserDetailChartElement = document.querySelector("#adminUserDetailChart");

const backToHubBtn = document.querySelector("#backToHubBtn");
const currentDatasetLabel = document.querySelector("#currentDatasetLabel");
const dataPathInput = document.querySelector("#dataPath");
const indexTypeInput = document.querySelector("#indexType");
const distanceMetricInput = document.querySelector("#distanceMetric");
const hnswMField = document.querySelector("#hnswMField");
const hnswMInput = document.querySelector("#hnswM");
const hnswEfConstructField = document.querySelector("#hnswEfConstructField");
const hnswEfConstructInput = document.querySelector("#hnswEfConstruct");
const hnswEfSearchField = document.querySelector("#hnswEfSearchField");
const hnswEfSearchInput = document.querySelector("#hnswEfSearch");
const ivfNlistField = document.querySelector("#ivfNlistField");
const ivfNlistInput = document.querySelector("#ivfNlist");
const ivfNprobeField = document.querySelector("#ivfNprobeField");
const ivfNprobeInput = document.querySelector("#ivfNprobe");
const pqCompressionField = document.querySelector("#pqCompressionField");
const pqCompressionInput = document.querySelector("#pqCompression");
const inspectDataBtn = document.querySelector("#inspectDataBtn");
const buildIndexBtn = document.querySelector("#buildIndexBtn");
const indexStatus = document.querySelector("#indexStatus");
const healthBadge = document.querySelector("#healthBadge");
const healthText = document.querySelector("#healthText");
const datasetInfo = document.querySelector("#datasetInfo");
const indexBuildProgress = document.querySelector("#indexBuildProgress");
const indexBuildProgressBar = document.querySelector("#indexBuildProgressBar");
const indexBuildProgressMeta = document.querySelector("#indexBuildProgressMeta");
const indexBuildStageLabel = document.querySelector("#indexBuildStageLabel");
const indexBuildElapsed = document.querySelector("#indexBuildElapsed");
const indexBuildProcessed = document.querySelector("#indexBuildProcessed");
const indexBuildRate = document.querySelector("#indexBuildRate");
const indexBuildEta = document.querySelector("#indexBuildEta");
const indexBuildTimeline = document.querySelector("#indexBuildTimeline");
const contextHelpTrigger = document.querySelector("#contextHelpTrigger");
const contextHelpTemplate = document.querySelector("#contextHelpTemplate");
const contextHelpOverlay = document.querySelector("#contextHelpOverlay");
const contextHelpOverlayCard = document.querySelector("#contextHelpOverlayCard");
const contextHelpOverlayBody = document.querySelector("#contextHelpOverlayBody");
const contextHelpOverlayClose = document.querySelector("#contextHelpOverlayClose");
const aiAssistantDock = document.querySelector("#aiAssistantDock");
const aiAssistantLauncher = document.querySelector("#aiAssistantLauncher");
const aiAssistantPanel = document.querySelector("#aiAssistantPanel");
const aiAssistantClose = document.querySelector("#aiAssistantClose");
const aiAssistantSuggestedQuestionBtn = document.querySelector("#aiAssistantSuggestedQuestionBtn");
const aiAssistantInput = document.querySelector("#aiAssistantInput");
const aiAssistantSendBtn = document.querySelector("#aiAssistantSendBtn");
const aiAssistantStatus = document.querySelector("#aiAssistantStatus");
const aiAssistantMessages = document.querySelector("#aiAssistantMessages");

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

const overviewDatasetName = document.querySelector("#overviewDatasetName");
const overviewTotalCells = document.querySelector("#overviewTotalCells");
const overviewCellTypeCount = document.querySelector("#overviewCellTypeCount");
const overviewSampleCount = document.querySelector("#overviewSampleCount");
const overviewAvgGeneCount = document.querySelector("#overviewAvgGeneCount");
const overviewAvgMitoPct = document.querySelector("#overviewAvgMitoPct");
const cellTypeScopeNote = document.querySelector("#cellTypeScopeNote");
const sampleScopeNote = document.querySelector("#sampleScopeNote");
const qualityScopeNote = document.querySelector("#qualityScopeNote");
const cellTypeDonutChartElement = document.querySelector("#cellTypeDonutChart");
const cellTypeQualityBarChartElement = document.querySelector("#cellTypeQualityBarChart");
const sampleStackChartElement = document.querySelector("#sampleStackChart");
const sampleSimilarityChartElement = document.querySelector("#sampleSimilarityChart");
const qualityHistogramChartElement = document.querySelector("#qualityHistogramChart");
const qualityBoxplotChartElement = document.querySelector("#qualityBoxplotChart");
const qualityMetricButtons = Array.from(document.querySelectorAll(".quality-metric-btn"));

const umapLegend = document.querySelector("#umapLegend");
const resetUmapBtn = document.querySelector("#resetUmapBtn");
const umapPreviewLevel = document.querySelector("#umapPreviewLevel");
const umapColorMode = document.querySelector("#umapColorMode");
const umapInfoTotal = document.querySelector("#umapInfoTotal");
const umapInfoShown = document.querySelector("#umapInfoShown");
const umapInfoFiltered = document.querySelector("#umapInfoFiltered");
const umapInfoSource = document.querySelector("#umapInfoSource");
const umapInfoSampled = document.querySelector("#umapInfoSampled");
const umapLoadingOverlay = document.querySelector("#umapLoadingOverlay");
const umapChartElement = document.querySelector("#umapChart");
const cellDetailPanel = document.querySelector("#cellDetailPanel");

const queryModeMetric = document.querySelector("#queryModeMetric");
const resultCountMetric = document.querySelector("#resultCountMetric");
const queryTimeMetric = document.querySelector("#queryTimeMetric");
const highlightMetric = document.querySelector("#highlightMetric");
const precisionMetric = document.querySelector("#precisionMetric");
const recallMetric = document.querySelector("#recallMetric");
const annTimeMetric = document.querySelector("#annTimeMetric");
const exactTimeMetric = document.querySelector("#exactTimeMetric");
const resultsBody = document.querySelector("#resultsBody");

const HIGHLIGHT_LIMIT = 100;
const BUILD_JOB_POLL_MS = 1200;
const BUILD_JOB_STORAGE_KEY = "sework.activeBuildJob";
const DEFAULT_UMAP_LEVEL = "preview";
const AI_ASSISTANT_SUGGESTED_QUESTION =
  "请结合当前数据集，分别说明 HNSW、IVF、PQ 的优势、劣势、适用场景，并给出各自推荐的参数设置。";

const QUALITY_METRICS = {
  gene: { label: "基因数", histogramKey: "gene_count_histogram", pointField: "gene_count" },
  umi: { label: "UMI", histogramKey: "umi_count_histogram", pointField: "umi_count" },
  mito: { label: "线粒体比例", histogramKey: "mito_pct_histogram", pointField: "mito_pct" },
};

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
  charts: {},
  umapPoints: [],
  umapFilteredPoints: [],
  umapBaseSeries: [],
  umapPointByCellId: new Map(),
  umapFilteredPointByCellId: new Map(),
  umapMeta: null,
  umapHighlights: [],
  umapQueryCenter: null,
  umapFocusedCellId: "",
  umapSelectionCellIds: [],
  umapColorMode: "default",
  umapPreviewLevel: DEFAULT_UMAP_LEVEL,
  chartFocus: { key: "", value: "" },
  analyticsGlobal: null,
  qualityMetric: "gene",
  currentResults: [],
  buildJobId: null,
  buildPollTimer: null,
  buildJobContextPath: "",
  buildPollToken: 0,
  buildPollInFlight: false,
  buildElapsedTimer: null,
  buildElapsedAnchorMs: null,
  buildElapsedStatus: "",
  aiAssistantOpen: false,
  aiAssistantBusy: false,
  aiAssistantMessages: [],
  contextHelpOpen: false,
  adminOverview: null,
  adminUsers: [],
  adminDatasets: [],
  adminIndexes: [],
  adminBuildJobs: [],
  adminAuditLogs: [],
  adminUserDetail: null,
  adminActiveTab: "overview",
};

const BUILD_STAGE_LABELS = {
  queued: "任务执行状态",
  loading_dataset: "加载数据集",
  dataset_loaded: "数据集已就绪",
  building_hnsw: "构建对应索引",
  persisting_index: "保存索引信息",
  completed: "构建完成",
  failed: "构建失败",
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

function isAdmin() {
  return ["admin", "super_admin"].includes(trimText(state.currentUser?.role).toLowerCase());
}

function isSuperAdmin() {
  return trimText(state.currentUser?.role).toLowerCase() === "super_admin";
}

function loadPersistedBuildJob() {
  return parseJson(localStorage.getItem(BUILD_JOB_STORAGE_KEY));
}

function savePersistedBuildJob(payload) {
  if (!payload?.jobId || !payload?.dataPath) return;
  localStorage.setItem(
    BUILD_JOB_STORAGE_KEY,
    JSON.stringify({
      jobId: payload.jobId,
      dataPath: payload.dataPath,
      savedAt: new Date().toISOString(),
    })
  );
}

function clearPersistedBuildJob() {
  localStorage.removeItem(BUILD_JOB_STORAGE_KEY);
}

function formatClockTime(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";
  return date.toLocaleTimeString("zh-CN", { hour12: false });
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

function humanizeIndexType(value) {
  const normalized = trimText(value).toLowerCase();
  if (normalized === "hnsw") return "HNSW";
  if (normalized === "ivf") return "IVF";
  if (normalized === "pq") return "PQ";
  return normalized ? normalized.toUpperCase() : "--";
}

function humanizeDistanceMetric(value, effectiveMetric = "") {
  const normalized = trimText(value).toLowerCase();
  const normalizedEffective = trimText(effectiveMetric).toLowerCase();
  const metricLabels = {
    cosine: "Cosine",
    ip: "Dot (IP)",
    l2: "Euclid (L2)",
    pearson: "Pearson",
  };
  const effectiveLabels = {
    inner_product: "inner product",
    l2: "L2",
  };
  const label = metricLabels[normalized] || (normalized ? normalized.toUpperCase() : "--");
  if (normalized === "pearson" && normalizedEffective && normalizedEffective !== normalized) {
    return `${label} (${effectiveLabels[normalizedEffective] || normalizedEffective})`;
  }
  return label;
}

function historyIndexParamEntries(item = {}) {
  const indexType = trimText(item.index_type).toLowerCase();
  const hnswParams = item.hnsw_params || {};
  const searchParams = item.search_params || {};
  const quantizationConfig = item.quantization_config || {};

  if (indexType === "hnsw") {
    return [
      ["HNSW M", hnswParams.m ?? "--"],
      ["EF Construct", hnswParams.ef_construct ?? "--"],
      ["EF Search", searchParams.hnsw_ef ?? "--"],
    ];
  }

  if (indexType === "ivf") {
    return [
      ["IVF NList", quantizationConfig.nlist ?? "--"],
      ["IVF NProbe", searchParams.nprobe ?? "--"],
    ];
  }

  if (indexType === "pq") {
    return [
      ["PQ Compression", quantizationConfig.compression || "--"],
      ["PQ SubQ", quantizationConfig.subquantizers ?? "--"],
      ["PQ NBits", quantizationConfig.nbits ?? "--"],
    ];
  }

  return [];
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

function parseTimestampMs(value) {
  if (!value) return null;
  const time = new Date(value).getTime();
  return Number.isFinite(time) ? time : null;
}

function resolveBuildElapsedAnchorMs(job = {}) {
  const status = trimText(job.status).toLowerCase();
  const historyStart = Array.isArray(job.history) && job.history.length ? job.history[0]?.time : null;
  const candidates =
    status === "running"
      ? [job.started_at, job.created_at, historyStart, job.updated_at]
      : [job.created_at, historyStart, job.updated_at, job.started_at];

  for (const candidate of candidates) {
    const parsed = parseTimestampMs(candidate);
    if (parsed !== null) return parsed;
  }
  return state.buildElapsedAnchorMs ?? null;
}

function resolveBuildElapsedSeconds(job = {}) {
  const serverElapsed = numberOrNull(job.elapsed_seconds);
  const status = trimText(job.status).toLowerCase();
  if (status !== "queued" && status !== "running") {
    return serverElapsed;
  }

  const anchorMs = resolveBuildElapsedAnchorMs(job);
  if (anchorMs === null) {
    return serverElapsed;
  }

  const clientElapsed = Math.max((Date.now() - anchorMs) / 1000, 0);
  const roundedClientElapsed = Math.round(clientElapsed * 10) / 10;
  if (serverElapsed === null) {
    return roundedClientElapsed;
  }
  return Math.max(serverElapsed, roundedClientElapsed);
}

function stopBuildElapsedTicker() {
  if (state.buildElapsedTimer) {
    window.clearInterval(state.buildElapsedTimer);
    state.buildElapsedTimer = null;
  }
  state.buildElapsedAnchorMs = null;
  state.buildElapsedStatus = "";
}

function syncBuildElapsedTicker(job = {}) {
  if (!indexBuildElapsed) {
    stopBuildElapsedTicker();
    return;
  }
  const status = trimText(job.status).toLowerCase();
  if (status !== "queued" && status !== "running") {
    stopBuildElapsedTicker();
    return;
  }

  const anchorMs = resolveBuildElapsedAnchorMs(job);
  if (anchorMs !== null) {
    state.buildElapsedAnchorMs = anchorMs;
  }
  state.buildElapsedStatus = status;

  if (state.buildElapsedTimer || state.buildElapsedAnchorMs === null) {
    return;
  }

  state.buildElapsedTimer = window.setInterval(() => {
    if (!indexBuildElapsed || state.buildElapsedAnchorMs === null) return;
    const anchorIso = new Date(state.buildElapsedAnchorMs).toISOString();
    const liveElapsedSeconds = resolveBuildElapsedSeconds(
      state.buildElapsedStatus === "running"
        ? { status: "running", started_at: anchorIso }
        : { status: "queued", created_at: anchorIso }
    );
    if (liveElapsedSeconds !== null && liveElapsedSeconds !== undefined) {
      indexBuildElapsed.textContent = `已耗时 ${formatEtaSeconds(liveElapsedSeconds)}`;
    }
  }, 250);
}

const messageAutoHideTimers = new WeakMap();

function formatPercentValue(value) {
  if (value === null || value === undefined || value === "") return "--";
  const num = Number(value);
  return Number.isFinite(num) ? `${num.toFixed(2)}%` : String(value);
}

function numberOrNull(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function trimText(value) {
  return String(value || "").trim();
}

function normalizePathToken(value) {
  return trimText(value).replaceAll("\\", "/").replace(/\/+/g, "/").toLowerCase();
}

function positiveIntegerOrNull(value) {
  const num = Number(value);
  if (!Number.isInteger(num) || num <= 0) return null;
  return num;
}

function updateIndexConfigVisibility() {
  const indexType = trimText(indexTypeInput?.value || "hnsw").toLowerCase();
  if (hnswMField) hnswMField.classList.toggle("d-none", indexType !== "hnsw");
  if (hnswEfConstructField) hnswEfConstructField.classList.toggle("d-none", indexType !== "hnsw");
  if (hnswEfSearchField) hnswEfSearchField.classList.toggle("d-none", indexType !== "hnsw");
  if (ivfNlistField) ivfNlistField.classList.toggle("d-none", indexType !== "ivf");
  if (ivfNprobeField) ivfNprobeField.classList.toggle("d-none", indexType !== "ivf");
  if (pqCompressionField) pqCompressionField.classList.toggle("d-none", indexType !== "pq");
}

function currentIndexBuildOptions() {
  const indexType = trimText(indexTypeInput?.value || "hnsw").toLowerCase() || "hnsw";
  const distanceMetric = trimText(distanceMetricInput?.value || "cosine").toLowerCase() || "cosine";
  const quantizationConfig = {};
  const hnswParams = {};
  const searchParams = {};

  if (indexType === "hnsw") {
    const hnswM = positiveIntegerOrNull(hnswMInput?.value);
    const hnswEfConstruct = positiveIntegerOrNull(hnswEfConstructInput?.value);
    const hnswEfSearch = positiveIntegerOrNull(hnswEfSearchInput?.value);
    if (hnswM) hnswParams.m = hnswM;
    if (hnswEfConstruct) hnswParams.ef_construct = hnswEfConstruct;
    if (hnswEfSearch) searchParams.hnsw_ef = hnswEfSearch;
  }

  if (indexType === "ivf") {
    const nlist = positiveIntegerOrNull(ivfNlistInput?.value);
    const nprobe = positiveIntegerOrNull(ivfNprobeInput?.value);
    if (nlist) quantizationConfig.nlist = nlist;
    if (nprobe) searchParams.nprobe = nprobe;
  }

  if (indexType === "pq" && pqCompressionInput?.value) {
    quantizationConfig.compression = trimText(pqCompressionInput.value).toLowerCase();
  }

  return {
    index_type: indexType,
    distance_metric: distanceMetric,
    quantization_config: quantizationConfig,
    hnsw_params: hnswParams,
    search_params: searchParams,
  };
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

function setUmapLoading(loading, text = "正在更新 UMAP 预览...") {
  if (!umapLoadingOverlay) return;
  umapLoadingOverlay.classList.toggle("d-none", !loading);
  const label = umapLoadingOverlay.querySelector(".umap-loading-text");
  if (label) label.textContent = text;
}

function metadataValue(item, key) {
  const metadata = item?.metadata || {};
  if (key === "sample_id") return trimText(metadata.sample_id || metadata.donor_id);
  if (key === "donor_id") return trimText(metadata.donor_id || metadata.sample_id);
  return trimText(metadata[key]);
}

function pointMatchesFilters(point, filters) {
  return Object.entries(filters || {}).every(([key, value]) => metadataValue(point, key) === trimText(value));
}

function combinedLocalFilters() {
  const filters = activeFilters();
  if (state.chartFocus.key && state.chartFocus.value) {
    filters[state.chartFocus.key] = state.chartFocus.value;
  }
  return filters;
}

function paletteColor(value) {
  const seed = trimText(value);
  if (!seed) return "rgba(125,211,252,0.7)";
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) % 360;
  }
  return `hsla(${hash}, 82%, 66%, 0.82)`;
}

function buildBaseItemStyle(point) {
  const mode = state.umapColorMode || "default";
  if (mode === "cell_type") {
    return { color: paletteColor(metadataValue(point, "cell_type")), opacity: 0.36 };
  }
  if (mode === "disease") {
    return { color: paletteColor(metadataValue(point, "disease")), opacity: 0.42 };
  }
  return { color: "rgba(125,211,252,0.42)", opacity: 0.42 };
}

function clearMessageAutoHide(element) {
  const timer = messageAutoHideTimers.get(element);
  if (timer) {
    window.clearTimeout(timer);
    messageAutoHideTimers.delete(element);
  }
}

function setMessage(element, message, tone = "neutral", classSuffix = "", autoHideMs = 0) {
  if (!element) return;
  clearMessageAutoHide(element);
  const className =
    tone === "success"
      ? "status-message success-message"
      : tone === "error"
        ? "status-message error-message"
        : "status-message neutral-message";
  element.className = `${className}${classSuffix ? ` ${classSuffix}` : ""}`;
  element.textContent = message;
  element.classList.remove("d-none");
  element.hidden = false;
  if (autoHideMs > 0) {
    const timer = window.setTimeout(() => {
      element.textContent = "";
      element.classList.add("d-none");
      element.hidden = true;
      messageAutoHideTimers.delete(element);
    }, autoHideMs);
    messageAutoHideTimers.set(element, timer);
  }
}

function setAiAssistantDockVisible(visible) {
  if (!aiAssistantDock) return;
  aiAssistantDock.classList.toggle("d-none", !visible);
  aiAssistantDock.hidden = !visible;
  if (!visible) {
    state.aiAssistantOpen = false;
    if (aiAssistantPanel) {
      aiAssistantPanel.classList.add("d-none");
      aiAssistantPanel.hidden = true;
    }
  }
}

function setContextHelpOpen(open) {
  if (!contextHelpOverlay || !contextHelpOverlayCard || !contextHelpOverlayBody || !contextHelpTemplate) return;
  state.contextHelpOpen = Boolean(open);
  contextHelpOverlay.classList.toggle("d-none", !state.contextHelpOpen);
  contextHelpOverlay.hidden = !state.contextHelpOpen;
  if (!state.contextHelpOpen) return;

  contextHelpOverlayBody.innerHTML = contextHelpTemplate.innerHTML;
  const triggerRect = contextHelpTrigger?.getBoundingClientRect();
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
  const cardWidth = Math.min(460, Math.max(280, viewportWidth - 24));
  const cardHeight = Math.min(560, Math.max(260, Math.floor(viewportHeight * 0.62)));
  let left = (triggerRect?.right || 24) + 12;
  let top = triggerRect?.top || 24;

  if (left + cardWidth > viewportWidth - 12) {
    left = Math.max(12, (triggerRect?.left || 12) - cardWidth - 12);
  }
  if (left < 12) {
    left = 12;
  }
  if (top + cardHeight > viewportHeight - 12) {
    top = Math.max(12, viewportHeight - cardHeight - 12);
  }
  if (top < 12) {
    top = 12;
  }

  contextHelpOverlayCard.style.left = `${Math.round(left)}px`;
  contextHelpOverlayCard.style.top = `${Math.round(top)}px`;
}

function setAiAssistantPanelOpen(open) {
  if (!aiAssistantPanel) return;
  state.aiAssistantOpen = Boolean(open);
  aiAssistantPanel.classList.toggle("d-none", !state.aiAssistantOpen);
  aiAssistantPanel.hidden = !state.aiAssistantOpen;
}

function aiAssistantDatasetSummaryLine(datasetSummary = null) {
  if (!datasetSummary) return "";
  return [
    datasetSummary.format || "-",
    datasetSummary.cell_count ? `${formatNumber(datasetSummary.cell_count)} cells` : null,
    datasetSummary.vector_dim ? `dim ${formatNumber(datasetSummary.vector_dim)}` : null,
    datasetSummary.embedding_key ? `embedding ${datasetSummary.embedding_key}` : null,
  ]
    .filter(Boolean)
    .join(" · ");
}

function scrollAiAssistantMessagesToBottom() {
  if (!aiAssistantMessages) return;
  aiAssistantMessages.scrollTop = aiAssistantMessages.scrollHeight;
}

function renderAiAssistantInline(text = "") {
  return escapeHtml(String(text || ""))
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function renderAiAssistantMarkdown(text = "") {
  const lines = String(text || "").replace(/\r/g, "").split("\n");
  const html = [];
  let listMode = "";

  const closeList = () => {
    if (listMode) {
      html.push(listMode === "ul" ? "</ul>" : "</ol>");
      listMode = "";
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      continue;
    }

    const bulletMatch = line.match(/^[-*]\s+(.+)$/);
    if (bulletMatch) {
      if (listMode !== "ul") {
        closeList();
        html.push("<ul>");
        listMode = "ul";
      }
      html.push(`<li>${renderAiAssistantInline(bulletMatch[1])}</li>`);
      continue;
    }

    const numberMatch = line.match(/^\d+\.\s+(.+)$/);
    if (numberMatch) {
      if (listMode !== "ol") {
        closeList();
        html.push("<ol>");
        listMode = "ol";
      }
      html.push(`<li>${renderAiAssistantInline(numberMatch[1])}</li>`);
      continue;
    }

    closeList();

    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      const level = Math.min(headingMatch[1].length + 1, 6);
      html.push(`<h${level}>${renderAiAssistantInline(headingMatch[2])}</h${level}>`);
      continue;
    }

    html.push(`<p>${renderAiAssistantInline(line)}</p>`);
  }

  closeList();
  return html.join("");
}

function renderAiAssistantMessages() {
  if (!aiAssistantMessages) return;
  if (!state.aiAssistantMessages.length) {
    aiAssistantMessages.innerHTML = `
      <div class="ai-assistant-placeholder">
        这里会显示你和 AI 的对话内容。默认推荐问题会围绕 HNSW / IVF / PQ 的优劣和参数建议展开。
      </div>
    `;
    return;
  }

  aiAssistantMessages.innerHTML = state.aiAssistantMessages
    .map((message) => {
      const roleClass = message.role === "user" ? "is-user" : "is-assistant";
      const roleLabel = message.role === "user" ? "你" : "AI";
      const meta = trimText(message.meta || "");
      return `
        <article class="ai-assistant-message ${roleClass}">
          <div class="ai-assistant-message-role">${escapeHtml(roleLabel)}</div>
          <div class="ai-assistant-message-bubble">
            ${meta ? `<div class="ai-assistant-message-meta">${escapeHtml(meta)}</div>` : ""}
            <div class="ai-assistant-message-content">${
              message.role === "assistant"
                ? renderAiAssistantMarkdown(message.content || "")
                : escapeHtml(message.content || "").replace(/\n/g, "<br>")
            }</div>
          </div>
        </article>
      `;
    })
    .join("");
  scrollAiAssistantMessagesToBottom();
}

function resetAiAssistantConversation() {
  state.aiAssistantMessages = [
    {
      role: "assistant",
      content:
        "你好，我可以结合当前数据集回答索引类型、距离度量、参数设置和构建策略相关问题。你可以先点上方推荐问题，也可以直接在底部输入任意问题。",
      meta: "",
      skipHistory: true,
    },
  ];
  renderAiAssistantMessages();
}

function appendAiAssistantMessage(role, content, { meta = "", skipHistory = false } = {}) {
  state.aiAssistantMessages.push({
    role,
    content: String(content || ""),
    meta: String(meta || ""),
    skipHistory: Boolean(skipHistory),
  });
  renderAiAssistantMessages();
}

function serializeAiAssistantConversationHistory() {
  return state.aiAssistantMessages
    .filter((item) => !item.skipHistory && ["user", "assistant"].includes(item.role) && trimText(item.content))
    .slice(-8)
    .map((item) => ({
      role: item.role,
      content: item.content,
    }));
}

function compactDatasetInfoForAi() {
  const info = normalizeDatasetInfo(state.currentDatasetInfo || {}, state.currentDataPath || trimText(dataPathInput?.value));
  return {
    source_path: info.source_path,
    format: info.format,
    cell_count: info.cell_count,
    gene_count: info.gene_count,
    vector_dim: info.vector_dim,
    embedding_key: info.embedding_key,
    visualization_source: info.visualization_source,
    metadata_columns: Array.isArray(info.metadata_columns) ? info.metadata_columns : [],
  };
}

async function sendAiAssistantQuestion(questionText = "") {
  const dataPath = trimText(state.currentDataPath || dataPathInput?.value);
  if (!dataPath) {
    throw new Error("请先选择或输入当前数据集路径");
  }
  const question = trimText(questionText);
  if (!question) {
    throw new Error("请输入问题");
  }
  const conversationHistory = serializeAiAssistantConversationHistory();

  setAiAssistantPanelOpen(true);
  appendAiAssistantMessage("user", question);
  state.aiAssistantBusy = true;
  if (aiAssistantSuggestedQuestionBtn) aiAssistantSuggestedQuestionBtn.disabled = true;
  if (aiAssistantSendBtn) aiAssistantSendBtn.disabled = true;
  setMessage(aiAssistantStatus, "AI 正在思考并组织回答...", "neutral");

  try {
    const response = await requestJson("/api/ai/chat", {
      method: "POST",
      body: JSON.stringify({
        data_path: dataPath,
        dataset_info: compactDatasetInfoForAi(),
        current_build_options: currentIndexBuildOptions(),
        user_question: question,
        conversation_history: conversationHistory,
      }),
      timeoutMs: 60000,
    });
    appendAiAssistantMessage("assistant", response.answer || "", {
      meta: aiAssistantDatasetSummaryLine(response.dataset_summary || null),
    });
    setMessage(
      aiAssistantStatus,
      `AI 已回复（${response.model || "LLM"}）`,
      "success"
    );
    if (aiAssistantInput) aiAssistantInput.value = "";
    return response;
  } catch (error) {
    setMessage(aiAssistantStatus, error.message, "error");
    throw error;
  } finally {
    state.aiAssistantBusy = false;
    if (aiAssistantSuggestedQuestionBtn) aiAssistantSuggestedQuestionBtn.disabled = false;
    if (aiAssistantSendBtn) aiAssistantSendBtn.disabled = false;
  }
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
  state.buildPollToken += 1;
  state.buildPollInFlight = false;
  stopBuildElapsedTicker();
  state.buildJobId = null;
  state.buildJobContextPath = "";
}

async function requestJson(url, options = {}) {
  const { timeoutMs = 0, headers: optionHeaders, ...fetchOptions } = options || {};
  const headers = { ...(optionHeaders || {}) };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (state.authToken) {
    headers.Authorization = `Bearer ${state.authToken}`;
  }

  let abortController = null;
  let timeoutId = 0;
  if (timeoutMs > 0 && typeof AbortController !== "undefined") {
    abortController = new AbortController();
    timeoutId = window.setTimeout(() => abortController.abort(), timeoutMs);
  }

  let response;
  try {
    response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: abortController?.signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error(`Request timeout after ${timeoutMs} ms`);
    }
    throw error;
  } finally {
    if (timeoutId) window.clearTimeout(timeoutId);
  }
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
  authView.hidden = false;
  hubView.classList.add("d-none");
  hubView.hidden = true;
  mainView.classList.add("d-none");
  mainView.hidden = true;
  setAiAssistantDockVisible(false);
}

function showHubView() {
  authView.classList.add("d-none");
  authView.hidden = true;
  hubView.classList.remove("d-none");
  hubView.hidden = false;
  mainView.classList.add("d-none");
  mainView.hidden = true;
  const userLabel = state.currentUser
    ? `${state.currentUser.username} (${state.currentUser.role})`
    : "--";
  hubCurrentUserLabel.textContent = userLabel;
  applyRoleUI();
  setAiAssistantDockVisible(false);
}

function resizeAllCharts() {
  if (state.umapChart) state.umapChart.resize();
  Object.values(state.charts).forEach((chart) => chart?.resize?.());
}

function showMainView() {
  authView.classList.add("d-none");
  authView.hidden = true;
  hubView.classList.add("d-none");
  hubView.hidden = true;
  mainView.classList.remove("d-none");
  mainView.hidden = false;
  setAiAssistantDockVisible(true);
  const userLabel = state.currentUser
    ? `${state.currentUser.username} (${state.currentUser.role})`
    : "--";
  currentUserLabel.textContent = userLabel;
  applyRoleUI();
  window.requestAnimationFrame(() => {
    initUmapChartIfNeeded();
    ensureAnalyticsCharts();
    resizeAllCharts();
  });
}

function formatAdminTimestamp(value) {
  const text = trimText(value);
  return text ? text.replace("T", " ").slice(0, 19) : "-";
}

function adminRoleClass(role) {
  const normalized = trimText(role).toLowerCase();
  if (normalized === "super_admin") return "role-super-admin";
  if (normalized === "admin") return "role-admin";
  return "role-user";
}

function adminStatusClass(status) {
  const normalized = trimText(status).toLowerCase();
  if (normalized === "completed" || normalized === "ready" || normalized === "active") return "status-active";
  if (normalized === "failed" || normalized === "disabled" || normalized === "inactive") return "status-disabled";
  return "status-pending";
}

function formatBuildParamsInline(item = {}) {
  const entries = typeof historyIndexParamEntries === "function" ? historyIndexParamEntries(item) : [];
  if (!entries.length) return "-";
  return entries
    .map(([label, value]) => `${label}:${value}`)
    .join(" · ");
}

function getAdminTabPanel(tabName) {
  return {
    overview: adminOverviewTab,
    users: adminUsersTab,
    datasets: adminDatasetsTab,
    indexes: adminIndexesTab,
    jobs: adminJobsTab,
    audit: adminAuditTab,
  }[tabName] || null;
}

function setAdminTab(tabName = "overview") {
  state.adminActiveTab = tabName;
  document.querySelectorAll("[data-admin-tab]").forEach((button) => {
    const active = button.dataset.adminTab === tabName;
    button.classList.toggle("is-active", active);
  });
  [adminOverviewTab, adminUsersTab, adminDatasetsTab, adminIndexesTab, adminJobsTab, adminAuditTab].forEach((panel) => {
    if (!panel) return;
    const active = panel === getAdminTabPanel(tabName);
    panel.classList.toggle("is-active", active);
  });
}

function renderAdminSummary(overview = null) {
  const counts = overview?.counts || {};
  if (adminUserCount) adminUserCount.textContent = formatNumber(counts.users_total || 0);
  if (adminActiveUserCount) adminActiveUserCount.textContent = formatNumber(counts.users_active || 0);
  if (adminDisabledUserCount) adminDisabledUserCount.textContent = formatNumber(counts.users_disabled || 0);
  if (adminDatasetCount) adminDatasetCount.textContent = formatNumber(counts.datasets_total || 0);
  if (adminIndexCount) adminIndexCount.textContent = formatNumber(counts.indexes_total || 0);
  if (adminFailedJobCount) adminFailedJobCount.textContent = formatNumber(counts.jobs_failed || 0);
  if (adminAdminCount) {
    adminAdminCount.textContent = formatNumber((counts.admins_total || 0) + (counts.super_admins_total || 0));
  }
  if (adminInProgressJobCount) adminInProgressJobCount.textContent = formatNumber(counts.jobs_in_progress || 0);
}

function renderAdminOverviewCharts(overview = null) {
  const data = overview || state.adminOverview;
  const indexTypeChart = getOrCreateChart("adminIndexTypeChart", adminIndexTypeChartElement);
  const metricChart = getOrCreateChart("adminMetricChart", adminMetricChartElement);
  const buildTrendChart = getOrCreateChart("adminBuildTrendChart", adminBuildTrendChartElement);
  const topUsersChart = getOrCreateChart("adminTopUsersChart", adminTopUsersChartElement);

  if (indexTypeChart) {
    indexTypeChart.setOption({
      tooltip: { trigger: "item" },
      series: [{ type: "pie", radius: ["42%", "72%"], data: data?.distributions?.index_types || [] }],
    });
  }
  if (metricChart) {
    metricChart.setOption({
      tooltip: { trigger: "item" },
      series: [{ type: "pie", radius: ["42%", "72%"], data: data?.distributions?.metrics || [] }],
    });
  }
  if (buildTrendChart) {
    const trend = Array.isArray(data?.build_job_trend) ? data.build_job_trend : [];
    buildTrendChart.setOption({
      tooltip: { trigger: "axis" },
      legend: { textStyle: { color: "#cbd5e1" } },
      xAxis: { type: "category", data: trend.map((item) => item.day) },
      yAxis: { type: "value" },
      series: [
        { name: "总任务", type: "line", smooth: true, data: trend.map((item) => item.total) },
        { name: "成功", type: "line", smooth: true, data: trend.map((item) => item.completed) },
        { name: "失败", type: "line", smooth: true, data: trend.map((item) => item.failed) },
      ],
    });
  }
  if (topUsersChart) {
    const topUsers = Array.isArray(data?.top_users) ? data.top_users : [];
    topUsersChart.setOption({
      tooltip: { trigger: "axis" },
      xAxis: { type: "value" },
      yAxis: {
        type: "category",
        data: topUsers.map((item) => item.username),
      },
      series: [{ type: "bar", data: topUsers.map((item) => item.index_count) }],
    });
  }
}

function renderAdminUserDetail(detail = null) {
  state.adminUserDetail = detail;
  if (!detail?.user) {
    if (adminUserDetailHint) adminUserDetailHint.textContent = "未选择用户";
    if (adminUserDetailMeta) adminUserDetailMeta.innerHTML = "点击上方“详情”查看该用户的数据集、索引和任务情况。";
    if (adminUserDatasetsList) adminUserDatasetsList.innerHTML = "--";
    if (adminUserIndexesList) adminUserIndexesList.innerHTML = "--";
    if (adminUserJobsList) adminUserJobsList.innerHTML = "--";
    const detailChart = getOrCreateChart("adminUserDetailChart", adminUserDetailChartElement);
    if (detailChart) detailChart.clear();
    return;
  }

  const user = detail.user;
  if (adminUserDetailHint) adminUserDetailHint.textContent = `${user.username} (${user.role})`;
  if (adminUserDetailMeta) {
    adminUserDetailMeta.innerHTML = `
      <div class="admin-detail-pairs">
        <span>账号：${escapeHtml(user.username)}</span>
        <span>角色：${escapeHtml(user.role)}</span>
        <span>状态：${escapeHtml(user.is_active ? "启用" : "停用")}</span>
        <span>最近登录：${escapeHtml(formatAdminTimestamp(user.last_login_at))}</span>
        <span>数据集：${escapeHtml(formatNumber(user.dataset_count || 0))}</span>
        <span>索引：${escapeHtml(formatNumber(user.index_count || 0))}</span>
      </div>
    `;
  }
  if (adminUserDatasetsList) {
    const datasets = Array.isArray(detail.datasets) ? detail.datasets.slice(0, 8) : [];
    adminUserDatasetsList.innerHTML = datasets.length
      ? datasets.map((item) => `<div>${escapeHtml(item.dataset_name || item.data_path || "-")} · ${escapeHtml(item.status || "-")}</div>`).join("")
      : "无数据集";
  }
  if (adminUserIndexesList) {
    const indexes = Array.isArray(detail.indexes) ? detail.indexes.slice(0, 8) : [];
    adminUserIndexesList.innerHTML = indexes.length
      ? indexes.map((item) => `<div>${escapeHtml(item.index_name)} · ${escapeHtml(item.index_type)} · ${escapeHtml(item.distance_metric)}</div>`).join("")
      : "无索引";
  }
  if (adminUserJobsList) {
    const jobs = Array.isArray(detail.jobs) ? detail.jobs.slice(0, 8) : [];
    adminUserJobsList.innerHTML = jobs.length
      ? jobs.map((item) => `<div>${escapeHtml(item.index_name || "-")} · ${escapeHtml(item.status || "-")} · ${escapeHtml(formatAdminTimestamp(item.updated_at))}</div>`).join("")
      : "无任务";
  }
  const detailChart = getOrCreateChart("adminUserDetailChart", adminUserDetailChartElement);
  if (detailChart) {
    detailChart.setOption({
      tooltip: { trigger: "item" },
      series: [{ type: "pie", radius: ["38%", "70%"], data: detail?.charts?.index_types || [] }],
    });
  }
}

function renderAdminUsers(users = []) {
  if (!adminUsersBody) return;
  if (!users.length) {
    adminUsersBody.innerHTML = `
      <tr>
        <td colspan="10" class="table-state">当前没有可显示的用户账号</td>
      </tr>
    `;
    return;
  }

  adminUsersBody.innerHTML = users
    .map((user) => {
      const isCurrent = Number(user.id) === Number(state.currentUser?.id);
      const manageable = !isCurrent && user.role !== "super_admin" && (isSuperAdmin() || user.role === "user");
      const canToggleRole = manageable && isSuperAdmin() && ["user", "admin"].includes(user.role);
      const roleToggleText = user.role === "admin" ? "降为用户" : "设为管理员";
      return `
        <tr data-admin-user-id="${escapeHtml(user.id)}">
          <td>${escapeHtml(user.id)}</td>
          <td>${escapeHtml(user.username)}</td>
          <td>${escapeHtml(user.display_name || "-")}</td>
          <td><span class="table-pill ${adminRoleClass(user.role)}">${escapeHtml(user.role)}</span></td>
          <td><span class="table-pill ${user.is_active ? "status-active" : "status-disabled"}">${escapeHtml(user.is_active ? "启用" : "停用")}</span></td>
          <td>${escapeHtml(formatAdminTimestamp(user.last_login_at))}</td>
          <td>${escapeHtml(formatNumber(user.dataset_count || 0))}</td>
          <td>${escapeHtml(formatNumber(user.index_count || 0))}</td>
          <td>${escapeHtml(user.last_job_status || "-")}</td>
          <td class="admin-actions-cell">
            <button class="btn action-btn secondary-btn btn-sm" data-admin-action="detail-user" data-user-id="${escapeHtml(user.id)}">详情</button>
            <button class="btn action-btn secondary-btn btn-sm" data-admin-action="toggle-status" data-user-id="${escapeHtml(user.id)}" ${manageable ? "" : "disabled"}>${escapeHtml(user.is_active ? "停用" : "启用")}</button>
            <button class="btn action-btn secondary-btn btn-sm" data-admin-action="reset-password" data-user-id="${escapeHtml(user.id)}" ${manageable ? "" : "disabled"}>重置密码</button>
            <button class="btn action-btn secondary-btn btn-sm" data-admin-action="toggle-role" data-user-id="${escapeHtml(user.id)}" ${canToggleRole ? "" : "disabled"}>${escapeHtml(roleToggleText)}</button>
            ${isCurrent ? '<span class="admin-self-hint">当前账号</span>' : `<button class="btn action-btn danger-btn btn-sm" data-admin-action="delete-user" data-user-id="${escapeHtml(user.id)}" ${manageable ? "" : "disabled"}>删除</button>`}
          </td>
        </tr>
      `;
    })
    .join("");
}

function renderAdminDatasets(datasets = []) {
  if (!adminDatasetsBody) return;
  if (!datasets.length) {
    adminDatasetsBody.innerHTML = `<tr><td colspan="10" class="table-state">当前没有可显示的数据集</td></tr>`;
    return;
  }
  adminDatasetsBody.innerHTML = datasets
    .map((item) => `
      <tr>
        <td>${escapeHtml(item.id)}</td>
        <td>${escapeHtml(item.owner_username || "-")}</td>
        <td>${escapeHtml(item.dataset_name || "-")}</td>
        <td>${escapeHtml(item.data_path || "-")}</td>
        <td>${escapeHtml(item.source_format || "-")}</td>
        <td>${escapeHtml(formatNumber(item.cell_count || 0))}</td>
        <td>${escapeHtml(item.vector_dim ?? "-")}</td>
        <td><span class="table-pill ${adminStatusClass(item.status)}">${escapeHtml(item.status || "-")}</span></td>
        <td>${escapeHtml(formatNumber(item.index_count || 0))}</td>
        <td class="admin-actions-cell">
          <button class="btn action-btn danger-btn btn-sm" data-admin-action="delete-dataset" data-dataset-id="${escapeHtml(item.id)}">删除</button>
        </td>
      </tr>
    `)
    .join("");
}

function renderAdminIndexes(indexes = []) {
  if (!adminIndexesBody) return;
  if (!indexes.length) {
    adminIndexesBody.innerHTML = `<tr><td colspan="10" class="table-state">当前没有可显示的索引</td></tr>`;
    return;
  }
  adminIndexesBody.innerHTML = indexes
    .map((item) => `
      <tr>
        <td>${escapeHtml(item.id)}</td>
        <td>${escapeHtml(item.owner_username || "-")}</td>
        <td>${escapeHtml(item.dataset_name || "-")}</td>
        <td>${escapeHtml(item.index_name || "-")}</td>
        <td>${escapeHtml(item.index_type || "-")}</td>
        <td>${escapeHtml(item.distance_metric || "-")}</td>
        <td>${escapeHtml(formatBuildParamsInline(item))}</td>
        <td><span class="table-pill ${item.is_active ? "status-active" : adminStatusClass(item.status)}">${escapeHtml(item.is_active ? "active" : item.status || "-")}</span></td>
        <td>${escapeHtml(formatAdminTimestamp(item.updated_at))}</td>
        <td class="admin-actions-cell">
          <button class="btn action-btn secondary-btn btn-sm" data-admin-action="activate-index" data-index-id="${escapeHtml(item.id)}">激活</button>
          <button class="btn action-btn danger-btn btn-sm" data-admin-action="delete-index" data-index-id="${escapeHtml(item.id)}">删除</button>
        </td>
      </tr>
    `)
    .join("");
}

function renderAdminBuildJobs(jobs = []) {
  if (!adminBuildJobsBody) return;
  if (!jobs.length) {
    adminBuildJobsBody.innerHTML = `<tr><td colspan="7" class="table-state">当前没有可显示的任务</td></tr>`;
    return;
  }
  adminBuildJobsBody.innerHTML = jobs
    .map((job) => `
      <tr>
        <td>${escapeHtml(job.job_id || "-")}</td>
        <td>${escapeHtml(job.owner_username || "-")}</td>
        <td>${escapeHtml(job.dataset_name || "-")}</td>
        <td>${escapeHtml(job.index_name || "-")}</td>
        <td><span class="table-pill ${adminStatusClass(job.status)}">${escapeHtml(job.status || "-")}</span></td>
        <td>${escapeHtml(job.stage || "-")}</td>
        <td>${escapeHtml(formatAdminTimestamp(job.updated_at))}</td>
      </tr>
    `)
    .join("");
}

function renderAdminAuditLogs(logs = []) {
  if (!adminAuditLogsBody) return;
  if (!logs.length) {
    adminAuditLogsBody.innerHTML = `<tr><td colspan="6" class="table-state">当前没有审计日志</td></tr>`;
    return;
  }
  adminAuditLogsBody.innerHTML = logs
    .map((item) => {
      const target = item.target_username || item.target_dataset_id || item.target_index_id || "-";
      const detail = Object.keys(item.detail || {}).length ? JSON.stringify(item.detail) : "-";
      return `
        <tr>
          <td>${escapeHtml(formatAdminTimestamp(item.created_at))}</td>
          <td>${escapeHtml(item.actor_username || `#${item.actor_user_id}`)}</td>
          <td>${escapeHtml(item.actor_role || "-")}</td>
          <td>${escapeHtml(item.action_type || "-")}</td>
          <td>${escapeHtml(String(target))}</td>
          <td>${escapeHtml(detail)}</td>
        </tr>
      `;
    })
    .join("");
}

function renderAdminDashboard() {
  renderAdminSummary(state.adminOverview);
  renderAdminOverviewCharts(state.adminOverview);
  renderAdminUsers(state.adminUsers);
  renderAdminDatasets(state.adminDatasets);
  renderAdminIndexes(state.adminIndexes);
  renderAdminBuildJobs(state.adminBuildJobs);
  renderAdminAuditLogs(state.adminAuditLogs);
  renderAdminUserDetail(state.adminUserDetail);
}

async function loadAdminOverview() {
  const data = await getJson("/api/admin/overview");
  state.adminOverview = data.overview || null;
}

async function loadAdminUsers() {
  const data = await getJson("/api/admin/users");
  state.adminUsers = Array.isArray(data.users) ? data.users : [];
  if (adminUsersHint) adminUsersHint.textContent = `共 ${state.adminUsers.length} 个账号`;
}

async function loadAdminDatasets() {
  const data = await getJson("/api/admin/datasets");
  state.adminDatasets = Array.isArray(data.datasets) ? data.datasets : [];
}

async function loadAdminIndexes() {
  const data = await getJson("/api/admin/indexes");
  state.adminIndexes = Array.isArray(data.indexes) ? data.indexes : [];
}

async function loadAdminBuildJobs() {
  const data = await getJson("/api/admin/build-jobs?limit=120");
  state.adminBuildJobs = Array.isArray(data.jobs) ? data.jobs : [];
}

async function loadAdminAuditLogs() {
  const data = await getJson("/api/admin/audit-logs?limit=120");
  state.adminAuditLogs = Array.isArray(data.logs) ? data.logs : [];
}

async function loadAdminUserDetail(userId) {
  if (!userId) {
    renderAdminUserDetail(null);
    return;
  }
  const detail = await getJson(`/api/admin/users/${encodeURIComponent(userId)}`);
  renderAdminUserDetail(detail);
}

async function loadAdminDashboard() {
  if (!isAdmin()) {
    applyRoleUI();
    return;
  }
  setMessage(adminMessage, "正在同步管理员工作台...", "neutral");
  if (adminUsersHint) adminUsersHint.textContent = "同步中";
  await Promise.all([
    loadAdminOverview(),
    loadAdminUsers(),
    loadAdminDatasets(),
    loadAdminIndexes(),
    loadAdminBuildJobs(),
    loadAdminAuditLogs(),
  ]);
  renderAdminDashboard();
  if (state.adminUserDetail?.user?.id) {
    const exists = state.adminUsers.some((item) => Number(item.id) === Number(state.adminUserDetail.user.id));
    if (exists) {
      await loadAdminUserDetail(state.adminUserDetail.user.id);
    } else {
      renderAdminUserDetail(null);
    }
  }
  setMessage(adminMessage, "管理员工作台已更新。", "success");
}

async function createManagedUser() {
  if (!isAdmin()) {
    throw new Error("当前账号无管理员权限");
  }
  const username = trimText(adminCreateUsername?.value);
  const displayName = trimText(adminCreateDisplayName?.value);
  const email = trimText(adminCreateEmail?.value);
  const password = adminCreatePassword?.value || "";
  const role = trimText(adminCreateRole?.value) || "user";

  if (!username) throw new Error("请输入账号");
  if (password.length < 6) throw new Error("密码至少需要 6 位");

  adminCreateUserBtn.disabled = true;
  setMessage(adminMessage, "正在创建用户...", "neutral");
  try {
    const data = await postJson("/api/admin/users", { username, display_name: displayName, email, password, role });
    if (adminCreateUsername) adminCreateUsername.value = "";
    if (adminCreateDisplayName) adminCreateDisplayName.value = "";
    if (adminCreateEmail) adminCreateEmail.value = "";
    if (adminCreatePassword) adminCreatePassword.value = "";
    if (adminCreateRole) adminCreateRole.value = "user";
    setMessage(adminMessage, `用户已创建：${data.user?.username || username}`, "success");
    await loadAdminDashboard();
  } finally {
    adminCreateUserBtn.disabled = false;
  }
}

async function updateManagedUser(userId, payload, successMessage) {
  if (!isAdmin()) {
    throw new Error("当前账号无管理员权限");
  }
  await requestJson(`/api/admin/users/${encodeURIComponent(userId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  setMessage(adminMessage, successMessage, "success");
  await loadAdminDashboard();
}

async function resetManagedUserPassword(userId, password) {
  await postJson(`/api/admin/users/${encodeURIComponent(userId)}/reset-password`, { password });
  setMessage(adminMessage, "密码已重置", "success");
  await loadAdminDashboard();
}

async function deleteManagedUser(userId) {
  if (!isAdmin()) {
    throw new Error("当前账号无管理员权限");
  }
  await requestJson(`/api/admin/users/${encodeURIComponent(userId)}`, { method: "DELETE" });
  renderAdminUserDetail(null);
  setMessage(adminMessage, "用户已删除", "success");
  await loadAdminDashboard();
}

async function deleteManagedDataset(datasetId) {
  await requestJson(`/api/admin/datasets/${encodeURIComponent(datasetId)}`, { method: "DELETE" });
  setMessage(adminMessage, "数据集已删除", "success");
  await loadAdminDashboard();
}

async function activateManagedIndex(indexId) {
  await postJson(`/api/admin/indexes/${encodeURIComponent(indexId)}/activate`, {});
  setMessage(adminMessage, "索引已激活", "success");
  await loadAdminDashboard();
}

async function deleteManagedIndex(indexId) {
  await requestJson(`/api/admin/indexes/${encodeURIComponent(indexId)}`, { method: "DELETE" });
  setMessage(adminMessage, "索引已删除", "success");
  await loadAdminDashboard();
}

function saveSession(token, user) {
  state.authToken = token;
  state.currentUser = user;
  localStorage.setItem("authToken", token);
  localStorage.setItem("currentUser", JSON.stringify(user));
}

function toggleAdminOnly(element, visible) {
  if (!element) return;
  element.classList.toggle("d-none", !visible);
  element.hidden = !visible;
}

function applyRoleUI() {
  const admin = isAdmin();
  toggleAdminOnly(hubAdminBadge, admin);
  toggleAdminOnly(mainAdminBadge, admin);
  toggleAdminOnly(adminPanelSection, admin);
  if (adminCreateRole) {
    const adminOption = Array.from(adminCreateRole.options || []).find((item) => item.value === "admin");
    if (adminOption) {
      adminOption.hidden = !isSuperAdmin();
      adminOption.disabled = !isSuperAdmin();
      if (!isSuperAdmin() && adminCreateRole.value === "admin") {
        adminCreateRole.value = "user";
      }
    }
  }

  if (!admin) {
    state.adminOverview = null;
    state.adminUsers = [];
    state.adminDatasets = [];
    state.adminIndexes = [];
    state.adminBuildJobs = [];
    state.adminAuditLogs = [];
    renderAdminUserDetail(null);
    if (adminUsersBody) adminUsersBody.innerHTML = `<tr><td colspan="10" class="table-state">当前账号不是管理员，无法查看用户管理面板</td></tr>`;
    if (adminDatasetsBody) adminDatasetsBody.innerHTML = `<tr><td colspan="10" class="table-state">当前账号不是管理员，无法查看数据集管理面板</td></tr>`;
    if (adminIndexesBody) adminIndexesBody.innerHTML = `<tr><td colspan="10" class="table-state">当前账号不是管理员，无法查看索引管理面板</td></tr>`;
    if (adminBuildJobsBody) adminBuildJobsBody.innerHTML = `<tr><td colspan="7" class="table-state">当前账号不是管理员，无法查看任务监管面板</td></tr>`;
    if (adminAuditLogsBody) adminAuditLogsBody.innerHTML = `<tr><td colspan="6" class="table-state">当前账号不是管理员，无法查看审计面板</td></tr>`;
    if (adminUsersHint) adminUsersHint.textContent = "仅管理员可见";
    if (adminUserCount) adminUserCount.textContent = "0";
    if (adminActiveUserCount) adminActiveUserCount.textContent = "0";
    if (adminDisabledUserCount) adminDisabledUserCount.textContent = "0";
    if (adminDatasetCount) adminDatasetCount.textContent = "0";
    if (adminIndexCount) adminIndexCount.textContent = "0";
    if (adminFailedJobCount) adminFailedJobCount.textContent = "0";
    if (adminAdminCount) adminAdminCount.textContent = "0";
    if (adminInProgressJobCount) adminInProgressJobCount.textContent = "0";
    return;
  }

  setAdminTab(state.adminActiveTab || "overview");
}

function clearSession() {
  clearBuildPolling();
  clearPersistedBuildJob();
  state.authToken = "";
  state.currentUser = null;
  state.activeIndex = null;
  state.currentDataPath = "";
  state.currentDatasetInfo = null;
  state.adminOverview = null;
  state.adminUsers = [];
  state.adminDatasets = [];
  state.adminIndexes = [];
  state.adminBuildJobs = [];
  state.adminAuditLogs = [];
  state.adminUserDetail = null;
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

function noDataOption(text) {
  return {
    animation: false,
    backgroundColor: "transparent",
    xAxis: { show: false },
    yAxis: { show: false },
    series: [],
    graphic: {
      type: "text",
      left: "center",
      top: "middle",
      style: {
        text,
        fill: "#94a3b8",
        fontSize: 13,
      },
    },
  };
}

function getOrCreateChart(key, element) {
  if (!window.echarts || !element) return null;
  if (!state.charts[key]) {
    state.charts[key] = window.echarts.init(element, null, { renderer: "canvas" });
  }
  return state.charts[key];
}

function ensureAnalyticsCharts() {
  getOrCreateChart("cellTypeDonut", cellTypeDonutChartElement);
  getOrCreateChart("cellTypeQuality", cellTypeQualityBarChartElement);
  getOrCreateChart("sampleStack", sampleStackChartElement);
  getOrCreateChart("sampleSimilarity", sampleSimilarityChartElement);
  getOrCreateChart("qualityHistogram", qualityHistogramChartElement);
  getOrCreateChart("qualityBoxplot", qualityBoxplotChartElement);
}

function renderOverviewStrip(summary = {}) {
  if (overviewDatasetName) overviewDatasetName.textContent = summary.dataset_name || shortPath(state.currentDataPath);
  if (overviewTotalCells) overviewTotalCells.textContent = formatNumber(summary.total_cells);
  if (overviewCellTypeCount) overviewCellTypeCount.textContent = formatNumber(summary.cell_type_count);
  if (overviewSampleCount) overviewSampleCount.textContent = formatNumber(summary.sample_count);
  if (overviewAvgGeneCount) overviewAvgGeneCount.textContent = formatNumber(summary.avg_gene_count);
  if (overviewAvgMitoPct) overviewAvgMitoPct.textContent = formatPercentValue(summary.avg_mito_pct);
  const mitoChip = overviewAvgMitoPct?.closest(".overview-chip");
  if (mitoChip) mitoChip.classList.toggle("is-warning", Number(summary.avg_mito_pct) > 10);
}

function setScopeNotes(text) {
  if (cellTypeScopeNote) cellTypeScopeNote.textContent = text;
  if (sampleScopeNote) sampleScopeNote.textContent = text;
  if (qualityScopeNote) qualityScopeNote.textContent = text;
}

function currentScopeLabel() {
  if (state.umapSelectionCellIds.length) {
    return `框选 ${formatNumber(state.umapSelectionCellIds.length)} 个`;
  }
  if (state.chartFocus.key && state.chartFocus.value) {
    return state.chartFocus.key === "cell_type" ? `细胞类型 ${state.chartFocus.value}` : `样本 ${state.chartFocus.value}`;
  }
  if (Object.keys(activeFilters()).length) {
    return "筛选后";
  }
  return "全局";
}

function computeHistogram(values, bins = 12) {
  if (!values.length) return { bins: [], counts: [] };
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) {
    return { bins: [Number(min.toFixed(4))], counts: [values.length] };
  }
  const step = (max - min) / bins;
  const bucketCounts = new Array(bins).fill(0);
  for (const value of values) {
    const index = Math.min(bins - 1, Math.max(0, Math.floor((value - min) / step)));
    bucketCounts[index] += 1;
  }
  return {
    bins: bucketCounts.map((_, index) => Number((min + step * (index + 0.5)).toFixed(4))),
    counts: bucketCounts,
  };
}

function fiveNumberSummary(values) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const at = (ratio) => {
    const position = (sorted.length - 1) * ratio;
    const lower = Math.floor(position);
    const upper = Math.ceil(position);
    if (lower === upper) return sorted[lower];
    const weight = position - lower;
    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
  };
  return [
    Number(sorted[0].toFixed(4)),
    Number(at(0.25).toFixed(4)),
    Number(at(0.5).toFixed(4)),
    Number(at(0.75).toFixed(4)),
    Number(sorted[sorted.length - 1].toFixed(4)),
  ];
}

function buildSimilarityMatrix(samples, cellTypes, sampleTypeCounts) {
  const labels = [...samples];
  const vectors = labels.map((sample) => cellTypes.map((cellType) => sampleTypeCounts.get(`${sample}__${cellType}`) || 0));
  const matrix = [];
  for (let row = 0; row < labels.length; row += 1) {
    const rowVector = vectors[row];
    const rowNorm = Math.hypot(...rowVector) || 1;
    for (let col = 0; col < labels.length; col += 1) {
      const colVector = vectors[col];
      const colNorm = Math.hypot(...colVector) || 1;
      const dot = rowVector.reduce((sum, value, index) => sum + value * colVector[index], 0);
      matrix.push([row, col, Number((dot / (rowNorm * colNorm)).toFixed(4))]);
    }
  }
  return { labels, matrix };
}

function buildScopeAnalytics(points = []) {
  const safePoints = Array.isArray(points) ? points : [];
  const cellTypeCounts = new Map();
  const sampleCounts = new Map();
  const sampleTypeCounts = new Map();
  const geneValues = [];
  const umiValues = [];
  const mitoValues = [];

  for (const point of safePoints) {
    const cellType = metadataValue(point, "cell_type") || "Unknown";
    const sampleId = metadataValue(point, "sample_id") || "Unknown";
    const geneCount = numberOrNull(point?.metadata?.gene_count);
    const umiCount = numberOrNull(point?.metadata?.umi_count);
    const mitoPct = numberOrNull(point?.metadata?.mito_pct);

    cellTypeCounts.set(cellType, (cellTypeCounts.get(cellType) || 0) + 1);
    sampleCounts.set(sampleId, (sampleCounts.get(sampleId) || 0) + 1);
    sampleTypeCounts.set(`${sampleId}__${cellType}`, (sampleTypeCounts.get(`${sampleId}__${cellType}`) || 0) + 1);
    if (geneCount !== null) geneValues.push(geneCount);
    if (umiCount !== null) umiValues.push(umiCount);
    if (mitoPct !== null) mitoValues.push(mitoPct);
  }

  const sortedCellTypes = Array.from(cellTypeCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([name]) => name);
  const sortedSamples = Array.from(sampleCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name]) => name);

  const cellTypeDistribution = sortedCellTypes.map((name) => {
    const subset = safePoints.filter((point) => metadataValue(point, "cell_type") === name);
    const genes = subset.map((point) => numberOrNull(point?.metadata?.gene_count)).filter((value) => value !== null);
    const mito = subset.map((point) => numberOrNull(point?.metadata?.mito_pct)).filter((value) => value !== null);
    const avgGene = genes.length ? genes.reduce((sum, value) => sum + value, 0) / genes.length : null;
    const avgMito = mito.length ? mito.reduce((sum, value) => sum + value, 0) / mito.length : null;
    return {
      name,
      count: cellTypeCounts.get(name) || 0,
      avg_gene_count: avgGene === null ? null : Number(avgGene.toFixed(4)),
      avg_mito_pct: avgMito === null ? null : Number(avgMito.toFixed(4)),
    };
  });

  const sampleDistribution = {
    samples: sortedSamples,
    cell_types: sortedCellTypes.slice(0, 8),
    series: sortedCellTypes.slice(0, 8).map((cellType) => ({
      name: cellType,
      data: sortedSamples.map((sample) => sampleTypeCounts.get(`${sample}__${cellType}`) || 0),
    })),
    similarity: buildSimilarityMatrix(sortedSamples, sortedCellTypes.slice(0, 8), sampleTypeCounts),
  };

  const boxplotLabels = sortedCellTypes.slice(0, 8);
  const boxplotValues = boxplotLabels
    .map((cellType) => {
      const values = safePoints
        .filter((point) => metadataValue(point, "cell_type") === cellType)
        .map((point) => numberOrNull(point?.metadata?.gene_count))
        .filter((value) => value !== null);
      return fiveNumberSummary(values);
    })
    .filter(Boolean);

  return {
    summary: {
      dataset_name: state.analyticsGlobal?.summary?.dataset_name || shortPath(state.currentDataPath),
      total_cells: safePoints.length,
      cell_type_count: cellTypeCounts.size,
      sample_count: sampleCounts.size,
      avg_gene_count: geneValues.length ? Number((geneValues.reduce((sum, value) => sum + value, 0) / geneValues.length).toFixed(4)) : null,
      avg_umi_count: umiValues.length ? Number((umiValues.reduce((sum, value) => sum + value, 0) / umiValues.length).toFixed(4)) : null,
      avg_mito_pct: mitoValues.length ? Number((mitoValues.reduce((sum, value) => sum + value, 0) / mitoValues.length).toFixed(4)) : null,
    },
    cell_type_distribution: cellTypeDistribution,
    sample_distribution: sampleDistribution,
    quality: {
      gene_count_histogram: computeHistogram(geneValues),
      umi_count_histogram: computeHistogram(umiValues),
      mito_pct_histogram: computeHistogram(mitoValues),
      boxplot_gene_count: {
        labels: boxplotLabels.slice(0, boxplotValues.length),
        series: boxplotValues,
      },
    },
  };
}

function getCurrentScopePoints() {
  if (state.umapSelectionCellIds.length) {
    return state.umapSelectionCellIds
      .map((cellId) => state.umapFilteredPointByCellId.get(cellId) || state.umapPointByCellId.get(cellId))
      .filter(Boolean);
  }
  return state.umapFilteredPoints;
}

function analyticsForCurrentView() {
  const usingLocalScope =
    state.umapSelectionCellIds.length > 0 ||
    Object.keys(activeFilters()).length > 0 ||
    Boolean(state.chartFocus.key && state.chartFocus.value);
  if (!usingLocalScope || !state.umapPoints.length) {
    return state.analyticsGlobal;
  }
  return buildScopeAnalytics(getCurrentScopePoints());
}

function findResultByCellId(cellId) {
  return state.currentResults.find((item) => item.cell_id === cellId) || null;
}

function findPointByCellId(cellId) {
  return state.umapFilteredPointByCellId.get(cellId) || state.umapPointByCellId.get(cellId) || null;
}

function renderCellDetail(cellId = "") {
  if (!cellDetailPanel) return;
  const point = findPointByCellId(cellId);
  const result = findResultByCellId(cellId);
  if (!cellId || !point) {
    if (state.umapSelectionCellIds.length > 1) {
      const scopeAnalytics = buildScopeAnalytics(getCurrentScopePoints());
      cellDetailPanel.innerHTML = `
        <dt>选区</dt><dd>${escapeHtml(formatNumber(state.umapSelectionCellIds.length))} 个细胞</dd>
        <dt>类型数</dt><dd>${escapeHtml(formatNumber(scopeAnalytics?.summary?.cell_type_count))}</dd>
        <dt>样本数</dt><dd>${escapeHtml(formatNumber(scopeAnalytics?.summary?.sample_count))}</dd>
      `;
      return;
    }
    cellDetailPanel.innerHTML = `<dt>状态</dt><dd>尚未选中细胞</dd>`;
    return;
  }
  const metadata = point.metadata || {};
  const entries = [
    ["细胞 ID", cellId],
    ["细胞类型", metadata.cell_type || "-"],
    ["疾病", metadata.disease || "-"],
    ["年龄组", metadata.AgeGroup || "-"],
    ["性别", metadata.sex || "-"],
    ["组织", metadata.tissue || "-"],
    ["捐赠者", metadata.donor_id || metadata.sample_id || "-"],
    ["样本", metadata.sample_id || metadata.donor_id || "-"],
    ["基因数", formatNumber(metadata.gene_count)],
    ["UMI", formatNumber(metadata.umi_count)],
    ["线粒体比例", formatPercentValue(metadata.mito_pct)],
    ["UMAP X", formatMetric(point.x)],
    ["UMAP Y", formatMetric(point.y)],
  ];
  if (result) {
    entries.push(["距离", formatMetric(result.distance)]);
    entries.push(["相似度", formatMetric(result.score)]);
  }
  cellDetailPanel.innerHTML = entries
    .map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`)
    .join("");
}

function selectCell(cellId, { syncRow = true } = {}) {
  state.umapFocusedCellId = cellId || "";
  if (cellId) {
    state.umapSelectionCellIds = [];
  }
  renderUmapFromState();
  renderCellDetail(cellId);
  if (syncRow) {
    focusResultRow(cellId);
  }
}

function renderCellTypeCharts(analytics) {
  const donutChart = getOrCreateChart("cellTypeDonut", cellTypeDonutChartElement);
  const qualityChart = getOrCreateChart("cellTypeQuality", cellTypeQualityBarChartElement);
  const rows = analytics?.cell_type_distribution || [];
  if (!donutChart || !qualityChart) return;
  if (!rows.length) {
    donutChart.setOption(noDataOption("暂无细胞类型统计"), true);
    qualityChart.setOption(noDataOption("暂无质量指标统计"), true);
    return;
  }

  donutChart.setOption(
    {
      animationDuration: 220,
      tooltip: { trigger: "item" },
      legend: { show: false },
      series: [
        {
          type: "pie",
          radius: ["44%", "72%"],
          center: ["50%", "50%"],
          itemStyle: { borderWidth: 2, borderColor: "rgba(9,16,28,0.92)" },
          label: { color: "#cbd5e1", formatter: "{b}" },
          data: rows.map((item) => ({ name: item.name, value: item.count })),
        },
      ],
    },
    true
  );

  qualityChart.setOption(
    {
      animationDuration: 220,
      tooltip: { trigger: "axis" },
      legend: { top: 0, textStyle: { color: "#cbd5e1" } },
      grid: { left: 52, right: 20, top: 34, bottom: 50 },
      xAxis: {
        type: "category",
        axisLabel: { color: "#94a3b8", rotate: 18 },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.2)" } },
        data: rows.map((item) => item.name),
      },
      yAxis: [
        {
          type: "value",
          name: "基因数",
          nameTextStyle: { color: "#94a3b8" },
          axisLabel: { color: "#94a3b8" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
        },
        {
          type: "value",
          name: "线粒体%",
          nameTextStyle: { color: "#94a3b8" },
          axisLabel: { color: "#94a3b8" },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "平均基因数",
          type: "bar",
          data: rows.map((item) => item.avg_gene_count ?? 0),
          itemStyle: { color: "rgba(59,130,246,0.82)" },
        },
        {
          name: "平均线粒体比例",
          type: "line",
          yAxisIndex: 1,
          smooth: true,
          data: rows.map((item) => item.avg_mito_pct ?? 0),
          itemStyle: { color: "#f59e0b" },
        },
      ],
    },
    true
  );

  donutChart.off("click");
  qualityChart.off("click");
  const onCellTypeClick = (params) => applyChartFocus("cell_type", params?.name || "");
  donutChart.on("click", onCellTypeClick);
  qualityChart.on("click", onCellTypeClick);
}

function renderSampleCharts(analytics) {
  const stackChart = getOrCreateChart("sampleStack", sampleStackChartElement);
  const similarityChart = getOrCreateChart("sampleSimilarity", sampleSimilarityChartElement);
  const sampleDistribution = analytics?.sample_distribution || {};
  const samples = sampleDistribution.samples || [];
  const series = sampleDistribution.series || [];
  const similarity = sampleDistribution.similarity || { labels: [], matrix: [] };
  if (!stackChart || !similarityChart) return;
  if (!samples.length || !series.length) {
    stackChart.setOption(noDataOption("暂无样本来源统计"), true);
    similarityChart.setOption(noDataOption("暂无样本相似矩阵"), true);
    return;
  }

  stackChart.setOption(
    {
      animationDuration: 220,
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      legend: { top: 0, textStyle: { color: "#cbd5e1" } },
      grid: { left: 50, right: 18, top: 38, bottom: 44 },
      xAxis: {
        type: "category",
        data: samples,
        axisLabel: { color: "#94a3b8", rotate: 14 },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.2)" } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#94a3b8" },
        splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
      },
      series: series.map((item) => ({
        ...item,
        type: "bar",
        stack: "total",
        emphasis: { focus: "series" },
      })),
    },
    true
  );

  similarityChart.setOption(
    {
      animationDuration: 220,
      tooltip: {
        formatter(params) {
          const [row, col, score] = params.data || [];
          return `${escapeHtml(similarity.labels[row] || "-")} vs ${escapeHtml(similarity.labels[col] || "-")}<br>相似度: ${escapeHtml(formatMetric(score))}`;
        },
      },
      grid: { left: 62, right: 12, top: 20, bottom: 50 },
      xAxis: {
        type: "category",
        data: similarity.labels || [],
        axisLabel: { color: "#94a3b8", rotate: 18 },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.2)" } },
      },
      yAxis: {
        type: "category",
        data: similarity.labels || [],
        axisLabel: { color: "#94a3b8" },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.2)" } },
      },
      visualMap: {
        min: 0,
        max: 1,
        calculable: false,
        orient: "horizontal",
        left: "center",
        bottom: 0,
        textStyle: { color: "#94a3b8" },
      },
      series: [
        {
          type: "heatmap",
          data: similarity.matrix || [],
          label: { show: false },
          emphasis: { itemStyle: { borderColor: "#fff", borderWidth: 1 } },
        },
      ],
    },
    true
  );

  stackChart.off("click");
  similarityChart.off("click");
  stackChart.on("click", (params) => applyChartFocus("sample_id", params?.name || ""));
  similarityChart.on("click", (params) => {
    const row = params?.data?.[0];
    if (row === undefined) return;
    applyChartFocus("sample_id", similarity.labels[row] || "");
  });
}

function renderQualityCharts(analytics) {
  const histogramChart = getOrCreateChart("qualityHistogram", qualityHistogramChartElement);
  const boxplotChart = getOrCreateChart("qualityBoxplot", qualityBoxplotChartElement);
  const metricConfig = QUALITY_METRICS[state.qualityMetric] || QUALITY_METRICS.gene;
  const histogram = analytics?.quality?.[metricConfig.histogramKey] || { bins: [], counts: [] };
  const boxplot = analytics?.quality?.boxplot_gene_count || { labels: [], series: [] };
  if (!histogramChart || !boxplotChart) return;
  if (!histogram.bins?.length) {
    histogramChart.setOption(noDataOption("暂无质量分布"), true);
  } else {
    histogramChart.setOption(
      {
        animationDuration: 220,
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        grid: { left: 50, right: 16, top: 20, bottom: 40 },
        xAxis: {
          type: "category",
          data: histogram.bins.map((item) => formatMetric(item)),
          axisLabel: { color: "#94a3b8", showMinLabel: true, showMaxLabel: true },
          axisLine: { lineStyle: { color: "rgba(148,163,184,0.2)" } },
        },
        yAxis: {
          type: "value",
          axisLabel: { color: "#94a3b8" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
        },
        series: [
          {
            type: "bar",
            data: histogram.counts || [],
            itemStyle: { color: "rgba(34,211,238,0.78)" },
          },
        ],
      },
      true
    );
  }
  if (!boxplot.labels?.length || !boxplot.series?.length) {
    boxplotChart.setOption(noDataOption("暂无箱线图"), true);
  } else {
    boxplotChart.setOption(
      {
        animationDuration: 220,
        tooltip: { trigger: "item" },
        grid: { left: 52, right: 16, top: 20, bottom: 44 },
        xAxis: {
          type: "category",
          data: boxplot.labels,
          axisLabel: { color: "#94a3b8", rotate: 16 },
          axisLine: { lineStyle: { color: "rgba(148,163,184,0.2)" } },
        },
        yAxis: {
          type: "value",
          axisLabel: { color: "#94a3b8" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
        },
        series: [
          {
            type: "boxplot",
            data: boxplot.series,
            itemStyle: {
              color: "rgba(59,130,246,0.25)",
              borderColor: "#60a5fa",
            },
          },
        ],
      },
      true
    );
  }
}

function renderAnalyticsForCurrentState() {
  ensureAnalyticsCharts();
  const analytics = analyticsForCurrentView();
  if (!analytics) {
    renderOverviewStrip({});
    setScopeNotes("等待加载");
    return;
  }
  renderOverviewStrip(analytics.summary || {});
  setScopeNotes(currentScopeLabel());
  renderCellTypeCharts(analytics);
  renderSampleCharts(analytics);
  renderQualityCharts(analytics);
}

function applyChartFocus(key, value) {
  const normalizedValue = trimText(value);
  if (!normalizedValue) return;
  const isSameFocus = state.chartFocus.key === key && state.chartFocus.value === normalizedValue;
  state.chartFocus = isSameFocus ? { key: "", value: "" } : { key, value: normalizedValue };

  if (key === "cell_type" && filterCellType && !isSameFocus) {
    const optionExists = Array.from(filterCellType.options || []).some((option) => option.value === normalizedValue);
    if (optionExists) {
      filterCellType.value = normalizedValue;
      state.chartFocus = { key: "", value: "" };
    }
  }

  refreshUmapByControls();
  setMessage(
    queryStatus,
    isSameFocus ? "统计联动筛选已清除" : `已按${key === "cell_type" ? "细胞类型" : "样本"}联动到当前视图：${normalizedValue}`,
    "neutral"
  );
}

async function loadAnalyticsForCurrentDataset() {
  if (!state.currentDataPath) {
    state.analyticsGlobal = null;
    renderAnalyticsForCurrentState();
    return;
  }
  try {
    const analytics = await getJson(`/api/dataset/umap-stats?data_path=${encodeURIComponent(state.currentDataPath)}`);
    state.analyticsGlobal = analytics;
    renderAnalyticsForCurrentState();
  } catch (error) {
    state.analyticsGlobal = null;
    renderAnalyticsForCurrentState();
    setMessage(queryStatus, `统计数据加载失败：${error.message}`, "neutral");
  }
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

function humanizeBuildStage(stage) {
  return BUILD_STAGE_LABELS[stage] || stage || "处理中";
}

function renderIndexBuildTimeline(history = []) {
  if (!indexBuildTimeline) return;
  const safeHistory = Array.isArray(history) ? history : [];
  if (!safeHistory.length) {
    indexBuildTimeline.innerHTML = `
      <li class="build-timeline-item">
        <span class="build-timeline-dot"></span>
        <div>
          <div class="build-timeline-text">任务尚未开始</div>
        </div>
      </li>
    `;
    return;
  }

  indexBuildTimeline.innerHTML = safeHistory
    .slice()
    .reverse()
    .map(
      (item) => `
        <li class="build-timeline-item">
          <span class="build-timeline-dot"></span>
          <div>
            <div class="build-timeline-text">${escapeHtml(item.text || humanizeBuildStage(item.stage))}</div>
            <div class="build-timeline-time">${escapeHtml(formatClockTime(item.time))}</div>
          </div>
        </li>
      `
    )
    .join("");
}

function updateIndexProgress(job) {
  const status = trimText(job.status).toLowerCase();
  const isComplete = status === "completed";
  const isFailed = status === "failed";
  const stageLabel = isComplete ? "处理完成" : isFailed ? "处理失败" : "未处理完成";
  const barText = stageLabel;

  indexBuildProgressBar.style.width = "100%";
  indexBuildProgressBar.textContent = barText;
  indexBuildProgressBar.setAttribute("aria-valuenow", isComplete ? "100" : "0");
  indexBuildProgressBar.classList.remove("is-pending", "is-complete", "is-failed");
  indexBuildProgressBar.classList.add(isComplete ? "is-complete" : isFailed ? "is-failed" : "is-pending");

  if (indexBuildStageLabel) {
    indexBuildStageLabel.textContent = humanizeBuildStage(job.stage || status || "queued");
  }
  if (indexBuildElapsed) indexBuildElapsed.textContent = "";
  if (indexBuildProcessed) indexBuildProcessed.textContent = "";
  if (indexBuildRate) indexBuildRate.textContent = "";
  if (indexBuildEta) indexBuildEta.textContent = "";

  indexBuildProgressMeta.textContent = job.message || barText;
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
  if (!Number.isInteger(topK) || topK < 1 || topK > 10000) {
    throw new Error("Top-K must be an integer between 1 and 10000");
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

function isBuildContextCurrent(job = null) {
  if (job?.job_id && state.buildJobId && trimText(job.job_id) === trimText(state.buildJobId)) {
    return true;
  }
  return normalizePathToken(state.currentDataPath) === normalizePathToken(state.buildJobContextPath);
}

function focusResultRow(cellId) {
  if (!cellId || !resultsBody) return;
  const rows = resultsBody.querySelectorAll("tr[data-cell-id]");
  let matchedRow = null;
  rows.forEach((row) => {
    const isActive = row.dataset.cellId === cellId;
    row.classList.toggle("is-active", isActive);
    if (isActive) matchedRow = row;
  });
  if (matchedRow) {
    matchedRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

function focusCellOnUmap(cellId) {
  selectCell(cellId || "", { syncRow: false });
}

function initUmapChartIfNeeded() {
  if (state.umapChart || !window.echarts || !umapChartElement) return;
  state.umapChart = window.echarts.init(umapChartElement, null, { renderer: "canvas" });
  state.umapChart.setOption(buildUmapOption([], [], null, null));
  state.umapChart.on("click", (params) => {
    const cellId = params?.data?.cell_id;
    if (!cellId) return;
    focusResultRow(cellId);
    selectCell(cellId, { syncRow: false });
  });
  state.umapChart.on("brushSelected", (params) => {
    const selectedIndices = [];
    const batches = Array.isArray(params?.batch) ? params.batch : [];
    batches.forEach((batch) => {
      (batch.selected || []).forEach((item) => {
        if (item.seriesIndex !== 0) return;
        (item.dataIndex || []).forEach((index) => {
          const point = state.umapFilteredPoints[index];
          if (point?.cell_id) selectedIndices.push(point.cell_id);
        });
      });
    });
    state.umapSelectionCellIds = Array.from(new Set(selectedIndices));
    if (state.umapSelectionCellIds.length <= 1) {
      renderCellDetail(state.umapSelectionCellIds[0] || state.umapFocusedCellId);
    } else {
      state.umapFocusedCellId = "";
      renderCellDetail("");
    }
    renderAnalyticsForCurrentState();
  });
  window.addEventListener("resize", () => {
    resizeAllCharts();
  });
}

function buildUmapOption(baseData, highlightData, queryCenter, focusedPoint) {
  return {
    animation: false,
    brush: {
      toolbox: ["rect", "clear"],
      xAxisIndex: 0,
      yAxisIndex: 0,
      throttleType: "debounce",
      throttleDelay: 120,
      brushMode: "single",
      inBrush: { opacity: 1 },
      outOfBrush: { opacity: 0.14 },
    },
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
        type: "scatterGL",
        progressive: 6000,
        progressiveThreshold: 10000,
        data: baseData,
        symbolSize(value) {
          return value?.[2] ?? 2.4;
        },
        blendMode: "lighter",
        itemStyle: { opacity: 0.42 },
        silent: false,
      },
      {
        name: "Hits",
        type: "scatter",
        data: highlightData,
        symbolSize(value) {
          return Math.max(7.5, 10.8 - Math.min((value?.[2] || 1) - 1, 7) * 0.65);
        },
        itemStyle: {
          color: "#ffffff",
          borderColor: "#ef4444",
          borderWidth: 2,
          shadowBlur: 18,
          shadowColor: "rgba(239,68,68,0.55)",
        },
        z: 20,
      },
      {
        name: "Query Center",
        type: "scatter",
        data: queryCenter ? [queryCenter] : [],
        symbolSize: 16,
        itemStyle: {
          color: "#fbbf24",
          borderColor: "#fff7cc",
          borderWidth: 2,
          shadowBlur: 20,
          shadowColor: "rgba(251,191,36,0.65)",
        },
        z: 30,
      },
      {
        name: "Focused Cell",
        type: "scatter",
        data: focusedPoint ? [focusedPoint] : [],
        symbolSize: 13,
        itemStyle: {
          color: "#fde68a",
          borderColor: "#ffffff",
          borderWidth: 2,
          shadowBlur: 22,
          shadowColor: "rgba(253,230,138,0.7)",
        },
        z: 35,
      },
    ],
  };
}

function updateUmapInfoBar() {
  const total = state.umapMeta?.total_points ?? state.umapPoints.length;
  const shown = state.umapMeta?.returned_points ?? state.umapPoints.length;
  const filtered = state.umapFilteredPoints.length;
  const source = state.umapMeta?.visualization_source || "--";
  const sampled = state.umapMeta?.sampled ? "采样" : "全量";
  const level = state.umapMeta?.sampling_level || state.umapPreviewLevel || DEFAULT_UMAP_LEVEL;
  if (umapInfoTotal) umapInfoTotal.textContent = `总量 ${formatNumber(total)}`;
  if (umapInfoShown) umapInfoShown.textContent = `${level} ${formatNumber(shown)}`;
  if (umapInfoFiltered) umapInfoFiltered.textContent = `当前视图 ${formatNumber(filtered)}`;
  if (umapInfoSource) umapInfoSource.textContent = `来源 ${source}`;
  if (umapInfoSampled) umapInfoSampled.textContent = sampled;
}

function setDefaultUmapLegend() {
  if (!state.umapMeta || state.umapPoints.length === 0) {
    umapLegend.textContent = "暂无可视化数据";
    updateUmapInfoBar();
    return;
  }
  const total = state.umapMeta.total_points ?? state.umapPoints.length;
  const returned = state.umapMeta.returned_points ?? state.umapPoints.length;
  const source = state.umapMeta.visualization_source || "unknown";
  const level = state.umapMeta.sampling_level || state.umapPreviewLevel || DEFAULT_UMAP_LEVEL;
  const sampled = state.umapMeta.sampled ? " | sampled" : "";
  const filtered = state.umapFilteredPoints.length;
  const filterText = filtered !== returned ? ` | filtered ${formatNumber(filtered)}` : "";
  const selectionText = state.umapSelectionCellIds.length ? ` | selected ${formatNumber(state.umapSelectionCellIds.length)}` : "";
  umapLegend.textContent = `total ${formatNumber(total)} | ${level} ${formatNumber(returned)}${filterText}${selectionText} | ${source}${sampled}`;
  updateUmapInfoBar();
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

  state.umapMeta = {
    total_points: payload.total_points,
    returned_points: payload.returned_points ?? state.umapPoints.length,
    sampled: Boolean(payload.sampled),
    visualization_source: payload.visualization_source || "unknown",
    sampling_level: payload.sampling_level || state.umapPreviewLevel || DEFAULT_UMAP_LEVEL,
  };

  initUmapChartIfNeeded();
  state.umapHighlights = [];
  state.umapFocusedCellId = "";
  state.umapSelectionCellIds = [];
  state.umapQueryCenter = null;
  applyUmapFiltersLocally();
}

function clearUmapHighlights() {
  state.umapHighlights = [];
  state.umapQueryCenter = null;
  state.umapFocusedCellId = "";
  state.umapSelectionCellIds = [];
  renderUmapFromState();
  setDefaultUmapLegend();
  if (highlightMetric) highlightMetric.textContent = "0";
  renderCellDetail("");
  renderAnalyticsForCurrentState();
}

function buildFocusedPoint(cellId) {
  if (!cellId) return null;
  const point = state.umapFilteredPointByCellId.get(cellId) || state.umapPointByCellId.get(cellId);
  if (!point) return null;
  return {
    value: [point.x, point.y, 0],
    cell_id: point.cell_id,
  };
}

function buildQueryCenterPoint(cellId) {
  if (!cellId) return null;
  const point = state.umapFilteredPointByCellId.get(cellId) || state.umapPointByCellId.get(cellId);
  if (!point) return null;
  return {
    value: [point.x, point.y, 0],
    cell_id: point.cell_id,
  };
}

function renderUmapFromState() {
  if (!state.umapChart) return;
  const focusedPoint = buildFocusedPoint(state.umapFocusedCellId);
  state.umapChart.setOption(
    {
      series: [
        { data: state.umapBaseSeries },
        { data: state.umapHighlights },
        { data: state.umapQueryCenter ? [state.umapQueryCenter] : [] },
        { data: focusedPoint ? [focusedPoint] : [] },
      ],
    },
    false
  );
  setDefaultUmapLegend();
}

function applyUmapFiltersLocally() {
  const filters = combinedLocalFilters();
  const filteredPoints = state.umapPoints.filter((point) => pointMatchesFilters(point, filters));
  state.umapFilteredPoints = filteredPoints;
  state.umapFilteredPointByCellId = new Map();
  const allowedCellIds = new Set(filteredPoints.map((point) => point.cell_id));
  state.umapSelectionCellIds = state.umapSelectionCellIds.filter((cellId) => allowedCellIds.has(cellId));
  if (state.umapFocusedCellId && !allowedCellIds.has(state.umapFocusedCellId)) {
    state.umapFocusedCellId = "";
  }
  state.umapBaseSeries = filteredPoints.map((point) => {
    state.umapFilteredPointByCellId.set(point.cell_id, point);
    return {
      value: [point.x, point.y, 2.2],
      cell_id: point.cell_id,
      metadata: point.metadata,
      itemStyle: buildBaseItemStyle(point),
    };
  });
  renderUmapFromState();
  renderAnalyticsForCurrentState();
  renderCellDetail(state.umapFocusedCellId);
}

function applyUmapHighlights(results = [], modeLabel = "Query", queryCenterCellId = "") {
  if (!state.umapChart) return 0;
  let missingCount = 0;
  const highlights = [];

  for (const [index, item] of results.slice(0, HIGHLIGHT_LIMIT).entries()) {
    const base = state.umapFilteredPointByCellId.get(item.cell_id) || state.umapPointByCellId.get(item.cell_id);
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

  state.umapHighlights = highlights;
  state.umapQueryCenter = buildQueryCenterPoint(queryCenterCellId);
  renderUmapFromState();

  const total = state.umapMeta?.total_points ?? state.umapPoints.length;
  umapLegend.textContent =
    missingCount > 0
      ? `total ${formatNumber(total)} | ${modeLabel} highlights ${highlights.length} | missing ${missingCount}`
      : `total ${formatNumber(total)} | ${modeLabel} highlights ${highlights.length}`;
  updateUmapInfoBar();
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
  state.currentResults = Array.isArray(results) ? results : [];
  if (!Array.isArray(results) || results.length === 0) {
    state.umapFocusedCellId = "";
    renderCellDetail("");
    await showTableState("No results. Adjust query or filters.");
    return;
  }

  const html = results
    .map((item, idx) => {
      const md = item.metadata || {};
      return `
        <tr class="is-clickable" data-cell-id="${escapeHtml(item.cell_id)}">
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
  const rows = resultsBody.querySelectorAll("tr[data-cell-id]");
  rows.forEach((row) => {
    row.addEventListener("click", () => {
      const cellId = row.dataset.cellId || "";
      focusResultRow(cellId);
      selectCell(cellId, { syncRow: false });
    });
  });
}

function resetMainPageOutputs() {
  state.currentResults = [];
  state.chartFocus = { key: "", value: "" };
  state.umapSelectionCellIds = [];
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
    const data = await requestJson("/api/indexes", { timeoutMs: 3000 });
    state.historyIndexes = Array.isArray(data.indexes) ? data.indexes : [];
    renderHistoryCards(state.historyIndexes);
  } catch (error) {
    state.historyIndexes = [];
    historyCards.innerHTML = "";
    const timeoutLike = /timeout/i.test(error.message || "");
    setMessage(
      hubHistoryMessage,
      timeoutLike
        ? "历史索引加载超时，可先直接录入数据集进入核心页面"
        : `历史索引加载失败：${error.message}`,
      timeoutLike ? "neutral" : "error"
    );
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
      const parameterRows = historyIndexParamEntries(item)
        .map(
          ([label, value]) =>
            `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value === null || value === undefined || value === "" ? "--" : String(value))}</dd>`
        )
        .join("");
      return `
        <article class="history-card">
          <button
            class="history-card-delete"
            type="button"
            data-delete-index="${item.id}"
            aria-label="删除索引 ${escapeHtml(item.index_name)}"
            title="删除索引"
          >
            &times;
          </button>
          <h3 class="history-card-title">${escapeHtml(item.index_name)}</h3>
          <p class="history-card-subtitle">${escapeHtml(statusLabel)} | updated ${escapeHtml(item.updated_at || "-")}</p>
          <dl class="history-card-meta">
            <dt>Data Path</dt><dd>${escapeHtml(item.data_path || "-")}</dd>
            <dt>Collection</dt><dd>${escapeHtml(item.collection_name || "-")}</dd>
            <dt>Format</dt><dd>${escapeHtml(item.source_format || "-")}</dd>
            <dt>Index Type</dt><dd>${escapeHtml(humanizeIndexType(item.index_type))}</dd>
            <dt>Metric</dt><dd>${escapeHtml(humanizeDistanceMetric(item.distance_metric, item.effective_metric))}</dd>
            ${parameterRows}
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

  for (const btn of historyCards.querySelectorAll("[data-delete-index]")) {
    btn.addEventListener("click", async () => {
      const indexId = Number(btn.dataset.deleteIndex);
      if (!Number.isInteger(indexId) || indexId <= 0) return;
      btn.disabled = true;
      try {
        await deleteHistoryIndex(indexId);
      } catch (error) {
        setMessage(hubHistoryMessage, error.message, "error");
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

async function deleteHistoryIndex(indexId) {
  const indexRecord = state.historyIndexes.find((item) => Number(item.id) === indexId);
  if (!indexRecord) {
    throw new Error("未找到目标索引");
  }

  const confirmed = window.confirm(
    `确定要删除索引“${indexRecord.index_name}”吗？该操作会同时删除索引记录、构建任务记录以及 FAISS 索引文件，且不可恢复。`
  );
  if (!confirmed) {
    return;
  }

  setMessage(hubHistoryMessage, `Deleting ${indexRecord.index_name}...`, "neutral");
  const data = await requestJson(`/api/indexes/${encodeURIComponent(indexId)}`, { method: "DELETE" });
  const nextActiveIndex = data.next_active_index || null;
  if (
    state.activeIndex &&
    (Number(state.activeIndex.id) === indexId || state.activeIndex.collection_name === indexRecord.collection_name)
  ) {
    state.activeIndex = nextActiveIndex;
  }
  await loadHistoryIndexes();
  setMessage(hubHistoryMessage, `索引 ${indexRecord.index_name} 已删除`, "success", "", 10000);
}

async function loadHubData() {
  const tasks = [loadHistoryIndexes()];
  if (isAdmin()) {
    tasks.push(loadAdminDashboard());
  }
  await Promise.allSettled(tasks);
}

function loadHubDataInBackground() {
  loadHubData().catch((error) => {
    setMessage(hubHistoryMessage, `历史索引初始化失败：${error.message}`, "error");
  });
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
  state.aiAssistantOpen = false;
  if (aiAssistantInput) aiAssistantInput.value = "";
  resetAiAssistantConversation();
  setMessage(aiAssistantStatus, "可点击上方推荐问题，或在底部输入任意问题。", "neutral");
  renderDatasetInfo(state.currentDatasetInfo);
  if (umapPreviewLevel) {
    umapPreviewLevel.value = state.umapPreviewLevel || DEFAULT_UMAP_LEVEL;
  }
  if (umapColorMode) {
    umapColorMode.value = state.umapColorMode || "default";
  }

  showMainView();
  resetMainPageOutputs();
  setIndexProgressVisible(false);
  stopBuildElapsedTicker();
  indexBuildProgressBar.style.width = "100%";
  indexBuildProgressBar.textContent = "未处理完成";
  indexBuildProgressBar.setAttribute("aria-valuenow", "0");
  indexBuildProgressBar.classList.remove("is-pending", "is-complete", "is-failed");
  indexBuildProgressBar.classList.add("is-pending");
  indexBuildProgressMeta.textContent = "";
  if (indexBuildStageLabel) indexBuildStageLabel.textContent = "任务状态";
  if (indexBuildElapsed) indexBuildElapsed.textContent = "";
  if (indexBuildProcessed) indexBuildProcessed.textContent = "";
  if (indexBuildRate) indexBuildRate.textContent = "";
  if (indexBuildEta) indexBuildEta.textContent = "";
  renderIndexBuildTimeline([]);

  if (state.activeIndex?.id) {
    setBadgeState("is-ready", "Index Ready", "Top-K query available");
    setMessage(indexStatus, `Loaded index: ${state.activeIndex.index_name}`, "success");
  } else {
    setBadgeState("is-idle", "No Index", "UMAP available, build index when needed");
    setMessage(indexStatus, "No active index for current dataset", "neutral");
  }

  await Promise.all([
    loadUmapForCurrentDataset(),
    loadAnalyticsForCurrentDataset(),
    loadMetadataOptionsForCurrentDataset(),
  ]);

  await resumeBuildProgressForCurrentDataset();
}

async function loadUmapForCurrentDataset() {
  if (!state.currentDataPath) {
    applyUmapData({ points: [], returned_points: 0, total_points: 0, visualization_source: "none" });
    setMessage(queryStatus, "No data path for UMAP", "error");
    return;
  }

  umapLegend.textContent = "Loading UMAP...";
  setUmapLoading(true, "正在读取 UMAP 预览...");
  try {
    const level = state.umapPreviewLevel || DEFAULT_UMAP_LEVEL;
    const preview = await getJson(
      `/api/dataset/umap-preview?data_path=${encodeURIComponent(state.currentDataPath)}&level=${encodeURIComponent(level)}`
    );
    applyUmapData(preview);
    state.currentDatasetInfo = normalizeDatasetInfo(
      {
        ...state.currentDatasetInfo,
        visualization_source: preview.visualization_source || state.currentDatasetInfo?.visualization_source,
      },
      state.currentDataPath
    );
    renderDatasetInfo(state.currentDatasetInfo);
    return;
  } catch (previewError) {
    if (state.activeIndex?.id) {
      try {
        const indexed = await getJson(
          `/api/visualization/umap?index_id=${encodeURIComponent(state.activeIndex.id)}&limit=10000`
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
  } finally {
    setUmapLoading(false);
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
      loadAnalyticsForCurrentDataset(),
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
  const applyToCurrentView = isBuildContextCurrent(job);
  if (applyToCurrentView) {
    setIndexProgressVisible(true);
    updateIndexProgress(job);
  }

  if (job.status === "queued" || job.status === "running") {
    if (applyToCurrentView) {
      savePersistedBuildJob({ jobId: job.job_id, dataPath: state.buildJobContextPath || state.currentDataPath });
      setBadgeState("is-loading", "Building Index", "Writing vectors into FAISS");
      setMessage(indexStatus, job.message || "Build running...", "neutral");
    }
    return;
  }

  if (job.status === "failed") {
    clearPersistedBuildJob();
    clearBuildPolling();
    if (applyToCurrentView) {
      setBadgeState("is-error", "Build Failed", "Check data format or parameters");
      setMessage(indexStatus, job.error || job.message || "Index build failed", "error");
    }
    return;
  }

  if (job.status === "completed") {
    clearPersistedBuildJob();
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
      await loadAnalyticsForCurrentDataset();
    }
    await loadHistoryIndexes();
  }
}

async function pollBuildJob(jobId) {
  clearBuildPolling();
  state.buildJobId = jobId;
  const pollToken = state.buildPollToken;
  savePersistedBuildJob({ jobId, dataPath: state.buildJobContextPath || state.currentDataPath });

  const pollOnce = async () => {
    if (!state.buildJobId || pollToken !== state.buildPollToken || state.buildPollInFlight) return;
    state.buildPollInFlight = true;
    try {
      const data = await getJson(`/api/index/build/jobs/${encodeURIComponent(jobId)}`);
      if (pollToken !== state.buildPollToken || state.buildJobId !== jobId) return;
      const job = data.job || {};
      await handleBuildJobUpdate(job);
      if (pollToken !== state.buildPollToken || state.buildJobId !== jobId) return;
      if (job.status === "completed" || job.status === "failed") {
        clearBuildPolling();
      }
    } catch (error) {
      if (pollToken !== state.buildPollToken || state.buildJobId !== jobId) return;
      clearBuildPolling();
      setBadgeState("is-error", "Progress Error", "Failed to get build progress");
      setMessage(indexStatus, error.message, "error");
    } finally {
      if (pollToken === state.buildPollToken) {
        state.buildPollInFlight = false;
      }
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

  const buildOptions = currentIndexBuildOptions();

  buildIndexBtn.disabled = true;
  setCurrentDataset(path);
  state.activeIndex = null;
  state.buildJobContextPath = path;
  const queuedAt = new Date().toISOString();
  const localQueuedJob = {
    job_id: "",
    status: "queued",
    progress_pct: 0,
    stage: "queued",
    message: "任务已提交，等待进入执行队列",
    processed_cells: 0,
    total_cells: null,
    elapsed_seconds: 0,
    rate_cells_per_second: null,
    eta_seconds: null,
    created_at: queuedAt,
    updated_at: queuedAt,
    started_at: null,
    history: [{ stage: "queued", text: "构建任务已创建，等待执行", time: queuedAt }],
  };
  setBadgeState("is-loading", "Building Index", "Submitting async build task");
  setMessage(indexStatus, "索引构建任务已提交，可在下方查看实时进度。", "neutral");
  setIndexProgressVisible(true);
  updateIndexProgress(localQueuedJob);

  loadMetadataOptionsForCurrentDataset().catch(() => undefined);

  try {
    const response = await postJson("/api/index/build", {
      data_path: path,
      index_type: buildOptions.index_type,
      distance_metric: buildOptions.distance_metric,
      quantization_config: buildOptions.quantization_config,
      hnsw_params: buildOptions.hnsw_params,
      search_params: buildOptions.search_params,
      async: true,
      activate: true,
      reuse_if_available: true,
    });
    if (response.reused && response.index) {
      clearPersistedBuildJob();
      state.activeIndex = response.index;
      state.currentDatasetInfo = normalizeDatasetInfo(
        { ...state.currentDatasetInfo, ...response.index },
        state.currentDataPath
      );
      renderDatasetInfo(state.currentDatasetInfo);
      setIndexProgressVisible(false);
      setBadgeState("is-ready", "Index Ready", "Existing index reused");
      setMessage(indexStatus, `已直接复用历史索引：${response.index.index_name}`, "success");
      await loadMetadataOptionsForCurrentDataset();
      await loadHistoryIndexes();
      return;
    }
    if (!response.job_id) {
      throw new Error("Build job id missing");
    }
    updateIndexProgress({
      ...localQueuedJob,
      job_id: response.job_id,
      status: response.status || "queued",
      stage: response.stage || "queued",
      updated_at: new Date().toISOString(),
    });
    await pollBuildJob(response.job_id);
  } catch (error) {
    clearBuildPolling();
    setBadgeState("is-error", "Submit Failed", "Could not submit build task");
    setMessage(indexStatus, error.message, "error");
  } finally {
    buildIndexBtn.disabled = false;
  }
}

async function fetchBuildJobStatus(jobId) {
  const data = await getJson(`/api/index/build/jobs/${encodeURIComponent(jobId)}`);
  return data.job || null;
}

async function findLatestRunningBuildJob(dataPath) {
  const query = dataPath ? `?data_path=${encodeURIComponent(dataPath)}` : "";
  const data = await getJson(`/api/index/build/jobs/latest-running${query}`);
  return data.job || null;
}

async function resumeBuildProgressForCurrentDataset() {
  if (!state.currentDataPath || state.buildJobId) return false;

  const persisted = loadPersistedBuildJob();
  let job = null;

  if (persisted?.jobId && trimText(persisted.dataPath) === trimText(state.currentDataPath)) {
    try {
      job = await fetchBuildJobStatus(persisted.jobId);
    } catch {
      job = null;
    }
  }

  if (!job) {
    try {
      job = await findLatestRunningBuildJob(state.currentDataPath);
    } catch {
      job = null;
    }
  }

  if (!job || !["queued", "running"].includes(job.status)) {
    if (persisted && trimText(persisted.dataPath) === trimText(state.currentDataPath)) {
      clearPersistedBuildJob();
    }
    return false;
  }

  state.buildJobContextPath = state.currentDataPath;
  setIndexProgressVisible(true);
  updateIndexProgress(job);
  setBadgeState("is-loading", "Building Index", "Resuming task progress");
  setMessage(indexStatus, job.message || "正在恢复索引构建进度...", "neutral");
  await pollBuildJob(job.job_id);
  return true;
}

async function restoreBuildPageAfterLogin() {
  const persisted = loadPersistedBuildJob();
  if (!persisted?.jobId || !persisted?.dataPath) return false;

  let job = null;
  try {
    job = await fetchBuildJobStatus(persisted.jobId);
  } catch {
    try {
      job = await findLatestRunningBuildJob(persisted.dataPath);
    } catch {
      job = null;
    }
  }

  if (!job || !["queued", "running"].includes(job.status)) {
    clearPersistedBuildJob();
    return false;
  }

  const infoRaw = await postJson("/api/dataset/inspect", { data_path: persisted.dataPath });
  state.activeIndex = null;
  await enterCorePage({
    dataPath: persisted.dataPath,
    info: normalizeDatasetInfo(infoRaw, persisted.dataPath),
    indexRecord: null,
  });
  return true;
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
    const highlightCount = applyUmapHighlights(data.results, "ID query", cellId);
    selectCell(cellId, { syncRow: true });
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
    if (Array.isArray(data.results) && data.results.length) {
      selectCell(data.results[0].cell_id, { syncRow: true });
    }
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
  METADATA_FILTER_FIELDS.forEach((field) => {
    if (field.element) field.element.value = "";
  });
  if (umapColorMode) {
    umapColorMode.value = "default";
    state.umapColorMode = "default";
  }
  state.chartFocus = { key: "", value: "" };
  state.umapSelectionCellIds = [];
  applyUmapFiltersLocally();
  clearUmapHighlights();
  focusResultRow("");
  setMessage(queryStatus, "UMAP 已恢复到默认全局概览", "neutral");
}

function refreshUmapByControls() {
  setUmapLoading(true, "正在按当前筛选条件重绘...");
  window.requestAnimationFrame(() => {
    applyUmapFiltersLocally();
    if (state.currentResults.length) {
      applyUmapHighlights(state.currentResults, "Filtered view", state.umapQueryCenter?.cell_id || "");
    }
    setUmapLoading(false);
  });
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
    loadHubDataInBackground();
    const restored = await restoreBuildPageAfterLogin();
    if (!restored) {
      showHubView();
    }
  } catch {
    clearSession();
  }
}

async function enterAfterLogin(token, user) {
  saveSession(token, user);
  showHubView();
  loadHubDataInBackground();
  const restored = await restoreBuildPageAfterLogin();
  if (!restored) {
    showHubView();
  }
}

window.__seworkAfterLogin = enterAfterLogin;

logoutBtn.addEventListener("click", clearSession);
hubLogoutBtn.addEventListener("click", clearSession);

openNewDatasetBtn.addEventListener("click", () => {
  openNewDatasetFromHub().catch((error) => {
    setMessage(hubNewDatasetMessage, error.message, "error");
  });
});

if (aiAssistantLauncher) {
  aiAssistantLauncher.addEventListener("click", () => {
    setAiAssistantPanelOpen(!state.aiAssistantOpen);
  });
}

if (contextHelpTrigger) {
  contextHelpTrigger.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    setContextHelpOpen(!state.contextHelpOpen);
  });
}

if (contextHelpOverlayClose) {
  contextHelpOverlayClose.addEventListener("click", () => {
    setContextHelpOpen(false);
  });
}

if (contextHelpOverlay) {
  contextHelpOverlay.addEventListener("click", (event) => {
    if (event.target === contextHelpOverlay) {
      setContextHelpOpen(false);
    }
  });
}

window.addEventListener("resize", () => {
  if (state.contextHelpOpen) {
    setContextHelpOpen(true);
  }
});

if (aiAssistantClose) {
  aiAssistantClose.addEventListener("click", () => {
    setAiAssistantPanelOpen(false);
  });
}

if (aiAssistantSuggestedQuestionBtn) {
  aiAssistantSuggestedQuestionBtn.addEventListener("click", () => {
    sendAiAssistantQuestion(AI_ASSISTANT_SUGGESTED_QUESTION).catch(() => undefined);
  });
}

if (aiAssistantSendBtn) {
  aiAssistantSendBtn.addEventListener("click", () => {
    sendAiAssistantQuestion(aiAssistantInput?.value || "").catch(() => undefined);
  });
}

if (aiAssistantInput) {
  aiAssistantInput.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      sendAiAssistantQuestion(aiAssistantInput.value || "").catch(() => undefined);
    }
  });
}

backToHubBtn.addEventListener("click", async () => {
  showHubView();
  await loadHubData();
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

if (indexTypeInput) {
  indexTypeInput.addEventListener("change", () => {
    updateIndexConfigVisibility();
  });
}

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

if (umapPreviewLevel) {
  umapPreviewLevel.addEventListener("change", () => {
    state.umapPreviewLevel = umapPreviewLevel.value || DEFAULT_UMAP_LEVEL;
    loadUmapForCurrentDataset().catch((error) => {
      setMessage(queryStatus, error.message, "error");
    });
  });
}

if (umapColorMode) {
  umapColorMode.addEventListener("change", () => {
    state.umapColorMode = umapColorMode.value || "default";
    refreshUmapByControls();
  });
}

qualityMetricButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const metric = button.dataset.qualityMetric || "gene";
    state.qualityMetric = metric;
    qualityMetricButtons.forEach((item) => item.classList.toggle("is-active", item === button));
    renderAnalyticsForCurrentState();
  });
});

METADATA_FILTER_FIELDS.forEach((field) => {
  if (!field.element) return;
  field.element.addEventListener("change", () => {
    refreshUmapByControls();
  });
});

if (evaluateToggle) {
  evaluateToggle.addEventListener("change", () => {
    refreshEvaluationUI();
  });
}

if (adminRefreshDashboardBtn) {
  adminRefreshDashboardBtn.addEventListener("click", () => {
    loadAdminDashboard().catch((error) => {
      setMessage(adminMessage, error.message, "error");
    });
  });
}

if (adminTabs) {
  adminTabs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-admin-tab]");
    if (!button) return;
    setAdminTab(button.dataset.adminTab || "overview");
  });
}

if (adminCreateUserBtn) {
  adminCreateUserBtn.addEventListener("click", () => {
    createManagedUser().catch((error) => {
      setMessage(adminMessage, error.message, "error");
    });
  });
}

if (adminUsersBody) {
  adminUsersBody.addEventListener("click", (event) => {
    const button = event.target.closest("[data-admin-action]");
    if (!button) return;

    const action = button.dataset.adminAction;
    const userId = Number(button.dataset.userId);
    if (!Number.isInteger(userId) || userId <= 0) return;

    const run = async () => {
      button.disabled = true;
      try {
        if (action === "detail-user") {
          await loadAdminUserDetail(userId);
          return;
        }

        if (action === "toggle-status") {
          const current = state.adminUsers.find((item) => Number(item.id) === userId);
          if (!current) throw new Error("未找到目标用户");
          const nextActive = !Boolean(current.is_active);
          const confirmed = window.confirm(`确定要将账号“${current.username}”${nextActive ? "启用" : "停用"}吗？`);
          if (!confirmed) return;
          await updateManagedUser(
            userId,
            { is_active: nextActive },
            `账号 ${current.username} 已${nextActive ? "启用" : "停用"}`
          );
          return;
        }

        if (action === "reset-password") {
          const current = state.adminUsers.find((item) => Number(item.id) === userId);
          if (!current) throw new Error("未找到目标用户");
          const password = window.prompt(`请输入账号“${current.username}”的新密码（至少 6 位）`);
          if (password === null) return;
          if (String(password).length < 6) throw new Error("密码至少需要 6 位");
          await resetManagedUserPassword(userId, password);
          return;
        }

        if (action === "toggle-role") {
          const current = state.adminUsers.find((item) => Number(item.id) === userId);
          if (!current) throw new Error("未找到目标用户");
          const nextRole = current.role === "admin" ? "user" : "admin";
          const confirmed = window.confirm(`确定要将账号“${current.username}”调整为 ${nextRole} 吗？`);
          if (!confirmed) return;
          await updateManagedUser(userId, { role: nextRole }, `账号 ${current.username} 已调整为 ${nextRole}`);
          return;
        }

        if (action === "delete-user") {
          const current = state.adminUsers.find((item) => Number(item.id) === userId);
          if (!current) throw new Error("未找到目标用户");
          const confirmed = window.confirm(`确定要删除账号“${current.username}”吗？该操作不可恢复。`);
          if (!confirmed) return;
          await deleteManagedUser(userId);
        }
      } catch (error) {
        setMessage(adminMessage, error.message, "error");
      } finally {
        button.disabled = false;
      }
    };

    run().catch((error) => {
      setMessage(adminMessage, error.message, "error");
      button.disabled = false;
    });
  });
}

if (adminDatasetsBody) {
  adminDatasetsBody.addEventListener("click", (event) => {
    const button = event.target.closest("[data-admin-action='delete-dataset']");
    if (!button) return;
    const datasetId = Number(button.dataset.datasetId);
    if (!Number.isInteger(datasetId) || datasetId <= 0) return;
    const current = state.adminDatasets.find((item) => Number(item.id) === datasetId);
    const label = current?.dataset_name || `#${datasetId}`;
    const run = async () => {
      button.disabled = true;
      try {
        const confirmed = window.confirm(`确定要删除数据集“${label}”吗？关联索引也会一并删除。`);
        if (!confirmed) return;
        await deleteManagedDataset(datasetId);
      } catch (error) {
        setMessage(adminMessage, error.message, "error");
      } finally {
        button.disabled = false;
      }
    };
    run().catch((error) => {
      setMessage(adminMessage, error.message, "error");
      button.disabled = false;
    });
  });
}

if (adminIndexesBody) {
  adminIndexesBody.addEventListener("click", (event) => {
    const button = event.target.closest("[data-admin-action]");
    if (!button) return;
    const action = button.dataset.adminAction;
    const indexId = Number(button.dataset.indexId);
    if (!Number.isInteger(indexId) || indexId <= 0) return;
    const current = state.adminIndexes.find((item) => Number(item.id) === indexId);
    const label = current?.index_name || `#${indexId}`;
    const run = async () => {
      button.disabled = true;
      try {
        if (action === "activate-index") {
          await activateManagedIndex(indexId);
          return;
        }
        if (action === "delete-index") {
          const confirmed = window.confirm(`确定要删除索引“${label}”吗？该操作不可恢复。`);
          if (!confirmed) return;
          await deleteManagedIndex(indexId);
        }
      } catch (error) {
        setMessage(adminMessage, error.message, "error");
      } finally {
        button.disabled = false;
      }
    };
    run().catch((error) => {
      setMessage(adminMessage, error.message, "error");
      button.disabled = false;
    });
  });
}

setQueryMetrics();
refreshEvaluationUI();
updateIndexConfigVisibility();
showTableState("No query results yet. Build/activate an index then query.").catch(() => undefined);
checkAuthAndInit();
