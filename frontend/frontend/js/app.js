// IFRI_MentorLink - JavaScript global

// Flash messages auto-hide
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    });
  }, 4000);
});

// Toggle password visibility
function togglePwd(id) {
  const el = document.getElementById(id);
  if (el) el.type = el.type === 'password' ? 'text' : 'password';
}

// Compétences chips toggle
function toggleComp(label, type) {
  const cb = label.querySelector('input');
  setTimeout(() => {
    label.classList.toggle('selected-' + type, cb.checked);
  }, 0);
}

// Fermer modales en cliquant outside
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', function(e) {
    if (e.target === this) this.classList.remove('open');
  });
});
