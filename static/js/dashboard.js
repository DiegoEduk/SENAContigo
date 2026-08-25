/**
 * SENAContigo - Dashboard Logic & Controller
 */

let currentUser = null;
let currentTab = 'resumen';
let chartEstadoActual = null;
let chartEvolucion = null;
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', async () => {
  try {
    if (!API.getToken()) {
      showLoginView();
      return;
    }

    currentUser = await API.getMe();
    API.setUser(currentUser);

    // Strictly check if user is ONLY an Aprendiz (Learner)
    const roles = (currentUser.roles || []).map(r => (typeof r === 'string' ? r : r.nombre).toLowerCase());
    if (currentUser.rol) roles.push(currentUser.rol.toLowerCase());
    
    const hasAdminRole = roles.some(r => ['superadmin', 'direccion', 'coordinador', 'instructor', 'lider_bienestar', 'lider_contratacion'].includes(r));
    
    if (roles.includes('aprendiz') && !hasAdminRole) {
      window.location.href = window.location.protocol === 'file:' ? 'aprendiz.html' : '/aprendiz';
      return;
    }

    showWorkspaceView();
  } catch (err) {
    console.error('Error inicializando dashboard:', err);
    showLoginView();
  }
});

function showLoginView() {
  const loginEl = document.getElementById('usuariosLoginContainer');
  const workEl = document.getElementById('usuariosWorkspace');
  const headEl = document.getElementById('usuariosHeaderControls');
  if (loginEl) loginEl.classList.remove('hidden');
  if (workEl) workEl.classList.add('hidden');
  if (headEl) headEl.classList.add('hidden');
}

function showWorkspaceView() {
  const loginEl = document.getElementById('usuariosLoginContainer');
  const workEl = document.getElementById('usuariosWorkspace');
  const headEl = document.getElementById('usuariosHeaderControls');
  if (loginEl) loginEl.classList.add('hidden');
  if (workEl) workEl.classList.remove('hidden');
  if (headEl) headEl.classList.remove('hidden');
  setupUserInterface();
  loadCurrentTab();
}

function togglePasswordVisibility() {
  const pass = document.getElementById('inputPassword');
  const icon = document.getElementById('eyeIcon');
  if (!pass || !icon) return;
  if (pass.type === 'password') {
    pass.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  } else {
    pass.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  }
}

async function handleStaffLogin(e) {
  e.preventDefault();
  const correo = document.getElementById('inputCorreo').value.trim();
  const password = document.getElementById('inputPassword').value;

  if (!correo || !password) {
    Toast.warning('Por favor ingrese su correo y contraseña.');
    return;
  }

  try {
    Loading.show('Autenticando usuario...');
    const res = await API.login(correo, password);
    Loading.hide();

    API.setToken(res.access_token);
    API.setUser(res.usuario);

    Toast.success(`¡Bienvenido(a), ${res.usuario.nombres}!`, 'Inicio de Sesión Exitoso');
    
    currentUser = await API.getMe();
    const roles = (currentUser.roles || []).map(r => (typeof r === 'string' ? r : r.nombre).toLowerCase());
    if (currentUser.rol) roles.push(currentUser.rol.toLowerCase());
    const hasAdminRole = roles.some(r => ['superadmin', 'direccion', 'coordinador', 'instructor', 'lider_bienestar', 'lider_contratacion'].includes(r));
    
    if (roles.includes('aprendiz') && !hasAdminRole) {
      window.location.href = window.location.protocol === 'file:' ? 'aprendiz.html' : '/aprendiz';
      return;
    }

    showWorkspaceView();
  } catch (err) {
    Loading.hide();
    Toast.error(err.message || 'Error al autenticar usuario.', 'Autenticación Fallida');
  }
}

function setupUserInterface() {
  if (!currentUser) return;

  const roles = (currentUser.roles || []).map(r => (typeof r === 'string' ? r : r.nombre).toLowerCase());
  if (currentUser.rol) roles.push(currentUser.rol.toLowerCase());

  const primaryRole = roles[0] || 'usuario';
  
  // Set role badge & name
  const badgeEl = document.getElementById('userRoleBadge');
  if (badgeEl) badgeEl.innerText = primaryRole.toUpperCase();

  const nameEl = document.getElementById('navUserName');
  if (nameEl) nameEl.innerText = `${currentUser.nombres} ${currentUser.apellidos}`;

  const mailEl = document.getElementById('navUserMail');
  if (mailEl) mailEl.innerText = currentUser.correo;

  // Set Scope details
  const scopeEl = document.getElementById('scopeDetails');
  if (scopeEl) {
    if (roles.includes('superadmin')) {
      scopeEl.innerHTML = `<p><i class="fas fa-globe text-sena-primary mr-1"></i> Cobertura Nacional SENA</p>`;
    } else if (roles.includes('direccion') && currentUser.regional_id) {
      scopeEl.innerHTML = `<p><i class="fas fa-map text-sena-primary mr-1"></i> Regional ID: ${currentUser.regional_id}</p>`;
    } else if (roles.includes('coordinador') && currentUser.centro_id) {
      scopeEl.innerHTML = `<p><i class="fas fa-building text-sena-primary mr-1"></i> Centro ID: ${currentUser.centro_id}</p>`;
    } else if (roles.includes('lider_contratacion')) {
      scopeEl.innerHTML = `<p><i class="fas fa-file-contract text-sena-primary mr-1"></i> Módulo de Contratación</p>`;
    } else if (roles.includes('lider_bienestar')) {
      scopeEl.innerHTML = `<p><i class="fas fa-heart text-sena-primary mr-1"></i> Módulo de Bienestar</p>`;
    }
  }

  // Filter sidebar items according to user role permissions
  const menuPermissions = {
    superadmin: ['resumen', 'aprendices', 'fichas', 'contratos', 'beneficios', 'casos', 'variables', 'encuestas', 'analytics', 'audit'],
    direccion: ['resumen', 'aprendices', 'fichas', 'contratos', 'beneficios', 'casos', 'variables', 'encuestas', 'analytics'],
    coordinador: ['resumen', 'aprendices', 'fichas', 'contratos', 'beneficios', 'casos', 'variables', 'encuestas'],
    instructor: ['resumen', 'aprendices', 'fichas', 'casos'],
    lider_contratacion: ['resumen', 'contratos', 'aprendices'],
    lider_bienestar: ['resumen', 'beneficios', 'casos', 'aprendices']
  };

  let allowedTabs = ['resumen', 'aprendices', 'fichas', 'contratos', 'beneficios', 'casos', 'variables', 'encuestas', 'analytics', 'audit'];
  
  if (!roles.includes('superadmin')) {
    allowedTabs = [];
    roles.forEach(r => {
      if (menuPermissions[r]) {
        allowedTabs = [...new Set([...allowedTabs, ...menuPermissions[r]])];
      }
    });
    if (allowedTabs.length === 0) allowedTabs = ['resumen'];
  }

  // Hide non-permitted nav buttons
  const navBtns = document.querySelectorAll('[id^="nav-"]');
  navBtns.forEach(btn => {
    const tabName = btn.id.replace('nav-', '');
    if (!allowedTabs.includes(tabName)) {
      btn.classList.add('hidden');
    } else {
      btn.classList.remove('hidden');
    }
  });

  // Adjust initial tab based on role if default tab is forbidden
  if (!allowedTabs.includes(currentTab)) {
    navSwitch(allowedTabs[0]);
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.toggle('hidden');
}

function navSwitch(tabName) {
  currentTab = tabName;

  // Update nav buttons highlight
  const navBtns = document.querySelectorAll('[id^="nav-"]');
  navBtns.forEach(btn => {
    btn.classList.remove('bg-[#27F531]', 'text-[#252525]', 'font-black');
    btn.classList.add('text-slate-600', 'hover:bg-[#F3F2F2]');
  });

  const activeBtn = document.getElementById(`nav-${tabName}`);
  if (activeBtn) {
    activeBtn.classList.remove('text-slate-600', 'hover:bg-[#F3F2F2]');
    activeBtn.classList.add('bg-[#27F531]', 'text-[#252525]', 'font-black');
  }

  // Update Breadcrumb
  const breadcrumbEl = document.getElementById('breadcrumbCurrent');
  if (breadcrumbEl) {
    const titles = {
      resumen: 'Resumen General',
      aprendices: 'Aprendices & Matrículas',
      fichas: 'Fichas Formativas',
      contratos: 'Contratación de Aprendices',
      beneficios: 'Beneficios Institucionales',
      casos: 'Gestión de Casos & Alertas',
      variables: 'Variables Dinámicas',
      encuestas: 'Engine de Encuestas',
      analytics: 'Evolución Longitudinal',
      audit: 'Auditoría del Sistema'
    };
    breadcrumbEl.innerText = titles[tabName] || tabName;
  }

  // Hide all sections
  const sections = document.querySelectorAll('section[id^="sec-"]');
  sections.forEach(sec => sec.classList.add('hidden'));

  // Show active section
  const activeSec = document.getElementById(`sec-${tabName}`);
  if (activeSec) activeSec.classList.remove('hidden');

  loadCurrentTab();
}

function loadCurrentTab() {
  switch (currentTab) {
    case 'resumen':
      loadResumenData();
      break;
    case 'aprendices':
      loadAprendicesData();
      break;
    case 'fichas':
      loadFichasData();
      break;
    case 'contratos':
      loadContratos();
      break;
    case 'beneficios':
      loadBeneficiosData();
      break;
    case 'casos':
      loadCasosData();
      break;
    case 'variables':
      loadVariablesData();
      break;
    case 'encuestas':
      loadEncuestasData();
      break;
    case 'analytics':
      loadAnalyticsData();
      break;
    case 'audit':
      loadAuditLogsData();
      break;
  }
}

// SECTION 1: RESUMEN GENERAL
async function loadResumenData() {
  try {
    const data = await API.getAnalyticsDashboard();

    document.getElementById('kpiAprendices').innerText = data.total_aprendices || 0;
    document.getElementById('kpiEncuestas').innerText = data.encuestas_activas || 0;
    document.getElementById('kpiAfectados').innerText = data.afectados_grave_critico || 0;
    document.getElementById('kpiContratos').innerText = data.contratos_vigentes || 0;

    renderChartEstadoActual(data.distribucion_afectacion || []);
  } catch (err) {
    Toast.error(err.message, 'Fallo cargando KPIs');
  }
}

function renderChartEstadoActual(distribucion) {
  const ctx = document.getElementById('chartEstadoActual');
  if (!ctx) return;

  if (chartEstadoActual) {
    chartEstadoActual.destroy();
  }

  const labels = distribucion.map(d => d.variable);
  const sinAfectacion = distribucion.map(d => d.sin_afectacion || 0);
  const leve = distribucion.map(d => d.leve || 0);
  const moderada = distribucion.map(d => d.moderada || 0);
  const grave = distribucion.map(d => d.grave || 0);

  chartEstadoActual = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Sin Afectación', data: sinAfectacion, backgroundColor: '#8FFA94' },
        { label: 'Leve', data: leve, backgroundColor: '#63F86B' },
        { label: 'Moderada', data: moderada, backgroundColor: '#27F531' },
        { label: 'Grave / Crítica', data: grave, backgroundColor: '#252525' }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true }
      }
    }
  });
}

// SECTION 2: APRENDICES & MATRÍCULAS
function debounceLoadAprendices() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadAprendicesData(), 300);
}

async function loadAprendicesData() {
  const tbl = document.getElementById('tblAprendices');
  tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">Cargando aprendices...</td></tr>`;

  try {
    const searchVal = document.getElementById('searchAprendices')?.value || '';
    const aprendices = await API.getAprendices({ search: searchVal });
    window.currentAprendicesList = aprendices;

    if (!aprendices || !aprendices.length) {
      tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">No se encontraron aprendices registrados.</td></tr>`;
      return;
    }

    tbl.innerHTML = aprendices.map(ap => `
      <tr class="hover:bg-slate-50 transition">
        <td class="p-3 font-bold text-sena-dark">
          ${ap.nombres} ${ap.apellidos}
        </td>
        <td class="p-3 font-mono">${ap.tipo_documento} ${ap.numero_documento}</td>
        <td class="p-3">
          <div>${ap.correo}</div>
          <div class="text-slate-400 text-[10px]">${ap.celular || 'Sin celular'}</div>
        </td>
        <td class="p-3">
          <div>${ap.direccion_vivienda || 'N/A'}</div>
          <div class="text-slate-400 text-[10px]">${ap.ciudad || ''} ${ap.departamento ? '- ' + ap.departamento : ''}</div>
        </td>
        <td class="p-3">
          <span class="badge-state bg-[#EBF8E1] text-[#2E8800] border border-[#39A900]/30">${ap.matriculas ? ap.matriculas.length : 0} Ficha(s)</span>
        </td>
        <td class="p-3 text-right">
          <button onclick="openModalMatricula(${ap.id})" class="px-2.5 py-1 bg-sena-primary text-sena-dark font-black text-[11px] rounded-lg hover:bg-sena-secondary transition">
            <i class="fas fa-link mr-1"></i> Matricular
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Error al cargar aprendices: ${err.message}</td></tr>`;
  }
}

// SECTION 3: FICHAS FORMATIVAS
async function loadFichasData() {
  const tbl = document.getElementById('tblFichas');
  tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">Cargando fichas...</td></tr>`;

  try {
    const fichas = await API.getFichas();
    if (!fichas || !fichas.length) {
      tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">No se encontraron fichas formativas.</td></tr>`;
      return;
    }

    tbl.innerHTML = fichas.map(f => `
      <tr class="hover:bg-slate-50 transition">
        <td class="p-3 font-bold text-sena-dark font-mono">${f.ficha_caracterizacion}</td>
        <td class="p-3 font-semibold">${f.programa ? f.programa.nombre : f.programa_codigo}</td>
        <td class="p-3 text-slate-500">${f.centro_id}</td>
        <td class="p-3">
          <div>${f.ciudad || 'BOGOTÁ D.C.'}</div>
          <div class="text-slate-400 text-[10px]">${f.departamento || 'BOGOTÁ D.C.'}</div>
        </td>
        <td class="p-3 text-[11px]">
          ${f.fecha_inicial} / ${f.fecha_final}
        </td>
        <td class="p-3">
          <span class="badge-state bg-[#8FFA94] text-sena-dark">${f.estado_ficha}</span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Error al cargar fichas: ${err.message}</td></tr>`;
  }
}

// SECTION 4: CONTRATACIÓN DE APRENDICES
async function loadContratos() {
  const tbl = document.getElementById('tblContratos');
  tbl.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-400">Cargando contratos...</td></tr>`;

  try {
    const searchVal = document.getElementById('searchContratos')?.value || '';
    const estadoVal = document.getElementById('filterEstadoContrato')?.value || '';

    const params = {};
    if (searchVal) params.search = searchVal;
    if (estadoVal) params.estado = estadoVal;

    const contratos = await API.getContratos(params);
    window.currentContratosList = contratos;

    if (!contratos || !contratos.length) {
      tbl.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-400">No se encontraron contratos de aprendizaje registrados.</td></tr>`;
      return;
    }

    tbl.innerHTML = contratos.map(c => {
      let stateBadgeClass = 'bg-slate-200 text-slate-800';
      if (c.estado_contrato === 'EN PATROCINIO') stateBadgeClass = 'bg-indigo-100 text-indigo-900 border border-indigo-300';
      if (c.estado_contrato === 'EN ETAPA PRACTICA') stateBadgeClass = 'bg-[#EBF8E1] text-[#2E8800] border border-[#39A900]/30';
      if (c.estado_contrato === 'ACTIVO') stateBadgeClass = 'bg-blue-100 text-blue-900';
      if (c.estado_contrato === 'FINALIZADO') stateBadgeClass = 'bg-slate-800 text-white';
      if (c.estado_contrato === 'CANCELADO') stateBadgeClass = 'bg-red-100 text-red-900';

      return `
        <tr class="hover:bg-slate-50 transition">
          <td class="p-3 font-bold text-sena-dark">${c.nombre_empresa}</td>
          <td class="p-3 font-semibold">${c.aprendiz_nombre || 'Aprendiz ID ' + c.aprendiz_id}</td>
          <td class="p-3 font-mono">${c.ficha_caracterizacion || 'N/A'}</td>
          <td class="p-3">
            <div>${c.ciudad || 'N/A'}</div>
            <div class="text-slate-400 text-[10px]">${c.departamento || ''}</div>
          </td>
          <td class="p-3 text-[11px]">${c.fecha_inicio_contrato} ${c.fecha_fin_contrato ? '/ ' + c.fecha_fin_contrato : ''}</td>
          <td class="p-3">
            <span class="badge-state ${stateBadgeClass}">${c.estado_contrato}</span>
          </td>
          <td class="p-3 text-right">
            <button onclick="promptUpdateContratoStatus(${c.id}, '${c.estado_contrato}')" class="px-2.5 py-1 bg-slate-800 text-white font-bold text-[11px] rounded-lg hover:bg-slate-900 transition">
              Cambiar Estado
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbl.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-red-500">Error al cargar contratos: ${err.message}</td></tr>`;
  }
}

async function promptUpdateContratoStatus(contratoId, currentStatus) {
  const newStatus = prompt(`Cambiar estado del contrato #${contratoId} (Actual: ${currentStatus}):\nOpciones: EN PATROCINIO, EN ETAPA PRACTICA, ACTIVO, FINALIZADO, SUSPENDIDO, CANCELADO`, currentStatus);
  if (newStatus && newStatus !== currentStatus) {
    try {
      await API.updateContrato(contratoId, { estado_contrato: newStatus.toUpperCase() });
      Toast.success('Estado del contrato actualizado correctamente');
      loadContratos();
    } catch (err) {
      Toast.error(err.message, 'Fallo al actualizar contrato');
    }
  }
}

// SECTION 5: BENEFICIOS INSTITUCIONALES
async function loadBeneficiosData() {
  const container = document.getElementById('listBeneficios');
  if (!container) return;

  try {
    const beneficios = await API.getBeneficios();
    if (!beneficios || !beneficios.length) {
      container.innerHTML = `<div class="col-span-2 p-6 text-center text-slate-400 bg-white rounded-2xl border border-sena-border">No hay beneficios creados en el catálogo.</div>`;
      return;
    }

    container.innerHTML = beneficios.map(b => `
      <div class="bg-white p-5 rounded-2xl border border-sena-border shadow-sm space-y-2 relative">
        <div class="flex justify-between items-start">
          <span class="text-[10px] font-black uppercase text-[#00324D] bg-[#8FFA94] px-2 py-0.5 rounded-full">${b.codigo}</span>
          <span class="text-[10px] font-bold text-slate-400">${b.tipo_beneficio}</span>
        </div>
        <h4 class="font-black text-sena-dark text-sm">${b.nombre}</h4>
        <p class="text-xs text-slate-500 leading-relaxed">${b.descripcion || 'Sin descripción.'}</p>
      </div>
    `).join('');
  } catch (err) {
    Toast.error(err.message, 'Fallo cargando beneficios');
  }
}

// SECTION 6: CASOS DE ATENCIÓN
async function loadCasosData() {
  const tbl = document.getElementById('tblCasos');
  if (!tbl) return;
  tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">Cargando casos...</td></tr>`;

  try {
    const casos = await API.getCasos();
    if (!casos || !casos.length) {
      tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">No hay casos de atención registrados.</td></tr>`;
      return;
    }

    tbl.innerHTML = casos.map(c => `
      <tr class="hover:bg-slate-50 transition">
        <td class="p-3 font-bold text-sena-dark">${c.titulo}</td>
        <td class="p-3">${c.aprendiz_id}</td>
        <td class="p-3"><span class="badge-state bg-amber-100 text-amber-900">${c.prioridad}</span></td>
        <td class="p-3"><span class="badge-state bg-blue-100 text-blue-900">${c.estado}</span></td>
        <td class="p-3 text-[11px]">${c.created_at ? c.created_at.split('T')[0] : 'N/A'}</td>
        <td class="p-3 text-right">
          <button onclick="openModalSeguimiento(${c.id})" class="px-2.5 py-1 bg-sena-primary text-sena-dark font-black text-[11px] rounded-lg hover:bg-sena-secondary transition">
            Seguimiento
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbl.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Error cargando casos: ${err.message}</td></tr>`;
  }
}

// SECTION 7: VARIABLES DINÁMICAS
async function loadVariablesData() {
  const container = document.getElementById('listVariables');
  if (!container) return;

  try {
    const variables = await API.getVariables();
    if (!variables || !variables.length) {
      container.innerHTML = `<div class="col-span-2 p-6 text-center text-slate-400 bg-white rounded-2xl border border-sena-border">No hay variables dinámicas configuradas.</div>`;
      return;
    }

    container.innerHTML = variables.map(v => `
      <div class="bg-white p-5 rounded-2xl border border-sena-border shadow-sm space-y-3">
        <div class="flex justify-between items-center">
          <span class="text-[10px] font-black uppercase text-sena-dark bg-[#8FFA94] px-2.5 py-0.5 rounded-full">${v.codigo}</span>
          <span class="text-[10px] font-bold text-slate-400">Versión 1</span>
        </div>
        <h4 class="font-black text-sena-dark text-sm">${v.nombre}</h4>
        <p class="text-xs text-slate-500">${v.descripcion || 'Sin descripción.'}</p>
        <div class="pt-2 border-t border-slate-100 flex flex-wrap gap-1">
          ${v.opciones ? v.opciones.map(o => `<span class="text-[10px] bg-sena-bg px-2 py-0.5 rounded text-slate-700 font-semibold">${o.texto_opcion} (${o.nivel_afectacion})</span>`).join('') : ''}
        </div>
      </div>
    `).join('');
  } catch (err) {
    Toast.error(err.message, 'Fallo cargando variables');
  }
}

// SECTION 8: ENGINE DE ENCUESTAS
async function loadEncuestasData() {
  const container = document.getElementById('listEncuestas');
  if (!container) return;

  try {
    const encuestas = await API.getEncuestas();
    if (!encuestas || !encuestas.length) {
      container.innerHTML = `<div class="p-6 text-center text-slate-400 bg-white rounded-2xl border border-sena-border">No hay encuestas institucionales creadas.</div>`;
      return;
    }

    container.innerHTML = encuestas.map(e => `
      <div class="bg-white p-5 rounded-2xl border border-sena-border shadow-sm space-y-3 flex justify-between items-center">
        <div>
          <span class="text-[10px] font-black uppercase bg-blue-100 text-blue-900 px-2 py-0.5 rounded-full">${e.estado || 'Activa'}</span>
          <h4 class="font-black text-sena-dark text-base mt-1">${e.nombre}</h4>
          <p class="text-xs text-slate-500">${e.descripcion || 'Sin descripción.'}</p>
        </div>
        <div class="text-right">
          <span class="text-xs font-bold text-slate-600 block">${e.preguntas ? e.preguntas.length : 0} Preguntas</span>
        </div>
      </div>
    `).join('');
  } catch (err) {
    Toast.error(err.message, 'Fallo cargando encuestas');
  }
}

// SECTION 9: ANALÍTICA LONGITUDINAL
async function loadAnalyticsData() {
  try {
    const evo = await API.getAnalyticsEvolucion();
    renderChartEvolucion(evo || []);

    const ind = await API.getAnalyticsIndiceAfectacion();
    const tbl = document.getElementById('tblIndiceAfectacion');
    if (tbl) {
      tbl.innerHTML = (ind || []).map(i => `
        <tr class="hover:bg-slate-50 transition">
          <td class="p-3 font-bold text-sena-dark">${i.aprendiz_nombre || 'Aprendiz #' + i.aprendiz_id}</td>
          <td class="p-3 font-mono">${i.ficha_id || 'N/A'}</td>
          <td class="p-3 font-bold">${i.indice_ponderado}</td>
          <td class="p-3"><span class="badge-state ${i.nivel_riesgo === 'CRITICO' ? 'bg-red-900 text-white' : 'bg-amber-100 text-amber-900'}">${i.nivel_riesgo}</span></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    Toast.error(err.message, 'Fallo cargando analítica');
  }
}

function renderChartEvolucion(data) {
  const ctx = document.getElementById('chartEvolucion');
  if (!ctx) return;

  if (chartEvolucion) chartEvolucion.destroy();

  const labels = data.map(d => d.corte || 'Corte');
  const afectaciones = data.map(d => d.total_grave_critico || 0);

  chartEvolucion = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Aprendices en Riesgo Grave/Crítico',
        data: afectaciones,
        borderColor: '#27F531',
        backgroundColor: 'rgba(39, 245, 49, 0.15)',
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

// SECTION 10: AUDITORÍA
async function loadAuditLogsData() {
  const tbl = document.getElementById('tblAudit');
  if (!tbl) return;
  tbl.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400">Cargando registros...</td></tr>`;

  try {
    const logs = await API.getAuditLogs();
    if (!logs || !logs.length) {
      tbl.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400">No hay registros de auditoría.</td></tr>`;
      return;
    }

    tbl.innerHTML = logs.map(l => `
      <tr class="hover:bg-slate-50 transition">
        <td class="p-3 font-bold">${l.usuario_id || 'Sistema'}</td>
        <td class="p-3 font-mono text-[11px]">${l.operacion}</td>
        <td class="p-3">${l.entidad}</td>
        <td class="p-3 text-[11px] text-slate-500">${l.detalles || ''}</td>
        <td class="p-3 text-[11px]">${l.created_at ? l.created_at.split('T')[0] : 'N/A'}</td>
      </tr>
    `).join('');
  } catch (err) {
    tbl.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-red-500">Acceso restringido a auditoría.</td></tr>`;
  }
}

// MODAL HANDLERS
function openModalAprendiz() { document.getElementById('modalAprendiz')?.classList.remove('hidden'); }
function closeModalAprendiz() { document.getElementById('modalAprendiz')?.classList.add('hidden'); }

async function handleCreateAprendiz(e) {
  e.preventDefault();
  const data = {
    tipo_documento: document.getElementById('apTipoDoc').value,
    numero_documento: document.getElementById('apNumDoc').value.trim(),
    nombres: document.getElementById('apNombres').value.trim(),
    apellidos: document.getElementById('apApellidos').value.trim(),
    correo: document.getElementById('apCorreo').value.trim(),
    celular: document.getElementById('apCelular').value.trim() || null,
    direccion_vivienda: document.getElementById('apDireccion').value.trim() || null,
    ciudad: document.getElementById('apCiudad').value.trim() || null,
    departamento: document.getElementById('apDepartamento').value.trim() || null
  };

  try {
    await API.createAprendiz(data);
    Toast.success('Aprendiz registrado exitosamente');
    closeModalAprendiz();
    loadAprendicesData();
  } catch (err) {
    Toast.error(err.message, 'Fallo registrando aprendiz');
  }
}

async function openModalContrato() {
  document.getElementById('modalContrato')?.classList.remove('hidden');
  const sel = document.getElementById('contratoMatriculaId');
  if (sel) {
    sel.innerHTML = `<option value="">Cargando matrículas...</option>`;
    try {
      const aprendices = await API.getAprendices();
      let optionsHtml = `<option value="">Seleccione un aprendiz / matrícula...</option>`;
      aprendices.forEach(ap => {
        if (ap.matriculas && ap.matriculas.length) {
          ap.matriculas.forEach(m => {
            optionsHtml += `<option value="${m.id}">${ap.nombres} ${ap.apellidos} - Ficha ${m.ficha_id} (ID Matrícula #${m.id})</option>`;
          });
        }
      });
      sel.innerHTML = optionsHtml;
    } catch (err) {
      sel.innerHTML = `<option value="">Error cargando matrículas</option>`;
    }
  }
}
function closeModalContrato() { document.getElementById('modalContrato')?.classList.add('hidden'); }

async function handleCreateContrato(e) {
  e.preventDefault();
  const data = {
    matricula_id: parseInt(document.getElementById('contratoMatriculaId').value),
    nombre_empresa: document.getElementById('contratoEmpresa').value.trim(),
    departamento: document.getElementById('contratoDepartamento').value.trim(),
    ciudad: document.getElementById('contratoCiudad').value.trim(),
    fecha_inicio_contrato: document.getElementById('contratoFechaInicio').value,
    fecha_fin_contrato: document.getElementById('contratoFechaFin').value || null,
    estado_contrato: document.getElementById('contratoEstado').value,
    observaciones: document.getElementById('contratoObservaciones').value.trim() || null
  };

  try {
    await API.createContrato(data);
    Toast.success('Contrato de aprendizaje registrado');
    closeModalContrato();
    loadContratos();
  } catch (err) {
    Toast.error(err.message, 'Fallo registrando contrato');
  }
}

function openModalFicha() { document.getElementById('modalFicha')?.classList.remove('hidden'); }
function closeModalFicha() { document.getElementById('modalFicha')?.classList.add('hidden'); }

async function handleCreateFicha(e) {
  e.preventDefault();
  const data = {
    ficha_caracterizacion: document.getElementById('fichaNum').value.trim(),
    programa_codigo: document.getElementById('fichaPrograma').value || '228118',
    centro_id: document.getElementById('fichaCentro').value || '9201',
    departamento: document.getElementById('fichaDepartamento').value.trim() || 'BOGOTÁ D.C.',
    ciudad: document.getElementById('fichaCiudad').value.trim() || 'BOGOTÁ D.C.',
    fecha_inicial: document.getElementById('fichaFechaInicio').value,
    fecha_final: document.getElementById('fichaFechaFin').value,
    estado_ficha: 'EJECUCION'
  };

  try {
    await API.createFicha(data);
    Toast.success('Ficha formativa creada exitosamente');
    closeModalFicha();
    loadFichasData();
  } catch (err) {
    Toast.error(err.message, 'Fallo al crear ficha');
  }
}

function openModalVariable() { document.getElementById('modalVariable')?.classList.remove('hidden'); }
function closeModalVariable() { document.getElementById('modalVariable')?.classList.add('hidden'); }

async function handleCreateVariable(e) {
  e.preventDefault();
  const data = {
    categoria_id: parseInt(document.getElementById('varCategoriaId').value || 1),
    nombre: document.getElementById('varNombre').value.trim(),
    codigo: document.getElementById('varCodigo').value.trim().toUpperCase(),
    descripcion: document.getElementById('varDescripcion').value.trim() || null
  };

  try {
    await API.createVariable(data);
    Toast.success('Variable dinámica creada');
    closeModalVariable();
    loadVariablesData();
  } catch (err) {
    Toast.error(err.message, 'Fallo creando variable');
  }
}

function openModalCaso() { document.getElementById('modalCaso')?.classList.remove('hidden'); }
function closeModalCaso() { document.getElementById('modalCaso')?.classList.add('hidden'); }

async function handleCreateCaso(e) {
  e.preventDefault();
  const data = {
    aprendiz_id: parseInt(document.getElementById('casoAprendizId').value),
    titulo: document.getElementById('casoTitulo').value.trim(),
    descripcion: document.getElementById('casoDescripcion').value.trim(),
    prioridad: document.getElementById('casoPrioridad').value,
    origen: 'MANUAL'
  };

  try {
    await API.createCaso(data);
    Toast.success('Caso de atención abierto exitosamente');
    closeModalCaso();
    loadCasosData();
  } catch (err) {
    Toast.error(err.message, 'Fallo al crear caso');
  }
}

function openModalSeguimiento(casoId) {
  document.getElementById('segCasoId').value = casoId;
  document.getElementById('modalSeguimiento')?.classList.remove('hidden');
}
function closeModalSeguimiento() { document.getElementById('modalSeguimiento')?.classList.add('hidden'); }

async function handleSaveSeguimiento(e) {
  e.preventDefault();
  const casoId = document.getElementById('segCasoId').value;
  const comentario = document.getElementById('segComentario').value.trim();
  const nuevoEstado = document.getElementById('segNuevoEstado').value || null;

  try {
    await API.addSeguimientoCaso(casoId, comentario, nuevoEstado);
    Toast.success('Seguimiento guardado correctamente');
    closeModalSeguimiento();
    loadCasosData();
  } catch (err) {
    Toast.error(err.message, 'Fallo guardando seguimiento');
  }
}

function openModalBeneficio() { document.getElementById('modalBeneficio')?.classList.remove('hidden'); }
function closeModalBeneficio() { document.getElementById('modalBeneficio')?.classList.add('hidden'); }

async function handleCreateBeneficio(e) {
  e.preventDefault();
  const data = {
    codigo: document.getElementById('benCodigo').value.trim().toUpperCase(),
    nombre: document.getElementById('benNombre').value.trim(),
    tipo_beneficio: document.getElementById('benTipo').value,
    descripcion: document.getElementById('benDescripcion').value.trim() || null,
    es_automatico_matricula: document.getElementById('benAutoMatricula').checked
  };

  try {
    await API.createBeneficio(data);
    Toast.success('Beneficio creado en el catálogo');
    closeModalBeneficio();
    loadBeneficiosData();
  } catch (err) {
    Toast.error(err.message, 'Fallo creando beneficio');
  }
}

function openModalAsignarBeneficio() { document.getElementById('modalAsignarBeneficio')?.classList.remove('hidden'); }
function closeModalAsignarBeneficio() { document.getElementById('modalAsignarBeneficio')?.classList.add('hidden'); }

async function handleAsignarBeneficio(e) {
  e.preventDefault();
  const data = {
    aprendiz_id: parseInt(document.getElementById('asigAprendizId').value),
    beneficio_id: parseInt(document.getElementById('asigBeneficioId').value),
    origen: 'DIRECTO_LIDER_BIENESTAR',
    observaciones: document.getElementById('asigObservaciones').value.trim() || null
  };

  try {
    await API.asignarBeneficio(data);
    Toast.success('Beneficio otorgado al aprendiz');
    closeModalAsignarBeneficio();
    loadBeneficiosData();
  } catch (err) {
    Toast.error(err.message, 'Fallo otorgando beneficio');
  }
}
