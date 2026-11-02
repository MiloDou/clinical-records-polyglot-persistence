"""
Pruebas end-to-end — Entrega II · Bases de Datos II · URL
Verifica que los 4 motores respondan correctamente.
Uso:
cd Code/backend
source .venv/bin/activate
python tests/test_endpoints.py
"""
import requests
import sys

BASE = "http://localhost:8000"
INSTITUCIONES = {
    "hospital": {"usuario": "medico@hospital.gt", "password": "Test1234!"},
    "pediatria": {"usuario": "medico@pediatria.gt", "password": "Test1234!"},
    "laboratorio": {"usuario": "tecnico@laboratorio.gt", "password": "Test1234!"},
    "odontologia": {"usuario": "secretaria@dental.gt", "password": "Test1234!"},
}

ok_count, errores = 0, []


def ok(msg):
    global ok_count
    ok_count += 1
    print(f"✅ {msg}")


def falla(msg):
    print(f"❌ {msg}")
    errores.append(msg)


def prueba(nombre, credenciales):
    print(f"\n{'═'*55}")
    print(f" INSTITUCIÓN: {nombre.upper()}")
    print(f"{'═'*55}")

    # 1. Login
    r = requests.post(f"{BASE}/auth/login", json=credenciales)
    if r.status_code != 200:
        falla(f"[{nombre}] Login falló ({r.status_code}): {r.text[:120]}")
        return
    token = r.json().get("access_token")
    ok(f"[{nombre}] Login exitoso")
    H = {"Authorization": f"Bearer {token}"}

    # 2. Registrar paciente
    payload = {
        "nombre": f"Paciente Test {nombre.title()}",
        "dpi": f"TEST{nombre[:4].upper()}0001",
        "fecha_nacimiento": "1995-06-20",
        "telefono": "55550000",
    }
    r = requests.post(f"{BASE}/pacientes/", json=payload, headers=H)
    if r.status_code not in (200, 201):
        falla(f"[{nombre}] Registrar paciente ({r.status_code}): {r.text[:120]}")
        return
    pid = r.json().get("id_paciente") or r.json().get("id")
    ok(f"[{nombre}] Paciente registrado → id={pid}")

    # 3. Buscar paciente por DPI
    r = requests.get(f"{BASE}/pacientes/buscar", params={"dpi": payload["dpi"]}, headers=H)
    if r.status_code == 200 and r.json():
        ok(f"[{nombre}] Búsqueda por DPI exitosa")
    else:
        falla(f"[{nombre}] Búsqueda por DPI ({r.status_code})")

    # 4. Registrar consulta
    r = requests.post(
        f"{BASE}/consultas/",
        json={
            "id_paciente": pid,
            "motivo": "Control de rutina — prueba automática",
            "profesional": "Dr. Sistema",
        },
        headers=H,
    )
    if r.status_code not in (200, 201):
        falla(f"[{nombre}] Registrar consulta ({r.status_code}): {r.text[:120]}")
        return
    cid = r.json().get("id_consulta") or r.json().get("id")
    ok(f"[{nombre}] Consulta registrada → id={cid}")

    # 5. Agregar diagnóstico
    r = requests.post(
        f"{BASE}/consultas/diagnostico",
        json={
            "id_consulta": cid,
            "descripcion": "Sin hallazgos patológicos",
            "codigo_cie10": "Z00.0",
        },
        headers=H,
    )
    if r.status_code in (200, 201):
        ok(f"[{nombre}] Diagnóstico agregado")
    else:
        falla(f"[{nombre}] Diagnóstico ({r.status_code}): {r.text[:120]}")

    # 6. Recetar medicamento
    r = requests.post(
        f"{BASE}/consultas/receta",
        json={
            "id_consulta": cid,
            "medicamento": "Paracetamol 500mg",
            "dosis": "1 tableta",
            "frecuencia": "Cada 8 horas",
            "duracion_dias": 5,
        },
        headers=H,
    )
    if r.status_code in (200, 201):
        ok(f"[{nombre}] Receta registrada")
    else:
        falla(f"[{nombre}] Receta ({r.status_code}): {r.text[:120]}")

    # 7. Ver historial completo
    r = requests.get(f"{BASE}/historial/{pid}", headers=H)
    if r.status_code == 200 and r.json():
        ok(f"[{nombre}] Historial consultado")
    else:
        falla(f"[{nombre}] Historial ({r.status_code}): {r.text[:120]}")

    # 8. Archivar historial
    r = requests.patch(f"{BASE}/pacientes/{pid}/archivar", headers=H)
    if r.status_code == 200:
        ok(f"[{nombre}] Historial archivado")
    else:
        falla(f"[{nombre}] Archivar ({r.status_code}): {r.text[:120]}")


if __name__ == "__main__":
    print("\n🔬 Pruebas end-to-end — Entrega II · URL")
    print(f" Servidor: {BASE}\n")
    for inst, creds in INSTITUCIONES.items():
        prueba(inst, creds)

    total = ok_count + len(errores)
    print(f"\n{'═'*55}")
    print(f"Resultado: {ok_count}/{total} pruebas pasaron\n")
    if not errores:
        print("✅ TODO LISTO — aplicación lista para la demo")
    else:
        print(f"❌ {len(errores)} error(es) pendiente(s):\n")
        for e in errores:
            print(f" • {e}")
        sys.exit(1)
