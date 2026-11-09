import re
from typing import Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.models import PacienteIn, PacienteOut
from core.routing import get_repository
from core.errors import ClinicalConflictError
from core.auth import require_permission
from domain.ports import IRepository

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post("/", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def registrar_paciente(
    datos: PacienteIn,
    _user: dict = Depends(require_permission("patient_write")),
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.registrar_paciente(datos)
    except ClinicalConflictError:
        raise
    except ConnectionError:
        raise
    except Exception as e:
        safe_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar paciente: {safe_msg}",
        )


@router.get("/buscar", response_model=Union[PacienteOut, List[PacienteOut]])
def buscar_paciente(
    dpi: Optional[str] = Query(None, description="DPI o CUI del paciente a buscar"),
    nombre: Optional[str] = Query(None, min_length=2, max_length=120, description="Coincidencia parcial del nombre"),
    _user: dict = Depends(require_permission("patient_read")),
    repo: IRepository = Depends(get_repository),
):
    if (dpi is None) == (nombre is None):
        raise HTTPException(status_code=422, detail="Indique exactamente uno de estos criterios: dpi o nombre")

    if nombre is not None:
        termino = " ".join(nombre.split())
        if len(termino) < 2:
            raise HTTPException(status_code=422, detail="Escriba al menos 2 caracteres del nombre")
        pacientes = repo.buscar_pacientes_por_nombre(termino)
        if not pacientes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron pacientes cuyo nombre coincida con '{termino}'",
            )
        return pacientes

    cui = "".join(char for char in dpi if char not in " .-")
    if not re.fullmatch(r"[0-9]{13}", cui):
        raise HTTPException(status_code=422, detail="El CUI debe contener exactamente 13 dígitos")
    paciente = repo.buscar_paciente(cui)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún paciente con el DPI '{dpi}'",
        )
    return paciente


@router.patch("/{id_paciente}/archivar")
def archivar_historial(
    id_paciente: str,
    _user: dict = Depends(require_permission("archive")),
    repo: IRepository = Depends(get_repository),
):
    exito = repo.archivar_historial(id_paciente)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se pudo archivar el paciente {id_paciente} o no existe",
        )
    return {
        "mensaje": "Historial clínico archivado exitosamente",
        "id_paciente": id_paciente,
        "archivado": True,
    }

