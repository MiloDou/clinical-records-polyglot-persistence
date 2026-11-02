import os
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

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


class OdontologiaFirebaseAdapter(IRepository):
    """
    Adaptador de Persistencia para la Clínica Odontológica usando Firebase Firestore.
    Cumple con el contrato IRepository.
    Colecciones Firestore:
    - /pacientes/{id}
    - /atenciones/{id} (incluye diagnosticos[], procedimientos[], recetas[])
    Si serviceAccountKey.json no está presente aún, opera con persistencia documental equivalente.
    """

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv(
            "FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json"
        )
        self.db = None
        self._is_live = False
        
        # Almacén de colecciones en memoria si Firebase no tiene credenciales configuradas
        self._store_pacientes: Dict[str, Dict[str, Any]] = {}
        self._store_atenciones: Dict[str, Dict[str, Any]] = {}

        self._init_firebase()

    def _init_firebase(self):
        if os.path.exists(self.credentials_path):
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore

                if not firebase_admin._apps:
                    cred = credentials.Certificate(self.credentials_path)
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self._is_live = True
                print("[OdontologiaFirebaseAdapter] Conectado exitosamente a Firebase Firestore.")
            except Exception as e:
                print(f"[OdontologiaFirebaseAdapter] No se pudo inicializar Firebase Admin SDK: {e}. Usando emulador documental.")
                self._is_live = False
        else:
            print("[OdontologiaFirebaseAdapter] serviceAccountKey.json no encontrado. Usando emulador documental para Odontología.")

    # 1. Registrar paciente
    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        existing = self.buscar_paciente(datos.dpi)
        if existing:
            return existing

        doc_id = str(uuid.uuid4())[:8]
        data = {
            "nombre": datos.nombre,
            "dpi": datos.dpi.strip(),
            "fecha_nacimiento": str(datos.fecha_nacimiento),
            "telefono": datos.telefono,
            "genero": datos.genero or "No especificado",
            "direccion": datos.direccion or "",
            "estado": "activo",
            "fecha_registro": str(date.today()),
        }

        if self._is_live and self.db:
            doc_ref = self.db.collection("pacientes").document(doc_id)
            doc_ref.set(data)
        else:
            data["id"] = doc_id
            self._store_pacientes[doc_id] = data

        return PacienteOut(
            id_paciente=doc_id,
            id=doc_id,
            nombre=data["nombre"],
            dpi=data["dpi"],
            fecha_nacimiento=data["fecha_nacimiento"],
            telefono=data["telefono"],
            genero=data["genero"],
            direccion=data["direccion"],
            estado=data["estado"],
            fecha_registro=data["fecha_registro"],
        )

    # 2. Buscar paciente por DPI
    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        target_dpi = dpi.strip()
        if self._is_live and self.db:
            docs = self.db.collection("pacientes").where("dpi", "==", target_dpi).limit(1).stream()
            for doc in docs:
                d = doc.to_dict()
                return PacienteOut(
                    id_paciente=doc.id,
                    id=doc.id,
                    nombre=d.get("nombre", ""),
                    dpi=d.get("dpi", ""),
                    fecha_nacimiento=str(d.get("fecha_nacimiento", "")),
                    telefono=d.get("telefono"),
                    genero=d.get("genero"),
                    direccion=d.get("direccion"),
                    estado=d.get("estado", "activo"),
                    fecha_registro=str(d.get("fecha_registro", "")),
                )
            return None
        else:
            for pid, d in self._store_pacientes.items():
                if d.get("dpi") == target_dpi:
                    return PacienteOut(
                        id_paciente=pid,
                        id=pid,
                        nombre=d.get("nombre", ""),
                        dpi=d.get("dpi", ""),
                        fecha_nacimiento=str(d.get("fecha_nacimiento", "")),
                        telefono=d.get("telefono"),
                        genero=d.get("genero"),
                        direccion=d.get("direccion"),
                        estado=d.get("estado", "activo"),
                        fecha_registro=str(d.get("fecha_registro", "")),
                    )
            return None

    # 3. Registrar consulta / atención odontológica
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        cid = str(uuid.uuid4())[:8]
        now_str = str(datetime.now())
        data = {
            "id_atencion": cid,
            "id_paciente": str(datos.id_paciente),
            "motivo": datos.motivo,
            "profesional": datos.profesional or "Dra. Odontóloga",
            "fecha": now_str,
            "procedimientos": [
                {
                    "pieza_dental": "General / Cavidad oral",
                    "procedimiento": datos.motivo,
                }
            ],
            "diagnosticos": [],
            "recetas": [],
        }

        if self._is_live and self.db:
            self.db.collection("atenciones").document(cid).set(data)
        else:
            self._store_atenciones[cid] = data

        return ConsultaOut(
            id_consulta=cid,
            id=cid,
            id_paciente=datos.id_paciente,
            motivo=datos.motivo,
            profesional=data["profesional"],
            fecha=now_str,
        )

    # 4. Agregar diagnóstico dental
    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        cid = str(datos.id_consulta)
        diag_id = str(uuid.uuid4())[:8]
        diag_data = {
            "id_diagnostico": diag_id,
            "codigo_cie10": datos.codigo_cie10 or "K02.9",
            "descripcion": datos.descripcion,
            "fecha": str(date.today()),
        }

        if self._is_live and self.db:
            from firebase_admin import firestore
            doc_ref = self.db.collection("atenciones").document(cid)
            doc_ref.update({"diagnosticos": firestore.ArrayUnion([diag_data])})
        else:
            if cid in self._store_atenciones:
                self._store_atenciones[cid].setdefault("diagnosticos", []).append(diag_data)

        return DiagnosticoOut(
            id_diagnostico=diag_id,
            id_consulta=cid,
            codigo_cie10=diag_data["codigo_cie10"],
            descripcion=diag_data["descripcion"],
            fecha=diag_data["fecha"],
        )

    # 5. Recetar medicamento
    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        cid = str(datos.id_consulta)
        receta_id = str(uuid.uuid4())[:8]
        receta_data = {
            "id_receta": receta_id,
            "medicamento": datos.medicamento,
            "dosis": datos.dosis,
            "frecuencia": datos.frecuencia,
            "duracion_dias": datos.duracion_dias,
        }

        if self._is_live and self.db:
            from firebase_admin import firestore
            doc_ref = self.db.collection("atenciones").document(cid)
            doc_ref.update({"recetas": firestore.ArrayUnion([receta_data])})
        else:
            if cid in self._store_atenciones:
                self._store_atenciones[cid].setdefault("recetas", []).append(receta_data)

        return RecetaOut(
            id_receta=receta_id,
            id_consulta=cid,
            medicamento=datos.medicamento,
            dosis=datos.dosis,
            frecuencia=datos.frecuencia,
            duracion_dias=datos.duracion_dias,
        )

    # 6. Obtener historial completo
    def get_historial(self, id_paciente: Any) -> HistorialOut:
        pid = str(id_paciente)
        paciente_dict = None

        if self._is_live and self.db:
            doc = self.db.collection("pacientes").document(pid).get()
            if doc.exists:
                paciente_dict = doc.to_dict()
                paciente_dict["id"] = doc.id
        else:
            paciente_dict = self._store_pacientes.get(pid)

        if not paciente_dict:
            raise ValueError(f"Paciente con id {pid} no encontrado en Odontología")

        paciente = PacienteOut(
            id_paciente=pid,
            id=pid,
            nombre=paciente_dict.get("nombre", ""),
            dpi=paciente_dict.get("dpi", ""),
            fecha_nacimiento=str(paciente_dict.get("fecha_nacimiento", "")),
            telefono=paciente_dict.get("telefono"),
            genero=paciente_dict.get("genero"),
            direccion=paciente_dict.get("direccion"),
            estado=paciente_dict.get("estado", "activo"),
            fecha_registro=str(paciente_dict.get("fecha_registro", "")),
        )

        atenciones = []
        if self._is_live and self.db:
            docs = self.db.collection("atenciones").where("id_paciente", "==", pid).stream()
            for d in docs:
                item = d.to_dict()
                item["id_atencion"] = d.id
                atenciones.append(item)
        else:
            for at in self._store_atenciones.values():
                if str(at.get("id_paciente")) == pid:
                    atenciones.append(at)

        consultas = []
        diagnosticos = []
        recetas = []
        procedimientos = []

        for at in atenciones:
            cid = at.get("id_atencion", "")
            consultas.append({
                "id_consulta": cid,
                "id": cid,
                "fecha": at.get("fecha"),
                "motivo": at.get("motivo"),
                "profesional": at.get("profesional"),
            })
            for d in at.get("diagnosticos", []):
                diagnosticos.append({
                    "id_diagnostico": d.get("id_diagnostico"),
                    "id_consulta": cid,
                    "codigo_cie10": d.get("codigo_cie10"),
                    "descripcion": d.get("descripcion"),
                })
            for r in at.get("recetas", []):
                recetas.append({
                    "id_receta": r.get("id_receta"),
                    "id_consulta": cid,
                    "medicamento": r.get("medicamento"),
                    "dosis": r.get("dosis"),
                    "frecuencia": r.get("frecuencia"),
                    "duracion_dias": r.get("duracion_dias"),
                })
            for pr in at.get("procedimientos", []):
                procedimientos.append({
                    "id_consulta": cid,
                    "pieza_dental": pr.get("pieza_dental"),
                    "procedimiento": pr.get("procedimiento"),
                })

        return HistorialOut(
            paciente=paciente,
            consultas=consultas,
            diagnosticos=diagnosticos,
            recetas=recetas,
            procedimientos_dentales=procedimientos,
        )

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        pid = str(id_paciente)
        if self._is_live and self.db:
            doc_ref = self.db.collection("pacientes").document(pid)
            doc_ref.update({"estado": "archivado"})
            return True
        else:
            if pid in self._store_pacientes:
                self._store_pacientes[pid]["estado"] = "archivado"
                return True
            return False
