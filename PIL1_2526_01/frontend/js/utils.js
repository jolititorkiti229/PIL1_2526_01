// ===== IFRI MentorLink - Utilitaires globaux =====

const API_BASE = '/api';

// ===== API Helper =====
async function api(endpoint, options = {}) {
  const defaults = {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers }
  };
  const config = { ...defaults, ...options, headers: { ...defaults.headers, ...options.headers } };
  if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
    config.headers['Content-Type'] = 'application/json';
  }
  if (config.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, config);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw { status: res.status, message: data.error || 'Erreur serveur' };
    return data;
  } catch (e) {
    if (e.status === 401) {
      window.location.href = '/pages/login.html';
    }
    throw e;
  }
}

// ===== Toast =====
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(20px)'; toast.style.transition = '0.3s'; setTimeout(() => toast.remove(), 300); }, 3500);
}

// ===== Auth =====
let currentUser = null;

async function checkAuth(required = true) {
  try {
    currentUser = await api('/auth/me');
    return currentUser;
  } catch {
    if (required) window.location.href = '/pages/login.html';
    return null;
  }
}

async function logout() {
  await api('/auth/logout', { method: 'POST' });
  currentUser = null;
  window.location.href = '/pages/login.html';
}

// ===== Avatar =====
function getInitials(nom, prenom) {
  return ((prenom?.[0] || '') + (nom?.[0] || '')).toUpperCase();
}

function renderAvatar(user, size = 'md') {
  if (user?.photo) {
    return `<img src="${user.photo}" class="avatar avatar-${size}" alt="${user.prenom} ${user.nom}" onerror="this.style.display='none';this.nextSibling.style.display='flex'">
            <span class="avatar avatar-${size}" style="display:none">${getInitials(user.nom, user.prenom)}</span>`;
  }
  return `<span class="avatar avatar-${size}">${getInitials(user?.nom, user?.prenom)}</span>`;
}

// ===== Date formatting =====
function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now - d;
  if (diff < 60000) return 'À l\'instant';
  if (diff < 3600000) return `Il y a ${Math.floor(diff / 60000)} min`;
  if (diff < 86400000) return `Il y a ${Math.floor(diff / 3600000)}h`;
  if (diff < 604800000) return `Il y a ${Math.floor(diff / 86400000)} j`;
  return d.toLocaleDateString('fr-FR');
}

function formatTime(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

// ===== Stars =====
function renderStars(note, max = 5) {
  if (!note) return '<span class="text-muted text-sm">Aucun avis</span>';
  const full = Math.round(note);
  return '★'.repeat(full) + '☆'.repeat(max - full);
}

// ===== Score bar =====
function renderScoreBar(score) {
  const color = score >= 70 ? '#10B981' : score >= 50 ? '#F59E0B' : '#6B7280';
  return `
    <div style="display:flex;align-items:center;gap:8px">
      <div class="compatibility-bar" style="flex:1">
        <div class="compatibility-fill" style="width:${score}%;background:${color}"></div>
      </div>
      <span style="font-size:12px;font-weight:700;color:${color};min-width:36px">${score}%</span>
    </div>`;
}

// ===== Sidebar active link =====
function setActiveSidebarLink() {
  const page = window.location.pathname.split('/').pop();
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href') || '';
    if (href.includes(page)) item.classList.add('active');
    else item.classList.remove('active');
  });
}

// ===== Init sidebar user =====
async function initSidebar() {
  const user = await checkAuth();
  const el = document.getElementById('sidebar-user-name');
  if (el && user) el.textContent = `${user.prenom} ${user.nom}`;
  const avatarEl = document.getElementById('sidebar-avatar');
  if (avatarEl && user) avatarEl.innerHTML = renderAvatar(user, 'sm');

  // Notif count
  try {
    const { count } = await api('/notifications/non-lues');
    if (count > 0) {
      document.querySelectorAll('.notif-count').forEach(el => {
        el.textContent = count;
        el.classList.remove('hidden');
      });
    }
  } catch {}

  setActiveSidebarLink();
}

// ===== Modal =====
function openModal(id) { document.getElementById(id)?.classList.add('active'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('active'); }

document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});

// ===== Loading =====
function showLoading(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = '<div class="loading-center"><div class="spinner"></div></div>';
}

function emptyState(icon, title, subtitle = '', actionHtml = '') {
  return `<div class="empty-state">
    <div class="empty-icon">${icon}</div>
    <h3>${title}</h3>
    ${subtitle ? `<p class="mt-8">${subtitle}</p>` : ''}
    ${actionHtml ? `<div class="mt-16">${actionHtml}</div>` : ''}
  </div>`;
}
