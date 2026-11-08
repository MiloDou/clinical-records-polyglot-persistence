# Plataforma de historiales clínicos

Proyecto académico cliente-servidor con React, FastAPI y cuatro adaptadores de persistencia:
hospital → PostgreSQL, pediatría → MySQL, laboratorio → MongoDB y odontología → Firestore.
La institución se obtiene del usuario autenticado; el navegador no contiene contraseñas.

## Preparar las bases

Clona la rama de entrega y trabaja desde la carpeta del repositorio:

```bash
git clone --branch backend --single-branch https://github.com/MiloDou/clinical-records-polyglot-persistence.git
cd clinical-records-polyglot-persistence
```

Prepara los cuatro motores antes de iniciar la API:

1. **PostgreSQL.** En una instalación nueva, crea `clinica_poliglota` y restaura
   `backend/scripts/postgres_localhost-2026_09_06_17_23_24-dump.sql`:
   `createdb -U postgres clinica_poliglota` y después
   `psql -U postgres -d clinica_poliglota < backend/scripts/postgres_localhost-2026_09_06_17_23_24-dump.sql`.
   No reimportes el dump sobre una base que ya contiene expedientes.
2. **MySQL 8.** Ejecuta `mysql -u root -p < backend/scripts/mysql_pediatria.sql`.
   El script crea el esquema `pediatria_db` y sus tablas con `CREATE TABLE IF NOT EXISTS`.
3. **MongoDB.** Inicia el servidor local o un contenedor vacío:
   `docker run -d --name mongo-laboratorio -p 127.0.0.1:27017:27017 mongo:latest`.
   Las colecciones se crean al primer registro.
4. **Firestore.** Habilita Firestore en el proyecto y coloca la credencial de servicio en
   `backend/serviceAccountKey.json`. Este archivo se obtiene desde Firebase Console;
   no está ni debe estar en GitHub. `FIREBASE_CREDENTIALS_PATH`
   en `backend/.env` acepta una ruta absoluta o una ruta relativa a `backend/`.
   Solo el backend usa Firebase Admin; el frontend llama a FastAPI.

## Configuración

Copia `backend/.env.example` a `backend/.env` y ajusta conexiones y
`JWT_SECRET` (una cadena aleatoria larga, distinta de cualquier ejemplo).
El archivo `Code/.env` solo define `VITE_API_URL` para el cliente. Los dos
archivos cumplen funciones distintas. Si `JWT_SECRET` queda vacío, el servidor
genera uno efímero y las sesiones se invalidan al reiniciar.

## Ejecutar

Linux/macOS (Windows: usa `.venv\Scripts\activate` para activar el entorno y
`.venv\Scripts\python` para ejecutar Python):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

En otra terminal, desde `Code`:

```bash
npm ci
npm run dev
```

Abre `http://localhost:5173`. El acceso muestra una pantalla de inicio de
sesión; la institución se selecciona automáticamente a partir de la cuenta.

## Cuentas locales de demostración

La contraseña de las seis cuentas es `Test1234!`. Las contraseñas se almacenan
como hash PBKDF2 en el backend; estas cuentas son exclusivamente para la demo,
no para desplegar con pacientes reales.

| Institución | Cuenta | Permisos principales |
|---|---|---|
| Hospital | `medico@hospital.gt` | Atención clínica y archivo |
| Pediatría | `medico@pediatria.gt` | Atención, crecimiento, vacunas y archivo |
| Laboratorio | `tecnico@laboratorio.gt` | Pacientes, órdenes y resultados |
| Laboratorio | `medico@laboratorio.gt` | Atención clínica y archivo |
| Odontología | `secretaria@dental.gt` | Pacientes y citas; historial clínico redactado |
| Odontología | `odontologo@dental.gt` | Atención, procedimientos y archivo |

## Verificar

La suite de integración crea expedientes **sintéticos**, verifica lectura y
operaciones clínicas, y termina archivándolos. Desde `Code/backend`:

```bash
./.venv/bin/python tests/test_endpoints.py
```

Si todavía falta Firestore, prueba los tres motores disponibles:

```bash
TEST_INSTITUTIONS=hospital,pediatria,laboratorio ./.venv/bin/python tests/test_endpoints.py
```

La prueba local del adaptador odontológico no necesita credenciales y **no**
sustituye una prueba de integración con Firestore real:

```bash
./.venv/bin/python -m unittest tests.test_firestore_adapter -v
```

Para verificar el cliente: `npm run build`. Para una comprobación rápida
del servidor: `curl http://127.0.0.1:8000/health`. La última verificación
completa, con los cuatro motores activos, aprobó 66/66 pruebas. En la repetición
del 8 de noviembre de 2026, 53 pasaron y MongoDB devolvió 503 porque Docker no
estaba disponible; se documenta para distinguir una dependencia apagada de un
fallo del adaptador.

## Alcance y límites

Los cuatro motores exponen registro, búsqueda, consulta, diagnóstico, tratamiento,
receta, historial y archivo. Hospital, pediatría y odontología también manejan
citas separadas; pediatría registra crecimiento y vacunas en tablas; laboratorio
guarda resultados variables dentro de la orden; odontología guarda procedimientos
en la atención. Las operaciones separadas por peticiones HTTP no forman una sola
transacción global.

El sistema usa cuentas de demostración; antes de manejar información real se
requiere un almacén de usuarios administrable, políticas de acceso y auditoría,
cifrado y revisión de privacidad. El chequeo `/health` solo indica que la API
responde, no que las cuatro bases estén disponibles.
