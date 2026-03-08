/* ============================================================
   auth.js — Módulo de autenticación JWT para frontend vanilla
   ============================================================ */

// API_BASE is defined in api.js (loaded after this file) — do NOT declare it here again.
// Using a local fallback only for the login() function below.
const _AUTH_BASE = 'http://localhost:8000';

const AUTH_KEY   = 'cafeteria_token';
const USER_KEY   = 'cafeteria_user';

// ---- IDs de rol que tienen acceso al sistema ----
const ROLES_CON_ACCESO = {
  1: 'Administrador',
  2: 'Cajero',
  6: 'Encargado de Almacén',
};

// ---- Rutas por rol (al hacer login exitoso) ----
const RUTA_POR_ROL = {
  1: 'plantillas/admin.html',
  2: 'plantillas/venta.html',
  6: 'plantillas/compra.html',
};


/* ============================================================
   STORAGE
   ============================================================ */

function guardarSesion(token, usuario) {
  localStorage.setItem(AUTH_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(usuario));
}

function getToken() {
  return localStorage.getItem(AUTH_KEY);
}

function getUsuario() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

function limpiarSesion() {
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(USER_KEY);
}


/* ============================================================
   LOGIN
   ============================================================ */

/**
 * Llama al endpoint POST /auth/login.
 * Guarda el token y datos del usuario en localStorage.
 * Retorna el objeto usuario o lanza Error con mensaje claro.
 */
async function login(email, password) {
  console.log('🔐 [auth.login] Iniciando login con email:', email);
  
  try {
    const endpoint = `${_AUTH_BASE}/auth/login`;
    console.log('📡 [auth.login] Endpoint:', endpoint);
    
    const resp = await fetch(endpoint, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email, password }),
    });

    console.log('📨 [auth.login] Respuesta HTTP:', resp.status, resp.statusText);
    
    const data = await resp.json();
    console.log('📦 [auth.login] Datos recibidos:', data);

    if (!resp.ok) {
      const error = new Error(data.detail || 'Error al iniciar sesión');
      console.error('❌ [auth.login] Error HTTP:', error.message);
      throw error;
    }

    // Verificar que el rol tiene acceso al sistema
    console.log('🔑 [auth.login] Verificando acceso para id_rol:', data.id_rol);
    console.log('📋 [auth.login] ROLES_CON_ACCESO:', ROLES_CON_ACCESO);
    
    if (!ROLES_CON_ACCESO[data.id_rol]) {
      const error = new Error(`El rol "${data.rol}" no tiene acceso al sistema.`);
      console.error('❌ [auth.login] Acceso denegado:', error.message);
      throw error;
    }

    const usuario = {
      id_usuario:  data.id_usuario,
      id_personal: data.id_personal,
      nombre:      data.nombre,
      rol:         data.rol,
      id_rol:      data.id_rol,
    };

    console.log('✅ [auth.login] Usuario autenticado:', usuario);
    guardarSesion(data.access_token, usuario);
    console.log('💾 [auth.login] Sesión guardada en localStorage');
    
    return usuario;
  } catch (err) {
    console.error('❌ [auth.login] Excepción capturada:', err);
    throw err;
  }
}


/* ============================================================
   LOGOUT
   ============================================================ */

function logout() {
  limpiarSesion();
  // Redirigir al login
  window.location.href = '/app/index.html';
}


/* ============================================================
   GUARD — proteger páginas privadas
   ============================================================ */

/**
 * Llama esto al inicio de cada página protegida.
 * Si no hay sesión válida, redirige al login.
 * Opcionalmente verifica que el rol sea uno de los permitidos.
 *
 * @param {number[]} [rolesPermitidos] — array de id_rol, omitir para permitir todos.
 * @returns {object} usuario si la sesión es válida.
 */
function checkAuth(rolesPermitidos) {
  const token   = getToken();
  const usuario = getUsuario();

  if (!token || !usuario) {
    irALogin();
    return null;
  }

  // Verificar expiración del JWT (sin librería: decodificar payload base64)
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (Date.now() / 1000 > payload.exp) {
      limpiarSesion();
      irALogin();
      return null;
    }
  } catch {
    limpiarSesion();
    irALogin();
    return null;
  }

  // Verificar rol si se especificó
  if (rolesPermitidos && !rolesPermitidos.includes(usuario.id_rol)) {
    alert('No tienes permiso para acceder a esta página.');
    history.back();
    return null;
  }

  return usuario;
}

function irALogin() {
  const depth = window.location.pathname.split('/').filter(Boolean).length;
  const prefix = depth > 1 ? '../'.repeat(depth - 1) : '';
  window.location.href = prefix + 'index.html';
}


/* ============================================================
   HELPERS UI
   ============================================================ */

/** Inserta nombre + rol del usuario en el elemento con id="user-info" si existe */
function renderUserInfo() {
  const el = document.getElementById('user-info');
  if (!el) return;
  const u = getUsuario();
  if (u) {
    el.innerHTML = `
      <span class="user-name">${u.nombre}</span>
      <span class="user-role">${u.rol}</span>
    `;
  }
}

/** Headers para fetch autenticado */
function authHeaders() {
  return {
    'Content-Type':  'application/json',
    'Authorization': `Bearer ${getToken()}`,
  };
}
