const state = {
  summary: null,
  selectedPath: null,
};

const statusClass = (status) => {
  if (!status) return "neutral";
  if (status === "proof_succeeded" || status === "schema_valid" || status === "succeeded" || status === "passed") {
    return "ok";
  }
  if (status.includes("failed") || status.includes("invalid") || status === "unreadable") {
    return "danger";
  }
  if (status === "running" || status === "queued") return "warn";
  return "neutral";
};

const el = (id) => document.getElementById(id);

function badge(status) {
  const label = status || "not run";
  return `<span class="badge ${statusClass(label)}">${escapeHtml(label)}</span>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function shortHash(value) {
  if (!value) return "";
  return String(value).replace("sha256:", "").slice(0, 12);
}

async function loadSummary() {
  const response = await fetch("/api/summary");
  state.summary = await response.json();
  if (!state.selectedPath && state.summary.candidates.length) {
    const preferred = state.summary.candidates.find((candidate) => candidate.candidate_id === "AKNSD2TransportZero");
    state.selectedPath = (preferred || state.summary.candidates[0]).path;
    el("inputPath").value = state.selectedPath;
  }
  render();
}

function render() {
  renderToolchain();
  renderCommands();
  renderMetrics();
  renderCandidates();
  renderArtifacts();
  renderQueue();
  renderDetail();
  renderJobLog();
}

function renderToolchain() {
  const summary = state.summary;
  el("toolchain").textContent = `${summary.lean_toolchain} | ${summary.mathlib_revision}`;
}

function renderCommands() {
  const commands = el("commands");
  commands.innerHTML = state.summary.commands
    .map((command) => `<button title="${escapeHtml(command.description)}" data-command="${escapeHtml(command.name)}">${escapeHtml(command.label)}</button>`)
    .join("");
  commands.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => queueCommand(button.dataset.command));
  });
}

function renderMetrics() {
  const counts = state.summary.status_counts || {};
  el("metrics").innerHTML = [
    metric("Candidates", state.summary.candidate_count),
    metric("Artifacts", state.summary.artifact_count),
    metric("Succeeded", counts.proof_succeeded || 0),
    metric("Failed", Object.entries(counts).filter(([key]) => key !== "proof_succeeded").reduce((sum, [, value]) => sum + value, 0)),
  ].join("");
}

function metric(label, value) {
  return `<div class="metric"><span class="eyebrow">${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
}

function renderCandidates() {
  const rows = state.summary.candidates.map((candidate) => {
    const selected = candidate.path === state.selectedPath ? "selected" : "";
    const bounds = candidate.l_bound == null ? "" : `L:${candidate.l_bound} P:${candidate.p_bound}`;
    return `
      <tr class="${selected}" data-path="${escapeHtml(candidate.path)}">
        <td>${badge(candidate.artifact_status || candidate.validation_status)}</td>
        <td><strong>${escapeHtml(candidate.candidate_id)}</strong><div class="path">${escapeHtml(candidate.path)}</div></td>
        <td>${escapeHtml(candidate.source_kind)}</td>
        <td>${escapeHtml((candidate.fields || []).join(", "))}</td>
        <td>${escapeHtml(bounds)}</td>
        <td>${escapeHtml((candidate.claims || []).join(", "))}</td>
      </tr>
    `;
  }).join("");
  el("candidateRows").innerHTML = rows || `<tr><td colspan="6" class="empty">No candidates found.</td></tr>`;
  el("candidateRows").querySelectorAll("tr[data-path]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedPath = row.dataset.path;
      el("inputPath").value = state.selectedPath;
      render();
    });
  });
}

function renderArtifacts() {
  const cards = state.summary.artifacts.map((artifact) => `
    <article class="artifact-card">
      <h3>${escapeHtml(artifact.candidate_id)}</h3>
      <dl>
        <dt>Status</dt><dd>${badge(artifact.status)}</dd>
        <dt>Claims</dt><dd>${escapeHtml(artifact.claim_type || "")}</dd>
        <dt>Theorem</dt><dd>${escapeHtml(artifact.lean_theorem || "")}</dd>
        <dt>Lean hash</dt><dd>${escapeHtml(shortHash(artifact.generated_lean_hash))}</dd>
        <dt>Updated</dt><dd>${escapeHtml(artifact.timestamp_utc || "")}</dd>
      </dl>
    </article>
  `).join("");
  el("artifacts").innerHTML = cards || `<div class="empty">No proof artifacts found.</div>`;
}

function renderQueue() {
  const jobs = state.summary.jobs.slice(0, 8);
  el("queue").innerHTML = jobs.map((job) => `
    <div class="queue-item">
      <strong>${escapeHtml(job.label)} ${badge(job.status)}</strong>
      <small>${escapeHtml(job.input_path || "repository command")}</small>
    </div>
  `).join("") || `<div class="empty">No queued jobs.</div>`;
}

function renderDetail() {
  const candidate = state.summary.candidates.find((item) => item.path === state.selectedPath);
  if (!candidate) {
    el("detail").innerHTML = `<div class="empty">Select a candidate.</div>`;
    return;
  }
  const artifact = state.summary.artifacts.find((item) => item.candidate_id === candidate.candidate_id);
  const witness = artifact?.residual_witness ? JSON.stringify(artifact.residual_witness) : "";
  el("detail").innerHTML = `
    <dl>
      <dt>Candidate</dt><dd>${escapeHtml(candidate.candidate_id)}</dd>
      <dt>Path</dt><dd class="path">${escapeHtml(candidate.path)}</dd>
      <dt>Validation</dt><dd>${badge(candidate.validation_status)}</dd>
      <dt>Proof</dt><dd>${badge(candidate.artifact_status)}</dd>
      <dt>Source</dt><dd>${escapeHtml(candidate.source_kind)}</dd>
      <dt>Version</dt><dd>${escapeHtml(candidate.laxforge_version || "")}</dd>
      <dt>Matrix</dt><dd>${escapeHtml(candidate.matrix_size ? `${candidate.matrix_size}x${candidate.matrix_size}` : "")}</dd>
      <dt>Residual</dt><dd>${escapeHtml(witness)}</dd>
    </dl>
  `;
}

function renderJobLog() {
  const latest = state.summary.jobs[0];
  if (!latest) {
    el("jobLog").textContent = "No jobs queued.";
    return;
  }
  const result = latest.result ? `\n\nresult:\n${JSON.stringify(latest.result, null, 2)}` : "";
  el("jobLog").textContent = `${latest.label} [${latest.status}]\n${latest.log.join("\n")}${result}`;
}

async function queueCommand(command) {
  const spec = state.summary.commands.find((item) => item.name === command);
  const inputPath = spec?.requires_path ? el("inputPath").value.trim() : null;
  const response = await fetch("/api/jobs", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({command, input_path: inputPath}),
  });
  if (!response.ok) {
    const error = await response.json();
    el("jobLog").textContent = error.error || "command failed to queue";
  }
  await loadSummary();
}

el("refreshBtn").addEventListener("click", loadSummary);

loadSummary();
setInterval(loadSummary, 2500);
