// LangChain Mastery Interactive Frontend Logic

let activeTab = 'models';
let selectedParserType = 'pydantic';
let selectedScript = '01_chat_models_and_prompts.py';
let availableExamples = [];

document.addEventListener('DOMContentLoaded', async () => {
  await loadAppInfo();
  updateToolArgsUI();
});

// TAB SWITCHING
function switchTab(tabId) {
  activeTab = tabId;
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(el => {
    el.classList.remove('active', 'bg-emerald-500/10', 'text-emerald-400');
    el.classList.add('text-slate-400');
  });

  const pane = document.getElementById(`pane-${tabId}`);
  const btn = document.getElementById(`tab-btn-${tabId}`);
  if (pane) pane.classList.remove('hidden');
  if (btn) {
    btn.classList.add('active');
    btn.classList.remove('text-slate-400');
  }
}

// APP INFO & SCRIPT LIST
async function loadAppInfo() {
  try {
    const res = await fetch('/api/info');
    const data = await res.json();
    if (data.success) {
      availableExamples = data.examples || [];
      renderScriptList();
    }
  } catch (err) {
    console.error('Failed to load info:', err);
  }
}

function renderScriptList() {
  const container = document.getElementById('script-list');
  if (!container) return;
  container.innerHTML = availableExamples.map((ex, idx) => `
    <button onclick="selectScript('${ex.name}')" id="script-item-${ex.id}" class="script-btn w-full text-left px-3 py-2 rounded-xl text-xs font-medium border border-slate-800 bg-slate-900/50 hover:bg-slate-800 transition flex items-center justify-between ${idx === 0 ? 'border-yellow-500/50 text-yellow-400' : 'text-slate-300'}">
      <span>${ex.id}. ${ex.title}</span>
      <i class="fa-solid fa-chevron-right text-[10px] text-slate-500"></i>
    </button>
  `).join('');
}

function selectScript(filename) {
  selectedScript = filename;
  document.getElementById('runner-active-script').textContent = filename;
  document.querySelectorAll('.script-btn').forEach(btn => {
    btn.classList.remove('border-yellow-500/50', 'text-yellow-400');
    btn.classList.add('text-slate-300');
  });
  const activeEx = availableExamples.find(e => e.name === filename);
  if (activeEx) {
    const activeEl = document.getElementById(`script-item-${activeEx.id}`);
    if (activeEl) {
      activeEl.classList.add('border-yellow-500/50', 'text-yellow-400');
      activeEl.classList.remove('text-slate-300');
    }
  }
  loadScriptCode(filename);
}

// 1. MODELS & PROMPTS
async function runModelsPrompt() {
  const systemText = document.getElementById('model-system').value.trim();
  const template = document.getElementById('model-template').value.trim();
  const topic = document.getElementById('model-var-topic').value.trim();
  const style = document.getElementById('model-var-style').value.trim();
  const btn = document.getElementById('btn-run-prompt');
  const outBox = document.getElementById('model-output-box');
  const latencyEl = document.getElementById('model-latency');
  const renderedInspector = document.getElementById('model-rendered-inspector');
  const renderedList = document.getElementById('model-rendered-list');

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Invoking Model...';
  outBox.textContent = 'Formatting ChatPromptTemplate and sending to Gemini...';

  try {
    const res = await fetch('/api/demo/prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system: systemText,
        template: template,
        variables: { topic, style }
      })
    });
    const data = await res.json();
    if (data.success) {
      outBox.textContent = data.response;
      latencyEl.textContent = `${data.latency_ms} ms`;
      if (data.rendered_messages) {
        renderedInspector.classList.remove('hidden');
        renderedList.innerHTML = data.rendered_messages.map(m => `
          <div><strong class="text-emerald-300">[${m.role.toUpperCase()}]:</strong> ${m.content}</div>
        `).join('');
      }
    } else {
      outBox.textContent = `Error: ${data.error}`;
    }
  } catch (err) {
    outBox.textContent = `Network error: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Render & Invoke Model';
  }
}

// 2. OUTPUT PARSERS
function selectParser(type) {
  selectedParserType = type;
  const btns = {
    string: document.getElementById('btn-parse-str'),
    json: document.getElementById('btn-parse-json'),
    pydantic: document.getElementById('btn-parse-pyd')
  };
  Object.keys(btns).forEach(k => {
    if (k === type) {
      btns[k].className = 'px-3 py-1 text-xs rounded-md bg-teal-500 text-white font-semibold';
    } else {
      btns[k].className = 'px-3 py-1 text-xs rounded-md text-slate-400 hover:text-white';
    }
  });
  document.getElementById('parser-badge-type').textContent = `Parsed Data (${type.toUpperCase()} Schema)`;
}

async function runParserDemo() {
  const topic = document.getElementById('parser-topic').value.trim();
  const btn = document.getElementById('btn-run-parser');
  const outBox = document.getElementById('parser-output-box');
  const latencyEl = document.getElementById('parser-latency');

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Parsing...';
  outBox.textContent = 'Generating and validating schema...';

  try {
    const res = await fetch('/api/demo/parser', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        parser_type: selectedParserType,
        topic: topic
      })
    });
    const data = await res.json();
    if (data.success) {
      outBox.textContent = typeof data.data === 'object' ? JSON.stringify(data.data, null, 2) : data.data;
      latencyEl.textContent = `${data.latency_ms} ms (${data.parsed_type})`;
    } else {
      outBox.textContent = `Parsing Error: ${data.error}`;
    }
  } catch (err) {
    outBox.textContent = `Network error: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-play"></i> Execute Chain & Parse Output';
  }
}

// 3. LCEL CHAINS
let currentChainMode = 'parallel';
function updateChainMode(mode) {
  currentChainMode = mode;
  const header = document.getElementById('chain-header');
  if (mode === 'parallel') {
    header.textContent = 'Parallel Branches Output (RunnableParallel)';
  } else {
    header.textContent = 'Sequential Pipeline Output (Proposal -> Critique -> Pitch)';
  }
}

async function runChainDemo() {
  const text = document.getElementById('chain-input').value.trim();
  const btn = document.getElementById('btn-run-chain');
  const latencyEl = document.getElementById('chain-latency');

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Executing LCEL Pipeline...';

  try {
    const res = await fetch('/api/demo/chains', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, mode: currentChainMode })
    });
    const data = await res.json();
    if (data.success) {
      latencyEl.textContent = `${data.latency_ms} ms`;
      const grid = document.getElementById('chain-output-grid');
      if (currentChainMode === 'parallel') {
        grid.innerHTML = `
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-800">
            <span class="text-xs font-semibold text-blue-400">Branch 1: Summary</span>
            <p class="mt-1 text-slate-300 text-xs">${data.result.summary}</p>
          </div>
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-800">
            <span class="text-xs font-semibold text-teal-400">Branch 2: Tone & Sentiment</span>
            <p class="mt-1 text-slate-300 text-xs">${data.result.sentiment}</p>
          </div>
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-800">
            <span class="text-xs font-semibold text-purple-400">Branch 3: Technical Keywords</span>
            <p class="mt-1 text-slate-300 text-xs">${data.result.keywords}</p>
          </div>
        `;
      } else {
        grid.innerHTML = `
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-800">
            <span class="text-xs font-semibold text-blue-400">Step 1: Original Proposal</span>
            <p class="mt-1 text-slate-300 text-xs">${data.result.text}</p>
          </div>
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-800">
            <span class="text-xs font-semibold text-amber-400">Step 2: AI Critique</span>
            <p class="mt-1 text-slate-300 text-xs">${data.result.critique}</p>
          </div>
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-800">
            <span class="text-xs font-semibold text-emerald-400">Step 3: Revised Pitch</span>
            <p class="mt-1 text-slate-300 text-xs font-medium">${data.result.revised_pitch}</p>
          </div>
        `;
      }
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-play"></i> Execute LCEL Pipeline';
  }
}

// 4. MEMORY & CHAT
async function sendMemoryMessage(e) {
  e.preventDefault();
  const input = document.getElementById('memory-input');
  const msg = input.value.trim();
  const sessionId = document.getElementById('memory-session').value;
  const chatBox = document.getElementById('memory-chat-box');
  const btn = document.getElementById('btn-send-mem');

  if (!msg) return;

  // Append user bubble
  chatBox.innerHTML += `
    <div class="flex justify-end">
      <div class="bg-indigo-600/90 text-white rounded-2xl rounded-tr-sm px-3.5 py-2 max-w-[80%] text-xs">
        ${msg}
      </div>
    </div>
  `;
  input.value = '';
  chatBox.scrollTop = chatBox.scrollHeight;

  btn.disabled = true;

  try {
    const res = await fetch('/api/demo/memory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: msg })
    });
    const data = await res.json();
    if (data.success) {
      chatBox.innerHTML += `
        <div class="flex justify-start">
          <div class="bg-slate-900 border border-slate-800 text-slate-200 rounded-2xl rounded-tl-sm px-3.5 py-2 max-w-[80%] text-xs">
            ${data.reply}
          </div>
        </div>
      `;
    }
  } catch (err) {
    chatBox.innerHTML += `<div class="text-xs text-red-400">Error: ${err.message}</div>`;
  } finally {
    btn.disabled = false;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

async function resetMemorySession() {
  const sessionId = document.getElementById('memory-session').value;
  const chatBox = document.getElementById('memory-chat-box');
  try {
    await fetch('/api/demo/memory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, reset: true })
    });
    chatBox.innerHTML = `<div class="text-xs text-slate-500 text-center py-2">Session '${sessionId}' memory cleared.</div>`;
  } catch (err) {
    console.error(err);
  }
}

function loadSessionHistory() {
  const sessionId = document.getElementById('memory-session').value;
  document.getElementById('memory-chat-box').innerHTML = `
    <div class="text-xs text-slate-500 text-center py-2">Switched to session '${sessionId}'. Start typing!</div>
  `;
}

// 5. TEXT SPLITTER
async function runSplitterDemo() {
  const text = document.getElementById('splitter-text').value.trim();
  const chunkSize = parseInt(document.getElementById('splitter-size').value, 10);
  const chunkOverlap = parseInt(document.getElementById('splitter-overlap').value, 10);
  const btn = document.getElementById('btn-run-split');
  const container = document.getElementById('splitter-chunks-container');
  const countEl = document.getElementById('splitter-count');

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Splitting...';

  try {
    const res = await fetch('/api/demo/splitters', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, chunk_size: chunkSize, chunk_overlap: chunkOverlap })
    });
    const data = await res.json();
    if (data.success) {
      countEl.textContent = data.total_chunks;
      container.innerHTML = data.chunks.map(c => `
        <div class="p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs space-y-1">
          <div class="flex items-center justify-between text-amber-400 font-semibold text-[11px]">
            <span>Chunk #${c.index}</span>
            <span class="text-slate-500">${c.chars} chars</span>
          </div>
          <p class="text-slate-300 font-mono text-[11px] leading-relaxed whitespace-pre-wrap">${c.text}</p>
        </div>
      `).join('');
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-scissors"></i> Split Text into Chunks';
  }
}

// 6. RAG DEMO
function setRagQuery(q) {
  document.getElementById('rag-query').value = q;
}

async function runRagDemo() {
  const query = document.getElementById('rag-query').value.trim();
  const btn = document.getElementById('btn-run-rag');
  const vanillaBox = document.getElementById('rag-res-vanilla');
  const groundedBox = document.getElementById('rag-res-grounded');
  const latencyEl = document.getElementById('rag-latency');
  const retrievedBox = document.getElementById('rag-retrieved-box');
  const retrievedList = document.getElementById('rag-retrieved-list');

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running Vector Search & LCEL RAG...';
  vanillaBox.textContent = 'Querying standard Gemini (without context)...';
  groundedBox.textContent = 'Embedding query, retrieving from InMemoryVectorStore, and generating grounded response...';

  try {
    const res = await fetch('/api/demo/rag', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: query })
    });
    const data = await res.json();
    if (data.success) {
      vanillaBox.textContent = data.without_rag;
      groundedBox.textContent = data.with_rag;
      latencyEl.textContent = `${data.latency_ms} ms`;

      if (data.retrieved_docs && data.retrieved_docs.length > 0) {
        retrievedBox.classList.remove('hidden');
        retrievedList.innerHTML = data.retrieved_docs.map((doc, idx) => `
          <div class="p-2.5 bg-slate-900 rounded-lg border border-slate-800 text-[11px]">
            <span class="text-purple-400 font-semibold">[Doc ${idx + 1}: ${doc.title}]</span>
            <p class="text-slate-300 mt-1">${doc.content}</p>
          </div>
        `).join('');
      }
    } else {
      groundedBox.textContent = `Error: ${data.error}`;
    }
  } catch (err) {
    groundedBox.textContent = `Network error: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Retrieve & Generate (Side-by-Side Comparison)';
  }
}

// 7. TOOLS & FUNCTION CALLING
function updateToolArgsUI() {
  const toolName = document.getElementById('tool-select').value;
  const container = document.getElementById('tool-args-container');
  if (toolName === 'check_flight_status') {
    container.innerHTML = `
      <div>
        <label class="block text-xs font-semibold text-slate-400 mb-1">Flight Number (Try: BA-249, DL-104, LH-441)</label>
        <input id="tool-arg-1" type="text" value="BA-249" class="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-sm">
      </div>
    `;
  } else if (toolName === 'calculate_compound_interest') {
    container.innerHTML = `
      <div class="grid grid-cols-3 gap-2">
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Principal ($)</label>
          <input id="tool-arg-1" type="number" value="10000" class="w-full bg-slate-950 border border-slate-700 rounded-xl p-2 text-sm">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Rate (0.07)</label>
          <input id="tool-arg-2" type="number" step="0.01" value="0.07" class="w-full bg-slate-950 border border-slate-700 rounded-xl p-2 text-sm">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Years</label>
          <input id="tool-arg-3" type="number" value="5" class="w-full bg-slate-950 border border-slate-700 rounded-xl p-2 text-sm">
        </div>
      </div>
    `;
  } else { // get_stock_price
    container.innerHTML = `
      <div>
        <label class="block text-xs font-semibold text-slate-400 mb-1">Stock Ticker (NVDA, AAPL, GOOGL, TSLA)</label>
        <input id="tool-arg-1" type="text" value="NVDA" class="w-full bg-slate-950 border border-slate-700 rounded-xl p-2.5 text-sm">
      </div>
    `;
  }
}

async function runToolDemo() {
  const toolName = document.getElementById('tool-select').value;
  const btn = document.getElementById('btn-run-tool');
  const outBox = document.getElementById('tool-output-box');

  let args = {};
  if (toolName === 'check_flight_status') {
    args = { flight_number: document.getElementById('tool-arg-1').value.trim() };
  } else if (toolName === 'calculate_compound_interest') {
    args = {
      principal: parseFloat(document.getElementById('tool-arg-1').value),
      annual_rate: parseFloat(document.getElementById('tool-arg-2').value),
      years: parseInt(document.getElementById('tool-arg-3').value, 10)
    };
  } else {
    args = { ticker: document.getElementById('tool-arg-1').value.trim() };
  }

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Calling Tool...';

  try {
    const res = await fetch('/api/demo/tools', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool: toolName, args })
    });
    const data = await res.json();
    if (data.success) {
      outBox.textContent = `Executed @tool '${data.tool}' with parameters:\n${JSON.stringify(data.args, null, 2)}\n\n--> RESULT:\n${typeof data.result === 'object' ? JSON.stringify(data.result, null, 2) : data.result}`;
    } else {
      outBox.textContent = `Error: ${data.error}`;
    }
  } catch (err) {
    outBox.textContent = `Network error: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Invoke Tool Function';
  }
}

// 8. AUTONOMOUS AGENT DEMO
async function runAgentDemo() {
  const goal = document.getElementById('agent-goal').value.trim();
  const btn = document.getElementById('btn-run-agent');
  const container = document.getElementById('agent-steps-container');
  const latencyEl = document.getElementById('agent-latency');

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Agent Reasoning in Autonomous Loop...';
  container.innerHTML = `<div class="p-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-rose-300 text-center animate-pulse">Running Agent Loop: Planning -> Choosing Tools -> Executing -> Synthesizing...</div>`;

  try {
    const res = await fetch('/api/demo/agent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal })
    });
    const data = await res.json();
    if (data.success) {
      latencyEl.textContent = `${data.latency_ms} ms (${data.total_steps} iterations)`;
      container.innerHTML = data.steps.map(s => {
        if (s.type === 'action') {
          return `
            <div class="p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs space-y-2">
              <div class="flex items-center justify-between text-rose-400 font-semibold">
                <span>🧠 Step ${s.step}: Agent Reasoning & Tool Invocation</span>
              </div>
              <p class="text-slate-300 italic text-[11px]">${s.thought}</p>
              <div class="space-y-1.5 pl-3 border-l-2 border-rose-500/50">
                ${s.actions.map(act => `
                  <div>
                    <span class="text-amber-400 font-semibold">▶ Action:</span> <code>${act.tool}(${JSON.stringify(act.args)})</code>
                    <div class="text-slate-400 mt-0.5"><span class="text-emerald-400">👁️ Observation:</span> ${act.observation}</div>
                  </div>
                `).join('')}
              </div>
            </div>
          `;
        } else {
          return `
            <div class="p-4 bg-slate-900 border border-emerald-800/60 rounded-xl text-xs space-y-2">
              <div class="text-emerald-400 font-bold text-sm flex items-center gap-2">
                <i class="fa-solid fa-circle-check"></i> Step ${s.step}: Goal Achieved & Final Synthesis
              </div>
              <p class="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">${s.final_answer}</p>
            </div>
          `;
        }
      }).join('');
    } else {
      container.innerHTML = `<div class="text-xs text-red-400 p-3 bg-slate-950 rounded-xl border border-red-900">Error: ${data.error}</div>`;
    }
  } catch (err) {
    container.innerHTML = `<div class="text-xs text-red-400 p-3 bg-slate-950 rounded-xl border border-red-900">Network error: ${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Launch Agent Reasoning Loop';
  }
}

// 9. STANDALONE SCRIPT RUNNER & CODE VIEWER
let currentScriptView = 'output';

function toggleScriptView(view) {
  currentScriptView = view;
  const outBtn = document.getElementById('btn-view-output');
  const codeBtn = document.getElementById('btn-view-code');
  const terminal = document.getElementById('runner-terminal');
  const code = document.getElementById('runner-code');

  if (view === 'output') {
    outBtn.className = 'text-xs px-3 py-1 bg-yellow-500 text-slate-950 font-bold rounded-lg';
    codeBtn.className = 'text-xs px-3 py-1 bg-slate-800 text-slate-300 rounded-lg hover:text-white';
    terminal.classList.remove('hidden');
    code.classList.add('hidden');
  } else {
    codeBtn.className = 'text-xs px-3 py-1 bg-emerald-500 text-slate-950 font-bold rounded-lg';
    outBtn.className = 'text-xs px-3 py-1 bg-slate-800 text-slate-300 rounded-lg hover:text-white';
    code.classList.remove('hidden');
    terminal.classList.add('hidden');
    loadScriptCode(selectedScript);
  }
}

async function loadScriptCode(filename) {
  const codeEl = document.getElementById('runner-code');
  codeEl.textContent = 'Loading source code...';
  try {
    const res = await fetch(`/api/get-code/${filename}`);
    const data = await res.json();
    if (data.success) {
      codeEl.textContent = data.code;
    }
  } catch (err) {
    codeEl.textContent = `Failed to load source: ${err.message}`;
  }
}

async function runSelectedScript() {
  const btn = document.getElementById('btn-run-script');
  const terminal = document.getElementById('runner-terminal');

  toggleScriptView('output');
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-[10px]"></i> Running...';
  terminal.textContent = `[Terminal Process]: python ${selectedScript}\nExecuting in background, capturing output...\n`;

  try {
    const res = await fetch(`/api/run-example/${selectedScript}`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      terminal.textContent = data.output;
    } else {
      terminal.textContent = `Execution Failed (exit code ${data.returncode || 'err'}):\n${data.output || data.error}`;
    }
  } catch (err) {
    terminal.textContent = `Network error executing script: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-play text-[10px]"></i> Run Script';
  }
}
