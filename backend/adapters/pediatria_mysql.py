import os
import mysql.connector
from mysql.connector import Error, IntegrityError
import functools
from contextlib import contextmanager
from typing import Optional, List
from datetime import datetime

from core.models import (
    PacienteIn, PacienteOut, ConsultaIn, ConsultaOut,
    DiagnosticoIn, DiagnosticoOut, RecetaIn, RecetaOut, HistorialOut
)


def _fk_a_not_found(fn):
    """Una violación de llave foránea significa que el paciente/consulta referenciado no existe -> ValueError (404)."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except IntegrityError as e:
            if e.errno != 1452:  # 1452 = FK inexistente
                raise
            raise ValueError(f"Recurso referenciado no encontrado: {e.msg}") from None
    return wrapper

class PediatriaMysqlAdapter:
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "root")
        self.database = os.getenv("MYSQL_DB", "pediatria_db")

    def _get_connection(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
        except Error as e:
            raise ConnectionError(f"No se pudo conectar a MySQL: {e}")

    @contextmanager
    def _connection(self):
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        with self._connection() as conn:
            cursor = conn.cursor(dictionary=True)
            # Buscar si el DPI ya existe
            cursor.execute("SELECT id_paciente FROM Paciente WHERE dpi_cui = %s", (datos.dpi,))
            existente = cursor.fetchone()

            # Extraer campos opcionales de forma segura sin romper Pydantic
            genero = getattr(datos, 'genero', None) or 'No especificado'
            tipo_sangre = getattr(datos, 'tipo_sangre', None) or 'O+'

            if existente:
                cursor.execute("""
                    UPDATE Paciente 
                    SET nombre_paciente = %s, fecha_nacimiento = %s, genero_paciente = %s,
                        tipo_sangre = %s, estado_paciente = 'activo'
                    WHERE id_paciente = %s
                """, (datos.nombre, datos.fecha_nacimiento, genero, tipo_sangre, existente['id_paciente']))
                pid = existente['id_paciente']
            else:
                cursor.execute("""
                    INSERT INTO Paciente (nombre_paciente, dpi_cui, fecha_nacimiento, genero_paciente, tipo_sangre, telefono_paciente, estado_paciente)
                    VALUES (%s, %s, %s, %s, %s, %s, 'activo')
                """, (datos.nombre, datos.dpi, datos.fecha_nacimiento, genero, tipo_sangre, datos.telefono))
                pid = cursor.lastrowid

            return PacienteOut(
                id_paciente=str(pid),
                nombre=datos.nombre,
                dpi=datos.dpi,
                fecha_nacimiento=str(datos.fecha_nacimiento),
                telefono=datos.telefono,
                estado="activo"
            )
        
    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        with self._connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Paciente WHERE dpi_cui = %s", (dpi,))
            row = cursor.fetchone()
            if not row:
                return None
            return PacienteOut(
                id_paciente=str(row['id_paciente']),
                nombre=row['nombre_paciente'],
                dpi=row['dpi_cui'],
                fecha_nacimiento=str(row['fecha_nacimiento']),
                telefono=row.get('telefono_paciente'),
                estado=row.get('estado_paciente', 'activo')
            )

    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        with self._connection() as conn:
            cursor = conn.cursor(dictionary=True)
            ahora = datetime.now()
            # Asegurar id_pediatra = 1 por defecto si no viene especificado
            id_pediatra = 1
            cursor.execute("""
                INSERT INTO Consulta (id_paciente, pediatra, fecha_consulta, motivo_consulta, notas_consulta)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(datos.id_paciente), id_pediatra, ahora, datos.motivo, datos.observaciones))
            cid = cursor.lastrowid

            return ConsultaOut(
                id_consulta=str(cid),
                id_paciente=str(datos.id_paciente),
                fecha=ahora.isoformat(),
                motivo=datos.motivo,
                profesional="Dra. Sofía Castillo"
            )

    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        with self._connection() as conn:
            cursor = conn.cursor(dictionary=True)
            # Guardamos la observación del diagnóstico en las notas clínicas de la consulta
            cursor.execute("""
                UPDATE Consulta 
                SET notas_consulta = CONCAT(COALESCE(notas_consulta, ''), ' | Diagnóstico: ', %s, ' (CIE10: ', %s, ')')
                WHERE id_consulta = %s
            """, (datos.descripcion, datos.codigo_cie10 or 'Z00.0', int(datos.id_consulta)))
            if cursor.rowcount == 0:
                raise ValueError(f"Consulta con id {datos.id_consulta} no encontrada")

            return DiagnosticoOut(
                id_diagnostico=f"diag-{datos.id_consulta}",
                id_consulta=str(datos.id_consulta),
                descripcion=datos.descripcion,
                codigo_cie10=datos.codigo_cie10
            )

    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        with self._connection() as conn:
            cursor = conn.cursor(dictionary=True)
            # Buscar medicamento o crear uno genérico si no existe
            cursor.execute("SELECT id_medicamento FROM Medicamento WHERE nombre_medicamento LIKE %s LIMIT 1", (f"%{datos.medicamento}%",))
            med = cursor.fetchone()
            if med:
                med_id = med['id_medicamento']
            else:
                cursor.execute("INSERT INTO Medicamento (nombre_medicamento, presentacion) VALUES (%s, 'Genérica')", (datos.medicamento,))
                med_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO Receta (id_consulta, id_medicamento, dosis, frecuencia, duracion_dias)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(datos.id_consulta), med_id, datos.dosis, datos.frecuencia, datos.duracion_dias))
            rid = cursor.lastrowid

            return RecetaOut(
                id_receta=str(rid),
                id_consulta=str(datos.id_consulta),
                medicamento=datos.medicamento,
                dosis=datos.dosis,
                frecuencia=datos.frecuencia,
                duracion_dias=datos.duracion_dias
            )

    def get_historial(self, id_paciente: int) -> HistorialOut:
        with self._connection() as conn:
            cursor = conn.cursor(dictionary=True)
            # Paciente
            cursor.execute("SELECT * FROM Paciente WHERE id_paciente = %s", (id_paciente,))
            p_row = cursor.fetchone()
            if not p_row:
                raise ValueError(f"Paciente con id {id_paciente} no encontrado")

            paciente_out = PacienteOut(
                id_paciente=str(p_row['id_paciente']),
                nombre=p_row['nombre_paciente'],
                dpi=p_row['dpi_cui'],
                fecha_nacimiento=str(p_row['fecha_nacimiento']),
                telefono=p_row.get('telefono_paciente'),
                estado=p_row.get('estado_paciente', 'activo')
            )

            # Consultas
            cursor.execute("""
                SELECT c.id_consulta, c.id_paciente, c.fecha_consulta, c.motivo_consulta, c.notas_consulta,
                       p.nombre_pediatra
                FROM Consulta c
                LEFT JOIN Pediatra p ON c.pediatra = p.id_pediatra
                WHERE c.id_paciente = %s
                ORDER BY c.fecha_consulta DESC
            """, (id_paciente,))
            consultas_rows = cursor.fetchall()

            consultas = []
            diagnosticos = []
            recetas = []

            for c in consultas_rows:
                cid = c['id_consulta']
                consultas.append(ConsultaOut(
                    id_consulta=str(cid),
                    id_paciente=str(c['id_paciente']),
                    fecha=str(c['fecha_consulta']),
                    motivo=c.get('motivo_consulta') or '',
                    profesional=c.get('nombre_pediatra') or 'Dra. Sofía Castillo'
                ))

                if c.get('notas_consulta') and 'Diagnóstico:' in c['notas_consulta']:
                    diagnosticos.append(DiagnosticoOut(
                        id_diagnostico=f"diag-{cid}",
                        id_consulta=str(cid),
                        descripcion=c['notas_consulta'],
                        codigo_cie10="Z00.0"
                    ))

                # Recetas vinculadas
                cursor.execute("""
                    SELECT r.id_receta, r.id_consulta, r.dosis, r.frecuencia, r.duracion_dias,
                           m.nombre_medicamento
                    FROM Receta r
                    JOIN Medicamento m ON r.id_medicamento = m.id_medicamento
                    WHERE r.id_consulta = %s
                """, (cid,))
                for r in cursor.fetchall():
                    recetas.append(RecetaOut(
                        id_receta=str(r['id_receta']),
                        id_consulta=str(r['id_consulta']),
                        medicamento=r['nombre_medicamento'],
                        dosis=r['dosis'],
                        frecuencia=r['frecuencia'],
                        duracion_dias=r['duracion_dias']
                    ))

            return HistorialOut(
                paciente=paciente_out,
                consultas=consultas,
                diagnosticos=diagnosticos,
                recetas=recetas
            )

    def archivar_historial(self, id_paciente: int) -> bool:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Paciente SET estado_paciente = 'archivado' WHERE id_paciente = %s", (id_paciente,))
            return cursor.rowcount > 0

# Paciente/consulta inexistente -> ValueError (404) en lugar de error de integridad (400)
for _metodo in ("registrar_consulta", "agregar_diagnostico", "recetar_medicamento"):
    setattr(PediatriaMysqlAdapter, _metodo, _fk_a_not_found(getattr(PediatriaMysqlAdapter, _metodo)))

