/**
 * SENAContigo - Centralized API Client & UI Utilities
 * Base URL: http://uc0w0o00cgwg4wk0kkogog4g.72.62.13.66.sslip.io/api/v1
 */

const API_BASE_REMOTE = 'http://uc0w0o00cgwg4wk0kkogog4g.72.62.13.66.sslip.io/api/v1';

// Determine default API BASE URL (Direct Remote API)
const getApiBaseUrl = () => {
  const customUrl = localStorage.getItem('senacontigo_api_url');
  if (customUrl) return customUrl.replace(/\/$/, '');
  return API_BASE_REMOTE;
};

// Global Toast Notifications System
const Toast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toastContainer';
      this.container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', title = '', duration = 4000) {
    this.init();

    const toast = document.createElement('div');
    toast.className = 'pointer-events-auto transform transition-all duration-300 ease-out translate-x-12 opacity-0 p-4 rounded-xl shadow-lg border text-xs flex items-start gap-3 backdrop-blur-md';

    let bgClass = 'bg-white border-slate-200 text-slate-800';
    let iconClass = 'fa-circle-info text-blue-500';

    if (type === 'success') {
      bgClass = 'bg-emerald-950/90 border-[#27F531]/40 text-white';
      iconClass = 'fa-circle-check text-[#27F531]';
    } else if (type === 'error') {
      bgClass = 'bg-red-950/90 border-red-500/40 text-white';
      iconClass = 'fa-circle-xmark text-red-400';
    } else if (type === 'warning') {
      bgClass = 'bg-amber-950/90 border-amber-500/40 text-white';
      iconClass = 'fa-triangle-exclamation text-amber-400';
    }

    toast.className += ` ${bgClass}`;

    toast.innerHTML = `
      <i class="fas ${iconClass} text-lg mt-0.5"></i>
      <div class="flex-1">
        ${title ? `<h4 class="font-bold mb-0.5 text-sm">${title}</h4>` : ''}
        <p class="leading-relaxed">${message}</p>
      </div>
      <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white transition">
        <i class="fas fa-xmark text-sm"></i>
      </button>
    `;

    this.container.appendChild(toast);

    // Animate In
    requestAnimationFrame(() => {
      toast.classList.remove('translate-x-12', 'opacity-0');
      toast.classList.add('translate-x-0', 'opacity-100');
    });

    // Auto Remove
    if (duration > 0) {
      setTimeout(() => {
        toast.classList.remove('translate-x-0', 'opacity-100');
        toast.classList.add('translate-x-12', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
      }, duration);
    }
  },

  success(msg, title = 'Éxito') { this.show(msg, 'success', title); },
  error(msg, title = 'Error') { this.show(msg, 'error', title); },
  warning(msg, title = 'Advertencia') { this.show(msg, 'warning', title); },
  info(msg, title = 'Información') { this.show(msg, 'info', title); }
};

// Global Loading Indicator
const Loading = {
  overlay: null,

  show(text = 'Cargando información...') {
    if (!this.overlay) {
      this.overlay = document.createElement('div');
      this.overlay.id = 'loadingOverlay';
      this.overlay.className = 'fixed inset-0 bg-[#252525]/60 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-white text-xs gap-3 transition-opacity duration-200';
      this.overlay.innerHTML = `
        <div class="relative w-12 h-12">
          <div class="absolute inset-0 rounded-full border-4 border-[#8FFA94]/30"></div>
          <div class="absolute inset-0 rounded-full border-4 border-t-[#27F531] animate-spin"></div>
        </div>
        <p id="loadingOverlayText" class="font-bold tracking-wider uppercase text-[11px] text-[#8FFA94]">${text}</p>
      `;
      document.body.appendChild(this.overlay);
    } else {
      document.getElementById('loadingOverlayText').innerText = text;
      this.overlay.classList.remove('hidden');
    }
  },

  hide() {
    if (this.overlay) {
      this.overlay.classList.add('hidden');
    }
  }
};

const API = {
  baseUrl: getApiBaseUrl(),

  getToken() {
    return localStorage.getItem('senacontigo_token');
  },

  setToken(token) {
    localStorage.setItem('senacontigo_token', token);
  },

  getUser() {
    const u = localStorage.getItem('senacontigo_user');
    return u ? JSON.parse(u) : null;
  },

  setUser(user) {
    localStorage.setItem('senacontigo_user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('senacontigo_token');
    localStorage.removeItem('senacontigo_user');
    Toast.info('Sesión cerrada correctamente');
    setTimeout(() => {
      window.location.href = window.location.protocol === 'file:' ? 'index.html' : '/';
    }, 500);
  },

  async request(endpoint, options = {}, showLoader = true) {
    if (showLoader) Loading.show();

    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers
    };

    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (showLoader) Loading.hide();

      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        this.logout();
        throw new Error('Su sesión ha expirado. Por favor ingrese de nuevo.');
      }

      const data = await response.json().catch(() => ({ detail: 'Respuesta no válida del servidor' }));

      if (!response.ok) {
        let msg = 'Error en el servidor';
        if (typeof data.detail === 'string') {
          msg = data.detail;
        } else if (Array.isArray(data.detail)) {
          msg = data.detail.map(e => e.msg || e.detail).join(', ');
        }
        throw new Error(msg);
      }

      return data;
    } catch (err) {
      if (showLoader) Loading.hide();
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth
  login(correo, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ correo, password })
    });
  },

  getMe() {
    return this.request('/auth/me');
  },

  getUsuarios(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/usuarios${q ? '?' + q : ''}`);
  },

  createUsuario(data) {
    return this.request('/usuarios', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Organization
  getRegionales() {
    return this.request('/regionales');
  },

  getCentros(regional_id = null) {
    const q = regional_id ? `?regional_id=${regional_id}` : '';
    return this.request(`/centros${q}`);
  },

  // Academic
  getProgramas() {
    return this.request('/programas');
  },

  getFichas(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/fichas${q ? '?' + q : ''}`);
  },

  createFicha(data) {
    return this.request('/fichas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Apprentices & Matriculas
  getAprendices(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/aprendices${q ? '?' + q : ''}`);
  },

  createAprendiz(data) {
    return this.request('/aprendices', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  createMatricula(data) {
    return this.request('/matriculas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Contracts
  getContratos(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/contratos${q ? '?' + q : ''}`);
  },

  getContratosAprendiz(aprendizId) {
    return this.request(`/contratos/aprendiz/${aprendizId}`);
  },

  createContrato(data) {
    return this.request('/contratos', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  updateContrato(id, data) {
    return this.request(`/contratos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  // Benefits
  getBeneficios() {
    return this.request('/beneficios');
  },

  createBeneficio(data) {
    return this.request('/beneficios', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  getBeneficiosAprendiz(aprendizId) {
    return this.request(`/beneficios/aprendiz/${aprendizId}`);
  },

  asignarBeneficio(data) {
    return this.request('/beneficios/aprendiz', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Dynamic Variables
  getCategorias() {
    return this.request('/variables/categorias');
  },

  getVariables(categoria_id = null) {
    const q = categoria_id ? `?categoria_id=${categoria_id}` : '';
    return this.request(`/variables${q}`);
  },

  createVariable(data) {
    return this.request('/variables', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Survey Engine
  getEncuestas(estado = null) {
    const q = estado ? `?estado=${estado}` : '';
    return this.request(`/encuestas${q}`);
  },

  createEncuesta(data) {
    return this.request('/encuestas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  createCorte(encuestaId, data) {
    return this.request(`/encuestas/${encuestaId}/cortes`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Learner Portal
  getEncuestasPendientes() {
    return this.request('/portal/encuestas-pendientes');
  },

  submitRespuestas(encuesta_id, respuestas) {
    return this.request('/portal/responder', {
      method: 'POST',
      body: JSON.stringify({ encuesta_id, respuestas })
    });
  },

  getMiHistorial() {
    return this.request('/portal/mi-historial');
  },

  // Cases & Rules
  getCasos(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/casos${q ? '?' + q : ''}`);
  },

  createCaso(data) {
    return this.request('/casos', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  addSeguimientoCaso(casoId, comentario, nuevoEstado = null) {
    return this.request(`/casos/${casoId}/seguimiento`, {
      method: 'POST',
      body: JSON.stringify({ comentario, nuevo_estado: nuevoEstado })
    });
  },

  getReglas() {
    return this.request('/reglas');
  },

  createRegla(data) {
    return this.request('/reglas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Analytics & Dashboard
  getAnalyticsDashboard(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/analytics/dashboard${q ? '?' + q : ''}`);
  },

  getAnalyticsEvolucion() {
    return this.request('/analytics/evolucion-longitudinal');
  },

  getAnalyticsIndiceAfectacion() {
    return this.request('/analytics/indice-afectacion');
  },

  // Audit Logs
  getAuditLogs(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/audit${q ? '?' + q : ''}`);
  }
};

// Export to window
window.API = API;
window.Toast = Toast;
window.Loading = Loading;

// CSV Export Utility
window.exportToCSV = function(filename, rows) {
  if (!rows || !rows.length) {
    Toast.warning('No hay datos disponibles para exportar');
    return;
  }
  const separator = ',';
  const keys = Object.keys(rows[0]);
  const csvContent =
    keys.join(separator) +
    '\n' +
    rows.map(row => {
      return keys.map(k => {
        let cell = row[k] === null || row[k] === undefined ? '' : row[k];
        cell = cell instanceof Date ? cell.toLocaleString() : cell.toString();
        cell = cell.replace(/"/g, '""');
        if (cell.search(/("|,|\n)/g) >= 0) {
          cell = `"${cell}"`;
        }
        return cell;
      }).join(separator);
    }).join('\n');

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    Toast.success(`Archivo ${filename} exportado exitosamente`);
  }
};
