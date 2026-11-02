import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

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


class InMemoryMongoCollection:
    """Fallback en memoria con semántica documental MongoDB si mongod no está en ejecución."""
    def __init__(self):
        self.docs: Dict[str, Dict[str, Any]] = {}

    def insert_one(self, doc: Dict[str, Any]):
        new_doc = dict(doc)
        if "_id" not in new_doc:
            new_doc["_id"] = ObjectId()
        oid_str = str(new_doc["_id"])
        self.docs[oid_str] = new_doc
        class Result:
            inserted_id = new_doc["_id"]
        return Result()

    def find_one(self, query: Dict[str, Any]):
        for doc in self.docs.values():
            match = True
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    def find(self, query: Dict[str, Any]):
        results = []
        for doc in self.docs.values():
            match = True
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        match = False
                        break
                elif str(doc.get(k)) != str(v):
                    match = False
                    break
            if match:
                results.append(dict(doc))
        return results

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
        doc = self.find_one(query)
        if not doc:
            class Result:
                matched_count = 0
                modified_count = 0
            return Result()
        
        oid_str = str(doc["_id"])
        target = self.docs[oid_str]
        
        if "$set" in update:
            for k, v in update["$set"].items():
                target[k] = v
        if "$push" in update:
            for k, v in update["$push"].items():
                if k not in target or not isinstance(target[k], list):
                    target[k] = []
                target[k].append(v)
                
        class Result:
            matched_count = 1
            modified_count = 1
        return Result()


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
        self._is_live = False
        
        # In-memory storage si mongod no está disponible
        self._fallback_pacientes = InMemoryMongoCollection()
        self._fallback_ordenes = InMemoryMongoCollection()

        self._connect()

    def _connect(self):
        try:
            client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=1500)
            client.admin.command("ping")
            self.client = client
            self.db = client[self.db_name]
            self._is_live = True
            print(f"[LaboratorioMongoAdapter] Conectado exitosamente a MongoDB en {self.uri}/{self.db_name}")
        except Exception:
            self._is_live = False
            self.db = None
            print(f"[LaboratorioMongoAdapter] MongoDB no disponible en {self.uri}. Operando con motor documental interno.")

    @property
    def col_pacientes(self):
        if self._is_live and self.db is not None:
            return self.db["pacientes"]
        return self._fallback_pacientes

    @property
    def col_ordenes(self):
        if self._is_live and self.db is not None:
            return self.db["ordenes"]
        return self._fallback_ordenes

    # 1. Registrar paciente
    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        existing = self.col_pacientes.find_one({"dpi": datos.dpi.strip()})
        if existing:
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

    # 3. Registrar consulta (orden de examen en laboratorio)
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        now_str = str(datetime.now())
        orden_doc = {
            "id_paciente": str(datos.id_paciente),
            "motivo": datos.motivo,
            "profesional": datos.profesional or "Técnico de Laboratorio",
            "fecha": now_str,
            "examenes": [
                {
                    "nombre_examen": datos.motivo,
                    "estado": "completado",
                    "resultados_parametros": [
                        {
                            "parametro": "Glucosa basal",
                            "valor": "92 mg/dL",
                            "rango_referencia": "70 - 100 mg/dL"
                        },
                        {
                            "parametro": "Hemoglobina",
                            "valor": "14.5 g/dL",
                            "rango_referencia": "13.5 - 17.5 g/dL"
                        }
                    ]
                }
            ],
            "diagnosticos": [],
            "recetas": [],
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
        cid_str = str(datos.id_consulta)
        diag_id = str(ObjectId())
        diag_entry = {
            "id_diagnostico": diag_id,
            "codigo_cie10": datos.codigo_cie10 or "Z00.0",
            "descripcion": datos.descripcion,
            "fecha": str(date.today()),
        }

        query = {"_id": ObjectId(cid_str)} if ObjectId.is_valid(cid_str) else {"_id": cid_str}
        self.col_ordenes.update_one(query, {"$push": {"diagnosticos": diag_entry}})

        return DiagnosticoOut(
            id_diagnostico=diag_id,
            id_consulta=cid_str,
            codigo_cie10=diag_entry["codigo_cie10"],
            descripcion=diag_entry["descripcion"],
            fecha=diag_entry["fecha"],
        )

    # 5. Recetar medicamento (indicaciones terapéuticas o reactivos)
    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
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
        self.col_ordenes.update_one(query, {"$push": {"recetas": receta_entry}})

        return RecetaOut(
            id_receta=receta_id,
            id_consulta=cid_str,
            medicamento=datos.medicamento,
            dosis=datos.dosis,
            frecuencia=datos.frecuencia,
            duracion_dias=datos.duracion_dias,
        )

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
            examenes_laboratorio=examenes_laboratorio,
        )

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        pid_str = str(id_paciente)
        query = {"_id": ObjectId(pid_str)} if ObjectId.is_valid(pid_str) else {"_id": pid_str}
        res = self.col_pacientes.update_one(query, {"$set": {"estado": "archivado"}})
        return res.matched_count > 0 or res.modified_count > 0
