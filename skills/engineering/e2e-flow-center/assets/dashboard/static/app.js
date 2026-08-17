const $ = (selector) => document.querySelector(selector);
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

function element(name, text, className) {
  const node = document.createElement(name);
  if (text !== undefined && text !== null) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function badge(text, kind = "") { return element("span", text, `badge ${kind}`.trim()); }

function metric(value, label) {
  const node = element("div", undefined, "metric");
  node.append(element("strong", String(value)), element("span", label));
  return node;
}

function setTab(view) {
  const reports = view === "reports";
  $("#flows-tab").setAttribute("aria-selected", String(!reports));
  $("#reports-tab").setAttribute("aria-selected", String(reports));
  $("#flows-panel").hidden = reports;
  $("#reports-panel").hidden = !reports;
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

function renderFlows(payload) {
  const summary = $("#flow-summary");
  summary.replaceChildren();
  const executable = payload.flows.filter(({ flow, valid }) => valid && flow?.status === "active" && flow?.enabled).length;
  summary.append(metric(payload.validFlowCount, "结构有效"), metric(payload.invalidFlowCount, "需要处理"), metric(executable, "可执行流程"), metric(payload.flows.length, "流程总数"));
  const list = $("#flow-list");
  list.replaceChildren();
  if (!payload.flows.length) {
    list.append(element("p", "没有发现 .yaml 流程文件；请先由①抽离业务流程。", "empty"));
    return;
  }
  for (const record of payload.flows) {
    const flow = record.flow || {};
    const card = element("article", undefined, "flow-card");
    const top = element("div", undefined, "flow-top");
    const heading = element("div");
    heading.append(element("h3", flow.name || record.path), element("p", flow.id || record.path, "muted"));
    const states = element("div", undefined, "flow-meta");
    states.append(badge(record.valid ? "结构有效" : "结构有误", record.valid ? "ok" : "error"));
    if (flow.status) states.append(badge(flow.status, "accent"));
    if (typeof flow.enabled === "boolean") states.append(badge(flow.enabled ? "已启用" : "未启用", flow.enabled ? "ok" : ""));
    top.append(heading, states); card.append(top);
    if (flow.persona && flow.goal) card.append(element("p", `${flow.persona}：${flow.goal}`));
    const meta = element("div", undefined, "flow-meta");
    if (flow.category) meta.append(element("span", flow.category));
    if (Array.isArray(flow.sources)) meta.append(element("span", `来源 ${flow.sources.length} 项`));
    if (Array.isArray(flow.paths)) meta.append(element("span", `影响路径 ${flow.paths.length} 项`));
    card.append(meta);
    if (record.issues.length) {
      const issues = element("ul", undefined, "issues");
      for (const issue of record.issues) { const row = element("li"); row.append(element("span", `${issue.field}：`, "issue-field"), document.createTextNode(issue.message)); issues.append(row); }
      card.append(issues);
    }
    list.append(card);
  }
}

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

async function init() {
  $("#flows-tab").addEventListener("click", () => setTab("flows"));
  $("#reports-tab").addEventListener("click", () => setTab("reports"));
  try {
    const [health, flows] = await Promise.all([api("/api/health"), api("/api/flows")]);
    $("#project-summary").textContent = `${health.projectName} · ${health.validFlowCount} 条结构有效流程，${health.invalidFlowCount} 条需要处理`;
    renderFlows(flows);
    if (location.pathname === "/reports/extraction") setTab("reports");
    await renderReports();
  } catch (error) { $("#project-summary").textContent = `无法读取看板数据：${error.message}`; $("#flow-list").replaceChildren(element("p", error.message, "error-box")); }
}

init();
