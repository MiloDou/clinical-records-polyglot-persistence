import os
from pathlib import Path
import uuid
from datetime import date, datetime
from typing import Any, Dict, Optional

import functools

import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core import exceptions as gexc
from google.auth import exceptions as gauth_exc
from google.cloud.firestore_v1.base_query import FieldFilter

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
    ProcedimientoDentalIn,
    TratamientoIn,
)
from domain.ports import IRepository
from core.errors import ClinicalConflictError

_APP_NAME = "odontologia"


def _map_google_errors(fn):
    """
    Traduce fallas de Firestore/Google a excepciones del dominio:
      - NotFound                      -> ValueError (HTTP 404)
      - red, credenciales, timeouts   -> ConnectionError (HTTP 503 vía manejador global)
    Los ValueError propios del adaptador (recurso inexistente) pasan intactos.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except gexc.NotFound as e:
            raise ValueError(f"Recurso no encontrado en Firestore: {e.message}") from None
        except (gexc.GoogleAPIError, gauth_exc.GoogleAuthError) as e:
            raise ConnectionError(f"Firebase Firestore no disponible: {e}") from None
    return wrapper


class OdontologiaFirebaseAdapter(IRepository):
    """
    Adaptador de Persistencia Documental para la Clínica Odontológica usando Firebase Firestore.
    Cumple con el contrato IRepository con el siguiente modelado (embedded vs referenced):
      - /pacientes/{id}   -> documento raíz (referenciado)
      - /citas/{id}       -> referencia a paciente + odontólogo
      - /atenciones/{id}  -> referencia a cita; procedimientos[], diagnosticos[] y recetas[] embebidos
    Una "consulta" del contrato equivale a una cita atendida: cita y atención comparten el mismo id.
    """

    def __init__(self, credentials_path: Optional[str] = None, client: Any = None):
        configured = credentials_path or os.getenv(
            "FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json"
        )
        path = Path(configured).expanduser()
        self.credentials_path = str(path if path.is_absolute() else Path(__file__).resolve().parents[1] / path)
        self._db = client

    @property
    def db(self) -> Any:
        """Inicializa firebase-admin de forma perezosa (una sola app con nombre propio)."""
        if self._db is None:
            try:
                try:
                    app = firebase_admin.get_app(_APP_NAME)
                except ValueError:
                    if not os.path.isfile(self.credentials_path):
                        raise ConnectionError(
                            f"Firebase no disponible: no se encontró la credencial en '{self.credentials_path}'"
                        )
                    app = firebase_admin.initialize_app(
                        credentials.Certificate(self.credentials_path), name=_APP_NAME
                    )
                self._db = firestore.client(app)
            except ConnectionError:
                raise
            except Exception as e:
                raise ConnectionError(f"Firebase no se pudo inicializar: {e}") from None
        return self._db

    @staticmethod
    def _fmt_fecha(value: Any) -> Optional[str]:
        """Mismo formato que str(datetime) de los motores SQL: 'YYYY-MM-DD HH:MM:SS'."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None, microsecond=0).isoformat(sep=" ")
        return str(value)

    @staticmethod
    def _to_paciente(doc_id: str, d: Dict[str, Any]) -> PacienteOut:
        return PacienteOut(
            id_paciente=doc_id,
            id=doc_id,
            nombre=d["nombre"],
            dpi=d["dpi"],
            fecha_nacimiento=str(d["fecha_nacimiento"]),
            genero=d.get("genero"),
            telefono=d.get("telefono"),
            direccion=d.get("direccion"),
            estado=d.get("estado", "activo"),
            tutor_nombre=d.get("tutor_nombre"),
            tutor_telefono=d.get("tutor_telefono"),
            fecha_registro=d.get("fecha_registro"),
        )

    def _atencion_ref(self, id_consulta: Any):
        ref = self.db.collection("atenciones").document(str(id_consulta))
        snap = ref.get()
        if not snap.exists:
            raise ValueError(f"Consulta/atención con id {id_consulta} no encontrada")
        self._assert_active(snap.to_dict()["id_paciente"])
        return ref

    def _assert_active(self, id_paciente: Any):
        snap = self.db.collection("pacientes").document(str(id_paciente)).get()
        if not snap.exists:
            raise ValueError(f"Paciente con id {id_paciente} no encontrado")
        if snap.to_dict().get("estado", "activo") != "activo":
            raise ClinicalConflictError("El historial está archivado y no admite nuevos registros")

    def _find_by_dpi(self, dpi: str):
        docs = (
            self.db.collection("pacientes")
            .where(filter=FieldFilter("dpi", "==", dpi))
            .limit(1)
            .get()
        )
        return docs[0] if docs else None

    # 1. Registrar paciente
    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        dpi = datos.dpi.strip()
        existente = self._find_by_dpi(dpi)
        if existente:
            if existente.to_dict().get("estado", "activo") != "activo":
                raise ClinicalConflictError("El historial está archivado y no se puede reactivar desde el registro")
            # Upsert por DPI (equivalente al ON CONFLICT de los motores relacionales)
            existente.reference.update({"nombre": datos.nombre, "estado": "activo"})
            ref = existente.reference
        else:
            ref = self.db.collection("pacientes").document()
            ref.set(
                {
                    "nombre": datos.nombre,
                    "dpi": dpi,
                    "fecha_nacimiento": str(datos.fecha_nacimiento),
                    "genero": datos.genero or "No especificado",
                    "telefono": datos.telefono,
                    "direccion": datos.direccion,
                    "tutor_nombre": datos.tutor_nombre,
                    "tutor_telefono": datos.tutor_telefono,
                    "estado": "activo",
                    "fecha_registro": date.today().isoformat(),
                }
            )
        snap = ref.get()
        return self._to_paciente(snap.id, snap.to_dict())

    # 2. Buscar paciente por DPI
    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        snap = self._find_by_dpi(dpi.strip())
        return self._to_paciente(snap.id, snap.to_dict()) if snap else None

    @_map_google_errors
    def buscar_pacientes_por_nombre(self, nombre: str) -> list[PacienteOut]:
        termino = " ".join(nombre.split()).casefold()
        coincidencias = []
        for snap in self.db.collection("pacientes").stream():
            data = snap.to_dict() or {}
            if termino in str(data.get("nombre", "")).casefold():
                coincidencias.append(self._to_paciente(snap.id, data))
                if len(coincidencias) == 25:
                    break
        return sorted(coincidencias, key=lambda paciente: paciente.nombre.casefold())

    # 3. Registrar consulta (cita + atención en un batch atómico)
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        pid = str(datos.id_paciente)
        paciente_ref = self.db.collection("pacientes").document(pid)
        self._assert_active(pid)

        fecha = self._fmt_fecha(datos.fecha) or self._fmt_fecha(datetime.now())
        profesional = datos.profesional or "Dr. Sistema"

        cita_ref = self.db.collection("citas").document()
        atencion_ref = self.db.collection("atenciones").document(cita_ref.id)

        batch = self.db.batch()
        batch.set(
            cita_ref,
            {
                "id_paciente": pid,
                "paciente_ref": paciente_ref,
                "odontologo": profesional,
                "fecha": fecha,
                "motivo": datos.motivo,
                "estado": "atendida",
            },
        )
        batch.set(
            atencion_ref,
            {
                "id_cita": cita_ref.id,
                "cita_ref": cita_ref,
                "id_paciente": pid,
                "fecha": fecha,
                "observaciones": datos.observaciones,
                "procedimientos": [],
                "diagnosticos": [],
                "recetas": [],
                "tratamientos": [],
            },
        )
        batch.commit()

        return ConsultaOut(
            id_consulta=cita_ref.id,
            id=cita_ref.id,
            id_paciente=pid,
            motivo=datos.motivo,
            profesional=profesional,
            observaciones=datos.observaciones,
            fecha=fecha,
        )

    def registrar_cita(self, datos: CitaIn) -> dict:
        pid = str(datos.id_paciente)
        paciente_ref = self.db.collection("pacientes").document(pid)
        self._assert_active(pid)
        ref = self.db.collection("citas").document()
        ref.set({
            "id_paciente": pid, "paciente_ref": paciente_ref,
            "odontologo": None, "fecha": self._fmt_fecha(datos.fecha),
            "motivo": datos.servicio, "notas": datos.notas, "estado": "programada",
        })
        return {"id_cita": ref.id, "id_paciente": pid,
                "fecha": self._fmt_fecha(datos.fecha), "servicio": datos.servicio,
                "estado": "programada"}

    def cambiar_cita(self, id_cita: Any, datos: CitaCambioIn) -> dict:
        ref = self.db.collection("citas").document(str(id_cita))
        snap = ref.get()
        if not snap.exists:
            raise ValueError(f"Cita con id {id_cita} no encontrada")
        self._assert_active(snap.to_dict()["id_paciente"])
        if snap.to_dict().get("estado") == "atendida":
            raise ClinicalConflictError("Una cita atendida ya no se puede modificar")
        update = {}
        if datos.fecha is not None:
            update["fecha"] = self._fmt_fecha(datos.fecha)
        if datos.estado is not None:
            update["estado"] = datos.estado
        ref.update(update)
        row = {**snap.to_dict(), **update}
        return {"id_cita": str(id_cita), "id_paciente": row["id_paciente"],
                "fecha": row["fecha"], "servicio": row["motivo"], "estado": row["estado"]}

    # 4. Agregar diagnóstico (embebido en la atención)
    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        ref = self._atencion_ref(datos.id_consulta)
        diag = {
            "id_diagnostico": uuid.uuid4().hex,
            "codigo_cie10": (datos.codigo_cie10 or "Z00.0").strip(),
            "descripcion": datos.descripcion,
            "fecha": date.today().isoformat(),
        }
        ref.update({"diagnosticos": firestore.ArrayUnion([diag])})
        return DiagnosticoOut(id_consulta=str(datos.id_consulta), **diag)

    # 5. Recetar medicamento (embebido en la atención)
    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        ref = self._atencion_ref(datos.id_consulta)
        receta = {
            "id_receta": uuid.uuid4().hex,
            "medicamento": datos.medicamento.strip(),
            "dosis": datos.dosis,
            "frecuencia": datos.frecuencia,
            "duracion_dias": datos.duracion_dias,
        }
        ref.update({"recetas": firestore.ArrayUnion([receta])})
        return RecetaOut(id_consulta=str(datos.id_consulta), **receta)

    def registrar_tratamiento(self, datos: TratamientoIn) -> dict:
        ref = self._atencion_ref(datos.id_consulta)
        item = {
            "id_tratamiento": uuid.uuid4().hex,
            "id_consulta": str(datos.id_consulta),
            "descripcion": datos.descripcion,
            "indicaciones": datos.indicaciones,
            "fecha_inicio": str(datos.fecha_inicio or date.today()),
            "fecha_fin": str(datos.fecha_fin) if datos.fecha_fin else None,
        }
        ref.update({"tratamientos": firestore.ArrayUnion([item])})
        return item

    def registrar_procedimiento(self, datos: ProcedimientoDentalIn) -> dict:
        ref = self._atencion_ref(datos.id_consulta)
        item = {
            "id_procedimiento": uuid.uuid4().hex,
            "id_consulta": str(datos.id_consulta),
            "pieza": datos.pieza,
            "procedimiento": datos.procedimiento,
            "notas": datos.notas,
            "fecha": date.today().isoformat(),
        }
        ref.update({"procedimientos": firestore.ArrayUnion([item])})
        return item

    # 6. Obtener historial completo
    def get_historial(self, id_paciente: Any) -> HistorialOut:
        pid = str(id_paciente)
        p_snap = self.db.collection("pacientes").document(pid).get()
        if not p_snap.exists:
            raise ValueError(f"Paciente con id {pid} no encontrado")

        citas = {
            s.id: s.to_dict()
            for s in self.db.collection("citas").where(filter=FieldFilter("id_paciente", "==", pid)).get()
        }
        atenciones = {
            s.id: s.to_dict()
            for s in self.db.collection("atenciones").where(filter=FieldFilter("id_paciente", "==", pid)).get()
        }

        consultas, diagnosticos, recetas, procedimientos, tratamientos = [], [], [], [], []
        citas_out = []
        for cid, cita in sorted(citas.items(), key=lambda kv: kv[1].get("fecha") or "", reverse=True):
            citas_out.append({"id_cita": cid, "id_paciente": pid, "fecha": cita.get("fecha"),
                              "servicio": cita.get("motivo"), "estado": cita.get("estado")})
            if cita.get("estado") != "atendida":
                continue
            at = atenciones.get(cid, {})
            consultas.append(
                {
                    "id_consulta": cid,
                    "id": cid,
                    "fecha": cita.get("fecha"),
                    "motivo": cita.get("motivo"),
                    "profesional": cita.get("odontologo") or "Dr. Sistema",
                    "observaciones": at.get("observaciones"),
                }
            )
            diagnosticos += [{**d, "id_consulta": cid} for d in at.get("diagnosticos", [])]
            recetas += [{**r, "id_consulta": cid} for r in at.get("recetas", [])]
            procedimientos += [{**p, "id_consulta": cid} for p in at.get("procedimientos", [])]
            tratamientos += [{**t, "id_consulta": cid} for t in at.get("tratamientos", [])]

        return HistorialOut(
            paciente=self._to_paciente(p_snap.id, p_snap.to_dict()),
            citas=citas_out,
            consultas=consultas,
            diagnosticos=diagnosticos,
            recetas=recetas,
            procedimientos_dentales=procedimientos,
            tratamientos=tratamientos,
        )

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        ref = self.db.collection("pacientes").document(str(id_paciente))
        if not ref.get().exists:
            return False
        ref.update({"estado": "archivado"})
        return True


# Aplica la traducción de errores a los 7 métodos del contrato IRepository
for _metodo in (
    "registrar_paciente", "buscar_paciente", "buscar_pacientes_por_nombre", "get_historial", "registrar_consulta",
    "registrar_cita", "cambiar_cita",
    "agregar_diagnostico", "recetar_medicamento", "registrar_tratamiento",
    "registrar_procedimiento", "archivar_historial",
):
    setattr(OdontologiaFirebaseAdapter, _metodo,
            _map_google_errors(getattr(OdontologiaFirebaseAdapter, _metodo)))
