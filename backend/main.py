from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from routers import auth, consultas, historial, pacientes

app = FastAPI(
    title="Plataforma de Historiales Clínicos — Persistencia Políglota",
    description="Backend FastAPI con Arquitectura Hexagonal que orquesta 4 motores independientes: PostgreSQL (Hospital), MongoDB (Laboratorio), MySQL (Pediatría) y Firebase (Odontología).",
    version="2.0.0",
)

# Configuración de CORS para el cliente Vite / React en localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Errores de conectividad con cualquier motor -> 503 (no 400/500 genérico)
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(ConnectionError)
async def connection_error_handler(request: Request, exc: ConnectionError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


# Registrar routers
app.include_router(auth.router)
app.include_router(pacientes.router)
app.include_router(consultas.router)
app.include_router(historial.router)


@app.get("/", tags=["Sistema"])
def root():
    return {
        "sistema": "Plataforma de Historiales Clínicos · Persistencia Políglota",
        "universidad": "Universidad Rafael Landívar · Bases de Datos II",
        "entrega": "Entrega II",
        "motores": {
            "hospital": "PostgreSQL (clinica_poliglota, schema hospital)",
            "laboratorio": "MongoDB (laboratorio_db, colecciones pacientes y ordenes)",
            "pediatria": "MySQL (pediatria_db)",
            "odontologia": "Firebase Firestore (colecciones pacientes y atenciones)",
        },
        "docs": "/docs",
        "estado": "operativo",
    }


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

