from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.models import PacienteIn, PacienteOut
from core.routing import get_repository
from domain.ports import IRepository

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post("/", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def registrar_paciente(
    datos: PacienteIn,
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.registrar_paciente(datos)
    except Exception as e:
        safe_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar paciente: {safe_msg}",
        )


@router.get("/buscar", response_model=PacienteOut)
def buscar_paciente_por_dpi(
    dpi: str = Query(..., description="DPI o CUI del paciente a buscar"),
    repo: IRepository = Depends(get_repository),
):
    paciente = repo.buscar_paciente(dpi)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún paciente con el DPI '{dpi}'",
        )
    return paciente


@router.patch("/{id_paciente}/archivar")
def archivar_historial(
    id_paciente: str,
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

