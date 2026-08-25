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

function formatFechaColombia(fechaRaw) {
  if (!fechaRaw) return 'N/A';
  try {
    const d = new Date(fechaRaw);
    if (!isNaN(d.getTime())) {
      return d.toLocaleString('es-CO', {
        timeZone: 'America/Bogota',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    }
  } catch (e) {}

  const parts = String(fechaRaw).split('T');
  const dateStr = parts[0] || '';
  const timeStr = parts[1] ? parts[1].substring(0, 5) : '';
  return `${dateStr} ${timeStr}`.trim();
}

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

  // Sincronizar selector móvil si está presente
  const mobileSelect = document.getElementById('mobileTabSelect');
  if (mobileSelect) {
    mobileSelect.value = tabName;
  }

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
    case 'historial':
      loadMyHistory();
      break;
    case 'contrato':
      loadMyContract();
      break;
    case 'beneficios':
      loadMyBenefits();
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

let isReanswering = false;

// TAB 2: SURVEY WIZARD
async function loadPendingSurveys() {
  const container = document.getElementById('surveyWizardContainer');
  if (!container) return;
  container.innerHTML = `<p class="text-center text-slate-400 py-8">Cargando encuestas...</p>`;

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

    // Verificar si la encuesta ya fue respondida previamente por el aprendiz y no ha solicitado re-responder
    if (activeSurvey.ya_respondida && !isReanswering) {
      renderCompletedSurveyBanner(container);
      return;
    }

    currentQuestionIndex = 0;
    userAnswers = {};
    isDirtySurvey = false;
    renderSurveyQuestion();
  } catch (err) {
    container.innerHTML = `<p class="text-center text-red-500 py-8">Error cargando encuestas: ${err.message}</p>`;
  }
}

function renderCompletedSurveyBanner(container) {
  if (!container) container = document.getElementById('surveyWizardContainer');
  if (!container || !activeSurvey) return;

  container.innerHTML = `
    <div class="p-8 bg-white rounded-3xl border border-sena-border shadow-sm text-center space-y-5">
      <div class="w-16 h-16 bg-[#EBF8E1] text-[#39A900] rounded-full flex items-center justify-center text-3xl mx-auto border border-[#39A900]/30">
        <i class="fas fa-circle-check"></i>
      </div>
      <div class="space-y-2">
        <span class="text-[10px] font-black uppercase text-[#2E8800] bg-[#EBF8E1] px-3 py-1 rounded-full border border-[#39A900]/30 tracking-wider">Encuesta Diligenciada</span>
        <h3 class="text-xl font-black text-sena-dark mt-2">${activeSurvey.nombre || activeSurvey.titulo}</h3>
        <p class="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
          Ya has registrado previamente tus respuestas para esta encuesta. Tu información socioeconómica se encuentra almacenada y disponible en tu historial.
        </p>
      </div>

      <div class="pt-4 border-t border-sena-border flex flex-col sm:flex-row items-center justify-center gap-3">
        <button onclick="startReansweringSurvey()" class="w-full sm:w-auto px-6 py-3 bg-[#252525] text-white font-black text-xs uppercase tracking-wider rounded-xl hover:bg-slate-800 transition shadow-md flex items-center justify-center gap-2">
          <i class="fas fa-arrows-rotate text-[#27F531]"></i> Volver a responder la encuesta
        </button>
      </div>
    </div>
  `;
}

function startReansweringSurvey() {
  isReanswering = true;
  currentQuestionIndex = 0;
  userAnswers = {};
  isDirtySurvey = false;
  renderSurveyQuestion();
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
    if (!activeSurvey) return;

    const answersKeys = Object.keys(userAnswers);
    if (!answersKeys.length) {
      Toast.warning('Por favor responda las preguntas de la encuesta antes de enviar.', 'Encuesta Incompleta');
      return;
    }

    const respuestasArray = answersKeys
      .map(varId => {
        const q = activeSurvey.preguntas ? activeSurvey.preguntas.find(p => p.variable_id === parseInt(varId)) : null;
        const val = userAnswers[varId];

        if (val === null || val === undefined || val === '') return null;

        const isOptId = typeof val === 'number' || (typeof val === 'string' && !isNaN(parseInt(val)) && /^\d+$/.test(String(val).trim()));
        return {
          variable_id: parseInt(varId),
          variable_version_id: q ? q.variable_version_id : null,
          opcion_id: isOptId ? parseInt(val) : null,
          valor_texto: !isOptId ? String(val) : null
        };
      })
      .filter(item => item !== null);

    if (!respuestasArray.length) {
      Toast.warning('Por favor seleccione una opción o escriba su respuesta antes de enviar.', 'Encuesta Incompleta');
      return;
    }

    await API.submitRespuestas(activeSurvey.id, respuestasArray, activeSurvey.corte_id || null);
    isDirtySurvey = false;
    isReanswering = false;
    userAnswers = {};
    Toast.success('¡Encuesta enviada exitosamente! Gracias por tu colaboración.', 'Encuesta Registrada');
    loadPendingSurveys();
  } catch (err) {
    Toast.error(err.message || 'No se pudo registrar la encuesta', 'Fallo al enviar encuesta');
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
      let badgeStyle = 'bg-[#EBF8E1] text-[#2E8800] border border-[#39A900]/30';
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

let allHistoryQuestions = [];
let targetSingleQuestion = null;
let singleQuestionAnswerVal = null;
let historyWizardStepIndex = 0;
let historyWizardAnswers = {};

// TAB 5: MI EVOLUCIÓN HISTÓRICA
async function loadMyHistory() {
  const container = document.getElementById('myHistoryTimeline');
  if (!container) return;
  container.innerHTML = `<p class="text-center text-slate-400 py-6">Cargando caracterización...</p>`;

  try {
    const historial = await API.getMiHistorial();
    allHistoryQuestions = historial || [];

    if (!allHistoryQuestions || !allHistoryQuestions.length) {
      container.innerHTML = `<div class="p-6 text-center text-slate-400 bg-[#F3F2F2] rounded-2xl border border-sena-border">No hay preguntas de caracterización disponibles.</div>`;
      return;
    }

    // Evaluar si el aprendiz ya tiene al menos una respuesta registrada
    const totalRespuestasRegistradas = allHistoryQuestions.reduce((acc, q) => {
      const cant = (q.respuestas && q.respuestas.length) ? q.respuestas.length : (q.pendiente === false ? 1 : 0);
      return acc + cant;
    }, 0);

    const hasAnyAnswer = totalRespuestasRegistradas > 0;

    if (!hasAnyAnswer) {
      // CASO A: No ha respondido ninguna pregunta -> Presentar Wizard multipaso con autoguardado
      renderHistoryWizardUnanswered(container);
    } else {
      // CASO B: Ya tiene al menos 1 respuesta -> Mostrar diseño de Evolución Histórica
      renderHistoryTimelineCards(container);
    }
  } catch (err) {
    container.innerHTML = `<p class="text-center text-red-500 py-6">Error cargando historial: ${err.message}</p>`;
  }
}

/**
 * CASO A: Renderizado del Wizard Multipaso con Autoguardado Pregunta por Pregunta
 */
function renderHistoryWizardUnanswered(container) {
  if (!allHistoryQuestions || !allHistoryQuestions.length) return;

  if (historyWizardStepIndex >= allHistoryQuestions.length) {
    historyWizardStepIndex = allHistoryQuestions.length - 1;
  }
  if (historyWizardStepIndex < 0) {
    historyWizardStepIndex = 0;
  }

  const total = allHistoryQuestions.length;
  const q = allHistoryQuestions[historyWizardStepIndex];
  const progressPct = Math.round(((historyWizardStepIndex + 1) / total) * 100);
  const selectedVal = historyWizardAnswers[q.variable_id];

  let inputFieldsHtml = '';
  if (q.opciones && q.opciones.length) {
    inputFieldsHtml = `
      <div class="space-y-2.5 pt-2">
        ${q.opciones.map(opt => {
          const isSelected = selectedVal === opt.id;
          return `
            <label class="flex items-center p-3.5 rounded-xl border ${isSelected ? 'border-[#27F531] bg-[#8FFA94]/20 font-bold' : 'border-sena-border hover:bg-slate-50'} cursor-pointer transition">
              <input type="radio" name="hw_opt_${q.variable_id}" value="${opt.id}" ${isSelected ? 'checked' : ''} onchange="autoSaveHistoryWizardOption(${q.variable_id}, ${opt.id})" class="text-[#27F531] focus:ring-[#27F531]">
              <span class="ml-3 text-sm text-sena-dark font-medium">${opt.texto}</span>
            </label>
          `;
        }).join('')}
      </div>
    `;
  } else {
    inputFieldsHtml = `
      <div class="pt-2">
        <textarea id="hw_text_${q.variable_id}" onchange="autoSaveHistoryWizardText(${q.variable_id}, this.value)" rows="3" class="w-full text-sm p-3.5 border border-sena-border rounded-xl focus:ring-2 focus:ring-[#27F531]" placeholder="Escriba su respuesta aquí...">${selectedVal || ''}</textarea>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="space-y-5 bg-white p-6 sm:p-8 rounded-3xl border border-sena-border shadow-sm">
      <!-- Header del Wizard -->
      <div class="flex justify-between items-start pb-4 border-b border-sena-border gap-2">
        <div class="space-y-1">
          <span class="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">Caracterización Socioeconómica y Bienestar</span>
          <h3 class="font-black text-sena-dark text-lg sm:text-xl">${q.variable_nombre || 'Pregunta de Caracterización'}</h3>
          <p class="text-xs text-slate-500">Cada respuesta se guarda automáticamente en tiempo real.</p>
        </div>
        <span class="text-xs font-black text-sena-dark bg-[#8FFA94] px-3.5 py-1 rounded-full whitespace-nowrap">Pregunta ${historyWizardStepIndex + 1} de ${total}</span>
      </div>

      <!-- Barra de Progreso -->
      <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
        <div class="bg-[#27F531] h-full transition-all duration-300" style="width: ${progressPct}%"></div>
      </div>

      <!-- Texto de la Pregunta -->
      <div class="py-2">
        <h4 class="text-base sm:text-lg font-black text-sena-dark leading-snug">${q.pregunta_texto || q.variable_nombre}</h4>
      </div>

      <!-- Opciones -->
      ${inputFieldsHtml}

      <!-- Indicador de Autoguardado -->
      <div id="autoSaveStatusIndicator" class="text-[11px] font-extrabold text-slate-400 flex items-center gap-1.5 pt-1">
        ${selectedVal ? '<span class="text-[#2E8800] flex items-center gap-1"><i class="fas fa-circle-check text-[#39A900]"></i> Respuesta guardada automáticamente</span>' : '<span>Selecciona una opción para guardar inmediatamente</span>'}
      </div>

      <!-- Botones de Navegación -->
      <div class="flex justify-between items-center pt-6 border-t border-sena-border">
        <button onclick="prevHistoryWizardStep()" ${historyWizardStepIndex === 0 ? 'disabled class="opacity-40 cursor-not-allowed text-xs text-slate-400 px-4 py-2.5"' : 'class="px-5 py-2.5 bg-slate-200 text-sena-dark font-bold text-xs rounded-xl hover:bg-slate-300 transition flex items-center gap-1"'}>
          <i class="fas fa-chevron-left"></i> Anterior
        </button>

        ${historyWizardStepIndex === total - 1 ? `
          <button onclick="finishHistoryWizard()" class="px-6 py-2.5 bg-sena-dark text-white font-black text-xs uppercase tracking-wider rounded-xl hover:bg-slate-800 transition shadow-md flex items-center gap-2">
            <i class="fas fa-circle-check text-[#27F531]"></i> Finalizar y Ver Histórico
          </button>
        ` : `
          <button onclick="nextHistoryWizardStep()" class="px-5 py-2.5 bg-sena-dark text-white font-bold text-xs rounded-xl hover:bg-slate-800 transition flex items-center gap-1">
            Siguiente <i class="fas fa-chevron-right ml-1"></i>
          </button>
        `}
      </div>
    </div>
  `;
}

let isSavingAutoStep = false;

async function autoSaveHistoryWizardOption(varId, optId) {
  if (isSavingAutoStep) return;

  const q = allHistoryQuestions.find(p => p.variable_id === varId);
  if (!q) return;

  if (historyWizardAnswers[varId] === optId && q.pendiente === false) return;

  isSavingAutoStep = true;
  historyWizardAnswers[varId] = optId;

  const payloadItem = {
    variable_id: varId,
    variable_version_id: q.variable_version_id || null,
    opcion_id: optId,
    valor_texto: null
  };

  const container = document.getElementById('myHistoryTimeline');
  if (container) renderHistoryWizardUnanswered(container);

  try {
    const indicator = document.getElementById('autoSaveStatusIndicator');
    if (indicator) indicator.innerHTML = `<span class="text-slate-500 animate-pulse"><i class="fas fa-spinner fa-spin mr-1"></i> Guardando respuesta...</span>`;

    await API.submitRespuestas(q.encuesta_id || 1, [payloadItem], q.corte_id || null);

    if (indicator) indicator.innerHTML = `<span class="text-[#2E8800] flex items-center gap-1"><i class="fas fa-circle-check text-[#39A900]"></i> Respuesta guardada automáticamente</span>`;

    q.pendiente = false;
    const optObj = q.opciones ? q.opciones.find(o => o.id === optId) : null;
    const respText = optObj ? optObj.texto : 'Respuesta guardada';
    q.respuestas = [{
      id: Date.now(),
      fecha_respuesta: new Date().toISOString(),
      respuesta_texto: respText,
      origen: 'web'
    }];
  } catch (err) {
    Toast.error(err.message || 'Error al guardar respuesta automática', 'Error');
  } finally {
    isSavingAutoStep = false;
  }
}

async function autoSaveHistoryWizardText(varId, textVal) {
  if (!textVal || !textVal.trim()) return;
  historyWizardAnswers[varId] = textVal;
  const q = allHistoryQuestions.find(p => p.variable_id === varId);
  if (!q) return;

  const payloadItem = {
    variable_id: varId,
    variable_version_id: q.variable_version_id || null,
    opcion_id: null,
    valor_texto: String(textVal)
  };

  try {
    const indicator = document.getElementById('autoSaveStatusIndicator');
    if (indicator) indicator.innerHTML = `<span class="text-slate-500 animate-pulse"><i class="fas fa-spinner fa-spin mr-1"></i> Guardando respuesta...</span>`;

    await API.submitRespuestas(q.encuesta_id || 1, [payloadItem], q.corte_id || null);

    if (indicator) indicator.innerHTML = `<span class="text-[#2E8800] flex items-center gap-1"><i class="fas fa-circle-check text-[#39A900]"></i> Respuesta guardada automáticamente</span>`;

    q.pendiente = false;
    if (!q.respuestas) q.respuestas = [];
    q.respuestas.push({
      id: Date.now(),
      fecha_respuesta: new Date().toISOString(),
      respuesta_texto: textVal,
      origen: 'web'
    });
  } catch (err) {
    Toast.error(err.message || 'Error al guardar respuesta automática', 'Error');
  }
}

function nextHistoryWizardStep() {
  if (historyWizardStepIndex < allHistoryQuestions.length - 1) {
    historyWizardStepIndex++;
    const container = document.getElementById('myHistoryTimeline');
    if (container) renderHistoryWizardUnanswered(container);
  }
}

function prevHistoryWizardStep() {
  if (historyWizardStepIndex > 0) {
    historyWizardStepIndex--;
    const container = document.getElementById('myHistoryTimeline');
    if (container) renderHistoryWizardUnanswered(container);
  }
}

async function finishHistoryWizard() {
  Toast.success('¡Proceso de caracterización completado!', 'Encuesta Registrada');
  await loadMyHistory();
}

/**
 * CASO B: Renderizado de la Línea de Tiempo de Evolución Histórica
 */
function renderHistoryTimelineCards(container) {
  container.innerHTML = allHistoryQuestions.map((h, idx) => {
    const varNombre = h.variable_nombre || 'Variable';
    const pregunta = h.pregunta_texto || 'Pregunta registrada';
    const isPendiente = h.pendiente === true || !h.respuestas || h.respuestas.length === 0;

    // Deduplicar estrictamente respuestas por id o por texto+fecha
    const rawList = h.respuestas && h.respuestas.length ? h.respuestas : (
      (h.id && h.respuesta_texto) ? [{ id: h.id, fecha_respuesta: h.fecha_respuesta, respuesta_texto: h.respuesta_texto, origen: h.origen || 'web' }] : []
    );

    const seenKeys = new Set();
    const respuestasList = [];
    for (const r of rawList) {
      const key = r.id ? `id_${r.id}` : `${r.respuesta_texto}_${r.fecha_respuesta}`;
      if (!seenKeys.has(key)) {
        seenKeys.add(key);
        respuestasList.push(r);
      }
    }

    let listHtml = '';
    if (isPendiente || respuestasList.length === 0) {
      listHtml = `
        <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-600 text-xs font-medium flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <span>Sin respuestas registradas en esta medición.</span>
          <button onclick="openSingleQuestionModal(${h.variable_id})" class="px-3.5 py-1.5 bg-sena-dark text-white font-bold text-xs rounded-xl hover:bg-slate-800 transition shadow-sm flex items-center gap-1.5 self-end sm:self-auto">
            <i class="fas fa-pen-to-square text-[#27F531]"></i> Responder ahora
          </button>
        </div>
      `;
    } else {
      listHtml = respuestasList.map((resp, rIdx) => {
        const fechaFormateada = formatFechaColombia(resp.fecha_respuesta);
        const isLatest = rIdx === 0;

        return `
          <div class="p-3.5 rounded-xl border ${isLatest ? 'bg-[#EBF8E1]/80 border-[#39A900]/40' : 'bg-[#F8F9FA] border-slate-200'} flex items-center justify-between gap-3 transition">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                ${isLatest ? '<span class="text-[9px] font-black uppercase bg-[#39A900] text-white px-2 py-0.5 rounded-full">Última medición</span>' : '<span class="text-[9px] font-extrabold uppercase bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full">Medición anterior</span>'}
                <span class="text-[10px] font-bold text-slate-500"><i class="far fa-clock mr-1"></i>${fechaFormateada}</span>
              </div>
              <p class="text-xs font-black ${isLatest ? 'text-[#00324D]' : 'text-slate-700'} mt-1 flex items-center gap-1.5">
                <i class="fas ${isLatest ? 'fa-circle-check text-[#39A900]' : 'fa-history text-slate-400'} text-xs"></i> ${resp.respuesta_texto || 'Respuesta registrada'}
              </p>
            </div>
          </div>
        `;
      }).join('');
    }

    return `
      <div class="p-5 bg-white rounded-2xl border border-sena-border shadow-sm space-y-3.5">
        <!-- Variable & Header -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-sena-border pb-3 gap-2">
          <div class="flex items-center gap-2.5">
            <span class="w-6 h-6 rounded-full bg-sena-dark text-white text-[10px] font-black flex items-center justify-center">${idx + 1}</span>
            <h4 class="font-black text-sena-dark text-sm">${varNombre}</h4>
          </div>

          <div class="flex items-center gap-3 flex-wrap">
            <span class="text-[10px] font-black text-slate-400 uppercase tracking-wider">${respuestasList.length} ${respuestasList.length === 1 ? 'medición' : 'mediciones'}</span>

            <button onclick="openSingleQuestionModal(${h.variable_id})" class="px-3.5 py-1.5 bg-sena-dark text-white font-extrabold text-xs rounded-xl hover:bg-slate-800 transition flex items-center gap-1.5 shadow-sm">
              <i class="fas fa-[#27F531] fa-plus"></i> Registrar nueva respuesta
            </button>
          </div>
        </div>

        <!-- Question Text -->
        <div class="space-y-1">
          <span class="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider block">Pregunta Realizada</span>
          <p class="text-xs sm:text-sm font-bold text-sena-dark leading-snug">
            ${pregunta}
            ${isPendiente || respuestasList.length === 0 ? `
              <span class="inline-flex items-center px-2 py-0.5 text-[10px] font-black uppercase bg-red-600 text-white rounded-full ml-1.5 align-middle shadow-sm">
                Pendiente
              </span>
            ` : ''}
          </p>
        </div>

        <!-- Answers List / Status -->
        <div class="space-y-2 pt-1">
          <span class="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider block">Historial de Respuestas</span>
          <div class="space-y-2">
            ${listHtml}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * LÓGICA DEL MODAL DE RESPUESTA POR PREGUNTA INDIVIDUAL
 */
function openSingleQuestionModal(variableId) {
  targetSingleQuestion = allHistoryQuestions.find(q => q.variable_id === variableId);
  if (!targetSingleQuestion) {
    Toast.error('No se pudo encontrar la pregunta seleccionada.', 'Error');
    return;
  }

  singleQuestionAnswerVal = null;

  document.getElementById('sqModalTitle').textContent = targetSingleQuestion.variable_nombre || 'Pregunta';
  document.getElementById('sqModalQuestionText').textContent = targetSingleQuestion.pregunta_texto || '';

  const container = document.getElementById('sqModalChoicesContainer');
  if (!container) return;

  if (targetSingleQuestion.opciones && targetSingleQuestion.opciones.length) {
    container.innerHTML = `
      <div class="space-y-2">
        ${targetSingleQuestion.opciones.map(opt => `
          <label onclick="singleQuestionAnswerVal = ${opt.id}" class="flex items-center p-3.5 rounded-xl border border-sena-border hover:bg-[#EBF8E1]/50 hover:border-[#39A900]/50 cursor-pointer transition">
            <input type="radio" name="sqOption" value="${opt.id}" class="text-[#27F531] focus:ring-[#27F531]">
            <span class="ml-3 text-xs sm:text-sm text-sena-dark font-semibold">${opt.texto}</span>
          </label>
        `).join('')}
      </div>
    `;
  } else {
    container.innerHTML = `
      <div>
        <textarea id="sqTextarea" oninput="singleQuestionAnswerVal = this.value" rows="3" class="w-full text-xs sm:text-sm p-3.5 border border-sena-border rounded-xl focus:ring-2 focus:ring-[#27F531]" placeholder="Escriba su respuesta aquí..."></textarea>
      </div>
    `;
  }

  document.getElementById('modalSingleQuestion')?.classList.remove('hidden');
}

function closeSingleQuestionModal() {
  document.getElementById('modalSingleQuestion')?.classList.add('hidden');
  targetSingleQuestion = null;
  singleQuestionAnswerVal = null;
}

async function submitSingleQuestionAnswer() {
  try {
    if (!targetSingleQuestion) return;

    if (singleQuestionAnswerVal === null || singleQuestionAnswerVal === undefined || singleQuestionAnswerVal === '') {
      Toast.warning('Por favor seleccione una opción o ingrese su respuesta antes de guardar.', 'Respuesta Requerida');
      return;
    }

    const isOptId = typeof singleQuestionAnswerVal === 'number' || (typeof singleQuestionAnswerVal === 'string' && !isNaN(parseInt(singleQuestionAnswerVal)) && /^\d+$/.test(String(singleQuestionAnswerVal).trim()));

    const payloadItem = {
      variable_id: targetSingleQuestion.variable_id,
      variable_version_id: targetSingleQuestion.variable_version_id || null,
      opcion_id: isOptId ? parseInt(singleQuestionAnswerVal) : null,
      valor_texto: !isOptId ? String(singleQuestionAnswerVal) : null
    };

    Loading.show('Guardando respuesta...');
    await API.submitRespuestas(
      targetSingleQuestion.encuesta_id || 1,
      [payloadItem],
      targetSingleQuestion.corte_id || null
    );
    Loading.hide();

    Toast.success('¡Respuesta registrada exitosamente!', 'Medición Guardada');
    closeSingleQuestionModal();
    await loadMyHistory();
  } catch (err) {
    Loading.hide();
    Toast.error(err.message || 'Error al guardar respuesta', 'Fallo al Guardar');
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
