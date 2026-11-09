from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    nombre: str = Field(min_length=2, max_length=120)
    dpi: str = Field(min_length=13, max_length=13)
    fecha_nacimiento: Union[date, str]
    telefono: Optional[str] = None
    genero: Optional[str] = "No especificado"
    direccion: Optional[str] = None
    tutor_nombre: Optional[str] = None
    tutor_telefono: Optional[str] = None

    @field_validator("nombre", mode="before")
    @classmethod
    def normalize_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @field_validator("dpi", mode="before")
    @classmethod
    def normalize_cui(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        compact = re.sub(r"[ .-]", "", value.strip())
        if not re.fullmatch(r"[0-9]{13}", compact):
            raise ValueError("El CUI debe contener exactamente 13 dígitos")
        return compact

    @field_validator("fecha_nacimiento", mode="before")
    @classmethod
    def validate_birth_date(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Use una fecha de nacimiento válida") from exc
        if isinstance(value, date) and value > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        return value

    @field_validator("telefono", "tutor_telefono", mode="before")
    @classmethod
    def normalize_guatemala_phone(cls, value: Any) -> Any:
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            value = str(value)
        digits = re.sub(r"\D", "", value)
        if digits.startswith("502") and len(digits) == 11:
            digits = digits[3:]
        if len(digits) != 8:
            raise ValueError("El teléfono debe contener 8 dígitos, opcionalmente con prefijo 502")
        return digits


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


class CitaIn(BaseSchema):
    id_paciente: Any
    fecha: datetime
    servicio: str = Field(min_length=2, max_length=200)
    notas: Optional[str] = None


class CitaCambioIn(BaseSchema):
    fecha: Optional[datetime] = None
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def valid_estado(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in {"programada", "cancelada"}:
            raise ValueError("Estado de cita inválido")
        return value


class DiagnosticoIn(BaseSchema):
    id_consulta: Any
    descripcion: str = Field(min_length=2, max_length=500)
    codigo_cie10: str = Field(min_length=3, max_length=10)


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


class TratamientoIn(BaseSchema):
    id_consulta: Any
    descripcion: str = Field(min_length=2, max_length=300)
    indicaciones: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class EncuentroHospitalIn(BaseSchema):
    """Flujo hospitalario completo guardado en una sola transacción SQL."""
    id_paciente: Any
    fecha: datetime
    motivo: str = Field(min_length=2, max_length=300)
    observaciones: Optional[str] = None
    codigo_cie10: str = Field(min_length=3, max_length=10)
    diagnostico: str = Field(min_length=2, max_length=500)
    tratamiento: str = Field(min_length=2, max_length=300)
    indicaciones: Optional[str] = None
    medicamento: str = Field(min_length=2, max_length=150)
    dosis: str = Field(min_length=1, max_length=20)
    frecuencia: str = Field(min_length=1, max_length=20)
    duracion_dias: int = Field(gt=0, le=3650)


class ResultadoParametro(BaseSchema):
    parametro: str = Field(min_length=1, max_length=100)
    valor: str = Field(min_length=1, max_length=100)
    unidad: Optional[str] = None
    rango_referencia: Optional[str] = None


class ResultadoLaboratorioIn(BaseSchema):
    id_consulta: Any
    resultados_parametros: List[ResultadoParametro] = Field(min_length=1)


class ProcedimientoDentalIn(BaseSchema):
    id_consulta: Any
    pieza: str = Field(min_length=1, max_length=40)
    procedimiento: str = Field(min_length=2, max_length=200)
    notas: Optional[str] = None


class ControlCrecimientoIn(BaseSchema):
    id_paciente: Any
    peso_kg: float = Field(gt=0, le=500)
    talla_cm: float = Field(gt=0, le=300)
    perimetro_cefalico_cm: Optional[float] = Field(default=None, gt=0, le=100)
    fecha_control: Optional[date] = None


class VacunaAplicadaIn(BaseSchema):
    id_paciente: Any
    nombre_vacuna: str = Field(min_length=2, max_length=100)
    dosis: str = Field(min_length=1, max_length=50)
    lote: Optional[str] = Field(default=None, max_length=50)
    fecha_aplicacion: Optional[date] = None


class HistorialOut(BaseSchema):
    paciente: PacienteOut
    consultas: List[Any] = Field(default_factory=list)
    citas: List[Any] = Field(default_factory=list)
    diagnosticos: List[Any] = Field(default_factory=list)
    recetas: List[Any] = Field(default_factory=list)
    tratamientos: List[Any] = Field(default_factory=list)
    examenes_laboratorio: List[Any] = Field(default_factory=list)
    controles_crecimiento: List[Any] = Field(default_factory=list)
    vacunas: List[Any] = Field(default_factory=list)
    procedimientos_dentales: List[Any] = Field(default_factory=list)

