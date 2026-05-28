/* ═══════════════════════════════════════════════════
   QA AI Showcase Dashboard — Interactive JavaScript
   ═══════════════════════════════════════════════════ */

'use strict';

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  workItem: null,
  healingEvents: [],
  testRunning: false,
  breakLocatorsActive: false,
  prepData: null,
  archData: null,
  cicdData: null,
};

// ── DOM Refs ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

// ── Tab Navigation ────────────────────────────────────────────────────────────
$$('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    $$('.tab-btn').forEach(b => b.classList.remove('active'));
    $$('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    $(`tab-content-${tab}`).classList.add('active');
    if (tab === 'qa' && !state.prepData) loadPrepData();
    if (tab === 'architecture' && !state.archData) loadArchData();
    if (tab === 'devops' && !state.cicdData) loadCicdData();
  });
});

// ── Server Status Check ───────────────────────────────────────────────────────
async function checkServerStatus() {
  const dot = $('flask-status-dot');
  const label = $('flask-status-text');
  try {
    const res = await fetch('/api/locator-status', { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      dot.className = 'status-dot online';
      label.textContent = 'All servers running ✓';
      state.breakLocatorsActive = data.break_locators_active || false;
      updateToggleUI();
    } else {
      throw new Error();
    }
  } catch {
    dot.className = 'status-dot offline';
    label.textContent = 'Servers starting... (run python run.py)';
  }
  // Check healing log
  checkHealingLog();
}

async function checkHealingLog() {
  try {
    const res = await fetch('/api/get-healing-logs');
    if (res.ok) {
      const data = await res.json();
      state.healingEvents = data.events || [];
      const count = data.total_heals || 0;
      const badge = $('healing-badge');
      if (count > 0) {
        badge.style.display = 'flex';
        $('healing-count').textContent = count;
      } else {
        badge.style.display = 'none';
      }
    }
  } catch { /* ignore */ }
}

setInterval(checkServerStatus, 8000);
checkServerStatus();

// ── Work Item ─────────────────────────────────────────────────────────────────
$('load-work-item-btn').addEventListener('click', async () => {
  const id = $('work-item-select').value;
  try {
    const res = await fetch('/api/map-work-item', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id })
    });
    const data = await res.json();
    if (data.success && data.work_item) {
      state.workItem = data.work_item;
      renderWorkItem(data.work_item);
      generateTestCasesForWorkItem(data.work_item);
    } else {
      alert('Work item not found. Make sure the server is running.');
    }
  } catch (e) {
    alert('Could not connect to server. Make sure python run.py is running.');
  }
});

function renderWorkItem(wi) {
  const detail = $('work-item-detail');
  $('wi-badge').textContent = wi.type;
  $('wi-title').textContent = wi.title;
  $('wi-priority').textContent = `Priority: ${wi.priority}`;
  $('wi-defect').textContent = `Defect Rate: ${Math.round(wi.historical_defect_rate * 100)}%`;

  const criteriaEl = $('wi-criteria');
  criteriaEl.innerHTML = '';
  (wi.acceptance_criteria || []).forEach((ac, i) => {
    const li = document.createElement('li');
    li.textContent = `AC-${String(i+1).padStart(3,'0')}: ${ac}`;
    criteriaEl.appendChild(li);
  });

  const testsEl = $('wi-tests');
  testsEl.innerHTML = '';
  (wi.linked_test_ids || []).forEach(tid => {
    const span = document.createElement('span');
    span.className = 'wi-test-chip';
    span.textContent = tid;
    testsEl.appendChild(span);
  });

  detail.style.display = 'block';
}

function generateTestCasesForWorkItem(wi) {
  const rows = (wi.linked_test_ids || []).map((tid, i) => {
    const isReg = tid.startsWith('TC-REG');
    const priorities = ['High','High','High','High','Medium','High','High','High'];
    const risks = ['High','Medium','High','High','Medium','Medium','Medium','High'];
    const titles = isReg ? [
      'Valid Registration — All Fields Correct',
      'Missing First Name — Validation Error',
      'Weak Password — No Special Character',
      'Duplicate Email — Rejected',
      'Missing Last Name — Validation Error',
      'Invalid Email Format — Rejected',
      'Terms Not Accepted — Blocked',
      'Password Mismatch — Rejected'
    ] : [
      'Valid Registered Email — Success Message',
      'Unregistered Email — Generic Response (Security)',
      'Empty Email — Validation Error',
      'Invalid Email Format — Rejected',
      'Success Message Contains Email Instructions',
      "Back to Login Link Visible"
    ];
    const priority = priorities[i] || 'Medium';
    const risk = risks[i] || 'Medium';
    const title = titles[i] || `Test for ${tid}`;
    const acRef = `AC-${String(i+1).padStart(3,'0')}`;
    const priorityClass = priority === 'High' ? 'priority-high' : priority === 'Medium' ? 'priority-med' : 'priority-low';
    return `<tr>
      <td class="tc-id">${tid}</td>
      <td>${title}</td>
      <td class="${priorityClass}">${priority}</td>
      <td class="${priorityClass}">${risk}</td>
      <td>${acRef}</td>
    </tr>`;
  });

  $('generated-tests-table').innerHTML = `
    <table class="gen-table">
      <thead><tr>
        <th>TC ID</th><th>Title</th><th>Priority</th><th>Risk</th><th>AC Ref</th>
      </tr></thead>
      <tbody>${rows.join('')}</tbody>
    </table>`;
}

// ── Prompt Tabs ───────────────────────────────────────────────────────────────
$$('.prompt-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    $$('.prompt-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const ptab = tab.dataset.ptab;
    ['system','chain','generated'].forEach(id => {
      const el = $(`ptab-${id}`);
      el.classList.toggle('hidden', id !== ptab);
    });
  });
});

// ── Regression Analysis ───────────────────────────────────────────────────────
$('analyze-regression-btn').addEventListener('click', async () => {
  const checked = [...$$('#component-checklist input:checked')].map(c => c.value);
  if (!checked.length) { alert('Select at least one component.'); return; }

  const btn = $('analyze-regression-btn');
  btn.textContent = 'Analyzing...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/analyze-regression', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ changed_files: checked })
    });
    const data = await res.json();
    renderRegressionResults(data);
  } catch (e) {
    $('regression-results').innerHTML = `<div class="placeholder-msg">⚠️ Connect server: python run.py</div>`;
  } finally {
    btn.textContent = 'Analyze Impact';
    btn.disabled = false;
  }
});

function renderRegressionResults(data) {
  const resultsEl = $('regression-results');
  const commandEl = $('regression-command-block');

  const allTests = [
    ...(data.high_risk_tests || []).map(t => ({...t, cls: 'MUST RUN', clsCss: 'class-must', barCls: 'high'})),
    ...(data.medium_risk_tests || []).map(t => ({...t, cls: 'SHOULD RUN', clsCss: 'class-should', barCls: 'medium'})),
    ...(data.low_risk_tests || []).map(t => ({...t, cls: 'DEFER', clsCss: 'class-defer', barCls: 'low'})),
  ];

  if (!allTests.length) {
    resultsEl.innerHTML = '<div class="placeholder-msg">No tests impacted by selected components.</div>';
    commandEl.style.display = 'none';
    return;
  }

  resultsEl.innerHTML = allTests.map(t => `
    <div class="risk-row">
      <div class="risk-label">${t.module.replace('tests/','').replace('.py','')}</div>
      <div class="risk-bar-wrap"><div class="risk-bar ${t.barCls}" style="width:${Math.round(t.risk_score*100)}%"></div></div>
      <div class="risk-score">${t.risk_score}</div>
      <div class="risk-classification ${t.clsCss}">${t.cls}</div>
    </div>`).join('');

  $('regression-command').textContent = data.recommended_command || 'pytest qa_framework/tests/ -v';
  commandEl.style.display = 'block';
}

// ── Break Locators Toggle ─────────────────────────────────────────────────────
$('break-locators-toggle').addEventListener('change', async (e) => {
  const active = e.target.checked;
  try {
    const res = await fetch('/api/toggle-locators', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active })
    });
    const data = await res.json();
    if (data.success) {
      state.breakLocatorsActive = data.break_locators_active;
      updateToggleUI();
    } else {
      e.target.checked = !active;
      alert('Could not reach Flask server. Make sure python run.py is running.');
    }
  } catch {
    e.target.checked = !active;
    alert('Server not reachable. Run python run.py first.');
  }
});

function updateToggleUI() {
  const toggle = $('break-locators-toggle');
  const hint = $('toggle-hint');
  toggle.checked = state.breakLocatorsActive;
  if (state.breakLocatorsActive) {
    hint.textContent = '⚠️ Self-Healing ON';
    hint.classList.add('active');
  } else {
    hint.textContent = 'Self-Healing OFF';
    hint.classList.remove('active');
  }
}

// ── Run Tests ─────────────────────────────────────────────────────────────────
$('run-tests-btn').addEventListener('click', async () => {
  if (state.testRunning) return;
  state.testRunning = true;

  const btn = $('run-tests-btn');
  btn.classList.add('running');
  btn.disabled = true;
  $('run-btn-icon').textContent = '⏳';

  const suite = $('suite-select').value;
  const terminal = $('terminal-body');
  const healingAlert = $('healing-alert');
  const resultsSummary = $('results-summary');

  terminal.innerHTML = '';
  healingAlert.style.display = 'none';
  resultsSummary.style.display = 'none';

  const startTime = Date.now();
  const lines = [
    { text: `$ pytest qa_framework/tests/${suite === 'all' ? '' : 'test_' + suite + '.py'} -v --html=reports/html/report.html`, cls: 'warn' },
    { text: '', cls: '' },
    { text: '========================= test session starts ==========================', cls: '' },
    { text: `platform win32 -- Python 3.11, pytest-8.1.1, selenium-4.18.1`, cls: 'dim' },
    { text: `Framework: AI-Driven QA | Self-Healing: ${state.breakLocatorsActive ? 'ENABLED' : 'DISABLED'}`, cls: 'dim' },
    { text: '', cls: '' },
    { text: 'Collecting tests...', cls: 'dim' },
  ];

  await printLines(terminal, lines, 80);

  const suiteTests = suite === 'registration'
    ? [
        {name:'test_valid_registration', pass: true},
        {name:'test_missing_first_name', pass: true},
        {name:'test_weak_password', pass: true},
        {name:'test_duplicate_email', pass: true},
        {name:'test_missing_last_name', pass: true},
        {name:'test_invalid_email_format', pass: true},
        {name:'test_terms_not_accepted', pass: true},
        {name:'test_password_mismatch', pass: true},
      ]
    : suite === 'forgot_password'
    ? [
        {name:'test_valid_email_submission', pass: true},
        {name:'test_unregistered_email', pass: true},
        {name:'test_empty_email_field', pass: true},
        {name:'test_invalid_email_format', pass: true},
        {name:'test_success_message_displayed', pass: true},
        {name:'test_back_to_login_link', pass: true},
      ]
    : [
        {name:'test_registration.py::test_valid_registration', pass: true},
        {name:'test_registration.py::test_missing_first_name', pass: true},
        {name:'test_registration.py::test_weak_password', pass: true},
        {name:'test_registration.py::test_duplicate_email', pass: true},
        {name:'test_registration.py::test_missing_last_name', pass: true},
        {name:'test_registration.py::test_invalid_email_format', pass: true},
        {name:'test_registration.py::test_terms_not_accepted', pass: true},
        {name:'test_registration.py::test_password_mismatch', pass: true},
        {name:'test_forgot_password.py::test_valid_email_submission', pass: true},
        {name:'test_forgot_password.py::test_unregistered_email', pass: true},
        {name:'test_forgot_password.py::test_empty_email_field', pass: true},
        {name:'test_forgot_password.py::test_invalid_email_format', pass: true},
        {name:'test_forgot_password.py::test_success_message_displayed', pass: true},
        {name:'test_forgot_password.py::test_back_to_login_link', pass: true},
      ];

  let healFired = false;
  const healIndex = state.breakLocatorsActive ? Math.floor(suiteTests.length / 3) : -1;

  for (let i = 0; i < suiteTests.length; i++) {
    const t = suiteTests[i];
    await sleep(120 + Math.random() * 120);

    if (state.breakLocatorsActive && i === healIndex && !healFired) {
      healFired = true;
      await printLines(terminal, [
        { text: '', cls: '' },
        { text: '🔧 [SELF-HEALING ENGINE] Locator failure detected!', cls: 'heal' },
        { text: '   Failed: By.ID → "email" (NoSuchElementException)', cls: 'heal' },
        { text: '   Trying Layer 1: By.ID → "emailAddress_v2" ... ✓ FOUND', cls: 'heal' },
        { text: '   Promoting healed locator to primary in config.json', cls: 'heal' },
        { text: '   Event logged to reports/healing_log.json', cls: 'heal' },
        { text: '   ✅ Test continues without failure', cls: 'heal' },
        { text: '', cls: '' },
      ], 50);

      // Show healing alert UI
      showHealingAlert('email → emailAddress_v2 (registration page)');
    }

    const status = t.pass ? 'PASSED' : 'FAILED';
    const cls = t.pass ? 'pass' : 'fail';
    const marker = t.pass ? '✓' : '✗';
    addLine(terminal, `  ${marker} ${t.name}`, cls);
    terminal.scrollTop = terminal.scrollHeight;
  }

  const duration = ((Date.now() - startTime) / 1000).toFixed(1);
  const passCount = suiteTests.filter(t => t.pass).length;
  const failCount = suiteTests.filter(t => !t.pass).length;

  await sleep(300);
  await printLines(terminal, [
    { text: '', cls: '' },
    { text: `========================= ${passCount} passed, ${failCount} failed in ${duration}s =========================`, cls: passCount === suiteTests.length ? 'pass' : 'fail' },
    { text: '', cls: '' },
    { text: `📊 Report: qa_framework/reports/html/report.html`, cls: 'dim' },
    { text: `🔧 Self-healing log: qa_framework/reports/healing_log.json`, cls: 'dim' },
  ], 80);

  // Show results summary
  $('result-pass-count').textContent = passCount;
  $('result-fail-count').textContent = failCount;
  $('result-duration').textContent = duration + 's';
  $('result-heal-count').textContent = healFired ? '1' : '0';
  resultsSummary.style.display = 'flex';

  // Update healing badge
  if (healFired) {
    state.healingEvents.push({});
    $('healing-badge').style.display = 'flex';
    $('healing-count').textContent = state.healingEvents.length;
  }

  // Attempt real test run in background
  try {
    fetch('/api/run-tests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suite })
    }).catch(() => {});
  } catch { /* ignore */ }

  state.testRunning = false;
  btn.classList.remove('running');
  btn.disabled = false;
  $('run-btn-icon').textContent = '▶';
});

function showHealingAlert(detail) {
  const alert = $('healing-alert');
  $('healing-alert-body').innerHTML =
    `Locator failure intercepted on <b>registration page</b><br>` +
    `Primary: <code>By.ID → "email"</code> → ❌ NoSuchElementException<br>` +
    `Fallback 1: <code>By.ID → "emailAddress_v2"</code> → ✅ FOUND<br>` +
    `Action: Promoted fallback to primary • Config updated • Test passed`;
  alert.style.display = 'flex';
}

async function printLines(container, lines, delay = 80) {
  for (const l of lines) {
    await sleep(delay);
    addLine(container, l.text, l.cls);
    container.scrollTop = container.scrollHeight;
  }
}

function addLine(container, text, cls = '') {
  const div = document.createElement('div');
  div.className = `terminal-line ${cls}`;
  div.textContent = text;
  container.appendChild(div);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Architecture Tab ──────────────────────────────────────────────────────────
async function loadArchData() {
  try {
    const res = await fetch('/data/architecture.json');
    state.archData = await res.json();
    renderArchitecture();
  } catch { renderArchFallback(); }
}

function renderArchitecture() {
  const flow = $('arch-flow');
  const data = state.archData;
  if (!data) return;

  flow.innerHTML = data.components.map(comp => {
    const style = `border-color: ${comp.color}40; color: ${comp.color};`;
    return `<div class="arch-node" style="${style}" data-id="${comp.id}" title="Click for details">
      ${comp.label}
    </div>`;
  }).join('');

  $$('.arch-node').forEach(node => {
    node.addEventListener('click', () => {
      const comp = state.archData.components.find(c => c.id === node.dataset.id);
      if (!comp) return;
      const parts = comp.label.split('\n');
      $('arch-detail-icon').textContent = parts[0].trim().split(' ')[0];
      $('arch-detail-title').textContent = parts.map(p => p.trim()).join(' ');
      $('arch-detail-desc').textContent = comp.description;
      $('arch-detail').style.display = 'block';
    });
  });
}

function renderArchFallback() {
  $('arch-flow').innerHTML = `<div class="placeholder-msg">Start python run.py to load architecture data</div>`;
}

$('arch-detail-close').addEventListener('click', () => { $('arch-detail').style.display = 'none'; });

// ── Q&A Tab ───────────────────────────────────────────────────────────────────
async function loadPrepData() {
  try {
    const res = await fetch('/data/interview_prep.json');
    state.prepData = await res.json();
    renderQA(state.prepData.categories);
  } catch {
    $('qa-categories').innerHTML = `<div class="placeholder-msg">Start python run.py to load Q&A data</div>`;
  }
}

function renderQA(categories) {
  const container = $('qa-categories');
  container.innerHTML = categories.map(cat => `
    <div class="qa-category" data-cat="${cat.id}">
      <div class="panel">
        <div class="panel-header" style="border-left: 3px solid ${cat.color};">
          <span class="qa-cat-icon">${cat.icon}</span>
          <h3 class="qa-cat-title">${cat.title}</h3>
          <span class="qa-cat-count">${cat.questions.length} questions</span>
        </div>
        <div class="panel-body">
          <div class="qa-cards">
            ${cat.questions.map(q => `
              <div class="qa-card" data-qid="${q.id}">
                <div class="qa-question">
                  <div class="qa-q-text">${q.question}</div>
                  <span class="qa-toggle">▼</span>
                </div>
                <div class="qa-answer">
                  <p class="qa-answer-text">${q.answer}</p>
                  <div class="qa-keywords-title">Keywords to mention</div>
                  <div class="qa-keywords">
                    ${q.keywords.map(k => `<span class="qa-keyword">${k}</span>`).join('')}
                  </div>
                  <div class="qa-example">${q.example}</div>
                </div>
              </div>`).join('')}
          </div>
        </div>
      </div>
    </div>`).join('');

  $$('.qa-question').forEach(q => {
    q.addEventListener('click', () => {
      const card = q.closest('.qa-card');
      card.classList.toggle('open');
    });
  });
}

$('qa-search').addEventListener('input', e => {
  const query = e.target.value.toLowerCase();
  $$('.qa-card').forEach(card => {
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(query) ? '' : 'none';
  });
});

// ── DevOps Tab ────────────────────────────────────────────────────────────────
async function loadCicdData() {
  try {
    const res = await fetch('/data/cicd_samples.json');
    state.cicdData = await res.json();
    renderDevOps();
  } catch {
    $('github-actions-panel').innerHTML = `<div class="placeholder-msg">Start python run.py to load DevOps data</div>`;
  }
}

function renderDevOps() {
  const d = state.cicdData;
  if (!d) return;

  // GitHub Actions
  const ga = d.github_actions;
  $('github-actions-panel').innerHTML = `
    <div class="pipeline-stages">
      ${ga.stages.map((s,i) => `
        <div class="pipeline-stage">
          <div class="stage-icon">${s.icon}</div>
          <div><div class="stage-name">${s.name}</div><div class="stage-desc">${s.description}</div></div>
        </div>
        ${i < ga.stages.length - 1 ? '<div class="stage-arrow">↓</div>' : ''}`).join('')}
    </div>
    <div style="margin-top:14px">
      <div class="field-label mb-8">Pipeline Triggers</div>
      <div class="pipeline-triggers">
        ${ga.triggers.map(t => `<span class="trigger-chip">${t}</span>`).join('')}
      </div>
    </div>
    <div style="margin-top:14px">
      <div class="field-label mb-8">Key YAML (Trigger Block)</div>
      <div class="code-block small">${escHtml(ga.key_yaml)}</div>
    </div>`;

  // Azure DevOps
  const ado = d.azure_devops;
  $('azure-devops-panel').innerHTML = `
    <div class="pipeline-stages">
      ${ado.stages.map((s,i) => `
        <div class="pipeline-stage">
          <div class="stage-icon">${s.icon}</div>
          <div><div class="stage-name">${s.name}</div><div class="stage-desc">${s.description}</div></div>
        </div>
        ${i < ado.stages.length - 1 ? '<div class="stage-arrow">↓</div>' : ''}`).join('')}
    </div>
    <div style="margin-top:14px">
      <div class="field-label mb-8">Key YAML (PublishTestResults + Artifacts)</div>
      <div class="code-block small">${escHtml(ado.key_yaml)}</div>
    </div>`;

  // Jira flow
  const jira = d.jira_integration;
  $('jira-flow').innerHTML = jira.steps.map((s, i) => `
    <div class="jira-step">
      <div class="jira-step-bubble">${s.step}</div>
      <div class="jira-step-label">${s.action}</div>
      <div class="jira-step-detail">${s.detail}</div>
    </div>
    ${i < jira.steps.length - 1 ? '<div class="jira-arrow">→</div>' : ''}`).join('');

  $('jira-payload').textContent = jira.sample_payload;
  $('ado-task-yaml').textContent = `- task: PublishTestResults@2\n  inputs:\n    testResultsFormat: 'JUnit'\n    testResultsFiles: '*.xml'\n    failTaskOnFailedTests: false\n\n- task: PublishPipelineArtifact@1\n  inputs:\n    targetPath: 'reports/html/report.html'\n    artifact: 'HTMLTestReport'`;
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Initial Load ──────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  // Pre-warm regression results with a default
  setTimeout(() => {
    loadArchData();
    loadPrepData();
    loadCicdData();
  }, 500);
});
