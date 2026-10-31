/**
 * PrivyLens - Privacy Evidence Workbench
 * Frontend Application Controller
 */

// Global State
let currentTab = "dashboard";
let inventoryData = [];
let summaryData = null;
let evaluationData = null;
let gapsData = [];
let registeredUploads = [];
let chartGovernance = null;

// Presets for all 18 attributes
const PRESETS = {
  // Class 1: Personal identity (PID)
  name: {
    col: "customer_name",
    samples: "Aarav Sharma\nPriya Patel\nRohan Singh\nSneha Gupta"
  },
  dob: {
    col: "date_of_birth",
    samples: "1992-05-14\n1988-11-20\n2001-02-28\n1975-09-12"
  },
  gender: {
    col: "gender",
    samples: "Male\nFemale\nNon-Binary\nFemale\nMale"
  },
  age: {
    col: "age",
    samples: "28\n34\n45\n19\n52"
  },

  // Class 2: Contact information (CNT)
  email: {
    col: "email_address",
    samples: "aarav.sharma@example.com\npriya.patel@company.org\nrohan@service.io\nsneha.g@domain.net"
  },
  phone: {
    col: "phone_number",
    samples: "+91-9876543210\n+91 9123456789\n9876543210\n+91-8765432109"
  },

  // Class 3: Government identifiers (GID)
  aadhaar: {
    col: "aadhaar_number",
    samples: "4532 1488 2947\n8024 0071 8931\n9201 3847 1029\n5412 8765 4321"
  },
  pan: {
    col: "pan_number",
    samples: "ABCDE1234F\nBNZPK4829G\nXYZPA9876L\nABCPS5678K"
  },
  passport: {
    col: "passport_number",
    samples: "A1234567\nZ9876543\nB2345678\nK3456789"
  },
  voter_id: {
    col: "voter_id",
    samples: "ABC1234567\nXYZ7654321\nDEF2345678\nLMN9876543"
  },
  driving_licence: {
    col: "driving_licence",
    samples: "DL-0420180012345\nMH1420190098765\nKA0520200012345\nTN0120210054321"
  },

  // Class 4: Financial information (FIN)
  bank_account: {
    col: "bank_account_number",
    samples: "123456789012\n98765432109876\n50100234567890\n30987654321"
  },
  ifsc: {
    col: "ifsc_code",
    samples: "HDFC0001234\nSBIN0004567\nICIC0000890\nUTIB0000123"
  },
  credit_card: {
    col: "card_number",
    samples: "4532-0151-1283-0366\n5425-2334-3010-9821\n4000-1234-5678-9010\n4532015112830366"
  },
  upi: {
    col: "upi_id",
    samples: "aarav.sharma@okhdfcbank\nrohan.singh@okaxis\npriya@paytm\nuser123@oksbi"
  },

  // Class 5: Location / address (LOC)
  postal_address: {
    col: "residential_address",
    samples: "123 MG Road, Sector 4\n45 Park Street, Flat 3B\n78 Residency Road, Apt 12\n101 Brigade Road"
  },
  pin_code: {
    col: "pin_code",
    samples: "560001\n110001\n400001\n700001\n500001"
  },
  geo_coords: {
    col: "geo_coordinates",
    samples: "12.971599, 77.594566\n19.076090, 72.877426\n28.613939, 77.209021\n13.082680, 80.270718"
  }
};

// Hero interactive preview data (simulating enterprise console tabs)
const HERO_PREVIEWS = {
  inventory: {
    title: "customer_contact_email",
    badge: "Contact Information · Verified",
    source: "customer_signups.csv",
    rule: "RULE_CNT_EMAIL (100% Match)",
    desc: "Email address detected conforming to standard RFC 5322 pattern. Safe sample inspection in memory with zero data leakage.",
    purpose: "Customer Support & Notifications",
    retention: "36 Months Statutory"
  },
  dashboard: {
    title: "Executive Privacy Dashboard",
    badge: "Real-time System Overview",
    source: "All Loaded Data Sources",
    rule: "18 Attributes across 5 Classes",
    desc: "Complete privacy summary across all files. Discovers 18 personal data attributes, flags missing retention rules, and verifies 100% offline safety.",
    purpose: "System-wide Monitoring",
    retention: "Continuous Monitoring"
  },
  sources: {
    title: "Data Source Registry",
    badge: "CSV & SQLite · Read-Only Mode",
    source: "customer_signups.csv & enterprise.db",
    rule: "Safe Bounded Ingestion (mode=ro)",
    desc: "Reads files strictly in read-only mode. Samples data rows in local memory to discover personal information without modifying original files.",
    purpose: "File Safety & Schema Profiling",
    retention: "Transient In-Memory Only"
  },
  scanner: {
    title: "Discovery Scanner Engine",
    badge: "5 Data Classes Active",
    source: "Instant Local Scan",
    rule: "Multi-Pattern + ML Verification",
    desc: "Instantly scans for Personal Identity, Contact Details, Government IDs, Financial Records, and Locations with high precision.",
    purpose: "Automated Personal Data Detection",
    retention: "Instant Profiling"
  },
  review: {
    title: "kyc_records.csv :: aadhaar_number",
    badge: "Awaiting Human Review",
    source: "kyc_verification_records.csv",
    rule: "RULE_GID_AADHAAR (Strict Check)",
    desc: "Discovered 12-digit Indian national identity number. Ready for human privacy steward confirmation before audit report generation.",
    purpose: "Identity Verification",
    retention: "12 Months Post-Account Closure"
  },
  gaps: {
    title: "GAP: Missing Retention Schedule",
    badge: "Privacy Gap · Action Needed",
    source: "customer_signups.csv :: date_of_birth",
    rule: "Retention Policy Missing",
    desc: "Personal data identified without a declared retention schedule. Flagged automatically so you can fix it before exporting audit reports.",
    purpose: "Age Verification",
    retention: "Not Defined (Needs Review)"
  }
};
// Aliases for compatibility
HERO_PREVIEWS.candidates = HERO_PREVIEWS.inventory;
HERO_PREVIEWS.rules = HERO_PREVIEWS.scanner;
HERO_PREVIEWS.audit = HERO_PREVIEWS.review;

// Document ready
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupDragAndDrop();
  loadAllData();
});

// ==========================================================================
// View Switching: Landing vs Console
// ==========================================================================
function showLandingView() {
  const landing = document.getElementById("landing-view");
  const workspace = document.getElementById("workspace-container");
  const publicNav = document.getElementById("public-nav");
  const landingNav = document.getElementById("landing-nav-links");
  const getStartedBtn = document.getElementById("btn-nav-get-started");
  const consoleTools = document.getElementById("console-header-tools");
  const consoleHorizontalNav = document.getElementById("console-horizontal-nav");

  if (landing) landing.classList.remove("hidden");
  if (workspace) workspace.classList.add("hidden");
  if (publicNav) publicNav.classList.remove("hidden");
  if (landingNav) landingNav.classList.remove("hidden");
  if (getStartedBtn) getStartedBtn.classList.remove("hidden");
  if (consoleTools) {
    consoleTools.classList.add("hidden");
    consoleTools.classList.remove("flex");
  }
  // Ensure enterprise console horizontal navigation is hidden on landing page
  if (consoleHorizontalNav) {
    consoleHorizontalNav.classList.add("hidden");
  }

  // Deactivate horizontal console tabs in landing view
  document.querySelectorAll(".console-tab-item").forEach(link => {
    link.classList.remove("active");
  });

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function openConsoleTab(tabId) {
  const landing = document.getElementById("landing-view");
  const workspace = document.getElementById("workspace-container");
  const publicNav = document.getElementById("public-nav");
  const landingNav = document.getElementById("landing-nav-links");
  const getStartedBtn = document.getElementById("btn-nav-get-started");
  const consoleTools = document.getElementById("console-header-tools");
  const consoleHorizontalNav = document.getElementById("console-horizontal-nav");

  if (landing) landing.classList.add("hidden");
  if (workspace) workspace.classList.remove("hidden");
  if (publicNav) publicNav.classList.remove("hidden");
  if (landingNav) landingNav.classList.add("hidden");
  if (getStartedBtn) getStartedBtn.classList.add("hidden");
  if (consoleTools) {
    consoleTools.classList.remove("hidden");
    consoleTools.classList.add("flex");
  }
  // Make enterprise console horizontal navigation bar visible
  if (consoleHorizontalNav) {
    consoleHorizontalNav.classList.remove("hidden");
  }

  switchConsoleTab(tabId);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showLandingSection(sectionId) {
  showLandingView();
  setTimeout(() => {
    const el = document.getElementById(sectionId);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }, 100);
}

function switchConsoleTab(tabId) {
  currentTab = tabId;

  // Ensure workspace is visible and landing view is hidden
  const landing = document.getElementById("landing-view");
  const workspace = document.getElementById("workspace-container");
  if (landing && !landing.classList.contains("hidden")) {
    landing.classList.add("hidden");
  }
  if (workspace && workspace.classList.contains("hidden")) {
    workspace.classList.remove("hidden");
  }

  const landingNav = document.getElementById("landing-nav-links");
  if (landingNav) landingNav.classList.add("hidden");
  const getStartedBtn = document.getElementById("btn-nav-get-started");
  if (getStartedBtn) getStartedBtn.classList.add("hidden");
  const consoleTools = document.getElementById("console-header-tools");
  if (consoleTools) {
    consoleTools.classList.remove("hidden");
    consoleTools.classList.add("flex");
  }
  const consoleHorizontalNav = document.getElementById("console-horizontal-nav");
  if (consoleHorizontalNav) {
    consoleHorizontalNav.classList.remove("hidden");
  }

  // Hide all tab contents
  document.querySelectorAll(".console-tab-content").forEach(el => {
    el.classList.add("hidden");
  });

  // Show target tab content
  const target = document.getElementById(`tab-${tabId}`);
  if (target) {
    target.classList.remove("hidden");
  }

  // Update horizontal header console active tab
  document.querySelectorAll(".console-tab-item").forEach(link => {
    link.classList.remove("active");
  });
  const activeTab = document.getElementById(`nav-tab-${tabId}`);
  if (activeTab) {
    activeTab.classList.add("active");
    try {
      activeTab.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
    } catch (_) {}
  }

  // Update sidebar active link if exists
  document.querySelectorAll(".side-link").forEach(link => {
    link.classList.remove("side-active");
  });
  const activeLink = document.getElementById(`nav-side-${tabId}`);
  if (activeLink) {
    activeLink.classList.add("side-active");
  }

  // Update workspace top title
  const titles = {
    dashboard: "Executive Privacy Dashboard",
    "data-sources": "Data Source Registry",
    scanner: "Discovery Scanner Engine",
    inventory: "Personal Data Inventory",
    metadata: "Metadata Management (RoPA)",
    review: "Evidence Review Center",
    rules: "Detection Rules & Sandbox",
    evaluation: "Evaluation Center",
    "evidence-gaps": "Evidence Gap Analysis",
    reports: "Reports Center"
  };
  const topTitle = document.getElementById("workspace-top-title");
  if (topTitle) topTitle.textContent = titles[tabId] || "PrivyLens Workspace";

  // Re-render chart if needed
  if (tabId === "dashboard" && chartGovernance) {
    chartGovernance.resize();
  }
}

// Hero interactive preview horizontal tab switcher
function updateHeroPreview(key) {
  const p = HERO_PREVIEWS[key];
  if (!p) return;

  const titleEl = document.getElementById("hero-preview-title");
  const badgeEl = document.getElementById("hero-preview-badge");
  const sourceEl = document.getElementById("hero-preview-source");
  const ruleEl = document.getElementById("hero-preview-rule");
  const descEl = document.getElementById("hero-preview-desc");
  const purposeEl = document.getElementById("hero-preview-purpose");
  const retentionEl = document.getElementById("hero-preview-retention");

  if (titleEl) titleEl.textContent = p.title;
  if (badgeEl) badgeEl.textContent = p.badge;
  if (sourceEl) sourceEl.textContent = p.source;
  if (ruleEl) ruleEl.textContent = p.rule;
  if (descEl) descEl.textContent = p.desc;
  if (purposeEl && p.purpose) purposeEl.textContent = p.purpose;
  if (retentionEl && p.retention) retentionEl.textContent = p.retention;

  // Update selected class on horizontal mockup tabs
  document.querySelectorAll(".window-nav-tab").forEach(tab => {
    tab.classList.remove("tab-selected");
  });
  const activeTab = document.getElementById(`hero-tab-${key}`);
  if (activeTab) {
    activeTab.classList.add("tab-selected");
  } else if (typeof event !== "undefined" && event && event.currentTarget) {
    event.currentTarget.classList.add("tab-selected");
  }
}

// ==========================================================================
// Data Fetching & Sync
// ==========================================================================
async function loadAllData() {
  try {
    const [sumRes, invRes, gapsRes, evalRes, uploadsRes] = await Promise.all([
      fetch("/api/summary").then(r => r.ok ? r.json() : null),
      fetch("/api/inventory").then(r => r.ok ? r.json() : { items: [] }),
      fetch("/api/gaps").then(r => r.ok ? r.json() : { gaps: [] }),
      fetch("/api/evaluation").then(r => r.ok ? r.json() : null),
      fetch("/api/uploads").then(r => r.ok ? r.json() : { uploads: [] })
    ]);

    summaryData = sumRes;
    inventoryData = (invRes && invRes.items) ? invRes.items : [];
    gapsData = (gapsRes && gapsRes.gaps) ? gapsRes.gaps : [];
    evaluationData = evalRes;
    registeredUploads = (uploadsRes && uploadsRes.uploads) ? uploadsRes.uploads : [];

    renderDashboard();
    renderInventory();
    renderEvidenceGaps();
    renderReviewQueue();
    renderRegisteredSources();
    if (evaluationData) renderEvaluationMetrics(evaluationData);

  } catch (err) {
    console.warn("Notice: Initial data load empty or pending scan:", err);
  }
}

// ==========================================================================
// Dashboard Rendering
// ==========================================================================
function renderDashboard() {
  const hasData = inventoryData && inventoryData.length > 0;
  const zeroStateEl = document.getElementById("dashboard-zero-state");

  if (zeroStateEl) {
    if (hasData) {
      zeroStateEl.classList.add("hidden");
    } else {
      zeroStateEl.classList.remove("hidden");
    }
  }

  // Update metric counters
  const sourcesCount = registeredUploads.length > 0 ? registeredUploads.length : (hasData ? 1 : 0);
  const columnsCount = inventoryData.length;
  const piiCount = inventoryData.filter(it => it.discovery.is_candidate_pii).length;
  const gapsCount = gapsData.length;

  const elSources = document.getElementById("metric-sources-count");
  const elCols = document.getElementById("metric-columns-inspected");
  const elPii = document.getElementById("metric-pii-count");
  const elGaps = document.getElementById("metric-gaps-count");

  if (elSources) elSources.textContent = sourcesCount;
  if (elCols) elCols.textContent = columnsCount;
  if (elPii) elPii.textContent = piiCount;
  if (elGaps) elGaps.textContent = gapsCount;
  const elHeaderGaps = document.getElementById("badge-header-gap-count");
  if (elHeaderGaps) elHeaderGaps.textContent = gapsCount;

  // Status numbers
  const awaitingCount = inventoryData.filter(it => it.governance.governance_status === "ACTIVE" || it.governance.governance_status === "UNREGISTERED").length;
  const confirmedCount = inventoryData.filter(it => it.governance.governance_status === "CONFIRMED").length;
  const missingPurpCount = gapsData.filter(g => g.gap_type === "MISSING_PURPOSE").length;
  const missingRetCount = gapsData.filter(g => g.gap_type === "MISSING_RETENTION").length;

  const elAwaiting = document.getElementById("stat-awaiting-review");
  const elConfirmed = document.getElementById("stat-confirmed");
  const elMissPurp = document.getElementById("stat-missing-purpose");
  const elMissRet = document.getElementById("stat-missing-retention");

  if (elAwaiting) elAwaiting.textContent = awaitingCount;
  if (elConfirmed) elConfirmed.textContent = confirmedCount;
  if (elMissPurp) elMissPurp.textContent = missingPurpCount;
  if (elMissRet) elMissRet.textContent = missingRetCount;

  // Class breakdown cards
  const classCounts = {
    "PID": { name: "Personal identity", count: 0, color: "border-blue-500", text: "text-blue-400" },
    "CNT": { name: "Contact information", count: 0, color: "border-emerald-500", text: "text-emerald-400" },
    "GID": { name: "Government identifiers", count: 0, color: "border-amber-500", text: "text-amber-400" },
    "FIN": { name: "Financial information", count: 0, color: "border-purple-500", text: "text-purple-400" },
    "LOC": { name: "Location / address", count: 0, color: "border-rose-500", text: "text-rose-400" }
  };

  inventoryData.forEach(it => {
    const cid = it.discovery.candidate_class_id;
    if (cid && classCounts[cid]) {
      classCounts[cid].count++;
    }
  });

  const cardsContainer = document.getElementById("class-distribution-cards");
  if (cardsContainer) {
    cardsContainer.innerHTML = Object.entries(classCounts).map(([cid, data]) => `
      <div class="p-2.5 rounded bg-[#0e1018] border-l-2 ${data.color} border border-slate-800 flex justify-between items-center">
        <div>
          <span class="text-[9px] font-mono ${data.text} block">${cid}</span>
          <b class="text-white text-xs">${data.name}</b>
        </div>
        <span class="text-sm font-mono font-bold text-slate-200">${data.count}</span>
      </div>
    `).join("");
  }

  // Render Governance Chart
  renderGovernanceChart();

  // Render Dashboard Recent Findings
  const recentFindingsContainer = document.getElementById("dashboard-recent-findings");
  const candidateFields = inventoryData.filter(it => it.discovery.is_candidate_pii);
  if (recentFindingsContainer) {
    if (candidateFields.length === 0) {
      recentFindingsContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></svg></div>
          <h3>No candidate findings</h3>
          <p>Load a data source to profile personal data fields.</p>
        </div>
      `;
    } else {
      recentFindingsContainer.innerHTML = candidateFields.slice(0, 5).map(it => `
        <div class="p-2 bg-[#0e1018] rounded border border-slate-800 flex justify-between items-center text-xs">
          <div>
            <span class="font-mono text-white font-medium">${it.discovery.column_name}</span>
            <small class="text-slate-500 block text-[10px]">${it.discovery.source_name}</small>
          </div>
          <div class="flex items-center gap-2">
            <span class="class-chip">${it.discovery.candidate_class_name || it.discovery.candidate_class_id}</span>
            <span class="font-mono text-[10px] text-violet-400 font-semibold">${Math.round(it.discovery.confidence_score * 100)}%</span>
          </div>
        </div>
      `).join("");
    }
  }

  // Render Dashboard Triage Queue
  const reviewQueueContainer = document.getElementById("dashboard-review-queue");
  if (reviewQueueContainer) {
    if (candidateFields.length === 0) {
      reviewQueueContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg></div>
          <h3>All candidate findings reviewed</h3>
          <p>All discovered fields currently have verification decisions recorded.</p>
        </div>
      `;
    } else {
      reviewQueueContainer.innerHTML = candidateFields.slice(0, 4).map(it => `
        <div class="p-2 bg-[#0e1018] rounded border border-slate-800 flex justify-between items-center text-xs">
          <div>
            <strong class="text-slate-200">${it.discovery.column_name}</strong>
            <small class="text-slate-500 block text-[10px]">Purpose: ${it.governance.purpose_name || 'Unassigned'}</small>
          </div>
          <button onclick="quickConfirmFinding('${it.field_id}')" class="button button-small text-[10px] py-1 px-2">
            Confirm &rarr;
          </button>
        </div>
      `).join("");
    }
  }
}

// Chart.js Governance Chart
function renderGovernanceChart() {
  const ctx = document.getElementById("chart-governance-posture");
  if (!ctx) return;

  const active = inventoryData.filter(it => it.governance.governance_status === "ACTIVE" || it.governance.governance_status === "CONFIRMED").length;
  const incomplete = inventoryData.filter(it => it.governance.governance_status === "INCOMPLETE" || it.governance.governance_status === "UNREGISTERED").length;
  const nonPii = inventoryData.filter(it => !it.discovery.is_candidate_pii).length;

  if (chartGovernance) chartGovernance.destroy();

  chartGovernance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Active / Compliant", "Missing Metadata / Shadow", "Non-PII Technical"],
      datasets: [{
        data: [active || 1, incomplete || 0, nonPii || 0],
        backgroundColor: ["#63B79B", "#D87980", "#333A4C"],
        borderColor: "#10131D",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#A1A8B8", font: { size: 10, family: "'Manrope', sans-serif" } }
        }
      },
      cutout: "70%"
    }
  });
}

// ==========================================================================
// Inventory Table
// ==========================================================================
function renderInventory(filterText = "", filterClass = "ALL") {
  const tbody = document.getElementById("inventory-table-body");
  if (!tbody) return;

  let filtered = [...inventoryData];

  if (filterClass === "PII_ONLY") {
    filtered = filtered.filter(it => it.discovery.is_candidate_pii);
  } else if (filterClass !== "ALL") {
    filtered = filtered.filter(it => it.discovery.candidate_class_id === filterClass);
  }

  if (filterText) {
    const q = filterText.toLowerCase();
    filtered = filtered.filter(it => 
      it.discovery.column_name.toLowerCase().includes(q) ||
      it.discovery.source_name.toLowerCase().includes(q) ||
      (it.governance.purpose_name && it.governance.purpose_name.toLowerCase().includes(q))
    );
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-6 text-slate-500 italic">No fields match the current filters.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(it => {
    const d = it.discovery;
    const g = it.governance;
    const confPercent = Math.round(d.confidence_score * 100);
    const confColor = confPercent >= 80 ? "text-emerald-400" : (confPercent >= 50 ? "text-violet-400" : "text-slate-500");
    const statusClass = g.governance_status === "CONFIRMED" ? "status-confirmed" : (g.governance_status === "ACTIVE" ? "status-ready" : "status-pending");

    return `
      <tr>
        <td class="mono-cell text-slate-400">${d.source_name}${d.table_name ? ' (' + d.table_name + ')' : ''}</td>
        <td class="font-bold text-white font-mono">${d.column_name}</td>
        <td>
          <span class="class-chip">${d.candidate_class_name || d.candidate_class_id || 'not personal data'}</span>
        </td>
        <td>
          <div class="flex items-center gap-1.5">
            <span class="font-mono font-bold ${confColor}">${confPercent}%</span>
          </div>
        </td>
        <td class="text-xs text-slate-300">${g.purpose_name || '<span class="text-rose-400 font-mono text-[10px]">MISSING</span>'}</td>
        <td class="mono-cell text-xs">${g.retention_period_months ? g.retention_period_months + 'm' : '<span class="text-rose-400 text-[10px]">NONE</span>'}</td>
        <td>
          <span class="status-pill ${statusClass}">${g.governance_status}</span>
        </td>
        <td>
          <button onclick="quickConfirmFinding('${it.field_id}')" class="text-[10px] text-violet-300 hover:text-white bg-[#1A1926] border border-slate-700 px-2 py-1 rounded">
            Verify
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function filterInventoryTable() {
  const searchInput = document.getElementById("inventory-search-input");
  const classFilter = document.getElementById("inventory-class-filter");
  const q = searchInput ? searchInput.value.trim() : "";
  const cls = classFilter ? classFilter.value : "ALL";
  renderInventory(q, cls);
}

// ==========================================================================
// Evidence Gap Analysis
// ==========================================================================
function renderEvidenceGaps() {
  const container = document.getElementById("gaps-container");
  const badge = document.getElementById("badge-total-gaps");

  if (badge) badge.textContent = gapsData.length;
  const headerGapBadge = document.getElementById("badge-header-gap-count");
  if (headerGapBadge) headerGapBadge.textContent = gapsData.length;
  if (!container) return;

  if (gapsData.length === 0) {
    container.innerHTML = `
      <div class="panel text-center py-8 text-slate-500 italic">
        No evidence gaps identified. Connect a data source to perform gap analysis.
      </div>
    `;
    return;
  }

  container.innerHTML = gapsData.map(g => {
    const sevBadgeColor = g.severity === "CRITICAL" ? "bg-rose-950 text-rose-300 border-rose-800" : (g.severity === "HIGH" ? "bg-amber-950 text-amber-300 border-amber-800" : "bg-blue-950 text-blue-300 border-blue-800");

    return `
      <div class="panel p-4 m-0 border-l-2 ${g.severity === 'CRITICAL' ? 'border-l-rose-500' : (g.severity === 'HIGH' ? 'border-l-amber-500' : 'border-l-blue-500')}">
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center gap-2">
            <span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold border ${sevBadgeColor}">${g.severity}</span>
            <strong class="text-sm text-white font-mono">${g.field_identifier}</strong>
          </div>
          <span class="class-chip text-[9px]">${g.gap_type}</span>
        </div>
        <p class="text-xs text-slate-300 leading-relaxed mb-2">${g.description}</p>
        <div class="text-[11px] text-slate-400 bg-[#0e1018] p-2 rounded border border-slate-800">
          <strong class="text-violet-300 font-mono text-[10px]">RECOMMENDED HUMAN ACTION:</strong> ${g.human_action_recommendation}
        </div>
      </div>
    `;
  }).join("");
}

// ==========================================================================
// Evidence Review Center (Human in the Loop)
// ==========================================================================
function renderReviewQueue() {
  const container = document.getElementById("review-cards-container");
  if (!container) return;

  const candidateFields = inventoryData.filter(it => it.discovery.is_candidate_pii);

  if (candidateFields.length === 0) {
    container.innerHTML = `
      <div class="panel col-span-2 text-center py-8 text-slate-500 italic">
        No candidate findings in the review queue. Upload a dataset to inspect candidate personal data.
      </div>
    `;
    return;
  }

  container.innerHTML = candidateFields.map(it => {
    const d = it.discovery;
    const g = it.governance;
    const conf = Math.round(d.confidence_score * 100);

    return `
      <div class="finding-card" id="finding-card-${it.field_id}">
        <div class="finding-top">
          <span class="class-chip">${d.candidate_class_name || d.candidate_class_id}</span>
          <span class="status-pill ${g.governance_status === 'CONFIRMED' ? 'status-confirmed' : 'status-pending'}">${g.governance_status}</span>
        </div>

        <div class="finding-title">
          <h3>${d.column_name}</h3>
          <span class="font-mono text-violet-400 font-bold">${conf}% Confidence</span>
        </div>

        <div class="finding-details">
          <div>
            <small>DATA SOURCE</small>
            <b>${d.source_name}</b>
          </div>
          <div>
            <small>DETECTED CLASS</small>
            <b>${d.candidate_class_id} (${d.candidate_class_name || 'N/A'})</b>
          </div>
        </div>

        <div class="evidence-box">
          <b>Rule Evaluation Evidence:</b>
          <p>${d.evidence_checklist.map(e => e.rule_name + ' (' + e.details + ')').join('; ') || 'Header & cell format heuristic match.'}</p>
        </div>

        <div class="grid grid-cols-2 gap-2 text-xs text-slate-400 mt-2">
          <div>
            <span class="text-[9px] block">DECLARED PURPOSE</span>
            <b class="text-white text-[11px]">${g.purpose_name || 'Unassigned'}</b>
          </div>
          <div>
            <span class="text-[9px] block">RETENTION LIMIT</span>
            <b class="text-white text-[11px]">${g.retention_period_months ? g.retention_period_months + ' Months' : 'Unspecified'}</b>
          </div>
        </div>

        <div class="flex items-center gap-2 mt-3 pt-3 border-t border-slate-800">
          <button onclick="recordReviewDecision('${it.field_id}', 'CONFIRMED')" class="button button-small flex-1 bg-emerald-600 hover:bg-emerald-500 text-white">
            Confirm Candidate
          </button>
          <button onclick="recordReviewDecision('${it.field_id}', 'REJECTED')" class="button button-small button-outline flex-1 border-rose-800 text-rose-300 hover:bg-rose-950">
            Reject (Non-PII)
          </button>
        </div>
      </div>
    `;
  }).join("");
}

async function quickConfirmFinding(fieldId) {
  await recordReviewDecision(fieldId, "CONFIRMED");
}

async function recordReviewDecision(fieldId, decision) {
  try {
    const res = await fetch("/api/review-finding", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ field_id: fieldId, decision: decision })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Finding marked as ${decision}`, "success");
      await loadAllData();
    } else {
      showToast(data.error || "Failed to update finding", "error");
    }
  } catch (err) {
    showToast("Error updating review decision", "error");
  }
}

// ==========================================================================
// Registered Data Sources
// ==========================================================================
function renderRegisteredSources() {
  const container = document.getElementById("registered-sources-list");
  const badge = document.getElementById("badge-source-count");

  if (badge) badge.textContent = registeredUploads.length;
  if (!container) return;

  if (registeredUploads.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg></div>
        <h3>No data sources registered</h3>
        <p>Upload a CSV file or SQLite database above to begin personal data discovery.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = registeredUploads.map(f => `
    <div class="p-3 bg-[#11141e] rounded border border-slate-800 flex items-center justify-between text-xs">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded bg-[#1A1F2C] flex items-center justify-center text-violet-400">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path></svg>
        </div>
        <div>
          <strong class="text-white block font-mono">${f.name}</strong>
          <small class="text-slate-400">${(f.size_bytes / 1024).toFixed(1)} KB • ${f.ext.toUpperCase()} Source</small>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="status-pill status-ready">Active</span>
        <button onclick="triggerRescan()" class="button button-outline button-small text-[10px]">
          Re-Scan
        </button>
      </div>
    </div>
  `).join("");
}

async function refreshDataSources() {
  await loadAllData();
  showToast("Data sources refreshed", "info");
}

// ==========================================================================
// Quick Sample Loader
// ==========================================================================
async function loadSampleQuick(sampleName) {
  showToast(`Loading synthetic fixture: ${sampleName}...`, "info");
  try {
    const res = await fetch("/api/load-sample", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample_name: sampleName, mode: "replace" })
    });
    const result = await res.json();
    if (res.ok && result.success) {
      showToast(`Scanned ${result.scanned_fields_count} fields in ${sampleName}!`, "success");
      await loadAllData();
      openConsoleTab("dashboard");
    } else {
      showToast(result.error || "Failed to load sample fixture", "error");
    }
  } catch (err) {
    showToast("Error loading sample fixture", "error");
  }
}

// ==========================================================================
// File Upload & Drag and Drop
// ==========================================================================
function setupDragAndDrop() {
  const dropZone = document.getElementById("console-file-drop");
  if (!dropZone) return;

  ["dragenter", "dragover"].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.add("border-violet-500", "bg-violet-950/20");
    });
  });

  ["dragleave", "drop"].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.remove("border-violet-500", "bg-violet-950/20");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      const input = document.getElementById("console-file-input");
      if (input) {
        input.files = e.dataTransfer.files;
        handleFileSelected({ target: input });
      }
    }
  });
}

function handleFileSelected(e) {
  const label = document.getElementById("console-file-label");
  const files = e.target.files;
  if (!label || !files) return;

  if (files.length === 1) {
    label.textContent = `Selected: ${files[0].name} (${(files[0].size / 1024).toFixed(1)} KB)`;
  } else if (files.length > 1) {
    label.textContent = `Selected ${files.length} files`;
  }
}

async function handleConsoleUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById("console-file-input");
  const statusBox = document.getElementById("upload-status-indicator");
  const btn = document.getElementById("btn-submit-console-upload");

  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
    showToast("Please select a CSV or SQLite file to upload", "error");
    return;
  }

  const formData = new FormData();
  formData.append("mode", "replace");
  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append("files", fileInput.files[i]);
  }

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin inline-block mr-1">&#9696;</span> Ingesting &amp; Profiling...`;
  }

  if (statusBox) {
    statusBox.classList.remove("hidden", "bg-rose-950", "text-rose-300", "bg-emerald-950", "text-emerald-300");
    statusBox.classList.add("bg-sky-950", "text-sky-300", "border", "border-sky-800");
    statusBox.textContent = "Profiling heuristics in transient memory...";
  }

  try {
    const res = await fetch("/api/upload-and-scan", {
      method: "POST",
      body: formData
    });
    const result = await res.json();

    if (!res.ok || result.error) {
      if (statusBox) {
        statusBox.className = "mt-3 p-3 rounded text-xs bg-rose-950 text-rose-300 border border-rose-800 block";
        statusBox.textContent = result.error || "Upload scan error";
      }
      showToast(result.error || "Upload scan failed", "error");
      return;
    }

    if (statusBox) {
      statusBox.className = "mt-3 p-3 rounded text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 block";
      statusBox.innerHTML = `<strong>Scan Complete:</strong> Profiled ${result.scanned_fields_count} fields across ${result.scanned_files.length} repository file(s). Found <span class="font-bold text-amber-300">${result.new_pii_detected}</span> candidate personal-data fields.`;
    }

    showToast("Source registered and scanned successfully!", "success");
    await loadAllData();

    setTimeout(() => {
      switchConsoleTab("inventory");
    }, 1200);

  } catch (err) {
    showToast("Network error uploading dataset: " + err.message, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `Register &amp; Scan Source`;
    }
  }
}

// Reset scan workspace (wipe past results)
async function resetScanWorkspace() {
  if (!confirm("Reset scan workspace? This clears current candidate findings and returns to a clean state.")) return;
  try {
    await fetch("/api/reset-scan", { method: "POST" });
    showToast("Scan workspace reset to clean state", "info");
    await loadAllData();
    switchConsoleTab("dashboard");
  } catch (err) {
    showToast("Error resetting scan workspace", "error");
  }
}

// Trigger re-scan
async function triggerRescan() {
  showToast("Re-running discovery engine heuristics...", "info");
  try {
    const res = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();
    showToast(`Scan refreshed: ${data.total_fields} fields evaluated!`, "success");
    await loadAllData();
  } catch (err) {
    showToast("Error re-scanning sources", "error");
  }
}

// ==========================================================================
// Discovery Scanner Tab
// ==========================================================================
async function triggerDiscoveryScan() {
  const pBar = document.getElementById("scanner-progress-bar");
  const pLabel = document.getElementById("scanner-progress-label");
  const pill = document.getElementById("scanner-status-pill");
  const summaryBox = document.getElementById("scanner-latest-summary");

  if (pill) {
    pill.className = "status-pill status-pending";
    pill.textContent = "SCANNING...";
  }

  // Animate progress
  let progress = 10;
  if (pBar) pBar.style.width = "10%";
  if (pLabel) pLabel.textContent = "10%";

  const interval = setInterval(() => {
    progress += 25;
    if (progress <= 90) {
      if (pBar) pBar.style.width = `${progress}%`;
      if (pLabel) pLabel.textContent = `${progress}%`;
    }
  }, 150);

  try {
    const res = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();

    clearInterval(interval);
    if (pBar) pBar.style.width = "100%";
    if (pLabel) pLabel.textContent = "100%";
    if (pill) {
      pill.className = "status-pill status-completed";
      pill.textContent = "COMPLETED";
    }

    if (summaryBox) {
      summaryBox.innerHTML = `
        <div class="p-3 bg-[#0e1018] rounded border border-slate-800 space-y-1">
          <strong class="text-white text-xs block">Execution Finished Successfully</strong>
          <div>Total columns inspected: <span class="font-mono text-emerald-400 font-bold">${data.total_fields}</span></div>
          <div>Candidate personal-data fields detected: <span class="font-mono text-violet-400 font-bold">${data.candidate_pii_count}</span></div>
          <div class="text-[10px] text-slate-500">Mode: Read-only schema introspection with zero sample value storage.</div>
        </div>
      `;
    }

    showToast("Discovery scan completed successfully", "success");
    await loadAllData();

  } catch (err) {
    clearInterval(interval);
    if (pill) {
      pill.className = "status-pill status-failed";
      pill.textContent = "FAILED";
    }
    showToast("Scan error: " + err.message, "error");
  }
}

// ==========================================================================
// Rule Sandbox Tester
// ==========================================================================
function loadSandboxPreset(key) {
  const p = PRESETS[key];
  if (!p) return;

  const colInput = document.getElementById("sandbox-col-input");
  const samplesInput = document.getElementById("sandbox-samples-input");

  if (colInput) colInput.value = p.col;
  if (samplesInput) samplesInput.value = p.samples;
  showToast(`Loaded preset for ${key.toUpperCase()}`, "info");
}

async function runSandboxTest() {
  const colInput = document.getElementById("sandbox-col-input");
  const samplesInput = document.getElementById("sandbox-samples-input");

  const colName = colInput ? colInput.value.trim() : "test_field";
  const samples = samplesInput ? samplesInput.value : "";

  try {
    const res = await fetch("/api/test-rule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ column_name: colName, samples: samples })
    });
    const data = await res.json();

    const clsBadge = document.getElementById("sandbox-result-class");
    const cnameEl = document.getElementById("sandbox-result-cname");
    const confEl = document.getElementById("sandbox-result-conf");
    const confBar = document.getElementById("sandbox-result-conf-bar");
    const evList = document.getElementById("sandbox-evidence-list");
    const maskedEl = document.getElementById("sandbox-masked-preview");

    const confScore = Math.round((data.confidence_score || 0) * 100);

    if (clsBadge) {
      clsBadge.textContent = data.candidate_class_id || "not personal data";
    }
    if (cnameEl) {
      cnameEl.textContent = data.candidate_class_name || "Clean Technical Field";
    }
    if (confEl) {
      confEl.textContent = `${confScore}%`;
    }
    if (confBar) {
      confBar.style.width = `${confScore}%`;
    }

    if (evList) {
      if (data.evidence_checklist && data.evidence_checklist.length > 0) {
        evList.innerHTML = data.evidence_checklist.map(e => `
          <div class="p-2 bg-[#171522] border border-[#343143] rounded text-[11px]">
            <div class="flex justify-between font-semibold text-violet-300">
              <span>${e.rule_name}</span>
              <span class="font-mono text-emerald-400">Match: ${(e.match_ratio * 100).toFixed(0)}%</span>
            </div>
            <div class="text-[10px] text-slate-400 mt-0.5">${e.details}</div>
          </div>
        `).join("");
      } else {
        evList.innerHTML = `<span class="text-slate-500 italic text-xs">No personal data detection rules triggered. Clean technical field.</span>`;
      }
    }

    if (maskedEl) {
      maskedEl.textContent = (data.masked_previews && data.masked_previews.length > 0) ? data.masked_previews.slice(0, 3).join(", ") : "N/A";
    }

    showToast(`Evaluation completed: ${data.candidate_class_name || 'Clean Field'} (${confScore}%)`, "success");

  } catch (err) {
    showToast("Sandbox test error: " + err.message, "error");
  }
}

// ==========================================================================
// Evaluation Center Rendering
// ==========================================================================
function renderEvaluationMetrics(ev) {
  if (!ev) return;

  const precEl = document.getElementById("eval-macro-precision");
  const recEl = document.getElementById("eval-macro-recall");
  const f1El = document.getElementById("eval-macro-f1");
  const totEl = document.getElementById("eval-total-fields");

  if (precEl) precEl.textContent = `${(ev.macro_precision * 100).toFixed(1)}%`;
  if (recEl) recEl.textContent = `${(ev.macro_recall * 100).toFixed(1)}%`;
  if (f1El) f1El.textContent = `${(ev.macro_f1 * 100).toFixed(1)}%`;
  if (totEl) totEl.textContent = ev.total_evaluated_fields;

  const tbody = document.getElementById("evaluation-table-body");
  if (tbody && ev.class_metrics) {
    tbody.innerHTML = Object.values(ev.class_metrics).map(m => `
      <tr>
        <td class="mono-cell font-bold text-violet-400">${m.class_id}</td>
        <td class="font-medium text-white">${m.class_name}</td>
        <td>${m.support}</td>
        <td class="text-emerald-400 font-mono">${m.true_positives}</td>
        <td class="text-rose-400 font-mono">${m.false_positives}</td>
        <td class="text-amber-400 font-mono">${m.false_negatives}</td>
        <td class="font-bold">${(m.precision * 100).toFixed(1)}%</td>
        <td class="font-bold">${(m.recall * 100).toFixed(1)}%</td>
        <td class="font-bold text-violet-400">${(m.f1_score * 100).toFixed(1)}%</td>
      </tr>
    `).join("");
  }
}

// ==========================================================================
// Theme Management (Dual Dark / Light Mode)
// ==========================================================================
function initTheme() {
  const saved = localStorage.getItem("privylens_theme");
  const isLight = saved === "light";
  document.body.classList.toggle("theme-light", isLight);
  const label = document.getElementById("label-theme");
  if (label) label.textContent = isLight ? "Light" : "Dark";
}

function toggleTheme() {
  const isLight = document.body.classList.toggle("theme-light");
  localStorage.setItem("privylens_theme", isLight ? "light" : "dark");
  const label = document.getElementById("label-theme");
  if (label) label.textContent = isLight ? "Light" : "Dark";
  if (chartGovernance) renderGovernanceChart();
}

// ==========================================================================
// Nav Search Handlers
// ==========================================================================
function handleNavSearch(e) {
  if (e.key === "Enter") {
    handleNavSearchClick();
  }
}

function handleNavSearchClick() {
  const input = document.getElementById("nav-search-input");
  const query = input ? input.value.trim().toLowerCase() : "";
  if (!query) return;

  if (query.includes("rule") || query.includes("regex") || query.includes("pan") || query.includes("aadhaar")) {
    openConsoleTab("rules");
  } else if (query.includes("gap") || query.includes("shadow") || query.includes("purpose")) {
    openConsoleTab("evidence-gaps");
  } else if (query.includes("source") || query.includes("csv") || query.includes("sqlite") || query.includes("upload")) {
    openConsoleTab("data-sources");
  } else if (query.includes("eval") || query.includes("benchmark") || query.includes("f1")) {
    openConsoleTab("evaluation");
  } else {
    openConsoleTab("inventory");
    const invSearch = document.getElementById("inventory-search-input");
    if (invSearch) {
      invSearch.value = query;
      filterInventoryTable();
    }
  }
}

// ==========================================================================
// Toast Notifications
// ==========================================================================
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast-item toast-${type}`;
  toast.textContent = message;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
