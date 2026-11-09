"""
Script de población de datos personalizados (Brayan)
Registra datos clínicos ficticios para demostración: 3 pacientes en MySQL y 3 en Firestore. No usar para decisiones clínicas.
"""
import sys
import requests

BASE_URL = "http://localhost:8000"

CREDENCIALES = {
    "pediatria": {"usuario": "medico@pediatria.gt", "password": "Test1234!"},
    "odontologia": {"usuario": "odontologo@dental.gt", "password": "Test1234!"}
}

# --- CASOS CLÍNICOS SINTÉTICOS: PEDIATRÍA (MySQL) ---
PACIENTES_PEDIATRIA = [
    {
        "paciente": {
            "nombre": 'Paciente Demo Pediatría 01',
            "dpi": '0000000000007',
            "fecha_nacimiento": "2021-08-15",
            "telefono": '00000007',
            "tutor_nombre": "Tutor de demostración 01",
            "tutor_telefono": '00000021',
            "genero": "Masculino"
        },
        "consulta": {
            "motivo": "Evaluación por cuadro asmático estacional y sibilancias",
            "profesional": "Dra. Sofía Castillo",
            "observaciones": "Tórax con tiraje intercostal leve. Murmullo vesicular disminuido."
        },
        "diagnostico": {
            "descripcion": "Asma predominantemente alérgica",
            "codigo_cie10": "J45.0"
        },
        "receta": {
            "medicamento": "Salbutamol Aerosol 100mcg",
            "dosis": "2 disparos con aerocámara",
            "frecuencia": "Cada 6 horas si presenta dificultad",
            "duracion_dias": 5
        }
    },
    {
        "paciente": {
            "nombre": 'Paciente Demo Pediatría 02',
            "dpi": '0000000000008',
            "fecha_nacimiento": "2023-03-10",
            "telefono": '00000008',
            "tutor_nombre": "Tutor de demostración 02",
            "tutor_telefono": '00000022',
            "genero": "Femenino"
        },
        "consulta": {
            "motivo": "Control rutinario de crecimiento e inicio de alimentación complementaria",
            "profesional": "Dr. Fernando Morales",
            "observaciones": "Tono muscular adecuado, percentiles de crecimiento dentro de rango normal."
        },
        "diagnostico": {
            "descripcion": "Supervisión de la alimentación y dieta del lactante",
            "codigo_cie10": "Z76.8"
        },
        "receta": {
            "medicamento": "Sulfato Ferroso gotas 25mg/ml",
            "dosis": "8 gotas",
            "frecuencia": "Una vez al día con jugo de frutas",
            "duracion_dias": 60
        }
    },
    {
        "paciente": {
            "nombre": 'Paciente Demo Pediatría 03',
            "dpi": '0000000000009',
            "fecha_nacimiento": "2018-11-25",
            "telefono": '00000009',
            "tutor_nombre": "Tutor de demostración 03",
            "tutor_telefono": '00000023',
            "genero": "Masculino"
        },
        "consulta": {
            "motivo": "Dolor ótico agudo derecho y fiebre de 38.5 grados tras episodio gripal",
            "profesional": "Dra. Sofía Castillo",
            "observaciones": "Otoscopia revela membrana timpánica derecha abombada y eritematosa."
        },
        "diagnostico": {
            "descripcion": "Otitis media aguda supurativa",
            "codigo_cie10": "H66.0"
        },
        "receta": {
            "medicamento": "Amoxicilina + Ácido Clavulánico 400/57mg suspensión",
            "dosis": "5 ml",
            "frecuencia": "Cada 12 horas con las comidas",
            "duracion_dias": 10
        }
    }
]

# --- CASOS CLÍNICOS SINTÉTICOS: ODONTOLOGÍA (Firebase) ---
PACIENTES_ODONTOLOGIA = [
    {
        "paciente": {
            "nombre": 'Paciente Demo Odontología 01',
            "dpi": '0000000000010',
            "fecha_nacimiento": "1997-06-18",
            "telefono": '00000010',
            "genero": "Femenino"
        },
        "consulta": {
            "motivo": "Sensibilidad marcada al frío en cuadrante superior izquierdo",
            "profesional": "Dra. Claudia Reyes",
            "observaciones": "Pieza 24 presenta filtración marginal en restauración de resina antigua."
        },
        "diagnostico": {
            "descripcion": "Caries secundaria (recurrente) de la dentina",
            "codigo_cie10": "K02.2"
        },
        "receta": {
            "medicamento": "Ketorolaco Trometamina 10mg sublingual",
            "dosis": "1 tableta sublingual",
            "frecuencia": "Cada 8 horas si hay dolor intenso",
            "duracion_dias": 3
        }
    },
    {
        "paciente": {
            "nombre": 'Paciente Demo Odontología 02',
            "dpi": '0000000000011',
            "fecha_nacimiento": "1993-12-04",
            "telefono": '00000011',
            "genero": "Masculino"
        },
        "consulta": {
            "motivo": "Sangrado gingival espontáneo durante el cepillado nocturno",
            "profesional": "Dr. Javier Méndez",
            "observaciones": "Presencia de cálculo dental supragingival moderado y encías edematosas."
        },
        "diagnostico": {
            "descripcion": "Gingivitis crónica por placa bacteriana",
            "codigo_cie10": "K05.1"
        },
        "receta": {
            "medicamento": "Gel Dental Clorhexidina al 0.20%",
            "dosis": "Aplicación tópica con hisopo",
            "frecuencia": "Cada 12 horas después del lavado",
            "duracion_dias": 14
        }
    },
    {
        "paciente": {
            "nombre": 'Paciente Demo Odontología 03',
            "dpi": '0000000000012',
            "fecha_nacimiento": "2001-09-22",
            "telefono": '00000012',
            "genero": "Femenino"
        },
        "consulta": {
            "motivo": "Dolor mandibular articular al abrir la boca (chasquido)",
            "profesional": "Dra. Claudia Reyes",
            "observaciones": "Tensión en músculos maseteros compatible con bruxismo nocturno."
        },
        "diagnostico": {
            "descripcion": "Trastorno de la articulación temporomandibular",
            "codigo_cie10": "K07.6"
        },
        "receta": {
            "medicamento": "Metocarbamol con Paracetamol tabletas",
            "dosis": "1 tableta",
            "frecuencia": "Cada noche antes de dormir",
            "duracion_dias": 7
        }
    }
]

def obtener_token(institucion: str) -> str:
    creds = CREDENCIALES[institucion]
    resp = requests.post(f"{BASE_URL}/auth/login", json=creds)
    if resp.status_code != 200:
        print(f"❌ Error al autenticar en {institucion}: {resp.status_code} - {resp.text}")
        sys.exit(1)
    return resp.json()["access_token"]

def registrar_institucion(institucion: str, lista_pacientes: list):
    print(f"\n{'='*60}")
    print(f"Cargando datos personalizados: {institucion.upper()}")
    print(f"{'='*60}")
    token = obtener_token(institucion)
    headers = {"Authorization": f"Bearer {token}"}

    for item in lista_pacientes:
        p = item["paciente"]
        rp = requests.post(f"{BASE_URL}/pacientes/", json=p, headers=headers)
        if rp.status_code not in (200, 201):
            print(f"  ❌ Fallo paciente {p['nombre']}: {rp.text}")
            continue
        pid = rp.json().get("id_paciente") or rp.json().get("id")
        print(f"  ✅ Paciente registrado: {p['nombre']} (ID: {pid})")

        c = item["consulta"].copy()
        c["id_paciente"] = str(pid)
        rc = requests.post(f"{BASE_URL}/consultas/", json=c, headers=headers)
        if rc.status_code not in (200, 201):
            print(f"     ❌ Fallo consulta: {rc.text}")
            continue
        cid = rc.json().get("id_consulta") or rc.json().get("id")
        print(f"     ✅ Consulta registrada (ID: {cid})")

        d = item["diagnostico"].copy()
        d["id_consulta"] = str(cid)
        rd = requests.post(f"{BASE_URL}/consultas/diagnostico", json=d, headers=headers)
        if rd.status_code in (200, 201):
            print(f"     ✅ Diagnóstico registrado ({d['codigo_cie10']})")

        r = item["receta"].copy()
        r["id_consulta"] = str(cid)
        rr = requests.post(f"{BASE_URL}/consultas/receta", json=r, headers=headers)
        if rr.status_code in (200, 201):
            print(f"     ✅ Receta prescrita ({r['medicamento']})")

if __name__ == "__main__":
    try:
        registrar_institucion("pediatria", PACIENTES_PEDIATRIA)
        registrar_institucion("odontologia", PACIENTES_ODONTOLOGIA)
        print("\n✅ Datos personalizados cargados exitosamente.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Servidor apagado en http://localhost:8000. Inicia uvicorn primero.")
