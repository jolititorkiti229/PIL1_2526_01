// ===== NAVIGATION =====
function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const page = document.getElementById(pageId);
  if (page) page.classList.add('active');

  // Update sidebar active state
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const navItem = document.querySelector(`[data-page="${pageId}"]`);
  if (navItem) navItem.classList.add('active');

  // Update topbar title
  const titles = {
    'page-dashboard': 'Tableau de bord',
    'page-profile': 'Mon profil',
    'page-search': 'Rechercher',
    'page-offers': 'Mes offres / demandes',
    'page-correspondances': 'Mes correspondances',
    'page-messages': 'Messagerie',
    'page-settings': 'Paramètres',
    'page-mentor-profile': 'Profil du mentor',
    'page-matching': 'Résultats de correspondance',
  };
  const titleEl = document.getElementById('topbar-title');
  if (titleEl && titles[pageId]) titleEl.textContent = titles[pageId];
}

function showAuth(view) {
  document.querySelectorAll('.auth-page').forEach(p => p.classList.remove('active'));
  document.getElementById('auth-' + view)?.classList.add('active');
}

function goToDashboard() {
  document.getElementById('landing-section').style.display = 'none';
  document.getElementById('auth-section').style.display = 'none';
  document.getElementById('app-section').style.display = 'flex';
  showPage('page-dashboard');
}

function goToAuth(view = 'login') {
  document.getElementById('landing-section').style.display = 'none';
  document.getElementById('app-section').style.display = 'none';
  document.getElementById('auth-section').style.display = 'flex';
  showAuth(view);
}

function goToLanding() {
  document.getElementById('auth-section').style.display = 'none';
  document.getElementById('app-section').style.display = 'none';
  document.getElementById('landing-section').style.display = 'block';
}

// ===== MESSAGING =====
function openConversation(name, initials, color) {
  document.querySelectorAll('.conv-item').forEach(c => c.classList.remove('active'));
  event?.currentTarget?.classList.add('active');

  const emptyChat = document.getElementById('empty-chat');
  const activeChat = document.getElementById('active-chat');
  if (emptyChat) emptyChat.style.display = 'none';
  if (activeChat) {
    activeChat.style.display = 'flex';
    const nameEl = activeChat.querySelector('.chat-header-info .name');
    if (nameEl) nameEl.textContent = name;
    const avatarEl = activeChat.querySelector('.chat-header .user-avatar');
    if (avatarEl) {
      avatarEl.style.background = color || 'linear-gradient(135deg, #5B4FE8, #7C3AED)';
      avatarEl.textContent = initials;
    }
  }
}

function sendMessage() {
  const input = document.getElementById('chat-input');
  if (!input || !input.value.trim()) return;
  const messages = document.getElementById('chat-messages');
  if (!messages) return;

  const bubble = document.createElement('div');
  bubble.style.cssText = 'display:flex;flex-direction:column;align-items:flex-end';
  bubble.innerHTML = `
    <div class="msg-bubble sent">${input.value.trim()}</div>
    <div class="msg-time" style="text-align:right">${new Date().toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'})}</div>
  `;
  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
  input.value = '';
}

// Enter key to send
document.addEventListener('DOMContentLoaded', () => {
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
  }
});

// ===== PROFILE TABS =====
function switchProfileTab(tabName) {
  document.querySelectorAll('.profile-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.profile-tab-content').forEach(c => c.style.display = 'none');
  document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
  document.getElementById(`tab-${tabName}`)?.style.setProperty('display', 'block');
}

// ===== PASSWORD TOGGLE =====
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
}
