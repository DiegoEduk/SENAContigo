// Centralized API Client for SENAContigo
const API_BASE = '/api';

const API = {
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
    window.location.href = '/';
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401 && !endpoint.includes('/auth/login')) {
      this.logout();
      throw new Error('Sesión expirada. Por favor inicie sesión nuevamente.');
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Error al procesar la solicitud');
    }
    return data;
  },

  // Auth Endpoints
  login(correo, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ correo, password })
    });
  },

  getMe() {
    return this.request('/auth/me');
  },

  // Organization
  getRegionales() {
    return this.request('/organizacion/regionales');
  },
  getCentros() {
    return this.request('/organizacion/centros');
  },
  getProgramas() {
    return this.request('/organizacion/programas');
  },
  getFichas() {
    return this.request('/organizacion/fichas');
  },
  getAprendices(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/organizacion/aprendices${q ? '?' + q : ''}`);
  },

  // Variables & Categories
  getCategorias() {
    return this.request('/variables/categorias');
  },
  getVariables() {
    return this.request('/variables/');
  },
  createVariable(data) {
    return this.request('/variables/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Surveys
  getEncuestas() {
    return this.request('/encuestas/');
  },
  createEncuesta(data) {
    return this.request('/encuestas/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  getEncuestaDetail(id) {
    return this.request(`/encuestas/${id}`);
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

  // Analytics & Indicators
  getAnalyticsEstadoActual(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/analytics/estado-actual${q ? '?' + q : ''}`);
  },
  getAnalyticsEvolucion() {
    return this.request('/analytics/evolucion-longitudinal');
  },
  getAnalyticsIndiceAfectacion() {
    return this.request('/analytics/indice-afectacion');
  },

  // Cases & Rules
  getReglas() {
    return this.request('/casos/reglas');
  },
  createRegla(data) {
    return this.request('/casos/reglas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  getCasos(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/casos/${q ? '?' + q : ''}`);
  },
  addSeguimientoCaso(casoId, comentario, nuevoEstado = null) {
    return this.request(`/casos/${casoId}/seguimiento`, {
      method: 'POST',
      body: JSON.stringify({ comentario, nuevo_estado: nuevoEstado })
    });
  }
};

window.API = API;
