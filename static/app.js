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
const hubAdminManualLink = document.querySelector("#hubAdminManualLink");
const mainAdminManualLink = document.querySelector("#mainAdminManualLink");

const historyCards = document.querySelector("#historyCards");
const hubHistoryMessage = document.querySelector("#hubHistoryMessage");
const hubDataPath = document.querySelector("#hubDataPath");
const hubDatasetFile = document.querySelector("#hubDatasetFile");
const hubDatasetFileName = document.querySelector("#hubDatasetFileName");
const uploadDatasetBtn = document.querySelector("#uploadDatasetBtn");
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
const datasetFileInput = document.querySelector("#datasetFile");
const datasetFileName = document.querySelector("#datasetFileName");
const uploadDataBtn = document.querySelector("#uploadDataBtn");
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
const aiAssistantDragHandle = document.querySelector("#aiAssistantDragHandle");
const aiAssistantHeroEyebrow = document.querySelector("#aiAssistantHeroEyebrow");
const aiAssistantHeroTitle = document.querySelector("#aiAssistantHeroTitle");
const aiAssistantHeroDescription = document.querySelector("#aiAssistantHeroDescription");
const aiAssistantModeCards = document.querySelector("#aiAssistantModeCards");
const aiAssistantSuggestionsList = document.querySelector("#aiAssistantSuggestionsList");
const aiAssistantRefreshSuggestions = document.querySelector("#aiAssistantRefreshSuggestions");
const aiAssistantMoveToggle = document.querySelector("#aiAssistantMoveToggle");
const aiAssistantFullscreenToggle = document.querySelector("#aiAssistantFullscreenToggle");
const aiAssistantClose = document.querySelector("#aiAssistantClose");
const aiAssistantInput = document.querySelector("#aiAssistantInput");
const aiAssistantRegenerateBtn = document.querySelector("#aiAssistantRegenerateBtn");
const aiAssistantSendBtn = document.querySelector("#aiAssistantSendBtn");
const aiAssistantStatus = document.querySelector("#aiAssistantStatus");
const aiAssistantConversationToggle = document.querySelector("#aiAssistantConversationToggle");
const aiAssistantMessages = document.querySelector("#aiAssistantMessages");

const filterCellType = document.querySelector("#filterCellType");
const filterDisease = document.querySelector("#filterDisease");
const filterAgeGroup = document.querySelector("#filterAgeGroup");
const filterDatasetName = document.querySelector("#filterDatasetName");
const filterSex = document.querySelector("#filterSex");
const filterTissue = document.querySelector("#filterTissue");
const filterDonorId = document.querySelector("#filterDonorId");

const cellIdInput = document.querySelector("#cellId");
const topKIdInput = document.querySelector("#topKId");
const queryVectorInput = document.querySelector("#queryVector");
const queryVectorCsvInput = document.querySelector("#queryVectorCsv");
const topKVectorInput = document.querySelector("#topKVector");
const searchByIdBtn = document.querySelector("#searchByIdBtn");
const searchByVectorBtn = document.querySelector("#searchByVectorBtn");
const queryStatus = document.querySelector("#queryStatus");
const evaluateToggle = document.querySelector("#evaluateToggle");
const evaluationSummary = document.querySelector("#evaluationSummary");
const annBenchmarkPanel = document.querySelector("#annBenchmarkPanel");
const annBenchmarkDelta = document.querySelector("#annBenchmarkDelta");
const annBeforeTime = document.querySelector("#annBeforeTime");
const annBeforePrecision = document.querySelector("#annBeforePrecision");
const annBeforeRecall = document.querySelector("#annBeforeRecall");
const annBeforeOverlap = document.querySelector("#annBeforeOverlap");
const annAfterTime = document.querySelector("#annAfterTime");
const annAfterPrecision = document.querySelector("#annAfterPrecision");
const annAfterRecall = document.querySelector("#annAfterRecall");
const annAfterOverlap = document.querySelector("#annAfterOverlap");
const annExactTime = document.querySelector("#annExactTime");
const annExactPrecision = document.querySelector("#annExactPrecision");
const annExactRecall = document.querySelector("#annExactRecall");
const annAfterIndexSize = document.querySelector("#annAfterIndexSize");
const annAfterRss = document.querySelector("#annAfterRss");
const annExactIndexSize = document.querySelector("#annExactIndexSize");
const annExactRss = document.querySelector("#annExactRss");

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
const exportUmapCsvBtn = document.querySelector("#exportUmapCsvBtn");
const exportUmapJsonBtn = document.querySelector("#exportUmapJsonBtn");
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
const resultsPagination = document.querySelector("#resultsPagination");
const resultsPageSummary = document.querySelector("#resultsPageSummary");
const resultsPageButtons = document.querySelector("#resultsPageButtons");
const resultsPrevPage = document.querySelector("#resultsPrevPage");
const resultsNextPage = document.querySelector("#resultsNextPage");

const HIGHLIGHT_LIMIT = 100;
const RESULTS_PAGE_SIZE = 10;
const BUILD_JOB_POLL_MS = 1200;
const BUILD_JOB_STORAGE_KEY = "sework.activeBuildJob";
const DEFAULT_UMAP_LEVEL = "preview";
const AI_ASSISTANT_POSITION_STORAGE_KEY = "sework.aiAssistantPosition";
const AI_ASSISTANT_VISIBLE_SUGGESTION_COUNT = 4;
const AI_ASSISTANT_MODE_ORDER = ["cell_query", "result_explanation", "knowledge_qa", "index_advice"];
const AI_ASSISTANT_MODE_CONFIG = {
  cell_query: {
    label: "细胞自然语言分析",
    shortLabel: "查细胞",
    heroEyebrow: "Hi~",
    heroTitle: "我是单细胞检索助手",
    heroDescription: "告诉我你想找哪类细胞、组织或疾病相关群体，我会联动当前数据集、结构化结果和知识证据一起回答。",
    placeholder: "请输入自然语言问题，例如：肝脏数据中和 fibrosis 相关的细胞类型有哪些？",
    intro:
      "你好，我可以结合当前数据集、知识库和检索结果回答细胞类型、marker gene、疾病关联、结果解释和下一步分析建议。",
    idleStatus: "可切换模式后提问，系统会联动知识库、细胞结果和 UMAP 展示。",
    endpoint: "/api/ai/cell-query",
    suggestions: [
      "查找与肝纤维化相关的免疫细胞，并解释为什么这些细胞值得关注。",
      "这个数据集里最像 T 细胞的是哪类细胞？",
      "帮我找出 liver 数据中可能与炎症相关的细胞群。",
      "哪些细胞和 macrophage 更接近，并给出原因？",
      "请结合当前结果，筛选值得优先关注的 fibrosis 相关细胞。",
      "如果我要观察 hepatocyte 附近的相关细胞，应该关注哪些候选？",
      "在当前数据集中，哪些 cell_type 最值得作为后续分析起点？",
      "请用自然语言总结当前数据集中最值得关注的细胞群。",
    ],
  },
  result_explanation: {
    label: "结果解释",
    shortLabel: "解释结果",
    heroEyebrow: "Explain",
    heroTitle: "我来解释为什么召回这些细胞",
    heroDescription: "当你已经做过 ID 或向量检索后，我可以结合 metadata、知识库和当前结果，解释这些细胞为什么会被召回。",
    placeholder: "例如：为什么这些细胞被召回？哪些证据支持它们可能是巨噬细胞？",
    intro:
      "你好，我可以解释当前检索结果的生物学意义，结合 metadata、知识库证据和 UMAP 联动说明为什么这些细胞值得关注。",
    idleStatus: "适合在完成一次检索后使用，帮助你解释结果来源、细胞类型和潜在意义。",
    endpoint: "/api/ai/cell-query",
    suggestions: [
      "为什么这些细胞被召回？请结合 metadata 和知识库说明。",
      "这些结果为什么可能是 macrophage，而不是 monocyte？",
      "请解释当前高亮细胞在 UMAP 上聚集意味着什么。",
      "这些细胞和 fibrosis 的关系是什么？",
      "哪些证据支持当前候选细胞与 stellate cell 更接近？",
      "为什么当前结果里会同时出现 immune cell 和 fibroblast？",
      "请解释当前 Top-K 结果的共同特征。",
      "从检索结果看，当前查询最可能对应哪类细胞？",
    ],
  },
  knowledge_qa: {
    label: "知识库问答",
    shortLabel: "知识问答",
    heroEyebrow: "Knowledge",
    heroTitle: "我可以回答 marker 和 cell type 问题",
    heroDescription: "你可以直接问某个 cell_type 的 marker gene、组织背景、生物学含义和常见分析注意点。",
    placeholder: "例如：这个 cell_type 的常见 marker gene 是什么？",
    intro:
      "你好，我可以结合知识库回答 cell_type、marker gene、组织和疾病关联等问题，并提醒你如何与当前数据集联合验证。",
    idleStatus: "适合查询 marker gene、细胞类型定义、组织来源和生物学意义。",
    endpoint: "/api/ai/cell-query",
    suggestions: [
      "这个 cell_type 的常见 marker gene 是什么？",
      "stellate cell 和 fibroblast 在 liver 中有什么区别？",
      "为什么 fibrosis 分析里要重点关注 macrophage、stellate cell 和 fibroblast？",
      "UMAP 上彼此靠近就一定是同类细胞吗？",
      "T cell 的常见 marker gene 是什么，应该如何验证？",
      "hepatocyte 在 liver 数据中通常有什么特征？",
      "如果我想判断某类细胞是不是 NK cell，应该看哪些 marker？",
      "知识库里与 liver 分析最相关的细胞类型有哪些？",
    ],
  },
  index_advice: {
    label: "索引建议",
    shortLabel: "索引建议",
    heroEyebrow: "Index",
    heroTitle: "我可以帮你选索引和参数",
    heroDescription: "如果你在 HNSW、IVF、PQ 之间犹豫，或者不知道 nlist、nprobe、M、efConstruction 怎么设，可以直接问我。",
    placeholder: "请输入索引或参数问题，例如：当前数据集更适合 HNSW 还是 IVF？",
    intro:
      "你好，我可以结合当前数据集回答 HNSW、IVF、PQ 的差异，帮助你选择距离度量和构建参数。",
    idleStatus: "可点击上方推荐问题，或直接咨询索引类型、参数设置和性能取舍。",
    endpoint: "/api/ai/chat",
    suggestions: [
      "请结合当前数据集，分别说明 HNSW、IVF、PQ 的优势、劣势、适用场景，并给出各自推荐的参数设置。",
      "当前数据集更适合 HNSW 还是 IVF？为什么？",
      "如果我更关注召回率，HNSW 参数应该怎么调？",
      "IVF 的 nlist 和 nprobe 应该如何权衡速度与准确率？",
      "在资源受限场景下，PQ 什么时候值得用？",
      "当前数据集的向量维度和规模下，推荐哪种索引结构？",
      "如果我要做交互式查询，HNSW 和 IVF 哪个更稳？",
      "如何向老师解释不同索引策略的取舍逻辑？",
    ],
  },
};

const QUALITY_METRICS = {
  gene: { label: "基因数", histogramKey: "gene_count_histogram", pointField: "gene_count" },
  umi: { label: "UMI", histogramKey: "umi_count_histogram", pointField: "umi_count" },
  mito: { label: "线粒体比例", histogramKey: "mito_pct_histogram", pointField: "mito_pct" },
};

const METADATA_FILTER_FIELDS = [
  { key: "cell_type", element: filterCellType, label: "Cell Type" },
  { key: "disease", element: filterDisease, label: "Disease" },
  { key: "AgeGroup", element: filterAgeGroup, label: "Age Group" },
  { key: "dataset_name", element: filterDatasetName, label: "Dataset" },
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
  umapChartDpr: 0,
  umapResizeObserver: null,
  chartResizeBound: false,
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
  currentResultsPage: 1,
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
  aiAssistantMode: "cell_query",
  aiAssistantMessages: [],
  aiAssistantLastQuestion: "",
  aiAssistantSuggestionOffsets: {},
  aiAssistantPosition: loadAiAssistantPosition(),
  aiAssistantMoveEnabled: false,
  aiAssistantFullscreen: false,
  aiAssistantConversationExpanded: false,
  aiAssistantDrag: {
    active: false,
    offsetX: 0,
    offsetY: 0,
  },
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

function getCurrentDevicePixelRatio() {
  const dpr = Number(window.devicePixelRatio) || 1;
  return dpr > 0 ? dpr : 1;
}

function buildChartInitOptions() {
  return {
    renderer: "canvas",
    devicePixelRatio: getCurrentDevicePixelRatio(),
    useDirtyRect: false,
  };
}

function getElementClientSize(element) {
  if (!element) return { width: 0, height: 0 };
  const rect = element.getBoundingClientRect();
  const width = Math.round(element.clientWidth || rect.width || 0);
  const height = Math.round(element.clientHeight || rect.height || 0);
  return { width, height };
}

function resizeChartToElement(chart, element) {
  if (!chart || !element) return;
  const { width, height } = getElementClientSize(element);
  if (width > 0 && height > 0) {
    chart.resize({ width, height, silent: true });
    return;
  }
  chart.resize();
}

function canvasMatchesDevicePixelRatio(container, dpr = getCurrentDevicePixelRatio()) {
  if (!container) return true;
  const canvases = Array.from(container.querySelectorAll("canvas"));
  if (!canvases.length) return true;
  return canvases.every((canvas) => {
    const rect = canvas.getBoundingClientRect();
    const cssWidth = Math.round(canvas.clientWidth || rect.width || 0);
    const cssHeight = Math.round(canvas.clientHeight || rect.height || 0);
    if (cssWidth <= 0 || cssHeight <= 0) return true;
    const expectedWidth = Math.round(cssWidth * dpr);
    const expectedHeight = Math.round(cssHeight * dpr);
    const widthDelta = Math.abs((canvas.width || 0) - expectedWidth);
    const heightDelta = Math.abs((canvas.height || 0) - expectedHeight);
    return widthDelta <= 2 && heightDelta <= 2;
  });
}

function captureUmapViewportState() {
  if (!state.umapChart?.getOption) return null;
  const option = state.umapChart.getOption();
  const dataZoom = Array.isArray(option?.dataZoom)
    ? option.dataZoom.map((zoom) => ({
        start: zoom.start,
        end: zoom.end,
        startValue: zoom.startValue,
        endValue: zoom.endValue,
      }))
    : [];
  return dataZoom.length ? { dataZoom } : null;
}

function restoreUmapViewportState(chart, snapshot) {
  if (!chart || !snapshot?.dataZoom?.length) return;
  chart.setOption({ dataZoom: snapshot.dataZoom }, false);
}

function parseJson(raw) {
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function loadAiAssistantPosition() {
  const stored = parseJson(localStorage.getItem(AI_ASSISTANT_POSITION_STORAGE_KEY));
  if (!stored || typeof stored !== "object") return null;
  const left = Number(stored.left);
  const top = Number(stored.top);
  if (!Number.isFinite(left) || !Number.isFinite(top)) return null;
  return { left, top };
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

function formatCompactTimeMs(value) {
  if (value === null || value === undefined || value === "") return "--";
  const num = Number(value);
  if (!Number.isFinite(num)) return String(value);
  if (num >= 100) return `${Math.round(num)} ms`;
  if (num >= 10) return `${num.toFixed(1)} ms`;
  return `${num.toFixed(2)} ms`;
}

function deriveDatasetTitle(item) {
  const pathSource = trimText(item?.data_path);
  const indexSource = trimText(item?.index_name);
  const rawName = (pathSource.split(/[\\/]/).pop() || indexSource || "dataset").replace(/\.(csv|h5ad)$/i, "");
  const primaryToken = trimText(rawName.split(/[_\-\s]+/)[0]) || trimText(indexSource.split(/[_\-\s]+/)[0]) || "dataset";
  const normalized = primaryToken
    ? `${primaryToken.charAt(0).toUpperCase()}${primaryToken.slice(1).toLowerCase()}`
    : "Dataset";
  return `${normalized} Dataset`;
}

function deriveDatasetSubtitle(item) {
  const indexName = trimText(item?.index_name);
  if (indexName) return indexName;
  const pathSource = trimText(item?.data_path);
  const baseName = pathSource.split(/[\\/]/).pop() || "";
  return baseName.replace(/\.(csv|h5ad)$/i, "") || "--";
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
  const parts = path.split(/[;\n,]+/).map((item) => trimText(item)).filter(Boolean);
  if (parts.length > 1) {
    return parts.map((item) => shortPath(item)).join(" + ");
  }
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
  if (!seed) return "#7dd3fc";
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) % 360;
  }
  return `hsl(${hash}, 82%, 66%)`;
}

function buildBaseItemStyle(point) {
  const mode = state.umapColorMode || "default";
  if (mode === "cell_type") {
    return { color: paletteColor(metadataValue(point, "cell_type")), opacity: 0.78 };
  }
  if (mode === "disease") {
    return { color: paletteColor(metadataValue(point, "disease")), opacity: 0.76 };
  }
  return { color: "#7dd3fc", opacity: 0.82 };
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
  element.innerHTML = `<span class="status-message-content">${escapeHtml(message)}</span>`;
  element.classList.remove("d-none");
  element.hidden = false;
  if (autoHideMs > 0) {
    const timer = window.setTimeout(() => {
      element.innerHTML = "";
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
  syncAiAssistantMoveUI();
  if (state.aiAssistantOpen) {
    window.requestAnimationFrame(() => {
      ensureAiAssistantPanelPosition();
      syncAiAssistantComposerState();
    });
  }
}

function syncAiAssistantMoveUI() {
  if (aiAssistantPanel) {
    aiAssistantPanel.classList.toggle("is-move-enabled", Boolean(state.aiAssistantMoveEnabled));
    aiAssistantPanel.classList.toggle("is-fullscreen", Boolean(state.aiAssistantFullscreen));
    aiAssistantPanel.classList.toggle("is-conversation-expanded", Boolean(state.aiAssistantConversationExpanded));
  }
  if (aiAssistantMoveToggle) {
    aiAssistantMoveToggle.classList.toggle("is-active", Boolean(state.aiAssistantMoveEnabled));
    aiAssistantMoveToggle.setAttribute(
      "aria-label",
      state.aiAssistantMoveEnabled ? "关闭移动模式" : "开启移动模式"
    );
    aiAssistantMoveToggle.title = state.aiAssistantMoveEnabled ? "移动模式已开启，拖动顶部即可挪动" : "点击开启移动模式";
  }
  if (aiAssistantFullscreenToggle) {
    aiAssistantFullscreenToggle.classList.toggle("is-active", Boolean(state.aiAssistantFullscreen));
    aiAssistantFullscreenToggle.setAttribute(
      "aria-label",
      state.aiAssistantFullscreen ? "恢复默认大小" : "切换全屏"
    );
    aiAssistantFullscreenToggle.title = state.aiAssistantFullscreen ? "点击恢复默认大小" : "点击全屏显示";
    aiAssistantFullscreenToggle.textContent = state.aiAssistantFullscreen ? "❐" : "⛶";
  }
  if (aiAssistantConversationToggle) {
    aiAssistantConversationToggle.textContent = state.aiAssistantConversationExpanded ? "收起对话区" : "展开对话区";
    aiAssistantConversationToggle.setAttribute(
      "aria-label",
      state.aiAssistantConversationExpanded ? "收起对话区" : "展开对话区"
    );
    aiAssistantConversationToggle.title = state.aiAssistantConversationExpanded
      ? "恢复完整助手布局"
      : "让对话区占用更多空间";
  }
}

function currentAiAssistantMode() {
  const value = trimText(state.aiAssistantMode || "cell_query");
  return AI_ASSISTANT_MODE_CONFIG[value] ? value : "cell_query";
}

function currentAiAssistantConfig() {
  return AI_ASSISTANT_MODE_CONFIG[currentAiAssistantMode()] || AI_ASSISTANT_MODE_CONFIG.cell_query;
}

function saveAiAssistantPosition(position) {
  if (!position) return;
  localStorage.setItem(AI_ASSISTANT_POSITION_STORAGE_KEY, JSON.stringify(position));
}

function clampAiAssistantPosition(left = 0, top = 0) {
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
  const padding = viewportWidth <= 768 ? 8 : 16;
  const width = aiAssistantPanel?.offsetWidth || 560;
  const height = aiAssistantPanel?.offsetHeight || 760;
  const maxLeft = Math.max(padding, viewportWidth - width - padding);
  const maxTop = Math.max(padding, viewportHeight - height - padding);
  return {
    left: Math.min(Math.max(left, padding), maxLeft),
    top: Math.min(Math.max(top, padding), maxTop),
  };
}

function getDefaultAiAssistantPosition() {
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
  const width = aiAssistantPanel?.offsetWidth || 560;
  const height = aiAssistantPanel?.offsetHeight || 760;
  return clampAiAssistantPosition(viewportWidth - width - 16, viewportHeight - height - 16);
}

function applyAiAssistantPanelPosition(position, { persist = true } = {}) {
  if (!aiAssistantPanel) return;
  const next = clampAiAssistantPosition(position?.left || 0, position?.top || 0);
  aiAssistantPanel.style.left = `${next.left}px`;
  aiAssistantPanel.style.top = `${next.top}px`;
  state.aiAssistantPosition = next;
  if (persist) {
    saveAiAssistantPosition(next);
  }
}

function ensureAiAssistantPanelPosition({ forceDefault = false } = {}) {
  if (state.aiAssistantFullscreen) {
    applyAiAssistantPanelPosition({ left: 12, top: 12 }, { persist: false });
    return;
  }
  const next = forceDefault || !state.aiAssistantPosition ? getDefaultAiAssistantPosition() : state.aiAssistantPosition;
  applyAiAssistantPanelPosition(next, { persist: true });
}

function getAiSuggestionOffset(mode) {
  return Number(state.aiAssistantSuggestionOffsets?.[mode] || 0);
}

function rotateAiAssistantSuggestions() {
  const mode = currentAiAssistantMode();
  const config = currentAiAssistantConfig();
  const total = Array.isArray(config.suggestions) ? config.suggestions.length : 0;
  if (!total) return;
  const nextOffset = (getAiSuggestionOffset(mode) + AI_ASSISTANT_VISIBLE_SUGGESTION_COUNT) % total;
  state.aiAssistantSuggestionOffsets[mode] = nextOffset;
  renderAiAssistantSuggestions();
}

function currentAiAssistantSuggestions() {
  const config = currentAiAssistantConfig();
  const suggestions = Array.isArray(config.suggestions) ? config.suggestions : [];
  if (suggestions.length <= AI_ASSISTANT_VISIBLE_SUGGESTION_COUNT) {
    return suggestions;
  }
  const offset = getAiSuggestionOffset(currentAiAssistantMode());
  return Array.from({ length: AI_ASSISTANT_VISIBLE_SUGGESTION_COUNT }, (_, index) => {
    return suggestions[(offset + index) % suggestions.length];
  });
}

function renderAiAssistantModeCards() {
  if (!aiAssistantModeCards) return;
  const activeMode = currentAiAssistantMode();
  aiAssistantModeCards.innerHTML = AI_ASSISTANT_MODE_ORDER.map((modeKey) => {
    const config = AI_ASSISTANT_MODE_CONFIG[modeKey];
    if (!config) return "";
    return `
      <button
        type="button"
        class="ai-assistant-mode-card ${modeKey === activeMode ? "is-active" : ""}"
        data-ai-mode="${escapeHtml(modeKey)}"
      >
        <span class="ai-assistant-mode-card-title">${escapeHtml(config.label)}</span>
        <span class="ai-assistant-mode-card-desc">${escapeHtml(config.heroDescription || config.intro || "")}</span>
      </button>
    `;
  }).join("");
}

function renderAiAssistantSuggestions() {
  if (!aiAssistantSuggestionsList) return;
  const suggestions = currentAiAssistantSuggestions();
  aiAssistantSuggestionsList.innerHTML = suggestions
    .map(
      (item) => `
        <button
          type="button"
          class="ai-assistant-suggestion-btn"
          data-ai-suggested-question="${escapeHtml(String(item || ""))}"
        >
          <span>${escapeHtml(String(item || ""))}</span>
        </button>
      `
    )
    .join("");
}

function syncAiAssistantComposerState() {
  const hasInput = Boolean(trimText(aiAssistantInput?.value || ""));
  if (aiAssistantSendBtn) {
    aiAssistantSendBtn.disabled = state.aiAssistantBusy || !hasInput;
  }
  if (aiAssistantRegenerateBtn) {
    aiAssistantRegenerateBtn.disabled = state.aiAssistantBusy || !trimText(state.aiAssistantLastQuestion);
  }
  if (aiAssistantRefreshSuggestions) {
    aiAssistantRefreshSuggestions.disabled = state.aiAssistantBusy;
  }
}

function fillAiAssistantInput(question = "") {
  if (!aiAssistantInput) return;
  aiAssistantInput.value = String(question || "");
  aiAssistantInput.focus();
  syncAiAssistantComposerState();
}

async function copyAiAssistantText(text = "") {
  const normalized = String(text || "");
  if (!normalized) return;
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(normalized);
    return;
  }
  const temp = document.createElement("textarea");
  temp.value = normalized;
  temp.setAttribute("readonly", "readonly");
  temp.style.position = "fixed";
  temp.style.opacity = "0";
  document.body.appendChild(temp);
  temp.select();
  document.execCommand("copy");
  document.body.removeChild(temp);
}

function humanizeAiRetrievalSource(value) {
  const normalized = trimText(value).toLowerCase();
  if (normalized === "existing_query_results") return "当前检索结果";
  if (normalized === "active_index") return "激活索引";
  if (normalized === "dataset_preview") return "数据集预览";
  if (normalized === "none") return "仅知识库";
  return value || "混合检索";
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
    const config = currentAiAssistantConfig();
    aiAssistantMessages.innerHTML = `
      <div class="ai-assistant-placeholder">
        这里会显示你和 AI 的对话内容。当前模式：${escapeHtml(config.label)}。
      </div>
    `;
    return;
  }

  aiAssistantMessages.innerHTML = state.aiAssistantMessages
    .map((message, index) => {
      const roleClass = message.role === "user" ? "is-user" : "is-assistant";
      const roleLabel = message.role === "user" ? "你" : "AI";
      const meta = trimText(message.meta || "");
      const linkedQuestion = trimText(message.linkedQuestion || findAiAssistantLinkedQuestion(index));
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
            ${message.role === "assistant" ? renderAiAssistantArtifacts(message.artifacts || null) : ""}
            <div class="ai-assistant-message-actions">
              <button type="button" class="ai-assistant-message-action" data-ai-copy-message-index="${index}">复制</button>
              ${
                message.role === "user"
                  ? `
                    <button type="button" class="ai-assistant-message-action" data-ai-edit-message-index="${index}">编辑</button>
                    <button type="button" class="ai-assistant-message-action" data-ai-resend-message-index="${index}">重新提问</button>
                  `
                  : linkedQuestion
                    ? `<button type="button" class="ai-assistant-message-action" data-ai-regenerate-message-index="${index}">重新生成</button>`
                    : ""
              }
            </div>
          </div>
        </article>
      `;
    })
    .join("");
  scrollAiAssistantMessagesToBottom();
}

function findAiAssistantLinkedQuestion(messageIndex) {
  for (let index = Number(messageIndex); index >= 0; index -= 1) {
    const item = state.aiAssistantMessages[index];
    if (item?.role === "user" && trimText(item.content)) {
      return trimText(item.content);
    }
  }
  return "";
}

function renderAiAssistantArtifacts(artifacts = null) {
  if (!artifacts || typeof artifacts !== "object") return "";

  const sections = [];
  const chips = [];
  if (artifacts.modeLabel) chips.push(`<span class="ai-artifact-chip">${escapeHtml(artifacts.modeLabel)}</span>`);
  if (artifacts.retrievalSource) {
    chips.push(
      `<span class="ai-artifact-chip">${escapeHtml(humanizeAiRetrievalSource(artifacts.retrievalSource))}</span>`
    );
  }
  if (artifacts.model && artifacts.model !== "rule-based-fallback") {
    chips.push(`<span class="ai-artifact-chip">${escapeHtml(artifacts.model)}</span>`);
  }
  const knowledgeHitCount = Array.isArray(artifacts.knowledgeHits) ? artifacts.knowledgeHits.length : 0;
  chips.push(
    `<span class="ai-artifact-chip">${escapeHtml(knowledgeHitCount ? `RAG 知识命中 ${knowledgeHitCount}` : "RAG 知识未命中")}</span>`
  );
  if (chips.length) {
    sections.push(`<div class="ai-assistant-artifact-chips">${chips.join("")}</div>`);
  }

  const shouldSearchKnowledge = Boolean(artifacts.intent?.should_search_knowledge);
  const knowledgeHints = artifacts.knowledgeHintsPayload || {};
  const hintEntries = Object.entries(knowledgeHints).filter(([, value]) =>
    Array.isArray(value) ? value.length : Boolean(value)
  );
  sections.push(`
    <section class="ai-assistant-artifact-section">
      <div class="ai-assistant-artifact-title">RAG 检索状态</div>
      <ul class="ai-assistant-artifact-ul">
        <li>
          <strong>should_search_knowledge</strong>
          <span>${escapeHtml(String(shouldSearchKnowledge))}</span>
        </li>
        <li>
          <strong>knowledge_hits</strong>
          <span>${escapeHtml(String(knowledgeHitCount))} 条</span>
        </li>
        <li>
          <strong>retrieval_source</strong>
          <span>${escapeHtml(artifacts.retrievalSource || "未返回")}</span>
        </li>
        ${
          hintEntries.length
            ? `<li>
                <strong>knowledge_hints</strong>
                <span>${escapeHtml(
                  hintEntries
                    .slice(0, 4)
                    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.slice(0, 6).join(", ") : value}`)
                    .join(" | ")
                )}</span>
              </li>`
            : ""
        }
      </ul>
    </section>
  `);

  const filters = Object.entries(artifacts.appliedFilters || {});
  if (filters.length) {
    sections.push(`
      <section class="ai-assistant-artifact-section">
        <div class="ai-assistant-artifact-title">解析出的筛选条件</div>
        <div class="ai-assistant-artifact-tags">
          ${filters
            .map(
              ([key, value]) => `
                <button
                  type="button"
                  class="ai-artifact-tag-btn"
                  data-ai-filter-key="${escapeHtml(key)}"
                  data-ai-filter-value="${escapeHtml(String(value ?? ""))}"
                >${escapeHtml(`${key}: ${value}`)}</button>
              `
            )
            .join("")}
        </div>
      </section>
    `);
  }

  const cellSummary = artifacts.cellSummary || {};
  const topCellTypes = Array.isArray(cellSummary.top_cell_types) ? cellSummary.top_cell_types : [];
  if (topCellTypes.length) {
    sections.push(`
      <section class="ai-assistant-artifact-section">
        <div class="ai-assistant-artifact-title">命中细胞摘要</div>
        <p class="ai-assistant-artifact-text">共命中 ${escapeHtml(String(cellSummary.hit_count || 0))} 个候选细胞。</p>
        <div class="ai-assistant-artifact-tags">
          ${topCellTypes
            .map(
              (item) => `
                <button
                  type="button"
                  class="ai-artifact-tag-btn"
                  data-ai-filter-key="cell_type"
                  data-ai-filter-value="${escapeHtml(String(item.name ?? ""))}"
                >${escapeHtml(`${item.name} (${item.count})`)}</button>
              `
            )
            .join("")}
        </div>
      </section>
    `);
  }

  const cellHits = Array.isArray(artifacts.cellHits) ? artifacts.cellHits.slice(0, 4) : [];
  if (cellHits.length) {
    sections.push(`
      <section class="ai-assistant-artifact-section">
        <div class="ai-assistant-artifact-title">候选细胞证据</div>
        <div class="ai-assistant-artifact-list">
          ${cellHits
            .map((item) => {
              const metadata = item.metadata || {};
              const subtitle = [
                metadata.cell_type || "未标注类型",
                metadata.disease || null,
                metadata.tissue || null,
              ]
                .filter(Boolean)
                .join(" · ");
              const reasonText = Array.isArray(item.reason_signals) ? item.reason_signals.slice(0, 2).join(" ") : "";
              return `
                <button
                  type="button"
                  class="ai-artifact-result-btn"
                  data-ai-focus-cell-id="${escapeHtml(String(item.cell_id ?? ""))}"
                >
                  <strong>${escapeHtml(String(item.cell_id ?? ""))}</strong>
                  <span>${escapeHtml(subtitle || "点击联动到结果表与 UMAP")}</span>
                  ${reasonText ? `<em>${escapeHtml(reasonText)}</em>` : ""}
                </button>
              `;
            })
            .join("")}
        </div>
      </section>
    `);
  }

  const knowledgeHits = Array.isArray(artifacts.knowledgeHits) ? artifacts.knowledgeHits.slice(0, 3) : [];
  if (knowledgeHits.length) {
    sections.push(`
      <section class="ai-assistant-artifact-section">
        <div class="ai-assistant-artifact-title">知识库证据</div>
        <ul class="ai-assistant-artifact-ul">
          ${knowledgeHits
            .map(
              (item) => `
                <li>
                  <strong>${escapeHtml(String(item.title ?? ""))}</strong>
                  <span>${escapeHtml(trimText(item.content || "").slice(0, 110))}</span>
                </li>
              `
            )
            .join("")}
        </ul>
      </section>
    `);
  }

  if (knowledgeHits.length) {
    sections.push(`
      <section class="ai-assistant-artifact-section">
        <div class="ai-assistant-artifact-title">RAG 命中详情</div>
        <ul class="ai-assistant-artifact-ul">
          ${knowledgeHits
            .map((item) => {
              const markerGenes = Array.isArray(item.marker_genes) ? item.marker_genes.slice(0, 8).join(", ") : "";
              const meta = [
                item.source ? `source=${item.source}` : "",
                item.retrieval_method ? `method=${item.retrieval_method}` : "",
                item.score !== undefined ? `score=${item.score}` : "",
              ]
                .filter(Boolean)
                .join(" · ");
              return `
                <li>
                  <strong>${escapeHtml(String(item.title ?? ""))}</strong>
                  <span>${escapeHtml(meta || "未返回来源信息")}</span>
                  ${markerGenes ? `<span>marker_genes: ${escapeHtml(markerGenes)}</span>` : ""}
                  <span>${escapeHtml(trimText(item.summary || item.content || "").slice(0, 140))}</span>
                </li>
              `;
            })
            .join("")}
        </ul>
      </section>
    `);
  }

  const nextSteps = Array.isArray(artifacts.nextSteps) ? artifacts.nextSteps.slice(0, 4) : [];
  if (nextSteps.length) {
    sections.push(`
      <section class="ai-assistant-artifact-section">
        <div class="ai-assistant-artifact-title">下一步分析建议</div>
        <ol class="ai-assistant-artifact-ol">
          ${nextSteps.map((item) => `<li>${escapeHtml(String(item ?? ""))}</li>`).join("")}
        </ol>
      </section>
    `);
  }

  return sections.length ? `<div class="ai-assistant-artifacts">${sections.join("")}</div>` : "";
}

function resetAiAssistantConversation() {
  const config = currentAiAssistantConfig();
  state.aiAssistantMessages = [
    {
      role: "assistant",
      content: config.intro,
      meta: "",
      skipHistory: true,
      artifacts: null,
      linkedQuestion: "",
    },
  ];
  renderAiAssistantMessages();
}

function appendAiAssistantMessage(role, content, { meta = "", skipHistory = false, artifacts = null, linkedQuestion = "" } = {}) {
  state.aiAssistantMessages.push({
    role,
    content: String(content || ""),
    meta: String(meta || ""),
    skipHistory: Boolean(skipHistory),
    artifacts,
    linkedQuestion: String(linkedQuestion || ""),
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

function compactCurrentResultsForAi(limit = 12) {
  return (Array.isArray(state.currentResults) ? state.currentResults : []).slice(0, limit).map((item) => {
    const point = findPointByCellId(item.cell_id) || {};
    return {
      cell_id: item.cell_id,
      score: item.score,
      similarity: item.score,
      distance: item.distance,
      metadata: item.metadata || {},
      viz: item.viz || {
        x: point.x,
        y: point.y,
      },
    };
  });
}

function syncAiAssistantModeUI({ resetConversation = false } = {}) {
  const mode = currentAiAssistantMode();
  const config = currentAiAssistantConfig();
  state.aiAssistantMode = mode;
  if (!Number.isFinite(getAiSuggestionOffset(mode))) {
    state.aiAssistantSuggestionOffsets[mode] = 0;
  }
  if (aiAssistantHeroEyebrow) {
    aiAssistantHeroEyebrow.textContent = config.heroEyebrow || "Hi~";
  }
  if (aiAssistantHeroTitle) {
    aiAssistantHeroTitle.textContent = config.heroTitle || config.label;
  }
  if (aiAssistantHeroDescription) {
    aiAssistantHeroDescription.textContent = config.heroDescription || config.intro;
  }
  if (aiAssistantInput) {
    aiAssistantInput.placeholder = config.placeholder;
  }
  renderAiAssistantModeCards();
  renderAiAssistantSuggestions();
  setMessage(aiAssistantStatus, config.idleStatus, "neutral");
  if (resetConversation) {
    resetAiAssistantConversation();
  }
  syncAiAssistantComposerState();
}

function buildAiAssistantArtifacts(response = {}) {
  return {
    modeLabel: currentAiAssistantConfig().label,
    model: response.model || "",
    retrievalSource: response.retrieval_source || "",
    appliedFilters: response.applied_filters || {},
    intent: response.intent || {},
    cellSummary: response.cell_summary || {},
    cellHits: response.cell_hits || [],
    knowledgeHits: response.knowledge_hits || [],
    knowledgeHintsPayload: response.knowledge_hints || {},
    nextSteps: response.next_steps || [],
  };
}

function applyAiAssistantFilters(filters = {}) {
  let changed = false;
  Object.entries(filters || {}).forEach(([key, value]) => {
    const targetField = METADATA_FILTER_FIELDS.find((field) => field.key === key);
    const selectElement = targetField?.element;
    if (!selectElement || value === undefined || value === null || value === "") return;
    const targetValue = String(value);
    const optionExists = Array.from(selectElement.options || []).some((option) => option.value === targetValue);
    if (!optionExists) return;
    if (selectElement.value !== targetValue) {
      selectElement.value = targetValue;
      changed = true;
    }
  });
  if (changed) {
    refreshUmapByControls();
  }
  return changed;
}

async function syncAiCellAnalysisResponse(response = {}) {
  const aiResults = Array.isArray(response.cell_hits) ? response.cell_hits : [];
  if (!aiResults.length) return;
  const normalizedResults = aiResults.map((item) => ({
    cell_id: item.cell_id,
    distance: item.distance,
    score: item.score,
    metadata: item.metadata || {},
    viz: item.umap || {},
    reason_signals: item.reason_signals || [],
    selected: Boolean(item.selected),
  }));
  await renderResults(normalizedResults);
  applyAiAssistantFilters(response.applied_filters || {});
  const highlightCount = applyUmapHighlights(normalizedResults, "AI query", response.query_context?.selected_cell_id || "");
  const focusCellId =
    normalizedResults.find((item) => item.selected)?.cell_id ||
    response.query_context?.selected_cell_id ||
    normalizedResults[0]?.cell_id ||
    "";
  if (focusCellId) {
    selectCell(focusCellId, { syncRow: true });
  }
  setQueryMetrics({
    mode: "AI 自然语言分析",
    resultCount: normalizedResults.length,
    queryTime: null,
    highlightCount,
  });
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
  const mode = currentAiAssistantMode();
  const endpoint = currentAiAssistantConfig().endpoint || "/api/ai/cell-query";
  const selectedCellId =
    trimText(state.umapFocusedCellId) ||
    trimText(state.umapQueryCenter?.cell_id) ||
    trimText(cellIdInput?.value);
  const conversationHistory = serializeAiAssistantConversationHistory();

  setAiAssistantPanelOpen(true);
  appendAiAssistantMessage("user", question);
  state.aiAssistantLastQuestion = question;
  state.aiAssistantBusy = true;
  setMessage(aiAssistantStatus, "AI 正在思考并组织回答...", "neutral");
  syncAiAssistantComposerState();

  try {
    const response = await requestJson(endpoint, {
      method: "POST",
      body: JSON.stringify({
        data_path: dataPath,
        dataset_info: compactDatasetInfoForAi(),
        current_build_options: currentIndexBuildOptions(),
        user_question: question,
        mode_hint: mode,
        conversation_history: conversationHistory,
        index_id: state.activeIndex?.id || null,
        current_results: compactCurrentResultsForAi(),
        selected_cell_id: selectedCellId,
        query_context: {
          selected_cell_id: selectedCellId,
          query_mode: trimText(queryModeMetric?.textContent),
        },
      }),
      timeoutMs: 60000,
    });
    if (mode === "cell_query") {
      await syncAiCellAnalysisResponse(response);
    }
    appendAiAssistantMessage("assistant", response.answer || "", {
      meta: aiAssistantDatasetSummaryLine(response.dataset_summary || null),
      artifacts: buildAiAssistantArtifacts(response),
      linkedQuestion: question,
    });
    setMessage(
      aiAssistantStatus,
      `AI 已回复（${response.model || "LLM"}，${currentAiAssistantConfig().label}）`,
      "success"
    );
    if (aiAssistantInput) aiAssistantInput.value = "";
    syncAiAssistantComposerState();
    return response;
  } catch (error) {
    setMessage(aiAssistantStatus, error.message, "error");
    throw error;
  } finally {
    state.aiAssistantBusy = false;
    syncAiAssistantComposerState();
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

function setBenchmarkVisible(visible) {
  if (!annBenchmarkPanel) return;
  annBenchmarkPanel.hidden = !visible;
  annBenchmarkPanel.classList.toggle("d-none", !visible);
}

function clearAnnBenchmark() {
  if (annBenchmarkDelta) annBenchmarkDelta.textContent = "等待评估";
  if (annBeforeTime) annBeforeTime.textContent = "--";
  if (annBeforePrecision) annBeforePrecision.textContent = "--";
  if (annBeforeRecall) annBeforeRecall.textContent = "--";
  if (annBeforeOverlap) annBeforeOverlap.textContent = "--";
  if (annAfterTime) annAfterTime.textContent = "--";
  if (annAfterPrecision) annAfterPrecision.textContent = "--";
  if (annAfterRecall) annAfterRecall.textContent = "--";
  if (annAfterOverlap) annAfterOverlap.textContent = "--";
  if (annExactTime) annExactTime.textContent = "--";
  if (annExactPrecision) annExactPrecision.textContent = "--";
  if (annExactRecall) annExactRecall.textContent = "--";
  if (annAfterIndexSize) annAfterIndexSize.textContent = "--";
  if (annAfterRss) annAfterRss.textContent = "--";
  if (annExactIndexSize) annExactIndexSize.textContent = "--";
  if (annExactRss) annExactRss.textContent = "--";
}

function formatMegabytes(value) {
  if (value === null || value === undefined || value === "") return "--";
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return "--";
  return `${formatMetric(numericValue)} MB`;
}

function formatMemoryUsage(mbValue, percentValue) {
  const mbText = formatMegabytes(mbValue);
  if (mbText === "--") return "--";
  if (percentValue === null || percentValue === undefined || percentValue === "") return mbText;
  const numericPercent = Number(percentValue);
  if (!Number.isFinite(numericPercent)) return mbText;
  return `${mbText} (${formatMetric(numericPercent)}%)`;
}

function renderAnnBenchmark(benchmark = null) {
  if (!benchmark) {
    clearAnnBenchmark();
    setBenchmarkVisible(false);
    return;
  }
  const before = benchmark.before || {};
  const after = benchmark.after || {};
  const exact = benchmark.exact || {};
  const delta = benchmark.delta || {};
  const isFallback = Boolean(benchmark.params && benchmark.params.fallback);
  const formatOverlap = (value) => (value === null || value === undefined ? "--" : `${formatNumber(value)} / ${formatNumber(benchmark.top_k)}`);

  setBenchmarkVisible(true);
  if (annBeforeTime) annBeforeTime.textContent = formatTime(before.query_time_ms);
  if (annBeforePrecision) annBeforePrecision.textContent = formatRate(before.precision_at_k);
  if (annBeforeRecall) annBeforeRecall.textContent = formatRate(before.recall_at_k);
  if (annBeforeOverlap) annBeforeOverlap.textContent = formatOverlap(before.overlap_count);
  if (annAfterTime) annAfterTime.textContent = formatTime(after.query_time_ms);
  if (annAfterPrecision) annAfterPrecision.textContent = formatRate(after.precision_at_k);
  if (annAfterRecall) annAfterRecall.textContent = formatRate(after.recall_at_k);
  if (annAfterOverlap) annAfterOverlap.textContent = formatOverlap(after.overlap_count);
  if (annExactTime) annExactTime.textContent = formatTime(exact.query_time_ms);
  if (annExactPrecision) annExactPrecision.textContent = formatRate(exact.precision_at_k);
  if (annExactRecall) annExactRecall.textContent = formatRate(exact.recall_at_k);
  if (annAfterIndexSize) annAfterIndexSize.textContent = formatMegabytes(after.persistent_index_size_mb);
  if (annAfterRss) annAfterRss.textContent = formatMemoryUsage(after.faiss_service_rss_mb, after.faiss_service_rss_percent);
  if (annExactIndexSize) annExactIndexSize.textContent = formatMegabytes(exact.persistent_index_size_mb);
  if (annExactRss) annExactRss.textContent = formatMemoryUsage(exact.faiss_service_rss_mb, exact.faiss_service_rss_percent);

  if (annBenchmarkDelta) {
    if (isFallback) {
      annBenchmarkDelta.textContent = "";
      return;
    }
    const timeDelta = Number(delta.query_time_ms || 0);
    const precisionDelta = Number(delta.precision_at_k || 0);
    const recallDelta = Number(delta.recall_at_k || 0);
    const timeText = timeDelta > 0 ? `快 ${formatTime(timeDelta)}` : timeDelta < 0 ? `慢 ${formatTime(Math.abs(timeDelta))}` : "耗时持平";
    annBenchmarkDelta.textContent = `${timeText} / P@K ${precisionDelta >= 0 ? "+" : ""}${formatRate(precisionDelta, true)} / R@K ${recallDelta >= 0 ? "+" : ""}${formatRate(recallDelta, true)}`;
  }
}

function setEvaluationIdleMessage(enabled) {
  if (!evaluationSummary) return;
  if (enabled) {
    clearAnnBenchmark();
    setBenchmarkVisible(true);
    setMessage(
      evaluationSummary,
      "Exact evaluation enabled. Query will run before/after ANN + exact baseline.",
      "neutral"
    );
    return;
  }
  renderAnnBenchmark(null);
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
  clearAnnBenchmark();
  setBenchmarkVisible(true);
  setMessage(evaluationSummary, "Running before/after ANN + exact evaluation...", "neutral");
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

async function uploadDatasetFile(file) {
  if (!file) {
    throw new Error("请选择要上传的 CSV 或 h5ad 文件");
  }

  const formData = new FormData();
  formData.append("file", file);
  const headers = {};
  if (state.authToken) {
    headers.Authorization = `Bearer ${state.authToken}`;
  }

  const response = await fetch("/api/dataset/upload", {
    method: "POST",
    headers,
    body: formData,
  });
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
    throw new Error(data.error || `Upload failed (${response.status})`);
  }
  return data;
}

function downloadBlob(content, filename, contentType) {
  const blob = new Blob([content], { type: contentType });
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}

function safeExportName(pathValue) {
  const shortName = shortPath(pathValue).split("/").pop() || "dataset";
  const stem = shortName.replace(/\.[^.]+$/, "") || "dataset";
  return stem.replace(/[^A-Za-z0-9_.-]+/g, "_").replace(/^[_\-.]+|[_\-.]+$/g, "") || "dataset";
}

function exportTimestamp() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\..+$/, "").replace("T", "_");
}

function buildUmapExportRows(points) {
  return (points || []).map((point) => {
    const row = {
      cell_id: point.cell_id || "",
      umap_x: point.x,
      umap_y: point.y,
    };
    Object.entries(point.metadata || {}).forEach(([key, value]) => {
      row[`metadata_${key}`] = value;
    });
    return row;
  });
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  if (/[",\r\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function rowsToCsv(rows) {
  const baseColumns = ["cell_id", "umap_x", "umap_y"];
  const metadataColumns = Array.from(
    new Set(rows.flatMap((row) => Object.keys(row).filter((key) => key.startsWith("metadata_"))))
  ).sort();
  const columns = [...baseColumns, ...metadataColumns];
  return [
    columns.join(","),
    ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(",")),
  ].join("\r\n");
}

function showAuthView() {
  document.body.classList.add("auth-mode");
  authView.classList.remove("d-none");
  authView.hidden = false;
  hubView.classList.add("d-none");
  hubView.hidden = true;
  mainView.classList.add("d-none");
  mainView.hidden = true;
  setAiAssistantDockVisible(false);
}

function showHubView() {
  document.body.classList.remove("auth-mode");
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
  syncUmapCanvasResolution();
  Object.values(state.charts).forEach((chart) => {
    if (!chart) return;
    resizeChartToElement(chart, chart.getDom?.());
  });
}

function showMainView() {
  document.body.classList.remove("auth-mode");
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
  toggleAdminOnly(hubAdminManualLink, admin);
  toggleAdminOnly(mainAdminManualLink, admin);
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
    original_vector_dim: raw.original_vector_dim ?? null,
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
    ["Original Dim", formatNumber(info.original_vector_dim)],
    ["Vector Dim", formatNumber(info.vector_dim)],
    ["Embedding", info.embedding_key || "-"],
    ["Viz Source", info.visualization_source || "-"],
  ];
  datasetInfo.innerHTML = fields
    .map(
      ([label, value]) =>
        `<div class="dataset-info-item"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`
    )
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
        fill: "#64748b",
        fontSize: 13,
      },
    },
  };
}

function getOrCreateChart(key, element) {
  if (!window.echarts || !element) return null;
  if (!state.charts[key]) {
    state.charts[key] = window.echarts.init(element, null, buildChartInitOptions());
  }
  resizeChartToElement(state.charts[key], element);
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
  if (!state.umapPoints.length) {
    return state.analyticsGlobal;
  }
  if (!usingLocalScope) {
    return state.analyticsGlobal || buildScopeAnalytics(state.umapPoints);
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
  if (!cellId || (!point && !result)) {
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
  const metadata = point?.metadata || result?.metadata || {};
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
  ];
  if (point) {
    entries.push(["UMAP X", formatMetric(point.x)]);
    entries.push(["UMAP Y", formatMetric(point.y)]);
  }
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
          itemStyle: { borderWidth: 2, borderColor: "#ffffff" },
          label: { color: "#111827", formatter: "{b}" },
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
      legend: { top: 0, textStyle: { color: "#374151" } },
      grid: { left: 52, right: 20, top: 34, bottom: 50 },
      xAxis: {
        type: "category",
        axisLabel: { color: "#475569", rotate: 18 },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.35)" } },
        data: rows.map((item) => item.name),
      },
      yAxis: [
        {
          type: "value",
          name: "基因数",
          nameTextStyle: { color: "#475569" },
          axisLabel: { color: "#475569" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.14)" } },
        },
        {
          type: "value",
          name: "线粒体%",
          nameTextStyle: { color: "#475569" },
          axisLabel: { color: "#475569" },
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

function compactChartLabel(value, maxLength = 12) {
  const text = String(value || "-");
  if (text.length <= maxLength) return text;
  const edgeLength = Math.max(3, Math.floor((maxLength - 1) / 2));
  return `${text.slice(0, edgeLength)}…${text.slice(-edgeLength)}`;
}

function renderSampleCharts(analytics) {
  const stackChart = getOrCreateChart("sampleStack", sampleStackChartElement);
  const similarityChart = getOrCreateChart("sampleSimilarity", sampleSimilarityChartElement);
  const sampleDistribution = analytics?.sample_distribution || {};
  const allSamples = sampleDistribution.samples || [];
  const allSeries = sampleDistribution.series || [];
  const similarity = sampleDistribution.similarity || { labels: [], matrix: [] };
  if (!stackChart || !similarityChart) return;
  if (!allSamples.length || !allSeries.length) {
    stackChart.setOption(noDataOption("暂无样本来源统计"), true);
    similarityChart.setOption(noDataOption("暂无样本相似矩阵"), true);
    return;
  }

  const sampleLimit = 8;
  const seriesLimit = 6;
  const samples = allSamples.slice(0, sampleLimit);
  const visibleSeries = allSeries.slice(0, seriesLimit).map((item) => ({
    ...item,
    data: (item.data || []).slice(0, sampleLimit),
  }));
  const similarityLabels = (similarity.labels || []).slice(0, sampleLimit);
  const similarityMatrix = (similarity.matrix || []).filter(
    (item) => Number(item?.[0]) < sampleLimit && Number(item?.[1]) < sampleLimit
  );

  stackChart.setOption(
    {
      animationDuration: 220,
      color: ["#5b7bd5", "#8acb72", "#ffc857", "#ef6461", "#67b7d1", "#43aa7b"],
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        confine: true,
      },
      legend: {
        type: "scroll",
        top: 8,
        left: 12,
        right: 12,
        itemWidth: 16,
        itemHeight: 10,
        textStyle: { color: "#374151", fontSize: 11 },
        pageTextStyle: { color: "#64748b" },
      },
      grid: { left: 48, right: 16, top: 74, bottom: 76, containLabel: false },
      xAxis: {
        type: "category",
        data: samples,
        axisLabel: {
          color: "#475569",
          rotate: 28,
          interval: 0,
          fontSize: 10,
          formatter: (value) => compactChartLabel(value, 11),
        },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.35)" } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#475569", fontSize: 10 },
        splitLine: { lineStyle: { color: "rgba(148,163,184,0.14)" } },
      },
      series: visibleSeries.map((item) => ({
        ...item,
        type: "bar",
        stack: "total",
        barMaxWidth: 30,
        emphasis: { focus: "series" },
      })),
    },
    true
  );

  similarityChart.setOption(
    {
      animationDuration: 220,
      tooltip: {
        confine: true,
        formatter(params) {
          const [row, col, score] = params.data || [];
          return `${escapeHtml(similarityLabels[row] || "-")} vs ${escapeHtml(similarityLabels[col] || "-")}<br>相似度: ${escapeHtml(formatMetric(score))}`;
        },
      },
      grid: { left: 82, right: 14, top: 18, bottom: 72 },
      xAxis: {
        type: "category",
        data: similarityLabels,
        axisLabel: {
          color: "#475569",
          rotate: 28,
          interval: 0,
          fontSize: 10,
          formatter: (value) => compactChartLabel(value, 9),
        },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.35)" } },
      },
      yAxis: {
        type: "category",
        data: similarityLabels,
        axisLabel: {
          color: "#475569",
          fontSize: 10,
          formatter: (value) => compactChartLabel(value, 9),
        },
        axisLine: { lineStyle: { color: "rgba(148,163,184,0.35)" } },
      },
      visualMap: {
        min: 0,
        max: 1,
        calculable: false,
        orient: "horizontal",
        left: "center",
        bottom: 8,
        itemWidth: 12,
        itemHeight: 150,
        text: ["高", "低"],
        textGap: 8,
        textStyle: { color: "#475569", fontSize: 10 },
      },
      series: [
        {
          type: "heatmap",
          data: similarityMatrix,
          label: { show: false },
          emphasis: { itemStyle: { borderColor: "#ffffff", borderWidth: 1 } },
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
    applyChartFocus("sample_id", similarityLabels[row] || "");
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
          axisLabel: { color: "#475569", showMinLabel: true, showMaxLabel: true },
          axisLine: { lineStyle: { color: "rgba(148,163,184,0.35)" } },
        },
        yAxis: {
          type: "value",
          axisLabel: { color: "#475569" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.14)" } },
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
          axisLabel: { color: "#475569", rotate: 16 },
          axisLine: { lineStyle: { color: "rgba(148,163,184,0.35)" } },
        },
        yAxis: {
          type: "value",
          axisLabel: { color: "#475569" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.14)" } },
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
    renderDatasetInfo(state.currentDatasetInfo || {});
    renderAnalyticsForCurrentState();
    return;
  }
  try {
    const analytics = await getJson(`/api/dataset/umap-stats?data_path=${encodeURIComponent(state.currentDataPath)}`);
    state.analyticsGlobal = analytics;
    renderDatasetInfo(state.currentDatasetInfo || {});
    renderAnalyticsForCurrentState();
  } catch (error) {
    state.analyticsGlobal = null;
    renderDatasetInfo(state.currentDatasetInfo || {});
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

async function focusResultRow(cellId) {
  if (!resultsBody) return false;
  if (!cellId) {
    resultsBody.querySelectorAll("tr[data-cell-id]").forEach((row) => row.classList.remove("is-active"));
    return false;
  }

  const resultIndex = state.currentResults.findIndex((item) => item.cell_id === cellId);
  if (resultIndex < 0) return false;

  const targetPage = Math.floor(resultIndex / RESULTS_PAGE_SIZE) + 1;
  if (targetPage !== state.currentResultsPage) {
    state.currentResultsPage = targetPage;
    await renderCurrentResultsPage();
  }

  let matchedRow = null;
  resultsBody.querySelectorAll("tr[data-cell-id]").forEach((row) => {
    const isActive = row.dataset.cellId === cellId;
    row.classList.toggle("is-active", isActive);
    if (isActive) matchedRow = row;
  });
  if (matchedRow) {
    matchedRow.scrollIntoView({ behavior: "smooth", block: "center" });
    return true;
  }
  return false;
}

function focusCellOnUmap(cellId) {
  selectCell(cellId || "", { syncRow: false });
}

function applyUmapBrushSelection(cellIds = []) {
  state.umapSelectionCellIds = Array.from(new Set(cellIds.filter(Boolean)));
  if (state.umapSelectionCellIds.length === 1) {
    state.umapFocusedCellId = state.umapSelectionCellIds[0];
    renderCellDetail(state.umapFocusedCellId);
  } else {
    state.umapFocusedCellId = "";
    renderCellDetail("");
  }
  renderUmapFromState();
  renderAnalyticsForCurrentState();
  setMessage(
    queryStatus,
    state.umapSelectionCellIds.length
      ? `已框选 ${state.umapSelectionCellIds.length} 个细胞，左侧已切换为选区统计。`
      : "框选已清除，左侧已恢复全局统计。",
    "neutral"
  );
}

function cellIdsFromBrushAreas(areas = []) {
  const selected = [];
  for (const area of areas) {
    const range = area?.coordRange;
    if (!Array.isArray(range) || !Array.isArray(range[0]) || !Array.isArray(range[1])) continue;
    const xMin = Math.min(Number(range[0][0]), Number(range[0][1]));
    const xMax = Math.max(Number(range[0][0]), Number(range[0][1]));
    const yMin = Math.min(Number(range[1][0]), Number(range[1][1]));
    const yMax = Math.max(Number(range[1][0]), Number(range[1][1]));
    if (![xMin, xMax, yMin, yMax].every(Number.isFinite)) continue;
    state.umapFilteredPoints.forEach((point) => {
      if (point.x >= xMin && point.x <= xMax && point.y >= yMin && point.y <= yMax) {
        selected.push(point.cell_id);
      }
    });
  }
  return selected;
}

function bindUmapChartEvents(chart) {
  if (!chart) return;
  chart.on("click", async (params) => {
    const cellId = params?.data?.cell_id;
    if (!cellId) return;
    selectCell(cellId, { syncRow: false });
    const located = await focusResultRow(cellId);
    if (!located && state.currentResults.length) {
      setMessage(queryStatus, "该细胞不在当前 Top-K 查询结果中，已在右侧显示细胞详情。", "neutral");
    }
  });
  chart.on("brushSelected", (params) => {
    const selectedCellIds = [];
    const batches = Array.isArray(params?.batch) ? params.batch : [];
    batches.forEach((batch) => {
      (batch.selected || []).forEach((item) => {
        if (item.seriesIndex !== 0) return;
        (item.dataIndex || []).forEach((index) => {
          const point = state.umapFilteredPoints[index];
          if (point?.cell_id) selectedCellIds.push(point.cell_id);
        });
      });
    });
    if (selectedCellIds.length) {
      applyUmapBrushSelection(selectedCellIds);
    }
  });
  chart.on("brushEnd", (params) => {
    const areas = Array.isArray(params?.areas) ? params.areas : [];
    applyUmapBrushSelection(cellIdsFromBrushAreas(areas));
  });
}

function recreateUmapChart(preserveView = true) {
  if (!window.echarts || !umapChartElement) return null;
  const viewportState = preserveView ? captureUmapViewportState() : null;
  if (state.umapChart) {
    state.umapChart.dispose();
    state.umapChart = null;
  }
  state.umapChart = window.echarts.init(umapChartElement, null, buildChartInitOptions());
  state.umapChartDpr = getCurrentDevicePixelRatio();
  bindUmapChartEvents(state.umapChart);
  resizeChartToElement(state.umapChart, umapChartElement);
  state.umapChart.setOption(
    buildUmapOption(
      state.umapBaseSeries || [],
      state.umapHighlights || [],
      state.umapQueryCenter,
      buildFocusedPoint(state.umapFocusedCellId)
    ),
    true
  );
  restoreUmapViewportState(state.umapChart, viewportState);
  return state.umapChart;
}

function ensureUmapResizeObserver() {
  if (state.umapResizeObserver || !window.ResizeObserver || !umapChartElement) return;
  state.umapResizeObserver = new window.ResizeObserver(() => {
    window.requestAnimationFrame(() => {
      syncUmapCanvasResolution();
    });
  });
  state.umapResizeObserver.observe(umapChartElement);
}

function syncUmapCanvasResolution() {
  if (!state.umapChart || !umapChartElement) return;
  resizeChartToElement(state.umapChart, umapChartElement);
  const dpr = getCurrentDevicePixelRatio();
  const dprChanged = Math.abs((state.umapChartDpr || dpr) - dpr) > 0.01;
  if (dprChanged || !canvasMatchesDevicePixelRatio(umapChartElement, dpr)) {
    recreateUmapChart(true);
  }
}

function setMessageWithAction(
  element,
  message,
  tone,
  actionLabel,
  onAction,
  classSuffix = "",
  autoHideMs = 0
) {
  setMessage(element, message, tone, classSuffix, autoHideMs);
  if (!element || !actionLabel || typeof onAction !== "function") return;
  const actionBtn = document.createElement("button");
  actionBtn.type = "button";
  actionBtn.className = "status-message-action";
  actionBtn.textContent = actionLabel;
  actionBtn.addEventListener("click", onAction);
  element.appendChild(actionBtn);
}

function refreshFileInputName(input, nameElement) {
  if (!input || !nameElement) return;
  const file = input.files?.[0] || null;
  const text = file?.name || "未选择文件";
  nameElement.textContent = text;
  const shell = nameElement.closest(".file-input-shell");
  if (shell) shell.classList.toggle("has-file", Boolean(file));
}

function bindFileInputName(input, nameElement) {
  if (!input || !nameElement) return;
  refreshFileInputName(input, nameElement);
  input.addEventListener("change", () => {
    refreshFileInputName(input, nameElement);
  });
}

bindFileInputName(hubDatasetFile, hubDatasetFileName);
bindFileInputName(datasetFileInput, datasetFileName);

function initUmapChartIfNeeded() {
  if (!window.echarts || !umapChartElement) return;
  if (!state.umapChart) {
    recreateUmapChart(false);
  }
  ensureUmapResizeObserver();
  if (!state.chartResizeBound) {
    window.addEventListener("resize", resizeAllCharts);
    state.chartResizeBound = true;
  }
  syncUmapCanvasResolution();
}

function buildUmapOption(baseData, highlightData, queryCenter, focusedPoint) {
  return {
    animation: false,
    animationThreshold: 2000,
    hoverLayerThreshold: 1000000,
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
        type: "scatter",
        progressive: 12000,
        progressiveThreshold: 30000,
        large: false,
        largeThreshold: 1000000,
        data: baseData,
        symbol: "circle",
        symbolSize(value) {
          return Math.max(value?.[2] ?? 3.2, 3.2);
        },
        blendMode: "source-over",
        itemStyle: {
          color: "#7dd3fc",
          opacity: 0.82,
        },
        emphasis: {
          scale: false,
          itemStyle: {
            opacity: 0.96,
          },
        },
        silent: false,
      },
      {
        name: "Hits",
        type: "scatter",
        data: highlightData,
        symbol: "circle",
        symbolSize(value) {
          return Math.max(7.5, 10.8 - Math.min((value?.[2] || 1) - 1, 7) * 0.65);
        },
        itemStyle: {
          color: "#ffffff",
          borderColor: "#ef4444",
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: "rgba(239,68,68,0.55)",
        },
        z: 20,
      },
      {
        name: "Query Center",
        type: "scatter",
        data: queryCenter ? [queryCenter] : [],
        symbol: "circle",
        symbolSize: 16,
        itemStyle: {
          color: "#fbbf24",
          borderColor: "#fff7cc",
          borderWidth: 2,
          shadowBlur: 12,
          shadowColor: "rgba(251,191,36,0.65)",
        },
        z: 30,
      },
      {
        name: "Focused Cell",
        type: "scatter",
        data: focusedPoint ? [focusedPoint] : [],
        symbol: "circle",
        symbolSize: 13,
        itemStyle: {
          color: "#fde68a",
          borderColor: "#ffffff",
          borderWidth: 2,
          shadowBlur: 12,
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
      value: [point.x, point.y, 3.2],
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

function setResultsPaginationVisible(visible) {
  if (!resultsPagination) return;
  resultsPagination.hidden = !visible;
  resultsPagination.classList.toggle("d-none", !visible);
}

function updateResultsPagination() {
  const totalResults = state.currentResults.length;
  const totalPages = Math.max(1, Math.ceil(totalResults / RESULTS_PAGE_SIZE));
  state.currentResultsPage = Math.min(Math.max(1, state.currentResultsPage), totalPages);
  setResultsPaginationVisible(totalResults > RESULTS_PAGE_SIZE);

  if (resultsPageSummary) {
    const start = totalResults ? (state.currentResultsPage - 1) * RESULTS_PAGE_SIZE + 1 : 0;
    const end = Math.min(state.currentResultsPage * RESULTS_PAGE_SIZE, totalResults);
    resultsPageSummary.textContent = `显示 ${start}-${end} 条，共 ${totalResults} 条`;
  }
  if (resultsPrevPage) resultsPrevPage.disabled = state.currentResultsPage <= 1;
  if (resultsNextPage) resultsNextPage.disabled = state.currentResultsPage >= totalPages;
  if (resultsPageButtons) {
    resultsPageButtons.innerHTML = Array.from({ length: totalPages }, (_, index) => {
      const page = index + 1;
      const activeClass = page === state.currentResultsPage ? " is-active" : "";
      return `<button type="button" class="results-page-btn${activeClass}" data-results-page="${page}" aria-label="第 ${page} 页">${page}</button>`;
    }).join("");
  }
}

async function showTableState(message, tone = "neutral") {
  setResultsPaginationVisible(false);
  const stateClass = tone === "error" ? "table-state is-error" : "table-state";
  await setTableHtmlWithTransition(`<tr><td colspan="8" class="${stateClass}">${escapeHtml(message)}</td></tr>`);
}

async function renderCurrentResultsPage() {
  const totalPages = Math.max(1, Math.ceil(state.currentResults.length / RESULTS_PAGE_SIZE));
  state.currentResultsPage = Math.min(Math.max(1, state.currentResultsPage), totalPages);
  const startIndex = (state.currentResultsPage - 1) * RESULTS_PAGE_SIZE;
  const pageResults = state.currentResults.slice(startIndex, startIndex + RESULTS_PAGE_SIZE);
  const html = pageResults.map((item, idx) => {
    const md = item.metadata || {};
    return `
      <tr class="is-clickable" data-cell-id="${escapeHtml(item.cell_id)}">
        <td>${startIndex + idx + 1}</td>
        <td class="cell-id">${escapeHtml(item.cell_id)}</td>
        <td>${escapeHtml(formatMetric(item.distance))}</td>
        <td>${escapeHtml(formatMetric(item.score))}</td>
        <td>${escapeHtml(md.cell_type || "-")}</td>
        <td>${escapeHtml(md.disease || "-")}</td>
        <td>${escapeHtml(md.AgeGroup || "-")}</td>
        <td>${escapeHtml(md.sex || "-")}</td>
      </tr>`;
  }).join("");

  await setTableHtmlWithTransition(html);
  updateResultsPagination();
  resultsBody.querySelectorAll("tr[data-cell-id]").forEach((row) => {
    row.addEventListener("click", () => {
      const cellId = row.dataset.cellId || "";
      focusResultRow(cellId);
      selectCell(cellId, { syncRow: false });
    });
  });
}

async function renderResults(results = []) {
  state.currentResults = Array.isArray(results) ? results : [];
  state.currentResultsPage = 1;
  if (!state.currentResults.length) {
    state.umapFocusedCellId = "";
    renderCellDetail("");
    await showTableState("No results. Adjust query or filters.");
    return;
  }
  await renderCurrentResultsPage();
}

function resetMainPageOutputs() {
  state.currentResults = [];
  state.chartFocus = { key: "", value: "" };
  state.umapSelectionCellIds = [];
  setQueryMetrics();
  setMessage(queryStatus, "Ready for query", "neutral");
  refreshEvaluationUI();
  renderAnnBenchmark(null);
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
    if (timeoutLike) {
      setMessage(hubHistoryMessage, "历史索引加载超时，可先直接录入数据集进入核心页面", "neutral");
    } else {
      setMessageWithAction(hubHistoryMessage, `历史索引加载失败：${error.message}`, "error", "重试", () => {
        loadHistoryIndexes().catch((retryError) => {
          setMessage(hubHistoryMessage, retryError.message, "error");
        });
      });
    }
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
      const datasetTitle = deriveDatasetTitle(item);
      const datasetSubtitle = deriveDatasetSubtitle(item);
      const indexLabel = humanizeIndexType(item.index_type);
      const metricLabel = humanizeDistanceMetric(item.distance_metric, item.effective_metric);
      const vectorsText = item.cell_count ? formatNumber(item.cell_count) : "--";
      const dimensionText = item.vector_dim ? formatNumber(item.vector_dim) : "--";
      const buildText = formatCompactTimeMs(item.build_time_ms);
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
          <div class="history-card-header">
            <div class="history-card-header-copy">
              <div class="history-card-kicker-row">
                <span class="history-card-kicker-dot${item.is_active ? " is-active" : ""}" aria-hidden="true"></span>
                <span class="history-card-kicker">${escapeHtml(statusLabel)}</span>
              </div>
              <h3 class="history-card-title" title="${escapeHtml(datasetTitle)}">${escapeHtml(datasetTitle)}</h3>
              <p class="history-card-subtitle" title="${escapeHtml(datasetSubtitle)}">${escapeHtml(datasetSubtitle)}</p>
            </div>
          </div>
          <div class="history-card-summary">
            <p class="history-card-summary-title">${escapeHtml(indexLabel)} Index</p>
            <p class="history-card-summary-subtitle">${escapeHtml(metricLabel)} similarity</p>
          </div>
          <dl class="history-card-stat-grid">
            <div class="history-card-stat">
              <dt>Vectors</dt>
              <dd>${escapeHtml(vectorsText)}</dd>
            </div>
            <div class="history-card-stat">
              <dt>Dimension</dt>
              <dd>${escapeHtml(dimensionText)}</dd>
            </div>
          </dl>
          <div class="history-card-build-row">
            <span class="history-card-build-label">Build</span>
            <span class="history-card-build-value">${escapeHtml(buildText)}</span>
          </div>
          <div class="history-card-footer">
            <p class="history-card-footnote" title="${escapeHtml(datasetSubtitle)}">${escapeHtml(datasetSubtitle)}</p>
            <button class="btn action-btn secondary-btn btn-sm mt-2 history-card-open-btn" data-open-index="${item.id}">Open →</button>
          </div>
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

async function uploadDatasetFromHub() {
  const file = hubDatasetFile?.files?.[0] || null;
  if (!file) {
    setMessage(hubNewDatasetMessage, "请选择要上传的 CSV 或 h5ad 文件", "error");
    return;
  }

  if (uploadDatasetBtn) uploadDatasetBtn.disabled = true;
  if (openNewDatasetBtn) openNewDatasetBtn.disabled = true;
  setMessage(hubNewDatasetMessage, "Uploading dataset...", "neutral");
  try {
    const uploaded = await uploadDatasetFile(file);
    const path = uploaded.data_path || "";
    if (!path) throw new Error("Uploaded dataset path missing");
    hubDataPath.value = path;
    state.activeIndex = null;
    await enterCorePage({
      dataPath: path,
      info: normalizeDatasetInfo(uploaded.dataset || {}, path),
      indexRecord: null,
    });
    setMessage(hubNewDatasetMessage, `Uploaded dataset: ${path}`, "success");
  } catch (error) {
    setMessage(hubNewDatasetMessage, error.message, "error");
  } finally {
    if (uploadDatasetBtn) uploadDatasetBtn.disabled = false;
    if (openNewDatasetBtn) openNewDatasetBtn.disabled = false;
  }
}

async function enterCorePage({ dataPath, info, indexRecord }) {
  setCurrentDataset(dataPath);
  state.currentDatasetInfo = normalizeDatasetInfo(info || {}, state.currentDataPath);
  state.activeIndex = indexRecord || null;
  state.aiAssistantOpen = true;
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
  setAiAssistantPanelOpen(true);
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

async function exportUmapForCurrentDataset(fileFormat) {
  if (!state.currentDataPath) {
    setMessage(queryStatus, "No data path for UMAP export", "error");
    return;
  }

  const format = fileFormat === "json" ? "json" : "csv";
  const button = format === "json" ? exportUmapJsonBtn : exportUmapCsvBtn;
  const rows = buildUmapExportRows(getCurrentScopePoints());
  if (!rows.length) {
    setMessage(queryStatus, "No UMAP points to export", "error");
    return;
  }

  if (button) button.disabled = true;
  setMessage(queryStatus, `Exporting UMAP ${format.toUpperCase()}...`, "neutral");
  try {
    const filename = `${safeExportName(state.currentDataPath)}_umap_${exportTimestamp()}.${format}`;
    if (format === "json") {
      downloadBlob(JSON.stringify(rows, null, 2), filename, "application/json;charset=utf-8");
    } else {
      downloadBlob(rowsToCsv(rows), filename, "text/csv;charset=utf-8");
    }
    setMessage(queryStatus, `UMAP exported: ${filename}, ${formatNumber(rows.length)} points`, "success");
  } catch (error) {
    setMessage(queryStatus, `UMAP export failed: ${error.message}`, "error");
  } finally {
    if (button) button.disabled = false;
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

async function uploadDatasetFromMain() {
  const file = datasetFileInput?.files?.[0] || null;
  if (!file) {
    setMessage(indexStatus, "请选择要上传的 CSV 或 h5ad 文件", "error");
    return;
  }

  if (uploadDataBtn) uploadDataBtn.disabled = true;
  if (inspectDataBtn) inspectDataBtn.disabled = true;
  if (buildIndexBtn) buildIndexBtn.disabled = true;
  setMessage(indexStatus, "Uploading dataset...", "neutral");
  try {
    const uploaded = await uploadDatasetFile(file);
    const path = uploaded.data_path || "";
    if (!path) throw new Error("Uploaded dataset path missing");
    dataPathInput.value = path;
    state.activeIndex = null;
    setCurrentDataset(path);
    state.currentDatasetInfo = normalizeDatasetInfo(uploaded.dataset || {}, path);
    renderDatasetInfo(state.currentDatasetInfo);
    setBadgeState("is-idle", "No Index", "Dataset uploaded, build index when needed");
    await Promise.all([
      loadUmapForCurrentDataset(),
      loadAnalyticsForCurrentDataset(),
      loadMetadataOptionsForCurrentDataset(),
    ]);
    setMessage(indexStatus, `Dataset uploaded: ${path}`, "success");
  } catch (error) {
    setMessage(indexStatus, error.message, "error");
  } finally {
    if (uploadDataBtn) uploadDataBtn.disabled = false;
    if (inspectDataBtn) inspectDataBtn.disabled = false;
    if (buildIndexBtn) buildIndexBtn.disabled = false;
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
    renderAnnBenchmark(data.improvement_benchmark || null);
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    clearUmapHighlights();
    setQueryMetrics({ mode: "Search by ID", resultCount: 0, queryTime: null, highlightCount: 0 });
    refreshEvaluationUI(null, evaluate);
    renderAnnBenchmark(null);
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

  let topK;
  const csvFile = queryVectorCsvInput?.files?.[0] || null;
  try {
    topK = positiveTopK(topKVectorInput);
    if (!csvFile) {
      parseVectorInput();
    }
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
    let data;
    if (csvFile) {
      const formData = new FormData();
      formData.append("file", csvFile);
      formData.append("top_k", String(topK));
      formData.append("index_id", String(state.activeIndex.id));
      formData.append("filters", JSON.stringify(activeFilters()));
      formData.append("evaluate", evaluate ? "true" : "false");
      const headers = {};
      if (state.authToken) headers.Authorization = `Bearer ${state.authToken}`;
      const response = await fetch("/api/search/by-vector-csv", {
        method: "POST",
        headers,
        body: formData,
      });
      const rawText = await response.text();
      try {
        data = rawText ? JSON.parse(rawText) : {};
      } catch {
        throw new Error("Failed to parse server response");
      }
      if (!response.ok) {
        throw new Error(data.error || `Request failed (${response.status})`);
      }
    } else {
      const vector = parseVectorInput();
      data = await postJson("/api/search/by-vector", {
        vector,
        top_k: topK,
        filters: activeFilters(),
        index_id: state.activeIndex.id,
        evaluate,
      });
    }
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
      `Done: ${Array.isArray(data.results) ? data.results.length : 0} results, ${formatTime(data.query_time_ms)}${
        data.query?.csv ? `, CSV dim ${data.query.csv.input_dim}` : ""
      }`,
      "success"
    );
    refreshEvaluationUI(data.evaluation || null, evaluate);
    renderAnnBenchmark(data.improvement_benchmark || null);
  } catch (error) {
    setMessage(queryStatus, error.message, "error");
    await showTableState(error.message, "error");
    clearUmapHighlights();
    setQueryMetrics({ mode: "Search by Vector", resultCount: 0, queryTime: null, highlightCount: 0 });
    refreshEvaluationUI(null, evaluate);
    renderAnnBenchmark(null);
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

if (resultsPagination) {
  resultsPagination.addEventListener("click", (event) => {
    const pageButton = event.target.closest("[data-results-page]");
    if (pageButton) {
      state.currentResultsPage = Number(pageButton.dataset.resultsPage) || 1;
    } else if (event.target.closest("#resultsPrevPage")) {
      state.currentResultsPage -= 1;
    } else if (event.target.closest("#resultsNextPage")) {
      state.currentResultsPage += 1;
    } else {
      return;
    }
    renderCurrentResultsPage().catch(() => undefined);
  });
}
logoutBtn.addEventListener("click", clearSession);
hubLogoutBtn.addEventListener("click", clearSession);

function handleOpenNewDatasetFromHub() {
  openNewDatasetFromHub().catch((error) => {
    setMessage(hubNewDatasetMessage, error.message, "error");
  });
}

openNewDatasetBtn.addEventListener("click", handleOpenNewDatasetFromHub);

if (uploadDatasetBtn) {
  uploadDatasetBtn.addEventListener("click", () => {
    uploadDatasetFromHub().catch((error) => {
      setMessage(hubNewDatasetMessage, error.message, "error");
    });
  });
}

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
  if (aiAssistantPanel && !aiAssistantPanel.hidden) {
    ensureAiAssistantPanelPosition();
  }
});

if (aiAssistantDragHandle) {
  aiAssistantDragHandle.addEventListener("mousedown", (event) => {
    if (event.button !== 0 || !aiAssistantPanel) return;
    if (!state.aiAssistantMoveEnabled) return;
    if (state.aiAssistantFullscreen) return;
    if (event.target.closest("button")) return;
    const rect = aiAssistantPanel.getBoundingClientRect();
    state.aiAssistantDrag.active = true;
    state.aiAssistantDrag.offsetX = event.clientX - rect.left;
    state.aiAssistantDrag.offsetY = event.clientY - rect.top;
    aiAssistantPanel.classList.add("is-dragging");
    event.preventDefault();
  });
}

document.addEventListener("mousemove", (event) => {
  if (!state.aiAssistantDrag.active || !aiAssistantPanel) return;
  applyAiAssistantPanelPosition(
    {
      left: event.clientX - state.aiAssistantDrag.offsetX,
      top: event.clientY - state.aiAssistantDrag.offsetY,
    },
    { persist: false }
  );
});

document.addEventListener("mouseup", () => {
  if (!state.aiAssistantDrag.active || !aiAssistantPanel) return;
  state.aiAssistantDrag.active = false;
  aiAssistantPanel.classList.remove("is-dragging");
  if (state.aiAssistantPosition) {
    saveAiAssistantPosition(state.aiAssistantPosition);
  }
});

if (aiAssistantMoveToggle) {
  aiAssistantMoveToggle.addEventListener("click", () => {
    if (state.aiAssistantFullscreen) {
      setMessage(aiAssistantStatus, "请先退出全屏，再开启移动模式。", "neutral", "", 1800);
      return;
    }
    state.aiAssistantMoveEnabled = !state.aiAssistantMoveEnabled;
    syncAiAssistantMoveUI();
    setMessage(
      aiAssistantStatus,
      state.aiAssistantMoveEnabled ? "移动模式已开启，可拖动顶部移动窗口。" : "移动模式已关闭，窗口当前位置已固定。",
      "neutral",
      "",
      1800
    );
  });
}

if (aiAssistantFullscreenToggle) {
  aiAssistantFullscreenToggle.addEventListener("click", () => {
    state.aiAssistantFullscreen = !state.aiAssistantFullscreen;
    if (state.aiAssistantFullscreen) {
      state.aiAssistantMoveEnabled = false;
    }
    syncAiAssistantMoveUI();
    if (state.aiAssistantFullscreen) {
      ensureAiAssistantPanelPosition();
      setMessage(aiAssistantStatus, "已切换为全屏显示。", "neutral", "", 1800);
      return;
    }
    ensureAiAssistantPanelPosition({ forceDefault: true });
    setMessage(aiAssistantStatus, "已恢复默认大小。", "neutral", "", 1800);
  });
}

if (aiAssistantConversationToggle) {
  aiAssistantConversationToggle.addEventListener("click", () => {
    state.aiAssistantConversationExpanded = !state.aiAssistantConversationExpanded;
    syncAiAssistantMoveUI();
    setMessage(
      aiAssistantStatus,
      state.aiAssistantConversationExpanded ? "已展开对话区，长对话现在会拥有更多空间。" : "已收起对话区，恢复完整助手布局。",
      "neutral",
      "",
      1800
    );
    window.requestAnimationFrame(() => {
      scrollAiAssistantMessagesToBottom();
    });
  });
}

if (aiAssistantClose) {
  aiAssistantClose.addEventListener("click", () => {
    setAiAssistantPanelOpen(false);
  });
}

if (aiAssistantModeCards) {
  aiAssistantModeCards.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-ai-mode]");
    if (!trigger) return;
    const nextMode = trimText(trigger.dataset.aiMode || "");
    if (!AI_ASSISTANT_MODE_CONFIG[nextMode] || nextMode === currentAiAssistantMode()) return;
    state.aiAssistantMode = nextMode;
    syncAiAssistantModeUI({ resetConversation: true });
  });
}

if (aiAssistantRefreshSuggestions) {
  aiAssistantRefreshSuggestions.addEventListener("click", () => {
    rotateAiAssistantSuggestions();
  });
}

if (aiAssistantSuggestionsList) {
  aiAssistantSuggestionsList.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-ai-suggested-question]");
    if (!trigger) return;
    const question = trimText(trigger.dataset.aiSuggestedQuestion || "");
    if (!question) return;
    fillAiAssistantInput(question);
    setMessage(aiAssistantStatus, "推荐问题已填入输入框，可继续编辑或直接发送。", "neutral", "", 2200);
  });
}

if (aiAssistantSendBtn) {
  aiAssistantSendBtn.addEventListener("click", () => {
    sendAiAssistantQuestion(aiAssistantInput?.value || "").catch(() => undefined);
  });
}

if (aiAssistantRegenerateBtn) {
  aiAssistantRegenerateBtn.addEventListener("click", () => {
    sendAiAssistantQuestion(state.aiAssistantLastQuestion || "").catch(() => undefined);
  });
}

if (aiAssistantInput) {
  aiAssistantInput.addEventListener("input", () => {
    syncAiAssistantComposerState();
  });
  aiAssistantInput.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      sendAiAssistantQuestion(aiAssistantInput.value || "").catch(() => undefined);
    }
  });
}

if (aiAssistantMessages) {
  aiAssistantMessages.addEventListener("click", async (event) => {
    const copyButton = event.target.closest("[data-ai-copy-message-index]");
    if (copyButton) {
      const message = state.aiAssistantMessages[Number(copyButton.dataset.aiCopyMessageIndex)];
      if (!message) return;
      try {
        await copyAiAssistantText(message.content || "");
        setMessage(aiAssistantStatus, "已复制到剪贴板。", "success", "", 1800);
      } catch (error) {
        setMessage(aiAssistantStatus, error.message || "复制失败", "error", "", 2200);
      }
      return;
    }

    const editButton = event.target.closest("[data-ai-edit-message-index]");
    if (editButton) {
      const message = state.aiAssistantMessages[Number(editButton.dataset.aiEditMessageIndex)];
      if (!message) return;
      fillAiAssistantInput(message.content || "");
      setMessage(aiAssistantStatus, "已将问题填回输入框，你可以继续编辑。", "neutral", "", 2200);
      return;
    }

    const resendButton = event.target.closest("[data-ai-resend-message-index]");
    if (resendButton) {
      const message = state.aiAssistantMessages[Number(resendButton.dataset.aiResendMessageIndex)];
      if (!message) return;
      sendAiAssistantQuestion(message.content || "").catch(() => undefined);
      return;
    }

    const regenerateButton = event.target.closest("[data-ai-regenerate-message-index]");
    if (regenerateButton) {
      const index = Number(regenerateButton.dataset.aiRegenerateMessageIndex);
      const message = state.aiAssistantMessages[index];
      const linkedQuestion = trimText(message?.linkedQuestion || findAiAssistantLinkedQuestion(index));
      if (!linkedQuestion) return;
      sendAiAssistantQuestion(linkedQuestion).catch(() => undefined);
      return;
    }

    const filterButton = event.target.closest("[data-ai-filter-key]");
    if (filterButton) {
      const key = filterButton.dataset.aiFilterKey || "";
      const value = filterButton.dataset.aiFilterValue || "";
      applyAiAssistantFilters({ [key]: value });
      setMessage(queryStatus, `已按 AI 建议应用筛选：${key}=${value}`, "neutral");
      return;
    }

    const cellButton = event.target.closest("[data-ai-focus-cell-id]");
    if (cellButton) {
      const cellId = trimText(cellButton.dataset.aiFocusCellId || "");
      if (!cellId) return;
      selectCell(cellId, { syncRow: true });
      focusResultRow(cellId).catch(() => undefined);
      setMessage(queryStatus, `已聚焦 AI 推荐细胞：${cellId}`, "neutral");
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

if (uploadDataBtn) {
  uploadDataBtn.addEventListener("click", () => {
    uploadDatasetFromMain().catch((error) => {
      setMessage(indexStatus, error.message, "error");
    });
  });
}

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

if (exportUmapCsvBtn) {
  exportUmapCsvBtn.addEventListener("click", () => {
    exportUmapForCurrentDataset("csv").catch((error) => {
      setMessage(queryStatus, error.message, "error");
    });
  });
}

if (exportUmapJsonBtn) {
  exportUmapJsonBtn.addEventListener("click", () => {
    exportUmapForCurrentDataset("json").catch((error) => {
      setMessage(queryStatus, error.message, "error");
    });
  });
}

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
syncAiAssistantModeUI({ resetConversation: true });
syncAiAssistantMoveUI();
showTableState("No query results yet. Build/activate an index then query.").catch(() => undefined);
checkAuthAndInit();
