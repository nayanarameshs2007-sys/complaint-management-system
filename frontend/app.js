// CivicPulse API Frontend Connector & Auth System

const API_BASE = '/api';

// Helper for Priority Badge
function getPriorityBadge(priority) {
  const p = (priority || '').toUpperCase();
  if (p === 'CRITICAL') return `<span class="badge badge-critical">🔴 CRITICAL</span>`;
  if (p === 'HIGH') return `<span class="badge badge-high">🟠 HIGH</span>`;
  if (p === 'MEDIUM') return `<span class="badge badge-medium">🟡 MEDIUM</span>`;
  return `<span class="badge badge-low">🟢 LOW</span>`;
}

// Helper for Status Badge
function getStatusBadge(status) {
  if (status === 'Resolved') return `<span class="badge badge-resolved">✅ RESOLVED</span>`;
  if (status === 'IN PROGRESS' || status === 'In Progress') return `<span class="badge badge-in-progress">⚙️ IN PROGRESS</span>`;
  return `<span class="badge badge-status">📥 ${status || 'Submitted'}</span>`;
}

// --- OFFICER AUTHENTICATION SYSTEM ---

function handleOfficerLogin(event) {
  event.preventDefault();
  const officerId = document.getElementById('officerId').value.trim();
  const department = document.getElementById('department').value;
  const password = document.getElementById('password').value;

  if (!officerId || !department || !password) {
    alert("Please fill in all officer credentials.");
    return;
  }

  // Set session authentication
  sessionStorage.setItem('officerLoggedIn', 'true');
  sessionStorage.setItem('officerId', officerId);
  sessionStorage.setItem('officerDept', department);

  // Redirect to official dashboard
  window.location.href = 'dashboard.html';
}

function checkOfficerAuth() {
  const isLoggedIn = sessionStorage.getItem('officerLoggedIn') === 'true';
  const currentPage = window.location.pathname;

  if ((currentPage.includes('dashboard.html') || currentPage.includes('complaint.html')) && !isLoggedIn) {
    window.location.href = 'login.html';
    return false;
  }

  // Render Officer Info badge in header if logged in
  const officerInfoEl = document.getElementById('officerInfo');
  if (officerInfoEl && isLoggedIn) {
    const id = sessionStorage.getItem('officerId') || 'OFFICER';
    const dept = sessionStorage.getItem('officerDept') || 'General';
    officerInfoEl.innerHTML = `
      <span>🛡️ <strong>${id}</strong> (${dept})</span>
    `;
  }

  return true;
}

function handleLogout() {
  sessionStorage.removeItem('officerLoggedIn');
  sessionStorage.removeItem('officerId');
  sessionStorage.removeItem('officerDept');
  window.location.href = 'login.html';
}

// --- CITIZEN COMPLAINT SUBMISSION ---

async function handleFormSubmit(event) {
  event.preventDefault();
  const desc = document.getElementById('description').value;
  const loc = document.getElementById('location').value;
  const submitBtn = event.target.querySelector('button[type="submit"]');

  submitBtn.innerText = "⏳ Analyzing & Routing...";
  submitBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/complaints`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: desc, location: loc })
    });

    if (!res.ok) throw new Error('Submission failed');
    const data = await res.json();

    sessionStorage.setItem('lastSubmitted', JSON.stringify(data));
    window.location.href = `result.html?id=${data.complaint_id}`;
  } catch (err) {
    alert("Error connecting to backend API. Please ensure server is running.");
    console.error(err);
    submitBtn.innerText = "🚀 Submit Complaint & Analyze";
    submitBtn.disabled = false;
  }
}

// --- COMPLAINT RESULT PAGE ---

async function loadResultData() {
  const resIdEl = document.getElementById('resId');
  if (!resIdEl) return;

  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get('id');

  if (!id) return;

  try {
    const res = await fetch(`${API_BASE}/complaints/${id}`);
    if (!res.ok) throw new Error('Failed to fetch complaint details');
    const data = await res.json();

    document.getElementById('resId').innerText = data.complaint_id;
    document.getElementById('resCategory').innerText = data.category;
    document.getElementById('resPriority').innerHTML = getPriorityBadge(data.priority);
    document.getElementById('resDepartment').innerText = data.department;
    document.getElementById('resStatus').innerHTML = getStatusBadge(data.status);
    document.getElementById('trackLink').href = `track.html?id=${data.complaint_id}`;

    if (data.duplicate_of) {
      const dupDiv = document.createElement('div');
      dupDiv.className = 'card';
      dupDiv.style.cssText = 'background: #fff7ed; border-left: 4px solid var(--priority-high); margin-top: 1rem; text-align: left; padding: 1rem;';
      dupDiv.innerHTML = `
        <h5 style="color: #c2410c; margin-bottom: 0.25rem;">⚠️ Possible Duplicate Detected</h5>
        <p style="font-size: 0.85rem; color: #7c2d12;">
          This issue appears <strong>${data.similarity_score}% similar</strong> to existing complaint <strong>${data.duplicate_of}</strong>. It has been linked to prevent redundant field dispatches.
        </p>
      `;
      document.querySelector('.card').appendChild(dupDiv);
    }
  } catch (err) {
    console.error("Result page load error:", err);
  }
}

// --- TRACK COMPLAINT PAGE ---

async function handleTrackSubmit(event) {
  if (event) event.preventDefault();
  const searchId = document.getElementById('searchId').value.trim();
  if (searchId) loadTrackData(searchId);
}

async function loadTrackData(id) {
  const resultCard = document.getElementById('trackResultCard');
  if (!resultCard) return;

  try {
    const res = await fetch(`${API_BASE}/complaints/${id}`);
    if (!res.ok) {
      alert(`No complaint found with ID: "${id}"`);
      return;
    }
    const item = await res.json();

    document.getElementById('trackId').innerText = item.complaint_id;
    document.getElementById('trackDesc').innerText = item.description;
    document.getElementById('trackLoc').innerText = item.location;
    document.getElementById('trackCategory').innerText = item.category;
    document.getElementById('trackDept').innerText = item.department;
    document.getElementById('trackPriorityBadge').innerHTML = getPriorityBadge(item.priority);
    document.getElementById('trackStatus').innerHTML = getStatusBadge(item.status);
    document.getElementById('trackDate').innerText = `Submitted on ${item.created_at}`;

    const timelineEl = document.getElementById('trackTimeline');
    const isResolved = item.status === 'Resolved';
    const isInProgress = item.status === 'In Progress' || isResolved;

    timelineEl.innerHTML = `
      <li class="timeline-item completed">
        <div class="timeline-title">Complaint Submitted</div>
        <div class="timeline-date">${item.created_at}</div>
      </li>
      <li class="timeline-item completed">
        <div class="timeline-title">AI Analysis & Routing</div>
        <div class="timeline-date">Categorized as ${item.category} → ${item.department}</div>
      </li>
      <li class="timeline-item ${isInProgress ? (isResolved ? 'completed' : 'active') : ''}">
        <div class="timeline-title">Department Assigned</div>
        <div class="timeline-date">${item.department} team dispatched</div>
      </li>
      <li class="timeline-item ${isResolved ? 'completed' : (isInProgress ? 'active' : '')}">
        <div class="timeline-title">${isResolved ? 'Resolved' : 'In Progress'}</div>
        <div class="timeline-date">${isResolved ? 'Issue marked resolved by field officer' : 'Field work underway'}</div>
      </li>
    `;

    resultCard.style.display = 'block';
  } catch (err) {
    console.error("Track load error:", err);
  }
}

// --- OFFICER DASHBOARD ---

async function loadDashboardData() {
  const listEl = document.getElementById('complaintsList');
  if (!listEl) return;

  if (!checkOfficerAuth()) return;

  try {
    // Fetch dashboard stats
    const statsRes = await fetch(`${API_BASE}/stats`);
    if (statsRes.ok) {
      const s = await statsRes.json();
      document.getElementById('statTotal').innerText = s.total;
      document.getElementById('statCritical').innerText = s.critical;
      document.getElementById('statHigh').innerText = s.high;
      document.getElementById('statPending').innerText = s.pending;
      document.getElementById('statResolved').innerText = s.resolved;

      // Toggle duplicate cluster alert banner dynamically
      const banner = document.getElementById('duplicateClusterBanner');
      if (banner && s.duplicates > 0) {
        banner.style.display = 'block';
        const badge = document.getElementById('clusterCountBadge');
        if (badge) badge.innerText = `${s.duplicates} Duplicates Linked`;
      }
    }

    // Apply Filters (Department auto-select based on logged-in officer if assigned)
    const officerDept = sessionStorage.getItem('officerDept');
    const deptSelect = document.getElementById('filterDepartment');
    if (deptSelect && officerDept && officerDept !== 'All' && !deptSelect.dataset.userChanged) {
      deptSelect.value = officerDept;
    }

    const pri = document.getElementById('filterPriority')?.value || '';
    const dept = deptSelect?.value || '';
    const st = document.getElementById('filterStatus')?.value || '';

    const params = new URLSearchParams();
    if (pri) params.append('priority', pri);
    if (dept) params.append('department', dept);
    if (st) params.append('status', st);

    const listRes = await fetch(`${API_BASE}/complaints?${params.toString()}`);
    if (listRes.ok) {
      const items = await listRes.json();

      if (items.length === 0) {
        listEl.innerHTML = `
          <tr>
            <td colspan="7" style="padding: 2rem; text-align: center; color: var(--text-muted);">No complaints match the selected filter criteria.</td>
          </tr>
        `;
        return;
      }

      listEl.innerHTML = items.map(c => `
        <tr style="border-bottom: 1px solid var(--border-color); ${c.duplicate_of ? 'background: #fffbeb;' : ''}">
          <td style="padding: 0.75rem; font-weight: 600; color: var(--primary-color);">
            ${c.complaint_id}
            ${c.duplicate_of ? `<span title="Duplicate of ${c.duplicate_of}" style="font-size:0.75rem; background:#fef3c7; color:#92400e; padding:2px 4px; border-radius:4px; margin-left:4px;">DUP</span>` : ''}
          </td>
          <td style="padding: 0.75rem; max-width: 260px;">${c.description}</td>
          <td style="padding: 0.75rem;">${c.category}</td>
          <td style="padding: 0.75rem;">${c.department}</td>
          <td style="padding: 0.75rem;">${getPriorityBadge(c.priority)}</td>
          <td style="padding: 0.75rem;">${getStatusBadge(c.status)}</td>
          <td style="padding: 0.75rem;">
            <a href="complaint.html?id=${c.complaint_id}" class="btn btn-secondary" style="padding: 0.25rem 0.6rem; font-size: 0.8rem;">View</a>
          </td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error("Dashboard load error:", err);
  }
}

function applyFilters() {
  const deptSelect = document.getElementById('filterDepartment');
  if (deptSelect) deptSelect.dataset.userChanged = "true";
  loadDashboardData();
}

// --- COMPLAINT DETAILS PAGE ---

async function loadComplaintDetails() {
  const detailIdEl = document.getElementById('detailId');
  if (!detailIdEl) return;

  if (!checkOfficerAuth()) return;

  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get('id') || "CMP-1001";

  try {
    const res = await fetch(`${API_BASE}/complaints/${id}`);
    if (!res.ok) return;

    const data = await res.json();

    document.getElementById('detailId').innerText = data.complaint_id;
    document.getElementById('detailDate').innerText = `Submitted on ${data.created_at}`;
    document.getElementById('detailDesc').innerText = data.description;
    document.getElementById('detailLocation').innerText = data.location;
    document.getElementById('detailCategory').innerText = data.category;
    document.getElementById('detailDept').innerText = data.department;
    document.getElementById('detailPriority').innerHTML = getPriorityBadge(data.priority);
    document.getElementById('detailStatus').innerHTML = getStatusBadge(data.status);

    const dupEl = document.getElementById('detailDuplicate');
    if (data.duplicate_of) {
      dupEl.innerHTML = `<span style="color: #c2410c; font-weight: 700;">⚠️ Duplicate of ${data.duplicate_of} (${data.similarity_score}% similarity)</span>`;
    } else if (data.linked_duplicates && data.linked_duplicates.length > 0) {
      dupEl.innerHTML = `<span style="color: #0369a1; font-weight: 700;">🔗 Original Issue (${data.linked_duplicates.length} duplicate complaints linked)</span>`;
    } else {
      dupEl.innerText = "Unique submission (No duplicates)";
    }
  } catch (err) {
    console.error("Complaint details error:", err);
  }
}

async function updateComplaintStatus(newStatus) {
  const id = document.getElementById('detailId').innerText;
  try {
    const res = await fetch(`${API_BASE}/complaints/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });

    if (!res.ok) throw new Error('Status update failed');
    const updated = await res.json();

    document.getElementById('detailStatus').innerHTML = getStatusBadge(updated.status);
    alert(`Complaint status updated to: ${newStatus}`);
  } catch (err) {
    alert("Failed to update status.");
    console.error(err);
  }
}

// Global DOM Loaded Dispatcher
document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('result.html')) loadResultData();
  if (window.location.pathname.includes('track.html')) {
    const id = new URLSearchParams(window.location.search).get('id');
    if (id) {
      document.getElementById('searchId').value = id;
      loadTrackData(id);
    }
  }
  if (window.location.pathname.includes('dashboard.html')) {
    checkOfficerAuth();
    loadDashboardData();
  }
  if (window.location.pathname.includes('complaint.html')) {
    checkOfficerAuth();
    loadComplaintDetails();
  }
});
