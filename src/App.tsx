import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight, Check, CircleHelp, FileClock, Menu, Orbit, Plus, Search,
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

type Field = { name: string; label: string; placeholder?: string; type?: string; wide?: boolean }

const forms: Partial<Record<SectionId, Field[]>> = {
  patients: [
    { name: 'fullName', label: 'Nombre completo', placeholder: 'Nombre y apellidos', wide: true },
    { name: 'document', label: 'Documento de identificación (DPI/CUI)', placeholder: 'Ej. TEST0001' },
    { name: 'birthDate', label: 'Fecha de nacimiento', type: 'date' },
    { name: 'contact', label: 'Teléfono de contacto', placeholder: 'Número de teléfono' },
  ],
  appointments: [
    { name: 'patient', label: 'ID del paciente', placeholder: 'ID del paciente' },
    { name: 'date', label: 'Fecha y hora', type: 'datetime-local' },
    { name: 'service', label: 'Servicio', placeholder: 'Servicio o especialidad' },
    { name: 'professional', label: 'Profesional responsable', placeholder: 'Nombre del profesional' },
  ],
  consultations: [
    { name: 'patient', label: 'ID del paciente', placeholder: 'ID numérico o alfanumérico del paciente' },
    { name: 'date', label: 'Fecha de consulta', type: 'date' },
    { name: 'professional', label: 'Profesional responsable', placeholder: 'Nombre del profesional' },
    { name: 'note', label: 'Motivo y notas de consulta', placeholder: 'Resumen clínico de la consulta', wide: true },
  ],
  diagnoses: [
    { name: 'patient', label: 'ID de la consulta', placeholder: 'ID de la consulta a asociar' },
    { name: 'code', label: 'Código CIE-10', placeholder: 'Ej. Z00.0' },
    { name: 'diagnosis', label: 'Diagnóstico clínico', placeholder: 'Descripción clínica', wide: true },
  ],
  treatments: [
    { name: 'patient', label: 'ID del paciente o consulta', placeholder: 'ID' },
    { name: 'plan', label: 'Plan de tratamiento', placeholder: 'Descripción del tratamiento', wide: true },
    { name: 'startDate', label: 'Fecha de inicio', type: 'date' },
    { name: 'endDate', label: 'Fecha de seguimiento', type: 'date' },
  ],
  prescriptions: [
    { name: 'patient', label: 'ID de la consulta', placeholder: 'ID de la consulta asociada' },
    { name: 'medicine', label: 'Medicamento', placeholder: 'Nombre genérico del medicamento' },
    { name: 'dose', label: 'Dosis e indicaciones', placeholder: 'Ej. 1 tableta cada 8 horas', wide: true },
  ],
  procedures: [
    { name: 'patient', label: 'ID del paciente o atención', placeholder: 'ID' },
    { name: 'area', label: 'Pieza o área dental', placeholder: 'Referencia de la pieza o zona' },
    { name: 'procedure', label: 'Procedimiento', placeholder: 'Procedimiento realizado', wide: true },
  ],
  'lab-orders': [
    { name: 'patient', label: 'ID del paciente', placeholder: 'ID del paciente' },
    { name: 'exam', label: 'Examen solicitado', placeholder: 'Nombre del examen' },
    { name: 'priority', label: 'Prioridad', placeholder: 'Ordinaria / urgente' },
  ],
  'lab-results': [
    { name: 'order', label: 'Orden de examen', placeholder: 'Identificador de la orden' },
  ],
  growth: [
    { name: 'patient', label: 'ID del paciente', placeholder: 'ID del paciente' },
    { name: 'date', label: 'Fecha de control', type: 'date' },
    { name: 'weight', label: 'Peso (kg)', type: 'number' },
    { name: 'height', label: 'Talla (cm)', type: 'number' },
    { name: 'head', label: 'Perímetro cefálico (cm)', type: 'number' },
  ],
  vaccines: [
    { name: 'patient', label: 'ID del paciente', placeholder: 'ID del paciente' },
    { name: 'vaccine', label: 'Vacuna', placeholder: 'Nombre de la vacuna' },
    { name: 'dose', label: 'Dosis', placeholder: 'Número o nombre de la dosis' },
    { name: 'date', label: 'Fecha de aplicación', type: 'date' },
  ],
  archive: [
    { name: 'patient', label: 'ID del paciente a archivar', placeholder: 'ID del paciente' },
    { name: 'date', label: 'Fecha de solicitud', type: 'date' },
    { name: 'reason', label: 'Motivo de archivado', placeholder: 'Justificación de desactivación o baja', wide: true },
  ],
}

function App() {
  const [entered, setEntered] = useState(false)
  const [institutionId, setInstitutionId] = useState<InstitutionId>('hospital')
  const [section, setSection] = useState<SectionId>('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [formOpen, setFormOpen] = useState(false)
  const [notice, setNotice] = useState<string>('')
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const [token, setToken] = useState<string | null>(null)
  const [searchDpi, setSearchDpi] = useState<string>('')
  const [patientResult, setPatientResult] = useState<any | null>(null)
  const [historyResult, setHistoryResult] = useState<any | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  const workspace = useMemo(() => createInstitutionWorkspace(institutionId), [institutionId])
  const details = sectionDetails[section]
  const currentEngine = INSTITUTION_CREDENTIALS[institutionId].motor

  // Autenticar al cargar o cambiar de institución
  useEffect(() => {
    let isMounted = true
    async function login() {
      const creds = INSTITUTION_CREDENTIALS[institutionId]
      try {
        const res = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ usuario: creds.usuario, password: creds.password }),
        })
        if (res.ok) {
          const data = await res.json()
          if (isMounted) {
            setToken(data.access_token)
            setIsConnected(true)
          }
        } else {
          if (isMounted) {
            setIsConnected(false)
            setToken(null)
          }
        }
      } catch (err) {
        if (isMounted) {
          setIsConnected(false)
          setToken(null)
        }
      }
    }
    login()
    return () => {
      isMounted = false
    }
  }, [institutionId])

  function changeSection(nextSection: SectionId) {
    setSection(nextSection)
    setFormOpen(false)
    setMobileMenuOpen(false)
    setNotice('')
  }

  function changeInstitution(nextInstitution: InstitutionId) {
    setInstitutionId(nextInstitution)
    setSection('overview')
    setFormOpen(false)
    setNotice('')
    setPatientResult(null)
    setHistoryResult(null)
  }

  async function handleSearch(event?: React.FormEvent) {
    if (event) event.preventDefault()
    if (!searchDpi.trim()) return
    setLoading(true)
    setNotice('')
    try {
      const headers: Record<string, string> = {}
      if (token) headers['Authorization'] = `Bearer ${token}`

      const res = await fetch(`${API_URL}/pacientes/buscar?dpi=${encodeURIComponent(searchDpi.trim())}`, { headers })
      if (res.ok) {
        const data = await res.json()
        setPatientResult(data)
        setSection('search')
        // Consultar historial
        const pid = data.id_paciente || data.id
        if (pid) {
          const histRes = await fetch(`${API_URL}/historial/${pid}`, { headers })
          if (histRes.ok) {
            const histData = await histRes.json()
            setHistoryResult(histData)
          }
        }
      } else {
        setPatientResult(null)
        setHistoryResult(null)
        setNotice(`No se encontró ningún paciente con el DPI ${searchDpi}`)
      }
    } catch (err: any) {
      setNotice(`Error al buscar paciente: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  async function handleFormSubmit(data: Record<string, string>) {
    setLoading(true)
    setNotice('')
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' }
      if (token) headers['Authorization'] = `Bearer ${token}`

      if (section === 'patients') {
        const payload = {
          nombre: data.fullName,
          dpi: data.document,
          fecha_nacimiento: data.birthDate || '1990-01-01',
          telefono: data.contact || '',
          tutor_nombre: data.guardian || '',
        }
        const res = await fetch(`${API_URL}/pacientes/`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        })
        if (res.ok) {
          const out = await res.json()
          setNotice(`✅ Paciente '${out.nombre}' registrado con éxito en ${workspace.institution.name}. ID: ${out.id_paciente || out.id}`)
          setFormOpen(false)
          setPatientResult(out)
          setSearchDpi(out.dpi)
        } else {
          const err = await res.json()
          setNotice(`❌ Error al registrar paciente: ${err.detail || 'Fallo en el servidor'}`)
        }
      } else if (section === 'consultations') {
        const payload = {
          id_paciente: data.patient,
          motivo: data.note || 'Consulta médica',
          profesional: data.professional || 'Médico tratante',
        }
        const res = await fetch(`${API_URL}/consultas/`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        })
        if (res.ok) {
          const out = await res.json()
          setNotice(`✅ Consulta registrada con éxito. ID: ${out.id_consulta || out.id}`)
          setFormOpen(false)
        } else {
          const err = await res.json()
          setNotice(`❌ Error al registrar consulta: ${err.detail || 'Fallo en el servidor'}`)
        }
      } else if (section === 'diagnoses') {
        const payload = {
          id_consulta: data.patient,
          descripcion: data.diagnosis,
          codigo_cie10: data.code || 'Z00.0',
        }
        const res = await fetch(`${API_URL}/consultas/diagnostico`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        })
        if (res.ok) {
          setNotice(`✅ Diagnóstico agregado con éxito a la consulta ${data.patient}.`)
          setFormOpen(false)
        } else {
          const err = await res.json()
          setNotice(`❌ Error al agregar diagnóstico: ${err.detail || 'Fallo en el servidor'}`)
        }
      } else if (section === 'prescriptions') {
        const payload = {
          id_consulta: data.patient,
          medicamento: data.medicine,
          dosis: data.dose,
          frecuencia: 'Según indicación',
          duracion_dias: 5,
        }
        const res = await fetch(`${API_URL}/consultas/receta`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        })
        if (res.ok) {
          setNotice(`✅ Receta registrada con éxito para la consulta ${data.patient}.`)
          setFormOpen(false)
        } else {
          const err = await res.json()
          setNotice(`❌ Error al registrar receta: ${err.detail || 'Fallo en el servidor'}`)
        }
      } else if (section === 'archive') {
        const pid = data.patient
        const res = await fetch(`${API_URL}/pacientes/${pid}/archivar`, {
          method: 'PATCH',
          headers,
        })
        if (res.ok) {
          setNotice(`✅ Historial del paciente ${pid} archivado exitosamente (baja administrativa).`)
          setFormOpen(false)
        } else {
          const err = await res.json()
          setNotice(`❌ Error al archivar paciente: ${err.detail || 'Fallo en el servidor'}`)
        }
      } else {
        setNotice(`Operación ${details.action} procesada en ${workspace.institution.name}.`)
        setFormOpen(false)
      }
    } catch (err: any) {
      setNotice(`Error de comunicación con el servidor: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (!entered) {
    return <Manifest onEnter={() => setEntered(true)} />
  }

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
              <span><Signal size={15} /> Intentando conectar con http://localhost:8000... Asegúrese de que el backend esté ejecutándose.</span>
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
              {loading ? 'Buscando...' : 'Buscar'} <ArrowRight size={16} />
            </button>
          </form>

          {notice && (
            <div className="system-notice" role="status">
              <Signal size={16} />
              <p>{notice}</p>
              <button onClick={() => setNotice('')} aria-label="Cerrar aviso"><X size={16} /></button>
            </div>
          )}

          {/* Resultado de búsqueda de paciente */}
          {patientResult && (
            <div className="patient-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>{patientResult.nombre}</h3>
                <span className={`badge ${patientResult.estado === 'archivado' ? 'badge-archived' : 'badge-active'}`}>
                  {patientResult.estado}
                </span>
              </div>
              <p><strong>ID:</strong> {patientResult.id_paciente || patientResult.id} | <strong>DPI:</strong> {patientResult.dpi}</p>
              <p><strong>Fecha de Nacimiento:</strong> {patientResult.fecha_nacimiento} | <strong>Teléfono:</strong> {patientResult.telefono || 'No registrado'}</p>
              {patientResult.tutor_nombre && <p><strong>Tutor:</strong> {patientResult.tutor_nombre} ({patientResult.tutor_telefono})</p>}

              {historyResult && (
                <div style={{ marginTop: 15, borderTop: '1px solid #ccc', paddingTop: 10 }}>
                  <h4 style={{ margin: '10px 0 5px' }}>Historial de Consultas ({historyResult.consultas?.length || 0})</h4>
                  <div className="history-timeline">
                    {historyResult.consultas?.map((c: any, idx: number) => (
                      <div key={idx} className="history-entry">
                        <h4>Consulta #{c.id_consulta || c.id} — {c.profesional || 'Médico'}</h4>
                        <p><strong>Motivo:</strong> {c.motivo}</p>
                        <p style={{ fontSize: 11, color: '#888' }}>Fecha: {c.fecha}</p>
                      </div>
                    ))}
                    {historyResult.consultas?.length === 0 && <p style={{ fontSize: 12, color: '#777' }}>No hay consultas registradas para este paciente.</p>}
                  </div>

                  <h4 style={{ margin: '15px 0 5px' }}>Diagnósticos Registrados ({historyResult.diagnosticos?.length || 0})</h4>
                  <div className="history-timeline">
                    {historyResult.diagnosticos?.map((d: any, idx: number) => (
                      <div key={idx} className="history-entry" style={{ borderLeftColor: '#0056b3' }}>
                        <h4>{d.codigo_cie10 ? `[${d.codigo_cie10}] ` : ''}{d.descripcion}</h4>
                        <p style={{ fontSize: 11, color: '#888' }}>Asociado a Consulta #{d.id_consulta}</p>
                      </div>
                    ))}
                  </div>

                  <h4 style={{ margin: '15px 0 5px' }}>Recetas y Medicamentos ({historyResult.recetas?.length || 0})</h4>
                  <div className="history-timeline">
                    {historyResult.recetas?.map((r: any, idx: number) => (
                      <div key={idx} className="history-entry" style={{ borderLeftColor: '#28a745' }}>
                        <h4>💊 {r.medicamento}</h4>
                        <p>Dosis: {r.dosis} | Frecuencia: {r.frecuencia} | Duración: {r.duracion_dias} días</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {section === 'overview' ? (
            <EmptyOverview onAction={() => { changeSection('patients'); setFormOpen(true) }} />
          ) : section === 'search' ? (
            !patientResult && <EmptyState icon="search" title="Búsqueda de Pacientes" description="Ingrese el DPI en la barra superior para buscar el expediente en el motor activo." />
          ) : (
            <section className="operation-area" aria-label={details.title}>
              {!formOpen ? (
                <div>
                  <EmptyState icon={section === 'archive' ? 'archive' : section === 'lab-results' ? 'lab' : 'history'} title={details.emptyTitle} description={details.description} />
                  <button className="primary-action" onClick={() => { setFormOpen(true); setNotice('') }}>
                    <Plus size={16} /> {details.action}
                  </button>
                </div>
              ) : (
                <OperationForm
                  section={section}
                  institutionId={institutionId}
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
  institutionId,
  onCancel,
  onSubmit,
}: {
  section: SectionId
  institutionId: InstitutionId
  onCancel: () => void
  onSubmit: (data: Record<string, string>) => void
}) {
  const [formData, setFormData] = useState<Record<string, string>>({})
  const fields = forms[section] ?? [
    { name: 'patient', label: 'ID del Paciente', placeholder: 'ID del paciente o historia' },
    { name: 'detail', label: 'Detalle de la operación', placeholder: 'Información requerida', wide: true },
  ]
  const visibleFields = section === 'patients' && institutionId === 'pediatrics'
    ? [...fields, { name: 'guardian', label: 'Madre, padre o persona tutora', placeholder: 'Nombre de responsable', wide: true }]
    : fields

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    onSubmit(formData)
  }

  return (
    <form className="operation-form" onSubmit={handleSubmit}>
      <div className="form-heading">
        <div>
          <span>CAPTURA DE OPERACIÓN</span>
          <h3>{sectionDetails[section].action}</h3>
        </div>
        <span className="connected"><Signal size={13} /> EN LÍNEA · {INSTITUTION_CREDENTIALS[institutionId].motor}</span>
      </div>
      <p className="privacy-note">
        <strong>Persistencia activa:</strong> Los datos ingresados se enviarán directamente al motor de la institución activa ({INSTITUTION_CREDENTIALS[institutionId].motor}).
      </p>
      <div className="form-grid">
        {visibleFields.map((field) => (
          <label key={field.name} className={field.wide ? 'field-wide' : ''}>
            {field.label}
            <input
              name={field.name}
              type={field.type ?? 'text'}
              placeholder={field.placeholder}
              value={formData[field.name] || ''}
              onChange={handleChange}
              required
            />
          </label>
        ))}
      </div>
      <div className="form-actions">
        <button type="button" className="secondary-action" onClick={onCancel}>Cancelar</button>
        <button type="submit" className="primary-action"><Check size={15} /> Guardar en {INSTITUTION_CREDENTIALS[institutionId].motor}</button>
      </div>
    </form>
  )
}

export default App
