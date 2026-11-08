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
  overview: { title: 'Índice de operaciones clínicas', emptyTitle: 'Índice de operaciones clínicas', description: 'Seleccione una operación en el menú lateral o registre un nuevo paciente.', action: 'Iniciar registro' },
  search: { title: 'Buscar paciente', emptyTitle: 'Búsqueda de pacientes', description: 'Ingrese el DPI en la barra superior para cargar el expediente desde el motor activo.', action: 'Nueva búsqueda' },
  patients: { title: 'Registro de pacientes', emptyTitle: 'Nuevo expediente clínico', description: 'Registre un paciente en el motor de la institución activa. Si el DPI ya existe, se actualizará su expediente.', action: 'Nuevo registro' },
  histories: { title: 'Historial clínico', emptyTitle: 'Seleccione un paciente para consultar su historial', description: 'Las consultas, diagnósticos y recetas se muestran en orden cronológico.', action: 'Buscar paciente' },
  appointments: { title: 'Citas', emptyTitle: 'Programación de citas', description: 'La cita se registra como una consulta del paciente con su fecha y servicio.', action: 'Programar cita' },
  consultations: { title: 'Consultas', emptyTitle: 'Consultas del paciente', description: 'Cada consulta forma parte del historial clínico y sirve de base para diagnósticos y recetas.', action: 'Registrar consulta' },
  diagnoses: { title: 'Diagnósticos', emptyTitle: 'Diagnósticos clínicos', description: 'El diagnóstico se asocia a una consulta existente del paciente (código CIE-10).', action: 'Agregar diagnóstico' },
  treatments: { title: 'Tratamientos', emptyTitle: 'Planes de tratamiento', description: 'El plan de tratamiento se registra como una consulta de seguimiento en el historial.', action: 'Indicar tratamiento' },
  prescriptions: { title: 'Recetas', emptyTitle: 'Recetas y medicamentos', description: 'La receta se asocia a una consulta existente con dosis, frecuencia y duración.', action: 'Crear receta' },
  procedures: { title: 'Procedimientos odontológicos', emptyTitle: 'Procedimientos odontológicos', description: 'El procedimiento se registra como una atención del paciente, con la pieza o área tratada.', action: 'Registrar procedimiento' },
  'lab-orders': { title: 'Órdenes de examen', emptyTitle: 'Órdenes de examen', description: 'La orden se guarda en el laboratorio con sus exámenes y parámetros embebidos.', action: 'Crear orden' },
  'lab-results': { title: 'Resultados de laboratorio', emptyTitle: 'Resultados de laboratorio', description: 'Busque al paciente por DPI para ver sus exámenes y parámetros de resultado.', action: 'Ver resultados' },
  growth: { title: 'Control de crecimiento', emptyTitle: 'Controles de crecimiento', description: 'Peso, talla y perímetro cefálico se registran como una consulta de control.', action: 'Registrar control' },
  vaccines: { title: 'Vacunación', emptyTitle: 'Registro de vacunación', description: 'Cada dosis aplicada se registra como una consulta en el historial del paciente.', action: 'Registrar vacuna' },
  archive: { title: 'Archivo clínico', emptyTitle: 'Archivado de historial', description: 'Da de baja administrativa el expediente del paciente cargado; se conserva para consulta.', action: 'Solicitar archivado' },
}
