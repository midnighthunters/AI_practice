// State management
let currentWorkflowId = "01_gemini_http_request";
let executionData = null;
let selectedNodeIndex = 0;
let activeDrawerTab = "params";

const WORKFLOW_CONFIGS = {
  "01_gemini_http_request": {
    title: "01: Gemini Flash Direct cURL / HTTP",
    defaultInput: "Explain how AI works in a few words",
    presets: [
      { label: "AI in a few words", text: "Explain how AI works in a few words" },
      { label: "API Explanation", text: "Summarize what an API is in 2 sentences" },
      { label: "Haiku on n8n", text: "Write a haiku about n8n workflow automation" }
    ],
    nodes: [
      { name: "Webhook Trigger", type: "n8n-nodes-base.webhook", icon: "fa-bolt", color: "orange" },
      { name: "Prepare Payload", type: "n8n-nodes-base.set", icon: "fa-sliders", color: "blue" },
      { name: "HTTP Request - Gemini API", type: "n8n-nodes-base.httpRequest", icon: "fa-globe", color: "purple" },
      { name: "Format Gemini Response", type: "n8n-nodes-base.code", icon: "fa-code", color: "emerald" },
      { name: "Respond to Webhook", type: "n8n-nodes-base.respondToWebhook", icon: "fa-reply", color: "slate" }
    ]
  },
  "02_smart_customer_triage": {
    title: "02: Support Ticket Triage & Routing",
    defaultInput: "I demand a full refund! My server went down during our Black Friday sale and we lost thousands of dollars. Nobody is answering your phones!",
    presets: [
      { label: "Outage & Refund (Urgent)", text: "I demand a full refund! My server went down during our Black Friday sale and we lost thousands of dollars. Nobody is answering your phones!" },
      { label: "Billing Invoice (Normal)", text: "Hi team, could you please send me a PDF copy of our October invoice for tax purposes?" },
      { label: "Feature Request", text: "Would love to see dark mode added to the mobile application settings." }
    ],
    nodes: [
      { name: "Incoming Support Ticket", type: "n8n-nodes-base.webhook", icon: "fa-envelope", color: "orange" },
      { name: "Extract Ticket Data", type: "n8n-nodes-base.set", icon: "fa-sliders", color: "blue" },
      { name: "Gemini Classification", type: "n8n-nodes-base.httpRequest", icon: "fa-brain", color: "purple" },
      { name: "Parse Structured JSON", type: "n8n-nodes-base.code", icon: "fa-code", color: "emerald" },
      { name: "Check Priority", type: "n8n-nodes-base.switch", icon: "fa-code-branch", color: "amber" },
      { name: "Routing Action", type: "n8n-nodes-base.set", icon: "fa-bell", color: "rose" }
    ]
  },
  "03_n8n_rag_pipeline": {
    title: "03: Enterprise RAG Knowledge Base in n8n",
    defaultInput: "What is the launch date for Project NovaStar?",
    presets: [
      { label: "Project NovaStar", text: "What is the launch date for Project NovaStar?" },
      { label: "Wi-Fi & Wellness", text: "What is the internal office Wi-Fi password and wellness stipend?" },
      { label: "Refund Policy", text: "What is the refund policy for software licenses and hardware?" },
      { label: "CEO Allergies", text: "Who is the CEO and what is his allergy and favorite dessert?" }
    ],
    nodes: [
      { name: "User Question Webhook", type: "n8n-nodes-base.webhook", icon: "fa-bolt", color: "orange" },
      { name: "Vector Store & Retrieval", type: "n8n-nodes-base.code", icon: "fa-database", color: "blue" },
      { name: "Prompt Augmentation", type: "n8n-nodes-base.code", icon: "fa-puzzle-piece", color: "purple" },
      { name: "Gemini RAG Generation", type: "n8n-nodes-base.httpRequest", icon: "fa-brain", color: "emerald" },
      { name: "Synthesize RAG Response", type: "n8n-nodes-base.code", icon: "fa-file-lines", color: "teal" }
    ]
  },
  "04_gemini_ai_agent_tools": {
    title: "04: Gemini AI Agent with Tools & Memory",
    defaultInput: "Check tracking status for order ORD-102 and calculate a 15% discount on $420",
    presets: [
      { label: "Order ORD-102 + 15% Discount", text: "Check tracking status for order ORD-102 and calculate a 15% discount on $420" },
      { label: "Order ORD-101 Lookup", text: "What is the delivery carrier and status for order ORD-101?" },
      { label: "Math Calculation", text: "Calculate 25 * 18 + 150" }
    ],
    nodes: [
      { name: "When chat message received", type: "@n8n/chatTrigger", icon: "fa-comments", color: "orange" },
      { name: "AI Agent (ReAct / Tools)", type: "@n8n/agent", icon: "fa-robot", color: "purple" },
      { name: "Google Gemini Chat Model", type: "@n8n/lmChatGoogleGemini", icon: "fa-microchip", color: "emerald" },
      { name: "Calculator Tool", type: "@n8n/toolCalculator", icon: "fa-calculator", color: "blue" },
      { name: "Order Tracking DB Tool", type: "@n8n/toolCode", icon: "fa-box", color: "amber" }
    ]
  }
};

// DOM Elements
const workflowSelect = document.getElementById("workflowSelect");
const workflowInput = document.getElementById("workflowInput");
const presetChipsContainer = document.getElementById("presetChipsContainer");
const btnExecute = document.getElementById("btnExecute");
const nodePipeline = document.getElementById("nodePipeline");
const btnDownloadJson = document.getElementById("btnDownloadJson");

// Drawer Elements
const drawerNodeName = document.getElementById("drawerNodeName");
const drawerNodeType = document.getElementById("drawerNodeType");
const drawerNodeIcon = document.getElementById("drawerNodeIcon");
const drawerNodeTime = document.getElementById("drawerNodeTime");
const tabInput = document.getElementById("tabInput");
const tabParams = document.getElementById("tabParams");
const tabOutput = document.getElementById("tabOutput");
const contentInput = document.getElementById("contentInput");
const contentParams = document.getElementById("contentParams");
const contentOutput = document.getElementById("contentOutput");
const jsonInput = document.getElementById("jsonInput");
const jsonOutput = document.getElementById("jsonOutput");
const paramsContainer = document.getElementById("paramsContainer");
const badgeInputCount = document.getElementById("badgeInputCount");
const badgeOutputCount = document.getElementById("badgeOutputCount");
const btnCopyJson = document.getElementById("btnCopyJson");

// Summary Panel Elements
const execLatencyBadge = document.getElementById("execLatencyBadge");
const execStatusBadge = document.getElementById("execStatusBadge");
const panelResult = document.getElementById("panelResult");
const panelCurl = document.getElementById("panelCurl");
const tabBtnResult = document.getElementById("tabBtnResult");
const tabBtnCurl = document.getElementById("tabBtnCurl");
const curlSnippet = document.getElementById("curlSnippet");

// Initialize
function init() {
  workflowSelect.addEventListener("change", onWorkflowChange);
  btnExecute.addEventListener("click", executeWorkflow);
  workflowInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") executeWorkflow();
  });
  btnDownloadJson.addEventListener("click", downloadCurrentWorkflow);

  // Drawer Tabs
  tabInput.addEventListener("click", () => switchDrawerTab("input"));
  tabParams.addEventListener("click", () => switchDrawerTab("params"));
  tabOutput.addEventListener("click", () => switchDrawerTab("output"));

  // Bottom Summary Tabs
  tabBtnResult.addEventListener("click", () => switchSummaryTab("result"));
  tabBtnCurl.addEventListener("click", () => switchSummaryTab("curl"));

  btnCopyJson.addEventListener("click", copyCurrentOutput);

  // Render Initial Workflow
  renderWorkflowUI(currentWorkflowId);
}

function onWorkflowChange(e) {
  currentWorkflowId = e.target.value;
  executionData = null;
  renderWorkflowUI(currentWorkflowId);
}

function renderWorkflowUI(wfId) {
  const config = WORKFLOW_CONFIGS[wfId];
  if (!config) return;

  // Set default input
  workflowInput.value = config.defaultInput;

  // Render Preset Chips
  presetChipsContainer.innerHTML = "";
  config.presets.forEach(p => {
    const btn = document.createElement("button");
    btn.className = "text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-2.5 py-1 rounded-md border border-slate-700/80 transition-all whitespace-nowrap cursor-pointer";
    btn.innerText = p.label;
    btn.addEventListener("click", () => {
      workflowInput.value = p.text;
      executeWorkflow();
    });
    presetChipsContainer.appendChild(btn);
  });

  // Render Nodes
  renderCanvasNodes(config.nodes);

  // Update Curl Snippet
  updateCurlSnippet();

  // Reset Inspector
  selectedNodeIndex = 0;
  updateInspector();

  // Reset execution indicators
  execLatencyBadge.innerText = "0ms";
  execStatusBadge.innerText = "Ready";
  execStatusBadge.className = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-mono font-medium";
  panelResult.innerHTML = `<div class="text-slate-500 italic">Click "Execute Workflow" above to run this pipeline with Google Gemini!</div>`;
}

function renderCanvasNodes(nodes) {
  nodePipeline.innerHTML = "";

  nodes.forEach((node, idx) => {
    // Node Card
    const nodeEl = document.createElement("div");
    nodeEl.className = `n8n-node p-3.5 ${idx === selectedNodeIndex ? "selected" : ""}`;
    nodeEl.id = `node-${idx}`;
    nodeEl.onclick = () => selectNode(idx);

    nodeEl.innerHTML = `
      <div class="node-handle node-handle-left"></div>
      <div class="node-handle node-handle-right"></div>
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-${node.color}-500/20 border border-${node.color}-500/40 text-${node.color}-400 flex items-center justify-center text-sm shrink-0">
          <i class="fa-solid ${node.icon}"></i>
        </div>
        <div class="overflow-hidden flex-1">
          <div class="font-bold text-xs text-white truncate">${node.name}</div>
          <div class="text-[10px] font-mono text-slate-400 truncate">${node.type}</div>
        </div>
      </div>
      <div class="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
        <span class="node-status text-slate-500 font-mono flex items-center space-x-1">
          <span class="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
          <span>IDLE</span>
        </span>
        <span class="node-time font-mono text-slate-400">--</span>
      </div>
    `;

    nodePipeline.appendChild(nodeEl);

    // Connector Line (if not last)
    if (idx < nodes.length - 1) {
      const connector = document.createElement("div");
      connector.className = "connector-line hidden sm:flex";
      connector.id = `connector-${idx}`;
      nodePipeline.appendChild(connector);
    }
  });
}

function selectNode(idx) {
  selectedNodeIndex = idx;
  document.querySelectorAll(".n8n-node").forEach((el, i) => {
    if (i === idx) el.classList.add("selected");
    else el.classList.remove("selected");
  });
  updateInspector();
}

function updateInspector() {
  const config = WORKFLOW_CONFIGS[currentWorkflowId];
  if (!config) return;

  const node = config.nodes[selectedNodeIndex];
  if (!node) return;

  drawerNodeName.innerText = node.name;
  drawerNodeType.innerText = node.type;
  drawerNodeIcon.innerHTML = `<i class="fa-solid ${node.icon}"></i>`;

  if (executionData && executionData.steps && executionData.steps[selectedNodeIndex]) {
    const step = executionData.steps[selectedNodeIndex];
    drawerNodeTime.innerText = `${step.execution_time_ms}ms`;

    // Input Tab
    const inItems = step.input || [];
    badgeInputCount.innerText = `[${inItems.length}]`;
    jsonInput.innerText = JSON.stringify(inItems, null, 2);

    // Output Tab
    const outItems = step.output || [];
    badgeOutputCount.innerText = `[${outItems.length}]`;
    jsonOutput.innerText = JSON.stringify(outItems, null, 2);

    // Params Tab
    renderParamsUI(step.parameters);
  } else {
    drawerNodeTime.innerText = `0ms`;
    badgeInputCount.innerText = `[0]`;
    badgeOutputCount.innerText = `[0]`;
    jsonInput.innerText = `[\n  // Waiting for execution run\n]`;
    jsonOutput.innerText = `[\n  // Waiting for execution run\n]`;
    renderParamsUI({
      status: "Configured",
      nodeType: node.type,
      model: "gemini-flash-latest",
      note: "Click 'Execute Workflow' to see live runtime parameter bindings."
    });
  }
}

function renderParamsUI(params) {
  paramsContainer.innerHTML = "";
  if (!params) return;

  for (const [key, value] of Object.entries(params)) {
    const row = document.createElement("div");
    row.className = "bg-slate-950 p-2.5 rounded border border-slate-800";

    const label = document.createElement("div");
    label.className = "text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1";
    label.innerText = key;

    const valEl = document.createElement("div");
    valEl.className = "text-xs font-mono text-slate-200 overflow-x-auto";

    if (typeof value === "object") {
      valEl.innerHTML = `<pre class="text-amber-300 text-[11px]">${JSON.stringify(value, null, 2)}</pre>`;
    } else {
      valEl.innerText = String(value);
    }

    row.appendChild(label);
    row.appendChild(valEl);
    paramsContainer.appendChild(row);
  }
}

async function executeWorkflow() {
  const inputVal = workflowInput.value.trim();
  btnExecute.disabled = true;
  btnExecute.classList.add("opacity-70");
  btnExecute.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-xs"></i><span>Executing...</span>`;

  execStatusBadge.innerText = "Running...";
  execStatusBadge.className = "bg-sky-500/10 text-sky-400 border border-sky-500/30 px-2 py-0.5 rounded font-mono font-medium animate-pulse";

  // Reset node UI states
  const config = WORKFLOW_CONFIGS[currentWorkflowId];
  config.nodes.forEach((_, idx) => {
    const nodeEl = document.getElementById(`node-${idx}`);
    if (nodeEl) {
      nodeEl.classList.remove("success", "running");
      const statusEl = nodeEl.querySelector(".node-status");
      if (statusEl) statusEl.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-slate-600"></span><span>WAITING</span>`;
      const timeEl = nodeEl.querySelector(".node-time");
      if (timeEl) timeEl.innerText = "--";
    }
    const connEl = document.getElementById(`connector-${idx}`);
    if (connEl) connEl.classList.remove("active");
  });

  try {
    const resp = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        workflow_id: currentWorkflowId,
        input: inputVal
      })
    });

    const data = await resp.json();
    executionData = data;

    // Animate execution sequentially
    const steps = data.steps || [];
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      const nodeEl = document.getElementById(`node-${i}`);
      const connEl = document.getElementById(`connector-${i - 1}`);

      if (connEl) connEl.classList.add("active");

      if (nodeEl) {
        nodeEl.classList.add("running");
        const statusEl = nodeEl.querySelector(".node-status");
        if (statusEl) statusEl.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse"></span><span class="text-sky-400">RUNNING</span>`;
      }

      // Small delay for animation visual feel
      await new Promise(r => setTimeout(r, Math.min(step.execution_time_ms, 250)));

      if (nodeEl) {
        nodeEl.classList.remove("running");
        nodeEl.classList.add("success");
        const statusEl = nodeEl.querySelector(".node-status");
        if (statusEl) statusEl.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span><span class="text-emerald-400">SUCCESS</span>`;
        const timeEl = nodeEl.querySelector(".node-time");
        if (timeEl) timeEl.innerText = `${step.execution_time_ms}ms`;
      }
    }

    // Select the last node by default or preserve selection
    updateInspector();

    // Update Bottom Summary
    execLatencyBadge.innerText = `${data.total_latency_ms}ms`;
    execStatusBadge.innerText = "Completed (200 OK)";
    execStatusBadge.className = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-mono font-medium";

    // Format Final Result Output
    renderFinalResult(data.final_result);
    updateCurlSnippet();

  } catch (err) {
    console.error(err);
    execStatusBadge.innerText = "Error";
    execStatusBadge.className = "bg-rose-500/10 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded font-mono font-medium";
    panelResult.innerHTML = `<div class="text-rose-400">Execution failed: ${err.message}</div>`;
  } finally {
    btnExecute.disabled = false;
    btnExecute.classList.remove("opacity-70");
    btnExecute.innerHTML = `<i class="fa-solid fa-play text-xs"></i><span>Execute Workflow</span>`;
  }
}

function renderFinalResult(res) {
  if (!res) {
    panelResult.innerHTML = `<div class="text-slate-500">No output returned.</div>`;
    return;
  }

  let html = `<div class="space-y-3">`;

  // If text answer exists (like RAG or Direct Gemini or AI Agent)
  if (res.answer || res.generatedText || res.output) {
    const text = res.answer || res.generatedText || res.output;
    html += `
      <div class="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
        <div class="text-orange-400 font-semibold mb-1.5 flex items-center space-x-1.5">
          <i class="fa-solid fa-sparkles"></i>
          <span>Gemini Generated Output:</span>
        </div>
        <div class="text-slate-100 text-sm font-sans whitespace-pre-wrap leading-relaxed">${text}</div>
      </div>
    `;
  }

  // If support analysis exists (Workflow 2)
  if (res.analysis) {
    const a = res.analysis;
    const urgencyColor = res.isUrgent ? "rose" : "emerald";
    html += `
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-2">
        <div class="bg-slate-950 p-2 rounded border border-slate-800">
          <span class="text-slate-500 text-[10px] block">CATEGORY</span>
          <span class="text-amber-400 font-bold">${a.category || "GENERAL"}</span>
        </div>
        <div class="bg-slate-950 p-2 rounded border border-slate-800">
          <span class="text-slate-500 text-[10px] block">URGENCY</span>
          <span class="text-${urgencyColor}-400 font-bold">${a.urgency || "NORMAL"}</span>
        </div>
        <div class="bg-slate-950 p-2 rounded border border-slate-800">
          <span class="text-slate-500 text-[10px] block">SENTIMENT</span>
          <span class="text-sky-400 font-bold">${a.sentiment || "NEUTRAL"}</span>
        </div>
        <div class="bg-slate-950 p-2 rounded border border-slate-800">
          <span class="text-slate-500 text-[10px] block">ROUTED TARGET</span>
          <span class="text-emerald-400 font-bold">${res.targetChannel || "Default"}</span>
        </div>
      </div>
    `;
  }

  // If RAG documents were retrieved
  if (res.retrievedDocuments && res.retrievedDocuments.length > 0) {
    html += `
      <div class="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
        <div class="text-slate-400 font-semibold text-[11px] mb-2 flex items-center space-x-1.5">
          <i class="fa-solid fa-book-bookmark text-blue-400"></i>
          <span>Verified Context Chunks Grounded into Prompt:</span>
        </div>
        <div class="space-y-1.5">
          ${res.retrievedDocuments.map((d, i) => `
            <div class="text-xs bg-slate-900 p-2 rounded border border-slate-800">
              <span class="font-bold text-slate-300">[Chunk ${i+1}]: ${d.title}</span>
              <p class="text-slate-400 font-sans mt-0.5 text-[11px]">${d.excerpt}</p>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  // Full Raw JSON preview toggle
  html += `
    <details class="text-[11px] text-slate-500 cursor-pointer">
      <summary class="hover:text-slate-300 select-none">View complete JSON payload</summary>
      <pre class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-slate-300 mt-2 overflow-x-auto whitespace-pre-wrap">${JSON.stringify(res, null, 2)}</pre>
    </details>
  </div>`;

  panelResult.innerHTML = html;
}

function updateCurlSnippet() {
  const inputVal = workflowInput.value.trim() || "Explain how AI works in a few words";
  const snippet = `curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \\
  -H 'Content-Type: application/json' \\
  -H 'X-goog-api-key: $GEMINI_API_KEY' \\
  -X POST \\
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": ${JSON.stringify(inputVal)}
          }
        ]
      }
    ]
  }'`;
  curlSnippet.innerText = snippet;
}

function switchDrawerTab(tab) {
  activeDrawerTab = tab;
  [tabInput, tabParams, tabOutput].forEach(t => {
    t.classList.remove("text-orange-400", "border-orange-500");
    t.classList.add("text-slate-400", "border-transparent");
  });
  [contentInput, contentParams, contentOutput].forEach(c => c.classList.add("hidden"));

  if (tab === "input") {
    tabInput.classList.add("text-orange-400", "border-orange-500");
    tabInput.classList.remove("text-slate-400", "border-transparent");
    contentInput.classList.remove("hidden");
  } else if (tab === "params") {
    tabParams.classList.add("text-orange-400", "border-orange-500");
    tabParams.classList.remove("text-slate-400", "border-transparent");
    contentParams.classList.remove("hidden");
  } else if (tab === "output") {
    tabOutput.classList.add("text-orange-400", "border-orange-500");
    tabOutput.classList.remove("text-slate-400", "border-transparent");
    contentOutput.classList.remove("hidden");
  }
}

function switchSummaryTab(tab) {
  if (tab === "result") {
    tabBtnResult.className = "text-xs px-2.5 py-1 rounded bg-orange-500/20 text-orange-400 font-medium border border-orange-500/40";
    tabBtnCurl.className = "text-xs px-2.5 py-1 rounded text-slate-400 hover:text-slate-200 font-medium";
    panelResult.classList.remove("hidden");
    panelCurl.classList.add("hidden");
  } else {
    tabBtnCurl.className = "text-xs px-2.5 py-1 rounded bg-orange-500/20 text-orange-400 font-medium border border-orange-500/40";
    tabBtnResult.className = "text-xs px-2.5 py-1 rounded text-slate-400 hover:text-slate-200 font-medium";
    panelCurl.classList.remove("hidden");
    panelResult.classList.add("hidden");
  }
}

function copyCurrentOutput() {
  const text = jsonOutput.innerText;
  navigator.clipboard.writeText(text).then(() => {
    const orig = btnCopyJson.innerHTML;
    btnCopyJson.innerHTML = `<i class="fa-solid fa-check text-emerald-400 mr-1"></i>Copied!`;
    setTimeout(() => { btnCopyJson.innerHTML = orig; }, 1800);
  });
}

function downloadCurrentWorkflow() {
  const filename = `${currentWorkflowId}.json`;
  window.location.href = `/api/workflow-download/${filename}`;
}

// Kickoff
document.addEventListener("DOMContentLoaded", init);
