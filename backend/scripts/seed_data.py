"""
Script de precarga de datos sintéticos para la Entrega II.
Carga ejemplos ficticios en los motores asignados a Ronaldo / Emilio:
- Hospital General (PostgreSQL)
- Laboratorio Clínico (MongoDB)

(Las partes de Pediatría y Odontología corresponden a Brayan).

Uso:
cd backend
source .venv/bin/activate
python scripts/seed_data.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from core.models import ConsultaIn, DiagnosticoIn, PacienteIn, RecetaIn
from core.routing import get_adapter_for_institution

SEED_DATA = {
    "hospital": [
        {
            "paciente": PacienteIn(
                nombre='Paciente Demo Hospital 01',
                dpi='0000000000001',
                fecha_nacimiento="1980-04-12",
                telefono='00000001',
                genero="Masculino",
                direccion='Dirección ficticia',
            ),
            "consulta": ConsultaIn(
                id_paciente="",
                motivo="Control trimestral de presión arterial y cefalea leve",
                profesional="Dr. Fernando García",
            ),
            "diagnostico": DiagnosticoIn(
                id_consulta="",
                descripcion="Hipertensión arterial esencial estadio I",
                codigo_cie10="I10",
            ),
            "receta": RecetaIn(
                id_consulta="",
                medicamento="Enalapril 20mg",
                dosis="1 tableta",
                frecuencia="Cada 24 horas",
                duracion_dias=30,
            ),
        },
        {
            "paciente": PacienteIn(
                nombre='Paciente Demo Hospital 02',
                dpi='0000000000002',
                fecha_nacimiento="1975-09-28",
                telefono='00000002',
                genero="Femenino",
                direccion='Dirección ficticia',
            ),
            "consulta": ConsultaIn(
                id_paciente="",
                motivo="Control glucémico y revisión de laboratorios",
                profesional="Dr. Fernando García",
            ),
            "diagnostico": DiagnosticoIn(
                id_consulta="",
                descripcion="Diabetes mellitus tipo 2 sin complicaciones",
                codigo_cie10="E11.9",
            ),
            "receta": RecetaIn(
                id_consulta="",
                medicamento="Metformina 850mg",
                dosis="1 tableta",
                frecuencia="Cada 12 horas",
                duracion_dias=60,
            ),
        },
        {
            "paciente": PacienteIn(
                nombre='Paciente Demo Hospital 03',
                dpi='0000000000003',
                fecha_nacimiento="1992-11-05",
                telefono='00000003',
                genero="Masculino",
                direccion='Dirección ficticia',
            ),
            "consulta": ConsultaIn(
                id_paciente="",
                motivo="Dolor lumbar tras esfuerzo físico laboral",
                profesional="Dr. Fernando García",
            ),
            "diagnostico": DiagnosticoIn(
                id_consulta="",
                descripcion="Lumbalgia mecánica aguda",
                codigo_cie10="M54.5",
            ),
            "receta": RecetaIn(
                id_consulta="",
                medicamento="Ibuprofeno 600mg",
                dosis="1 tableta",
                frecuencia="Cada 8 horas con comida",
                duracion_dias=7,
            ),
        },
    ],
    "laboratorio": [
        {
            "paciente": PacienteIn(
                nombre='Paciente Demo Laboratorio 01',
                dpi='0000000000004',
                fecha_nacimiento="1988-06-14",
                telefono='00000004',
                genero="Femenino",
            ),
            "consulta": ConsultaIn(
                id_paciente="",
                motivo="Orden de perfil lipídico y glucosa en ayunas",
                profesional="Lic. Carlos Méndez",
            ),
            "diagnostico": DiagnosticoIn(
                id_consulta="",
                descripcion="Dislipidemia mixta leve según química sanguínea",
                codigo_cie10="E78.2",
            ),
            "receta": RecetaIn(
                id_consulta="",
                medicamento="Recomendación dieta hipograsa y ejercicio",
                dosis="Indicación",
                frecuencia="Diaria",
                duracion_dias=90,
            ),
        },
        {
            "paciente": PacienteIn(
                nombre='Paciente Demo Laboratorio 02',
                dpi='0000000000005',
                fecha_nacimiento="1995-12-03",
                telefono='00000005',
                genero="Masculino",
            ),
            "consulta": ConsultaIn(
                id_paciente="",
                motivo="Hematología completa de rutina y frotis sanguíneo",
                profesional="Lic. Carlos Méndez",
            ),
            "diagnostico": DiagnosticoIn(
                id_consulta="",
                descripcion="Parámetros hematológicos en rangos de referencia",
                codigo_cie10="Z00.0",
            ),
            "receta": RecetaIn(
                id_consulta="",
                medicamento="Control anual preventivo",
                dosis="1 cita",
                frecuencia="Anual",
                duracion_dias=365,
            ),
        },
        {
            "paciente": PacienteIn(
                nombre='Paciente Demo Laboratorio 03',
                dpi='0000000000006',
                fecha_nacimiento="1983-02-21",
                telefono='00000006',
                genero="Femenino",
            ),
            "consulta": ConsultaIn(
                id_paciente="",
                motivo="Examen general de orina y cultivo microbiológico",
                profesional="Lic. Carlos Méndez",
            ),
            "diagnostico": DiagnosticoIn(
                id_consulta="",
                descripcion="Infección del tracto urinario baja aislada",
                codigo_cie10="N39.0",
            ),
            "receta": RecetaIn(
                id_consulta="",
                medicamento="Nitrofurantoína 100mg",
                dosis="1 cápsula",
                frecuencia="Cada 12 horas",
                duracion_dias=7,
            ),
        },
    ],
}


def sembrar_datos():
    print("🌱 Precargando datos clínicos de Ronaldo (Hospital y Laboratorio)...")
    for inst, lista in SEED_DATA.items():
        print(f"\n────────────────── {inst.upper()} ──────────────────")
        repo = get_adapter_for_institution(inst)
        for idx, item in enumerate(lista, 1):
            p = repo.registrar_paciente(item["paciente"])
            pid = p.id_paciente or p.id
            print(f"  [{idx}] Paciente: {p.nombre} (DPI: {p.dpi}) → ID: {pid}")

            c_in = item["consulta"]
            c_in.id_paciente = pid
            c = repo.registrar_consulta(c_in)
            cid = c.id_consulta or c.id

            d_in = item["diagnostico"]
            d_in.id_consulta = cid
            d = repo.agregar_diagnostico(d_in)

            r_in = item["receta"]
            r_in.id_consulta = cid
            r = repo.recetar_medicamento(r_in)
            print(f"      Consulta #{cid} | Diag: {d.descripcion[:30]}... | Receta: {r.medicamento}")

    print("\n✅ Datos clínicos de Ronaldo precargados exitosamente.")


if __name__ == "__main__":
    sembrar_datos()
