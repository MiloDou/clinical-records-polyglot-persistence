from fastapi import APIRouter, Depends, HTTPException, status

from core.models import (
    ConsultaIn,
    ConsultaOut,
    DiagnosticoIn,
    DiagnosticoOut,
    RecetaIn,
    RecetaOut,
)
from core.routing import get_repository
from domain.ports import IRepository

router = APIRouter(prefix="/consultas", tags=["Consultas Clínicas"])


@router.post("/", response_model=ConsultaOut, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ConsultaOut, status_code=status.HTTP_201_CREATED)
def registrar_consulta(
    datos: ConsultaIn,
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.registrar_consulta(datos)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar consulta: {str(e)}",
        )


@router.post("/diagnostico", response_model=DiagnosticoOut, status_code=status.HTTP_201_CREATED)
def agregar_diagnostico(
    datos: DiagnosticoIn,
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.agregar_diagnostico(datos)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al agregar diagnóstico: {str(e)}",
        )


@router.post("/receta", response_model=RecetaOut, status_code=status.HTTP_201_CREATED)
def recetar_medicamento(
    datos: RecetaIn,
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.recetar_medicamento(datos)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al recetar medicamento: {str(e)}",
        )

