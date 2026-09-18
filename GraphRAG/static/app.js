// GraphRAG Studio Client & Canvas Renderer
document.addEventListener('DOMContentLoaded', () => {
  // Navigation
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(`tab-${btn.dataset.tab}`);
      if (target) {
        target.classList.add('active');
        if (btn.dataset.tab === 'visualizer') {
          drawGraph();
        }
      }
    });
  });

  // Graph Data & Canvas
  const canvas = document.getElementById('graph-canvas');
  const ctx = canvas.getContext('2d');
  let graphData = { nodes: [], edges: [] };
  const nodePositions = {};

  async function loadGraphData() {
    try {
      const res = await fetch('/api/graph/data');
      graphData = await res.json();
      document.getElementById('stat-node-count').textContent = graphData.nodes.length;
      document.getElementById('stat-edge-count').textContent = graphData.edges.length;

      // Populate Path Dropdowns
      const srcSelect = document.getElementById('path-src');
      const tgtSelect = document.getElementById('path-tgt');
      srcSelect.innerHTML = '';
      tgtSelect.innerHTML = '';

      graphData.nodes.forEach(n => {
        const opt1 = new Option(n.label, n.id);
        const opt2 = new Option(n.label, n.id);
        srcSelect.add(opt1);
        tgtSelect.add(opt2);
      });

      if (srcSelect.options.length > 0) srcSelect.value = "Dr. Elena Vance";
      if (tgtSelect.options.length > 3) tgtSelect.value = "Falcon Heavy";

      calculateLayout();
      drawGraph();
    } catch (e) {
      console.error('Failed to load graph data:', e);
    }
  }

  function calculateLayout() {
    const width = canvas.width;
    const height = canvas.height;
    const total = graphData.nodes.length;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.38;

    graphData.nodes.forEach((node, idx) => {
      // Put hubs closer to center
      if (node.id === "QuantumNova") {
        nodePositions[node.id] = { x: centerX, y: centerY };
      } else {
        const angle = (idx / (total - 1)) * 2 * Math.PI;
        nodePositions[node.id] = {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle)
        };
      }
    });
  }

  function drawGraph() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Draw Edges
    graphData.edges.forEach(edge => {
      const src = nodePositions[edge.source];
      const tgt = nodePositions[edge.target];
      if (!src || !tgt) return;

      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Edge relation label
      const midX = (src.x + tgt.x) / 2;
      const midY = (src.y + tgt.y) / 2;
      ctx.font = '10px Fira Code';
      ctx.fillStyle = '#64748b';
      ctx.fillText(edge.relation, midX - 20, midY - 4);
    });

    // 2. Draw Nodes
    graphData.nodes.forEach(node => {
      const pos = nodePositions[node.id];
      if (!pos) return;

      const nodeRadius = 14 + (node.degree || 1) * 2;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, nodeRadius, 0, 2 * Math.PI);
      ctx.fillStyle = node.color || '#38bdf8';
      ctx.fill();
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Node label
      ctx.font = '12px Inter, sans-serif';
      ctx.fillStyle = '#f8fafc';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, pos.x, pos.y + nodeRadius + 14);
    });
  }

  // Tab 2: Path Finder
  const btnFindPath = document.getElementById('btn-find-path');
  const pathSrc = document.getElementById('path-src');
  const pathTgt = document.getElementById('path-tgt');
  const pathResult = document.getElementById('path-result');

  btnFindPath.addEventListener('click', async () => {
    btnFindPath.textContent = 'Searching Relational Hops...';
    try {
      const res = await fetch('/api/graph/path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: pathSrc.value, target: pathTgt.value })
      });
      const data = await res.json();
      if (!data.found || data.path.length === 0) {
        pathResult.textContent = `No direct or multi-hop path found connecting '${data.source}' to '${data.target}'.`;
      } else {
        let txt = `Discovered ${data.path.length}-hop connection path:\n\n`;
        data.path.forEach((hop, i) => {
          txt += `[Hop ${i+1}] (${hop.from}) ──[${hop.relation}]──► (${hop.to})\n`;
        });
        pathResult.textContent = txt;
      }
    } catch (e) {
      pathResult.textContent = `Path search error: ${e.message}`;
    } finally {
      btnFindPath.textContent = 'Find Shortest Relational Path';
    }
  });

  // Tab 3: Hybrid Query
  const btnHybridRun = document.getElementById('btn-hybrid-run');
  const hybridQInput = document.getElementById('hybrid-q-input');
  const hybridResults = document.getElementById('hybrid-results');
  const hybridSynthesis = document.getElementById('hybrid-synthesis');
  const hybridTriplets = document.getElementById('hybrid-triplets');
  const hybridDocs = document.getElementById('hybrid-docs');

  document.querySelectorAll('.sample-queries .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      hybridQInput.value = chip.dataset.hq;
    });
  });

  btnHybridRun.addEventListener('click', async () => {
    btnHybridRun.textContent = 'Executing GraphRAG...';
    try {
      const res = await fetch('/api/graph/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: hybridQInput.value, hops: 2 })
      });
      const data = await res.json();
      hybridResults.style.display = 'block';
      hybridSynthesis.textContent = data.synthesis;

      const triplets = data.retrieval?.graph_triplets_formatted || [];
      hybridTriplets.textContent = triplets.length > 0 ? triplets.join('\n') : 'No graph relations traversed.';

      const docs = data.retrieval?.retrieved_documents || [];
      hybridDocs.textContent = docs.map(d => `[${d.id}]: ${d.content}`).join('\n\n') || 'No raw chunks matched.';
    } catch (e) {
      alert(`GraphRAG query error: ${e.message}`);
    } finally {
      btnHybridRun.textContent = 'Execute GraphRAG';
    }
  });

  loadGraphData();
});
