// PrivLens Frontend Application Logic

let inventoryData = [];
let evaluationData = null;
let summaryData = null;
let rulesData = null;

let chartClasses = null;
let chartGov = null;
let chartEval = null;

// Preset samples for Rule Sandbox (PS-019 classes)
const PRESETS = {
  aadhaar: {
    col: "aadhaar_number",
    samples: "4532 1488 2947\n4916 0128 4912\n8024 0071 8931\n9485 2819 4912"
  },
  pan: {
    col: "pan_card_no",
    samples: "ABCDE1234F\nBKRPK9821Z\nXYZPA4519M\nDELPR8102Q"
  },
  upi: {
    col: "customer_upi_id",
    samples: "aarav.sharma@okhdfcbank\npriya.patel22@okaxis\nrohan.singh@paytm\nsneha@ybl"
  },
  ifsc: {
    col: "bank_ifsc_code",
    samples: "HDFC0001234\nSBIN0000456\nICIC0009876\nUTIB0002345"
  },
  coords: {
    col: "geo_coordinates",
    samples: "12.971599, 77.594566\n28.613939, 77.209023\n19.076090, 72.877426\n13.082680, 80.270721"
  },
  name: {
    col: "customer_name",
    samples: "Aarav Sharma\nPriya Patel\nRohan Singh\nSneha Verma"
  }
};

// Theme state
let currentTheme = localStorage.getItem("privlens_theme") || "dark";

function applyTheme(theme) {
  currentTheme = theme;
  const body = document.body;
  const icon = document.getElementById("icon-theme");
  const label = document.getElementById("label-theme");

  if (theme === "light") {
    body.classList.add("light-theme");
    if (icon) icon.className = "fa-solid fa-sun text-amber-500";
    if (label) label.textContent = "Bright";
    localStorage.setItem("privlens_theme", "light");
  } else {
    body.classList.remove("light-theme");
    if (icon) icon.className = "fa-solid fa-moon text-amber-400";
    if (label) label.textContent = "Dark";
    localStorage.setItem("privlens_theme", "dark");
  }

  updateChartsTheme();
}

function toggleTheme() {
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  applyTheme(newTheme);
}

function updateChartsTheme() {
  const isLight = currentTheme === "light";
  const textColor = isLight ? "#334155" : "#cbd5e1";
  const gridColor = isLight ? "#e2e8f0" : "#334155";

  if (chartClasses && chartClasses.options && chartClasses.options.plugins && chartClasses.options.plugins.legend) {
    chartClasses.options.plugins.legend.labels.color = textColor;
    chartClasses.update();
  }
  if (chartGov && chartGov.options && chartGov.options.plugins && chartGov.options.plugins.legend) {
    chartGov.options.plugins.legend.labels.color = textColor;
    chartGov.update();
  }
  if (chartEval && chartEval.options && chartEval.options.scales) {
    if (chartEval.options.scales.x) chartEval.options.scales.x.ticks.color = textColor;
    if (chartEval.options.scales.y) {
      chartEval.options.scales.y.ticks.color = textColor;
      chartEval.options.scales.y.grid.color = gridColor;
    }
    if (chartEval.options.plugins.legend) {
      chartEval.options.plugins.legend.labels.color = textColor;
    }
    chartEval.update();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  applyTheme(currentTheme);
  fetchAllData();
  setupEventListeners();
  loadSamplePreset('aadhaar');
});

function switchTab(tabId) {
  // Update nav buttons
  document.querySelectorAll(".tab-btn").forEach(btn => {
    if (btn.dataset.tab === tabId) {
      btn.classList.add("bg-slate-800", "text-white");
      btn.classList.remove("text-slate-300");
    } else {
      btn.classList.remove("bg-slate-800", "text-white");
      btn.classList.add("text-slate-300");
    }
  });

  // Toggle tab contents
  document.querySelectorAll(".tab-content").forEach(content => {
    content.classList.add("hidden");
  });
  const target = document.getElementById(`tab-${tabId}`);
  if (target) {
    target.classList.remove("hidden");
  }

  // Resize charts if switching to tabs containing charts
  if (tabId === "evaluation" && chartEval) {
    chartEval.resize();
  }
  if (tabId === "overview") {
    if (chartClasses) chartClasses.resize();
    if (chartGov) chartGov.resize();
  }
}

async function fetchAllData() {
  try {
    const [sumRes, invRes, gapsRes, evalRes, rulesRes] = await Promise.all([
      fetch("/api/summary").then(r => r.json()),
      fetch("/api/inventory").then(r => r.json()),
      fetch("/api/gaps").then(r => r.json()),
      fetch("/api/evaluation").then(r => r.json()),
      fetch("/api/rules").then(r => r.json())
    ]);

    summaryData = sumRes;
    inventoryData = invRes.items || [];
    evaluationData = evalRes;
    rulesData = rulesRes;

    renderOverview();
    renderInventory();
    renderGaps();
    renderEvaluation();
  } catch (err) {
    console.error("Error loading PrivLens data:", err);
  }
}

function renderOverview() {
  if (!summaryData) return;

  // KPI cards
  document.getElementById("stat-total-fields").textContent = summaryData.total_fields;
  document.getElementById("stat-pii-fields").textContent = summaryData.candidate_pii_count;
  document.getElementById("stat-gaps").textContent = summaryData.gap_count;
  document.getElementById("badge-gap-count").textContent = summaryData.gap_count;
  document.getElementById("stat-f1").textContent = (summaryData.evaluation_macro_f1 * 100).toFixed(1) + "%";

  // Predefined Data Classes Definitions Grid
  const grid = document.getElementById("cards-classes-grid");
  if (grid && rulesData && rulesData.data_classes) {
    grid.innerHTML = rulesData.data_classes.map(dc => {
      const colorMap = {
        PID: "border-sky-700 bg-sky-950/40 text-sky-300",
        CNT: "border-emerald-700 bg-emerald-950/40 text-emerald-300",
        GID: "border-amber-700 bg-amber-950/40 text-amber-300",
        FIN: "border-rose-700 bg-rose-950/40 text-rose-300",
        LOC: "border-purple-700 bg-purple-950/40 text-purple-300"
      };
      const clsStyle = colorMap[dc.id] || "border-slate-700 bg-slate-900 text-slate-300";
      const subtypesStr = dc.subtypes ? `<div class='text-[10px] text-slate-400 mt-1'>Subtypes: ${dc.subtypes.join(", ")}</div>` : "";
      return `
        <div class="border rounded-xl p-3 ${clsStyle} flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-xs">${dc.name}</span>
              <span class="text-[10px] font-mono px-1 py-0.2 rounded bg-black/40">${dc.id}</span>
            </div>
            <p class="text-[11px] text-slate-300 opacity-90 leading-relaxed">${dc.description}</p>
            ${subtypesStr}
          </div>
          <div class="mt-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Sensitivity: <span class="text-white">${dc.sensitivity_level}</span>
          </div>
        </div>
      `;
    }).join("");
  }

  // Render Chart 1: PII Classes
  const classDist = summaryData.class_distribution || {};
  const classLabels = Object.keys(classDist);
  const classValues = Object.values(classDist);

  const ctxClass = document.getElementById("chart-data-classes").getContext("2d");
  if (chartClasses) chartClasses.destroy();
  chartClasses = new Chart(ctxClass, {
    type: "doughnut",
    data: {
      labels: classLabels,
      datasets: [{
        data: classValues,
        backgroundColor: ["#38bdf8", "#34d399", "#fbbf24", "#f43f5e", "#a855f7"],
        borderWidth: 2,
        borderColor: "#1e293b"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#cbd5e1", font: { size: 11 } }
        }
      }
    }
  });

  // Render Chart 2: Governance Status Breakdown
  const govDist = summaryData.governance_distribution || {};
  const govLabels = Object.keys(govDist);
  const govValues = Object.values(govDist);

  const ctxGov = document.getElementById("chart-gov-status").getContext("2d");
  if (chartGov) chartGov.destroy();
  chartGov = new Chart(ctxGov, {
    type: "pie",
    data: {
      labels: govLabels,
      datasets: [{
        data: govValues,
        backgroundColor: ["#10b981", "#ef4444", "#f59e0b", "#6366f1"],
        borderWidth: 2,
        borderColor: "#1e293b"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#cbd5e1", font: { size: 11 } }
        }
      }
    }
  });
  updateChartsTheme();
}

function renderInventory() {
  const tbody = document.getElementById("inventory-tbody");
  if (!tbody) return;

  const searchTerm = (document.getElementById("inventory-search")?.value || "").toLowerCase();
  const classFilter = document.getElementById("filter-class")?.value || "ALL";
  const statusFilter = document.getElementById("filter-status")?.value || "ALL";

  const filtered = inventoryData.filter(item => {
    const d = item.discovery;
    const g = item.governance;

    // Search filter
    const matchesSearch = 
      d.source_name.toLowerCase().includes(searchTerm) ||
      (d.table_name && d.table_name.toLowerCase().includes(searchTerm)) ||
      d.column_name.toLowerCase().includes(searchTerm) ||
      (d.candidate_class_name && d.candidate_class_name.toLowerCase().includes(searchTerm));

    if (!matchesSearch) return false;

    // Class filter
    if (classFilter === "PII_ONLY" && !d.is_candidate_pii) return false;
    if (classFilter === "NON_PII" && d.is_candidate_pii) return false;
    if (["PID", "CNT", "GID", "FIN", "LOC"].includes(classFilter) && d.candidate_class_id !== classFilter) return false;

    // Status filter
    if (statusFilter !== "ALL" && g.governance_status !== statusFilter) return false;

    return true;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-500 italic">No matching technical fields found.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map((item, idx) => {
    const d = item.discovery;
    const g = item.governance;

    const sourceLabel = d.table_name ? `${d.source_name} &bull; <span class="font-bold text-sky-300">${d.table_name}</span>` : d.source_name;
    const isPii = d.is_candidate_pii;
    
    // Class Badge
    let classBadge = `<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400">not personal data</span>`;
    if (isPii) {
      const classColors = {
        PID: "bg-sky-950 text-sky-400 border-sky-800",
        CNT: "bg-emerald-950 text-emerald-400 border-emerald-800",
        GID: "bg-amber-950 text-amber-400 border-amber-800",
        FIN: "bg-rose-950 text-rose-400 border-rose-800",
        LOC: "bg-purple-950 text-purple-400 border-purple-800"
      };
      const cClass = classColors[d.candidate_class_id] || "bg-slate-800 text-slate-300";
      classBadge = `<span class="px-2 py-0.5 rounded border text-[11px] font-semibold ${cClass}">${d.candidate_class_name}</span>`;
    }

    // Confidence
    const confVal = Math.round(d.confidence_score * 100);
    const confBar = isPii ? `
      <div class="flex items-center space-x-2">
        <span class="font-bold text-white w-7 text-right">${confVal}%</span>
        <div class="w-16 bg-slate-700 h-1.5 rounded-full overflow-hidden">
          <div class="bg-sky-400 h-1.5 rounded-full" style="width: ${confVal}%"></div>
        </div>
      </div>
    ` : `<span class="text-slate-500">--</span>`;

    // Declared Purpose
    const purp = g.purpose_name ? 
      `<span class="text-slate-200">${g.purpose_name}</span>` : 
      (isPii ? `<span class="text-rose-400 font-semibold"><i class="fa-solid fa-circle-exclamation mr-1"></i>Missing Purpose</span>` : `<span class="text-slate-500">N/A</span>`);

    // Retention
    const ret = g.retention_period_months ? 
      `<span class="text-slate-300">${g.retention_period_months}m <span class="text-[10px] text-slate-500">(${g.retention_trigger})</span></span>` : 
      (isPii ? `<span class="text-amber-400 font-semibold"><i class="fa-solid fa-clock-rotate-left mr-1"></i>Missing</span>` : `<span class="text-slate-500">N/A</span>`);

    // Status
    const statusBadges = {
      ACTIVE: "bg-emerald-950 text-emerald-400 border-emerald-800",
      UNREGISTERED: "bg-rose-950 text-rose-400 border-rose-800",
      INCOMPLETE: "bg-amber-950 text-amber-400 border-amber-800",
      UNLINKED_PURPOSE: "bg-purple-950 text-purple-400 border-purple-800"
    };
    const sBadge = statusBadges[g.governance_status] || "bg-slate-800 text-slate-300 border-slate-700";

    return `
      <tr class="hover:bg-slate-800/40 transition">
        <td class="px-4 py-3 font-mono text-[11px] text-slate-400">${sourceLabel}</td>
        <td class="px-4 py-3 font-semibold text-white">${d.column_name}</td>
        <td class="px-4 py-3">${classBadge}</td>
        <td class="px-4 py-3">${confBar}</td>
        <td class="px-4 py-3 max-w-[200px] truncate">${purp}</td>
        <td class="px-4 py-3">${ret}</td>
        <td class="px-4 py-3">
          <span class="px-2 py-0.5 rounded border text-[10px] font-bold ${sBadge}">${g.governance_status}</span>
        </td>
        <td class="px-4 py-3 text-center">
          <button onclick="openEvidenceModal('${item.field_id}')" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-sky-300 border border-slate-700 text-xs font-medium transition" title="Inspect technical evidence">
            <i class="fa-solid fa-microscope mr-1"></i>Inspect
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function openEvidenceModal(fieldId) {
  const item = inventoryData.find(i => i.field_id === fieldId);
  if (!item) return;

  const d = item.discovery;
  const g = item.governance;

  document.getElementById("modal-field-title").textContent = `Field: ${d.column_name}`;
  document.getElementById("modal-field-source").textContent = `Asset: ${d.source_name}` + (d.table_name ? ` (Table: ${d.table_name})` : "");

  const cBadge = document.getElementById("modal-class-badge");
  cBadge.textContent = d.candidate_class_name || "Non-PII";
  document.getElementById("modal-confidence-badge").textContent = `Calculated Heuristic Confidence: ${Math.round(d.confidence_score * 100)}%`;

  // Render Rules
  const rulesList = document.getElementById("modal-rules-list");
  if (d.evidence_checklist && d.evidence_checklist.length > 0) {
    rulesList.innerHTML = d.evidence_checklist.map(e => `
      <div class="bg-slate-950 border border-slate-800 rounded-lg p-2.5 space-y-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-sky-400">${e.rule_name}</span>
          <span class="text-[10px] font-mono text-slate-400">Rule ID: ${e.rule_id}</span>
        </div>
        <div class="text-[11px] text-slate-300">${e.details}</div>
        <div class="flex items-center space-x-3 text-[10px] text-slate-400 pt-1">
          <span>Header Match: <strong class="${e.matched_by_header ? 'text-emerald-400' : 'text-slate-500'}">${e.matched_by_header ? 'YES' : 'NO'}</strong></span>
          <span>Sample Match: <strong class="${e.matched_by_value ? 'text-emerald-400' : 'text-slate-500'}">${e.sample_match_count}/${e.sample_total_count} (${(e.match_ratio * 100).toFixed(1)}%)</strong></span>
          <span>Score Weight: <strong class="text-amber-400">${e.confidence_contribution}</strong></span>
        </div>
      </div>
    `).join("");
  } else {
    rulesList.innerHTML = `<div class="text-slate-500 italic py-2">No personal data detection rules triggered. Clean technical field.</div>`;
  }

  // Render Masked Samples
  const samplesList = document.getElementById("modal-samples-list");
  if (d.sample_preview_masked && d.sample_preview_masked.length > 0) {
    samplesList.innerHTML = d.sample_preview_masked.map(s => `<div>&bull; ${s}</div>`).join("");
  } else {
    samplesList.innerHTML = `<div class="italic text-slate-600">No samples available.</div>`;
  }

  document.getElementById("modal-evidence").classList.remove("hidden");
}

function closeEvidenceModal() {
  document.getElementById("modal-evidence").classList.add("hidden");
}

function renderGaps(filterSeverity = "ALL") {
  const container = document.getElementById("gaps-container");
  if (!container) return;

  const allGaps = [];
  inventoryData.forEach(item => {
    (item.gaps || []).forEach(gap => {
      allGaps.push({ ...gap, item });
    });
  });

  const filtered = allGaps.filter(g => {
    if (filterSeverity === "ALL") return true;
    return g.severity === filterSeverity;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="bg-slate-800/40 border border-slate-700/60 rounded-xl p-8 text-center text-slate-400">
        <i class="fa-solid fa-circle-check text-emerald-400 text-3xl mb-2"></i>
        <p class="text-sm">No evidence gaps found under this filter criteria.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(gap => {
    const isCritical = gap.severity === "CRITICAL";
    const sevBadge = isCritical ? 
      `<span class="px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800 font-bold text-xs">CRITICAL GAP</span>` :
      `<span class="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800 font-bold text-xs">HIGH SEVERITY</span>`;

    const icon = isCritical ? "fa-shield-virus text-rose-400" : "fa-clock-rotate-left text-amber-400";

    return `
      <div class="bg-slate-800/80 border border-slate-700 rounded-xl p-4 shadow space-y-2">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-700/60 pb-2">
          <div class="flex items-center space-x-2">
            <i class="fa-solid ${icon}"></i>
            <h4 class="text-sm font-bold text-white">${gap.title}</h4>
          </div>
          <div class="flex items-center space-x-2">
            <span class="font-mono text-xs text-slate-400">${gap.field_identifier}</span>
            ${sevBadge}
          </div>
        </div>

        <p class="text-xs text-slate-300 leading-relaxed">${gap.description}</p>

        <div class="bg-slate-900 border border-slate-800 rounded-lg p-2.5 flex items-start space-x-2 text-xs">
          <i class="fa-solid fa-user-shield text-sky-400 mt-0.5"></i>
          <div>
            <span class="font-bold text-slate-200">Recommended Human Action:</span>
            <span class="text-slate-400 ml-1">${gap.human_action_recommendation}</span>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function filterGaps(sev) {
  document.querySelectorAll(".gap-filter-btn").forEach(b => {
    b.classList.remove("active", "bg-slate-700", "text-white");
    b.classList.add("bg-slate-800");
  });
  event.target.classList.add("active", "bg-slate-700", "text-white");
  renderGaps(sev);
}

function renderEvaluation() {
  if (!evaluationData) return;

  // Badges
  document.getElementById("badge-macro-p").textContent = `Macro Precision: ${(evaluationData.macro_precision * 100).toFixed(1)}%`;
  document.getElementById("badge-macro-r").textContent = `Macro Recall: ${(evaluationData.macro_recall * 100).toFixed(1)}%`;
  document.getElementById("badge-macro-f1").textContent = `Macro F1: ${(evaluationData.macro_f1 * 100).toFixed(1)}%`;

  // Render Table
  const tbody = document.getElementById("table-eval-tbody");
  const metrics = evaluationData.class_metrics || {};

  const labels = [];
  const precisions = [];
  const recalls = [];
  const f1s = [];

  tbody.innerHTML = Object.values(metrics).map(m => {
    labels.push(m.class_name);
    precisions.push((m.precision * 100).toFixed(1));
    recalls.push((m.recall * 100).toFixed(1));
    f1s.push((m.f1_score * 100).toFixed(1));

    return `
      <tr class="hover:bg-slate-800/40 transition">
        <td class="px-4 py-3 font-mono font-bold text-sky-400">${m.class_id}</td>
        <td class="px-4 py-3 font-semibold text-white">${m.class_name}</td>
        <td class="px-4 py-3 text-right font-bold text-slate-300">${m.support}</td>
        <td class="px-4 py-3 text-right text-emerald-400 font-bold">${m.true_positives}</td>
        <td class="px-4 py-3 text-right text-rose-400">${m.false_positives}</td>
        <td class="px-4 py-3 text-right text-amber-400">${m.false_negatives}</td>
        <td class="px-4 py-3 text-right font-semibold text-slate-200">${(m.precision * 100).toFixed(1)}%</td>
        <td class="px-4 py-3 text-right font-semibold text-slate-200">${(m.recall * 100).toFixed(1)}%</td>
        <td class="px-4 py-3 text-right font-extrabold text-emerald-400">${(m.f1_score * 100).toFixed(1)}%</td>
      </tr>
    `;
  }).join("");

  // Render Evaluation Chart
  const ctx = document.getElementById("chart-evaluation").getContext("2d");
  if (chartEval) chartEval.destroy();
  chartEval = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Precision (%)",
          data: precisions,
          backgroundColor: "#38bdf8",
          borderRadius: 4
        },
        {
          label: "Recall (%)",
          data: recalls,
          backgroundColor: "#a855f7",
          borderRadius: 4
        },
        {
          label: "F1-Score (%)",
          data: f1s,
          backgroundColor: "#10b981",
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { color: "#94a3b8" },
          grid: { color: "#334155" }
        },
        x: {
          ticks: { color: "#94a3b8" },
          grid: { display: false }
        }
      },
      plugins: {
        legend: {
          labels: { color: "#cbd5e1" }
        }
      }
    }
  });
  updateChartsTheme();
}

function loadSamplePreset(type) {
  const p = PRESETS[type];
  if (!p) return;
  document.getElementById("sandbox-col").value = p.col;
  document.getElementById("sandbox-samples").value = p.samples;
}

async function runSandboxTest() {
  const colName = document.getElementById("sandbox-col").value.trim();
  const samplesText = document.getElementById("sandbox-samples").value;

  try {
    const res = await fetch("/api/test-rule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ column_name: colName, samples: samplesText })
    });
    const data = await res.json();

    document.getElementById("sandbox-empty-msg").classList.add("hidden");
    const resBox = document.getElementById("sandbox-result-content");
    resBox.classList.remove("hidden");

    const clsEl = document.getElementById("sandbox-res-class");
    clsEl.textContent = data.candidate_class_name || "Non-PII Technical Field";

    const confEl = document.getElementById("sandbox-res-conf");
    confEl.textContent = `${Math.round(data.confidence_score * 100)}% Confidence`;

    const evEl = document.getElementById("sandbox-res-evidence");
    if (data.evidence_checklist && data.evidence_checklist.length > 0) {
      evEl.innerHTML = data.evidence_checklist.map(e => `
        <div class="bg-slate-950 p-2 rounded border border-slate-800 text-[11px]">
          <strong class="text-sky-400">${e.rule_name}</strong>: ${e.details}
        </div>
      `).join("");
    } else {
      evEl.innerHTML = `<span class="text-slate-500 italic">No rules matched.</span>`;
    }

    const prevEl = document.getElementById("sandbox-res-preview");
    if (data.masked_previews && data.masked_previews.length > 0) {
      prevEl.innerHTML = data.masked_previews.map(s => `<div>&bull; ${s}</div>`).join("");
    } else {
      prevEl.innerHTML = `<span class="text-slate-500 italic">No previews.</span>`;
    }
  } catch (err) {
    console.error("Sandbox test error:", err);
  }
}

async function triggerRescan() {
  const btn = document.getElementById("btn-rescan");
  const icon = document.getElementById("icon-rescan");
  icon.classList.add("fa-spin");
  btn.disabled = true;

  try {
    await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    await fetchAllData();
  } catch (err) {
    console.error("Error rescanning:", err);
  } finally {
    icon.classList.remove("fa-spin");
    btn.disabled = false;
  }
}

let selectedUploadFiles = [];

function openUploadModal() {
  selectedUploadFiles = [];
  renderSelectedFiles();
  const statusBox = document.getElementById("upload-status-box");
  if (statusBox) {
    statusBox.classList.add("hidden");
    statusBox.textContent = "";
  }
  document.getElementById("modal-upload").classList.remove("hidden");
}

function closeUploadModal() {
  document.getElementById("modal-upload").classList.add("hidden");
}

function handleFileSelect(files) {
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const name = file.name.toLowerCase();
    if (name.endsWith(".csv") || name.endsWith(".db") || name.endsWith(".sqlite") || name.endsWith(".sqlite3")) {
      // Avoid duplicate file names
      if (!selectedUploadFiles.some(f => f.name === file.name)) {
        selectedUploadFiles.push(file);
      }
    }
  }
  renderSelectedFiles();
}

function renderSelectedFiles() {
  const container = document.getElementById("selected-files-container");
  const list = document.getElementById("selected-files-list");
  if (!container || !list) return;

  if (selectedUploadFiles.length === 0) {
    container.classList.add("hidden");
    list.innerHTML = "";
    return;
  }

  container.classList.remove("hidden");
  list.innerHTML = selectedUploadFiles.map((file, idx) => {
    const isDb = file.name.endsWith(".db") || file.name.endsWith(".sqlite") || file.name.endsWith(".sqlite3");
    const icon = isDb ? "fa-database text-amber-400" : "fa-file-csv text-sky-400";
    const sizeKb = (file.size / 1024).toFixed(1);

    return `
      <div class="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs">
        <div class="flex items-center space-x-2">
          <i class="fa-solid ${icon}"></i>
          <span class="font-semibold text-slate-200">${file.name}</span>
          <span class="text-slate-500 font-mono text-[10px]">(${sizeKb} KB)</span>
        </div>
        <button onclick="removeSelectedFile(${idx})" class="text-slate-500 hover:text-rose-400 text-xs transition">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      </div>
    `;
  }).join("");
}

function removeSelectedFile(idx) {
  selectedUploadFiles.splice(idx, 1);
  renderSelectedFiles();
}

async function submitUploadAndScan() {
  const statusBox = document.getElementById("upload-status-box");
  const submitBtn = document.getElementById("btn-submit-upload");
  const playIcon = document.getElementById("icon-upload-play");

  if (selectedUploadFiles.length === 0) {
    statusBox.className = "p-3 rounded-lg text-xs bg-rose-950/70 border border-rose-800 text-rose-300 block";
    statusBox.textContent = "Please select at least one CSV file or SQLite database to scan.";
    return;
  }

  const mode = document.querySelector('input[name="upload-mode"]:checked')?.value || "append";

  const formData = new FormData();
  formData.append("mode", mode);
  selectedUploadFiles.forEach(file => {
    formData.append("files", file);
  });

  submitBtn.disabled = true;
  playIcon.className = "fa-solid fa-circle-notch fa-spin mr-1.5";

  statusBox.className = "p-3 rounded-lg text-xs bg-sky-950/70 border border-sky-800 text-sky-300 block";
  statusBox.textContent = "Uploading and profiling technical personal data heuristics...";

  try {
    const res = await fetch("/api/upload-and-scan", {
      method: "POST",
      body: formData
    });
    const result = await res.json();

    if (!res.ok || result.error) {
      statusBox.className = "p-3 rounded-lg text-xs bg-rose-950/70 border border-rose-800 text-rose-300 block";
      statusBox.textContent = result.error || "Error scanning uploaded files.";
      return;
    }

    statusBox.className = "p-3 rounded-lg text-xs bg-emerald-950/70 border border-emerald-800 text-emerald-300 block";
    statusBox.innerHTML = `
      <strong><i class="fa-solid fa-circle-check mr-1"></i>Scan Complete!</strong>
      Scanned ${result.scanned_fields_count} fields across ${result.scanned_files.length} file(s). 
      Identified <span class="font-bold text-amber-300">${result.new_pii_detected}</span> candidate personal data fields.
    `;

    // Refresh dashboard data
    await fetchAllData();

    // Auto close modal after 1.5 seconds and switch to inventory tab
    setTimeout(() => {
      closeUploadModal();
      switchTab("inventory");
    }, 1500);

  } catch (err) {
    console.error("Upload scan error:", err);
    statusBox.className = "p-3 rounded-lg text-xs bg-rose-950/70 border border-rose-800 text-rose-300 block";
    statusBox.textContent = "Network error during upload and scan: " + err.message;
  } finally {
    submitBtn.disabled = false;
    playIcon.className = "fa-solid fa-play mr-1.5";
  }
}

function setupEventListeners() {
  document.getElementById("inventory-search")?.addEventListener("input", renderInventory);
  document.getElementById("filter-class")?.addEventListener("change", renderInventory);
  document.getElementById("filter-status")?.addEventListener("change", renderInventory);

  // File Upload Drag & Drop & Browse
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("upload-file-input");

  if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
      if (e.target.files) {
        handleFileSelect(e.target.files);
      }
    });

    ["dragenter", "dragover"].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("border-emerald-400", "bg-slate-900");
      });
    });

    ["dragleave", "drop"].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("border-emerald-400", "bg-slate-900");
      });
    });

    dropZone.addEventListener("drop", (e) => {
      if (e.dataTransfer && e.dataTransfer.files) {
        handleFileSelect(e.dataTransfer.files);
      }
    });
  }
}
