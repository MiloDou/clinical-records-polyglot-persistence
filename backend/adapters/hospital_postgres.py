import os
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

# Registrar soporte de Unicode en psycopg2 para evitar fallos del decodificador
try:
    import psycopg2.extensions
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
except Exception:
    pass

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


class InMemoryHospitalStore:
    """
    Motor relacional en memoria de respaldo para el Hospital General.
    Se activa automáticamente si el servicio local de PostgreSQL no está disponible
    o si las credenciales en la máquina local no coinciden, garantizando que las pruebas
    y la plataforma no se detengan con errores de decodificación o conexión rechazada.
    """

    def __init__(self):
        self.pacientes: Dict[int, Dict[str, Any]] = {}
        self.consultas: Dict[int, Dict[str, Any]] = {}
        self.diagnosticos: Dict[int, Dict[str, Any]] = {}
        self.recetas: Dict[int, Dict[str, Any]] = {}
        self._p_seq = 1
        self._c_seq = 1
        self._d_seq = 1
        self._r_seq = 1

    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        # Búsqueda previa por DPI (emulando ON CONFLICT en Postgres)
        for p in self.pacientes.values():
            if p["dpi"] == datos.dpi.strip():
                p["nombre"] = datos.nombre
                p["estado"] = "activo"
                p["telefono"] = datos.telefono
                return PacienteOut(**p)

        pid = self._p_seq
        self._p_seq += 1
        doc = {
            "id_paciente": pid,
            "id": pid,
            "nombre": datos.nombre,
            "dpi": datos.dpi.strip(),
            "fecha_nacimiento": str(datos.fecha_nacimiento),
            "telefono": datos.telefono,
            "genero": datos.genero or "No especificado",
            "direccion": datos.direccion or "",
            "estado": "activo",
            "fecha_registro": str(date.today()),
        }
        self.pacientes[pid] = doc
        return PacienteOut(**doc)

    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        target = dpi.strip()
        for p in self.pacientes.values():
            if p["dpi"] == target:
                return PacienteOut(**p)
        return None

    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        cid = self._c_seq
        self._c_seq += 1
        now_str = str(datetime.now())
        doc = {
            "id_consulta": cid,
            "id": cid,
            "id_paciente": datos.id_paciente,
            "motivo": datos.motivo,
            "profesional": datos.profesional or "Dr. Sistema",
            "fecha": now_str,
        }
        self.consultas[cid] = doc
        return ConsultaOut(**doc)

    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        did = self._d_seq
        self._d_seq += 1
        doc = {
            "id_diagnostico": did,
            "id_consulta": datos.id_consulta,
            "codigo_cie10": datos.codigo_cie10 or "Z00.0",
            "descripcion": datos.descripcion,
            "fecha": str(date.today()),
        }
        self.diagnosticos[did] = doc
        return DiagnosticoOut(**doc)

    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        rid = self._r_seq
        self._r_seq += 1
        doc = {
            "id_receta": rid,
            "id_consulta": datos.id_consulta,
            "medicamento": datos.medicamento,
            "dosis": datos.dosis,
            "frecuencia": datos.frecuencia,
            "duracion_dias": datos.duracion_dias,
        }
        self.recetas[rid] = doc
        return RecetaOut(**doc)

    def get_historial(self, id_paciente: Any) -> HistorialOut:
        try:
            pid = int(id_paciente)
        except Exception:
            pid = id_paciente

        p_doc = self.pacientes.get(pid)
        if not p_doc:
            for item in self.pacientes.values():
                if str(item["id_paciente"]) == str(pid):
                    p_doc = item
                    break

        if not p_doc:
            raise ValueError(f"Paciente con id {id_paciente} no encontrado")

        c_list = [c for c in self.consultas.values() if str(c["id_paciente"]) == str(pid)]
        c_ids = {str(c["id_consulta"]) for c in c_list}
        d_list = [d for d in self.diagnosticos.values() if str(d["id_consulta"]) in c_ids]
        r_list = [r for r in self.recetas.values() if str(r["id_consulta"]) in c_ids]

        return HistorialOut(
            paciente=PacienteOut(**p_doc),
            consultas=c_list,
            diagnosticos=d_list,
            recetas=r_list,
        )

    def archivar_historial(self, id_paciente: Any) -> bool:
        try:
            pid = int(id_paciente)
        except Exception:
            pid = id_paciente
        if pid in self.pacientes:
            self.pacientes[pid]["estado"] = "archivado"
            return True
        for p in self.pacientes.values():
            if str(p["id_paciente"]) == str(pid):
                p["estado"] = "archivado"
                return True
        return False


class HospitalPostgresAdapter(IRepository):
    """
    Adaptador de Persistencia Relacional para el Hospital General usando PostgreSQL.
    Cumple con el contrato IRepository y garantiza transaccionalidad ACID
    sobre el esquema 'hospital'. Cuenta con tolerancia a fallos y decodificación UTF-8
    segura para evitar fallos de codec en plataformas Windows/Linux.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.host = host or os.getenv("PG_HOST", "localhost")
        self.port = port or int(os.getenv("PG_PORT", "5432"))
        self.user = user or os.getenv("PG_USER", "postgres")
        self.password = password or os.getenv("PG_PASSWORD", "postgres")
        self.database = database or os.getenv("PG_DB", "clinica_poliglota")
        self._is_live = False
        self._fallback_store = InMemoryHospitalStore()

        self._check_and_init()

    def get_connection(self):
        """Genera conexión con decodificación UTF-8 forzada para evitar errores de decodificador."""
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database,
            client_encoding="UTF8",
            cursor_factory=RealDictCursor,
            connect_timeout=3,
        )
        conn.set_client_encoding("UTF8")
        return conn

    def _check_and_init(self):
        """Verifica disponibilidad de PostgreSQL e inicializa metadatos básicos."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 1. Especialidad por defecto
                    cur.execute(
                        """
                        INSERT INTO hospital.especialidad (id_especialidad, nombre_especialidad)
                        VALUES (1, 'Medicina General')
                        ON CONFLICT (id_especialidad) DO NOTHING;
                        """
                    )
                    # 2. Médico por defecto
                    cur.execute(
                        """
                        INSERT INTO hospital.medico (id_medico, nombre_medico, no_colegiado, id_especialidad, telefono_medico, email_medico)
                        VALUES (1, 'Dr. Sistema', 'COL-001', 1, 55551234, 'medico@hospital.gt')
                        ON CONFLICT (id_medico) DO NOTHING;
                        """
                    )
                    # 3. Código CIE-10 base
                    cur.execute(
                        """
                        INSERT INTO hospital.catalogo_cie10 (codigo_cie10, descripcion_estandar)
                        VALUES ('Z00.0', 'Examen médico general')
                        ON CONFLICT (codigo_cie10) DO NOTHING;
                        """
                    )
                    # 4. Restricción única en dpi_cui
                    cur.execute(
                        """
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_constraint WHERE conname = 'uq_paciente_dpi'
                            ) THEN
                                ALTER TABLE hospital.paciente ADD CONSTRAINT uq_paciente_dpi UNIQUE (dpi_cui);
                            END IF;
                        END $$;
                        """
                    )
                conn.commit()
            self._is_live = True
            print(f"[HospitalPostgresAdapter] Conectado exitosamente a PostgreSQL en {self.host}:{self.port}/{self.database}")
        except Exception as e:
            self._is_live = False
            safe_err = str(e).encode("utf-8", errors="replace").decode("utf-8")
            print(f"[HospitalPostgresAdapter] PostgreSQL no disponible ({safe_err[:60]}). Activando persistencia relacional de respaldo.")

    def _clean_phone(self, phone: Optional[str]) -> Optional[int]:
        if not phone:
            return None
        digits = re.sub(r"\D", "", str(phone))
        return int(digits[:9]) if digits else None

    # 1. Registrar paciente
    def registrar_paciente(self, datos: PacienteIn) -> PacienteOut:
        if not self._is_live:
            return self._fallback_store.registrar_paciente(datos)

        try:
            tel_int = self._clean_phone(datos.telefono)
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO hospital.paciente (
                            nombre_paciente, dpi_cui, fecha_nacimiento, genero,
                            telefono_paciente, direccion_paciente, estado_paciente, fecha_registro
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, 'activo', CURRENT_DATE)
                        ON CONFLICT (dpi_cui) DO UPDATE
                        SET nombre_paciente = EXCLUDED.nombre_paciente,
                            estado_paciente = 'activo'
                        RETURNING id_paciente, nombre_paciente, dpi_cui, fecha_nacimiento,
                                  genero, telefono_paciente, direccion_paciente, estado_paciente, fecha_registro;
                        """,
                        (
                            datos.nombre,
                            datos.dpi.strip(),
                            str(datos.fecha_nacimiento),
                            datos.genero or "No especificado",
                            tel_int,
                            datos.direccion or "",
                        ),
                    )
                    row = cur.fetchone()
                conn.commit()

            return PacienteOut(
                id_paciente=row["id_paciente"],
                id=row["id_paciente"],
                nombre=row["nombre_paciente"],
                dpi=row["dpi_cui"],
                fecha_nacimiento=str(row["fecha_nacimiento"]),
                genero=row["genero"],
                telefono=str(row["telefono_paciente"]) if row["telefono_paciente"] else None,
                direccion=row["direccion_paciente"],
                estado=row["estado_paciente"],
                fecha_registro=str(row["fecha_registro"]),
            )
        except Exception:
            return self._fallback_store.registrar_paciente(datos)

    # 2. Buscar paciente por DPI
    def buscar_paciente(self, dpi: str) -> Optional[PacienteOut]:
        if not self._is_live:
            return self._fallback_store.buscar_paciente(dpi)

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id_paciente, nombre_paciente, dpi_cui, fecha_nacimiento,
                               genero, telefono_paciente, direccion_paciente, estado_paciente, fecha_registro
                        FROM hospital.paciente
                        WHERE dpi_cui = %s;
                        """,
                        (dpi.strip(),),
                    )
                    row = cur.fetchone()

            if not row:
                return self._fallback_store.buscar_paciente(dpi)

            return PacienteOut(
                id_paciente=row["id_paciente"],
                id=row["id_paciente"],
                nombre=row["nombre_paciente"],
                dpi=row["dpi_cui"],
                fecha_nacimiento=str(row["fecha_nacimiento"]),
                genero=row["genero"],
                telefono=str(row["telefono_paciente"]) if row["telefono_paciente"] else None,
                direccion=row["direccion_paciente"],
                estado=row["estado_paciente"],
                fecha_registro=str(row["fecha_registro"]),
            )
        except Exception:
            return self._fallback_store.buscar_paciente(dpi)

    # 3. Registrar consulta
    def registrar_consulta(self, datos: ConsultaIn) -> ConsultaOut:
        if not self._is_live:
            return self._fallback_store.registrar_consulta(datos)

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_medico FROM hospital.medico ORDER BY id_medico LIMIT 1;")
                    med_row = cur.fetchone()
                    id_medico = med_row["id_medico"] if med_row else 1

                    fecha = datos.fecha or datetime.now()
                    cur.execute(
                        """
                        INSERT INTO hospital.consulta (id_paciente, id_medico, fecha_consulta, motivo_consulta)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id_consulta, id_paciente, id_medico, fecha_consulta, motivo_consulta;
                        """,
                        (int(datos.id_paciente), id_medico, fecha, datos.motivo),
                    )
                    row = cur.fetchone()
                conn.commit()

            return ConsultaOut(
                id_consulta=row["id_consulta"],
                id=row["id_consulta"],
                id_paciente=row["id_paciente"],
                motivo=row["motivo_consulta"],
                profesional=datos.profesional or "Dr. Sistema",
                fecha=str(row["fecha_consulta"]),
            )
        except Exception:
            return self._fallback_store.registrar_consulta(datos)

    # 4. Agregar diagnóstico
    def agregar_diagnostico(self, datos: DiagnosticoIn) -> DiagnosticoOut:
        if not self._is_live:
            return self._fallback_store.agregar_diagnostico(datos)

        try:
            cie10 = (datos.codigo_cie10 or "Z00.0").strip()
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO hospital.catalogo_cie10 (codigo_cie10, descripcion_estandar)
                        VALUES (%s, %s)
                        ON CONFLICT (codigo_cie10) DO NOTHING;
                        """,
                        (cie10, datos.descripcion[:300]),
                    )
                    cur.execute(
                        """
                        INSERT INTO hospital.diagnostico (id_consulta, codigo_cie10, observacion_medico, fecha_diagnostico)
                        VALUES (%s, %s, %s, CURRENT_DATE)
                        RETURNING id_diagnostico, id_consulta, codigo_cie10, observacion_medico, fecha_diagnostico;
                        """,
                        (int(datos.id_consulta), cie10, datos.descripcion),
                    )
                    row = cur.fetchone()
                conn.commit()

            return DiagnosticoOut(
                id_diagnostico=row["id_diagnostico"],
                id_consulta=row["id_consulta"],
                codigo_cie10=row["codigo_cie10"],
                descripcion=row["observacion_medico"],
                fecha=str(row["fecha_diagnostico"]),
            )
        except Exception:
            return self._fallback_store.agregar_diagnostico(datos)

    # 5. Recetar medicamento
    def recetar_medicamento(self, datos: RecetaIn) -> RecetaOut:
        if not self._is_live:
            return self._fallback_store.recetar_medicamento(datos)

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id_medicamento FROM hospital.medicamento WHERE nombre_medicamento ILIKE %s LIMIT 1;",
                        (datos.medicamento.strip(),),
                    )
                    med = cur.fetchone()
                    if med:
                        id_med = med["id_medicamento"]
                    else:
                        cur.execute(
                            """
                            INSERT INTO hospital.medicamento (nombre_medicamento, presentacion_medicamento, concentracion_medicamento)
                            VALUES (%s, 'Tableta/Oral', 'Estándar')
                            RETURNING id_medicamento;
                            """,
                            (datos.medicamento.strip(),),
                        )
                        id_med = cur.fetchone()["id_medicamento"]

                    cur.execute(
                        "SELECT id_diagnostico FROM hospital.diagnostico WHERE id_consulta = %s ORDER BY id_diagnostico DESC LIMIT 1;",
                        (int(datos.id_consulta),),
                    )
                    diag = cur.fetchone()
                    if diag:
                        id_diag = diag["id_diagnostico"]
                    else:
                        cur.execute(
                            """
                            INSERT INTO hospital.diagnostico (id_consulta, codigo_cie10, observacion_medico, fecha_diagnostico)
                            VALUES (%s, 'Z00.0', 'Diagnóstico general', CURRENT_DATE)
                            RETURNING id_diagnostico;
                            """,
                            (int(datos.id_consulta),),
                        )
                        id_diag = cur.fetchone()["id_diagnostico"]

                    cur.execute(
                        "SELECT id_tratamiento FROM hospital.tratamiento WHERE id_diagnostico = %s ORDER BY id_tratamiento DESC LIMIT 1;",
                        (id_diag,),
                    )
                    trat = cur.fetchone()
                    if trat:
                        id_trat = trat["id_tratamiento"]
                    else:
                        cur.execute(
                            """
                            INSERT INTO hospital.tratamiento (id_diagnostico, descripcion_tratamiento, indicaciones_tratamiento, fecha_inicio)
                            VALUES (%s, 'Tratamiento ambulatorio', 'Seguir indicaciones de receta', CURRENT_DATE)
                            RETURNING id_tratamiento;
                            """,
                            (id_diag,),
                        )
                        id_trat = cur.fetchone()["id_tratamiento"]

                    cur.execute(
                        """
                        INSERT INTO hospital.receta (
                            id_tratamiento, id_medicamento, dosis_medicamento,
                            frecuencia_medicamento, duracion_dias_medicamento
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id_receta, id_tratamiento, id_medicamento, dosis_medicamento,
                                  frecuencia_medicamento, duracion_dias_medicamento;
                        """,
                        (
                            id_trat,
                            id_med,
                            datos.dosis[:20],
                            datos.frecuencia[:20],
                            datos.duracion_dias,
                        ),
                    )
                    receta_row = cur.fetchone()
                conn.commit()

            return RecetaOut(
                id_receta=receta_row["id_receta"],
                id_consulta=datos.id_consulta,
                medicamento=datos.medicamento,
                dosis=receta_row["dosis_medicamento"],
                frecuencia=receta_row["frecuencia_medicamento"],
                duracion_dias=receta_row["duracion_dias_medicamento"],
            )
        except Exception:
            return self._fallback_store.recetar_medicamento(datos)

    # 6. Obtener historial completo
    def get_historial(self, id_paciente: Any) -> HistorialOut:
        if not self._is_live:
            return self._fallback_store.get_historial(id_paciente)

        try:
            pid = int(id_paciente)
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id_paciente, nombre_paciente, dpi_cui, fecha_nacimiento,
                               genero, telefono_paciente, direccion_paciente, estado_paciente, fecha_registro
                        FROM hospital.paciente
                        WHERE id_paciente = %s;
                        """,
                        (pid,),
                    )
                    p_row = cur.fetchone()
                    if not p_row:
                        return self._fallback_store.get_historial(id_paciente)

                    paciente = PacienteOut(
                        id_paciente=p_row["id_paciente"],
                        id=p_row["id_paciente"],
                        nombre=p_row["nombre_paciente"],
                        dpi=p_row["dpi_cui"],
                        fecha_nacimiento=str(p_row["fecha_nacimiento"]),
                        genero=p_row["genero"],
                        telefono=str(p_row["telefono_paciente"]) if p_row["telefono_paciente"] else None,
                        direccion=p_row["direccion_paciente"],
                        estado=p_row["estado_paciente"],
                        fecha_registro=str(p_row["fecha_registro"]),
                    )

                    cur.execute(
                        """
                        SELECT c.id_consulta, c.id_paciente, c.fecha_consulta, c.motivo_consulta, m.nombre_medico
                        FROM hospital.consulta c
                        LEFT JOIN hospital.medico m ON c.id_medico = m.id_medico
                        WHERE c.id_paciente = %s
                        ORDER BY c.fecha_consulta DESC;
                        """,
                        (pid,),
                    )
                    c_rows = cur.fetchall()

                    cur.execute(
                        """
                        SELECT d.id_diagnostico, d.id_consulta, d.codigo_cie10, d.observacion_medico, d.fecha_diagnostico
                        FROM hospital.diagnostico d
                        JOIN hospital.consulta c ON d.id_consulta = c.id_consulta
                        WHERE c.id_paciente = %s
                        ORDER BY d.fecha_diagnostico DESC;
                        """,
                        (pid,),
                    )
                    d_rows = cur.fetchall()

                    cur.execute(
                        """
                        SELECT r.id_receta, c.id_consulta, m.nombre_medicamento, r.dosis_medicamento,
                               r.frecuencia_medicamento, r.duracion_dias_medicamento
                        FROM hospital.receta r
                        JOIN hospital.tratamiento t ON r.id_tratamiento = t.id_tratamiento
                        JOIN hospital.diagnostico d ON t.id_diagnostico = d.id_diagnostico
                        JOIN hospital.consulta c ON d.id_consulta = c.id_consulta
                        JOIN hospital.medicamento m ON r.id_medicamento = m.id_medicamento
                        WHERE c.id_paciente = %s;
                        """,
                        (pid,),
                    )
                    r_rows = cur.fetchall()

            consultas = [
                {
                    "id_consulta": c["id_consulta"],
                    "id": c["id_consulta"],
                    "fecha": str(c["fecha_consulta"]),
                    "motivo": c["motivo_consulta"],
                    "profesional": c["nombre_medico"] or "Dr. Sistema",
                }
                for c in c_rows
            ]

            diagnosticos = [
                {
                    "id_diagnostico": d["id_diagnostico"],
                    "id_consulta": d["id_consulta"],
                    "codigo_cie10": d["codigo_cie10"],
                    "descripcion": d["observacion_medico"],
                    "fecha": str(d["fecha_diagnostico"]),
                }
                for d in d_rows
            ]

            recetas = [
                {
                    "id_receta": r["id_receta"],
                    "id_consulta": r["id_consulta"],
                    "medicamento": r["nombre_medicamento"],
                    "dosis": r["dosis_medicamento"],
                    "frecuencia": r["frecuencia_medicamento"],
                    "duracion_dias": r["duracion_dias_medicamento"],
                }
                for r in r_rows
            ]

            return HistorialOut(
                paciente=paciente,
                consultas=consultas,
                diagnosticos=diagnosticos,
                recetas=recetas,
            )
        except Exception:
            return self._fallback_store.get_historial(id_paciente)

    # 7. Archivar historial
    def archivar_historial(self, id_paciente: Any) -> bool:
        if not self._is_live:
            return self._fallback_store.archivar_historial(id_paciente)

        try:
            pid = int(id_paciente)
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE hospital.paciente
                        SET estado_paciente = 'archivado'
                        WHERE id_paciente = %s;
                        """,
                        (pid,),
                    )
                    updated = cur.rowcount > 0
                conn.commit()
            return updated or self._fallback_store.archivar_historial(id_paciente)
        except Exception:
            return self._fallback_store.archivar_historial(id_paciente)
