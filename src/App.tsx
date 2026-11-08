import { useEffect, useMemo, useState } from 'react'
import {
  AlertTriangle, ArrowRight, Check, CheckCircle2, CircleHelp, FileClock, Menu, Orbit, Plus, Search,
  ShieldCheck, Signal, X,
} from 'lucide-react'
import {
  createInstitutionWorkspace,
  institutions,
  sectionDetails,
  type InstitutionId,
  type NavigationItem,
  type SectionId,
} from './domain/institutions'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const INSTITUTION_CREDENTIALS: Record<InstitutionId, { usuario: string; password: string; motor: string }> = {
  hospital: { usuario: 'medico@hospital.gt', password: 'Test1234!', motor: 'PostgreSQL' },
  pediatrics: { usuario: 'medico@pediatria.gt', password: 'Test1234!', motor: 'MySQL' },
  laboratory: { usuario: 'tecnico@laboratorio.gt', password: 'Test1234!', motor: 'MongoDB' },
  dental: { usuario: 'secretaria@dental.gt', password: 'Test1234!', motor: 'Firebase Firestore' },
}

/* ── Cliente HTTP: un solo punto que traduce los códigos del backend a mensajes ── */

type Notice = { kind: 'ok' | 'error' | 'warn'; text: string }
type ApiResult<T = any> = { ok: true; data: T } | { ok: false; status: number; message: string }

async function apiRequest<T = any>(path: string, token: string | null, init: RequestInit = {}): Promise<ApiResult<T>> {
  const headers: Record<string, string> = { ...(init.body ? { 'Content-Type': 'application/json' } : {}) }
  if (token) headers.Authorization = `Bearer ${token}`
  let res: Response
  try {
    res = await fetch(`${API_URL}${path}`, { ...init, headers: { ...headers, ...(init.headers as Record<string, string>) } })
  } catch {
    return { ok: false, status: 0, message: `No hay comunicación con el servidor (${API_URL}). Verifique que FastAPI esté en ejecución.` }
  }
  let body: any = null
  try { body = await res.json() } catch { /* respuesta sin cuerpo JSON */ }
  if (res.ok) return { ok: true, data: body as T }
  const detail = typeof body?.detail === 'string' ? body.detail : ''
  const message =
    res.status === 404 ? `No encontrado: ${detail || 'el paciente o la consulta indicada no existe.'}` :
    res.status === 503 ? `Servicio no disponible: el motor de base de datos no responde en este momento. Intente de nuevo en unos segundos.${detail ? ` (${detail})` : ''}` :
    res.status === 401 ? 'La sesión expiró. Cambie de institución o recargue la página para volver a autenticarse.' :
    res.status === 422 ? 'Datos inválidos: revise los campos obligatorios del formulario.' :
    detail || `Error inesperado del servidor (HTTP ${res.status}).`
  return { ok: false, status: res.status, message }
}

/* ── Formularios: cada sección se traduce a una operación del contrato IRepository ── */

type Field = {
  name: string; label: string; placeholder?: string
  type?: 'text' | 'date' | 'datetime-local' | 'number' | 'textarea' | 'consulta'
  wide?: boolean; optional?: boolean
}
type Operation = 'paciente' | 'consulta' | 'diagnostico' | 'receta' | 'archivo'
type FormSpec = { op: Operation; fields: Field[]; toConsulta?: (d: Record<string, string>) => { motivo: string; observaciones?: string; fecha?: string } }

const consultaSelect: Field = { name: 'consulta', label: 'Consulta asociada', type: 'consulta', wide: true }

const formSpecs: Partial<Record<SectionId, FormSpec>> = {
  patients: {
    op: 'paciente',
    fields: [
      { name: 'fullName', label: 'Nombre completo', placeholder: 'Nombre y apellidos', wide: true },
      { name: 'document', label: 'Documento de identificación (DPI/CUI)', placeholder: 'Ej. TEST0001' },
      { name: 'birthDate', label: 'Fecha de nacimiento', type: 'date' },
      { name: 'contact', label: 'Teléfono de contacto', placeholder: 'Número de teléfono', optional: true },
    ],
  },
  consultations: {
    op: 'consulta',
    fields: [
      { name: 'motivo', label: 'Motivo de consulta', placeholder: 'Ej. Dolor abdominal de 3 días', wide: true },
      { name: 'observaciones', label: 'Observaciones / notas de consulta', type: 'textarea', placeholder: 'Hallazgos, signos vitales, indicaciones', wide: true, optional: true },
    ],
    toConsulta: (d) => ({ motivo: d.motivo, observaciones: d.observaciones }),
  },
  appointments: {
    op: 'consulta',
    fields: [
      { name: 'date', label: 'Fecha y hora', type: 'datetime-local' },
      { name: 'service', label: 'Servicio', placeholder: 'Servicio o especialidad' },
      { name: 'notes', label: 'Notas de la cita', type: 'textarea', wide: true, optional: true },
    ],
    toConsulta: (d) => ({ motivo: `Cita programada: ${d.service}`, observaciones: d.notes, fecha: d.date }),
  },
  treatments: {
    op: 'consulta',
    fields: [
      { name: 'plan', label: 'Plan de tratamiento', placeholder: 'Descripción del tratamiento', wide: true },
      { name: 'followUp', label: 'Fecha de seguimiento', type: 'date', optional: true },
    ],
    toConsulta: (d) => ({ motivo: `Tratamiento indicado: ${d.plan}`, observaciones: d.followUp ? `Seguimiento: ${d.followUp}` : undefined }),
  },
  procedures: {
    op: 'consulta',
    fields: [
      { name: 'area', label: 'Pieza o área dental', placeholder: 'Ej. Pieza 36' },
      { name: 'procedure', label: 'Procedimiento', placeholder: 'Ej. Resina oclusal' },
      { name: 'notes', label: 'Notas', type: 'textarea', wide: true, optional: true },
    ],
    toConsulta: (d) => ({ motivo: `Procedimiento dental: ${d.procedure} (${d.area})`, observaciones: d.notes }),
  },
  'lab-orders': {
    op: 'consulta',
    fields: [
      { name: 'exam', label: 'Examen solicitado', placeholder: 'Ej. Hematología completa' },
      { name: 'priority', label: 'Prioridad', placeholder: 'Ordinaria / urgente', optional: true },
    ],
    toConsulta: (d) => ({ motivo: d.exam, observaciones: d.priority ? `Prioridad: ${d.priority}` : undefined }),
  },
  growth: {
    op: 'consulta',
    fields: [
      { name: 'weight', label: 'Peso (kg)', type: 'number' },
      { name: 'height', label: 'Talla (cm)', type: 'number' },
      { name: 'head', label: 'Perímetro cefálico (cm)', type: 'number', optional: true },
    ],
    toConsulta: (d) => ({
      motivo: 'Control de crecimiento',
      observaciones: `Peso ${d.weight} kg · Talla ${d.height} cm${d.head ? ` · PC ${d.head} cm` : ''}`,
    }),
  },
  vaccines: {
    op: 'consulta',
    fields: [
      { name: 'vaccine', label: 'Vacuna', placeholder: 'Nombre de la vacuna' },
      { name: 'dose', label: 'Dosis', placeholder: 'Ej. Segunda dosis' },
    ],
    toConsulta: (d) => ({ motivo: `Vacunación: ${d.vaccine}`, observaciones: `Dosis: ${d.dose}` }),
  },
  diagnoses: {
    op: 'diagnostico',
    fields: [
      consultaSelect,
      { name: 'code', label: 'Código CIE-10', placeholder: 'Ej. K29.7', optional: true },
      { name: 'diagnosis', label: 'Diagnóstico clínico', placeholder: 'Descripción clínica', wide: true },
    ],
  },
  prescriptions: {
    op: 'receta',
    fields: [
      consultaSelect,
      { name: 'medicine', label: 'Medicamento', placeholder: 'Nombre genérico' },
      { name: 'dose', label: 'Dosis', placeholder: 'Ej. 500 mg' },
      { name: 'frequency', label: 'Frecuencia', placeholder: 'Ej. Cada 8 horas' },
      { name: 'days', label: 'Duración (días)', type: 'number' },
    ],
  },
  archive: {
    op: 'archivo',
    fields: [
      { name: 'reason', label: 'Motivo de archivado', type: 'textarea', placeholder: 'Justificación de la baja administrativa', wide: true, optional: true },
    ],
  },
}

/** Secciones de solo lectura: muestran el historial del paciente cargado en lugar de un formulario. */
const READ_ONLY_SECTIONS: SectionId[] = ['search', 'histories', 'lab-results']

const patientIdOf = (p: any) => (p ? String(p.id_paciente ?? p.id ?? '') : '')

function App() {
  const [entered, setEntered] = useState(false)
  const [institutionId, setInstitutionId] = useState<InstitutionId>('hospital')
  const [section, setSection] = useState<SectionId>('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [formOpen, setFormOpen] = useState(false)
  const [notice, setNotice] = useState<Notice | null>(null)
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const [token, setToken] = useState<string | null>(null)
  const [searchDpi, setSearchDpi] = useState<string>('')
  const [patientResult, setPatientResult] = useState<any | null>(null)
  const [historyResult, setHistoryResult] = useState<any | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  const workspace = useMemo(() => createInstitutionWorkspace(institutionId), [institutionId])
  const details = sectionDetails[section]
  const currentEngine = INSTITUTION_CREDENTIALS[institutionId].motor
  const spec = formSpecs[section]
  const patientId = patientIdOf(patientResult)
  const isArchived = patientResult?.estado === 'archivado'
  const consultas: any[] = historyResult?.consultas ?? []

  // Autenticar al cargar o cambiar de institución
  useEffect(() => {
    let isMounted = true
    async function login() {
      const creds = INSTITUTION_CREDENTIALS[institutionId]
      const r = await apiRequest<{ access_token: string }>('/auth/login', null, {
        method: 'POST',
        body: JSON.stringify({ usuario: creds.usuario, password: creds.password }),
      })
      if (!isMounted) return
      setToken(r.ok ? r.data.access_token : null)
      setIsConnected(r.ok)
    }
    login()
    return () => { isMounted = false }
  }, [institutionId])

  function changeSection(nextSection: SectionId) {
    setSection(nextSection)
    setFormOpen(false)
    setMobileMenuOpen(false)
    setNotice(null)
  }

  function changeInstitution(nextInstitution: InstitutionId) {
    setInstitutionId(nextInstitution)
    setSection('overview')
    setFormOpen(false)
    setNotice(null)
    setPatientResult(null)
    setHistoryResult(null)
  }

  /** Recarga el historial desde el motor activo; es la fuente de verdad tras cada escritura. */
  async function refreshHistory(pid: string) {
    if (!pid) return
    const r = await apiRequest(`/historial/${encodeURIComponent(pid)}`, token)
    if (r.ok) {
      setHistoryResult(r.data)
      if (r.data?.paciente) setPatientResult(r.data.paciente)
    } else {
      setNotice({ kind: r.status === 503 ? 'warn' : 'error', text: `No se pudo actualizar el historial. ${r.message}` })
    }
  }

  async function handleSearch(event?: React.FormEvent) {
    if (event) event.preventDefault()
    const dpi = searchDpi.trim()
    if (!dpi) return
    setLoading(true)
    setNotice(null)
    const r = await apiRequest(`/pacientes/buscar?dpi=${encodeURIComponent(dpi)}`, token)
    if (r.ok) {
      setPatientResult(r.data)
      setHistoryResult(null)
      if (section === 'overview' || section === 'patients') setSection('search')
      await refreshHistory(patientIdOf(r.data))
    } else {
      setPatientResult(null)
      setHistoryResult(null)
      setNotice({ kind: r.status === 503 ? 'warn' : 'error', text: r.status === 404 ? `No se encontró ningún paciente con el DPI ${dpi} en ${workspace.institution.name}.` : r.message })
    }
    setLoading(false)
  }

  async function handleFormSubmit(data: Record<string, string>) {
    if (!spec) return
    setLoading(true)
    setNotice(null)
    const fail = (r: { status: number; message: string }) =>
      setNotice({ kind: r.status === 503 || r.status === 0 ? 'warn' : 'error', text: r.message })

    try {
      if (spec.op === 'paciente') {
        const r = await apiRequest('/pacientes/', token, {
          method: 'POST',
          body: JSON.stringify({
            nombre: data.fullName,
            dpi: data.document,
            fecha_nacimiento: data.birthDate,
            telefono: data.contact || null,
            tutor_nombre: data.guardian || null,
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: `Paciente '${r.data.nombre}' registrado en ${workspace.institution.name} (${currentEngine}). ID: ${patientIdOf(r.data)}` })
        setFormOpen(false)
        setPatientResult(r.data)
        setSearchDpi(r.data.dpi)
        await refreshHistory(patientIdOf(r.data))
        return
      }

      if (!patientId) {
        setNotice({ kind: 'error', text: 'Primero busque o registre un paciente.' })
        return
      }

      if (spec.op === 'consulta') {
        const c = spec.toConsulta!(data)
        const r = await apiRequest('/consultas/', token, {
          method: 'POST',
          body: JSON.stringify({
            id_paciente: patientId,
            motivo: c.motivo,
            observaciones: c.observaciones || null,
            ...(c.fecha ? { fecha: c.fecha } : {}),
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: `${details.action} guardado en ${currentEngine}. Consulta #${r.data.id_consulta ?? r.data.id}.` })
      } else if (spec.op === 'diagnostico') {
        const r = await apiRequest('/consultas/diagnostico', token, {
          method: 'POST',
          body: JSON.stringify({ id_consulta: data.consulta, descripcion: data.diagnosis, codigo_cie10: data.code || 'Z00.0' }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: `Diagnóstico agregado a la consulta #${data.consulta}.` })
      } else if (spec.op === 'receta') {
        const r = await apiRequest('/consultas/receta', token, {
          method: 'POST',
          body: JSON.stringify({
            id_consulta: data.consulta,
            medicamento: data.medicine,
            dosis: data.dose,
            frecuencia: data.frequency,
            duracion_dias: Number(data.days),
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: `Receta de ${data.medicine} registrada en la consulta #${data.consulta}.` })
      } else if (spec.op === 'archivo') {
        const r = await apiRequest(`/pacientes/${encodeURIComponent(patientId)}/archivar`, token, { method: 'PATCH' })
        if (!r.ok) return fail(r)
        setPatientResult((p: any) => (p ? { ...p, estado: 'archivado' } : p))
        setNotice({ kind: 'ok', text: `Historial de ${patientResult.nombre} archivado (baja administrativa).` })
      }

      setFormOpen(false)
      await refreshHistory(patientId)
    } finally {
      setLoading(false)
    }
  }

  if (!entered) {
    return <Manifest onEnter={() => setEntered(true)} />
  }

  const needsConsulta = spec?.op === 'diagnostico' || spec?.op === 'receta'

  return (
    <div className="workbench-shell">
      <header className="terminal-masthead">
        <div className="masthead-main">
          <div className="masthead-id">
            <Orbit size={20} strokeWidth={1.8} />
            <div>
              <span className="masthead-code">SISTEMA PÚBLICO UNIVERSAL · SP—03</span>
              <p>Plataforma de Historiales Clínicos · Persistencia Políglota</p>
            </div>
          </div>
          <div className="masthead-status">
            <span className="system-pill">URL · BASES DE DATOS II</span>
            <span className="system-pill">ENTREGA II · NOVIEMBRE 2026</span>
            <span className={`system-pill ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
              <Signal size={12} /> {isConnected ? `CONECTADO · ${currentEngine}` : 'SIN SERVIDOR'}
            </span>
          </div>
        </div>
        <button className="mobile-toggle" onClick={() => setMobileMenuOpen((open) => !open)} aria-expanded={mobileMenuOpen} aria-label="Menú de navegación">
          <Menu size={18} />
        </button>
      </header>

      <main className="workbench-body">
        <aside className={`workbench-nav ${mobileMenuOpen ? 'nav-open' : ''}`} aria-label="Navegación del sistema clínico">
          <div className="nav-workspace-header">
            <p className="kicker">INSTITUCIÓN EN LÍNEA</p>
            <h2>{workspace.institution.name}</h2>
            <span className="institution-badge"><ShieldCheck size={13} /> {currentEngine}</span>
          </div>

          <NavGroup label="Operaciones Generales" items={workspace.commonItems} active={section} onSelect={changeSection} />

          {workspace.specialtyItems.length > 0 && (
            <NavGroup label="Módulos Propios" items={workspace.specialtyItems} active={section} onSelect={changeSection} />
          )}

          <div className="nav-system-box">
            <div className="system-box-title">
              <CircleHelp size={14} />
              <span>ARQUITECTURA HEXAGONAL</span>
            </div>
            <p>El puerto IRepository desacopla las operaciones clínicas del motor físico.</p>
          </div>
        </aside>

        <section className="workbench-workspace" aria-labelledby="page-title">
          <div className="workspace-titlebar">
            <div>
              <p className="kicker">OPERACIONES CLÍNICAS · {workspace.institution.shortName.toUpperCase()}</p>
              <h1 id="page-title">{details.title}</h1>
              <p className="institution-description">{workspace.institution.description}</p>
            </div>
            <span className="institution-select-label">CAMBIAR INSTITUCIÓN</span>
          </div>

          <InstitutionTabs active={institutionId} onSelect={changeInstitution} />

          <p className="prototype-notice">
            {isConnected ? (
              <span className="connected"><Signal size={15} /> Servidor FastAPI en línea. Motor activo: <strong>{currentEngine}</strong>. Persistencia asegurada.</span>
            ) : (
              <span><Signal size={15} /> Intentando conectar con {API_URL}... Asegúrese de que el backend esté ejecutándose.</span>
            )}
          </p>

          <form className="patient-search" onSubmit={handleSearch}>
            <label className="search-input-wrap">
              <Search size={19} aria-hidden="true" />
              <span className="sr-only">Buscar por DPI</span>
              <input
                value={searchDpi}
                onChange={(e) => setSearchDpi(e.target.value)}
                placeholder="Buscar paciente por DPI (ej. TESTHOSP0001)..."
                aria-label="Búsqueda de pacientes por DPI"
              />
            </label>
            <button type="submit" className="search-submit" disabled={loading}>
              {loading ? 'Procesando...' : 'Buscar'} <ArrowRight size={16} />
            </button>
          </form>

          {notice && (
            <div className={`system-notice notice-${notice.kind}`} role={notice.kind === 'ok' ? 'status' : 'alert'}>
              {notice.kind === 'ok' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
              <p>{notice.text}</p>
              <button onClick={() => setNotice(null)} aria-label="Cerrar aviso"><X size={16} /></button>
            </div>
          )}

          {patientResult && <PatientCard patient={patientResult} history={historyResult} />}

          {section === 'overview' ? (
            <EmptyOverview onAction={() => { changeSection('patients'); setFormOpen(true) }} />
          ) : READ_ONLY_SECTIONS.includes(section) || !spec ? (
            !patientResult && <EmptyState icon={section === 'lab-results' ? 'lab' : 'search'} title={details.emptyTitle} description={details.description} />
          ) : (
            <section className="operation-area" aria-label={details.title}>
              {spec.op !== 'paciente' && !patientResult ? (
                <EmptyState icon="search" title="Seleccione un paciente" description={`Busque al paciente por DPI en la barra superior para ${details.action.toLowerCase()} en ${workspace.institution.name}.`} />
              ) : spec.op !== 'paciente' && isArchived ? (
                <EmptyState icon="archive" title="Historial archivado" description="Este paciente tiene baja administrativa; no se admiten nuevos registros clínicos." />
              ) : needsConsulta && consultas.length === 0 ? (
                <div>
                  <EmptyState icon="history" title="El paciente aún no tiene consultas" description={`Para ${details.action.toLowerCase()} primero registre una consulta.`} />
                  <button className="primary-action" onClick={() => changeSection('consultations')}>
                    <Plus size={16} /> Registrar consulta
                  </button>
                </div>
              ) : !formOpen ? (
                <div>
                  <EmptyState icon={section === 'archive' ? 'archive' : 'history'} title={details.emptyTitle} description={details.description} />
                  <button className="primary-action" onClick={() => { setFormOpen(true); setNotice(null) }} disabled={!isConnected}>
                    <Plus size={16} /> {details.action}
                  </button>
                </div>
              ) : (
                <OperationForm
                  key={section}
                  section={section}
                  fields={spec.fields}
                  institutionId={institutionId}
                  patient={spec.op === 'paciente' ? null : patientResult}
                  consultas={consultas}
                  loading={loading}
                  onCancel={() => setFormOpen(false)}
                  onSubmit={handleFormSubmit}
                />
              )}
            </section>
          )}

          <footer className="work-footer">
            <span>PLATAFORMA INTEGRADA · PERSISTENCIA POLÍGLOTA</span>
            <span className="footer-institutions">Hospital (PG) · Odontología (Firebase) · Laboratorio (Mongo) · Pediatría (MySQL)</span>
            <span className="footer-signal" aria-hidden="true"><i /></span>
          </footer>
        </section>
      </main>
    </div>
  )
}

function PatientCard({ patient, history }: { patient: any; history: any | null }) {
  const extra: { key: string; label: string }[] = [
    { key: 'examenes_laboratorio', label: 'Exámenes de laboratorio' },
    { key: 'procedimientos_dentales', label: 'Procedimientos dentales' },
    { key: 'controles_crecimiento', label: 'Controles de crecimiento' },
    { key: 'vacunas', label: 'Vacunas' },
  ]
  return (
    <div className="patient-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>{patient.nombre}</h3>
        <span className={`badge ${patient.estado === 'archivado' ? 'badge-archived' : 'badge-active'}`}>{patient.estado}</span>
      </div>
      <p><strong>ID:</strong> {patientIdOf(patient)} | <strong>DPI:</strong> {patient.dpi}</p>
      <p><strong>Fecha de Nacimiento:</strong> {patient.fecha_nacimiento} | <strong>Teléfono:</strong> {patient.telefono || 'No registrado'}</p>
      {patient.tutor_nombre && <p><strong>Tutor:</strong> {patient.tutor_nombre}{patient.tutor_telefono ? ` (${patient.tutor_telefono})` : ''}</p>}

      {history && (
        <div style={{ marginTop: 15, borderTop: '1px solid var(--line)', paddingTop: 10 }}>
          <h4 style={{ margin: '10px 0 5px' }}>Historial de Consultas ({history.consultas?.length || 0})</h4>
          <div className="history-timeline">
            {history.consultas?.map((c: any, idx: number) => (
              <div key={idx} className="history-entry">
                <h4>Consulta #{c.id_consulta || c.id} — {c.profesional || 'Médico'}</h4>
                <p><strong>Motivo:</strong> {c.motivo}</p>
                {c.observaciones && <p><strong>Observaciones:</strong> {c.observaciones}</p>}
                <p style={{ fontSize: 11, color: 'var(--muted)' }}>Fecha: {String(c.fecha ?? '')}</p>
              </div>
            ))}
            {!history.consultas?.length && <p style={{ fontSize: 12, color: 'var(--muted)' }}>No hay consultas registradas para este paciente.</p>}
          </div>

          <h4 style={{ margin: '15px 0 5px' }}>Diagnósticos Registrados ({history.diagnosticos?.length || 0})</h4>
          <div className="history-timeline">
            {history.diagnosticos?.map((d: any, idx: number) => (
              <div key={idx} className="history-entry" style={{ borderLeftColor: '#0056b3' }}>
                <h4>{d.codigo_cie10 ? `[${d.codigo_cie10}] ` : ''}{d.descripcion}</h4>
                <p style={{ fontSize: 11, color: 'var(--muted)' }}>Asociado a Consulta #{d.id_consulta}</p>
              </div>
            ))}
          </div>

          <h4 style={{ margin: '15px 0 5px' }}>Recetas y Medicamentos ({history.recetas?.length || 0})</h4>
          <div className="history-timeline">
            {history.recetas?.map((r: any, idx: number) => (
              <div key={idx} className="history-entry" style={{ borderLeftColor: '#28a745' }}>
                <h4>💊 {r.medicamento}</h4>
                <p>Dosis: {r.dosis} | Frecuencia: {r.frecuencia} | Duración: {r.duracion_dias} días</p>
              </div>
            ))}
          </div>

          {extra.filter(({ key }) => history[key]?.length).map(({ key, label }) => (
            <div key={key}>
              <h4 style={{ margin: '15px 0 5px' }}>{label} ({history[key].length})</h4>
              <div className="history-timeline">
                {history[key].map((item: any, idx: number) => (
                  <div key={idx} className="history-entry" style={{ borderLeftColor: '#a26600' }}>
                    <h4>{item.nombre_examen || item.procedimiento || item.nombre || item.vacuna || `Registro ${idx + 1}`}</h4>
                    {Array.isArray(item.resultados_parametros) && item.resultados_parametros.map((p: any, i: number) => (
                      <p key={i}>{p.parametro}: <strong>{p.valor}</strong> <span style={{ color: 'var(--muted)' }}>({p.rango_referencia})</span></p>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function Manifest({ onEnter }: { onEnter: () => void }) {
  return (
    <main className="manifest-page">
      <div className="manifest-layout">
        <section className="manifest-copy">
          <p className="manifest-kicker"><span /> DECLARACIÓN PÚBLICA</p>
          <h1>LA SALUD<br /><em>ES UN</em><br />DERECHO.</h1>
          <p className="manifest-lede">La salud pública universal pertenece a todas las personas. Una atención continua necesita historias clínicas que acompañen a cada paciente y a cada comunidad.</p>
          <button className="manifest-cta" onClick={onEnter}>Entrar al sistema <ArrowRight size={18} /></button>
          <div className="manifest-principles"><span><Check size={14} /> Atención continua</span><span><Check size={14} /> Historial clínico</span><span><Check size={14} /> Cuatro instituciones</span></div>
        </section>
        <figure className="manifest-artwork">
          <img src="/images/salud-comunitaria.png" alt="Ilustración editorial de personal de salud y comunidad frente a una clínica pública" />
          <figcaption><span>ATENCIÓN COMO DERECHO</span><span>GRÁFICA PÚBLICA · SPU</span></figcaption>
          <div className="artwork-stamp" aria-hidden="true"><ShieldCheck size={20} /><span>PARA<br />TODAS<br />Y TODOS</span></div>
        </figure>
      </div>
    </main>
  )
}

function NavGroup({ label, items, active, onSelect }: { label: string; items: NavigationItem[]; active: SectionId; onSelect: (id: SectionId) => void }) {
  return (
    <div className="nav-group">
      <p>{label}</p>
      {items.map(({ id, label: itemLabel, icon: Icon }) => (
        <button key={id} className={`nav-item ${active === id ? 'nav-item-active' : ''}`} onClick={() => onSelect(id)} aria-current={active === id ? 'page' : undefined}>
          <Icon size={17} strokeWidth={1.7} />
          <span>{itemLabel}</span>
          {active === id && <span className="nav-indicator" />}
        </button>
      ))}
    </div>
  )
}

function InstitutionTabs({ active, onSelect }: { active: InstitutionId; onSelect: (id: InstitutionId) => void }) {
  return (
    <div className="institution-tabs" aria-label="Cambiar institución">
      {Object.values(institutions).map((institution) => (
        <button key={institution.id} type="button" aria-pressed={active === institution.id} className={active === institution.id ? 'tab-active' : ''} onClick={() => onSelect(institution.id)}>
          {institution.shortName}
        </button>
      ))}
    </div>
  )
}

function EmptyOverview({ onAction }: { onAction: () => void }) {
  return (
    <section className="overview-empty" aria-labelledby="empty-title">
      <div className="coordinate-label coordinate-top">REGISTRO DE OPERACIONES <span>SPU—0001</span></div>
      <div className="empty-orbit" aria-hidden="true">
        <div className="orbit-ring orbit-ring-one" />
        <div className="orbit-ring orbit-ring-two" />
        <div className="orbit-cross"><span /><i /></div>
        <div className="orbit-core"><Search size={26} strokeWidth={1.4} /></div>
        <b className="orbit-dot" />
      </div>
      <h2 id="empty-title">Índice de Operaciones Clínicas</h2>
      <p>Seleccione una operación en el menú lateral o registre un nuevo paciente para comenzar.</p>
      <button className="empty-action" onClick={onAction}>Iniciar registro de paciente <ArrowRight size={15} /></button>
      <div className="coordinate-label coordinate-bottom"><span>HISTORIAL CLÍNICO</span><span>ACTIVO</span></div>
    </section>
  )
}

function EmptyState({ icon, title, description }: { icon: 'search' | 'history' | 'archive' | 'lab'; title: string; description: string }) {
  const Icon = icon === 'search' ? Search : icon === 'archive' ? ShieldCheck : icon === 'lab' ? Signal : FileClock
  return (
    <div className="empty-state">
      <div className="empty-state-icon"><Icon size={23} strokeWidth={1.6} /></div>
      <div><h2>{title}</h2><p>{description}</p></div>
    </div>
  )
}

function OperationForm({
  section,
  fields,
  institutionId,
  patient,
  consultas,
  loading,
  onCancel,
  onSubmit,
}: {
  section: SectionId
  fields: Field[]
  institutionId: InstitutionId
  patient: any | null
  consultas: any[]
  loading: boolean
  onCancel: () => void
  onSubmit: (data: Record<string, string>) => void
}) {
  const consultaId = (c: any) => String(c.id_consulta ?? c.id)
  const lastConsulta = consultas.length ? consultaId(consultas[consultas.length - 1]) : ''
  const [formData, setFormData] = useState<Record<string, string>>(() => ({ consulta: lastConsulta }))
  const motor = INSTITUTION_CREDENTIALS[institutionId].motor
  const visibleFields: Field[] = section === 'patients' && institutionId === 'pediatrics'
    ? [...fields, { name: 'guardian', label: 'Madre, padre o persona tutora', placeholder: 'Nombre de responsable', wide: true }]
    : fields

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    if (section === 'archive' && !window.confirm(`¿Archivar el historial de ${patient?.nombre}? Esta acción es una baja administrativa.`)) return
    onSubmit(formData)
  }

  return (
    <form className="operation-form" onSubmit={handleSubmit}>
      <div className="form-heading">
        <div>
          <span>CAPTURA DE OPERACIÓN</span>
          <h3>{sectionDetails[section].action}</h3>
        </div>
        <span className="connected"><Signal size={13} /> EN LÍNEA · {motor}</span>
      </div>
      <p className="privacy-note">
        {patient
          ? <><strong>Paciente:</strong> {patient.nombre} (ID {patientIdOf(patient)}) · Se guardará en {motor}.</>
          : <><strong>Persistencia activa:</strong> Los datos se enviarán directamente al motor de la institución activa ({motor}).</>}
      </p>
      <div className="form-grid">
        {visibleFields.map((field) => (
          <label key={field.name} className={field.wide ? 'field-wide' : ''}>
            {field.label}{field.optional ? ' (opcional)' : ''}
            {field.type === 'consulta' ? (
              <select name={field.name} value={formData[field.name] || ''} onChange={handleChange} required>
                {consultas.map((c) => (
                  <option key={consultaId(c)} value={consultaId(c)}>#{consultaId(c)} — {c.motivo}</option>
                ))}
              </select>
            ) : field.type === 'textarea' ? (
              <textarea name={field.name} placeholder={field.placeholder} value={formData[field.name] || ''} onChange={handleChange} required={!field.optional} rows={3} />
            ) : (
              <input
                name={field.name}
                type={field.type ?? 'text'}
                placeholder={field.placeholder}
                value={formData[field.name] || ''}
                onChange={handleChange}
                required={!field.optional}
                {...(field.type === 'number' ? { min: 0, step: 'any' } : {})}
              />
            )}
          </label>
        ))}
      </div>
      <div className="form-actions">
        <button type="button" className="secondary-action" onClick={onCancel}>Cancelar</button>
        <button type="submit" className="primary-action" disabled={loading}>
          <Check size={15} /> {loading ? 'Guardando...' : section === 'archive' ? 'Confirmar archivado' : `Guardar en ${motor}`}
        </button>
      </div>
    </form>
  )
}

export default App
