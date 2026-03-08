/* ============================================================
   api.js — Helpers de fetch autenticado, modales y notificaciones
   ============================================================ */

const API_BASE = 'http://localhost:8000';

/* ---- Fetch autenticado ---- */
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  Object.assign(headers, options.headers || {});
  try {
    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    if (res.status === 401) { limpiarSesion(); window.location.href = '/app/index.html'; return null; }
    return res;
  } catch {
    mostrarToast('Sin conexión con el servidor', 'error');
    return null;
  }
}

/* ---- Toast ---- */
let _toastT = null;
function mostrarToast(msg, tipo = 'success') {
  let t = document.getElementById('app-toast');
  if (!t) { t = document.createElement('div'); t.id = 'app-toast'; t.className = 'toast'; document.body.appendChild(t); }
  t.className = `toast toast-${tipo} show`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  t.innerHTML = `<span>${icons[tipo] || '•'}</span> ${msg}`;
  clearTimeout(_toastT);
  _toastT = setTimeout(() => t.classList.remove('show'), 4000);
}

/* ---- Modal ---- */
function abrirModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.display = 'flex';
  requestAnimationFrame(() => el.classList.add('open'));
}
function cerrarModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('open');
  setTimeout(() => { el.style.display = 'none'; }, 200);
}

/* ---- Helpers UI ---- */
function confirmarEliminar(msg = '¿Eliminar este registro?') { return confirm(msg); }
function badgeActivo(v) {
  return v ? '<span class="badge badge-success">Activo</span>' : '<span class="badge badge-error">Inactivo</span>';
}
function esc(s) { return s == null ? '' : String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function formatFecha(iso) { return iso ? new Date(iso).toLocaleDateString('es-BO', {day:'2-digit',month:'2-digit',year:'numeric'}) : '—'; }
function formatBs(n) { return `Bs ${parseFloat(n||0).toFixed(2)}`; }
