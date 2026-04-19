/**
 * Eisenhower Task Dashboard - Frontend Application
 * Handles UI rendering and WebSocket communication
 * Supports internationalization (i18n)
 */

// Global state
let currentData = null;
let ws = null;
let currentTab = 'matrix';
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initFilters();
  initLanguageSwitcher();
  connectWebSocket();
  // Initial data load via fetch as fallback
  fetchInitialData();
});

// Initialize language switcher
function initLanguageSwitcher() {
  const langBtn = document.getElementById('langBtn');
  const langDropdown = document.getElementById('langDropdown');

  if (!langBtn || !langDropdown) return;

  // Set initial button state based on current language
  updateLangButton(i18n.getLanguage());

  // Toggle dropdown
  langBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    langDropdown.classList.toggle('show');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', () => {
    langDropdown.classList.remove('show');
  });

  // Language selection
  langDropdown.querySelectorAll('.lang-option').forEach(option => {
    option.addEventListener('click', () => {
      const lang = option.dataset.lang;
      if (i18n.setLanguage(lang)) {
        updateLangButton(lang);
        // Re-render dynamic content
        renderAll();
      }
    });
  });
}

// Update language button display
function updateLangButton(lang) {
  const langBtn = document.getElementById('langBtn');
  const langText = langBtn.querySelector('.lang-text');
  langText.textContent = lang === 'zh-CN' ? '中文' : 'EN';
  langBtn.dataset.current = lang;
}

// Tab switching
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;
      currentTab = tabId;

      // Update active states
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      document.getElementById(tabId).classList.add('active');
    });
  });
}

// Filter buttons
function initFilters() {
  // Customer filters
  const customerFilters = document.querySelectorAll('#customers .filter-btn');
  customerFilters.forEach(btn => {
    btn.addEventListener('click', () => {
      customerFilters.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderCustomers(currentData?.customerProjects, btn.dataset.filter);
    });
  });

  // Delegation filters
  const delegationFilters = document.querySelectorAll('#delegation .filter-btn');
  delegationFilters.forEach(btn => {
    btn.addEventListener('click', () => {
      delegationFilters.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderDelegation(currentData?.delegation, btn.dataset.filter);
    });
  });
}

// WebSocket connection
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}`;

  updateConnectionStatus('connecting');

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('[WebSocket] Connected');
    updateConnectionStatus('connected');
    reconnectAttempts = 0;
  };

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      if (message.type === 'init' || message.type === 'update') {
        currentData = message.data;
        renderAll();
      }
    } catch (e) {
      console.error('[WebSocket] Parse error:', e);
    }
  };

  ws.onclose = () => {
    console.log('[WebSocket] Disconnected');
    updateConnectionStatus('disconnected');

    // Attempt reconnection
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      setTimeout(connectWebSocket, 3000 * reconnectAttempts);
    }
  };

  ws.onerror = (error) => {
    console.error('[WebSocket] Error:', error);
    updateConnectionStatus('disconnected');
  };
}

// Update connection status indicator
function updateConnectionStatus(status) {
  const statusEl = document.getElementById('connectionStatus');
  const dot = statusEl.querySelector('.status-dot');
  const text = statusEl.querySelector('.status-text');

  dot.className = 'status-dot';

  switch (status) {
    case 'connected':
      dot.classList.add('connected');
      text.textContent = i18n.t('status_live');
      break;
    case 'disconnected':
      dot.classList.add('disconnected');
      text.textContent = i18n.t('status_offline');
      break;
    default:
      text.textContent = i18n.t('status_connecting');
  }
}

// Fetch initial data via HTTP
async function fetchInitialData() {
  try {
    const response = await fetch('/api/tasks');
    if (!response.ok) throw new Error('HTTP ' + response.status);

    const data = await response.json();
    currentData = data;
    renderAll();
  } catch (e) {
    console.error('[Fetch] Error:', e);
  }
}

// Render all components
function renderAll() {
  if (!currentData) return;

  renderStats();
  renderMatrix();
  renderCustomers(currentData.customerProjects);
  renderDelegation(currentData.delegation);
  renderMaybe(currentData.maybe);
  updateTimestamp();
}

// Update stats bar
function renderStats() {
  const tasks = currentData.tasks;
  const customers = currentData.customerProjects;
  const delegation = currentData.delegation;
  const maybe = currentData.maybe;

  document.getElementById('q1Count').textContent = tasks?.stats?.q1 || 0;
  document.getElementById('q2Count').textContent = tasks?.stats?.q2 || 0;
  document.getElementById('q3Count').textContent = tasks?.stats?.q3 || 0;
  document.getElementById('q4Count').textContent = tasks?.stats?.q4 || 0;
  document.getElementById('customerCount').textContent = customers?.stats?.total || 0;
  document.getElementById('delegationCount').textContent = delegation?.stats?.total || 0;
  document.getElementById('maybeCount').textContent = maybe?.stats?.total || 0;
}

// Render quadrant matrix
function renderMatrix() {
  const tasks = currentData.tasks;
  if (!tasks) return;

  renderTaskList('q1List', tasks.q1);
  renderTaskList('q2List', tasks.q2);
  renderTaskList('q3List', tasks.q3);
  renderTaskList('q4List', tasks.q4);
}

// Store tooltip elements keyed by task ID for proper cleanup
const activeTooltips = new Map();

// Render a task list
function renderTaskList(elementId, tasks) {
  const container = document.getElementById(elementId);
  if (!container) return;

  // Clean up existing tooltips for this container
  container.querySelectorAll('.task-card').forEach(card => {
    const taskId = card.dataset.taskId;
    if (activeTooltips.has(taskId)) {
      const tooltip = activeTooltips.get(taskId);
      if (tooltip && tooltip.parentNode) {
        tooltip.parentNode.removeChild(tooltip);
      }
      activeTooltips.delete(taskId);
    }
  });

  if (!tasks || tasks.length === 0) {
    container.innerHTML = `<div class="empty-state">${i18n.t('empty_tasks')}</div>`;
    return;
  }

  container.innerHTML = tasks.map(task => `
    <div class="task-card ${task.blocked ? 'blocked' : ''} ${task.priority ? 'priority-' + task.priority.toLowerCase() : ''}" data-task-id="${task.id}">
      <div class="task-header">
        <span class="task-id">#${task.id}</span>
        ${task.priority ? `<span class="task-priority ${task.priority.toLowerCase()}">${task.priority}</span>` : ''}
      </div>
      <div class="task-title">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ''}
      ${task.tags.length > 0 ? `
        <div class="task-tags">
          ${task.tags.map(tag => `<span class="task-tag">${escapeHtml(tag)}</span>`).join('')}
        </div>
      ` : ''}
      <div class="task-meta">
        ${task.created ? `<span>${i18n.t('created_prefix')} ${task.created}</span>` : ''}
        ${task.blocked ? `<span class="blocked-badge">${i18n.t('blocked_badge')}</span>` : ''}
      </div>
    </div>
  `).join('');

  // Add hover event listeners for tooltips
  container.querySelectorAll('.task-card').forEach((card, index) => {
    const task = tasks[index];
    if (!task) return;

    // Create tooltip element and append to body to avoid CSS containment issues
    const tooltip = document.createElement('div');
    tooltip.className = 'task-tooltip';
    tooltip.innerHTML = `
      <div class="tooltip-header">
        <span class="tooltip-id">#${task.id}</span>
        ${task.priority ? `<span class="tooltip-priority ${task.priority.toLowerCase()}">${task.priority}</span>` : ''}
        ${task.blocked ? `<span class="tooltip-blocked">🚫 ${i18n.t('blocked_badge')}</span>` : ''}
      </div>
      <div class="tooltip-title">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="tooltip-section"><div class="tooltip-label">${i18n.t('description')}</div><div class="tooltip-desc">${escapeHtml(task.description)}</div></div>` : ''}
      ${task.subtasks && task.subtasks.length > 0 ? `
        <div class="tooltip-section">
          <div class="tooltip-label">${i18n.t('subtasks')} (${task.subtasks.length})</div>
          <div class="tooltip-subtasks">
            ${task.subtasks.map(sub => `<div class="tooltip-subtask">• ${escapeHtml(sub.title)}${sub.content ? `<br><small>${escapeHtml(sub.content)}</small>` : ''}</div>`).join('')}
          </div>
        </div>
      ` : ''}
      ${task.tags.length > 0 ? `
        <div class="tooltip-section">
          <div class="tooltip-label">${i18n.t('tags')}</div>
          <div class="tooltip-tags">
            ${task.tags.map(tag => `<span class="tooltip-tag">${escapeHtml(tag)}</span>`).join('')}
          </div>
        </div>
      ` : ''}
      <div class="tooltip-meta">
        ${task.created ? `<div><span class="tooltip-label">${i18n.t('created_prefix')}</span> ${task.created}</div>` : ''}
        ${task.updated ? `<div><span class="tooltip-label">${i18n.t('updated_prefix')}</span> ${task.updated}</div>` : ''}
      </div>
    `;
    document.body.appendChild(tooltip);
    activeTooltips.set(String(task.id), tooltip);

    card.addEventListener('mouseenter', (e) => {
      // First show tooltip to get its dimensions
      tooltip.classList.add('show');
      
      // Then calculate position based on actual dimensions
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let left = e.clientX + 15;
      let top = e.clientY + 15;

      // Adjust if tooltip goes off right edge
      if (left + tooltipRect.width > viewportWidth) {
        left = e.clientX - tooltipRect.width - 15;
      }

      // Adjust if tooltip goes off bottom edge
      if (top + tooltipRect.height > viewportHeight) {
        top = e.clientY - tooltipRect.height - 15;
      }

      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });

    card.addEventListener('mouseleave', () => {
      tooltip.classList.remove('show');
    });

    card.addEventListener('mousemove', (e) => {
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      // Calculate position relative to viewport
      let left = e.clientX + 15;
      let top = e.clientY + 15;

      // Adjust if tooltip goes off right edge
      if (left + tooltipRect.width > viewportWidth) {
        left = e.clientX - tooltipRect.width - 15;
      }

      // Adjust if tooltip goes off bottom edge
      if (top + tooltipRect.height > viewportHeight) {
        top = e.clientY - tooltipRect.height - 15;
      }

      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });
  });
}

// Render customer projects
function renderCustomers(data, filter = 'all') {
  const container = document.getElementById('customerList');
  if (!container || !data) return;

  const customers = data.customers || [];

  if (customers.length === 0) {
    container.innerHTML = `<div class="empty-state">${i18n.t('empty_customer')}</div>`;
    return;
  }

  // Clear any existing customer tooltips
  document.querySelectorAll('.customer-tooltip').forEach(t => t.remove());

  container.innerHTML = customers.map(customer => {
    // Filter projects
    let projects = customer.projects || [];
    if (filter === 'active') {
      projects = projects.filter(p => !p.blocked && p.status.toLowerCase().includes('active'));
    } else if (filter === 'blocked') {
      projects = projects.filter(p => p.blocked);
    }

    if (projects.length === 0) return '';

    return `
      <div class="customer-card" data-customer="${escapeHtml(customer.name)}">
        <div class="customer-header">
          <div class="customer-name">${escapeHtml(customer.name)}</div>
          <div class="customer-priority">${escapeHtml(customer.priority)}</div>
        </div>
        <div class="projects-list">
          ${projects.map(project => `
            <div class="project-item" data-project-id="${project.id}">
              <div class="project-header">
                <div class="project-name">${project.id}. ${escapeHtml(project.name)}</div>
                <div class="project-status ${project.blocked ? 'blocked' : project.status.toLowerCase().replace(/\s+/g, '')}">
                  ${project.blocked ? '🟡 ' + i18n.t('status_blocked') : escapeHtml(project.status)}
                </div>
              </div>
              <div class="project-meta">
                <span>${i18n.t('type_prefix')} ${escapeHtml(project.type)}</span>
                <span>${i18n.t('priority_prefix')} ${escapeHtml(project.priority)}</span>
                ${project.lastReview ? `<span>${i18n.t('reviewed_prefix')} ${escapeHtml(project.lastReview)}</span>` : ''}
              </div>
              ${project.notes ? `<div class="project-notes">${escapeHtml(project.notes)}</div>` : ''}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).filter(Boolean).join('') || `<div class="empty-state">${i18n.t('empty_filtered')}</div>`;

  // Add hover tooltips for project items
  container.querySelectorAll('.project-item').forEach(item => {
    const customerCard = item.closest('.customer-card');
    const customerName = customerCard?.dataset.customer || '';
    const projectId = item.dataset.projectId;
    
    // Find project data
    let project = null;
    for (const customer of customers) {
      project = customer.projects?.find(p => p.id.toString() === projectId);
      if (project) break;
    }
    if (!project) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'task-tooltip customer-tooltip';
    tooltip.innerHTML = `
      <div class="tooltip-header">
        <span class="tooltip-id">#${project.id}</span>
        <span class="tooltip-priority">${escapeHtml(customerName)}</span>
      </div>
      <div class="tooltip-title">${escapeHtml(project.name)}</div>
      <div class="tooltip-section">
        <div class="tooltip-label">${i18n.t('status_active')}</div>
        <div class="tooltip-desc">${project.blocked ? '🟡 ' + i18n.t('status_blocked') : escapeHtml(project.status)}</div>
      </div>
      <div class="tooltip-section">
        <div class="tooltip-label">${i18n.t('type_prefix')}</div>
        <div class="tooltip-desc">${escapeHtml(project.type)}</div>
      </div>
      <div class="tooltip-section">
        <div class="tooltip-label">${i18n.t('priority_prefix')}</div>
        <div class="tooltip-desc">${escapeHtml(project.priority)}</div>
      </div>
      ${project.notes ? `<div class="tooltip-section"><div class="tooltip-label">${i18n.t('description')}</div><div class="tooltip-desc">${escapeHtml(project.notes)}</div></div>` : ''}
      <div class="tooltip-meta">
        ${project.created ? `<div><span class="tooltip-label">${i18n.t('created_prefix')}</span> ${project.created}</div>` : ''}
        ${project.lastReview ? `<div><span class="tooltip-label">${i18n.t('reviewed_prefix')}</span> ${project.lastReview}</div>` : ''}
      </div>
    `;
    document.body.appendChild(tooltip);

    item.addEventListener('mouseenter', (e) => {
      tooltip.classList.add('show');
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      let left = e.clientX + 15;
      let top = e.clientY + 15;
      if (left + tooltipRect.width > viewportWidth) left = e.clientX - tooltipRect.width - 15;
      if (top + tooltipRect.height > viewportHeight) top = e.clientY - tooltipRect.height - 15;
      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });

    item.addEventListener('mouseleave', () => tooltip.classList.remove('show'));

    item.addEventListener('mousemove', (e) => {
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      let left = e.clientX + 15;
      let top = e.clientY + 15;
      if (left + tooltipRect.width > viewportWidth) left = e.clientX - tooltipRect.width - 15;
      if (top + tooltipRect.height > viewportHeight) top = e.clientY - tooltipRect.height - 15;
      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });
  });
}

// Render delegation tasks
function renderDelegation(data, filter = 'all') {
  const container = document.getElementById('delegationList');
  if (!container || !data) return;

  let tasks = data.tasks || [];

  if (filter === 'inProgress') {
    tasks = tasks.filter(t => t.status === i18n.t('status_in_progress') || t.status === '进行中');
  } else if (filter === 'overdue') {
    tasks = tasks.filter(t => t.overdue);
  }

  if (tasks.length === 0) {
    container.innerHTML = `<div class="empty-state">${i18n.t('empty_delegation')}</div>`;
    return;
  }

  // Clear existing delegation tooltips
  document.querySelectorAll('.delegation-tooltip').forEach(t => t.remove());

  container.innerHTML = tasks.map(task => `
    <div class="delegation-card ${task.overdue ? 'overdue' : ''}" data-task-id="${task.id}">
      <div class="delegation-header">
        <div class="delegation-title">${task.id}. ${escapeHtml(task.title)}</div>
        <div class="delegation-status ${task.status === i18n.t('status_in_progress') || task.status === '进行中' ? 'inprogress' : 'todo'}">
          ${task.status}
        </div>
      </div>
      ${task.description ? `<div class="delegation-desc">${escapeHtml(task.description)}</div>` : ''}
      <div class="delegation-meta">
        <span class="delegation-assignee">${escapeHtml(task.assignee)}</span>
        ${task.deadline ? `<span class="delegation-deadline ${task.overdue ? 'overdue' : ''}">
          ${task.overdue ? i18n.t('deadline_overdue') : i18n.t('deadline_prefix')} ${escapeHtml(task.deadline)}
        </span>` : ''}
      </div>
    </div>
  `).join('');

  // Add hover tooltips for delegation cards
  container.querySelectorAll('.delegation-card').forEach((card, index) => {
    const task = tasks[index];
    if (!task) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'task-tooltip delegation-tooltip';
    tooltip.innerHTML = `
      <div class="tooltip-header">
        <span class="tooltip-id">#${task.id}</span>
        ${task.overdue ? `<span class="tooltip-blocked">⚠️ ${i18n.t('deadline_overdue')}</span>` : ''}
      </div>
      <div class="tooltip-title">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="tooltip-section"><div class="tooltip-label">${i18n.t('description')}</div><div class="tooltip-desc">${escapeHtml(task.description)}</div></div>` : ''}
      <div class="tooltip-section">
        <div class="tooltip-label">${i18n.t('status_in_progress')}</div>
        <div class="tooltip-desc">${escapeHtml(task.status)}</div>
      </div>
      <div class="tooltip-section">
        <div class="tooltip-label">${i18n.t('assignee_prefix')}</div>
        <div class="tooltip-desc">${escapeHtml(task.assignee)}</div>
      </div>
      ${task.deadline ? `<div class="tooltip-section"><div class="tooltip-label">${i18n.t('deadline_prefix')}</div><div class="tooltip-desc ${task.overdue ? 'overdue' : ''}">${escapeHtml(task.deadline)}</div></div>` : ''}
      ${task.created ? `<div class="tooltip-meta"><span class="tooltip-label">${i18n.t('created_prefix')}</span> ${task.created}</div>` : ''}
    `;
    document.body.appendChild(tooltip);

    card.addEventListener('mouseenter', (e) => {
      tooltip.classList.add('show');
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      let left = e.clientX + 15;
      let top = e.clientY + 15;
      if (left + tooltipRect.width > viewportWidth) left = e.clientX - tooltipRect.width - 15;
      if (top + tooltipRect.height > viewportHeight) top = e.clientY - tooltipRect.height - 15;
      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });

    card.addEventListener('mouseleave', () => tooltip.classList.remove('show'));

    card.addEventListener('mousemove', (e) => {
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      let left = e.clientX + 15;
      let top = e.clientY + 15;
      if (left + tooltipRect.width > viewportWidth) left = e.clientX - tooltipRect.width - 15;
      if (top + tooltipRect.height > viewportHeight) top = e.clientY - tooltipRect.height - 15;
      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });
  });
}

// Render maybe list
function renderMaybe(data) {
  const container = document.getElementById('maybeList');
  if (!container || !data) return;

  const tasks = data.tasks || [];

  if (tasks.length === 0) {
    container.innerHTML = `<div class="empty-state">${i18n.t('empty_maybe')}</div>`;
    return;
  }

  // Clear existing maybe tooltips
  document.querySelectorAll('.maybe-tooltip').forEach(t => t.remove());

  container.innerHTML = tasks.map(task => `
    <div class="maybe-card" data-task-id="${task.id}">
      <div class="maybe-category">${escapeHtml(task.category)}</div>
      <div class="maybe-title">${task.id}. ${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="maybe-desc">${escapeHtml(task.description)}</div>` : ''}
    </div>
  `).join('');

  // Add hover tooltips for maybe cards
  container.querySelectorAll('.maybe-card').forEach((card, index) => {
    const task = tasks[index];
    if (!task) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'task-tooltip maybe-tooltip';
    tooltip.innerHTML = `
      <div class="tooltip-header">
        <span class="tooltip-id">#${task.id}</span>
        <span class="tooltip-priority">${escapeHtml(task.category)}</span>
      </div>
      <div class="tooltip-title">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="tooltip-section"><div class="tooltip-label">${i18n.t('description')}</div><div class="tooltip-desc">${escapeHtml(task.description)}</div></div>` : ''}
      ${task.created ? `<div class="tooltip-meta"><span class="tooltip-label">${i18n.t('created_prefix')}</span> ${task.created}</div>` : ''}
    `;
    document.body.appendChild(tooltip);

    card.addEventListener('mouseenter', (e) => {
      tooltip.classList.add('show');
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      let left = e.clientX + 15;
      let top = e.clientY + 15;
      if (left + tooltipRect.width > viewportWidth) left = e.clientX - tooltipRect.width - 15;
      if (top + tooltipRect.height > viewportHeight) top = e.clientY - tooltipRect.height - 15;
      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });

    card.addEventListener('mouseleave', () => tooltip.classList.remove('show'));

    card.addEventListener('mousemove', (e) => {
      const tooltipRect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      let left = e.clientX + 15;
      let top = e.clientY + 15;
      if (left + tooltipRect.width > viewportWidth) left = e.clientX - tooltipRect.width - 15;
      if (top + tooltipRect.height > viewportHeight) top = e.clientY - tooltipRect.height - 15;
      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    });
  });
}

// Update timestamp
function updateTimestamp() {
  const el = document.getElementById('lastUpdate');
  if (el && currentData?.timestamp) {
    const date = new Date(currentData.timestamp);
    // Use locale based on current language
    const locale = i18n.getLanguage() === 'zh-CN' ? 'zh-CN' : 'en-US';
    el.textContent = date.toLocaleString(locale);
  }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Refresh button handler (manual refresh)
function refreshData() {
  fetchInitialData();
}

// Export for debugging
window.taskDashboard = {
  refresh: refreshData,
  getData: () => currentData,
  getWebSocket: () => ws
};
