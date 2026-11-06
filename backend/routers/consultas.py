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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConnectionError:
        raise
    except Exception as e:
        safe_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar consulta: {safe_msg}",
        )


@router.post("/diagnostico", response_model=DiagnosticoOut, status_code=status.HTTP_201_CREATED)
def agregar_diagnostico(
    datos: DiagnosticoIn,
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.agregar_diagnostico(datos)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConnectionError:
        raise
    except Exception as e:
        safe_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al agregar diagnóstico: {safe_msg}",
        )


@router.post("/receta", response_model=RecetaOut, status_code=status.HTTP_201_CREATED)
def recetar_medicamento(
    datos: RecetaIn,
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.recetar_medicamento(datos)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConnectionError:
        raise
    except Exception as e:
        safe_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al recetar medicamento: {safe_msg}",
        )

