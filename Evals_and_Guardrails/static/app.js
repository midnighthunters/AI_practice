// Evals & Guardrails Interactive Studio Logic
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
      if (target) target.classList.add('active');
    });
  });

  // Tab 1: LLM-as-a-Judge
  const btnRunJudge = document.getElementById('btn-run-judge');
  const judgeQ = document.getElementById('judge-q');
  const judgeCtx = document.getElementById('judge-ctx');
  const judgeAns = document.getElementById('judge-ans');
  const judgeVerdict = document.getElementById('judge-verdict');
  const judgeAccVal = document.getElementById('judge-acc-val');
  const judgeConcVal = document.getElementById('judge-conc-val');
  const judgeCompVal = document.getElementById('judge-comp-val');
  const judgeReasoning = document.getElementById('judge-reasoning');

  btnRunJudge.addEventListener('click', async () => {
    btnRunJudge.textContent = 'Evaluating...';
    try {
      const res = await fetch('/api/eval/judge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: judgeQ.value,
          context: judgeCtx.value,
          answer: judgeAns.value
        })
      });
      const data = await res.json();
      judgeVerdict.className = `verdict-banner ${data.passed ? 'passed' : 'failed'}`;
      judgeVerdict.textContent = data.passed ? '✅ CANDIDATE PASSED QUALITY AUDIT' : '❌ CANDIDATE FAILED QUALITY AUDIT';
      judgeAccVal.textContent = `${data.accuracy_score}/5`;
      judgeConcVal.textContent = `${data.conciseness_score}/5`;
      judgeCompVal.textContent = `${data.overall_score}/5.0`;
      judgeReasoning.textContent = data.reasoning;
    } catch (e) {
      judgeReasoning.textContent = `Error: ${e.message}`;
    } finally {
      btnRunJudge.textContent = 'Evaluate Candidate Response';
    }
  });

  // Tab 2: RAG Triad
  const btnRunTriad = document.getElementById('btn-run-triad');
  const triadQ = document.getElementById('triad-q');
  const triadCtx = document.getElementById('triad-ctx');
  const triadAns = document.getElementById('triad-ans');
  const triadStatus = document.getElementById('triad-status');
  const meterFaithVal = document.getElementById('meter-faith-val');
  const meterRelVal = document.getElementById('meter-rel-val');
  const meterPrecVal = document.getElementById('meter-prec-val');
  const barFaith = document.getElementById('bar-faith');
  const barRel = document.getElementById('bar-rel');
  const barPrec = document.getElementById('bar-prec');

  btnRunTriad.addEventListener('click', async () => {
    btnRunTriad.textContent = 'Diagnosing...';
    try {
      const contexts = triadCtx.value.split('\n').map(s => s.trim()).filter(Boolean);
      const res = await fetch('/api/eval/rag-triad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: triadQ.value,
          contexts: contexts,
          answer: triadAns.value
        })
      });
      const data = await res.json();
      triadStatus.className = `verdict-banner ${data.health === 'EXCELLENT' ? 'passed' : 'failed'}`;
      triadStatus.textContent = `RAG Pipeline Health: [${data.health}] (Composite Score: ${data.composite_rag_score})`;

      meterFaithVal.textContent = `${Math.round(data.faithfulness * 100)}%`;
      barFaith.style.width = `${Math.round(data.faithfulness * 100)}%`;

      meterRelVal.textContent = `${Math.round(data.answer_relevance * 100)}%`;
      barRel.style.width = `${Math.round(data.answer_relevance * 100)}%`;

      meterPrecVal.textContent = `${Math.round(data.context_precision * 100)}%`;
      barPrec.style.width = `${Math.round(data.context_precision * 100)}%`;
    } catch (e) {
      triadStatus.textContent = `Diagnosis error: ${e.message}`;
    } finally {
      btnRunTriad.textContent = 'Diagnose RAG Pipeline';
    }
  });

  // Tab 3: Guardrails
  const btnScanGuard = document.getElementById('btn-scan-guard');
  const guardInputText = document.getElementById('guard-input-text');
  const guardResults = document.getElementById('guard-results');
  const guardAction = document.getElementById('guard-action');
  const guardInjection = document.getElementById('guard-injection');
  const guardPii = document.getElementById('guard-pii');
  const guardSanitized = document.getElementById('guard-sanitized');

  document.querySelectorAll('.btn-group .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      guardInputText.value = chip.dataset.t;
    });
  });

  btnScanGuard.addEventListener('click', async () => {
    btnScanGuard.textContent = 'Scanning...';
    try {
      const res = await fetch('/api/guard/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: guardInputText.value })
      });
      const data = await res.json();
      guardResults.style.display = 'block';
      guardAction.className = `verdict-banner ${data.action === 'PASS' ? 'passed' : 'failed'}`;
      guardAction.textContent = data.action === 'PASS' ? 'PASS (Traffic Cleared for LLM)' : 'BLOCK (Security Threat Intercepted)';

      guardInjection.textContent = data.injection_detected ? `DETECTED (${data.matched_trigger})` : 'Clean (No attack signatures)';
      guardPii.textContent = data.pii_detected ? data.pii_items.join(', ') : 'None';
      guardSanitized.textContent = data.action === 'PASS' ? data.sanitized_prompt : '[REQUEST BLOCKED BY INLINE FIREWALL - NOT SENT TO LLM]';
    } catch (e) {
      alert(`Guardrail error: ${e.message}`);
    } finally {
      btnScanGuard.textContent = 'Inspect via Input Guardrail';
    }
  });

  // Tab 4: Semantic Cache
  const btnCacheSend = document.getElementById('btn-cache-send');
  const cacheQInput = document.getElementById('cache-q-input');
  const cacheHitStatus = document.getElementById('cache-hit-status');
  const cacheLatencyVal = document.getElementById('cache-latency-val');
  const cacheSimVal = document.getElementById('cache-sim-val');
  const cacheAnswerBox = document.getElementById('cache-answer-box');

  document.querySelectorAll('.sample-queries .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      cacheQInput.value = chip.dataset.cq;
    });
  });

  btnCacheSend.addEventListener('click', async () => {
    btnCacheSend.textContent = 'Sending...';
    try {
      const res = await fetch('/api/cache/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: cacheQInput.value })
      });
      const data = await res.json();
      cacheHitStatus.textContent = data.cache_hit ? 'CACHE HIT ⚡' : 'CACHE MISS ⏳';
      cacheHitStatus.style.color = data.cache_hit ? '#34d399' : '#f59e0b';
      cacheLatencyVal.textContent = `${data.latency_ms} ms`;
      cacheSimVal.textContent = data.cache_hit ? `${data.similarity}` : '0.0 (Cold)';
      cacheAnswerBox.textContent = data.response + (data.matched_query ? `\n\n[Cache matched against previously stored query: "${data.matched_query}"]` : '');
    } catch (e) {
      cacheAnswerBox.textContent = `Cache query error: ${e.message}`;
    } finally {
      btnCacheSend.textContent = 'Send Query';
    }
  });
});
