from typing import Any, Optional, Protocol
from core.models import (
    ConsultaIn,
    ConsultaOut,
    DiagnosticoIn,
    DiagnosticoOut,
    HistorialOut,
    PacienteIn,
    PacienteOut,
    RecetaIn,
    RecetaOut,
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

    def archivar_historial(self, id_paciente: Any) -> bool:
        """Cambia el estado del paciente o expediente a 'archivado' (baja administrativa)."""
        ...
