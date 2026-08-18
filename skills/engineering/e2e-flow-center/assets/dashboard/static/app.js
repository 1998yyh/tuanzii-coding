"use strict";

/* ---------- 基础工具 ---------- */
const $ = (selector) => document.querySelector(selector);

function element(name, text, className) {
  const node = document.createElement(name);
  if (text !== undefined && text !== null) node.textContent = text;
  if (className) node.className = className;
  return node;
}

async function api(path) {
  const response = await fetch(path, { credentials: "same-origin" });
  if (!response.ok) {
    let detail = `请求失败（${response.status}）。`;
    try { detail = (await response.json()).detail || detail; } catch (_) { /* Keep the status message. */ }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return response.json();
}

function formatTime(value) {
  if (!value) return "--";
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString("zh-CN", { dateStyle: "medium", timeStyle: "short" });
}

function formatBytes(value) {
  if (!Number.isFinite(value)) return "--";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

function showError(message) {
  $("#error-text").textContent = message;
  $("#error-banner").hidden = false;
}

/* ---------- 内联 SVG 图标（lucide, ISC） ---------- */
const ICON_PATHS = {
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
  chevron: '<path d="m9 18 6-6-6-6"/>',
  listChecks: '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/>',
  alert: '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6h4.5"/>',
  user: '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
  shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
  gitCompare: '<circle cx="5" cy="6" r="3"/><path d="M12 6h5a2 2 0 0 1 2 2v7"/><path d="m15 9-3-3 3-3"/><circle cx="19" cy="18" r="3"/><path d="M12 18H7a2 2 0 0 1-2-2V9"/><path d="m9 15 3 3-3 3"/>',
  fileCode: '<path d="M4 22h14a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v4"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="m5 12-3 3 3 3"/><path d="m9 18 3-3-3-3"/>',
  activity: '<path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>',
  camera: '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
  video: '<path d="m16 13 5.2 3.5a.5.5 0 0 0 .8-.4V7.9a.5.5 0 0 0-.8-.4L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
  fileText: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>',
  external: '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
  archive: '<rect x="2" y="3" width="20" height="5" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/>',
  entry: '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" x2="3" y1="12" y2="12"/>',
};

function icon(name, size = 16) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", String(size));
  svg.setAttribute("height", String(size));
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "2");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  svg.innerHTML = ICON_PATHS[name] || "";
  return svg;
}

/* ---------- 标签映射 ---------- */
const STATUS_LABELS = { draft: "草稿", ready: "已就绪", active: "已激活", retired: "已停用" };
const REASON_LABELS = { "path-match": "路径匹配", "always-run": "始终运行" };
const RUN_STATUS_LABELS = { passed: "通过", failed: "失败", blocked: "阻塞", cancelled: "已取消", unknown: "未知" };
const EVIDENCE_TYPE_LABELS = { screenshot: "截图", video: "视频", trace: "Trace", report: "HTML 报告", log: "执行日志", attachment: "附件" };
const scenarioLabels = {
  "first-extraction": "首次抽离",
  inventory: "已有流程盘点",
  "added-flow": "新增流程",
  "changed-flow": "原流程变更",
  "goal-retired": "业务目标下线",
  "implementation-change": "纯实现变化",
  "unable-to-determine": "无法判断",
};
const operationLabels = {
  created: "创建",
  "semantic-updated": "语义更新",
  "provenance-updated": "仅更新溯源",
  retired: "下线",
  unchanged: "未修改",
};

/* ---------- 看板状态 ---------- */
const state = {
  payload: null,
  activeKey: null,
  query: "",
  runs: [],
  currentRunId: null,
};

const flowKey = (record) => record.flow?.id || record.path;
const flowTone = (record) => (!record.valid ? "attention" : record.affected ? "affected" : "ready");

function badge(text, kind = "") { return element("span", text, `badge ${kind}`.trim()); }

function metric(value, label) {
  const node = element("div", undefined, "metric");
  node.append(element("strong", String(value)), element("span", label));
  return node;
}

function sectionTitle(iconName, title, note) {
  const wrap = element("div", undefined, "section-title");
  const copy = element("div");
  copy.append(element("h3", title));
  if (note) copy.append(element("p", note));
  wrap.append(icon(iconName, 18), copy);
  return wrap;
}

/* ---------- 左栏：目录 ---------- */
function filteredRecords() {
  const records = state.payload?.flows || [];
  const needle = state.query.trim().toLowerCase();
  if (!needle) return records;
  return records.filter((record) => {
    const flow = record.flow || {};
    return [flow.name, flow.id, flow.category, flow.goal, record.path]
      .some((value) => String(value || "").toLowerCase().includes(needle));
  });
}

function renderCatalog() {
  const payload = state.payload;
  if (!payload) return;
  $("#catalog-total").textContent = `${payload.flows.length} 条流程`;
  $("#catalog-attention").textContent = payload.invalidFlowCount ? `${payload.invalidFlowCount} 条需处理` : "";

  const nav = $("#flow-nav");
  nav.replaceChildren();
  const groups = new Map();
  for (const record of filteredRecords()) {
    const category = record.flow?.category || "未分类";
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push(record);
  }
  if (!groups.size) {
    nav.append(element("p", state.query ? "没有匹配的流程。" : "没有发现 .yaml 流程文件；请先由 e2e-flow-extract 抽离业务流程。", "empty-copy"));
  }
  for (const [category, records] of groups) {
    const group = element("section", undefined, "flow-group");
    const heading = element("h2", category);
    heading.append(element("span", String(records.length)));
    group.append(heading);
    for (const record of records) {
      const flow = record.flow || {};
      const item = element("button", undefined, `flow-nav-item${flowKey(record) === state.activeKey ? " active" : ""}`);
      item.type = "button";
      item.dataset.key = flowKey(record);
      item.setAttribute("aria-current", String(flowKey(record) === state.activeKey));
      const dot = element("span", undefined, `flow-dot ${flowTone(record)}`);
      dot.setAttribute("aria-hidden", "true");
      const copy = element("span", undefined, "flow-nav-copy");
      copy.append(element("strong", flow.name || record.path));
      copy.append(element("small", `${flow.priority || "--"} · ${flow.id || record.path}`));
      item.append(dot, copy, icon("chevron", 15));
      item.addEventListener("click", () => {
        state.activeKey = flowKey(record);
        renderCatalog();
        renderDetail();
      });
      group.append(item);
    }
    nav.append(group);
  }

  const changedBox = $("#changed-files");
  const changed = payload.changedPaths || [];
  if (!payload.gitAvailable) {
    changedBox.hidden = false;
    $("#changed-count").textContent = "不可用";
    $("#changed-list").replaceChildren(element("p", "当前项目不是 Git 仓库，影响分析不可用。", "muted"));
  } else if (changed.length) {
    changedBox.hidden = false;
    $("#changed-count").textContent = String(changed.length);
    $("#changed-list").replaceChildren(...changed.map((path) => element("code", path)));
  } else {
    changedBox.hidden = true;
  }
}

/* ---------- 中栏：流程详情 ---------- */
function currentRecord() {
  const records = state.payload?.flows || [];
  return records.find((record) => flowKey(record) === state.activeKey) || null;
}

function renderDetail() {
  const pane = $("#flow-detail");
  pane.replaceChildren();
  const record = currentRecord();
  if (!record) {
    if (!(state.payload?.flows || []).length) {
      const empty = element("div", undefined, "empty-state");
      empty.append(icon("listChecks", 24), element("h2", "暂无流程"), element("p", "由 e2e-flow-extract 抽离业务流程后，这里会显示流程目录。"));
      pane.append(empty);
    } else {
      pane.append(element("p", "选择左侧流程查看详情。", "empty"));
    }
    return;
  }
  const flow = record.flow;
  if (!flow) {
    const hero = element("section", undefined, "flow-hero");
    hero.append(element("p", record.path, "section-label"), element("h2", "流程文件无法解析"));
    pane.append(hero, diagnosticsSection(record));
    return;
  }

  const hero = element("section", undefined, "flow-hero");
  hero.append(element("p", `${flow.category || "未分类"} / ${flow.id}`, "section-label"), element("h2", flow.name || flow.id));
  if (flow.description) hero.append(element("p", flow.description, "flow-description"));
  const meta = element("div", undefined, "flow-meta");
  const persona = element("span");
  persona.append(icon("user", 15), element("b", "用户角色"), document.createTextNode(flow.persona || "未定义"));
  const goal = element("span");
  goal.append(icon("shield", 15), element("b", "业务目标"), document.createTextNode(flow.goal || "未定义"));
  meta.append(persona, goal);
  hero.append(meta);

  const badges = element("div", undefined, "badge-row");
  badges.append(badge(STATUS_LABELS[flow.status] || flow.status || "未知", flow.status === "active" ? "ok" : flow.status === "retired" ? "" : "accent"));
  badges.append(badge(record.valid ? "结构有效" : "结构有误", record.valid ? "ok" : "error"));
  if (state.payload?.gitAvailable) {
    if (record.affected) {
      badges.append(badge(`受影响 · ${(record.reasons || []).map((reason) => REASON_LABELS[reason] || reason).join(" + ")}`, "affected"));
    } else {
      badges.append(badge("未受影响"));
    }
  }
  if (flow.priority) badges.append(badge(flow.priority));
  for (const tag of flow.tags || []) badges.append(badge(tag));
  badges.append(badge(flow.enabled ? "已启用" : "未启用", flow.enabled ? "ok" : ""));
  hero.append(badges);
  pane.append(hero);

  if (!record.valid) pane.append(diagnosticsSection(record));

  const stepsSection = element("section", undefined, "detail-section");
  stepsSection.append(sectionTitle("listChecks", "业务步骤", `${(flow.steps || []).length} 个可观察检查点`));
  const steps = element("ol", undefined, "step-list");
  (flow.steps || []).forEach((step, index) => {
    const row = element("li");
    row.append(element("span", String(index + 1).padStart(2, "0"), "step-index"));
    const copy = element("div");
    copy.append(element("h4", step.title || step.id || `步骤 ${index + 1}`));
    copy.append(element("p", step.expected || "未定义预期结果。"));
    row.append(copy);
    steps.append(row);
  });
  stepsSection.append(steps);
  pane.append(stepsSection);

  const grid = element("section", undefined, "detail-grid");
  const testBlock = element("div", undefined, "detail-section compact-section");
  const sourceLabels = { external: "业务项目", existing: "项目已有" };
  testBlock.append(sectionTitle("fileCode", "测试来源", `${sourceLabels[flow.test?.source] || "未知来源"} Playwright 测试`));
  testBlock.append(element("code", flow.test?.spec || "未配置", "path-block"));
  grid.append(testBlock);

  const pathsBlock = element("div", undefined, "detail-section compact-section");
  pathsBlock.append(sectionTitle("gitCompare", "影响路径", `${(flow.paths || []).length} 条项目路径规则`));
  const pathList = element("div", undefined, "path-list");
  for (const pattern of flow.paths || []) pathList.append(element("code", pattern));
  pathsBlock.append(pathList);
  grid.append(pathsBlock);

  const entryBlock = element("div", undefined, "detail-section compact-section");
  entryBlock.append(sectionTitle("entry", "入口", flow.entry?.requiresAuth ? "需要登录态" : "无需登录态"));
  entryBlock.append(element("code", flow.entry?.url || "未配置", "path-block"));
  grid.append(entryBlock);
  pane.append(grid);
}

function diagnosticsSection(record) {
  const section = element("section", undefined, "diagnostics");
  section.append(sectionTitle("alert", "需要处理", "修复以下问题后流程才结构有效。"));
  const list = element("ul");
  for (const issue of record.issues) {
    const row = element("li");
    row.append(element("span", `${issue.field}：`, "issue-field"), document.createTextNode(issue.message));
    list.append(row);
  }
  section.append(list);
  return section;
}

/* ---------- 右栏：运行记录 ---------- */
function evidenceUrl(path) {
  return `/evidence/${String(path).split("/").map(encodeURIComponent).join("/")}`;
}

function runStatusIcon(status) {
  if (status === "passed") return icon("check", 14);
  if (status === "failed" || status === "blocked") return icon("x", 14);
  if (status === "cancelled") return icon("clock", 14);
  return icon("alert", 14);
}

function renderRunList() {
  const list = $("#run-list");
  list.replaceChildren();
  if (!state.runs.length) {
    list.append(element("p", "暂无运行记录。由 e2e-evidence 运行流程后，结果会写入项目 results/ 目录。", "empty-copy"));
    return;
  }
  for (const run of state.runs) {
    const item = element("button", undefined, `run-item${run.id === state.currentRunId ? " active" : ""}`);
    item.type = "button";
    const iconWrap = element("span", undefined, `run-icon run-${run.status}`);
    iconWrap.append(runStatusIcon(run.status));
    const copy = element("span");
    copy.append(element("strong", RUN_STATUS_LABELS[run.status] || run.status));
    copy.append(element("small", formatTime(run.createdAt)));
    item.append(iconWrap, copy, element("em", `${run.flows.length} 条流程`));
    item.addEventListener("click", () => {
      state.currentRunId = run.id;
      renderRunList();
      renderRunDetail();
    });
    list.append(item);
  }
}

function renderRunDetail() {
  const pane = $("#run-detail");
  const run = state.runs.find((item) => item.id === state.currentRunId);
  if (!run) {
    pane.hidden = true;
    pane.replaceChildren();
    return;
  }
  pane.hidden = false;
  pane.replaceChildren();
  const heading = element("div", undefined, "run-detail-heading");
  heading.append(element("h2", `运行 ${run.id}`), badge(RUN_STATUS_LABELS[run.status] || run.status, run.status === "passed" ? "ok" : run.status === "failed" ? "error" : "accent"));
  pane.append(heading);
  const meta = element("dl");
  const rows = [
    ["开始时间", formatTime(run.createdAt)],
    ["证据文件", `${run.evidenceSummary?.total || 0} 个`],
  ];
  if (run.command) rows.push(["命令", run.command]);
  for (const [term, value] of rows) {
    const row = element("div");
    row.append(element("dt", term), element("dd", value));
    meta.append(row);
  }
  pane.append(meta);

  for (const flow of run.flows) {
    const item = element("details", undefined, "result-item");
    const summary = element("summary");
    summary.append(badge(flow.flowId || "未知流程", flow.status === "passed" ? "ok" : flow.status === "failed" ? "error" : ""));
    item.append(summary);
    if (flow.spec) item.append(element("p", flow.spec, "muted"));
    if (flow.stepIds?.length) item.append(element("p", `执行到步骤：${flow.stepIds.join(" → ")}`, "muted"));
    if (flow.error || flow.output) item.append(element("pre", flow.error || flow.output));
    for (const warning of flow.evidenceWarnings || []) {
      const note = element("p", warning, "warning");
      note.prepend(icon("alert", 14));
      item.append(note);
    }
    const trigger = element("button", undefined, "button compact evidence-trigger");
    trigger.type = "button";
    trigger.append(icon("activity", 14), document.createTextNode(" 查看证据"), element("span", String(flow.evidence.length)));
    trigger.disabled = !flow.evidence.length;
    trigger.addEventListener("click", (event) => openEvidenceModal(run, flow, event.currentTarget));
    item.append(trigger);
    pane.append(item);
  }
}

/* ---------- 证据中心模态框 ---------- */
function openEvidenceModal(run, flow, returnFocus) {
  const backdrop = element("div", undefined, "modal-backdrop");
  const modal = element("section", undefined, "evidence-modal");
  modal.setAttribute("role", "dialog");
  modal.setAttribute("aria-modal", "true");
  modal.setAttribute("aria-labelledby", "evidence-modal-heading");

  const header = element("header", undefined, "evidence-modal-header");
  const titleWrap = element("div");
  const heading = element("h2", flow.flowId || "未知流程");
  heading.id = "evidence-modal-heading";
  titleWrap.append(
    element("p", `运行 ${run.id}`, "section-label"),
    heading,
    element("p", `${formatTime(run.createdAt)} · ${flow.evidence.length} 个证据文件`, "muted"),
  );
  const actions = element("div", undefined, "evidence-modal-actions");
  actions.append(badge(RUN_STATUS_LABELS[flow.status] || flow.status || "未知", flow.status === "passed" ? "ok" : flow.status === "failed" ? "error" : "accent"));
  const close = element("button", undefined, "icon-button");
  close.type = "button";
  close.setAttribute("aria-label", "关闭证据中心");
  close.title = "关闭证据中心";
  close.append(icon("x", 18));
  actions.append(close);
  header.append(titleWrap, actions);

  const body = element("div", undefined, "evidence-modal-body");
  const screenshots = flow.evidence.filter((item) => item.type === "screenshot");
  const videos = flow.evidence.filter((item) => item.type === "video");
  const files = flow.evidence.filter((item) => !["screenshot", "video"].includes(item.type));

  if (screenshots.length) {
    const group = element("div", undefined, "evidence-group");
    const title = element("h4");
    title.append(icon("camera", 14), document.createTextNode("运行截图"));
    const gridBox = element("div", undefined, "screenshot-grid");
    for (const item of screenshots) {
      const link = element("a", undefined, "screenshot-item");
      link.href = evidenceUrl(item.path);
      link.target = "_blank";
      link.rel = "noreferrer";
      const img = element("img");
      img.src = evidenceUrl(item.path);
      img.alt = `${item.name} 截图`;
      img.loading = "lazy";
      link.append(img, element("span", item.name));
      gridBox.append(link);
    }
    group.append(title, gridBox);
    body.append(group);
  }
  if (videos.length) {
    const group = element("div", undefined, "evidence-group");
    const title = element("h4");
    title.append(icon("video", 14), document.createTextNode("视频回放"));
    group.append(title);
    for (const item of videos) {
      const video = element("video", undefined, "evidence-video");
      video.controls = true;
      video.preload = "metadata";
      video.src = evidenceUrl(item.path);
      video.setAttribute("aria-label", `${item.name} 视频回放`);
      group.append(video);
    }
    body.append(group);
  }
  if (files.length) {
    const group = element("div", undefined, "evidence-group");
    const title = element("h4");
    title.append(icon("fileText", 14), document.createTextNode("运行文件"));
    const links = element("div", undefined, "evidence-links");
    for (const item of files) {
      const link = element("a");
      link.href = evidenceUrl(item.path);
      link.target = "_blank";
      link.rel = "noreferrer";
      const isDownload = ["trace", "log", "attachment"].includes(item.type);
      if (isDownload) link.setAttribute("download", item.name);
      link.append(icon(item.type === "trace" ? "archive" : item.type === "report" ? "external" : "download", 14));
      const copy = element("span");
      copy.append(element("b", EVIDENCE_TYPE_LABELS[item.type] || "文件"), element("small", `${item.name} · ${formatBytes(item.size)}`));
      link.append(copy, icon(isDownload ? "download" : "external", 13));
      links.append(link);
    }
    group.append(title, links);
    body.append(group);
  }
  if (!flow.evidence.length) body.append(element("p", "本次流程没有生成可展示的证据文件。", "evidence-empty"));

  modal.append(header, body);
  backdrop.append(modal);
  document.body.append(backdrop);
  document.body.style.overflow = "hidden";
  close.focus();

  function closeModal() {
    window.removeEventListener("keydown", onKeyDown, true);
    backdrop.remove();
    document.body.style.overflow = "";
    if (returnFocus instanceof HTMLElement) returnFocus.focus();
  }
  function onKeyDown(event) {
    if (event.key === "Escape") {
      event.stopPropagation();
      closeModal();
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = [...modal.querySelectorAll('button, a[href], video[controls], [tabindex]:not([tabindex="-1"])')]
      .filter((node) => !node.hasAttribute("disabled"));
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
  window.addEventListener("keydown", onKeyDown, true);
  backdrop.addEventListener("mousedown", (event) => {
    if (event.target === backdrop) closeModal();
  });
  close.addEventListener("click", closeModal);
}

/* ---------- 数据加载 ---------- */
async function refreshFlows() {
  const payload = await api("/api/flows");
  state.payload = payload;
  const records = payload.flows || [];
  if (!records.some((record) => flowKey(record) === state.activeKey)) {
    state.activeKey = records.length ? flowKey(records[0]) : null;
  }
  const projectName = String(payload.project || "").split("/").filter(Boolean).pop() || "当前项目";
  $("#project-summary").textContent = `${projectName} · ${payload.validFlowCount} 条结构有效，${payload.invalidFlowCount} 条需处理`;
  renderCatalog();
  renderDetail();
}

async function refreshRuns() {
  const payload = await api("/api/runs");
  state.runs = payload.runs || [];
  if (!state.runs.some((run) => run.id === state.currentRunId)) {
    state.currentRunId = state.runs[0]?.id || null;
  }
  renderRunList();
  renderRunDetail();
}

/* ---------- 抽离报告（既有逻辑，保持不动） ---------- */
function reportError(message) {
  const detail = $("#report-detail"); detail.replaceChildren(element("p", message, "error-box"));
}

function listText(items, map = (value) => value) {
  const list = element("ul", undefined, "inline-list");
  for (const item of items || []) list.append(element("li", map(item), "badge"));
  return list;
}

function renderReport(report) {
  const target = $("#report-detail"); target.replaceChildren();
  const header = element("header", undefined, "report-header");
  header.append(element("p", report.id, "eyebrow"), element("h2", "抽离报告"), element("p", `${report.createdAt} · ${report.approvalMode} · ${report.validation.level}/${report.validation.status}`, "muted"));
  header.append(listText(report.scenarios, (scenario) => scenarioLabels[scenario] || scenario)); target.append(header);
  const summary = element("div", undefined, "report-grid");
  summary.append(metric(report.summary.createdFlowCount, "创建"), metric(report.summary.semanticUpdatedFlowCount, "语义更新"), metric(report.summary.provenanceUpdatedFlowCount, "仅更新溯源"), metric(report.summary.retiredFlowCount ?? 0, "下线"), metric(report.summary.readyFlowCount, "ready"), metric(report.summary.draftFlowCount, "draft"), metric(report.summary.blockedFlowCount, "阻塞")); target.append(summary);

  const changes = element("section", undefined, "detail-section"); changes.append(element("h3", "流程变更"));
  if (!report.flowChanges.length) changes.append(element("p", "本次没有写入或更新流程。", "empty"));
  for (const change of report.flowChanges) {
    const row = element("details", undefined, "change");
    const title = element("summary", `${change.flowId} · ${operationLabels[change.operation] || change.operation}`); row.append(title);
    const before = change.lifecycle.before ? `${change.lifecycle.before.status} / ${change.lifecycle.before.enabled ? "enabled" : "disabled"}` : "新流程";
    const after = `${change.lifecycle.after.status} / ${change.lifecycle.after.enabled ? "enabled" : "disabled"}`;
    row.append(element("p", `${change.flow.persona} 要 ${change.flow.goal}`), element("p", `入口：${change.flow.entryUrl}；成功信号：${change.flow.successSignal}`, "muted"), element("p", `生命周期：${before} → ${after}`, "muted"), element("p", `下一步：${change.nextAction}`, "muted"));
    const evidence = element("ul", undefined, "evidence");
    for (const item of change.evidence) { const range = item.lineStart ? `:${item.lineStart}${item.lineEnd ? `-${item.lineEnd}` : ""}` : ""; evidence.append(element("li", `${item.path}${range} — ${item.reason}`)); }
    row.append(evidence); changes.append(row);
  }
  target.append(changes);

  const uncertainty = element("section", undefined, "detail-section"); uncertainty.append(element("h3", "覆盖与存疑"));
  for (const item of report.coverage.uncovered || []) uncertainty.append(element("p", `未覆盖：${item.area} — ${item.reason}`, "warning"));
  for (const item of report.uncertainties || []) uncertainty.append(element("p", `${item.severity}：${item.summary}；需要：${item.question}`, item.severity === "blocking" ? "error-box" : "warning"));
  if (!(report.coverage.uncovered || []).length && !(report.uncertainties || []).length) uncertainty.append(element("p", "没有记录未覆盖区域或存疑项。", "muted"));
  target.append(uncertainty);

  const handoff = element("section", undefined, "detail-section"); handoff.append(element("h3", "移交③ e2e-test-gen"));
  handoff.append(element("p", report.handoff.e2eTestGen.readyFlowIds.length ? `可移交：${report.handoff.e2eTestGen.readyFlowIds.join("、")}` : "本次没有可交给测试生成的流程。", report.handoff.e2eTestGen.readyFlowIds.length ? "" : "warning"));
  for (const blocked of report.handoff.e2eTestGen.blockedFlows) handoff.append(element("p", `${blocked.flowId}：${blocked.reason}`, "muted"));
  target.append(handoff);
}

async function renderReports() {
  const payload = await api("/api/extraction-reports");
  const list = $("#report-list"); list.replaceChildren();
  if (!payload.reports.length) { list.append(element("p", "尚无抽离报告。由①完成抽离后会写入不可变 JSON 快照。", "empty")); return; }
  const params = new URLSearchParams(location.search); const requested = params.get("report");
  const valid = payload.reports.filter((report) => report.valid);
  for (const report of payload.reports) {
    if (!report.valid) { list.append(element("p", `${report.filename}：${report.errors.join("；")}`, "error-box")); continue; }
    const button = element("button", undefined, "report-button"); button.type = "button"; button.dataset.id = report.id; button.append(element("strong", report.id), element("span", report.scenarios.map((item) => scenarioLabels[item] || item).join(" · ")), element("span", `${report.createdAt} · 阻塞 ${report.summary.blockedFlowCount}`));
    button.addEventListener("click", () => selectReport(report.id)); list.append(button);
  }
  const selection = valid.find((report) => report.id === requested) || valid[0];
  if (selection) await selectReport(selection.id);
}

async function selectReport(reportId) {
  document.querySelectorAll(".report-button").forEach((button) => button.setAttribute("aria-current", String(button.dataset.id === reportId)));
  try { renderReport(await api(`/api/extraction-reports/${encodeURIComponent(reportId)}`)); } catch (error) { reportError(error.message); }
}

/* ---------- 视图切换与入口 ---------- */
function setView(view) {
  const reports = view === "reports";
  $("#board-tab").setAttribute("aria-selected", String(!reports));
  $("#reports-tab").setAttribute("aria-selected", String(reports));
  $("#board-view").hidden = reports;
  $("#reports-view").hidden = !reports;
}

async function refreshAll() {
  const button = $("#refresh-button");
  button.classList.add("spin");
  try {
    await Promise.all([refreshFlows(), refreshRuns()]);
  } catch (error) {
    showError(error.message);
  } finally {
    button.classList.remove("spin");
  }
}

async function init() {
  $("#board-tab").addEventListener("click", () => setView("board"));
  $("#reports-tab").addEventListener("click", () => setView("reports"));
  $("#refresh-button").addEventListener("click", refreshAll);
  $("#error-close").addEventListener("click", () => { $("#error-banner").hidden = true; });
  $("#flow-search").addEventListener("input", (event) => {
    state.query = event.target.value;
    renderCatalog();
  });
  try {
    await refreshAll();
    if (location.pathname === "/reports/extraction") setView("reports");
    await renderReports();
  } catch (error) {
    $("#project-summary").textContent = `无法读取看板数据：${error.message}`;
    showError(error.message);
  }
}

init();
