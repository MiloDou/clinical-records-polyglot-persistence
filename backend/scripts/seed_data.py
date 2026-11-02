"""
Script de precarga de datos de prueba para la Entrega II.
Carga datos clínicos en los motores asignados a Ronaldo / Emilio:
- Hospital General (PostgreSQL)
- Laboratorio Clínico (MongoDB)

(Las partes de Pediatría y Odontología corresponden a Brayan).

Uso:
cd Code/backend
source .venv/bin/activate
python scripts/seed_data.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.models import ConsultaIn, DiagnosticoIn, PacienteIn, RecetaIn
from core.routing import get_adapter_for_institution

SEED_DATA = {
    "hospital": [
        {
            "paciente": PacienteIn(
                nombre="Carlos Roberto Gómez López",
                dpi="1234567890101",
                fecha_nacimiento="1980-04-12",
                telefono="55214488",
                genero="Masculino",
                direccion="Zona 11, Ciudad de Guatemala",
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
                nombre="Elena Patricia Morales Ruiz",
                dpi="2345678900101",
                fecha_nacimiento="1975-09-28",
                telefono="54129933",
                genero="Femenino",
                direccion="Zona 7, Mixco",
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
                nombre="Jorge Mario Castillo Santos",
                dpi="3456789010101",
                fecha_nacimiento="1992-11-05",
                telefono="59001122",
                genero="Masculino",
                direccion="Zona 1, Villa Nueva",
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
                nombre="Ana Lucía Contreras Vela",
                dpi="7890123450101",
                fecha_nacimiento="1988-06-14",
                telefono="59998877",
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
                nombre="Marco Antonio Barrientos",
                dpi="8901234560101",
                fecha_nacimiento="1995-12-03",
                telefono="57776655",
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
                nombre="Silvia Regina Cordero",
                dpi="9012345670101",
                fecha_nacimiento="1983-02-21",
                telefono="52223344",
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
