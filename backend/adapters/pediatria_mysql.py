import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import mysql.connector
from mysql.connector import Error

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


class PediatriaMysqlAdapter(IRepository):
    """
    Adaptador de Persistencia para el Centro Médico Pediátrico usando MySQL.
    Cumple con el contrato IRepository.
    Diseñado para consultas frecuentes y seguimiento de crecimiento/vacunación.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.host = host or os.getenv("MYSQL_HOST", "localhost")
        self.port = int(port or os.getenv("MYSQL_PORT", "3306"))
        self.user = user or os.getenv("MYSQL_USER", "root")
        self.password = password or os.getenv("MYSQL_PASSWORD", "123")
        self.database = database or os.getenv("MYSQL_DB", "pediatria_db")

    def get_connection(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    # 1. Registrar paciente
    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                INSERT INTO paciente (
                    nombre_paciente, dpi_cui, fecha_nacimiento, genero,
                    telefono_paciente, tutor_nombre, tutor_telefono, estado, fecha_registro
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo', CURRENT_DATE)
                ON DUPLICATE KEY UPDATE
                    nombre_paciente = VALUES(nombre_paciente),
                    estado = 'activo',
                    id_paciente = LAST_INSERT_ID(id_paciente)
            """
            cursor.execute(
                sql,
                (
                    datos.nombre,
                    datos.dpi.strip(),
                    str(datos.fecha_nacimiento),
                    datos.genero or "No especificado",
                    datos.telefono or "",
                    datos.tutor_nombre or "",
                    datos.tutor_telefono or "",
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid

            cursor.execute("SELECT * FROM paciente WHERE id_paciente = %s", (new_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        return PacienteOut(
            id_paciente=row["id_paciente"],
            id=row["id_paciente"],
            nombre=row["nombre_paciente"],
            dpi=row["dpi_cui"],
            fecha_nacimiento=str(row["fecha_nacimiento"]),
            genero=row["genero"],
            telefono=row["telefono_paciente"],
            tutor_nombre=row["tutor_nombre"],
            tutor_telefono=row["tutor_telefono"],
            estado=row["estado"],
            fecha_registro=str(row["fecha_registro"]),
        )

    # 2. Buscar paciente por DPI
    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM paciente WHERE dpi_cui = %s", (dpi.strip(),))
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not row:
            return None

        return PacienteOut(
            id_paciente=row["id_paciente"],
            id=row["id_paciente"],
            nombre=row["nombre_paciente"],
            dpi=row["dpi_cui"],
            fecha_nacimiento=str(row["fecha_nacimiento"]),
            genero=row["genero"],
            telefono=row["telefono_paciente"],
            tutor_nombre=row["tutor_nombre"],
            tutor_telefono=row["tutor_telefono"],
            estado=row["estado"],
            fecha_registro=str(row["fecha_registro"]),
        )

    # 3. Registrar consulta
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            now_dt = datetime.now()
            sql = """
                INSERT INTO consulta_pediatrica (id_paciente, fecha_consulta, nombre_medico, motivo, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    int(datos.id_paciente),
                    now_dt,
                    datos.profesional or "Dra. Sofía Morales",
                    datos.motivo,
                    datos.observaciones or "",
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

        return ConsultaOut(
            id_consulta=new_id,
            id=new_id,
            id_paciente=datos.id_paciente,
            motivo=datos.motivo,
            profesional=datos.profesional or "Dra. Sofía Morales",
            fecha=str(now_dt),
        )

    # 4. Agregar diagnóstico
    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                INSERT INTO diagnostico (id_consulta, codigo_cie10, descripcion)
                VALUES (%s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    int(datos.id_consulta),
                    datos.codigo_cie10 or "Z00.0",
                    datos.descripcion,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

        return DiagnosticoOut(
            id_diagnostico=new_id,
            id_consulta=datos.id_consulta,
            codigo_cie10=datos.codigo_cie10 or "Z00.0",
            descripcion=datos.descripcion,
            fecha=str(date.today()),
        )

    # 5. Recetar medicamento
    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                INSERT INTO receta (id_consulta, medicamento, dosis, frecuencia, duracion_dias)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    int(datos.id_consulta),
                    datos.medicamento,
                    datos.dosis,
                    datos.frecuencia,
                    datos.duracion_dias,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

        return RecetaOut(
            id_receta=new_id,
            id_consulta=datos.id_consulta,
            medicamento=datos.medicamento,
            dosis=datos.dosis,
            frecuencia=datos.frecuencia,
            duracion_dias=datos.duracion_dias,
        )

    # 6. Obtener historial completo
    def get_historial(self, id_paciente: Any) -> HistorialOut:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            pid = int(id_paciente)
            cursor.execute("SELECT * FROM paciente WHERE id_paciente = %s", (pid,))
            p_row = cursor.fetchone()
            if not p_row:
                raise ValueError(f"Paciente con id {pid} no encontrado en Pediatría")

            paciente = PacienteOut(
                id_paciente=p_row["id_paciente"],
                id=p_row["id_paciente"],
                nombre=p_row["nombre_paciente"],
                dpi=p_row["dpi_cui"],
                fecha_nacimiento=str(p_row["fecha_nacimiento"]),
                genero=p_row["genero"],
                telefono=p_row["telefono_paciente"],
                tutor_nombre=p_row["tutor_nombre"],
                tutor_telefono=p_row["tutor_telefono"],
                estado=p_row["estado"],
                fecha_registro=str(p_row["fecha_registro"]),
            )

            # Consultas
            cursor.execute(
                "SELECT * FROM consulta_pediatrica WHERE id_paciente = %s ORDER BY fecha_consulta DESC",
                (pid,),
            )
            c_rows = cursor.fetchall()

            # Diagnósticos
            cursor.execute(
                """
                SELECT d.* FROM diagnostico d
                JOIN consulta_pediatrica c ON d.id_consulta = c.id_consulta
                WHERE c.id_paciente = %s
                """,
                (pid,),
            )
            d_rows = cursor.fetchall()

            # Recetas
            cursor.execute(
                """
                SELECT r.* FROM receta r
                JOIN consulta_pediatrica c ON r.id_consulta = c.id_consulta
                WHERE c.id_paciente = %s
                """,
                (pid,),
            )
            r_rows = cursor.fetchall()

            # Controles de crecimiento
            cursor.execute(
                "SELECT * FROM control_crecimiento WHERE id_paciente = %s ORDER BY fecha_control DESC",
                (pid,),
            )
            cc_rows = cursor.fetchall()

            # Vacunas
            cursor.execute(
                "SELECT * FROM vacuna_aplicada WHERE id_paciente = %s ORDER BY fecha_aplicacion DESC",
                (pid,),
            )
            v_rows = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        consultas = [
            {
                "id_consulta": c["id_consulta"],
                "id": c["id_consulta"],
                "fecha": str(c["fecha_consulta"]),
                "motivo": c["motivo"],
                "profesional": c["nombre_medico"],
            }
            for c in c_rows
        ]

        diagnosticos = [
            {
                "id_diagnostico": d["id_diagnostico"],
                "id_consulta": d["id_consulta"],
                "codigo_cie10": d["codigo_cie10"],
                "descripcion": d["descripcion"],
            }
            for d in d_rows
        ]

        recetas = [
            {
                "id_receta": r["id_receta"],
                "id_consulta": r["id_consulta"],
                "medicamento": r["medicamento"],
                "dosis": r["dosis"],
                "frecuencia": r["frecuencia"],
                "duracion_dias": r["duracion_dias"],
            }
            for r in r_rows
        ]

        return HistorialOut(
            paciente=paciente,
            consultas=consultas,
            diagnosticos=diagnosticos,
            recetas=recetas,
            controles_crecimiento=cc_rows,
            vacunas=v_rows,
        )

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            pid = int(id_paciente)
            cursor.execute("UPDATE paciente SET estado = 'archivado' WHERE id_paciente = %s", (pid,))
            conn.commit()
            updated = cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
        return updated
