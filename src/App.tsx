import { useMemo, useState } from 'react'
import {
  ArrowRight, ArrowUpRight, Check, ChevronDown, CircleHelp, FileClock, Menu, Orbit, Plus, Search,
  ShieldCheck, Signal, X,
} from 'lucide-react'
import { createInstitutionWorkspace, institutions, sectionDetails, type InstitutionId, type NavigationItem, type SectionId } from './domain/institutions'

type Field = { name: string; label: string; placeholder?: string; type?: string; wide?: boolean }

const forms: Partial<Record<SectionId, Field[]>> = {
  patients: [
    { name: 'fullName', label: 'Nombre completo', placeholder: 'Nombre y apellidos', wide: true },
    { name: 'document', label: 'Documento de identificación', placeholder: 'No escriba datos reales en esta demostración' },
    { name: 'birthDate', label: 'Fecha de nacimiento', type: 'date' },
    { name: 'contact', label: 'Teléfono de contacto', placeholder: 'Número de teléfono' },
  ],
  appointments: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'date', label: 'Fecha y hora', type: 'datetime-local' },
    { name: 'service', label: 'Servicio', placeholder: 'Servicio o especialidad' },
    { name: 'professional', label: 'Profesional responsable', placeholder: 'Nombre del profesional' },
  ],
  consultations: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'date', label: 'Fecha de consulta', type: 'date' },
    { name: 'professional', label: 'Profesional responsable', placeholder: 'Nombre del profesional' },
    { name: 'note', label: 'Motivo y notas de consulta', placeholder: 'Resumen clínico de la consulta', wide: true },
  ],
  diagnoses: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'code', label: 'Código CIE-10', placeholder: 'Código diagnóstico' },
    { name: 'diagnosis', label: 'Diagnóstico', placeholder: 'Descripción clínica', wide: true },
  ],
  treatments: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'plan', label: 'Plan de tratamiento', placeholder: 'Descripción del tratamiento', wide: true },
    { name: 'startDate', label: 'Fecha de inicio', type: 'date' },
    { name: 'endDate', label: 'Fecha de seguimiento', type: 'date' },
  ],
  prescriptions: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'medicine', label: 'Medicamento', placeholder: 'Nombre genérico del medicamento' },
    { name: 'dose', label: 'Dosis e indicaciones', placeholder: 'Dosis, vía y frecuencia', wide: true },
  ],
  procedures: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'area', label: 'Pieza o área dental', placeholder: 'Referencia de la pieza o zona' },
    { name: 'procedure', label: 'Procedimiento', placeholder: 'Procedimiento realizado', wide: true },
  ],
  'lab-orders': [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'exam', label: 'Examen solicitado', placeholder: 'Nombre del examen' },
    { name: 'priority', label: 'Prioridad', placeholder: 'Ordinaria / urgente' },
  ],
  'lab-results': [
    { name: 'order', label: 'Orden de examen', placeholder: 'Identificador de la orden' },
  ],
  growth: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'date', label: 'Fecha de control', type: 'date' },
    { name: 'weight', label: 'Peso (kg)', type: 'number' },
    { name: 'height', label: 'Talla (cm)', type: 'number' },
    { name: 'head', label: 'Perímetro cefálico (cm)', type: 'number' },
  ],
  vaccines: [
    { name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' },
    { name: 'vaccine', label: 'Vacuna', placeholder: 'Nombre de la vacuna' },
    { name: 'dose', label: 'Dosis', placeholder: 'Número o nombre de la dosis' },
    { name: 'date', label: 'Fecha de aplicación', type: 'date' },
  ],
  archive: [
    { name: 'patient', label: 'Paciente o historia clínica', placeholder: 'Nombre o número de historia' },
    { name: 'date', label: 'Fecha de solicitud', type: 'date' },
    { name: 'reason', label: 'Motivo de archivado', placeholder: 'Justificación de desactivación', wide: true },
  ],
}

function App() {
  const [entered, setEntered] = useState(false)
  const [institutionId, setInstitutionId] = useState<InstitutionId>('hospital')
  const [section, setSection] = useState<SectionId>('overview')
  const [formOpen, setFormOpen] = useState(false)
  const [notice, setNotice] = useState('')
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const workspace = useMemo(() => createInstitutionWorkspace(institutionId), [institutionId])
  const details = sectionDetails[section]

  function changeSection(next: SectionId) {
    setSection(next)
    setFormOpen(false)
    setNotice('')
    setMobileNavOpen(false)
  }

  function changeInstitution(next: InstitutionId) {
    setInstitutionId(next)
    setSection('overview')
    setFormOpen(false)
    setNotice('')
  }

  function showUnavailable(action: string) {
    setNotice(`${action}: no se envió ni guardó información. El servidor aún no está conectado.`)
  }

  if (!entered) {
    return <Manifest onEnter={() => setEntered(true)} />
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Saltar al contenido</a>
      {mobileNavOpen && <button className="nav-scrim" onClick={() => setMobileNavOpen(false)} aria-label="Cerrar navegación" />}
      <aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`} aria-label="Navegación principal">
        <div className="sidebar-brand">
          <div className="brand-seal" aria-hidden="true"><Orbit size={21} strokeWidth={1.6} /></div>
          <div><strong>SALUD PÚBLICA</strong><span>UNIVERSAL</span></div>
          <button className="close-nav" onClick={() => setMobileNavOpen(false)} aria-label="Cerrar navegación"><X size={19} /></button>
        </div>

        <div className="workspace-label">CLIENTE <span>MAQUETA</span></div>
        <nav className="side-nav">
          <NavGroup label="GESTIÓN CLÍNICA" items={workspace.commonItems} active={section} onSelect={changeSection} />
          {workspace.specialtyItems.length > 0 && <NavGroup label={workspace.institution.shortName.toLocaleUpperCase('es')} items={workspace.specialtyItems} active={section} onSelect={changeSection} />}
        </nav>

        <div className="sidebar-bottom">
          <div className="orbital-mark" aria-hidden="true"><span /><i /><b /></div>
          <p>La atención continúa<br />cuando el historial permanece.</p>
          <button className="sidebar-help" onClick={() => setNotice('Esta interfaz es una maqueta funcional. La conexión con el servidor está pendiente.')}>
            <CircleHelp size={16} /> Acerca del sistema
          </button>
        </div>
      </aside>

      <main className="workspace-main" id="main-content">
        <header className="utility-bar">
          <button className="mobile-menu" onClick={() => setMobileNavOpen(true)} aria-label="Abrir navegación" aria-expanded={mobileNavOpen}><Menu size={20} /></button>
          <div className="utility-context"><span>PLATAFORMA CLÍNICA</span><b>/</b><span>{workspace.institution.name.toLocaleUpperCase('es')}</span></div>
          <div className="utility-actions">
            <span className="connection-badge"><Signal size={14} /> API DESCONECTADA</span>
            <button className="exit-button" onClick={() => { setEntered(false); setNotice('') }}>Salir <ArrowUpRight size={14} /></button>
          </div>
        </header>

        <section className="work-area" aria-labelledby="page-title">
          <div className="page-masthead">
            <div className="page-title-block">
              <p className="manifest-fragment">LA SALUD PÚBLICA UNIVERSAL ES UN DERECHO</p>
              <h1 id="page-title">{details.title}</h1>
              <p className="institution-description">{workspace.institution.description}</p>
            </div>
            <span className="institution-select-label">INSTITUCIÓN ACTIVA · VISTA LOCAL</span>
          </div>

          <InstitutionTabs active={institutionId} onSelect={changeInstitution} />

          <p className="prototype-notice"><Signal size={15} /> Prototipo sin conexión. No ingrese información clínica real; búsqueda y registro están deshabilitados.</p>
          <form className="patient-search" onSubmit={(event) => { event.preventDefault() }}>
            <label className="search-input-wrap">
              <Search size={19} aria-hidden="true" />
              <span className="sr-only">Buscar por documento, historia clínica o nombre</span>
              <input disabled placeholder="Búsqueda disponible al conectar la API" aria-label="Búsqueda de pacientes, API pendiente" />
            </label>
            <label className="service-filter"><span className="sr-only">Filtrar servicio</span>
              <select disabled defaultValue="all" aria-label="Filtro por servicio, disponible al conectar la API"><option value="all">Todos los servicios · API pendiente</option></select><ChevronDown size={15} aria-hidden="true" />
            </label>
            <button type="submit" className="search-submit" disabled>Buscar <ArrowRight size={16} /></button>
          </form>

          {notice && <div className="system-notice" role="status"><Signal size={16} /><p>{notice}</p><button onClick={() => setNotice('')} aria-label="Cerrar aviso"><X size={16} /></button></div>}

          {section === 'overview' ? (
            <EmptyOverview onAction={() => { changeSection('patients'); setFormOpen(true) }} />
          ) : section === 'search' ? (
            <EmptyState icon="search" title="Búsqueda disponible al conectar el servidor" description="El campo de búsqueda permanece deshabilitado hasta que exista una conexión real con la institución." />
          ) : (
            <section className="operation-area" aria-label={details.title}>
              <EmptyState icon={section === 'archive' ? 'archive' : section === 'lab-results' ? 'lab' : 'history'} title={details.emptyTitle} description={details.description} />
              {!formOpen ? (
                <button className="primary-action" onClick={() => { setFormOpen(true); setNotice('') }}>
                  <Plus size={16} /> {details.action}
                </button>
              ) : (
                <OperationForm section={section} institutionId={institutionId} onCancel={() => setFormOpen(false)} onSubmit={() => showUnavailable(details.action)} />
              )}
            </section>
          )}

          <footer className="work-footer">
            <span>MAQUETA DE INTERFAZ · SIN DATOS CLÍNICOS</span>
            <span className="footer-institutions">Hospital · Odontología · Laboratorio · Pediatría</span>
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
  return <div className="nav-group"><p>{label}</p>{items.map(({ id, label: itemLabel, icon: Icon }) => <button key={id} className={`nav-item ${active === id ? 'nav-item-active' : ''}`} onClick={() => onSelect(id)} aria-current={active === id ? 'page' : undefined}><Icon size={17} strokeWidth={1.7} /><span>{itemLabel}</span>{active === id && <span className="nav-indicator" />}</button>)}</div>
}

function InstitutionTabs({ active, onSelect }: { active: InstitutionId; onSelect: (id: InstitutionId) => void }) {
  return <div className="institution-tabs" aria-label="Cambiar institución · vista local">
    {Object.values(institutions).map((institution) => <button key={institution.id} type="button" aria-pressed={active === institution.id} className={active === institution.id ? 'tab-active' : ''} onClick={() => onSelect(institution.id)}>{institution.shortName}</button>)}
  </div>
}

function EmptyOverview({ onAction }: { onAction: () => void }) {
  return <section className="overview-empty" aria-labelledby="empty-title">
    <div className="coordinate-label coordinate-top">REGISTRO DE OPERACIONES <span>SPU—0001</span></div>
    <div className="empty-orbit" aria-hidden="true"><div className="orbit-ring orbit-ring-one" /><div className="orbit-ring orbit-ring-two" /><div className="orbit-cross"><span /><i /></div><div className="orbit-core"><Search size={26} strokeWidth={1.4} /></div><b className="orbit-dot" /></div>
    <h2 id="empty-title">Sin conexión a los historiales clínicos</h2>
    <p>No hay un servidor conectado para consultar pacientes ni confirmar si existen registros.</p>
    <button className="empty-action" onClick={onAction}>Iniciar registro <ArrowRight size={15} /></button>
    <div className="coordinate-label coordinate-bottom"><span>HISTORIAL CLÍNICO · VISTA VACÍA</span><span>— — —</span></div>
  </section>
}

function EmptyState({ icon, title, description }: { icon: 'search' | 'history' | 'archive' | 'lab'; title: string; description: string }) {
  const Icon = icon === 'search' ? Search : icon === 'archive' ? ShieldCheck : icon === 'lab' ? Signal : FileClock
  return <div className="empty-state">
    <div className="empty-state-icon"><Icon size={23} strokeWidth={1.6} /></div>
    <div><h2>{title}</h2><p>{description}</p></div>
  </div>
}

function OperationForm({ section, institutionId, onCancel, onSubmit }: { section: SectionId; institutionId: InstitutionId; onCancel: () => void; onSubmit: () => void }) {
  const [parameterCount, setParameterCount] = useState(1)
  const fields = forms[section] ?? [{ name: 'patient', label: 'Paciente', placeholder: 'Nombre o número de historia' }, { name: 'detail', label: 'Detalle de la operación', placeholder: 'Información requerida', wide: true }]
  const visibleFields = section === 'patients' && institutionId === 'pediatrics'
    ? [...fields, { name: 'guardian', label: 'Madre, padre o persona tutora', placeholder: 'Nombre de responsable', wide: true }]
    : fields
  return <form className="operation-form" onSubmit={(event) => { event.preventDefault(); onSubmit() }}>
    <div className="form-heading"><div><span>CAPTURA DE INTERFAZ</span><h3>{sectionDetails[section].action}</h3></div><span className="not-connected"><Signal size={13} /> SIN API</span></div>
    <p className="privacy-note"><strong>Solo demostración:</strong> use datos inventados. La API no está conectada; los campos no se envían ni guardan. La validación local conservará lo escrito en esta pantalla.</p>
    <div className="form-grid">{visibleFields.map((field) => <label key={field.name} className={field.wide ? 'field-wide' : ''}>{field.label}<input name={field.name} type={field.type ?? 'text'} placeholder={field.placeholder} required /></label>)}
      {section === 'lab-results' && <div className="field-wide lab-parameters">
        <div className="lab-parameters-heading"><h4>Parámetros del resultado</h4><button type="button" onClick={() => setParameterCount((count) => count + 1)}><Plus size={14} /> Agregar parámetro</button></div>
        {Array.from({ length: parameterCount }, (_, index) => <div className="lab-parameter-row" key={index}>
          <label>Parámetro<input name={`parameter-${index}`} placeholder="Nombre" required /></label>
          <label>Resultado<input name={`value-${index}`} placeholder="Valor" required /></label>
          <label>Unidad<input name={`unit-${index}`} placeholder="Unidad" required /></label>
          <label>Referencia<input name={`reference-${index}`} placeholder="Rango" required /></label>
        </div>)}
      </div>}
    </div>
    <div className="form-actions"><button type="button" className="secondary-action" onClick={onCancel}>Cancelar</button><button type="submit" className="primary-action"><Check size={15} /> Probar validación · no guarda</button></div>
  </form>
}

export default App
