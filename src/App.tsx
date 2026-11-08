import { useMemo, useState } from 'react'
import {
  AlertTriangle, ArrowRight, Check, CheckCircle2, FileClock, Menu, Plus, Search,
  ShieldCheck, Signal, Star, X,
} from 'lucide-react'
import {
  createInstitutionWorkspace,
  sectionDetails,
  type InstitutionId,
  type NavigationItem,
  type SectionId,
} from './domain/institutions'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const ENGINES: Record<InstitutionId, string> = {
  hospital: 'PostgreSQL', pediatrics: 'MySQL',
  laboratory: 'MongoDB', dental: 'Firebase Firestore',
}
const API_INSTITUTIONS: Record<string, InstitutionId> = {
  hospital: 'hospital', pediatria: 'pediatrics',
  laboratorio: 'laboratory', odontologia: 'dental',
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
    res.status === 401 ? 'La sesión expiró. Vuelva a iniciar sesión.' :
    res.status === 409 ? detail || 'La operación no se puede realizar en el estado actual del expediente.' :
    res.status === 422 ? 'Datos inválidos: revise los campos obligatorios del formulario.' :
    detail || `Error inesperado del servidor (HTTP ${res.status}).`
  return { ok: false, status: res.status, message }
}

/* ── Formularios: cada sección se traduce a una operación del contrato IRepository ── */

type Field = {
  name: string; label: string; placeholder?: string
  type?: 'text' | 'tel' | 'date' | 'datetime-local' | 'number' | 'textarea' | 'consulta' | 'select'
  options?: string[]; maxLength?: number; min?: string; max?: string; pattern?: string; inputMode?: 'numeric' | 'decimal' | 'tel'
  wide?: boolean; optional?: boolean
}
type Operation = 'paciente' | 'cita' | 'consulta' | 'diagnostico' | 'receta' | 'tratamiento' | 'procedimiento' | 'resultados' | 'crecimiento' | 'vacuna' | 'archivo'
type FormSpec = { op: Operation; fields: Field[]; toConsulta?: (d: Record<string, string>) => { motivo: string; observaciones?: string; fecha?: string } }

const consultaSelect: Field = { name: 'consulta', label: 'Consulta asociada', type: 'consulta', wide: true }

const formSpecs: Partial<Record<SectionId, FormSpec>> = {
  patients: {
    op: 'paciente',
    fields: [
      { name: 'fullName', label: 'Nombre completo', placeholder: 'Nombre y apellidos', wide: true },
      { name: 'document', label: 'CUI (13 dígitos)', placeholder: 'Ej. 2320556340103', maxLength: 17, pattern: '[0-9 .-]{13,17}', inputMode: 'numeric' },
      { name: 'birthDate', label: 'Fecha de nacimiento', type: 'date', max: new Date().toISOString().slice(0, 10) },
      { name: 'contact', label: 'Teléfono de contacto', type: 'tel', placeholder: '1234 5678 o +502 1234 5678', optional: true, maxLength: 20, inputMode: 'tel' },
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
    op: 'cita',
    fields: [
      { name: 'date', label: 'Fecha y hora', type: 'datetime-local' },
      { name: 'service', label: 'Servicio', placeholder: 'Servicio o especialidad' },
      { name: 'notes', label: 'Notas de la cita', type: 'textarea', wide: true, optional: true },
    ],
  },
  treatments: {
    op: 'tratamiento',
    fields: [
      consultaSelect,
      { name: 'plan', label: 'Plan de tratamiento', placeholder: 'Descripción del tratamiento', wide: true },
      { name: 'indications', label: 'Indicaciones', type: 'textarea', wide: true, optional: true },
      { name: 'followUp', label: 'Fecha de seguimiento', type: 'date', optional: true },
    ],
  },
  procedures: {
    op: 'procedimiento',
    fields: [
      consultaSelect,
      { name: 'area', label: 'Pieza o área dental', placeholder: 'Ej. Pieza 36' },
      { name: 'procedure', label: 'Procedimiento', placeholder: 'Ej. Resina oclusal' },
      { name: 'notes', label: 'Notas', type: 'textarea', wide: true, optional: true },
    ],
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
    op: 'crecimiento',
    fields: [
      { name: 'weight', label: 'Peso (kg)', type: 'number' },
      { name: 'height', label: 'Talla (cm)', type: 'number' },
      { name: 'head', label: 'Perímetro cefálico (cm)', type: 'number', optional: true },
    ],
  },
  vaccines: {
    op: 'vacuna',
    fields: [
      { name: 'vaccine', label: 'Vacuna', placeholder: 'Nombre de la vacuna' },
      { name: 'dose', label: 'Dosis', placeholder: 'Ej. Segunda dosis' },
      { name: 'lot', label: 'Lote', placeholder: 'Lote del vial', optional: true },
    ],
  },
  'lab-results': {
    op: 'resultados',
    fields: [
      consultaSelect,
      { name: 'parameter', label: 'Parámetro medido', placeholder: 'Ej. Hemoglobina' },
      { name: 'value', label: 'Valor', placeholder: 'Ej. 13.5' },
      { name: 'unit', label: 'Unidad', placeholder: 'Ej. g/dL', optional: true },
      { name: 'range', label: 'Rango de referencia', placeholder: 'Ej. 12–16', optional: true },
    ],
  },
  diagnoses: {
    op: 'diagnostico',
    fields: [
      consultaSelect,
      { name: 'code', label: 'Código CIE-10', placeholder: 'Ej. K29.7' },
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
    fields: [],
  },
}

/** Secciones de solo lectura: muestran el historial del paciente cargado en lugar de un formulario. */
const READ_ONLY_SECTIONS: SectionId[] = ['search', 'histories']

const patientIdOf = (p: any) => (p ? String(p.id_paciente ?? p.id ?? '') : '')
const normalizeCui = (value: string) => value.replace(/[ .-]/g, '')
const isValidCuiFormat = (value: string) => /^\d{13}$/.test(normalizeCui(value))
const normalizeLocalPhone = (value: string) => {
  const raw = value.trim()
  const digits = raw.replace(/\D/g, '')
  const national = (raw.startsWith('+') && digits.startsWith('502') && digits.length === 11) || (digits.startsWith('502') && digits.length === 11)
    ? digits.slice(3)
    : digits
  return national.length === 8 ? national : null
}

function App() {
  const [entered, setEntered] = useState(false)
  const [portalLeaving, setPortalLeaving] = useState(false)
  const [institutionId, setInstitutionId] = useState<InstitutionId>('hospital')
  const [section, setSection] = useState<SectionId>('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [formOpen, setFormOpen] = useState(false)
  const [notice, setNotice] = useState<Notice | null>(null)
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const [token, setToken] = useState<string | null>(null)
  const [loginError, setLoginError] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)
  const [signedInUser, setSignedInUser] = useState('')
  const [signedInRole, setSignedInRole] = useState('')
  const [searchDpi, setSearchDpi] = useState<string>('')
  const [notFoundCui, setNotFoundCui] = useState('')
  const [patientResult, setPatientResult] = useState<any | null>(null)
  const [historyResult, setHistoryResult] = useState<any | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  const workspace = useMemo(() => createInstitutionWorkspace(institutionId, signedInRole), [institutionId, signedInRole])
  const details = sectionDetails[section]
  const currentEngine = ENGINES[institutionId]
  const spec = formSpecs[section]
  const patientId = patientIdOf(patientResult)
  const isArchived = patientResult?.estado === 'archivado'
  const consultas: any[] = historyResult?.consultas ?? []

  function enterSystem() {
    if (portalLeaving) return
    setPortalLeaving(true)
    const delay = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 220
    window.setTimeout(() => setEntered(true), delay)
  }

  async function loginUser(usuario: string, password: string) {
    setLoginLoading(true)
    setLoginError('')
    const r = await apiRequest<{ access_token: string; institution: string; usuario: string; rol: string }>('/auth/login', null, {
      method: 'POST', body: JSON.stringify({ usuario, password }),
    })
    setLoginLoading(false)
    if (!r.ok) {
      setLoginError(r.message)
      return
    }
    const inst = API_INSTITUTIONS[r.data.institution]
    if (!inst) {
      setLoginError('La institución de esta cuenta no está disponible.')
      return
    }
    setInstitutionId(inst)
    setSignedInUser(r.data.usuario)
    setSignedInRole(r.data.rol)
    setToken(r.data.access_token)
    setIsConnected(true)
  }

  function changeSection(nextSection: SectionId) {
    setSection(nextSection)
    setFormOpen(false)
    setMobileMenuOpen(false)
    setNotice(null)
  }

  function logout() {
    setToken(null)
    setSignedInUser('')
    setSignedInRole('')
    setIsConnected(false)
    setSection('overview')
    setFormOpen(false)
    setNotice(null)
    setPatientResult(null)
    setHistoryResult(null)
    setSearchDpi('')
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
    const dpi = normalizeCui(searchDpi)
    if (!isValidCuiFormat(searchDpi)) {
      setNotice({ kind: 'error', text: 'Escriba los 13 dígitos del CUI. Puede incluir espacios o guiones.' })
      return
    }
    setLoading(true)
    setNotice(null)
    setNotFoundCui('')
    try {
      const r = await apiRequest(`/pacientes/buscar?dpi=${encodeURIComponent(dpi)}`, token)
      if (r.ok) {
        setPatientResult(r.data)
        setHistoryResult(null)
        if (section === 'overview' || section === 'patients') setSection('search')
        await refreshHistory(patientIdOf(r.data))
      } else {
        setPatientResult(null)
        setHistoryResult(null)
        if (r.status === 404) setNotFoundCui(dpi)
        setNotice({ kind: r.status === 503 ? 'warn' : 'error', text: r.status === 404 ? `No se encontró un paciente con ese CUI en ${workspace.institution.name}. Puede registrarlo desde “Pacientes”; el CUI quedará listo para copiar.` : r.message })
      }
    } finally { setLoading(false) }
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
            dpi: normalizeCui(data.document),
            fecha_nacimiento: data.birthDate,
            telefono: data.contact ? normalizeLocalPhone(data.contact) : null,
            tutor_nombre: data.guardian || null,
            tutor_telefono: data.guardianPhone ? normalizeLocalPhone(data.guardianPhone) : null,
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

      if (spec.op === 'cita') {
        const r = await apiRequest('/citas/', token, {
          method: 'POST',
          body: JSON.stringify({
            id_paciente: patientId, fecha: data.date,
            servicio: data.service, notas: data.notes || null,
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: `Cita #${r.data.id_cita} programada.` })
      } else if (spec.op === 'consulta') {
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
          body: JSON.stringify({ id_consulta: data.consulta, descripcion: data.diagnosis, codigo_cie10: data.code.trim() }),
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
      } else if (spec.op === 'tratamiento') {
        const r = await apiRequest('/consultas/tratamiento', token, {
          method: 'POST',
          body: JSON.stringify({
            id_consulta: data.consulta, descripcion: data.plan,
            indicaciones: data.indications || null, fecha_fin: data.followUp || null,
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: 'Tratamiento vinculado al diagnóstico y guardado.' })
      } else if (spec.op === 'procedimiento') {
        const r = await apiRequest('/especialidades/odontologia/procedimientos', token, {
          method: 'POST',
          body: JSON.stringify({
            id_consulta: data.consulta, pieza: data.area,
            procedimiento: data.procedure, notas: data.notes || null,
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: 'Procedimiento dental guardado en la atención.' })
      } else if (spec.op === 'resultados') {
        const r = await apiRequest('/especialidades/laboratorio/resultados', token, {
          method: 'POST',
          body: JSON.stringify({
            id_consulta: data.consulta,
            resultados_parametros: [{
              parametro: data.parameter, valor: data.value,
              unidad: data.unit || null, rango_referencia: data.range || null,
            }],
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: 'Resultado de laboratorio guardado.' })
      } else if (spec.op === 'crecimiento') {
        const r = await apiRequest('/especialidades/pediatria/crecimiento', token, {
          method: 'POST',
          body: JSON.stringify({
            id_paciente: patientId, peso_kg: Number(data.weight),
            talla_cm: Number(data.height),
            perimetro_cefalico_cm: data.head ? Number(data.head) : null,
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: 'Control de crecimiento guardado.' })
      } else if (spec.op === 'vacuna') {
        const r = await apiRequest('/especialidades/pediatria/vacunas', token, {
          method: 'POST',
          body: JSON.stringify({
            id_paciente: patientId, nombre_vacuna: data.vaccine,
            dosis: data.dose, lote: data.lot || null,
          }),
        })
        if (!r.ok) return fail(r)
        setNotice({ kind: 'ok', text: 'Vacuna aplicada y guardada en el historial.' })
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

  async function updateAppointment(id: string, change: { fecha?: string; estado?: string }) {
    setLoading(true)
    const r = await apiRequest(`/citas/${encodeURIComponent(id)}`, token, {
      method: 'PATCH', body: JSON.stringify(change),
    })
    if (r.ok) {
      setNotice({ kind: 'ok', text: change.estado === 'cancelada' ? 'Cita cancelada.' : 'Cita reprogramada.' })
      await refreshHistory(patientId)
    } else {
      setNotice({ kind: 'error', text: r.message })
    }
    setLoading(false)
  }

  if (!entered) {
    return <Manifest onEnter={enterSystem} isLeaving={portalLeaving} />
  }
  if (!token) {
    return <LoginScreen onLogin={loginUser} loading={loginLoading} error={loginError} />
  }

  const needsConsulta = ['diagnostico', 'receta', 'tratamiento', 'procedimiento', 'resultados'].includes(spec?.op || '')

  return (
    <div className="workbench-shell">
      <header className="terminal-masthead">
        <div className="masthead-main">
          <div className="masthead-id">
            <Star size={17} strokeWidth={1.8} fill="currentColor" />
            <p>Historial clínico</p>
          </div>
          <div className="masthead-status">
            <span className={`system-pill ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
              <Signal size={12} /> {isConnected ? 'Sesión activa' : 'Sin conexión'}
            </span>
            <span className="session-user">{signedInUser}</span>
            <button type="button" className="session-logout" onClick={logout}>Cerrar sesión</button>
          </div>
        </div>
        <button className="mobile-toggle" onClick={() => setMobileMenuOpen((open) => !open)} aria-expanded={mobileMenuOpen} aria-label="Menú de navegación">
          <Menu size={18} />
        </button>
      </header>

      <main className="workbench-body">
        <aside className={`workbench-nav ${mobileMenuOpen ? 'nav-open' : ''}`} aria-label="Navegación del sistema clínico">
          <NavGroup label="Operaciones" items={workspace.commonItems} active={section} onSelect={changeSection} />

          {workspace.specialtyItems.length > 0 && (
            <NavGroup label="Módulos Propios" items={workspace.specialtyItems} active={section} onSelect={changeSection} />
          )}

        </aside>

        <section className="workbench-workspace" aria-labelledby="page-title">
          <div className="workspace-titlebar">
            <h1 id="page-title">{details.title}</h1>
          </div>

          <div className="active-institution" aria-label="Institución de la sesión">{workspace.institution.name} · {currentEngine}</div>

          <form className="patient-search" onSubmit={handleSearch}>
            <label className="search-input-wrap">
              <Search size={19} aria-hidden="true" />
              <span className="sr-only">Buscar por CUI (13 dígitos)</span>
              <input
                value={searchDpi}
                onChange={(e) => setSearchDpi(e.target.value)}
                placeholder="Buscar paciente por CUI (13 dígitos)"
                aria-label="Búsqueda de pacientes por CUI, 13 dígitos"
                inputMode="numeric"
                autoComplete="off"
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
              {notFoundCui && <button className="notice-action" onClick={() => { setSearchDpi(notFoundCui); changeSection('patients'); setFormOpen(true); setNotice(null) }}>Registrar paciente</button>}
              <button onClick={() => setNotice(null)} aria-label="Cerrar aviso"><X size={16} /></button>
            </div>
          )}

          {patientResult && <PatientCard patient={patientResult} history={historyResult} showClinical={signedInRole !== 'secretaria'} />}
          {section === 'appointments' && historyResult?.citas?.length > 0 && (
            <AppointmentList citas={historyResult.citas} loading={loading} onUpdate={updateAppointment} />
          )}

          {section === 'overview' ? (
            <EmptyOverview onAction={() => { changeSection('patients'); setFormOpen(true) }} />
          ) : READ_ONLY_SECTIONS.includes(section) || !spec ? (
            !patientResult && <EmptyState icon={section === 'lab-results' ? 'lab' : 'search'} title={details.emptyTitle} description={details.description} />
          ) : (
            <section className="operation-area" aria-label={details.title}>
              {spec.op !== 'paciente' && !patientResult ? (
                <EmptyState icon="search" title="Seleccione un paciente" description={`Busque al paciente por CUI en la barra superior para ${details.action.toLowerCase()} en ${workspace.institution.name}.`} />
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
                  initialCui={spec.op === 'paciente' ? searchDpi : ''}
                  consultas={consultas}
                  loading={loading}
                  onCancel={() => setFormOpen(false)}
                  onSubmit={handleFormSubmit}
                />
              )}
            </section>
          )}

        </section>
      </main>
    </div>
  )
}

function PatientCard({ patient, history, showClinical }: { patient: any; history: any | null; showClinical: boolean }) {
  const extra: { key: string; label: string }[] = [
    { key: 'tratamientos', label: 'Tratamientos' },
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
      <p><strong>ID:</strong> {patientIdOf(patient)} | <strong>CUI:</strong> {patient.dpi}</p>
      <p><strong>Fecha de Nacimiento:</strong> {patient.fecha_nacimiento} | <strong>Teléfono:</strong> {patient.telefono || 'No registrado'}</p>
      {patient.tutor_nombre && <p><strong>Tutor:</strong> {patient.tutor_nombre}{patient.tutor_telefono ? ` (${patient.tutor_telefono})` : ''}</p>}

      {history && (showClinical || history.citas?.length > 0) && (
        <div style={{ marginTop: 15, borderTop: '1px solid var(--line)', paddingTop: 10 }}>
          {history.citas?.length > 0 && <>
            <h4>Citas ({history.citas.length})</h4>
            <div className="history-timeline">
              {history.citas.map((c: any) => (
                <div className="history-entry" key={c.id_cita}>
                  <h4>{c.servicio} · {c.estado}</h4>
                  <p>{String(c.fecha || '')}</p>
                </div>
              ))}
            </div>
          </>}
          {showClinical && <>
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
              <div key={idx} className="history-entry">
                <h4>{d.codigo_cie10 ? `[${d.codigo_cie10}] ` : ''}{d.descripcion}</h4>
                <p style={{ fontSize: 11, color: 'var(--muted)' }}>Asociado a Consulta #{d.id_consulta}</p>
              </div>
            ))}
          </div>

          <h4 style={{ margin: '15px 0 5px' }}>Recetas y Medicamentos ({history.recetas?.length || 0})</h4>
          <div className="history-timeline">
            {history.recetas?.map((r: any, idx: number) => (
              <div key={idx} className="history-entry">
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
                  <div key={idx} className="history-entry">
                    <h4>{item.nombre_examen || item.procedimiento || item.descripcion || item.nombre_vacuna || item.nombre || item.vacuna || `Registro ${idx + 1}`}</h4>
                    {item.estado && <p>Estado: {item.estado}</p>}
                    {item.pieza && <p>Pieza o área: {item.pieza}</p>}
                    {item.indicaciones && <p>Indicaciones: {item.indicaciones}</p>}
                    {item.peso_kg && <p>Peso: {item.peso_kg} kg · Talla: {item.talla_cm} cm{item.perimetro_cefalico_cm ? ` · PC: ${item.perimetro_cefalico_cm} cm` : ''}</p>}
                    {item.dosis && <p>Dosis: {item.dosis}{item.lote ? ` · Lote: ${item.lote}` : ''}</p>}
                    {Array.isArray(item.resultados_parametros) && item.resultados_parametros.map((p: any, i: number) => (
                      <p key={i}>{p.parametro}: <strong>{p.valor} {p.unidad || ''}</strong> <span style={{ color: 'var(--muted)' }}>{p.rango_referencia ? `(${p.rango_referencia})` : ''}</span></p>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          ))}
          </>}
        </div>
      )}
    </div>
  )
}

function AppointmentList({ citas, loading, onUpdate }: {
  citas: any[]
  loading: boolean
  onUpdate: (id: string, change: { fecha?: string; estado?: string }) => void
}) {
  const [newDates, setNewDates] = useState<Record<string, string>>({})
  return (
    <section className="appointment-list" aria-label="Citas programadas">
      <h2>Gestionar citas</h2>
      {citas.filter((c) => c.estado === 'programada').map((c) => {
        const id = String(c.id_cita)
        return (
          <div className="appointment-row" key={id}>
            <div><strong>{c.servicio}</strong><span>{String(c.fecha)}</span></div>
            <label>Reprogramar
              <input type="datetime-local" value={newDates[id] || ''} onChange={(e) =>
                setNewDates((dates) => ({ ...dates, [id]: e.target.value }))} />
            </label>
            <button type="button" disabled={loading || !newDates[id]} onClick={() =>
              onUpdate(id, { fecha: newDates[id] })}>Guardar fecha</button>
            <button type="button" disabled={loading} onClick={() =>
              onUpdate(id, { estado: 'cancelada' })}>Cancelar cita</button>
          </div>
        )
      })}
    </section>
  )
}

function Manifest({ onEnter, isLeaving }: { onEnter: () => void; isLeaving: boolean }) {
  return (
    <main className={`manifest-page${isLeaving ? ' is-leaving' : ''}`}>
      <div className="manifest-layout">
        <section className="manifest-copy">
          <h1>LA SALUD<br /><em>ES UN</em><br />DERECHO.</h1>
          <p className="manifest-lede">La salud pública universal pertenece a todas las personas. Una atención continua necesita historias clínicas que acompañen a cada paciente y a cada comunidad.</p>
          <button className="manifest-cta" onClick={onEnter}>Entrar al sistema <ArrowRight size={18} /></button>
        </section>
        <figure className="manifest-artwork">
          <img src="/images/salud-comunitaria.png" alt="Ilustración editorial de personal de salud y comunidad frente a una clínica pública" />
        </figure>
      </div>
    </main>
  )
}

function LoginScreen({ onLogin, loading, error }: {
  onLogin: (usuario: string, password: string) => void
  loading: boolean
  error: string
}) {
  const [usuario, setUsuario] = useState('')
  const [password, setPassword] = useState('')
  return (
    <main className="login-page">
      <form className="login-panel" onSubmit={(event) => {
        event.preventDefault()
        onLogin(usuario.trim(), password)
      }}>
        <span className="login-eyebrow">ACCESO INSTITUCIONAL</span>
        <h1>Historial clínico</h1>
        <p>Inicia sesión con tu cuenta. El sistema abrirá el expediente de tu institución.</p>
        {error && <div className="form-error" role="alert">{error}</div>}
        <label>Correo institucional
          <input type="email" value={usuario} onChange={(event) => setUsuario(event.target.value)}
            autoComplete="username" required autoFocus />
        </label>
        <label>Contraseña
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password" required />
        </label>
        <button className="primary-action" type="submit" disabled={loading}>
          {loading ? 'Verificando…' : 'Entrar al sistema'} <ArrowRight size={17} />
        </button>
      </form>
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

function EmptyOverview({ onAction }: { onAction: () => void }) {
  return (
    <section className="overview-empty" aria-labelledby="empty-title">
      <div className="overview-icon" aria-hidden="true"><Search size={22} strokeWidth={1.7} /></div>
      <h2 id="empty-title">Comienza con un paciente</h2>
      <p>Busca su expediente o registra uno nuevo.</p>
      <button className="empty-action" onClick={onAction}>Registrar paciente <ArrowRight size={15} /></button>
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
  initialCui,
  consultas,
  loading,
  onCancel,
  onSubmit,
}: {
  section: SectionId
  fields: Field[]
  institutionId: InstitutionId
  patient: any | null
  initialCui: string
  consultas: any[]
  loading: boolean
  onCancel: () => void
  onSubmit: (data: Record<string, string>) => void
}) {
  const consultaId = (c: any) => String(c.id_consulta ?? c.id)
  const lastConsulta = consultas.length ? consultaId(consultas[0]) : ''
  const [formData, setFormData] = useState<Record<string, string>>(() => ({ consulta: lastConsulta, document: initialCui }))
  const [formError, setFormError] = useState('')
  const motor = ENGINES[institutionId]
  const visibleFields = section === 'patients' && institutionId === 'pediatrics'
    ? [...fields,
      { name: 'guardian', label: 'Nombre del tutor', placeholder: 'Padre, madre o responsable', wide: true },
      { name: 'guardianPhone', label: 'Teléfono del tutor', type: 'tel' as const, placeholder: '1234 5678', optional: true },
    ]
    : fields

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    setFormError('')
    if (section === 'patients') {
      if (!isValidCuiFormat(formData.document || '')) {
        setFormError('El CUI debe tener exactamente 13 dígitos. Puede escribirlo con espacios o guiones.')
        return
      }
      if (formData.contact && !normalizeLocalPhone(formData.contact)) {
        setFormError('El teléfono debe tener 8 dígitos; el prefijo +502 es opcional.')
        return
      }
      if (formData.guardianPhone && !normalizeLocalPhone(formData.guardianPhone)) {
        setFormError('El teléfono del tutor debe tener 8 dígitos.')
        return
      }
    }
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
      {formError && <p className="form-error" role="alert">{formError}</p>}
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
            ) : field.type === 'select' ? (
              <select name={field.name} value={formData[field.name] || ''} onChange={handleChange} required={!field.optional}>
                <option value="">Seleccione…</option>
                {field.options?.map((option) => <option key={option} value={option}>{option}</option>)}
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
                maxLength={field.maxLength}
                pattern={field.pattern}
                inputMode={field.inputMode}
                min={field.min}
                max={field.max}
                autoComplete={field.name === 'document' ? 'off' : undefined}
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
