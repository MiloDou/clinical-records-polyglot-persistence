import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Iterator, Optional

import mysql.connector

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

_PACIENTE_COLS = """
    id_paciente, nombre_paciente, dpi_cui, fecha_nacimiento, genero,
    telefono_paciente, tutor_nombre, tutor_telefono, fecha_registro, estado
"""


class PediatriaMysqlAdapter(IRepository):
    """
    Adaptador de Persistencia Relacional para el Centro Médico Pediátrico usando MySQL 8.
    Cumple con el contrato IRepository sobre la base 'pediatria_db'
    (paciente, consulta_pediatrica, diagnostico, receta, control_crecimiento, vacuna_aplicada).
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.config = {
            "host": host or os.getenv("MYSQL_HOST", "localhost"),
            "port": port or int(os.getenv("MYSQL_PORT", "3306")),
            "user": user or os.getenv("MYSQL_USER", "root"),
            "password": password or os.getenv("MYSQL_PASSWORD", "root"),
            "database": database or os.getenv("MYSQL_DB", "pediatria_db"),
            "autocommit": False,
        }

    @contextmanager
    def _cursor(self) -> Iterator[Any]:
        """Abre conexión + cursor dict; commit al salir, rollback ante error, cierre garantizado."""
        conn = mysql.connector.connect(**self.config)
        cur = conn.cursor(dictionary=True)
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def _to_paciente(row: Dict[str, Any]) -> PacienteOut:
        return PacienteOut(
            id_paciente=row["id_paciente"],
            id=row["id_paciente"],
            nombre=row["nombre_paciente"],
            dpi=row["dpi_cui"],
            fecha_nacimiento=str(row["fecha_nacimiento"]),
            genero=row["genero"],
            telefono=row["telefono_paciente"],
            direccion=None,
            estado=row["estado"] or "activo",
            tutor_nombre=row["tutor_nombre"],
            tutor_telefono=row["tutor_telefono"],
            fecha_registro=str(row["fecha_registro"]) if row["fecha_registro"] else None,
        )

    @staticmethod
    def _float(value: Any) -> Optional[float]:
        return float(value) if value is not None else None

    # 1. Registrar paciente
    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        dpi = datos.dpi.strip()
        with self._cursor() as cur:
            # Upsert por DPI (equivalente al ON CONFLICT del adaptador PostgreSQL)
            cur.execute(
                """
                INSERT INTO paciente (
                    nombre_paciente, dpi_cui, fecha_nacimiento, genero,
                    telefono_paciente, tutor_nombre, tutor_telefono, estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo')
                ON DUPLICATE KEY UPDATE
                    nombre_paciente = VALUES(nombre_paciente),
                    estado = 'activo'
                """,
                (
                    datos.nombre,
                    dpi,
                    str(datos.fecha_nacimiento),
                    datos.genero or "No especificado",
                    datos.telefono,
                    datos.tutor_nombre,
                    datos.tutor_telefono,
                ),
            )
            cur.execute(f"SELECT {_PACIENTE_COLS} FROM paciente WHERE dpi_cui = %s", (dpi,))
            row = cur.fetchone()
        return self._to_paciente(row)

    # 2. Buscar paciente por DPI
    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        with self._cursor() as cur:
            cur.execute(f"SELECT {_PACIENTE_COLS} FROM paciente WHERE dpi_cui = %s", (dpi.strip(),))
            row = cur.fetchone()
        return self._to_paciente(row) if row else None

    # 3. Registrar consulta
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        fecha = datos.fecha or datetime.now().replace(microsecond=0)
        profesional = datos.profesional or "Dr. Sistema"
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO consulta_pediatrica (id_paciente, fecha_consulta, nombre_medico, motivo, observaciones)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (int(datos.id_paciente), fecha, profesional, datos.motivo, datos.observaciones),
            )
            cid = cur.lastrowid
        return ConsultaOut(
            id_consulta=cid,
            id=cid,
            id_paciente=int(datos.id_paciente),
            motivo=datos.motivo,
            profesional=profesional,
            observaciones=datos.observaciones,
            fecha=str(fecha),
        )

    # 4. Agregar diagnóstico
    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        cie10 = (datos.codigo_cie10 or "Z00.0").strip()
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO diagnostico (id_consulta, descripcion, codigo_cie10) VALUES (%s, %s, %s)",
                (int(datos.id_consulta), datos.descripcion, cie10),
            )
            did = cur.lastrowid
            # La tabla no guarda fecha propia: se toma la de la consulta
            cur.execute(
                "SELECT DATE(fecha_consulta) AS fecha FROM consulta_pediatrica WHERE id_consulta = %s",
                (int(datos.id_consulta),),
            )
            row = cur.fetchone()
        return DiagnosticoOut(
            id_diagnostico=did,
            id_consulta=int(datos.id_consulta),
            descripcion=datos.descripcion,
            codigo_cie10=cie10,
            fecha=str(row["fecha"]) if row else None,
        )

    # 5. Recetar medicamento
    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO receta (id_consulta, medicamento, dosis, frecuencia, duracion_dias)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    int(datos.id_consulta),
                    datos.medicamento.strip(),
                    datos.dosis,
                    datos.frecuencia,
                    datos.duracion_dias,
                ),
            )
            rid = cur.lastrowid
        return RecetaOut(
            id_receta=rid,
            id_consulta=int(datos.id_consulta),
            medicamento=datos.medicamento.strip(),
            dosis=datos.dosis,
            frecuencia=datos.frecuencia,
            duracion_dias=datos.duracion_dias,
        )

    # 6. Obtener historial completo
    def get_historial(self, id_paciente: Any) -> HistorialOut:
        pid = int(id_paciente)
        with self._cursor() as cur:
            cur.execute(f"SELECT {_PACIENTE_COLS} FROM paciente WHERE id_paciente = %s", (pid,))
            p_row = cur.fetchone()
            if not p_row:
                raise ValueError(f"Paciente con id {pid} no encontrado")

            cur.execute(
                """
                SELECT id_consulta, id_paciente, fecha_consulta, nombre_medico, motivo, observaciones
                FROM consulta_pediatrica
                WHERE id_paciente = %s
                ORDER BY fecha_consulta DESC
                """,
                (pid,),
            )
            c_rows = cur.fetchall()

            cur.execute(
                """
                SELECT d.id_diagnostico, d.id_consulta, d.codigo_cie10, d.descripcion,
                       DATE(c.fecha_consulta) AS fecha
                FROM diagnostico d
                JOIN consulta_pediatrica c ON d.id_consulta = c.id_consulta
                WHERE c.id_paciente = %s
                ORDER BY c.fecha_consulta DESC
                """,
                (pid,),
            )
            d_rows = cur.fetchall()

            cur.execute(
                """
                SELECT r.id_receta, r.id_consulta, r.medicamento, r.dosis, r.frecuencia, r.duracion_dias
                FROM receta r
                JOIN consulta_pediatrica c ON r.id_consulta = c.id_consulta
                WHERE c.id_paciente = %s
                """,
                (pid,),
            )
            r_rows = cur.fetchall()

            cur.execute(
                """
                SELECT id_control, fecha_control, peso_kg, talla_cm, perimetro_cefalico_cm
                FROM control_crecimiento
                WHERE id_paciente = %s
                ORDER BY fecha_control DESC
                """,
                (pid,),
            )
            g_rows = cur.fetchall()

            cur.execute(
                """
                SELECT id_vacuna, nombre_vacuna, fecha_aplicacion, dosis, lote
                FROM vacuna_aplicada
                WHERE id_paciente = %s
                ORDER BY fecha_aplicacion DESC
                """,
                (pid,),
            )
            v_rows = cur.fetchall()

        consultas = [
            {
                "id_consulta": c["id_consulta"],
                "id": c["id_consulta"],
                "fecha": str(c["fecha_consulta"]),
                "motivo": c["motivo"],
                "profesional": c["nombre_medico"] or "Dr. Sistema",
                "observaciones": c["observaciones"],
            }
            for c in c_rows
        ]

        diagnosticos = [
            {
                "id_diagnostico": d["id_diagnostico"],
                "id_consulta": d["id_consulta"],
                "codigo_cie10": d["codigo_cie10"],
                "descripcion": d["descripcion"],
                "fecha": str(d["fecha"]),
            }
            for d in d_rows
        ]

        recetas = [
            {
                "id_receta": r["id_receta"],
                "id_consulta": r["id_consulta"],
                "medicamento": r["medicamento"],
                "dosis": r["dosis"] or "",
                "frecuencia": r["frecuencia"] or "",
                "duracion_dias": r["duracion_dias"] or 0,
            }
            for r in r_rows
        ]

        controles = [
            {
                "id_control": g["id_control"],
                "fecha": str(g["fecha_control"]),
                "peso_kg": self._float(g["peso_kg"]),
                "talla_cm": self._float(g["talla_cm"]),
                "perimetro_cefalico_cm": self._float(g["perimetro_cefalico_cm"]),
            }
            for g in g_rows
        ]

        vacunas = [
            {
                "id_vacuna": v["id_vacuna"],
                "nombre_vacuna": v["nombre_vacuna"],
                "fecha": str(v["fecha_aplicacion"]),
                "dosis": v["dosis"],
                "lote": v["lote"],
            }
            for v in v_rows
        ]

        return HistorialOut(
            paciente=self._to_paciente(p_row),
            consultas=consultas,
            diagnosticos=diagnosticos,
            recetas=recetas,
            controles_crecimiento=controles,
            vacunas=vacunas,
        )

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        try:
            pid = int(id_paciente)
        except (TypeError, ValueError):
            return False
        with self._cursor() as cur:
            cur.execute("UPDATE paciente SET estado = 'archivado' WHERE id_paciente = %s", (pid,))
            # rowcount = 0 si ya estaba archivado; se valida existencia aparte
            cur.execute("SELECT 1 FROM paciente WHERE id_paciente = %s", (pid,))
            return cur.fetchone() is not None
