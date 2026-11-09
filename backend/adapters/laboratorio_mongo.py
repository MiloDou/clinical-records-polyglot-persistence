import os
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId
import pymongo
from pymongo.errors import PyMongoError

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
    ResultadoLaboratorioIn,
    TratamientoIn,
)
from domain.ports import IRepository
from core.errors import ClinicalConflictError


class LaboratorioMongoAdapter(IRepository):
    """
    Adaptador de Persistencia Documental para el Laboratorio Clínico usando MongoDB.
    Decisión de modelado según Plan Maestro:
    - Colección 'pacientes': documento separado
    - Colección 'ordenes': con array 'examenes' embebido
      - Dentro de cada examen: array 'resultados_parametros' embebido
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
    ):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGO_DB", "laboratorio_db")
        self.client: Optional[pymongo.MongoClient] = None
        self.db = None

    def _get_db(self):
        """
        Devuelve la base de datos viva. Si mongod no responde lanza ConnectionError,
        que el manejador global de FastAPI traduce a HTTP 503. Sin respaldo en memoria.
        """
        try:
            if self.client is None:
                self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=1500)
            self.client.admin.command("ping")
        except PyMongoError as e:
            self.client = None
            self.db = None
            raise ConnectionError("MongoDB no disponible; revise el servicio y la configuración de conexión") from None
        if self.db is None:
            self.db = self.client[self.db_name]
        return self.db

    @property
    def col_pacientes(self):
        return self._get_db()["pacientes"]

    @property
    def col_ordenes(self):
        return self._get_db()["ordenes"]

    @staticmethod
    def _id_query(value: Any) -> Dict[str, Any]:
        s = str(value)
        return {"_id": ObjectId(s)} if ObjectId.is_valid(s) else {"_id": s}

    def _assert_active(self, id_paciente: Any = None, id_consulta: Any = None):
        if id_consulta is not None:
            order = self.col_ordenes.find_one(self._id_query(id_consulta))
            if not order:
                raise ValueError(f"Orden/consulta con id {id_consulta} no encontrada")
            id_paciente = order["id_paciente"]
        patient = self.col_pacientes.find_one(self._id_query(id_paciente))
        if not patient:
            raise ValueError(f"Paciente con id {id_paciente} no encontrado")
        if patient.get("estado", "activo") != "activo":
            raise ClinicalConflictError("El historial está archivado y no admite nuevos registros")

    # 1. Registrar paciente
    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        existing = self.col_pacientes.find_one({"dpi": datos.dpi.strip()})
        if existing:
            if existing.get("estado", "activo") != "activo":
                raise ClinicalConflictError("El historial está archivado y no se puede reactivar desde el registro")
            self.col_pacientes.update_one(
                {"_id": existing["_id"]},
                {"$set": {"nombre": datos.nombre, "estado": "activo", "telefono": datos.telefono}}
            )
            doc_id = str(existing.get("_id"))
            return PacienteOut(
                id_paciente=doc_id,
                id=doc_id,
                nombre=datos.nombre,
                dpi=datos.dpi.strip(),
                fecha_nacimiento=str(datos.fecha_nacimiento),
                telefono=datos.telefono,
                genero=datos.genero or existing.get("genero"),
                direccion=datos.direccion or existing.get("direccion"),
                estado="activo",
                fecha_registro=str(existing.get("fecha_registro", date.today())),
            )

        doc = {
            "nombre": datos.nombre,
            "dpi": datos.dpi.strip(),
            "fecha_nacimiento": str(datos.fecha_nacimiento),
            "telefono": datos.telefono,
            "genero": datos.genero or "No especificado",
            "direccion": datos.direccion or "",
            "estado": "activo",
            "fecha_registro": str(date.today()),
        }
        res = self.col_pacientes.insert_one(doc)
        doc_id = str(res.inserted_id)

        return PacienteOut(
            id_paciente=doc_id,
            id=doc_id,
            nombre=doc["nombre"],
            dpi=doc["dpi"],
            fecha_nacimiento=doc["fecha_nacimiento"],
            telefono=doc["telefono"],
            genero=doc["genero"],
            direccion=doc["direccion"],
            estado=doc["estado"],
            fecha_registro=doc["fecha_registro"],
        )

    # 2. Buscar paciente por DPI
    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        doc = self.col_pacientes.find_one({"dpi": dpi.strip()})
        if not doc:
            return None
        doc_id = str(doc.get("_id"))
        return PacienteOut(
            id_paciente=doc_id,
            id=doc_id,
            nombre=doc.get("nombre", ""),
            dpi=doc.get("dpi", ""),
            fecha_nacimiento=str(doc.get("fecha_nacimiento", "")),
            telefono=doc.get("telefono"),
            genero=doc.get("genero"),
            direccion=doc.get("direccion"),
            estado=doc.get("estado", "activo"),
            fecha_registro=str(doc.get("fecha_registro", "")),
        )

    def buscar_pacientes_por_nombre(self, nombre: str) -> List[PacienteOut]:
        patron = re.escape(" ".join(nombre.split()))
        docs = self.col_pacientes.find(
            {"nombre": {"$regex": patron, "$options": "i"}}
        ).sort("nombre", 1).limit(25)
        return [PacienteOut(
            id_paciente=str(doc.get("_id")), id=str(doc.get("_id")),
            nombre=doc.get("nombre", ""), dpi=doc.get("dpi", ""),
            fecha_nacimiento=str(doc.get("fecha_nacimiento", "")),
            telefono=doc.get("telefono"), genero=doc.get("genero"),
            direccion=doc.get("direccion"), estado=doc.get("estado", "activo"),
            fecha_registro=str(doc.get("fecha_registro", "")),
        ) for doc in docs]

    # 3. Registrar orden pendiente; los resultados se agregan después de procesar la muestra.
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        self._assert_active(id_paciente=datos.id_paciente)
        now_str = str(datetime.now())
        orden_doc = {
            "id_paciente": str(datos.id_paciente),
            "motivo": datos.motivo,
            "profesional": datos.profesional or "Técnico de Laboratorio",
            "fecha": now_str,
            "examenes": [
                {
                    "nombre_examen": datos.motivo,
                    "estado": "pendiente",
                    "resultados_parametros": [],
                }
            ],
            "diagnosticos": [],
            "recetas": [],
            "tratamientos": [],
        }
        res = self.col_ordenes.insert_one(orden_doc)
        cid = str(res.inserted_id)

        return ConsultaOut(
            id_consulta=cid,
            id=cid,
            id_paciente=str(datos.id_paciente),
            motivo=datos.motivo,
            profesional=orden_doc["profesional"],
            fecha=now_str,
        )

    # 4. Agregar diagnóstico (hallazgo o interpretación de laboratorio)
    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        self._assert_active(id_consulta=datos.id_consulta)
        cid_str = str(datos.id_consulta)
        diag_id = str(ObjectId())
        diag_entry = {
            "id_diagnostico": diag_id,
            "codigo_cie10": datos.codigo_cie10 or "Z00.0",
            "descripcion": datos.descripcion,
            "fecha": str(date.today()),
        }

        query = {"_id": ObjectId(cid_str)} if ObjectId.is_valid(cid_str) else {"_id": cid_str}
        res = self.col_ordenes.update_one(query, {"$push": {"diagnosticos": diag_entry}})
        if res.matched_count == 0:
            raise ValueError(f"Orden/consulta con id {cid_str} no encontrada en Laboratorio")

        return DiagnosticoOut(
            id_diagnostico=diag_id,
            id_consulta=cid_str,
            codigo_cie10=diag_entry["codigo_cie10"],
            descripcion=diag_entry["descripcion"],
            fecha=diag_entry["fecha"],
        )

    # 5. Recetar medicamento (indicaciones terapéuticas o reactivos)
    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        self._assert_active(id_consulta=datos.id_consulta)
        cid_str = str(datos.id_consulta)
        receta_id = str(ObjectId())
        receta_entry = {
            "id_receta": receta_id,
            "medicamento": datos.medicamento,
            "dosis": datos.dosis,
            "frecuencia": datos.frecuencia,
            "duracion_dias": datos.duracion_dias,
        }

        query = {"_id": ObjectId(cid_str)} if ObjectId.is_valid(cid_str) else {"_id": cid_str}
        res = self.col_ordenes.update_one(query, {"$push": {"recetas": receta_entry}})
        if res.matched_count == 0:
            raise ValueError(f"Orden/consulta con id {cid_str} no encontrada en Laboratorio")

        return RecetaOut(
            id_receta=receta_id,
            id_consulta=cid_str,
            medicamento=datos.medicamento,
            dosis=datos.dosis,
            frecuencia=datos.frecuencia,
            duracion_dias=datos.duracion_dias,
        )

    def registrar_tratamiento(self, datos: TratamientoIn) -> dict:
        self._assert_active(id_consulta=datos.id_consulta)
        cid = str(datos.id_consulta)
        entry = {
            "id_tratamiento": str(ObjectId()), "id_consulta": cid,
            "descripcion": datos.descripcion, "indicaciones": datos.indicaciones,
            "fecha_inicio": str(datos.fecha_inicio or date.today()),
            "fecha_fin": str(datos.fecha_fin) if datos.fecha_fin else None,
        }
        result = self.col_ordenes.update_one(self._id_query(cid), {"$push": {"tratamientos": entry}})
        if not result.matched_count:
            raise ValueError(f"Orden/consulta con id {cid} no encontrada")
        return entry

    def registrar_resultados(self, datos: ResultadoLaboratorioIn) -> dict:
        self._assert_active(id_consulta=datos.id_consulta)
        cid = str(datos.id_consulta)
        params = [p.model_dump(mode="json") for p in datos.resultados_parametros]
        result = self.col_ordenes.update_one(
            {**self._id_query(cid), "examenes.0": {"$exists": True}},
            {"$push": {"examenes.0.resultados_parametros": {"$each": params}},
             "$set": {"examenes.0.estado": "con_resultados"}},
        )
        if not result.matched_count:
            raise ValueError(f"Orden/consulta con id {cid} no encontrada")
        return {"id_consulta": cid, "resultados_parametros": params, "estado": "con_resultados"}

    # 6. Obtener historial completo
    def get_historial(self, id_paciente: Any) -> HistorialOut:
        pid_str = str(id_paciente)
        query = {"_id": ObjectId(pid_str)} if ObjectId.is_valid(pid_str) else {"_id": pid_str}
        p_doc = self.col_pacientes.find_one(query)
        if not p_doc:
            # Buscar por id directo
            p_doc = self.col_pacientes.find_one({"id_paciente": pid_str})

        if not p_doc:
            raise ValueError(f"Paciente con id {pid_str} no encontrado en Laboratorio")

        doc_id = str(p_doc.get("_id"))
        paciente = PacienteOut(
            id_paciente=doc_id,
            id=doc_id,
            nombre=p_doc.get("nombre", ""),
            dpi=p_doc.get("dpi", ""),
            fecha_nacimiento=str(p_doc.get("fecha_nacimiento", "")),
            telefono=p_doc.get("telefono"),
            genero=p_doc.get("genero"),
            direccion=p_doc.get("direccion"),
            estado=p_doc.get("estado", "activo"),
            fecha_registro=str(p_doc.get("fecha_registro", "")),
        )

        ordenes = self.col_ordenes.find({"id_paciente": pid_str})
        if not ordenes:
            ordenes = self.col_ordenes.find({"id_paciente": doc_id})

        consultas = []
        diagnosticos = []
        recetas = []
        tratamientos = []
        examenes_laboratorio = []

        for ord_doc in ordenes:
            cid = str(ord_doc.get("_id"))
            consultas.append({
                "id_consulta": cid,
                "id": cid,
                "fecha": ord_doc.get("fecha"),
                "motivo": ord_doc.get("motivo"),
                "profesional": ord_doc.get("profesional"),
            })
            for d in ord_doc.get("diagnosticos", []):
                diagnosticos.append({
                    "id_diagnostico": d.get("id_diagnostico"),
                    "id_consulta": cid,
                    "codigo_cie10": d.get("codigo_cie10"),
                    "descripcion": d.get("descripcion"),
                    "fecha": d.get("fecha"),
                })
            for r in ord_doc.get("recetas", []):
                recetas.append({
                    "id_receta": r.get("id_receta"),
                    "id_consulta": cid,
                    "medicamento": r.get("medicamento"),
                    "dosis": r.get("dosis"),
                    "frecuencia": r.get("frecuencia"),
                    "duracion_dias": r.get("duracion_dias"),
                })
            tratamientos.extend(ord_doc.get("tratamientos", []))
            for ex in ord_doc.get("examenes", []):
                examenes_laboratorio.append({
                    "id_consulta": cid,
                    "nombre_examen": ex.get("nombre_examen"),
                    "estado": ex.get("estado"),
                    "resultados_parametros": ex.get("resultados_parametros", []),
                })

        return HistorialOut(
            paciente=paciente,
            consultas=consultas,
            diagnosticos=diagnosticos,
            recetas=recetas,
            tratamientos=tratamientos,
            examenes_laboratorio=examenes_laboratorio,
        )

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        pid_str = str(id_paciente)
        query = {"_id": ObjectId(pid_str)} if ObjectId.is_valid(pid_str) else {"_id": pid_str}
        res = self.col_pacientes.update_one(query, {"$set": {"estado": "archivado"}})
        return res.matched_count > 0 or res.modified_count > 0
