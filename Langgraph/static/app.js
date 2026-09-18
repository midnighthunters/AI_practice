/**
 * app.js - LangGraph Interactive Visualizer Controller
 */

let workflows = [];
let activeWorkflow = null;
let currentHitlSessionId = null;

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  try {
    const res = await fetch("/api/workflows");
    const data = await res.json();
    if (data.success) {
      workflows = data.workflows;
      renderWorkflowTabs();
      selectWorkflow(workflows[0].id);
    }
  } catch (err) {
    console.error("Failed to load workflows:", err);
  }

  // Setup static event listeners
  document.getElementById("runWorkflowBtn").addEventListener("click", handleRunWorkflow);
  document.getElementById("resetInputBtn").addEventListener("click", () => {
    if (activeWorkflow) renderInputFields(activeWorkflow);
  });

  document.getElementById("tabFormattedBtn").addEventListener("click", () => switchInspectorTab("formatted"));
  document.getElementById("tabRawBtn").addEventListener("click", () => switchInspectorTab("raw"));

  document.getElementById("hitlApproveBtn").addEventListener("click", () => handleHitlResume("APPROVED"));
  document.getElementById("hitlRejectBtn").addEventListener("click", () => handleHitlResume("REJECTED"));
}

function renderWorkflowTabs() {
  const container = document.getElementById("workflowTabs");
  container.innerHTML = "";

  workflows.forEach((wf, index) => {
    const btn = document.createElement("button");
    btn.id = `tab-${wf.id}`;
    btn.className = "px-3 py-2 rounded-xl text-xs font-semibold text-center border transition flex flex-col items-center justify-center gap-0.5 " +
      (index === 0 
        ? "bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30" 
        : "bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800/50");

    btn.innerHTML = `
      <span class="text-[10px] opacity-75 font-mono">#0${wf.number}</span>
      <span class="truncate w-full text-center">${wf.title.split(" ")[0]}</span>
    `;

    btn.addEventListener("click", () => selectWorkflow(wf.id));
    container.appendChild(btn);
  });
}

function selectWorkflow(workflowId) {
  activeWorkflow = workflows.find(w => w.id === workflowId);
  if (!activeWorkflow) return;

  // Update tab styles
  workflows.forEach(w => {
    const el = document.getElementById(`tab-${w.id}`);
    if (el) {
      if (w.id === workflowId) {
        el.className = "px-3 py-2 rounded-xl text-xs font-semibold text-center border transition flex flex-col items-center justify-center gap-0.5 bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30";
      } else {
        el.className = "px-3 py-2 rounded-xl text-xs font-semibold text-center border transition flex flex-col items-center justify-center gap-0.5 bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800/50";
      }
    }
  });

  // Update Banner Info
  document.getElementById("activeBadge").textContent = `Module #${activeWorkflow.number}`;
  document.getElementById("activeTitle").textContent = activeWorkflow.title;
  document.getElementById("activeDesc").textContent = activeWorkflow.description;

  // Render Visual Graph Topology
  renderGraphTopology(activeWorkflow);

  // Render Input Form
  renderInputFields(activeWorkflow);

  // Reset outputs
  document.getElementById("hitlBanner").classList.add("hidden");
  document.getElementById("stepCounter").textContent = "0 steps executed";
  document.getElementById("stepsTimeline").innerHTML = `
    <div class="text-xs text-slate-500 italic p-3 text-center">
      Click "Run Workflow Live" to trigger execution.
    </div>
  `;
  document.getElementById("inspectorFormatted").innerHTML = `
    <div class="text-xs text-slate-500 italic p-4 text-center">
      Awaiting workflow execution...
    </div>
  `;
  document.getElementById("jsonStatePre").textContent = "{}";
}

function renderGraphTopology(wf) {
  const canvas = document.getElementById("graphCanvas");
  canvas.innerHTML = "";

  // Render nodes as styled cards in a responsive flow
  const nodesWrapper = document.createElement("div");
  nodesWrapper.className = "flex flex-wrap items-center justify-center gap-3 w-full";

  wf.nodes.forEach((nodeName, idx) => {
    const isSpecial = nodeName === "START" || nodeName === "END";
    const nodeCard = document.createElement("div");
    nodeCard.id = `graph-node-${nodeName}`;
    nodeCard.className = `px-3.5 py-2 rounded-xl border text-xs font-mono font-semibold transition-all duration-300 flex items-center gap-2 ${
      isSpecial 
        ? "bg-slate-800/80 border-slate-700 text-slate-300 shadow-sm"
        : "bg-slate-900 border-indigo-500/40 text-indigo-200 shadow-md shadow-indigo-950/50"
    }`;

    let icon = "fa-cube";
    if (nodeName === "START") icon = "fa-play text-emerald-400";
    else if (nodeName === "END") icon = "fa-flag-checkered text-rose-400";
    else if (nodeName.includes("review") || nodeName.includes("critic")) icon = "fa-glasses text-amber-400";
    else if (nodeName.includes("tool")) icon = "fa-wrench text-cyan-400";
    else if (nodeName.includes("supervisor")) icon = "fa-user-tie text-purple-400";

    nodeCard.innerHTML = `<i class="fa-solid ${icon} text-xs"></i> <span>${nodeName}</span>`;
    nodesWrapper.appendChild(nodeCard);

    // Add visual flow arrow between nodes (for simple sequential display)
    if (idx < wf.nodes.length - 1) {
      const arrow = document.createElement("div");
      arrow.className = "text-slate-600 text-xs px-1";
      arrow.innerHTML = `<i class="fa-solid fa-arrow-right"></i>`;
      nodesWrapper.appendChild(arrow);
    }
  });

  canvas.appendChild(nodesWrapper);

  // Add Edge Legend
  const legend = document.createElement("div");
  legend.className = "mt-4 pt-3 border-t border-slate-800/60 w-full flex flex-wrap items-center justify-center gap-4 text-[11px] text-slate-400";
  
  wf.edges.forEach(edge => {
    const badge = document.createElement("span");
    badge.className = "inline-flex items-center gap-1 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800";
    badge.innerHTML = `<span class="text-slate-300">${edge.from}</span> <span class="text-indigo-400">➔</span> <span class="text-slate-300">${edge.to}</span>` + 
      (edge.label ? ` <span class="text-amber-400/90 text-[10px]">(${edge.label})</span>` : "");
    legend.appendChild(badge);
  });

  canvas.appendChild(legend);
}

function renderInputFields(wf) {
  const container = document.getElementById("inputFormContainer");
  container.innerHTML = "";

  Object.entries(wf.default_input).forEach(([key, val]) => {
    const fieldDiv = document.createElement("div");
    fieldDiv.className = "space-y-1.5";

    const label = document.createElement("label");
    label.className = "block text-xs font-mono text-indigo-300 uppercase";
    label.textContent = key.replace("_", " ");

    if (typeof val === "string" && val.length > 50) {
      const textarea = document.createElement("textarea");
      textarea.id = `input-${key}`;
      textarea.rows = 3;
      textarea.value = val;
      textarea.className = "w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition font-mono";
      fieldDiv.appendChild(label);
      fieldDiv.appendChild(textarea);
    } else {
      const input = document.createElement("input");
      input.id = `input-${key}`;
      input.type = "text";
      input.value = val;
      input.className = "w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition font-mono";
      fieldDiv.appendChild(label);
      fieldDiv.appendChild(input);
    }

    container.appendChild(fieldDiv);
  });
}

function gatherInputData() {
  if (!activeWorkflow) return {};
  const data = {};
  Object.keys(activeWorkflow.default_input).forEach(key => {
    const el = document.getElementById(`input-${key}`);
    if (el) data[key] = el.value;
  });
  return data;
}

async function handleRunWorkflow() {
  if (!activeWorkflow) return;

  const runBtn = document.getElementById("runWorkflowBtn");
  const originalHtml = runBtn.innerHTML;
  runBtn.disabled = true;
  runBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i><span>Running Graph...</span>`;

  // Clear previous execution state
  document.querySelectorAll("[id^='graph-node-']").forEach(el => {
    el.classList.remove("node-active", "node-completed");
  });
  document.getElementById("hitlBanner").classList.add("hidden");

  const payload = gatherInputData();

  try {
    const res = await fetch(`/api/run/${activeWorkflow.id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (!result.success) {
      alert("Error: " + (result.error || "Execution failed"));
      return;
    }

    // Workflow 7: Human-in-the-Loop Paused State
    if (activeWorkflow.id === "07_hitl" && result.is_paused) {
      currentHitlSessionId = result.session_id;
      displayHitlBreakpoint(result);
      return;
    }

    // Normal Execution Progression
    displayExecutionResults(result);

  } catch (err) {
    console.error("Run failed:", err);
    alert("Execution error: " + err.message);
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = originalHtml;
  }
}

function displayExecutionResults(result) {
  const stepsTimeline = document.getElementById("stepsTimeline");
  stepsTimeline.innerHTML = "";

  const steps = result.steps || [];
  document.getElementById("stepCounter").textContent = `${steps.length} steps executed`;

  // Animate nodes in graph canvas
  steps.forEach((step, idx) => {
    const nodeEl = document.getElementById(`graph-node-${step.node}`);
    if (nodeEl) {
      setTimeout(() => {
        nodeEl.classList.add("node-completed");
      }, idx * 150);
    }

    const stepCard = document.createElement("div");
    stepCard.className = "p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs space-y-1";
    stepCard.innerHTML = `
      <div class="flex items-center justify-between font-mono">
        <span class="text-indigo-400 font-bold"><i class="fa-solid fa-cube mr-1 text-slate-500"></i> ${step.node}</span>
        <span class="text-[10px] text-slate-500">Step #${idx + 1}</span>
      </div>
      <div class="text-[11px] text-slate-300 font-mono truncate">
        ${JSON.stringify(step.update).slice(0, 100)}...
      </div>
    `;
    stepsTimeline.appendChild(stepCard);
  });

  // Render State Output
  renderStateInspector(result.final_state);
}

function displayHitlBreakpoint(result) {
  const hitlBanner = document.getElementById("hitlBanner");
  const hitlDetails = document.getElementById("hitlDetails");
  const state = result.state_at_breakpoint;

  hitlDetails.innerHTML = `
    <div><strong>Proposed Action:</strong> Wire Transfer</div>
    <div><strong>Recipient:</strong> ${state.recipient}</div>
    <div><strong>Amount:</strong> $${Number(state.amount_usd).toLocaleString()} USD</div>
    <div><strong>Reason:</strong> ${state.reason}</div>
    <div class="text-amber-400 mt-1">Status: ${state.execution_status}</div>
  `;

  hitlBanner.classList.remove("hidden");

  // Highlight active node
  const pausedNode = document.getElementById("graph-node-execute_transfer");
  if (pausedNode) pausedNode.classList.add("node-active");

  renderStateInspector(state);
}

async function handleHitlResume(decision) {
  if (!currentHitlSessionId) return;

  const btnApprove = document.getElementById("hitlApproveBtn");
  const btnReject = document.getElementById("hitlRejectBtn");
  btnApprove.disabled = true;
  btnReject.disabled = true;

  try {
    const res = await fetch("/api/hitl/resume", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: currentHitlSessionId,
        decision: decision
      })
    });
    const result = await res.json();

    if (result.success) {
      document.getElementById("hitlBanner").classList.add("hidden");
      renderStateInspector(result.final_state);

      const pausedNode = document.getElementById("graph-node-execute_transfer");
      if (pausedNode) {
        pausedNode.classList.remove("node-active");
        pausedNode.classList.add("node-completed");
      }
    } else {
      alert("Resume failed: " + result.error);
    }
  } catch (err) {
    console.error(err);
  } finally {
    btnApprove.disabled = false;
    btnReject.disabled = false;
    currentHitlSessionId = null;
  }
}

function renderStateInspector(finalState) {
  // Raw JSON View
  document.getElementById("jsonStatePre").textContent = JSON.stringify(finalState, null, 2);

  // Formatted Cards View
  const container = document.getElementById("inspectorFormatted");
  container.innerHTML = "";

  if (!finalState || typeof finalState !== "object") {
    container.innerHTML = `<div class="text-xs text-slate-500 italic p-3">No state data.</div>`;
    return;
  }

  Object.entries(finalState).forEach(([key, value]) => {
    const card = document.createElement("div");
    card.className = "bg-slate-950/70 border border-slate-800 rounded-xl p-3 space-y-1.5";

    const header = document.createElement("div");
    header.className = "flex items-center justify-between text-xs font-mono font-bold text-indigo-300";
    header.innerHTML = `<span>${key}</span>`;
    card.appendChild(header);

    const body = document.createElement("div");
    body.className = "text-xs text-slate-200 leading-relaxed";

    if (Array.isArray(value)) {
      body.innerHTML = `<ul class="list-disc list-inside space-y-1 font-mono text-[11px] text-slate-300">
        ${value.map(item => `<li>${typeof item === "object" ? JSON.stringify(item) : item}</li>`).join("")}
      </ul>`;
    } else if (typeof value === "object" && value !== null) {
      body.innerHTML = `<pre class="bg-slate-900 p-2 rounded text-[11px] font-mono text-indigo-200 overflow-x-auto">${JSON.stringify(value, null, 2)}</pre>`;
    } else {
      body.innerHTML = `<div class="whitespace-pre-wrap">${value}</div>`;
    }

    card.appendChild(body);
    container.appendChild(card);
  });
}

function switchInspectorTab(tab) {
  const formattedEl = document.getElementById("inspectorFormatted");
  const rawEl = document.getElementById("inspectorRaw");
  const btnFormatted = document.getElementById("tabFormattedBtn");
  const btnRaw = document.getElementById("tabRawBtn");

  if (tab === "formatted") {
    formattedEl.classList.remove("hidden");
    rawEl.classList.add("hidden");
    btnFormatted.className = "px-2.5 py-1 text-xs font-medium rounded-lg bg-indigo-600 text-white transition";
    btnRaw.className = "px-2.5 py-1 text-xs font-medium rounded-lg text-slate-400 hover:text-white transition";
  } else {
    formattedEl.classList.add("hidden");
    rawEl.classList.remove("hidden");
    btnFormatted.className = "px-2.5 py-1 text-xs font-medium rounded-lg text-slate-400 hover:text-white transition";
    btnRaw.className = "px-2.5 py-1 text-xs font-medium rounded-lg bg-indigo-600 text-white transition";
  }
}
