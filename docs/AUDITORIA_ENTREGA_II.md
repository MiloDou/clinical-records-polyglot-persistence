# Auditoría técnica — Entrega II (Persistencia Políglota · Arquitectura Hexagonal)

Fecha: 2026-11-07 · Rama: `backend` · HEAD: `60a7f15`
Auditor: sesión de Claude Code a pedido de Benjamín · Destinatario: Ronaldo (Milo)

> **Snapshot histórico, sustituido.** Este informe describe el estado del 7 de noviembre y no la entrega actual. La evidencia vigente está en [`Documento_Comparativo_Entrega_II.pdf`](Documento_Comparativo_Entrega_II.pdf) y [`README.md`](../README.md); incluye la búsqueda por nombre y la corrida de 70/70 del 8 de noviembre de 2026.

> **Veredicto backend: ✅ 32/32 en verde** (segunda corrida, con MongoDB y MySQL levantados). En la primera corrida, con
> Docker apagado, Laboratorio y Pediatría devolvieron 503 reales, lo que confirma el manejo de caídas. Pendientes: frontend
> **sin commitear** y ciclo GUI no verificado en navegador. Detalles abajo.

---

## PARTE 1 — Verificación en vivo

### 1. Motores de persistencia

| Institución | Motor | Resultado en vivo | Observaciones |
|---|---|---|---|
| Hospital General | PostgreSQL `clinica_poliglota` | ✅ 8/8 | Login, alta, búsqueda DPI, consulta, diagnóstico, receta, historial, archivo. |
| Lab. Clínico | MongoDB `laboratorio_db` | ✅ 8/8 (corrida 2); 503 real con servicio caído (corrida 1) | `No servers found yet` en `localhost:27017`. **El 503 real funciona** (no existe ya `InMemoryMongoCollection`: búsqueda en el código = 0 coincidencias). |
| C. M. Pediátrico | MySQL `pediatria_db` (Docker) | ✅ 8/8 (corrida 2); 503 real con servicio caído (corrida 1) | `2003 Can't connect to MySQL server on localhost:3306`. Docker daemon apagado. |
| Clínica Odontológica | Firestore (`serviceAccountKey.json`) | ✅ 8/8 | Conexión real al proyecto en la nube (IDs de documento tipo `SKktKACu4BSAIMRcKE4B`). |

### 2. Backend FastAPI

- **Suite e2e** `backend/tests/test_endpoints.py`: 8 operaciones × 4 instituciones = 32 pasos. Corrida 1 (motores caídos): 18 OK + 2 × 503. Corrida 2 (todos arriba): **32/32 OK**.
  - ⚠️ La suite **no contiene casos 404**. Los 404 existen en `routers/consultas.py`, `routers/historial.py` y `routers/pacientes.py`, pero no hay prueba automatizada que los cubra. La afirmación “32/32 incluye 404” no es exacta.
- **JWT / login**: no hay bypass (no se acepta contraseña genérica; usuario inexistente → `None`). `verify_password` usa `hmac.compare_digest` ✅.
  - ⚠️ Compara **texto plano contra texto plano**: `USUARIOS_DB` en `core/auth.py` guarda `"Test1234!"` sin hash. Es tiempo constante, pero no es “comparación de hashes”. Recomendado: guardar un hash (p. ej. `hashlib.pbkdf2_hmac` o `passlib[bcrypt]`) y comparar el digest.
  - ⚠️ `JWT_SECRET` tiene un valor por defecto en el código; en producción debe venir siempre de `.env`.
- **CORS** (`main.py`): `allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]` ✅.

### 3. Frontend React + Vite

- `src/App.tsx` usa el cliente `apiRequest` (9 usos: login, historial, búsqueda DPI, alta, etc.). Búsqueda de `showUnavailable` / “Sin conexión” en `src/` = 0 coincidencias ✅.
- `npx tsc -b --noEmit` compila sin errores ✅.
- `src/styles.css`: `--rail: 264px` presente ✅.
- ⚠️ **No verificado en navegador**: el ciclo clínico por GUI y el refresco de contadores `(0) → (1)` no se probaron en esta auditoría (dos de los cuatro motores estaban caídos). Debe hacerse con el checklist de la Parte 3.
- ⚠️ Los cambios de `src/App.tsx`, `src/domain/institutions.ts` y `src/styles.css` (**+463 / −317**) están **sin commitear**.

---

## PARTE 2 — Reporte de cambios

### Backend (ya commiteado en `backend`)
- `adapters/hospital_postgres.py`: soporte unicode en psycopg2, decodificación tolerante de conexión/tokens (`53d87e9`).
- `adapters/laboratorio_mongo.py`: eliminado el respaldo en memoria; caída del servicio → **503** real (`dbd7d17`).
- `adapters/odontologia_firebase.py`: errores de red/credenciales → 503; documento inexistente → 404 (`dbd7d17`).
- `adapters/pediatria_mysql.py`: persistencia MySQL completa + seed (`f6c1cc1`, `1cbbf8b`).
- `core/auth.py`: cierre del bypass de login, `hmac.compare_digest` (`dbd7d17`).
- `routers/consultas.py`, `historial.py`, `pacientes.py`: `ValueError`/no encontrado → 404 consistente.

### Frontend (pendiente de commit)
- `src/App.tsx`: cliente `apiRequest` con token Bearer; formularios conectados a `/auth/login`, `/pacientes/`, `/pacientes/buscar`, `/historial/{id}`, consultas/diagnósticos/recetas; estados de error enlazados a las respuestas 404/503.
- `src/domain/institutions.ts`: metadatos de institución alineados a los slugs del backend.
- `src/styles.css`: riel lateral fijo de 264 px y contraste de textos inactivos.

### Git y PR
- Últimos commits: `60a7f15` merge · `1b28f18` ignore SQL · `1cbbf8b` seed · `dbd7d17` 503/404/bypass · `f0de89a` dump postgres.
- **PR Draft**: no se pudo confirmar (la CLI `gh` no está instalada en esta máquina). Revisar en GitHub que el PR `backend → main` siga en *Draft* (R‑05).
- `.gitignore`: `.env`, `*.env`, `serviceAccountKey.json`, `.venv/` ✅ (raíz y `backend/`). Ninguno está trackeado ✅.
  - ⚠️ **`.claude/` NO está en `.gitignore`** (aparece como no rastreado). Agregarlo.
  - ⚠️ `backend/scripts/postgres_localhost-...-dump.sql` **sigue trackeado** aunque `*.sql` está ignorado (se agregó antes de la regla). Si se quiere excluir: `git rm --cached` de ese archivo. Si se quiere conservar para restaurar el esquema, dejarlo y documentarlo.

### Pendientes para declarar 100 %
1. ~~Levantar Docker (MySQL) y MongoDB, re‑ejecutar la suite~~ → ✅ 32/32 confirmado.
2. Commitear el frontend y agregar `.claude/` al `.gitignore`.
3. Probar el ciclo clínico en la GUI en las 4 instituciones.
4. (Recomendado) agregar casos 404 a la suite y hashear las contraseñas de `USUARIOS_DB`.

---

## PARTE 3 — Guía de despliegue para Ronaldo

### 1. Actualizar la rama
```bash
git fetch origin
git checkout backend
git pull origin backend
```

### 2. `.env` y servicios
```bash
cp backend/.env.example backend/.env
```
Variables requeridas: `PG_HOST PG_PORT PG_USER PG_PASSWORD PG_DB=clinica_poliglota`,
`MYSQL_HOST MYSQL_PORT MYSQL_USER MYSQL_PASSWORD MYSQL_DB=pediatria_db`,
`MONGO_URI=mongodb://localhost:27017 MONGO_DB=laboratorio_db`,
`FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json`, `JWT_SECRET JWT_ALGORITHM JWT_EXPIRE_MINUTES`.
Pedir `serviceAccountKey.json` por canal privado y colocarlo en `backend/` (nunca commitearlo).

Servicios: PostgreSQL en 5432 con la base `clinica_poliglota` (restaurable desde `backend/scripts/*.sql`), Docker Desktop encendido con MySQL en 3306, MongoDB en 27017.

### 3. Backend + pruebas
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
En otra terminal:
```bash
cd backend
.venv\Scripts\python tests/test_endpoints.py
```
Esperado: `Resultado: 32 pruebas pasaron exitosamente.` Un 503 indica motor apagado, no error de código.

### 4. Frontend
```bash
npm install
npm run dev
```
Abrir `http://localhost:5173`. Usuarios (contraseña `Test1234!` para todos):

| Institución | Usuario |
|---|---|
| Hospital | `medico@hospital.gt` |
| Laboratorio | `tecnico@laboratorio.gt` |
| Pediatría | `medico@pediatria.gt` |
| Odontología | `secretaria@dental.gt` |

Checklist por institución: registrar paciente → buscar por DPI → registrar consulta → agregar diagnóstico → prescribir receta → verificar que los contadores del historial suben `(0) → (1)` → archivar historial.
