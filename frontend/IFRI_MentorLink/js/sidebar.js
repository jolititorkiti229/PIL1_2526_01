// Shared sidebar renderer
function renderSidebar(activePage) {
  const navItems = [
    { id:'dashboard', label:'Tableau de bord', href:'dashboard.html', icon:`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>` },
    { id:'profile', label:'Mon profil', href:'profile.html', icon:`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>` },
    { id:'search', label:'Rechercher', href:'search.html', icon:`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>` },
    { id:'offers', label:'Mes offres / demandes', href:'offers.html', icon:`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>` },
    { id:'matches', label:'Mes correspondances', href:'dashboard.html', icon:`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>` },
    { id:'messages', label:'Messagerie', href:'messages.html', icon:`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>`, badge: 3, badgeClass: '' },
    { id:'notifications', label:'Notifications', href:'notifications.html', icon:`<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>`, badge: 5, badgeClass: 'orange' },
  ];

  const html = `
    <div class="sidebar-logo">
      <div class="logo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L2 7l10 5 10-5-10-5z" fill="#fff"/>
          <path d="M2 17l10 5 10-5" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
          <path d="M2 12l10 5 10-5" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <span style="font-family:'Poppins',sans-serif;font-weight:700;font-size:14px;color:#fff;">IFRI_MentorLink</span>
    </div>
    <nav class="sidebar-nav">
      ${navItems.map(item => `
        <a href="${item.href}" class="nav-item ${activePage === item.id ? 'active' : ''}">
          ${item.icon}
          <span>${item.label}</span>
          ${item.badge ? `<span class="nav-badge ${item.badgeClass||''}">${item.badge}</span>` : ''}
        </a>
      `).join('')}
      <a href="index.html" class="nav-item logout" style="margin-top:24px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Déconnexion
      </a>
    </nav>
  `;
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.innerHTML = html;
}
