import type { LucideIcon } from 'lucide-react'
import {
  Archive, CalendarDays, ClipboardList, FileClock, FilePlus2, FlaskConical,
  HeartPulse, Microscope, Pill, Search, Syringe, Stethoscope, Users, Activity,
} from 'lucide-react'

export type InstitutionId = 'hospital' | 'dental' | 'laboratory' | 'pediatrics'
export type SectionId =
  | 'overview' | 'search' | 'patients' | 'histories' | 'appointments' | 'consultations'
  | 'diagnoses' | 'treatments' | 'prescriptions' | 'procedures' | 'lab-orders'
  | 'lab-results' | 'growth' | 'vaccines' | 'archive'

export type NavigationItem = { id: SectionId; label: string; icon: LucideIcon }
export type Institution = {
  id: InstitutionId
  name: string
  shortName: string
  description: string
  features: SectionId[]
}

export const institutions: Record<InstitutionId, Institution> = {
  hospital: {
    id: 'hospital', name: 'Hospital General', shortName: 'Hospital',
    description: 'Atención general, consultas y continuidad del expediente clínico.',
    features: ['appointments', 'consultations', 'diagnoses', 'treatments', 'prescriptions'],
  },
  dental: {
    id: 'dental', name: 'Clínica Odontológica', shortName: 'Odontología',
    description: 'Atención odontológica con acceso ágil para personal clínico y secretaría.',
    features: ['appointments', 'consultations', 'diagnoses', 'procedures', 'treatments'],
  },
  laboratory: {
    id: 'laboratory', name: 'Laboratorio Clínico', shortName: 'Laboratorio',
    description: 'Órdenes de examen y resultados con parámetros variables por estudio.',
    features: ['lab-orders', 'lab-results'],
  },
  pediatrics: {
    id: 'pediatrics', name: 'Centro Médico Pediátrico', shortName: 'Pediatría',
    description: 'Seguimiento pediátrico con controles de crecimiento y vacunación.',
    features: ['appointments', 'consultations', 'diagnoses', 'treatments', 'prescriptions', 'growth', 'vaccines'],
  },
}

const commonNavigation: NavigationItem[] = [
  { id: 'overview', label: 'Resumen', icon: Activity },
  { id: 'search', label: 'Buscar paciente', icon: Search },
  { id: 'patients', label: 'Registrar paciente', icon: FilePlus2 },
  { id: 'histories', label: 'Historial clínico', icon: FileClock },
  { id: 'appointments', label: 'Citas', icon: CalendarDays },
  { id: 'consultations', label: 'Consultas', icon: Stethoscope },
  { id: 'diagnoses', label: 'Diagnósticos', icon: ClipboardList },
  { id: 'treatments', label: 'Tratamientos', icon: HeartPulse },
  { id: 'prescriptions', label: 'Recetas', icon: Pill },
  { id: 'archive', label: 'Archivo clínico', icon: Archive },
]

const featureNavigation: Record<SectionId, NavigationItem> = {
  overview: commonNavigation[0], search: commonNavigation[1], patients: commonNavigation[2],
  histories: commonNavigation[3], appointments: commonNavigation[4], consultations: commonNavigation[5],
  diagnoses: commonNavigation[6], treatments: commonNavigation[7], prescriptions: commonNavigation[8],
  archive: commonNavigation[9],
  procedures: { id: 'procedures', label: 'Procedimientos', icon: Stethoscope },
  'lab-orders': { id: 'lab-orders', label: 'Órdenes de examen', icon: FlaskConical },
  'lab-results': { id: 'lab-results', label: 'Resultados', icon: Microscope },
  growth: { id: 'growth', label: 'Crecimiento', icon: Users },
  vaccines: { id: 'vaccines', label: 'Vacunación', icon: Syringe },
}

export type Workspace = { institution: Institution; commonItems: NavigationItem[]; specialtyItems: NavigationItem[] }

/** Factory Method: builds the institution-specific workspace from one shared UI vocabulary. */
export function createInstitutionWorkspace(id: InstitutionId): Workspace {
  const institution = institutions[id]
  const commonItems = commonNavigation
  const specialtyItems = institution.features
    .filter((feature) => !commonNavigation.some(({ id: section }) => section === feature))
    .map((feature) => featureNavigation[feature])
  return { institution, commonItems, specialtyItems }
}

export const sectionDetails: Record<SectionId, { title: string; emptyTitle: string; description: string; action: string }> = {
  overview: { title: 'Índice de operaciones clínicas', emptyTitle: 'Sin conexión a los historiales clínicos', description: 'No hay un servidor conectado para consultar pacientes ni confirmar si existen registros.', action: 'Iniciar registro' },
  search: { title: 'Buscar paciente', emptyTitle: 'La búsqueda está disponible al conectar el servidor', description: 'Busque por nombre, documento o número de historia clínica.', action: 'Nueva búsqueda' },
  patients: { title: 'Registro de pacientes', emptyTitle: 'Sin conexión al registro de pacientes', description: 'Conecte el servidor para consultar si hay pacientes o crear una nueva historia clínica.', action: 'Nuevo registro' },
  histories: { title: 'Historial clínico', emptyTitle: 'Seleccione un paciente para consultar su historial', description: 'Las consultas, diagnósticos y tratamientos se mostrarán en orden cronológico.', action: 'Buscar paciente' },
  appointments: { title: 'Citas', emptyTitle: 'Sin conexión al calendario de citas', description: 'El servidor debe conectarse antes de consultar o programar citas.', action: 'Programar cita' },
  consultations: { title: 'Consultas', emptyTitle: 'Sin conexión a las consultas', description: 'Al conectar el servidor, cada consulta formará parte del historial clínico del paciente.', action: 'Registrar consulta' },
  diagnoses: { title: 'Diagnósticos', emptyTitle: 'Sin conexión a los diagnósticos', description: 'Los diagnósticos se asociarán con una consulta y una historia clínica.', action: 'Agregar diagnóstico' },
  treatments: { title: 'Tratamientos', emptyTitle: 'Sin conexión a los tratamientos', description: 'El servidor debe conectarse para consultar o registrar planes de tratamiento.', action: 'Indicar tratamiento' },
  prescriptions: { title: 'Recetas', emptyTitle: 'Sin conexión a las recetas', description: 'Las indicaciones de medicamento requieren guardar la consulta en el servidor.', action: 'Crear receta' },
  procedures: { title: 'Procedimientos odontológicos', emptyTitle: 'Sin conexión a procedimientos odontológicos', description: 'Al conectar el servidor, cada procedimiento se asociará al paciente y su consulta.', action: 'Registrar procedimiento' },
  'lab-orders': { title: 'Órdenes de examen', emptyTitle: 'Sin conexión a las órdenes de examen', description: 'Las órdenes y sus parámetros se consultarán desde el laboratorio.', action: 'Crear orden' },
  'lab-results': { title: 'Resultados de laboratorio', emptyTitle: 'Sin conexión a los resultados de laboratorio', description: 'Cada examen puede incluir parámetros y unidades diferentes.', action: 'Ingresar resultados' },
  growth: { title: 'Control de crecimiento', emptyTitle: 'Sin conexión a los controles de crecimiento', description: 'Peso, talla y otras mediciones se registrarán por fecha.', action: 'Registrar control' },
  vaccines: { title: 'Vacunación', emptyTitle: 'Sin conexión al registro de vacunación', description: 'El historial de dosis aparecerá por paciente y fecha.', action: 'Registrar vacuna' },
  archive: { title: 'Archivo clínico', emptyTitle: 'No hay conexión con el archivo clínico', description: 'Al conectar el servidor, se podrán consultar y solicitar el archivado de historias clínicas.', action: 'Solicitar archivado' },
}
