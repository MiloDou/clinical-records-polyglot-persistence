"""Persistencia pediátrica sobre el esquema MySQL normalizado de Entrega 01."""

import os
from contextlib import contextmanager
from datetime import date, datetime
from typing import Any, List, Optional

import mysql.connector
from mysql.connector import Error, IntegrityError
from core.errors import ClinicalConflictError

from core.models import (
    CitaCambioIn, CitaIn, ConsultaIn, ConsultaOut, ControlCrecimientoIn, DiagnosticoIn, DiagnosticoOut,
    HistorialOut, PacienteIn, PacienteOut, RecetaIn, RecetaOut, TratamientoIn,
    VacunaAplicadaIn,
)


class PediatriaMysqlAdapter:
    def __init__(self):
        self.config = dict(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DB", "pediatria_db"),
            charset="utf8mb4",
        )

    @contextmanager
    def _connection(self):
        try:
            conn = mysql.connector.connect(**self.config)
        except Error as e:
            raise ConnectionError(f"MySQL no disponible: {e}") from None
        try:
            yield conn
            conn.commit()
        except IntegrityError as e:
            conn.rollback()
            if e.errno == 1452:
                raise ValueError("Paciente o consulta referenciada no existe") from None
            raise
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _patient(row):
        return PacienteOut(
            id_paciente=str(row["id_paciente"]), nombre=row["nombre_paciente"],
            dpi=row["dpi_cui"], fecha_nacimiento=str(row["fecha_nacimiento"]),
            telefono=row.get("telefono_paciente"), genero=row.get("genero"),
            tutor_nombre=row.get("tutor_nombre"), tutor_telefono=row.get("tutor_telefono"),
            estado=row.get("estado") or "activo", fecha_registro=str(row.get("fecha_registro") or ""),
        )

    @staticmethod
    def _assert_active(cur, id_paciente=None, id_consulta=None):
        if id_consulta is not None:
            cur.execute("""
                SELECT p.estado FROM paciente p
                JOIN consulta_pediatrica c ON c.id_paciente=p.id_paciente
                WHERE c.id_consulta=%s
            """, (int(id_consulta),))
        else:
            cur.execute("SELECT estado FROM paciente WHERE id_paciente=%s", (int(id_paciente),))
        row = cur.fetchone()
        if not row:
            raise ValueError("Paciente o consulta no encontrado")
        if row["estado"] != "activo":
            raise ClinicalConflictError("El historial está archivado y no admite nuevos registros")

    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT estado FROM paciente WHERE dpi_cui=%s", (datos.dpi,))
            existing = cur.fetchone()
            if existing and existing["estado"] != "activo":
                raise ClinicalConflictError("El historial está archivado y no se puede reactivar desde el registro")
            if not existing and not datos.tutor_nombre:
                raise ValueError("El expediente pediátrico requiere el nombre de un tutor responsable")
            cur.execute("""
                INSERT INTO paciente (nombre_paciente, dpi_cui, fecha_nacimiento, genero,
                                      telefono_paciente, tutor_nombre, tutor_telefono, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo')
                ON DUPLICATE KEY UPDATE nombre_paciente=VALUES(nombre_paciente),
                    telefono_paciente=VALUES(telefono_paciente),
                    tutor_nombre=COALESCE(VALUES(tutor_nombre), tutor_nombre),
                    tutor_telefono=COALESCE(VALUES(tutor_telefono), tutor_telefono), estado='activo'
            """, (datos.nombre, datos.dpi, datos.fecha_nacimiento, datos.genero,
                  datos.telefono, datos.tutor_nombre, datos.tutor_telefono))
            cur.execute("SELECT * FROM paciente WHERE dpi_cui=%s", (datos.dpi,))
            return self._patient(cur.fetchone())

    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM paciente WHERE dpi_cui=%s", (dpi,))
            row = cur.fetchone()
            return self._patient(row) if row else None

    def buscar_pacientes_por_nombre(self, nombre: str) -> List[PacienteOut]:
        termino = f"%{' '.join(nombre.split())}%"
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM paciente WHERE nombre_paciente LIKE %s ORDER BY nombre_paciente LIMIT 25",
                (termino,),
            )
            return [self._patient(row) for row in cur.fetchall()]

    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        fecha = datos.fecha or datetime.now()
        profesional = datos.profesional or "Profesional tratante"
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            self._assert_active(cur, id_paciente=datos.id_paciente)
            cur.execute("""
                INSERT INTO consulta_pediatrica
                    (id_paciente, fecha_consulta, nombre_medico, motivo, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(datos.id_paciente), fecha, profesional, datos.motivo, datos.observaciones))
            cid = cur.lastrowid
        return ConsultaOut(id_consulta=str(cid), id_paciente=str(datos.id_paciente),
                           fecha=str(fecha), motivo=datos.motivo,
                           profesional=profesional, observaciones=datos.observaciones)

    def registrar_cita(self, datos: CitaIn) -> dict:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            self._assert_active(cur, id_paciente=datos.id_paciente)
            cur.execute("""
                INSERT INTO cita_pediatrica (id_paciente, fecha, servicio, notas)
                VALUES (%s, %s, %s, %s)
            """, (int(datos.id_paciente), datos.fecha, datos.servicio, datos.notas))
            cid = cur.lastrowid
        return {"id_cita": cid, "id_paciente": datos.id_paciente,
                "fecha": str(datos.fecha), "servicio": datos.servicio, "estado": "programada"}

    def cambiar_cita(self, id_cita: Any, datos: CitaCambioIn) -> dict:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id_paciente FROM cita_pediatrica WHERE id_cita=%s", (int(id_cita),))
            cita = cur.fetchone()
            if not cita:
                raise ValueError(f"Cita con id {id_cita} no encontrada")
            self._assert_active(cur, id_paciente=cita["id_paciente"])
            cur.execute("""
                UPDATE cita_pediatrica SET fecha=COALESCE(%s, fecha),
                    estado=COALESCE(%s, estado) WHERE id_cita=%s
            """, (datos.fecha, datos.estado, int(id_cita)))
            if cur.rowcount == 0:
                raise ValueError(f"Cita con id {id_cita} no encontrada")
            cur.execute("SELECT * FROM cita_pediatrica WHERE id_cita=%s", (int(id_cita),))
            row = cur.fetchone()
        return {"id_cita": row["id_cita"], "id_paciente": row["id_paciente"],
                "fecha": str(row["fecha"]), "servicio": row["servicio"], "estado": row["estado"]}

    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            self._assert_active(cur, id_consulta=datos.id_consulta)
            cur.execute("""
                INSERT INTO diagnostico (id_consulta, codigo_cie10, descripcion)
                VALUES (%s, %s, %s)
            """, (int(datos.id_consulta), datos.codigo_cie10, datos.descripcion))
            did = cur.lastrowid
        return DiagnosticoOut(id_diagnostico=str(did), id_consulta=str(datos.id_consulta),
                              descripcion=datos.descripcion, codigo_cie10=datos.codigo_cie10)

    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            self._assert_active(cur, id_consulta=datos.id_consulta)
            cur.execute("""
                INSERT INTO receta (id_consulta, medicamento, dosis, frecuencia, duracion_dias)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(datos.id_consulta), datos.medicamento, datos.dosis,
                  datos.frecuencia, datos.duracion_dias))
            rid = cur.lastrowid
        return RecetaOut(id_receta=str(rid), id_consulta=str(datos.id_consulta),
                         medicamento=datos.medicamento, dosis=datos.dosis,
                         frecuencia=datos.frecuencia, duracion_dias=datos.duracion_dias)

    def registrar_tratamiento(self, datos: TratamientoIn) -> dict:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            self._assert_active(cur, id_consulta=datos.id_consulta)
            cur.execute("SELECT id_diagnostico FROM diagnostico WHERE id_consulta=%s ORDER BY id_diagnostico DESC LIMIT 1", (int(datos.id_consulta),))
            diag = cur.fetchone()
            if not diag:
                raise ClinicalConflictError("Registre un diagnóstico antes del tratamiento")
            cur.execute("""
                INSERT INTO tratamiento_pediatrico
                    (id_diagnostico, descripcion, indicaciones, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s, %s, %s)
            """, (diag["id_diagnostico"], datos.descripcion, datos.indicaciones,
                  datos.fecha_inicio or date.today(), datos.fecha_fin))
            tid = cur.lastrowid
        return {"id_tratamiento": tid, "id_consulta": datos.id_consulta,
                "descripcion": datos.descripcion, "indicaciones": datos.indicaciones}

    def registrar_control(self, datos: ControlCrecimientoIn) -> dict:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            self._assert_active(cur, id_paciente=datos.id_paciente)
            cur.execute("""
                INSERT INTO control_crecimiento
                    (id_paciente, fecha_control, peso_kg, talla_cm, perimetro_cefalico_cm)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(datos.id_paciente), datos.fecha_control or date.today(),
                  datos.peso_kg, datos.talla_cm, datos.perimetro_cefalico_cm))
            cid = cur.lastrowid
        return {"id_control": cid, **datos.model_dump(mode="json")}

    def registrar_vacuna(self, datos: VacunaAplicadaIn) -> dict:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            self._assert_active(cur, id_paciente=datos.id_paciente)
            cur.execute("""
                INSERT INTO vacuna_aplicada
                    (id_paciente, nombre_vacuna, fecha_aplicacion, dosis, lote)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(datos.id_paciente), datos.nombre_vacuna,
                  datos.fecha_aplicacion or date.today(), datos.dosis, datos.lote))
            vid = cur.lastrowid
        return {"id_vacuna": vid, **datos.model_dump(mode="json")}

    def get_historial(self, id_paciente: Any) -> HistorialOut:
        with self._connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM paciente WHERE id_paciente=%s", (int(id_paciente),))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Paciente con id {id_paciente} no encontrado")
            pid = row["id_paciente"]
            cur.execute("SELECT * FROM consulta_pediatrica WHERE id_paciente=%s ORDER BY fecha_consulta DESC", (pid,))
            consultations = cur.fetchall()
            cur.execute("""
                SELECT d.* FROM diagnostico d JOIN consulta_pediatrica c USING (id_consulta)
                WHERE c.id_paciente=%s ORDER BY d.id_diagnostico DESC
            """, (pid,))
            diagnoses = cur.fetchall()
            cur.execute("""
                SELECT r.* FROM receta r JOIN consulta_pediatrica c USING (id_consulta)
                WHERE c.id_paciente=%s ORDER BY r.id_receta DESC
            """, (pid,))
            prescriptions = cur.fetchall()
            cur.execute("""
                SELECT t.*, d.id_consulta FROM tratamiento_pediatrico t
                JOIN diagnostico d USING (id_diagnostico)
                JOIN consulta_pediatrica c ON c.id_consulta=d.id_consulta
                WHERE c.id_paciente=%s ORDER BY t.id_tratamiento DESC
            """, (pid,))
            treatments = cur.fetchall()
            cur.execute("SELECT * FROM control_crecimiento WHERE id_paciente=%s ORDER BY fecha_control DESC", (pid,))
            growth = cur.fetchall()
            cur.execute("SELECT * FROM vacuna_aplicada WHERE id_paciente=%s ORDER BY fecha_aplicacion DESC", (pid,))
            vaccines = cur.fetchall()
            cur.execute("SELECT * FROM cita_pediatrica WHERE id_paciente=%s ORDER BY fecha DESC", (pid,))
            appointments = cur.fetchall()

        return HistorialOut(
            paciente=self._patient(row),
            citas=[dict(a, fecha=str(a["fecha"])) for a in appointments],
            consultas=[dict(id_consulta=str(c["id_consulta"]), id_paciente=str(pid),
                            fecha=str(c["fecha_consulta"]), motivo=c["motivo"],
                            profesional=c["nombre_medico"], observaciones=c["observaciones"])
                       for c in consultations],
            diagnosticos=[dict(id_diagnostico=str(d["id_diagnostico"]),
                               id_consulta=str(d["id_consulta"]), descripcion=d["descripcion"],
                               codigo_cie10=d["codigo_cie10"]) for d in diagnoses],
            recetas=[dict(id_receta=str(r["id_receta"]), id_consulta=str(r["id_consulta"]),
                          medicamento=r["medicamento"], dosis=r["dosis"],
                          frecuencia=r["frecuencia"], duracion_dias=r["duracion_dias"])
                     for r in prescriptions],
            tratamientos=[dict(t, fecha_inicio=str(t["fecha_inicio"]),
                               fecha_fin=str(t["fecha_fin"]) if t["fecha_fin"] else None)
                          for t in treatments],
            controles_crecimiento=[dict(g, fecha_control=str(g["fecha_control"])) for g in growth],
            vacunas=[dict(v, fecha_aplicacion=str(v["fecha_aplicacion"])) for v in vaccines],
        )

    def archivar_historial(self, id_paciente: Any) -> bool:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE paciente SET estado='archivado' WHERE id_paciente=%s", (int(id_paciente),))
            return cur.rowcount > 0
