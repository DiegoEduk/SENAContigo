/**
 * SENAContigo - Learner Portal Controller
 */

let currentUser = null;
let currentTab = 'perfil';
let activeSurvey = null;
let currentQuestionIndex = 0;
let userAnswers = {};
let isDirtySurvey = false;
let myContractsCache = [];

document.addEventListener('DOMContentLoaded', async () => {
  try {
    initColombiaSelects();

    if (!API.getToken()) {
      showLoginView();
      return;
    }

    currentUser = await API.getMe();
    API.setUser(currentUser);

    showWorkspaceView();

    // Prevent accidental navigation when survey is dirty
    window.addEventListener('beforeunload', (e) => {
      if (isDirtySurvey) {
        e.preventDefault();
        e.returnValue = '';
      }
    });
  } catch (err) {
    console.error('Error inicializando portal aprendiz:', err);
    showLoginView();
  }
});

function showLoginView() {
  const loginEl = document.getElementById('aprendizLoginContainer');
  const workEl = document.getElementById('aprendizWorkspace');
  const headEl = document.getElementById('aprendizHeaderControls');
  if (loginEl) loginEl.classList.remove('hidden');
  if (workEl) workEl.classList.add('hidden');
  if (headEl) headEl.classList.add('hidden');
}

function showWorkspaceView() {
  const loginEl = document.getElementById('aprendizLoginContainer');
  const workEl = document.getElementById('aprendizWorkspace');
  const headEl = document.getElementById('aprendizHeaderControls');
  if (loginEl) loginEl.classList.add('hidden');
  if (workEl) workEl.classList.remove('hidden');
  if (headEl) headEl.classList.remove('hidden');
  setupLearnerHeader();
  loadTabContent();
}

async function handleAprendizLogin(e) {
  e.preventDefault();
  const doc = document.getElementById('inputDocAprendiz').value.trim();
  const ficha = document.getElementById('inputFichaAprendiz').value.trim();

  if (!doc || !ficha) {
    Toast.warning('Por favor ingrese su número de documento y ficha.');
    return;
  }

  try {
    Loading.show('Validando información del aprendiz...');
    const res = await API.loginAprendiz(doc, ficha);
    Loading.hide();

    API.setToken(res.access_token);
    API.setUser({
      ...res.aprendiz,
      rol: 'aprendiz',
      ficha_id: res.ficha_id
    });

    Toast.success(`¡Bienvenido(a), ${res.aprendiz.nombres}!`, 'Validación Exitosa');
    currentUser = await API.getMe();
    showWorkspaceView();
  } catch (err) {
    Loading.hide();
    Toast.error(err.message || 'No se pudo validar la información del aprendiz.', 'Validación Fallida');
  }
}

function setupLearnerHeader() {
  if (!currentUser) return;
  const nameEl = document.getElementById('learnerName');
  if (nameEl) nameEl.innerText = `${currentUser.nombres || 'Aprendiz'} ${currentUser.apellidos || ''}`;

  const mailEl = document.getElementById('learnerMail');
  if (mailEl) mailEl.innerText = currentUser.correo || '';
}

function switchTab(tabName) {
  if (isDirtySurvey && !confirm('Tiene respuestas sin guardar en la encuesta actual. ¿Desea salir sin guardar?')) {
    return;
  }
  isDirtySurvey = false;
  currentTab = tabName;

  const buttons = document.querySelectorAll('[id^="tab-"]');
  buttons.forEach(btn => {
    btn.classList.remove('bg-[#27F531]', 'text-[#252525]', 'font-black');
    btn.classList.add('text-slate-600', 'hover:bg-[#F3F2F2]');
  });

  const activeBtn = document.getElementById(`tab-${tabName}`);
  if (activeBtn) {
    activeBtn.classList.remove('text-slate-600', 'hover:bg-[#F3F2F2]');
    activeBtn.classList.add('bg-[#27F531]', 'text-[#252525]', 'font-black');
  }

  const sections = document.querySelectorAll('section[id^="sec-"]');
  sections.forEach(s => s.classList.add('hidden'));

  const activeSec = document.getElementById(`sec-${tabName}`);
  if (activeSec) activeSec.classList.remove('hidden');

  loadTabContent();
}

function loadTabContent() {
  switch (currentTab) {
    case 'perfil':
      loadProfile();
      break;
    case 'encuestas':
      loadPendingSurveys();
      break;
    case 'contrato':
      loadMyContract();
      break;
    case 'beneficios':
      loadMyBenefits();
      break;
    case 'historial':
      loadMyHistory();
      break;
  }
}

// TAB 1: PERFIL DEL APRENDIZ
async function loadProfile() {
  try {
    Loading.show('Cargando perfil...');
    const perfil = await API.getPerfilAprendiz();
    Loading.hide();

    // Actualizar campos bloqueados (inmutables)
    document.getElementById('profTipoDoc').value = perfil.tipo_documento || 'CC';
    document.getElementById('profNumDoc').value = perfil.numero_documento || '';

    // Campos editables
    document.getElementById('profNombres').value = perfil.nombres || '';
    document.getElementById('profApellidos').value = perfil.apellidos || '';
    document.getElementById('profCorreo').value = perfil.correo || '';
    document.getElementById('profCelular').value = perfil.celular || '';
    document.getElementById('profDireccion').value = perfil.direccion_vivienda || '';

    // Cargar Departamento y Ciudad en los selects buscables
    const deptVal = perfil.departamento || '';
    const cityVal = perfil.ciudad || '';

    if (deptVal) {
      const matchedDept = Object.keys(COLOMBIA_DATA).find(d => normalizeString(d) === normalizeString(deptVal));
      if (matchedDept) {
        selectDepartment(matchedDept, true);
        document.getElementById('profCiudad').value = cityVal;
      } else {
        document.getElementById('profDepartamento').value = deptVal;
        document.getElementById('profCiudad').value = cityVal;
        document.getElementById('profCiudad').disabled = false;
      }
    } else {
      document.getElementById('profDepartamento').value = '';
      document.getElementById('profCiudad').value = '';
      document.getElementById('profCiudad').disabled = true;
      document.getElementById('profCiudad').placeholder = "Primero seleccione departamento...";
    }
  } catch (err) {
    Loading.hide();
    Toast.error('Error al cargar datos del perfil: ' + err.message);
  }
}

async function handleUpdateProfile(e) {
  e.preventDefault();
  try {
    Loading.show('Guardando perfil...');
    const data = {
      nombres: document.getElementById('profNombres').value.trim(),
      apellidos: document.getElementById('profApellidos').value.trim(),
      correo: document.getElementById('profCorreo').value.trim(),
      celular: document.getElementById('profCelular').value.trim(),
      departamento: document.getElementById('profDepartamento').value.trim(),
      ciudad: document.getElementById('profCiudad').value.trim(),
      direccion_vivienda: document.getElementById('profDireccion').value.trim()
    };

    const updated = await API.updatePerfilAprendiz(data);
    Loading.hide();

    currentUser = { ...currentUser, ...updated };
    API.setUser(currentUser);
    setupLearnerHeader();

    Toast.success('Perfil actualizado correctamente.', 'Datos Guardados');
  } catch (err) {
    Loading.hide();
    Toast.error(err.message, 'Fallo al actualizar perfil');
  }
}

// TAB 2: SURVEY WIZARD
async function loadPendingSurveys() {
  const container = document.getElementById('surveyWizardContainer');
  if (!container) return;
  container.innerHTML = `<p class="text-center text-slate-400 py-8">Cargando encuestas pendientes...</p>`;

  try {
    const encuestas = await API.getEncuestasPendientes();
    if (!encuestas || !encuestas.length) {
      container.innerHTML = `
        <div class="text-center py-10 space-y-3">
          <div class="w-16 h-16 bg-[#8FFA94]/30 text-sena-dark rounded-full flex items-center justify-center text-2xl mx-auto">
            <i class="fas fa-circle-check"></i>
          </div>
          <h3 class="text-lg font-black text-sena-dark">¡Estás al día con tus encuestas!</h3>
          <p class="text-xs text-slate-500">No tienes encuestas de caracterización pendientes por diligenciar.</p>
        </div>
      `;
      return;
    }

    activeSurvey = encuestas[0];
    currentQuestionIndex = 0;
    userAnswers = {};
    isDirtySurvey = false;
    renderSurveyQuestion();
  } catch (err) {
    container.innerHTML = `<p class="text-center text-red-500 py-8">Error cargando encuestas: ${err.message}</p>`;
  }
}

function renderSurveyQuestion() {
  const container = document.getElementById('surveyWizardContainer');
  if (!container || !activeSurvey || !activeSurvey.preguntas || !activeSurvey.preguntas.length) return;

  const total = activeSurvey.preguntas.length;
  const q = activeSurvey.preguntas[currentQuestionIndex];
  const progressPct = Math.round(((currentQuestionIndex + 1) / total) * 100);

  let inputFieldsHtml = '';
  if (q.opciones && q.opciones.length) {
    inputFieldsHtml = `
      <div class="space-y-2.5 pt-2">
        ${q.opciones.map(opt => {
          const isSelected = userAnswers[q.variable_id] === opt.id;
          return `
            <label onclick="selectOption(${q.variable_id}, ${opt.id})" class="flex items-center p-3.5 rounded-xl border ${isSelected ? 'border-[#27F531] bg-[#8FFA94]/20 font-bold' : 'border-sena-border hover:bg-slate-50'} cursor-pointer transition">
              <input type="radio" name="var_${q.variable_id}" value="${opt.id}" ${isSelected ? 'checked' : ''} class="text-[#27F531] focus:ring-[#27F531]">
              <span class="ml-3 text-sm text-sena-dark font-medium">${opt.texto_opcion}</span>
            </label>
          `;
        }).join('')}
      </div>
    `;
  } else {
    inputFieldsHtml = `
      <div class="pt-2">
        <textarea id="textAns_${q.variable_id}" oninput="userAnswers[${q.variable_id}] = this.value; isDirtySurvey=true;" rows="3" class="w-full text-sm p-3.5 border border-sena-border rounded-xl focus:ring-2 focus:ring-[#27F531]" placeholder="Escriba su respuesta aquí...">${userAnswers[q.variable_id] || ''}</textarea>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="space-y-4">
      <div class="flex justify-between items-center pb-3 border-b border-sena-border">
        <div>
          <span class="text-[10px] font-black uppercase text-slate-400">Encuesta Institucional</span>
          <h3 class="font-black text-sena-dark text-lg">${activeSurvey.nombre || activeSurvey.titulo}</h3>
        </div>
        <span class="text-xs font-black text-sena-dark bg-[#8FFA94] px-3 py-1 rounded-full">Pregunta ${currentQuestionIndex + 1} de ${total}</span>
      </div>

      <!-- Progress Bar -->
      <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
        <div class="bg-[#27F531] h-full transition-all duration-300" style="width: ${progressPct}%"></div>
      </div>

      <!-- Question Text (Sin título de variable, con tamaño de pregunta incrementado) -->
      <div class="py-3">
        <h4 class="text-base sm:text-lg font-black text-sena-dark leading-snug">${q.texto_pregunta || q.nombre}</h4>
      </div>

      ${inputFieldsHtml}

      <!-- Navigation buttons -->
      <div class="flex justify-between items-center pt-6 border-t border-sena-border">
        <button onclick="prevQuestion()" ${currentQuestionIndex === 0 ? 'disabled class="opacity-40 cursor-not-allowed text-xs text-slate-400 px-4 py-2"' : 'class="px-4 py-2 bg-slate-200 text-sena-dark font-bold text-xs rounded-xl hover:bg-slate-300 transition"'}>
          <i class="fas fa-chevron-left mr-1"></i> Anterior
        </button>

        ${currentQuestionIndex === total - 1 ? `
          <button onclick="submitSurvey()" class="px-6 py-2.5 bg-[#27F531] text-[#252525] font-black text-xs uppercase tracking-wider rounded-xl hover:bg-[#63F86B] transition shadow-md flex items-center gap-2">
            <i class="fas fa-paper-plane"></i> Finalizar y Enviar
          </button>
        ` : `
          <button onclick="nextQuestion()" class="px-5 py-2.5 bg-[#252525] text-white font-bold text-xs rounded-xl hover:bg-slate-800 transition flex items-center gap-1">
            Siguiente <i class="fas fa-chevron-right ml-1"></i>
          </button>
        `}
      </div>
    </div>
  `;
}

function selectOption(varId, optId) {
  userAnswers[varId] = optId;
  isDirtySurvey = true;
  renderSurveyQuestion();
}

function nextQuestion() {
  if (currentQuestionIndex < activeSurvey.preguntas.length - 1) {
    currentQuestionIndex++;
    renderSurveyQuestion();
  }
}

function prevQuestion() {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    renderSurveyQuestion();
  }
}

async function submitSurvey() {
  try {
    const respuestasArray = Object.keys(userAnswers).map(varId => ({
      variable_id: parseInt(varId),
      opcion_id: typeof userAnswers[varId] === 'number' ? userAnswers[varId] : null,
      valor_texto: typeof userAnswers[varId] === 'string' ? userAnswers[varId] : null
    }));

    await API.submitRespuestas(activeSurvey.id, respuestasArray);
    isDirtySurvey = false;
    Toast.success('¡Encuesta enviada exitosamente! Gracias por tu colaboración.', 'Encuesta Registrada');
    loadPendingSurveys();
  } catch (err) {
    Toast.error(err.message, 'Fallo al enviar encuesta');
  }
}

// TAB 3: MI CONTRATO DE APRENDIZAJE
async function loadMyContract() {
  const container = document.getElementById('myContractContent');
  if (!container) return;
  container.innerHTML = `<p class="text-center text-slate-400 py-6">Cargando datos de contrato...</p>`;

  try {
    const contratos = await API.getMisContratos();
    myContractsCache = contratos || [];

    if (!contratos || !contratos.length) {
      container.innerHTML = `
        <div class="p-8 text-center bg-[#F3F2F2] rounded-2xl border border-sena-border space-y-3">
          <div class="w-14 h-14 bg-slate-200 text-slate-500 rounded-full flex items-center justify-center text-xl mx-auto">
            <i class="fas fa-folder-open"></i>
          </div>
          <h4 class="font-black text-sena-dark text-base">No registras un Contrato de Aprendizaje aún</h4>
          <p class="text-xs text-slate-500 max-w-md mx-auto">No se encuentra ningún contrato de aprendizaje asignado o registrado actualmente.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = contratos.map(c => {
      let badgeStyle = 'bg-emerald-100 text-emerald-900 border border-emerald-300';
      if (c.estado_contrato === 'EN PATROCINIO') badgeStyle = 'bg-indigo-100 text-indigo-900 border border-indigo-300';

      return `
        <div class="bg-white p-6 rounded-2xl border border-sena-border shadow-sm space-y-4">
          <div class="flex justify-between items-start border-b border-sena-border pb-3">
            <div>
              <span class="text-[10px] font-black uppercase text-slate-400">Empresa Patrocinadora</span>
              <h3 class="text-lg font-black text-sena-dark">${c.nombre_empresa}</h3>
            </div>
            <div class="flex items-center gap-2">
              <span class="badge-state ${badgeStyle}">${c.estado_contrato}</span>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div class="bg-[#F3F2F2] p-3.5 rounded-xl space-y-1">
              <span class="text-slate-400 font-extrabold uppercase text-[10px] block">Ubicación Etapa Práctica</span>
              <p class="font-bold text-sena-dark">${c.ciudad || 'N/A'}, ${c.departamento || ''}</p>
            </div>

            <div class="bg-[#F3F2F2] p-3.5 rounded-xl space-y-1">
              <span class="text-slate-400 font-extrabold uppercase text-[10px] block">Vigencia del Contrato</span>
              <p class="font-bold text-sena-dark">Inicio: ${c.fecha_inicio_contrato} ${c.fecha_fin_contrato ? '| Fin: ' + c.fecha_fin_contrato : ''}</p>
            </div>
          </div>

          ${c.observaciones ? `
            <div class="pt-2">
              <span class="text-slate-400 font-extrabold uppercase text-[10px] block mb-1">Observaciones</span>
              <p class="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-200">${c.observaciones}</p>
            </div>
          ` : ''}
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = `<p class="text-center text-red-500 py-6">Error cargando contrato: ${err.message}</p>`;
  }
}

// TAB 4: MIS APOYOS SENA
async function loadMyBenefits() {
  const container = document.getElementById('myBenefitsList');
  if (!container) return;
  container.innerHTML = `<p class="col-span-2 text-center text-slate-400 py-6">Cargando apoyos...</p>`;

  try {
    const beneficios = await API.getMisBeneficios();

    if (!beneficios || !beneficios.length) {
      container.innerHTML = `<div class="col-span-2 p-6 text-center text-slate-400 bg-[#F3F2F2] rounded-2xl border border-sena-border">No tienes apoyos institucionales asignados aún.</div>`;
      return;
    }

    container.innerHTML = beneficios.map(b => `
      <div class="bg-white p-5 rounded-2xl border border-sena-border shadow-sm space-y-2">
        <div class="flex justify-between items-center">
          <span class="text-[10px] font-black uppercase bg-[#8FFA94] text-sena-dark px-2.5 py-0.5 rounded-full">${b.estado || 'ACTIVO'}</span>
          <span class="text-[10px] text-slate-400 font-bold">${b.origen || 'AUTOMATICO'}</span>
        </div>
        <h4 class="font-black text-sena-dark text-sm">${b.beneficio_nombre || 'Apoyo SENA'}</h4>
        <p class="text-xs text-slate-500">${b.observaciones || 'Otorgado por la institución.'}</p>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<p class="col-span-2 text-center text-red-500 py-6">Error cargando apoyos: ${err.message}</p>`;
  }
}

// TAB 5: MI HISTORIAL
async function loadMyHistory() {
  const container = document.getElementById('myHistoryTimeline');
  if (!container) return;
  container.innerHTML = `<p class="text-center text-slate-400 py-6">Cargando historial...</p>`;

  try {
    const historial = await API.getMiHistorial();

    if (!historial || !historial.length) {
      container.innerHTML = `<div class="p-6 text-center text-slate-400 bg-[#F3F2F2] rounded-2xl border border-sena-border">No has diligenciado respuestas anteriormente.</div>`;
      return;
    }

    container.innerHTML = historial.map(h => `
      <div class="p-4 bg-white rounded-2xl border border-sena-border shadow-sm flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold text-slate-400 block">${h.fecha_respuesta ? h.fecha_respuesta.split('T')[0] : 'N/A'}</span>
          <h4 class="font-bold text-sena-dark text-xs">${h.variable ? h.variable.nombre : 'Variable'}</h4>
          ${h.valor_texto ? `<p class="text-xs text-slate-600 mt-1">${h.valor_texto}</p>` : ''}
        </div>
        <span class="badge-state bg-[#8FFA94] text-sena-dark">${h.opcion ? h.opcion.texto : 'Respuesta Registrada'}</span>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<p class="text-center text-red-500 py-6">Error cargando historial: ${err.message}</p>`;
  }
}

/**
 * Lógica de Selects Buscables de Departamentos y Municipios de Colombia
 */
function normalizeString(str) {
  return str ? str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase() : "";
}

function initColombiaSelects() {
  if (typeof COLOMBIA_DATA === 'undefined') return;
  const depts = Object.keys(COLOMBIA_DATA).sort();
  renderDeptOptions(depts);

  // Cerrar paneles al hacer clic fuera
  document.addEventListener('click', (e) => {
    const deptWrapper = document.getElementById('colombiaDeptWrapper');
    const cityWrapper = document.getElementById('colombiaCityWrapper');
    if (deptWrapper && !deptWrapper.contains(e.target)) {
      closeColombiaDropdown('dept');
    }
    if (cityWrapper && !cityWrapper.contains(e.target)) {
      closeColombiaDropdown('city');
    }
  });
}

function toggleColombiaDropdown(type) {
  if (type === 'city') {
    const inputCity = document.getElementById('profCiudad');
    if (inputCity && inputCity.disabled) return;
  }
  const panel = document.getElementById(type === 'dept' ? 'panelDept' : 'panelCity');
  const icon = document.getElementById(type === 'dept' ? 'iconDept' : 'iconCity');
  const searchInput = document.getElementById(type === 'dept' ? 'searchDept' : 'searchCity');
  
  if (!panel) return;
  const isHidden = panel.classList.contains('hidden');
  closeColombiaDropdown('dept');
  closeColombiaDropdown('city');
  
  if (isHidden) {
    panel.classList.remove('hidden');
    if (icon) icon.classList.add('rotate-180');
    if (searchInput) {
      searchInput.value = '';
      if (type === 'dept') filterDeptOptions();
      else filterCityOptions();
      setTimeout(() => searchInput.focus(), 50);
    }
  }
}

function closeColombiaDropdown(type) {
  const panel = document.getElementById(type === 'dept' ? 'panelDept' : 'panelCity');
  const icon = document.getElementById(type === 'dept' ? 'iconDept' : 'iconCity');
  if (panel) panel.classList.add('hidden');
  if (icon) icon.classList.remove('rotate-180');
}

function renderDeptOptions(depts) {
  const list = document.getElementById('listDept');
  if (!list) return;
  if (depts.length === 0) {
    list.innerHTML = `<li class="p-3 text-slate-400 text-center italic">No se encontraron departamentos</li>`;
    return;
  }
  list.innerHTML = depts.map(d => `
    <li onclick="selectDepartment('${d.replace(/'/g, "\\'")}')" 
        class="p-2.5 hover:bg-slate-100 cursor-pointer transition flex items-center justify-between font-medium">
      <span>${d}</span>
    </li>
  `).join('');
}

function filterDeptOptions() {
  if (typeof COLOMBIA_DATA === 'undefined') return;
  const searchEl = document.getElementById('searchDept');
  const query = searchEl ? normalizeString(searchEl.value) : '';
  const depts = Object.keys(COLOMBIA_DATA).sort().filter(d => normalizeString(d).includes(query));
  renderDeptOptions(depts);
}

function selectDepartment(deptName, keepSelectedCity = false) {
  const inputDept = document.getElementById('profDepartamento');
  const inputCity = document.getElementById('profCiudad');
  
  if (inputDept) inputDept.value = deptName;
  closeColombiaDropdown('dept');

  if (inputCity) {
    inputCity.disabled = false;
    inputCity.placeholder = "Seleccione una ciudad o municipio...";
    if (!keepSelectedCity) {
      inputCity.value = '';
    }
  }

  if (typeof COLOMBIA_DATA !== 'undefined') {
    const cities = (COLOMBIA_DATA[deptName] || []).slice().sort();
    renderCityOptions(cities);
  }
}

function renderCityOptions(cities) {
  const list = document.getElementById('listCity');
  if (!list) return;
  if (cities.length === 0) {
    list.innerHTML = `<li class="p-3 text-slate-400 text-center italic">No se encontraron municipios</li>`;
    return;
  }
  list.innerHTML = cities.map(c => `
    <li onclick="selectCity('${c.replace(/'/g, "\\'")}')" 
        class="p-2.5 hover:bg-slate-100 cursor-pointer transition flex items-center justify-between">
      <span>${c}</span>
    </li>
  `).join('');
}

function filterCityOptions() {
  if (typeof COLOMBIA_DATA === 'undefined') return;
  const currentDept = document.getElementById('profDepartamento').value;
  const searchEl = document.getElementById('searchCity');
  const query = searchEl ? normalizeString(searchEl.value) : '';
  const allCities = (COLOMBIA_DATA[currentDept] || []).slice().sort();
  const filtered = allCities.filter(c => normalizeString(c).includes(query));
  renderCityOptions(filtered);
}

function selectCity(cityName) {
  const inputCity = document.getElementById('profCiudad');
  if (inputCity) inputCity.value = cityName;
  closeColombiaDropdown('city');
}
