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
    features: ['appointments', 'consultations', 'diagnoses', 'procedures', 'treatments', 'prescriptions'],
  },
  laboratory: {
    id: 'laboratory', name: 'Laboratorio Clínico', shortName: 'Laboratorio',
    description: 'Órdenes de examen y resultados con parámetros variables por estudio.',
    features: ['lab-orders', 'lab-results', 'diagnoses', 'treatments', 'prescriptions'],
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

/** La navegación refleja los permisos de escritura de la cuenta autenticada. */
export function createInstitutionWorkspace(id: InstitutionId, role = ''): Workspace {
  const institution = institutions[id]
  const reception = role === 'secretaria'
  const technician = role === 'tecnico'
  const alwaysVisible = ['overview', 'search', 'patients', 'histories']
  const canShow = (feature: SectionId) => {
    if (reception) return [...alwaysVisible, 'appointments'].includes(feature)
    if (technician) return [...alwaysVisible, 'lab-orders', 'lab-results'].includes(feature)
    return [...alwaysVisible, 'archive', ...institution.features].includes(feature)
  }
  const commonItems = commonNavigation.filter(({ id: feature }) => canShow(feature))
  const specialtyItems = institution.features
    .filter((feature) => canShow(feature) && !commonNavigation.some(({ id: section }) => section === feature))
    .map((feature) => featureNavigation[feature])
  return { institution, commonItems, specialtyItems }
}

export const sectionDetails: Record<SectionId, { title: string; emptyTitle: string; description: string; action: string }> = {
  overview: { title: 'Resumen', emptyTitle: 'Resumen', description: 'Busca un paciente o registra uno nuevo.', action: 'Registrar paciente' },
  search: { title: 'Buscar paciente', emptyTitle: 'Búsqueda de pacientes', description: 'Ingrese el CUI en la barra superior para cargar el expediente desde el sistema activo.', action: 'Nueva búsqueda' },
  patients: { title: 'Registro de pacientes', emptyTitle: 'Nuevo expediente clínico', description: 'Registre un paciente en el sistema activo. Si el CUI ya existe, se actualizará su expediente.', action: 'Nuevo registro' },
  histories: { title: 'Historial clínico', emptyTitle: 'Seleccione un paciente para consultar su historial', description: 'Las consultas, diagnósticos y recetas se muestran en orden cronológico.', action: 'Buscar paciente' },
  appointments: { title: 'Citas', emptyTitle: 'Programación de citas', description: 'Programe una atención con fecha y servicio.', action: 'Programar cita' },
  consultations: { title: 'Consultas', emptyTitle: 'Consultas del paciente', description: 'Cada consulta forma parte del historial clínico y sirve de base para diagnósticos y recetas.', action: 'Registrar consulta' },
  diagnoses: { title: 'Diagnósticos', emptyTitle: 'Diagnósticos clínicos', description: 'El diagnóstico se asocia a una consulta existente del paciente (código CIE-10).', action: 'Agregar diagnóstico' },
  treatments: { title: 'Tratamientos', emptyTitle: 'Planes de tratamiento', description: 'Primero registre un diagnóstico; después vincule el plan a su consulta.', action: 'Indicar tratamiento' },
  prescriptions: { title: 'Recetas', emptyTitle: 'Recetas y medicamentos', description: 'La receta se asocia a una consulta existente con dosis, frecuencia y duración.', action: 'Crear receta' },
  procedures: { title: 'Procedimientos odontológicos', emptyTitle: 'Procedimientos odontológicos', description: 'Seleccione una atención y registre el procedimiento y la pieza tratada.', action: 'Registrar procedimiento' },
  'lab-orders': { title: 'Órdenes de examen', emptyTitle: 'Órdenes de examen', description: 'La orden se guarda pendiente hasta registrar resultados.', action: 'Crear orden' },
  'lab-results': { title: 'Resultados de laboratorio', emptyTitle: 'Resultados de laboratorio', description: 'Seleccione una orden y registre un parámetro medido.', action: 'Registrar resultado' },
  growth: { title: 'Control de crecimiento', emptyTitle: 'Controles de crecimiento', description: 'Registre medidas estructuradas para seguir su evolución.', action: 'Registrar control' },
  vaccines: { title: 'Vacunación', emptyTitle: 'Registro de vacunación', description: 'Registre cada dosis aplicada en el historial.', action: 'Registrar vacuna' },
  archive: { title: 'Archivo clínico', emptyTitle: 'Archivado de historial', description: 'Da de baja administrativa el expediente del paciente cargado; se conserva para consulta.', action: 'Solicitar archivado' },
}
