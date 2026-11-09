from typing import Any, List, Optional, Protocol
from core.models import (
    ConsultaIn,
    ConsultaOut,
    CitaIn,
    CitaCambioIn,
    DiagnosticoIn,
    DiagnosticoOut,
    HistorialOut,
    PacienteIn,
    PacienteOut,
    RecetaIn,
    RecetaOut,
    TratamientoIn,
)


class IRepository(Protocol):
    """
    Contrato Hexagonal (Puerto) para persistencia políglota de historiales clínicos.
    Debe ser implementado de forma equivalente por cada adaptador de motor:
    - PostgreSQL (Hospital General)
    - MongoDB (Laboratorio Clínico)
    - MySQL (Centro Médico Pediátrico)
    - Firebase Firestore (Clínica Odontológica)
    """

    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        """Registra un nuevo paciente en la base de datos."""
        ...

    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        """Busca un paciente activo o registrado por su DPI/CUI."""
        ...

    def buscar_pacientes_por_nombre(self, nombre: str) -> List[PacienteOut]:
        """Busca hasta 25 pacientes por coincidencia parcial de nombre."""
        ...

    def get_historial(self, id_paciente: Any) -> HistorialOut:
        """Obtiene el historial clínico completo del paciente (consultas, diagnósticos, recetas, etc.)."""
        ...

    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        """Registra una consulta médica u orden de atención vinculada al paciente."""
        ...

    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        """Asocia un diagnóstico clínico a una consulta previa."""
        ...

    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        """Registra una prescripción farmacológica para la consulta."""
        ...

    def registrar_tratamiento(self, datos: TratamientoIn) -> dict:
        """Asocia un plan de tratamiento a una consulta con diagnóstico."""
        ...

    def registrar_cita(self, datos: CitaIn) -> dict:
        """Agenda una cita sin crear una consulta clínica."""
        ...

    def cambiar_cita(self, id_cita: Any, datos: CitaCambioIn) -> dict:
        """Reprograma o cancela una cita existente."""
        ...

    def archivar_historial(self, id_paciente: Any) -> bool:
        """Cambia el estado del paciente o expediente a 'archivado' (baja administrativa)."""
        ...

