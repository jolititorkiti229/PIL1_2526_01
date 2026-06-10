// Génère le HTML de la sidebar
function getSidebarHTML() {
  return `
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-logo">
      <div class="logo-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <span>IFRI_MentorLink</span>
    </div>

    <nav class="sidebar-nav">
      <a href="/pages/dashboard.html" class="nav-item" data-page="dashboard">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/><rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/><rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/><rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/></svg>
        Tableau de bord
      </a>
      <a href="/pages/profile.html" class="nav-item" data-page="profile">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/></svg>
        Mon profil
      </a>
      <a href="/pages/recherche.html" class="nav-item" data-page="recherche">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/><path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        Rechercher
      </a>
      <a href="/pages/offres.html" class="nav-item" data-page="offres">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2"/><polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2"/><line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2"/><line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2"/></svg>
        Mes offres/demandes
      </a>
      <a href="/pages/correspondances.html" class="nav-item" data-page="correspondances">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/><path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="2"/><path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="2"/></svg>
        Mes correspondances
      </a>
      <a href="/pages/messagerie.html" class="nav-item" data-page="messagerie">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2"/></svg>
        Messagerie
        <span class="nav-badge hidden notif-count">0</span>
      </a>
      <a href="/pages/notifications.html" class="nav-item" data-page="notifications">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="2"/><path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="2"/></svg>
        Notifications
        <span class="nav-badge hidden notif-count">0</span>
      </a>
    </nav>

    <div class="sidebar-footer">
      <div class="flex items-center gap-8" style="margin-bottom:12px">
        <div id="sidebar-avatar"></div>
        <div style="overflow:hidden">
          <div id="sidebar-user-name" style="font-size:13px;font-weight:600;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">Chargement...</div>
        </div>
      </div>
      <button onclick="logout()" class="btn btn-ghost w-full" style="color:var(--sidebar-text);justify-content:flex-start;gap:8px">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2"/><polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="2"/><line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2"/></svg>
        Déconnexion
      </button>
    </div>
  </aside>`;
}

// Injecter la sidebar dans la page
function injectSidebar() {
  const placeholder = document.getElementById('sidebar-placeholder');
  if (placeholder) placeholder.outerHTML = getSidebarHTML();
}
