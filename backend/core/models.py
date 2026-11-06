from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class LoginIn(BaseSchema):
    usuario: str
    password: str


class TokenOut(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    institution: str
    usuario: str
    rol: Optional[str] = None


class PacienteIn(BaseSchema):
    nombre: str
    dpi: str
    fecha_nacimiento: Union[date, str]
    telefono: Optional[str] = None
    genero: Optional[str] = "No especificado"
    direccion: Optional[str] = None
    tutor_nombre: Optional[str] = None
    tutor_telefono: Optional[str] = None


class PacienteOut(BaseSchema):
    id_paciente: Any
    id: Optional[Any] = None
    nombre: str
    dpi: str
    fecha_nacimiento: Union[date, str]
    telefono: Optional[str] = None
    genero: Optional[str] = None
    direccion: Optional[str] = None
    estado: str = "activo"
    tutor_nombre: Optional[str] = None
    tutor_telefono: Optional[str] = None
    fecha_registro: Optional[Union[date, str]] = None

    def model_post_init(self, __context: Any) -> None:
        if self.id is None:
            self.id = self.id_paciente
        if self.id_paciente is None:
            self.id_paciente = self.id


class ConsultaIn(BaseSchema):
    id_paciente: Any
    motivo: str
    profesional: Optional[str] = "Dr. Sistema"
    observaciones: Optional[str] = None
    fecha: Optional[Union[datetime, date, str]] = None


class ConsultaOut(BaseSchema):
    id_consulta: Any
    id: Optional[Any] = None
    id_paciente: Any
    motivo: str
    profesional: Optional[str] = None
    observaciones: Optional[str] = None
    fecha: Optional[Union[datetime, date, str]] = None

    def model_post_init(self, __context: Any) -> None:
        if self.id is None:
            self.id = self.id_consulta
        if self.id_consulta is None:
            self.id_consulta = self.id


class DiagnosticoIn(BaseSchema):
    id_consulta: Any
    descripcion: str
    codigo_cie10: Optional[str] = "Z00.0"


class DiagnosticoOut(BaseSchema):
    id_diagnostico: Optional[Any] = None
    id_consulta: Any
    descripcion: str
    codigo_cie10: Optional[str] = None
    fecha: Optional[Union[date, str]] = None


class RecetaIn(BaseSchema):
    id_consulta: Any
    medicamento: str
    dosis: str
    frecuencia: str
    duracion_dias: int


class RecetaOut(BaseSchema):
    id_receta: Optional[Any] = None
    id_consulta: Any
    medicamento: str
    dosis: str
    frecuencia: str
    duracion_dias: int


class HistorialOut(BaseSchema):
    paciente: PacienteOut
    consultas: List[Any] = Field(default_factory=list)
    diagnosticos: List[Any] = Field(default_factory=list)
    recetas: List[Any] = Field(default_factory=list)
    examenes_laboratorio: List[Any] = Field(default_factory=list)
    controles_crecimiento: List[Any] = Field(default_factory=list)
    vacunas: List[Any] = Field(default_factory=list)
    procedimientos_dentales: List[Any] = Field(default_factory=list)

