"""
Pruebas end-to-end — Entrega II · Bases de Datos II · URL
Verifica el funcionamiento de los motores asignados.
- Hospital (PostgreSQL): Ronaldo / Emilio
- Laboratorio (MongoDB): Ronaldo / Emilio
- Pediatría (MySQL): Brayan
- Odontología (Firebase): Brayan

Uso:
cd Code/backend
source .venv/bin/activate
python tests/test_endpoints.py
"""
import requests
import secrets
import sys
import os

BASE = os.getenv("API_BASE", "http://localhost:8000")
INSTITUCIONES = {
    "hospital": {"usuario": "medico@hospital.gt", "password": "Test1234!", "dueno": "Ronaldo"},
    "laboratorio": {"usuario": "medico@laboratorio.gt", "password": "Test1234!", "dueno": "Ronaldo"},
    "pediatria": {"usuario": "medico@pediatria.gt", "password": "Test1234!", "dueno": "Brayan"},
    "odontologia": {"usuario": "odontologo@dental.gt", "password": "Test1234!", "dueno": "Brayan"},
}

ok_count, errores = 0, []


def ok(msg):
    global ok_count
    ok_count += 1
    print(f"✅ {msg}")


def falla(msg):
    print(f"❌ {msg}")
    errores.append(msg)


def info(msg):
    print(f"⏳ {msg}")


def prueba(nombre, credenciales):
    dueno = credenciales["dueno"]
    print(f"\n{'═'*55}")
    print(f" INSTITUCIÓN: {nombre.upper()} (Asignado a: {dueno})")
    print(f"{'═'*55}")

    # 1. Login
    r = requests.post(f"{BASE}/auth/login", json={"usuario": credenciales["usuario"], "password": credenciales["password"]})
    if r.status_code != 200:
        falla(f"[{nombre}] Login falló ({r.status_code}): {r.text[:120]}")
        return
    token = r.json().get("access_token")
    ok(f"[{nombre}] Login exitoso")
    H = {"Authorization": f"Bearer {token}"}
    wrong = requests.post(f"{BASE}/auth/login", json={"usuario": credenciales["usuario"], "password": "incorrecta"})
    if wrong.status_code == 401:
        ok(f"[{nombre}] Contraseña inválida rechazada")
    else:
        falla(f"[{nombre}] Contraseña inválida no fue rechazada ({wrong.status_code})")

    # 2. Registrar paciente
    payload = {
        "nombre": f"Paciente Prueba {nombre.title()} {secrets.token_hex(3)}",
        "dpi": str(1_000_000_000_000 + secrets.randbelow(9_000_000_000_000)),
        "fecha_nacimiento": "1995-06-20",
        "telefono": "55550000",
    }
    if nombre == "pediatria":
        payload["tutor_nombre"] = "Tutor de prueba"
        payload["tutor_telefono"] = "55550001"
    r = requests.post(f"{BASE}/pacientes/", json=payload, headers=H)
    if r.status_code == 501:
        info(f"[{nombre}] Módulo pendiente de implementación por {dueno}")
        return
    if r.status_code not in (200, 201):
        falla(f"[{nombre}] Registrar paciente ({r.status_code}): {r.text[:120]}")
        return
    pid = r.json().get("id_paciente") or r.json().get("id")
    ok(f"[{nombre}] Paciente registrado → id={pid}")

    # El flujo crítico del hospital se persiste de forma indivisible.
    integrated = requests.post(f"{BASE}/consultas/hospital/encuentro-completo", json={
        "id_paciente": pid, "fecha": "2026-11-08T10:30:00",
        "motivo": "Atención integral de prueba", "codigo_cie10": "Z00.0",
        "diagnostico": "Evaluación general", "tratamiento": "Control clínico",
        "indicaciones": "Seguimiento según evolución", "medicamento": "Paracetamol 500mg",
        "dosis": "1 tableta", "frecuencia": "Cada 8 horas", "duracion_dias": 3,
    }, headers=H)
    if nombre == "hospital":
        if integrated.status_code == 201 and all(integrated.json().get(k) for k in (
            "id_cita", "id_consulta", "id_diagnostico", "id_tratamiento", "id_receta"
        )):
            ok("[hospital] Atención integral guardada en una sola transacción")
        else:
            falla(f"[hospital] Atención integral ({integrated.status_code}): {integrated.text[:160]}")
    elif integrated.status_code == 403:
        ok(f"[{nombre}] Ruta de atención integral hospitalaria aislada")
    else:
        falla(f"[{nombre}] Ruta hospitalaria debió rechazar acceso ({integrated.status_code})")

    # 3. Buscar paciente por CUI
    r = requests.get(f"{BASE}/pacientes/buscar", params={"dpi": payload["dpi"]}, headers=H)
    if r.status_code == 200 and r.json():
        ok(f"[{nombre}] Búsqueda por CUI exitosa")
    else:
        falla(f"[{nombre}] Búsqueda por CUI ({r.status_code})")
    r = requests.get(f"{BASE}/pacientes/buscar", params={"nombre": payload["nombre"]}, headers=H)
    if r.status_code == 200 and any(
        str(coincidencia.get("id_paciente") or coincidencia.get("id")) == str(pid)
        for coincidencia in r.json()
    ):
        ok(f"[{nombre}] Búsqueda parcial por nombre exitosa")
    else:
        falla(f"[{nombre}] Búsqueda por nombre ({r.status_code}): {r.text[:120]}")
    r = requests.get(f"{BASE}/pacientes/buscar", params={"dpi": "9999999999999"}, headers=H)
    if r.status_code == 404:
        ok(f"[{nombre}] Paciente inexistente devuelve 404")
    else:
        falla(f"[{nombre}] Paciente inexistente devolvió {r.status_code}")

    if nombre == "hospital":
        blocked = requests.post(f"{BASE}/consultas/", json={
            "id_paciente": pid, "motivo": "No debe persistirse por separado"
        }, headers=H)
        if blocked.status_code == 409:
            ok("[hospital] Escrituras clínicas separadas bloqueadas para preservar atomicidad")
        else:
            falla(f"[hospital] Escritura clínica separada no bloqueada ({blocked.status_code})")
        cid = integrated.json().get("id_consulta") if integrated.status_code == 201 else None
        before = requests.get(f"{BASE}/historial/{pid}", headers=H)
        rollback = requests.post(f"{BASE}/consultas/hospital/encuentro-completo", json={
            "id_paciente": pid, "fecha": "2026-11-08T11:30:00",
            "motivo": "Prueba de reversión", "codigo_cie10": "Z00.0",
            "diagnostico": "No debe persistir", "tratamiento": "No debe persistir",
            "medicamento": "X" * 101, "dosis": "1", "frecuencia": "Una vez", "duracion_dias": 1,
        }, headers=H)
        after = requests.get(f"{BASE}/historial/{pid}", headers=H)
        keys = ("consultas", "citas", "diagnosticos", "tratamientos", "recetas")
        rolled_back = (rollback.status_code == 500 and before.status_code == after.status_code == 200
                       and all(len(before.json().get(k, [])) == len(after.json().get(k, [])) for k in keys))
        if rolled_back:
            ok("[hospital] Fallo intermedio revierte toda la cadena sin registros parciales")
        else:
            falla(f"[hospital] Reversión incompleta (HTTP {rollback.status_code})")
    else:
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
        r = requests.post(f"{BASE}/consultas/diagnostico", json={
            "id_consulta": "999999999", "descripcion": "No existe", "codigo_cie10": "Z00.0"
        }, headers=H)
        if r.status_code == 404:
            ok(f"[{nombre}] Consulta inexistente devuelve 404")
        else:
            falla(f"[{nombre}] Consulta inexistente devolvió {r.status_code}")

        r = requests.post(f"{BASE}/consultas/tratamiento", json={
            "id_consulta": cid, "descripcion": "Plan de comprobación",
            "indicaciones": "Seguimiento de comprobación"
        }, headers=H)
        if r.status_code == 201:
            ok(f"[{nombre}] Tratamiento estructurado guardado")
        else:
            falla(f"[{nombre}] Tratamiento ({r.status_code}): {r.text[:120]}")

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

    if nombre != "laboratorio":
        r = requests.post(f"{BASE}/citas/", json={
            "id_paciente": pid, "fecha": "2026-12-10T10:00:00", "servicio": "Control de prueba"
        }, headers=H)
        if r.status_code == 201:
            ok(f"[{nombre}] Cita programada")
            appointment = str(r.json()["id_cita"])
            r = requests.patch(f"{BASE}/citas/{appointment}",
                               json={"estado": "cancelada"}, headers=H)
            if r.status_code == 200:
                ok(f"[{nombre}] Cita cancelada")
            else:
                falla(f"[{nombre}] Cancelar cita ({r.status_code})")
        else:
            falla(f"[{nombre}] Programar cita ({r.status_code}): {r.text[:120]}")
    if nombre == "laboratorio":
        r = requests.post(f"{BASE}/especialidades/laboratorio/resultados", json={
            "id_consulta": cid,
            "resultados_parametros": [{"parametro": "Hemoglobina", "valor": "13.5", "unidad": "g/dL"}]
        }, headers=H)
        if r.status_code == 201:
            ok("[laboratorio] Resultado medido guardado")
        else:
            falla(f"[laboratorio] Resultado ({r.status_code}): {r.text[:120]}")
    if nombre == "odontologia":
        r = requests.post(f"{BASE}/especialidades/odontologia/procedimientos", json={
            "id_consulta": cid, "pieza": "36", "procedimiento": "Resina de prueba"
        }, headers=H)
        if r.status_code == 201:
            ok("[odontologia] Procedimiento dental guardado")
        else:
            falla(f"[odontologia] Procedimiento ({r.status_code}): {r.text[:120]}")
    if nombre == "pediatria":
        for path, payload, label in (
            ("/especialidades/pediatria/crecimiento",
             {"id_paciente": pid, "peso_kg": 21.2, "talla_cm": 119.4}, "Crecimiento"),
            ("/especialidades/pediatria/vacunas",
             {"id_paciente": pid, "nombre_vacuna": "Vacuna de prueba", "dosis": "Primera"}, "Vacuna"),
        ):
            r = requests.post(BASE + path, json=payload, headers=H)
            if r.status_code == 201:
                ok(f"[pediatria] {label} guardado")
            else:
                falla(f"[pediatria] {label} ({r.status_code}): {r.text[:120]}")

    # 7. Ver historial completo
    r = requests.get(f"{BASE}/historial/{pid}", headers=H)
    expected_keys = ["consultas", "diagnosticos", "recetas", "tratamientos"]
    expected_keys += {
        "laboratorio": ["examenes_laboratorio"],
        "odontologia": ["citas", "procedimientos_dentales"],
        "pediatria": ["citas", "controles_crecimiento", "vacunas"],
        "hospital": ["citas"],
    }[nombre]
    if r.status_code == 200 and all(len(r.json().get(key, [])) >= 1 for key in expected_keys):
        ok(f"[{nombre}] Historial consultado")
    else:
        falla(f"[{nombre}] Historial ({r.status_code}): {r.text[:120]}")
    r = requests.get(f"{BASE}/historial/999999999", headers=H)
    if r.status_code == 404:
        ok(f"[{nombre}] Historial inexistente devuelve 404")
    else:
        falla(f"[{nombre}] Historial inexistente devolvió {r.status_code}")

    # 8. Archivar historial
    r = requests.patch(f"{BASE}/pacientes/{pid}/archivar", headers=H)
    if r.status_code == 200:
        ok(f"[{nombre}] Historial archivado")
    else:
        falla(f"[{nombre}] Archivar ({r.status_code}): {r.text[:120]}")
    if nombre == "hospital":
        r = requests.post(f"{BASE}/consultas/hospital/encuentro-completo", json={
            "id_paciente": pid, "fecha": "2026-11-08T12:30:00",
            "motivo": "Debe rechazarse", "codigo_cie10": "Z00.0",
            "diagnostico": "No debe guardarse", "tratamiento": "No debe guardarse",
            "medicamento": "Paracetamol", "dosis": "1", "frecuencia": "Una vez", "duracion_dias": 1,
        }, headers=H)
        blocked_status = 409
    else:
        r = requests.post(f"{BASE}/consultas/", json={
            "id_paciente": pid, "motivo": "Debe rechazarse"
        }, headers=H)
        blocked_status = 409
    if r.status_code == blocked_status:
        ok(f"[{nombre}] Historial archivado bloquea escrituras")
    else:
        falla(f"[{nombre}] Historial archivado permitió escritura ({r.status_code})")


if __name__ == "__main__":
    print("\n🔬 Pruebas end-to-end — Entrega II · URL")
    print(f" Servidor: {BASE}\n")
    selected = set(filter(None, os.getenv("TEST_INSTITUTIONS", "").split(",")))
    for inst, creds in INSTITUCIONES.items():
        if selected and inst not in selected:
            continue
        prueba(inst, creds)

    total = ok_count + len(errores)
    print(f"\n{'═'*55}")
    print(f"Resultado: {ok_count} pruebas pasaron exitosamente.")
    if not errores:
        print("✅ Las partes implementadas pasaron todas las pruebas.")
    else:
        print(f"❌ {len(errores)} error(es) pendiente(s):\n")
        for e in errores:
            print(f" • {e}")
        sys.exit(1)
