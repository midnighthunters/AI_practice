// RAG Explainer Interactive Client Logic - Head-to-Head Arena & Deep Dive

document.addEventListener('DOMContentLoaded', () => {
  // Core Elements
  const queryInput = document.getElementById('queryInput');
  const runQueryBtn = document.getElementById('runQueryBtn');
  const clearInputBtn = document.getElementById('clearInputBtn');
  const topKSelect = document.getElementById('topKSelect');
  const arenaViewSelect = document.getElementById('arenaViewSelect');
  const arenaTitle = document.getElementById('arenaTitle');
  const arenaSubtitleBadge = document.getElementById('arenaSubtitleBadge');
  const presetButtons = document.querySelectorAll('.preset-btn');
  const breakButtons = document.querySelectorAll('.break-btn');

  // Left & Right Arena Elements
  const leftBadge = document.getElementById('leftBadge');
  const leftSubBadge = document.getElementById('leftSubBadge');
  const leftLatency = document.getElementById('leftLatency');
  const leftChunksSummary = document.getElementById('leftChunksSummary');
  const leftResponseBox = document.getElementById('leftResponseBox');
  const leftOutcomeStatus = document.getElementById('leftOutcomeStatus');
  const leftScoreBadge = document.getElementById('leftScoreBadge');

  const rightBadge = document.getElementById('rightBadge');
  const rightSubBadge = document.getElementById('rightSubBadge');
  const rightLatency = document.getElementById('rightLatency');
  const rightChunksSummary = document.getElementById('rightChunksSummary');
  const rightResponseBox = document.getElementById('rightResponseBox');
  const rightOutcomeStatus = document.getElementById('rightOutcomeStatus');
  const rightScoreBadge = document.getElementById('rightScoreBadge');

  // Pipeline Indicator Elements
  const pipelineSection = document.getElementById('pipelineSection');
  const stepQuery = document.getElementById('step-query');
  const stepRetrieve = document.getElementById('step-retrieve');
  const stepAugment = document.getElementById('step-augment');
  const stepGenerate = document.getElementById('step-generate');

  // Tab 1 & 2 Elements
  const retrievalCardsContainer = document.getElementById('retrievalCardsContainer');
  const augmentedPromptText = document.getElementById('augmentedPromptText');
  const copyPromptBtn = document.getElementById('copyPromptBtn');

  // Tab 3: Advanced Lab Elements
  const hydeContentBox = document.getElementById('hydeContentBox');
  const contextOrderBox = document.getElementById('contextOrderBox');
  const groundingScoreBadge = document.getElementById('groundingScoreBadge');
  const groundingStatusBox = document.getElementById('groundingStatusBox');
  const claimsListContainer = document.getElementById('claimsListContainer');

  // Tab 4: Knowledge Base Elements
  const documentsList = document.getElementById('documentsList');
  const docsCountBadge = document.getElementById('docsCountBadge');
  const showAddDocModalBtn = document.getElementById('showAddDocModalBtn');
  const closeAddDocModalBtn = document.getElementById('closeAddDocModalBtn');
  const cancelAddDocBtn = document.getElementById('cancelAddDocBtn');
  const saveDocBtn = document.getElementById('saveDocBtn');
  const resetDocsBtn = document.getElementById('resetDocsBtn');
  const addDocModal = document.getElementById('addDocModal');

  // Load initial documents
  loadDocuments();

  // Arena View Mode Change
  arenaViewSelect.addEventListener('change', () => {
    updateArenaLabels();
  });

  function updateArenaLabels() {
    const isHeadToHead = arenaViewSelect.value === 'naive_vs_adv';
    if (isHeadToHead) {
      arenaTitle.innerHTML = '<i class="fa-solid fa-scale-balanced text-indigo-400"></i> Head-to-Head: Naive RAG vs Advanced RAG';
      arenaSubtitleBadge.textContent = 'Literal Keyword Match vs HyDE + Re-Ranking';

      leftBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30';
      leftBadge.innerHTML = '<i class="fa-solid fa-box mr-1"></i> Naive RAG (Basic Vector Match)';
      leftSubBadge.textContent = 'Literal Keyword / TF-IDF Search';
      leftOutcomeStatus.className = 'flex items-center gap-1.5 text-amber-400 font-medium';
      leftOutcomeStatus.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Fails on Vocabulary Mismatch';

      rightBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
      rightBadge.innerHTML = '<i class="fa-solid fa-bolt mr-1"></i> Advanced RAG (HyDE + Re-Rank)';
      rightSubBadge.textContent = 'Semantic Bridge + Verification';
      rightOutcomeStatus.className = 'flex items-center gap-1.5 text-emerald-400 font-medium';
      rightOutcomeStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> High Recall & Self-Verified';
    } else {
      arenaTitle.innerHTML = '<i class="fa-solid fa-scale-balanced text-indigo-400"></i> Comparison: Pure LLM vs RAG-Augmented LLM';
      arenaSubtitleBadge.textContent = 'Zero Context vs Injected Knowledge Base';

      leftBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30';
      leftBadge.innerHTML = '<i class="fa-solid fa-xmark mr-1"></i> Without RAG (Raw LLM)';
      leftSubBadge.textContent = 'Zero Context Injected';
      leftOutcomeStatus.className = 'flex items-center gap-1.5 text-rose-400 font-medium';
      leftOutcomeStatus.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Ignorance or Hallucination';

      rightBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
      rightBadge.innerHTML = '<i class="fa-solid fa-check mr-1"></i> With RAG (Augmented LLM)';
      rightSubBadge.textContent = 'Grounded in Knowledge Base';
      rightOutcomeStatus.className = 'flex items-center gap-1.5 text-emerald-400 font-medium';
      rightOutcomeStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> Grounded & Factual';
    }
  }

  // Break Naive RAG buttons
  breakButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      queryInput.value = btn.dataset.query;
      arenaViewSelect.value = 'naive_vs_adv';
      updateArenaLabels();
      runComparison();
    });
  });

  // Regular preset buttons
  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      queryInput.value = btn.dataset.query;
      runComparison();
    });
  });

  // Clear Input
  clearInputBtn.addEventListener('click', () => {
    queryInput.value = '';
    queryInput.focus();
  });

  // Run Query
  runQueryBtn.addEventListener('click', () => {
    runComparison();
  });

  queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      runComparison();
    }
  });

  // Copy Prompt
  copyPromptBtn.addEventListener('click', () => {
    const text = augmentedPromptText.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const originalHTML = copyPromptBtn.innerHTML;
      copyPromptBtn.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i> Copied!';
      setTimeout(() => {
        copyPromptBtn.innerHTML = originalHTML;
      }, 2000);
    });
  });

  // Modal handlers
  showAddDocModalBtn.addEventListener('click', () => {
    addDocModal.classList.remove('hidden');
  });

  const closeModal = () => {
    addDocModal.classList.add('hidden');
    document.getElementById('newDocTitle').value = '';
    document.getElementById('newDocCategory').value = '';
    document.getElementById('newDocContent').value = '';
  };

  closeAddDocModalBtn.addEventListener('click', closeModal);
  cancelAddDocBtn.addEventListener('click', closeModal);

  saveDocBtn.addEventListener('click', async () => {
    const title = document.getElementById('newDocTitle').value.trim();
    const category = document.getElementById('newDocCategory').value.trim();
    const content = document.getElementById('newDocContent').value.trim();

    if (!title || !content) {
      alert('Please fill out both Title and Content.');
      return;
    }

    try {
      const res = await fetch('/api/documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, category, content })
      });
      const data = await res.json();
      if (data.success) {
        closeModal();
        loadDocuments();
      } else {
        alert('Error: ' + data.error);
      }
    } catch (err) {
      alert('Failed to save document: ' + err.message);
    }
  });

  resetDocsBtn.addEventListener('click', async () => {
    if (confirm('Reset knowledge base back to default sample documents?')) {
      try {
        const res = await fetch('/api/documents/reset', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          loadDocuments();
        }
      } catch (err) {
        alert('Reset failed: ' + err.message);
      }
    }
  });

  // Load documents list
  async function loadDocuments() {
    try {
      const res = await fetch('/api/documents');
      const data = await res.json();
      if (data.success) {
        docsCountBadge.textContent = data.count;
        renderDocuments(data.documents);
      }
    } catch (err) {
      console.error('Failed to load documents', err);
    }
  }

  function renderDocuments(docs) {
    if (!docs || docs.length === 0) {
      documentsList.innerHTML = '<div class="col-span-full text-slate-500 text-center py-6">Knowledge base is empty. Add a document!</div>';
      return;
    }

    documentsList.innerHTML = docs.map(doc => `
      <div class="doc-card rounded-xl border border-slate-800 bg-slate-900/60 p-4 relative group flex flex-col justify-between">
        <div>
          <div class="flex items-start justify-between gap-2 mb-2">
            <div>
              <span class="inline-block px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-1">
                ${escapeHtml(doc.category || 'General')}
              </span>
              <h5 class="text-sm font-bold text-white leading-snug">${escapeHtml(doc.title)}</h5>
            </div>
            <button onclick="deleteDocument('${doc.id}')" class="text-slate-600 hover:text-rose-400 p-1 transition" title="Delete chunk">
              <i class="fa-regular fa-trash-can text-xs"></i>
            </button>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">${escapeHtml(doc.content)}</p>
        </div>
        <div class="mt-3 pt-2 border-t border-slate-800/80 text-[11px] text-slate-500 font-mono">
          ID: ${escapeHtml(doc.id)}
        </div>
      </div>
    `).join('');
  }

  window.deleteDocument = async function(id) {
    if (confirm('Delete this knowledge document chunk?')) {
      try {
        const res = await fetch(`/api/documents/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
          loadDocuments();
        }
      } catch (err) {
        alert('Delete failed: ' + err.message);
      }
    }
  };

  // Main Comparison Runner
  async function runComparison() {
    const query = queryInput.value.trim();
    if (!query) {
      alert('Please enter a question to compare.');
      return;
    }

    const topK = parseInt(topKSelect.value, 10);
    const viewMode = arenaViewSelect.value; // 'naive_vs_adv' or 'raw_vs_rag'

    // UI Loading State
    runQueryBtn.disabled = true;
    runQueryBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-xs"></i> Comparing Pipelines...';

    pipelineSection.classList.remove('hidden');
    highlightStep(stepQuery);

    leftResponseBox.innerHTML = '<div class="flex items-center gap-2 text-slate-400"><i class="fa-solid fa-spinner fa-spin text-amber-400"></i> Processing query...</div>';
    leftChunksSummary.innerHTML = '<span class="text-slate-400"><i class="fa-solid fa-spinner fa-spin text-slate-500 mr-1.5"></i> Searching...</span>';
    leftLatency.textContent = 'loading...';
    leftScoreBadge.textContent = 'Match: --%';

    rightResponseBox.innerHTML = '<div class="flex items-center gap-2 text-slate-400"><i class="fa-solid fa-spinner fa-spin text-emerald-400"></i> Generating with Advanced RAG...</div>';
    rightChunksSummary.innerHTML = '<span class="text-slate-400"><i class="fa-solid fa-spinner fa-spin text-emerald-400 mr-1.5"></i> HyDE + Re-Ranking...</span>';
    rightLatency.textContent = 'loading...';
    rightScoreBadge.textContent = 'Match: --%';

    setTimeout(() => highlightStep(stepRetrieve), 400);
    setTimeout(() => highlightStep(stepAugment), 900);
    setTimeout(() => highlightStep(stepGenerate), 1400);

    try {
      const res = await fetch('/api/compare-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK })
      });

      const json = await res.json();
      if (!json.success) {
        throw new Error(json.error || 'Server error occurred');
      }

      const naiveData = json.naive;
      const advData = json.advanced;

      if (viewMode === 'naive_vs_adv') {
        // --- VIEW 1: NAIVE RAG VS ADVANCED RAG ---
        
        // Left Column: NAIVE RAG
        const naiveSelected = (naiveData.retrieval.all_documents || []).filter(d => d.selected);
        const naiveTopDoc = naiveSelected[0];
        const naiveTopScore = naiveTopDoc ? naiveTopDoc.score : 0;

        leftLatency.textContent = `${naiveData.with_rag.latency_ms} ms`;
        leftScoreBadge.textContent = `Match: ${naiveTopScore}%`;

        if (naiveTopScore === 0 || naiveSelected.length === 0) {
          leftChunksSummary.innerHTML = `
            <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-rose-950/80 border border-rose-800 text-rose-300 text-[11px] font-bold">
              <i class="fa-solid fa-xmark text-rose-400"></i> 0.0% Match - No Chunks Retrieved (Failed!)
            </span>
          `;
          leftResponseBox.innerHTML = `
            <div class="space-y-2">
              <span class="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800">
                <i class="fa-solid fa-ban mr-1"></i> FAILED RETRIEVAL (0.0% RELEVANCE)
              </span>
              <p class="text-rose-200/90 text-sm leading-relaxed">
                Naive keyword search found <strong>0 matching keywords</strong> in the documents because the query used words not found verbatim in the text.
              </p>
              <div class="bg-slate-950 p-2.5 rounded border border-rose-900/60 text-xs text-slate-400 italic">
                "${escapeHtml(naiveData.with_rag.response)}"
              </div>
            </div>
          `;
        } else {
          leftChunksSummary.innerHTML = naiveSelected.map(d => `
            <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-amber-950/80 border border-amber-800 text-amber-300 text-[11px] font-medium">
              <i class="fa-solid fa-file-lines text-[10px]"></i> ${escapeHtml(d.title)} (${d.score}%)
            </span>
          `).join(' ');
          leftResponseBox.textContent = naiveData.with_rag.response || 'No response';
        }

        // Right Column: ADVANCED RAG
        const advSelected = (advData.retrieval.all_documents || []).filter(d => d.selected);
        const advTopDoc = advSelected[0];
        const advTopScore = advTopDoc ? advTopDoc.score : 0;

        rightLatency.textContent = `${advData.with_rag.latency_ms} ms`;
        rightScoreBadge.textContent = `Re-Rank Match: ${advTopScore}%`;

        if (advSelected.length > 0) {
          rightChunksSummary.innerHTML = advSelected.map(d => `
            <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-[11px] font-medium">
              <i class="fa-solid fa-check text-emerald-400 text-[10px]"></i> ${escapeHtml(d.title)} (${d.score}%)
            </span>
          `).join(' ');
          rightResponseBox.innerHTML = `
            <div class="space-y-2">
              <span class="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                <i class="fa-solid fa-circle-check mr-1"></i> RESCUED BY HYDE & RE-RANKING (${advTopScore}%)
              </span>
              <p class="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">${escapeHtml(advData.with_rag.response)}</p>
            </div>
          `;
        } else {
          rightChunksSummary.innerHTML = '<span class="text-amber-400 text-xs">No chunks met threshold</span>';
          rightResponseBox.textContent = advData.with_rag.response;
        }

      } else {
        // --- VIEW 2: RAW LLM VS RAG ---
        leftLatency.textContent = `${naiveData.without_rag.latency_ms} ms`;
        leftScoreBadge.textContent = 'No Context';
        leftChunksSummary.innerHTML = '<span class="text-slate-500 italic">No search performed (Zero context)</span>';
        leftResponseBox.textContent = naiveData.without_rag.response;

        const advSelected = (advData.retrieval.all_documents || []).filter(d => d.selected);
        rightLatency.textContent = `${advData.with_rag.latency_ms} ms`;
        rightScoreBadge.textContent = `Match: ${advSelected[0] ? advSelected[0].score : 0}%`;
        rightChunksSummary.innerHTML = advSelected.map(d => `
          <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-[11px] font-medium">
            <i class="fa-solid fa-file-lines text-[10px]"></i> ${escapeHtml(d.title)} (${d.score}%)
          </span>
        `).join(' ');
        rightResponseBox.textContent = advData.with_rag.response;
      }

      // Populate Tab 1: Retrieval Cards (Side-by-side comparison of scores)
      renderRetrievalCards(naiveData.retrieval, advData.retrieval);

      // Populate Tab 2: Augmented Prompt
      augmentedPromptText.textContent = advData.augmentation.full_prompt;

      // Populate Tab 3: Advanced RAG Lab
      renderAdvancedLab(advData.advanced_features, (advData.retrieval.all_documents || []).filter(d => d.selected));

      // Complete all steps
      [stepQuery, stepRetrieve, stepAugment, stepGenerate].forEach(step => {
        step.classList.remove('pipeline-step-active');
        step.classList.add('text-emerald-400');
        const badge = step.querySelector('span:first-child');
        badge.classList.remove('bg-slate-800', 'text-slate-400');
        badge.classList.add('bg-emerald-950', 'text-emerald-400', 'border-emerald-700');
      });

    } catch (err) {
      leftResponseBox.innerHTML = `<span class="text-rose-400">Error: ${escapeHtml(err.message)}</span>`;
      rightResponseBox.innerHTML = `<span class="text-rose-400">Error: ${escapeHtml(err.message)}</span>`;
    } finally {
      runQueryBtn.disabled = false;
      runQueryBtn.innerHTML = '<i class="fa-solid fa-play text-xs"></i> Run Comparison';
    }
  }

  function highlightStep(activeStep) {
    [stepQuery, stepRetrieve, stepAugment, stepGenerate].forEach(step => {
      step.classList.remove('pipeline-step-active');
    });
    activeStep.classList.add('pipeline-step-active');
  }

  function renderRetrievalCards(naiveRetrieval, advRetrieval) {
    const advDocs = advRetrieval.all_documents || [];
    const naiveDocs = naiveRetrieval.all_documents || [];

    if (advDocs.length === 0) {
      retrievalCardsContainer.innerHTML = '<div class="col-span-full text-slate-500 text-center py-6">No documents to score.</div>';
      return;
    }

    retrievalCardsContainer.innerHTML = advDocs.map(doc => {
      const naiveMatch = naiveDocs.find(d => d.id === doc.id) || { score: 0 };
      const isSelected = doc.selected;
      const borderClass = isSelected ? 'border-emerald-500/50 bg-emerald-950/20 shadow-lg shadow-emerald-950/30' : 'border-slate-800 bg-slate-900/40 opacity-70';
      const statusBadge = isSelected 
        ? `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1"><i class="fa-solid fa-check"></i> SELECTED BY ADVANCED RAG (Rank #${doc.rank})</span>`
        : `<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-400 border border-slate-700">DISCARDED / LOW RELEVANCE</span>`;

      return `
        <div class="rounded-xl border ${borderClass} p-4 flex flex-col justify-between transition">
          <div>
            <div class="flex items-start justify-between gap-2 mb-2">
              <h5 class="text-sm font-bold text-white">${escapeHtml(doc.title)}</h5>
              <div class="flex items-center gap-3">
                <div class="text-right">
                  <span class="text-xs text-amber-400 font-mono font-bold">${naiveMatch.score}%</span>
                  <span class="block text-[8px] text-slate-500 uppercase">Naive</span>
                </div>
                <div class="text-right">
                  <span class="text-base font-extrabold ${isSelected ? 'text-emerald-400' : 'text-slate-400'} font-mono">${doc.score}%</span>
                  <span class="block text-[8px] text-slate-500 uppercase">Advanced</span>
                </div>
              </div>
            </div>
            <div class="mb-3">${statusBadge}</div>
            <p class="text-xs text-slate-300 leading-relaxed mb-3">${escapeHtml(doc.content)}</p>
          </div>
          <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2 text-xs">
            <span class="text-[11px] text-indigo-400 font-mono">Category: ${escapeHtml(doc.category)}</span>
            <span class="text-[11px] text-slate-500 font-mono">ID: ${escapeHtml(doc.id)}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderAdvancedLab(advFeatures, selectedDocs) {
    if (!advFeatures) return;

    // 1. HyDE
    if (advFeatures.hyde && advFeatures.hyde.hypothetical_passage) {
      hydeContentBox.innerHTML = `
        <span class="text-amber-300">"${escapeHtml(advFeatures.hyde.hypothetical_passage)}"</span>
        <div class="mt-2 text-[10px] text-slate-400 font-sans">
          Generated by Gemini to bridge vocabulary distance with private documents.
        </div>
      `;
    } else {
      hydeContentBox.innerHTML = `<span class="text-slate-500 italic">HyDE bypass (Naive RAG mode).</span>`;
    }

    // 2. Context Placement (Lost in the Middle)
    const strategy = advFeatures.context_arrangement || 'Direct Sequential';
    contextOrderBox.innerHTML = `
      <div class="flex items-center justify-between text-xs font-semibold text-blue-300 mb-1">
        <span>Strategy: ${escapeHtml(strategy)}</span>
      </div>
      <div class="space-y-1">
        ${selectedDocs.map((d, i) => `
          <div class="flex items-center justify-between bg-slate-950 px-2 py-1 rounded text-[11px]">
            <span class="truncate max-w-[180px] text-slate-300">Position #${i+1}: ${escapeHtml(d.title)}</span>
            <span class="text-emerald-400 font-mono text-[10px]">${d.score}%</span>
          </div>
        `).join('')}
      </div>
    `;

    // 3. Grounding Audit
    const audit = advFeatures.grounding_audit;
    if (audit) {
      groundingScoreBadge.textContent = `${audit.grounding_score_pct}%`;
      groundingScoreBadge.className = audit.grounding_score_pct >= 85 
        ? 'text-[11px] font-bold text-emerald-400 font-mono' 
        : 'text-[11px] font-bold text-amber-400 font-mono';

      groundingStatusBox.innerHTML = `
        <div class="w-full text-center space-y-1">
          <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${audit.grounding_score_pct >= 85 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">
            <i class="fa-solid ${audit.grounding_score_pct >= 85 ? 'fa-circle-check' : 'fa-triangle-exclamation'}"></i>
            ${escapeHtml(audit.status)}
          </div>
          <p class="text-[11px] text-slate-400">${audit.grounded_claims} of ${audit.total_claims} claims verified in context</p>
        </div>
      `;

      // Claim breakdown list
      if (audit.claims && audit.claims.length > 0) {
        claimsListContainer.innerHTML = audit.claims.map(claim => `
          <div class="rounded-lg border ${claim.is_grounded ? 'border-emerald-900/60 bg-emerald-950/20' : 'border-amber-900/60 bg-amber-950/20'} p-3 flex items-start justify-between gap-3">
            <div class="space-y-1">
              <p class="text-slate-200 leading-snug">"${escapeHtml(claim.sentence)}"</p>
              <div class="flex items-center gap-2 text-[10px] text-slate-400">
                <span>Source: <strong class="text-slate-300">${escapeHtml(claim.supporting_doc)}</strong></span>
                <span>&bull;</span>
                <span>Context Overlap: <strong class="text-slate-300 font-mono">${claim.overlap_ratio}%</strong></span>
              </div>
            </div>
            <span class="shrink-0 px-2 py-0.5 rounded text-[10px] font-bold ${claim.is_grounded ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">
              ${claim.is_grounded ? 'VERIFIED' : 'UNVERIFIED'}
            </span>
          </div>
        `).join('');
      } else {
        claimsListContainer.innerHTML = `<p class="text-slate-500 text-xs italic">No individual claims detected.</p>`;
      }
    }
  }

  // Tab switcher
  window.switchTab = function(tabName) {
    const tabs = ['retrieval', 'augment', 'advanced', 'docs'];
    tabs.forEach(t => {
      const btn = document.getElementById(`tabBtn${capitalize(t)}`);
      const content = document.getElementById(`tabContent${capitalize(t)}`);
      if (t === tabName) {
        btn.classList.add('border-indigo-500', 'text-indigo-400');
        btn.classList.remove('border-transparent', 'text-slate-400');
        content.classList.remove('hidden');
      } else {
        btn.classList.remove('border-indigo-500', 'text-indigo-400');
        btn.classList.add('border-transparent', 'text-slate-400');
        content.classList.add('hidden');
      }
    });
  };

  function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
