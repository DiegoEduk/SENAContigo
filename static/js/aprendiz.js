// Learner Portal JavaScript Logic
let currentSurveys = [];
let selectedAnswers = {}; // { variable_id: opcion_id }
let observations = {}; // { variable_id: text }

document.addEventListener('DOMContentLoaded', async () => {
    const user = API.getUser();
    if (!user || user.rol !== 'aprendiz') {
        window.location.href = '/';
        return;
    }

    document.getElementById('userName').textContent = `${user.nombres} ${user.apellidos}`;
    document.getElementById('greetingName').textContent = user.nombres;

    await loadEncuestas();
});

function switchTab(tab) {
    const secEnc = document.getElementById('secEncuestas');
    const secHis = document.getElementById('secHistorial');
    const secCon = document.getElementById('secContrato');
    const btnEnc = document.getElementById('tabBtnEncuestas');
    const btnHis = document.getElementById('tabBtnHistorial');
    const btnCon = document.getElementById('tabBtnContrato');

    secEnc.classList.add('hidden');
    secHis.classList.add('hidden');
    if (secCon) secCon.classList.add('hidden');

    btnEnc.className = "py-2.5 px-4 text-slate-500 hover:text-slate-800 border-b-2 border-transparent flex items-center gap-2";
    btnHis.className = "py-2.5 px-4 text-slate-500 hover:text-slate-800 border-b-2 border-transparent flex items-center gap-2";
    if (btnCon) btnCon.className = "py-2.5 px-4 text-slate-500 hover:text-slate-800 border-b-2 border-transparent flex items-center gap-2";

    if (tab === 'encuestas') {
        secEnc.classList.remove('hidden');
        btnEnc.className = "py-2.5 px-4 text-sena-green border-b-2 border-sena-green flex items-center gap-2 font-bold";
    } else if (tab === 'historial') {
        secHis.classList.remove('hidden');
        btnHis.className = "py-2.5 px-4 text-sena-green border-b-2 border-sena-green flex items-center gap-2 font-bold";
        loadHistorial();
    } else if (tab === 'contrato') {
        if (secCon) secCon.classList.remove('hidden');
        if (btnCon) btnCon.className = "py-2.5 px-4 text-sena-green border-b-2 border-sena-green flex items-center gap-2 font-bold";
        loadMiContrato();
    }
}

async function loadEncuestas() {
    const container = document.getElementById('surveyContainer');
    try {
        currentSurveys = await API.getEncuestasPendientes();
        
        if (!currentSurveys || currentSurveys.length === 0) {
            container.innerHTML = `
                <div class="sena-card p-8 text-center bg-white space-y-3">
                    <div class="w-16 h-16 bg-emerald-100 text-sena-green rounded-full flex items-center justify-center mx-auto text-2xl">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h3 class="font-bold text-lg text-slate-800">¡Al día! No tienes encuestas pendientes</h3>
                    <p class="text-xs text-slate-500 max-w-md mx-auto">
                        Gracias por mantener actualizada tu información. El equipo SENAContigo te notificará cuando se habilite un nuevo seguimiento.
                    </p>
                </div>
            `;
            return;
        }

        renderSurveys(currentSurveys);
    } catch (err) {
        container.innerHTML = `
            <div class="sena-card p-6 bg-red-50 text-red-700 text-sm border border-red-200 text-center">
                <i class="fas fa-exclamation-triangle mr-2"></i> ${err.message}
            </div>
        `;
    }
}

function renderSurveys(surveys) {
    const container = document.getElementById('surveyContainer');
    container.innerHTML = '';

    surveys.forEach((survey) => {
        const card = document.createElement('div');
        card.className = 'sena-card p-6 bg-white space-y-6 border-t-4 border-sena-green';

        let questionsHtml = '';
        if (survey.preguntas && survey.preguntas.length > 0) {
            survey.preguntas.forEach((p, idx) => {
                const v = p.variable;
                if (!v) return;

                let optionsHtml = '';
                if (v.opciones && v.opciones.length > 0) {
                    optionsHtml = v.opciones.map((op) => {
                        const levelClass = getLevelBadgeClass(op.nivel_afectacion);
                        return `
                            <div class="option-radio-card flex items-start space-x-3 cursor-pointer" 
                                 onclick="selectOption(${v.id}, ${op.id}, this)">
                                <input type="radio" name="var_${v.id}" value="${op.id}" class="mt-1 text-sena-green focus:ring-sena-green">
                                <div class="flex-grow text-xs">
                                    <div class="flex items-center justify-between">
                                        <span class="font-bold text-slate-800 text-sm">${op.texto}</span>
                                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${levelClass}">
                                            ${getLevelLabel(op.nivel_afectacion)}
                                        </span>
                                    </div>
                                    ${op.codigo ? `<span class="text-[10px] text-slate-400">Código: ${op.codigo}</span>` : ''}
                                </div>
                            </div>
                        `;
                    }).join('');
                }

                questionsHtml += `
                    <div class="space-y-3 border-b border-slate-100 pb-5 last:border-0">
                        <div class="flex items-center gap-2">
                            <span class="w-6 h-6 rounded-full bg-sena-green text-white font-bold text-xs flex items-center justify-center flex-shrink-0">${idx + 1}</span>
                            <h4 class="font-bold text-sm text-slate-800">${v.nombre} ${p.obligatoria ? '<span class="text-red-500">*</span>' : ''}</h4>
                        </div>
                        ${v.descripcion ? `<p class="text-xs text-slate-500 italic pl-8">${v.descripcion}</p>` : ''}
                        
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pl-0 sm:pl-8 pt-1">
                            ${optionsHtml}
                        </div>

                        <div class="pl-0 sm:pl-8 pt-2">
                            <input type="text" placeholder="Observaciones opcionales sobre esta situación..." 
                                   onchange="setObservation(${v.id}, this.value)"
                                   class="w-full text-xs p-2 border border-slate-200 rounded focus:ring-1 focus:ring-sena-green outline-none">
                        </div>
                    </div>
                `;
            });
        }

        card.innerHTML = `
            <div class="flex justify-between items-start border-b border-slate-100 pb-3">
                <div>
                    <span class="px-2 py-0.5 rounded bg-emerald-100 text-sena-darkgreen text-[10px] font-bold uppercase">Encuesta Activa</span>
                    <h3 class="text-lg font-bold text-slate-900 mt-1">${survey.nombre}</h3>
                    <p class="text-xs text-slate-500">${survey.descripcion || 'Diligencie todas las preguntas obligatorias.'}</p>
                </div>
            </div>

            <form onsubmit="submitForm(event, ${survey.id})" class="space-y-6">
                ${questionsHtml}
                
                <div id="surveyAlert_${survey.id}" class="hidden p-3 rounded bg-red-50 text-red-700 text-xs border border-red-200"></div>

                <div class="pt-4 border-t border-slate-100 flex justify-end">
                    <button type="submit" id="btnSubmit_${survey.id}" 
                            class="px-6 py-2.5 bg-sena-green hover:bg-sena-darkgreen text-white font-bold text-sm rounded-lg transition shadow-md flex items-center gap-2">
                        <i class="fas fa-paper-plane"></i> Enviar Respuestas
                    </button>
                </div>
            </form>
        `;

        container.appendChild(card);
    });
}

function selectOption(variableId, optionId, cardElem) {
    selectedAnswers[variableId] = optionId;
    const parent = cardElem.parentElement;
    parent.querySelectorAll('.option-radio-card').forEach(c => c.classList.remove('selected'));
    cardElem.classList.add('selected');
    const radio = cardElem.querySelector('input[type="radio"]');
    if (radio) radio.checked = true;
}

function setObservation(variableId, val) {
    observations[variableId] = val;
}

async function submitForm(e, surveyId) {
    e.preventDefault();
    const alertBox = document.getElementById(`surveyAlert_${surveyId}`);
    const btn = document.getElementById(`btnSubmit_${surveyId}`);
    alertBox.classList.add('hidden');

    const survey = currentSurveys.find(s => s.id === surveyId);
    if (!survey) return;

    // Validate required
    const missing = [];
    survey.preguntas.forEach(p => {
        if (p.obligatoria && !selectedAnswers[p.variable_id]) {
            missing.push(p.variable ? p.variable.nombre : `Variable #${p.variable_id}`);
        }
    });

    if (missing.length > 0) {
        alertBox.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i> Por favor responda las preguntas obligatorias: <strong>${missing.join(', ')}</strong>`;
        alertBox.classList.remove('hidden');
        return;
    }

    // Format payload
    const respuestasPayload = Object.keys(selectedAnswers).map(varId => ({
        variable_id: parseInt(varId),
        opcion_id: parseInt(selectedAnswers[varId]),
        observacion: observations[varId] || null
    }));

    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Guardando respuestas...`;

    try {
        await API.submitRespuestas(surveyId, respuestasPayload);
        alertBox.className = "p-4 rounded-lg bg-emerald-50 text-emerald-800 text-xs border border-emerald-300 font-medium";
        alertBox.innerHTML = `<i class="fas fa-check-circle text-sena-green mr-1"></i> ¡Respuestas registradas exitosamente! Gracias por tu colaboración.`;
        alertBox.classList.remove('hidden');
        
        setTimeout(() => {
            selectedAnswers = {};
            observations = {};
            loadEncuestas();
            switchTab('historial');
        }, 1500);
    } catch (err) {
        alertBox.className = "p-3 rounded bg-red-50 text-red-700 text-xs border border-red-200";
        alertBox.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i> ${err.message}`;
        alertBox.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fas fa-paper-plane"></i> Enviar Respuestas`;
    }
}

async function loadHistorial() {
    const container = document.getElementById('timelineContainer');
    try {
        const history = await API.getMiHistorial();
        if (!history || history.length === 0) {
            container.innerHTML = `<p class="pl-6 text-xs text-slate-400 italic">No tienes respuestas registradas aún.</p>`;
            return;
        }

        // Group by fecha / encuesta
        container.innerHTML = history.map(item => {
            const dateStr = item.fecha_respuesta ? new Date(item.fecha_respuesta).toLocaleString('es-CO') : 'Fecha no especificada';
            const vName = item.variable ? item.variable.nombre : 'Variable';
            const opText = item.opcion ? item.opcion.texto : (item.respuesta_texto || 'Respuesta registrada');
            const lvl = item.opcion ? item.opcion.nivel_afectacion : 0;
            const levelClass = getLevelBadgeClass(lvl);
            const levelLabel = getLevelLabel(lvl);

            return `
                <div class="relative pl-6 pb-4">
                    <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-sena-green border-2 border-white"></span>
                    <div class="sena-card p-4 text-xs space-y-1">
                        <div class="flex items-center justify-between text-slate-400 text-[10px]">
                            <span><i class="fas fa-calendar-alt mr-1"></i> ${dateStr}</span>
                            <span class="px-2 py-0.5 rounded-full font-bold ${levelClass}">${levelLabel}</span>
                        </div>
                        <h5 class="font-bold text-slate-800 text-sm">${vName}</h5>
                        <p class="text-slate-600 font-medium">Respuesta: <span class="text-sena-green font-bold">${opText}</span></p>
                        ${item.observacion ? `<p class="text-slate-400 italic">"${item.observacion}"</p>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        container.innerHTML = `<p class="pl-6 text-xs text-red-500">Error al cargar historial: ${err.message}</p>`;
    }
}

function getLevelBadgeClass(lvl) {
    switch (parseInt(lvl)) {
        case 0: return 'badge-level-0';
        case 1: return 'badge-level-1';
        case 2: return 'badge-level-2';
        case 3: return 'badge-level-3';
        case 4: return 'badge-level-4';
        default: return 'badge-level-0';
    }
}

function getLevelLabel(lvl) {
    switch (parseInt(lvl)) {
        case 0: return '0 - Sin afectación';
        case 1: return '1 - Leve';
        case 2: return '2 - Moderada';
        case 3: return '3 - Grave';
        case 4: return '4 - Crítica';
        default: return '0 - Sin afectación';
    }
}

async function loadMiContrato() {
    const container = document.getElementById('contratoAprendizContainer');
    if (!container) return;

    const user = API.getUser();
    if (!user) return;

    try {
        const contratos = await API.getContratosAprendiz(user.id);

        if (!contratos || contratos.length === 0) {
            container.innerHTML = `
                <div class="p-6 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 space-y-2">
                    <div class="flex items-center gap-2 text-amber-700 font-bold text-sm">
                        <i class="fas fa-info-circle text-lg"></i>
                        <span>Sin Contrato de Aprendizaje Registrado</span>
                    </div>
                    <p class="text-xs text-amber-800 leading-relaxed">
                        Actualmente no tienes ningún contrato de aprendizaje registrado en el sistema. 
                        <strong>Nota:</strong> Si no hay contratos registrados es porque aún no cuentas con este recurso o tu alternativa productiva no ha sido vinculada formalmente por tu centro de formación.
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = contratos.map(c => {
            let stateBadge = 'bg-slate-100 text-slate-700';
            if (c.estado_contrato === 'EN PATROCINIO') stateBadge = 'bg-indigo-100 text-indigo-800 font-bold';
            if (c.estado_contrato === 'EN ETAPA PRACTICA') stateBadge = 'bg-emerald-100 text-sena-darkgreen font-bold';
            if (c.estado_contrato === 'ACTIVO') stateBadge = 'bg-teal-100 text-teal-800 font-bold';
            if (c.estado_contrato === 'FINALIZADO') stateBadge = 'bg-blue-100 text-blue-800 font-bold';
            if (c.estado_contrato === 'SUSPENDIDO') stateBadge = 'bg-amber-100 text-amber-800 font-bold';

            return `
                <div class="sena-card p-5 bg-white border-l-4 border-sena-green space-y-3">
                    <div class="flex justify-between items-start">
                        <div>
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Empresa Patrocinadora</span>
                            <h4 class="text-lg font-black text-slate-900">${c.nombre_empresa}</h4>
                        </div>
                        <span class="px-3 py-1 rounded-full text-xs font-bold ${stateBadge}">${c.estado_contrato}</span>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-600 pt-2 border-t border-slate-100">
                        <div>
                            <span class="font-bold block text-slate-700">Ubicación Etapa Práctica:</span>
                            <span><i class="fas fa-map-marker-alt text-sena-green mr-1"></i> ${c.ciudad}, ${c.departamento}</span>
                        </div>
                        <div>
                            <span class="font-bold block text-slate-700">Fecha de Inicio:</span>
                            <span><i class="fas fa-calendar-check text-sena-green mr-1"></i> ${c.fecha_inicio_contrato}</span>
                        </div>
                        ${c.fecha_fin_contrato ? `
                        <div>
                            <span class="font-bold block text-slate-700">Fecha de Finalización:</span>
                            <span><i class="fas fa-calendar-xmark text-slate-400 mr-1"></i> ${c.fecha_fin_contrato}</span>
                        </div>
                        ` : ''}
                        ${c.ficha_id ? `
                        <div>
                            <span class="font-bold block text-slate-700">Ficha Formativa Originaria:</span>
                            <span>Ficha ${c.ficha_id}</span>
                        </div>
                        ` : ''}
                    </div>

                    ${c.observaciones ? `
                    <div class="bg-slate-50 p-2.5 rounded text-xs text-slate-600 border border-slate-100">
                        <strong class="text-slate-700">Observaciones:</strong> ${c.observaciones}
                    </div>
                    ` : ''}
                </div>
            `;
        }).join('');

    } catch (err) {
        container.innerHTML = `<div class="p-4 bg-red-50 text-red-600 text-xs rounded border border-red-200">Error al cargar contrato: ${err.message}</div>`;
    }
}

