import os
import uuid
from datetime import date, datetime
from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

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
from domain.ports import IRepository

_APP_NAME = "odontologia"


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
        self.credentials_path = credentials_path or os.getenv(
            "FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json"
        )
        self._db = client

    @property
    def db(self) -> Any:
        """Inicializa firebase-admin de forma perezosa (una sola app con nombre propio)."""
        if self._db is None:
            try:
                app = firebase_admin.get_app(_APP_NAME)
            except ValueError:
                if not os.path.isfile(self.credentials_path):
                    raise RuntimeError(
                        f"No se encontró la credencial de Firebase en '{self.credentials_path}'"
                    )
                app = firebase_admin.initialize_app(
                    credentials.Certificate(self.credentials_path), name=_APP_NAME
                )
            self._db = firestore.client(app)
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
        if not ref.get().exists:
            raise ValueError(f"Consulta/atención con id {id_consulta} no encontrada")
        return ref

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

    # 3. Registrar consulta (cita + atención en un batch atómico)
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        pid = str(datos.id_paciente)
        paciente_ref = self.db.collection("pacientes").document(pid)
        if not paciente_ref.get().exists:
            raise ValueError(f"Paciente con id {pid} no encontrado")

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

        consultas, diagnosticos, recetas, procedimientos = [], [], [], []
        for cid, cita in sorted(citas.items(), key=lambda kv: kv[1].get("fecha") or "", reverse=True):
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

        return HistorialOut(
            paciente=self._to_paciente(p_snap.id, p_snap.to_dict()),
            consultas=consultas,
            diagnosticos=diagnosticos,
            recetas=recetas,
            procedimientos_dentales=procedimientos,
        )

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        ref = self.db.collection("pacientes").document(str(id_paciente))
        if not ref.get().exists:
            return False
        ref.update({"estado": "archivado"})
        return True
