// MCP Inspector & Studio Client Logic
document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(`tab-${btn.dataset.tab}`);
      if (target) target.classList.add('active');
    });
  });

  // Handshake Tab
  const btnHandshake = document.getElementById('btn-run-handshake');
  const codeInitReq = document.getElementById('code-init-req');
  const codeInitResp = document.getElementById('code-init-resp');

  btnHandshake.addEventListener('click', async () => {
    btnHandshake.textContent = 'Negotiating Handshake...';
    try {
      const res = await fetch('/api/mcp/init', { method: 'POST' });
      const data = await res.json();
      codeInitReq.textContent = JSON.stringify(data.request, null, 2);
      codeInitResp.textContent = JSON.stringify(data.response, null, 2);
    } catch (e) {
      codeInitResp.textContent = `Error: ${e.message}`;
    } finally {
      btnHandshake.textContent = 'Re-run MCP Initialize Handshake';
    }
  });

  // Tools Tab
  let cachedTools = [];
  let currentTool = null;
  const toolsList = document.getElementById('tools-list');
  const toolForm = document.getElementById('tool-form');
  const btnCallTool = document.getElementById('btn-call-tool');
  const codeToolResult = document.getElementById('code-tool-result');

  async function loadTools() {
    try {
      const res = await fetch('/api/mcp/tools');
      const data = await res.json();
      cachedTools = data.result?.tools || [];
      toolsList.innerHTML = '';
      cachedTools.forEach(t => {
        const item = document.createElement('div');
        item.className = 'item-card';
        item.innerHTML = `<h4>🔧 ${t.name}</h4><p>${t.description}</p>`;
        item.addEventListener('click', () => selectTool(t, item));
        toolsList.appendChild(item);
      });
    } catch (e) {
      toolsList.textContent = `Failed to load tools: ${e.message}`;
    }
  }

  function selectTool(tool, element) {
    document.querySelectorAll('#tools-list .item-card').forEach(c => c.classList.remove('active'));
    element.classList.add('active');
    currentTool = tool;
    document.getElementById('tool-exec-title').textContent = `Execute: ${tool.name}`;

    const props = tool.inputSchema?.properties || {};
    let formHtml = '<div style="display:flex; flex-direction:column; gap:10px;">';
    for (const [key, schema] of Object.entries(props)) {
      const defVal = schema.default !== undefined ? schema.default : (key === 'principal' ? 10000 : (key === 'annual_rate' ? 8.5 : (key === 'years' ? 5 : (key === 'hostname' ? 'quantum-db-01' : ''))));
      formHtml += `
        <div>
          <label style="font-size:12px; color:#94a3b8; display:block; margin-bottom:4px;">${key} (${schema.type}):</label>
          <input type="text" id="arg-${key}" value="${defVal}" style="width:100%; background:#0b1120; border:1px solid #334155; color:#f8fafc; padding:8px; border-radius:6px; font-size:13px;">
        </div>`;
    }
    formHtml += '</div>';
    toolForm.innerHTML = formHtml;
    btnCallTool.style.display = 'inline-block';
  }

  btnCallTool.addEventListener('click', async () => {
    if (!currentTool) return;
    const props = currentTool.inputSchema?.properties || {};
    const args = {};
    for (const key of Object.keys(props)) {
      const val = document.getElementById(`arg-${key}`)?.value;
      if (props[key].type === 'number' || props[key].type === 'integer') {
        args[key] = parseFloat(val) || 0;
      } else if (props[key].type === 'boolean') {
        args[key] = val === 'true';
      } else {
        args[key] = val;
      }
    }

    codeToolResult.textContent = 'Calling tool via JSON-RPC...';
    try {
      const res = await fetch('/api/mcp/tools/call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: currentTool.name, arguments: args })
      });
      const data = await res.json();
      codeToolResult.textContent = JSON.stringify(data.response, null, 2);
    } catch (e) {
      codeToolResult.textContent = `Execution error: ${e.message}`;
    }
  });

  // Resources Tab
  const resourcesList = document.getElementById('resources-list');
  const resourceViewer = document.getElementById('resource-viewer');

  async function loadResources() {
    try {
      const res = await fetch('/api/mcp/resources');
      const data = await res.json();
      const list = data.result?.resources || [];
      resourcesList.innerHTML = '';
      list.forEach(r => {
        const item = document.createElement('div');
        item.className = 'item-card';
        item.innerHTML = `<h4>📂 ${r.name}</h4><p><code>${r.uri}</code> (${r.mimeType})</p>`;
        item.addEventListener('click', async () => {
          document.querySelectorAll('#resources-list .item-card').forEach(c => c.classList.remove('active'));
          item.classList.add('active');
          resourceViewer.innerHTML = '<pre>Reading resource from MCP Server...</pre>';
          const rRes = await fetch('/api/mcp/resource/read', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uri: r.uri })
          });
          const rData = await rRes.json();
          const content = rData.result?.contents?.[0]?.text || JSON.stringify(rData, null, 2);
          resourceViewer.innerHTML = `<pre><code>${content}</code></pre>`;
        });
        resourcesList.appendChild(item);
      });
    } catch (e) {
      resourcesList.textContent = `Error loading resources: ${e.message}`;
    }
  }

  // Prompts Tab
  const promptsList = document.getElementById('prompts-list');
  const promptRenderer = document.getElementById('prompt-renderer');

  async function loadPrompts() {
    try {
      const res = await fetch('/api/mcp/prompts');
      const data = await res.json();
      const list = data.result?.prompts || [];
      promptsList.innerHTML = '';
      list.forEach(p => {
        const item = document.createElement('div');
        item.className = 'item-card';
        item.innerHTML = `<h4>📜 ${p.name}</h4><p>${p.description}</p>`;
        item.addEventListener('click', async () => {
          document.querySelectorAll('#prompts-list .item-card').forEach(c => c.classList.remove('active'));
          item.classList.add('active');
          promptRenderer.innerHTML = '<pre>Rendering prompt template...</pre>';
          const args = p.name === 'code_review_security'
            ? { language: 'Python', code_snippet: 'os.system(user_cmd)', compliance_level: 'STRICT' }
            : { service_name: 'payment-gateway', error_log: 'Connection reset by peer at 14:02:11' };

          const pRes = await fetch('/api/mcp/prompts/get', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: p.name, arguments: args })
          });
          const pData = await pRes.json();
          const msg = pData.response?.result?.messages?.[0]?.content?.text || JSON.stringify(pData, null, 2);
          promptRenderer.innerHTML = `<pre><code>${msg}</code></pre>`;
        });
        promptsList.appendChild(item);
      });
    } catch (e) {
      promptsList.textContent = `Error loading prompts: ${e.message}`;
    }
  }

  // Agent Tab
  const btnAgentRun = document.getElementById('btn-agent-run');
  const agentQueryInput = document.getElementById('agent-query-input');
  const agentResults = document.getElementById('agent-results');
  const agentToolName = document.getElementById('agent-tool-name');
  const agentToolArgs = document.getElementById('agent-tool-args');
  const agentToolOutput = document.getElementById('agent-tool-output');
  const agentFinalText = document.getElementById('agent-final-text');

  document.querySelectorAll('.sample-queries .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      agentQueryInput.value = chip.dataset.q;
    });
  });

  btnAgentRun.addEventListener('click', async () => {
    const query = agentQueryInput.value.trim();
    if (!query) return;

    btnAgentRun.textContent = 'Agent Reasoning...';
    agentResults.style.display = 'none';

    try {
      const res = await fetch('/api/mcp/agent/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      agentToolName.textContent = data.selected_tool;
      agentToolArgs.textContent = JSON.stringify(data.tool_args, null, 2);
      agentToolOutput.textContent = JSON.stringify(data.mcp_response, null, 2);
      agentFinalText.textContent = data.final_synthesis;
      agentResults.style.display = 'block';
    } catch (e) {
      alert(`Agent execution failed: ${e.message}`);
    } finally {
      btnAgentRun.textContent = 'Ask MCP Agent';
    }
  });

  // Initial load
  loadTools();
  loadResources();
  loadPrompts();
});
