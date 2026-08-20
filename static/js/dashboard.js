// Dashboard JavaScript Logic
let chartEstadoActualInstance = null;
let chartEvolucionInstance = null;
let categoriesList = [];

document.addEventListener('DOMContentLoaded', async () => {
    const user = API.getUser();
    if (!user || user.rol === 'aprendiz') {
        window.location.href = '/';
        return;
    }

    // Set User Nav info
    document.getElementById('navUserName').textContent = `${user.nombres} ${user.apellidos}`;
    document.getElementById('navUserMail').textContent = user.correo_electronico;
    const badge = document.getElementById('userRoleBadge');
    badge.textContent = user.rol.toUpperCase();

    const scope = document.getElementById('scopeDetails');
    if (user.rol === 'direccion') {
        scope.innerHTML = `<p><i class="fas fa-building text-sena-green mr-1"></i> Cobertura: Regional Asignada</p>`;
    } else if (user.rol === 'coordinador') {
        scope.innerHTML = `<p><i class="fas fa-sitemap text-sena-green mr-1"></i> Cobertura: Centro de Formación</p>`;
    } else if (user.rol === 'instructor') {
        scope.innerHTML = `<p><i class="fas fa-chalkboard-user text-sena-green mr-1"></i> Cobertura: Fichas Asignadas</p>`;
    } else if (user.rol === 'lider_bienestar') {
        scope.innerHTML = `<p><i class="fas fa-heart text-sena-green mr-1"></i> Cobertura: Módulo de Beneficios</p>`;
    } else if (user.rol === 'lider_contratacion') {
        scope.innerHTML = `<p><i class="fas fa-file-contract text-sena-green mr-1"></i> Cobertura: Módulo de Contratación</p>`;
        navSwitch('contratos');
        return;
    }

    await loadResumenData();
});

function navSwitch(secName) {
    ['resumen', 'analytics', 'variables', 'encuestas', 'casos', 'contratos'].forEach(s => {
        const sec = document.getElementById(`sec-${s}`);
        const btn = document.getElementById(`nav-${s}`);
        if (!sec || !btn) return;
        if (s === secName) {
            sec.classList.remove('hidden');
            btn.className = "w-full text-left px-3 py-2.5 rounded-lg text-xs font-bold text-sena-green bg-sena-lightgreen flex items-center gap-2.5 transition";
        } else {
            sec.classList.add('hidden');
            btn.className = "w-full text-left px-3 py-2.5 rounded-lg text-xs font-bold text-slate-600 hover:bg-slate-100 flex items-center gap-2.5 transition";
        }
    });

    if (secName === 'analytics') loadAnalyticsData();
    if (secName === 'variables') loadVariablesData();
    if (secName === 'encuestas') loadEncuestasData();
    if (secName === 'casos') loadCasosData();
    if (secName === 'contratos') loadContratosData();
}

async function loadResumenData() {
    try {
        const aprendices = await API.getAprendices();
        document.getElementById('kpiAprendices').textContent = aprendices.length;

        const encuestas = await API.getEncuestas();
        document.getElementById('kpiEncuestas').textContent = encuestas.length;

        const casos = await API.getCasos();
        const pendientes = casos.filter(c => c.estado === 'ABIERTO' || c.estado === 'EN_PROCESO');
        document.getElementById('kpiCasos').textContent = pendientes.length;

        // Render Chart Estado Actual
        const stateData = await API.getAnalyticsEstadoActual();
        let gravesCount = 0;
        stateData.forEach(d => {
            gravesCount += (d.grave + d.critica);
        });
        document.getElementById('kpiAfectados').textContent = gravesCount;

        renderChartEstadoActual(stateData);

    } catch (err) {
        console.error("Error loading resumen data:", err);
    }
}

function renderChartEstadoActual(data) {
    const ctx = document.getElementById('chartEstadoActual');
    if (!ctx) return;

    if (chartEstadoActualInstance) {
        chartEstadoActualInstance.destroy();
    }

    const labels = data.map(d => d.variable_nombre);
    const datasetSin = data.map(d => d.sin_afectacion);
    const datasetLeve = data.map(d => d.leve);
    const datasetMod = data.map(d => d.moderada);
    const datasetGrave = data.map(d => d.grave);
    const datasetCrit = data.map(d => d.critica);

    chartEstadoActualInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: '0 - Sin Afectación', data: datasetSin, backgroundColor: '#39A900' },
                { label: '1 - Leve', data: datasetLeve, backgroundColor: '#0284C7' },
                { label: '2 - Moderada', data: datasetMod, backgroundColor: '#D97706' },
                { label: '3 - Grave', data: datasetGrave, backgroundColor: '#EA580C' },
                { label: '4 - Crítica', data: datasetCrit, backgroundColor: '#DC2626' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: true },
                y: { stacked: true, beginAtZero: true }
            },
            plugins: {
                legend: { position: 'bottom', labels: { font: { size: 11 } } }
            }
        }
    });
}

async function loadAnalyticsData() {
    try {
        const evoData = await API.getAnalyticsEvolucion();
        renderChartEvolucion(evoData);

        const indices = await API.getAnalyticsIndiceAfectacion();
        renderTablaIndice(indices);
    } catch (err) {
        console.error("Error loading analytics data:", err);
    }
}

function renderChartEvolucion(evoData) {
    const ctx = document.getElementById('chartEvolucion');
    if (!ctx) return;

    if (chartEvolucionInstance) {
        chartEvolucionInstance.destroy();
    }

    const labels = evoData.map(e => `${e.encuesta_nombre} (${e.fecha_inicio || ''})`);
    const graveCriticoData = evoData.map(e => {
        const n = e.niveles || {};
        return (parseInt(n["3"] || 0) + parseInt(n["4"] || 0));
    });
    const leveModData = evoData.map(e => {
        const n = e.niveles || {};
        return (parseInt(n["1"] || 0) + parseInt(n["2"] || 0));
    });

    chartEvolucionInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Afectación Grave / Crítica (Nivel 3 y 4)',
                    data: graveCriticoData,
                    borderColor: '#DC2626',
                    backgroundColor: 'rgba(220, 38, 38, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Afectación Leve / Moderada (Nivel 1 y 2)',
                    data: leveModData,
                    borderColor: '#D97706',
                    backgroundColor: 'rgba(217, 119, 6, 0.05)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function renderTablaIndice(indices) {
    const tbody = document.getElementById('tblIndiceAfectacion');
    if (!indices || indices.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-slate-400">Sin datos de índice aún.</td></tr>`;
        return;
    }

    tbody.innerHTML = indices.map(idx => {
        let badgeClass = 'badge-level-0';
        if (idx.nivel_clasificacion === 'MODERADO') badgeClass = 'badge-level-2';
        if (idx.nivel_clasificacion === 'ALTO') badgeClass = 'badge-level-3';
        if (idx.nivel_clasificacion === 'CRITICO') badgeClass = 'badge-level-4';

        return `
            <tr class="hover:bg-slate-50">
                <td class="p-3 font-bold text-slate-800">${idx.nombres} ${idx.apellidos}</td>
                <td class="p-3 font-medium">${idx.ficha}</td>
                <td class="p-3 font-black text-sena-dark">${idx.indice_total.toFixed(1)} pts</td>
                <td class="p-3"><span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${badgeClass}">${idx.nivel_clasificacion}</span></td>
            </tr>
        `;
    }).join('');
}

async function loadVariablesData() {
    const container = document.getElementById('listVariables');
    try {
        const variables = await API.getVariables();
        categoriesList = await API.getCategorias();

        container.innerHTML = variables.map(v => {
            const opcionesHtml = (v.opciones || []).map(op => `
                <div class="flex justify-between items-center bg-slate-50 p-2 rounded text-xs">
                    <span class="font-medium text-slate-700">${op.texto} (${op.codigo})</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${getLevelBadgeClass(op.nivel_afectacion)}">
                        Nivel ${op.nivel_afectacion}
                    </span>
                </div>
            `).join('');

            return `
                <div class="sena-card p-4 bg-white space-y-3">
                    <div class="flex justify-between items-start">
                        <div>
                            <span class="text-[10px] font-bold text-sena-green uppercase">Código: ${v.codigo}</span>
                            <h4 class="font-bold text-base text-slate-800">${v.nombre}</h4>
                            <p class="text-xs text-slate-500">${v.descripcion || 'Sin descripción'}</p>
                        </div>
                    </div>
                    <div class="space-y-1.5 pt-2 border-t border-slate-100">
                        <p class="text-[10px] font-bold text-slate-400 uppercase">Opciones de Respuesta:</p>
                        ${opcionesHtml}
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        container.innerHTML = `<p class="text-xs text-red-500">Error al cargar variables: ${err.message}</p>`;
    }
}

async function loadEncuestasData() {
    const container = document.getElementById('listEncuestas');
    try {
        const encuestas = await API.getEncuestas();
        container.innerHTML = encuestas.map(e => `
            <div class="sena-card p-5 bg-white space-y-2 border-l-4 border-sena-green">
                <div class="flex justify-between items-start">
                    <div>
                        <span class="px-2 py-0.5 rounded bg-emerald-100 text-sena-darkgreen text-[10px] font-bold uppercase">${e.tipo}</span>
                        <h4 class="text-base font-bold text-slate-800 mt-1">${e.nombre}</h4>
                        <p class="text-xs text-slate-500">${e.descripcion || ''}</p>
                    </div>
                    <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-700">${e.estado.toUpperCase()}</span>
                </div>
                <div class="text-xs text-slate-400 pt-2 border-t border-slate-100 flex gap-4">
                    <span><i class="fas fa-calendar mr-1"></i> Inicio: ${e.fecha_inicio || 'N/A'}</span>
                    <span><i class="fas fa-question-circle mr-1"></i> Preguntas: ${e.preguntas ? e.preguntas.length : 0}</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p class="text-xs text-red-500">Error al cargar encuestas: ${err.message}</p>`;
    }
}

async function loadCasosData() {
    const tbody = document.getElementById('tblCasos');
    try {
        const casos = await API.getCasos();
        if (!casos || casos.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">Sin casos registrados.</td></tr>`;
            return;
        }

        tbody.innerHTML = casos.map(c => {
            const aprName = c.aprendiz ? `${c.aprendiz.nombres} ${c.aprendiz.apellidos}` : 'Aprendiz';
            const dateStr = c.fecha_creacion ? new Date(c.fecha_creacion).toLocaleDateString('es-CO') : '';
            
            let prioBadge = 'bg-slate-100 text-slate-700';
            if (c.prioridad === 'CRITICA') prioBadge = 'bg-red-100 text-red-700 font-bold';
            if (c.prioridad === 'ALTA') prioBadge = 'bg-orange-100 text-orange-700 font-bold';

            return `
                <tr class="hover:bg-slate-50">
                    <td class="p-3">
                        <span class="font-bold text-slate-800 block">${c.titulo}</span>
                        <span class="text-[10px] text-slate-400">${c.descripcion || ''}</span>
                    </td>
                    <td class="p-3 font-medium">${aprName}</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] ${prioBadge}">${c.prioridad}</span></td>
                    <td class="p-3 font-bold text-sena-dark">${c.estado}</td>
                    <td class="p-3 text-slate-400">${dateStr}</td>
                    <td class="p-3 text-right">
                        <button onclick="resolveCaso(${c.id})" class="px-2.5 py-1 bg-sena-green text-white text-[10px] font-bold rounded hover:bg-sena-darkgreen transition">
                            <i class="fas fa-check mr-1"></i> Resolver
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Error: ${err.message}</td></tr>`;
    }
}

async function resolveCaso(casoId) {
    const comment = prompt("Ingrese nota de seguimiento para marcar el caso como RESUELTO:");
    if (!comment) return;

    try {
        await API.addSeguimientoCaso(casoId, comment, "RESUELTO");
        alert("Caso actualizado a RESUELTO.");
        loadCasosData();
    } catch (err) {
        alert("Error al resolver caso: " + err.message);
    }
}

function openModalVariable() {
    const modal = document.getElementById('modalVariable');
    const select = document.getElementById('varCategoriaId');
    select.innerHTML = categoriesList.map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');
    modal.classList.remove('hidden');
}

function closeModalVariable() {
    document.getElementById('modalVariable').classList.add('hidden');
}

async function handleCreateVariable(e) {
    e.preventDefault();
    const catId = parseInt(document.getElementById('varCategoriaId').value);
    const nombre = document.getElementById('varNombre').value.trim();
    const codigo = document.getElementById('varCodigo').value.trim().toUpperCase();
    const descripcion = document.getElementById('varDescripcion').value.trim();

    try {
        await API.createVariable({
            categoria_id: catId,
            nombre: nombre,
            codigo: codigo,
            descripcion: descripcion,
            tipo_respuesta: "opcion",
            opciones: [
                { codigo: "NORMAL", texto: "Sin afectación / Normal", valor_numerico: 0, orden: 1, nivel_afectacion: 0 },
                { codigo: "AFECTADA", texto: "Afectado levemente", valor_numerico: 1, orden: 2, nivel_afectacion: 1 },
                { codigo: "GRAVE", texto: "Afectación crítica o grave", valor_numerico: 3, orden: 3, nivel_afectacion: 3 }
            ]
        });
        alert("¡Variable creada exitosamente!");
        closeModalVariable();
        loadVariablesData();
    } catch (err) {
        alert("Error al crear variable: " + err.message);
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

// Contratación de Aprendices Functions
async function loadContratosData() {
    await loadContratos();
}

async function loadContratos() {
    const tbody = document.getElementById('tblContratos');
    if (!tbody) return;

    const search = document.getElementById('searchContratos')?.value?.trim() || '';
    const estado = document.getElementById('filterEstadoContrato')?.value || '';

    try {
        const params = {};
        if (search) params.search = search;
        if (estado) params.estado = estado;

        const contratos = await API.getContratos(params);

        if (!contratos || contratos.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-400">No se encontraron contratos de aprendizaje registrados.</td></tr>`;
            return;
        }

        tbody.innerHTML = contratos.map(c => {
            let stateBadge = 'bg-slate-100 text-slate-700';
            if (c.estado_contrato === 'EN PATROCINIO') stateBadge = 'bg-indigo-100 text-indigo-800 font-bold';
            if (c.estado_contrato === 'EN ETAPA PRACTICA') stateBadge = 'bg-emerald-100 text-sena-darkgreen font-bold';
            if (c.estado_contrato === 'ACTIVO') stateBadge = 'bg-teal-100 text-teal-800 font-bold';
            if (c.estado_contrato === 'FINALIZADO') stateBadge = 'bg-blue-100 text-blue-800 font-bold';
            if (c.estado_contrato === 'SUSPENDIDO') stateBadge = 'bg-amber-100 text-amber-800 font-bold';
            if (c.estado_contrato === 'CANCELADO') stateBadge = 'bg-red-100 text-red-800 font-bold';

            const aprNombre = c.aprendiz_nombre_completo || 'Aprendiz N/A';
            const fichaStr = c.ficha_id ? `Ficha ${c.ficha_id}` : 'Ficha N/A';
            const ubicacion = `${c.ciudad || ''}, ${c.departamento || ''}`;

            return `
                <tr class="hover:bg-slate-50">
                    <td class="p-3">
                        <span class="font-bold text-slate-800 block">${c.nombre_empresa}</span>
                        <span class="text-[10px] text-slate-400">${c.observaciones || ''}</span>
                    </td>
                    <td class="p-3 font-medium">${aprNombre}</td>
                    <td class="p-3 text-slate-500 font-medium">${fichaStr}</td>
                    <td class="p-3 text-slate-600 font-medium">${ubicacion}</td>
                    <td class="p-3 text-slate-500">${c.fecha_inicio_contrato || ''}</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] ${stateBadge}">${c.estado_contrato}</span></td>
                    <td class="p-3 text-right">
                        <button onclick="changeEstadoContrato(${c.id}, '${c.estado_contrato}')" class="px-2 py-1 bg-slate-800 text-white text-[10px] font-bold rounded hover:bg-slate-700 transition">
                            <i class="fas fa-edit mr-1"></i> Cambiar Estado
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-red-500">Error al cargar contratos: ${err.message}</td></tr>`;
    }
}

async function openModalContrato() {
    const modal = document.getElementById('modalContrato');
    const select = document.getElementById('contratoMatriculaId');
    select.innerHTML = '<option value="">Cargando matrículas...</option>';

    try {
        const aprendices = await API.getAprendices();
        let optionsHtml = '<option value="">Seleccione una matrícula...</option>';
        
        aprendices.forEach(apr => {
            (apr.matriculas || []).forEach(m => {
                optionsHtml += `<option value="${m.id}">${apr.nombres} ${apr.apellidos} - Ficha ${m.ficha_id} (${m.estado_matricula})</option>`;
            });
        });

        select.innerHTML = optionsHtml;
        modal.classList.remove('hidden');
    } catch (err) {
        alert("Error al cargar aprendices y matrículas: " + err.message);
    }
}

function closeModalContrato() {
    document.getElementById('modalContrato').classList.add('hidden');
}

async function handleCreateContrato(e) {
    e.preventDefault();
    const matriculaId = parseInt(document.getElementById('contratoMatriculaId').value);
    const nombreEmpresa = document.getElementById('contratoEmpresa').value.trim();
    const departamento = document.getElementById('contratoDepartamento').value.trim();
    const ciudad = document.getElementById('contratoCiudad').value.trim();
    const fechaInicio = document.getElementById('contratoFechaInicio').value;
    const fechaFin = document.getElementById('contratoFechaFin').value || null;
    const estado = document.getElementById('contratoEstado').value;
    const observaciones = document.getElementById('contratoObservaciones').value.trim();

    try {
        await API.createContrato({
            matricula_id: matriculaId,
            nombre_empresa: nombreEmpresa,
            departamento: departamento,
            ciudad: ciudad,
            fecha_inicio_contrato: fechaInicio,
            fecha_fin_contrato: fechaFin,
            estado_contrato: estado,
            observaciones: observaciones
        });

        alert("¡Contrato de aprendizaje registrado exitosamente!");
        closeModalContrato();
        loadContratos();
    } catch (err) {
        alert("Error al registrar contrato: " + err.message);
    }
}

async function changeEstadoContrato(contratoId, estadoActual) {
    const nuevoEstado = prompt("Ingrese el nuevo estado (EN PATROCINIO, EN ETAPA PRACTICA, ACTIVO, FINALIZADO, SUSPENDIDO, CANCELADO):", estadoActual);
    if (!nuevoEstado || nuevoEstado.toUpperCase() === estadoActual) return;

    try {
        await API.updateContrato(contratoId, { estado_contrato: nuevoEstado.toUpperCase() });
        alert("Estado del contrato actualizado correctamente.");
        loadContratos();
    } catch (err) {
        alert("Error al actualizar estado del contrato: " + err.message);
    }
}

