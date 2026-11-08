from fastapi import APIRouter, Depends, HTTPException, status

from core.models import (
    ConsultaIn,
    ConsultaOut,
    DiagnosticoIn,
    DiagnosticoOut,
    RecetaIn,
    RecetaOut,
    TratamientoIn,
)
from core.routing import get_repository
from core.errors import ClinicalConflictError
from core.auth import require_permission
from domain.ports import IRepository

router = APIRouter(prefix="/consultas", tags=["Consultas Clínicas"])


@router.post("/", response_model=ConsultaOut, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ConsultaOut, status_code=status.HTTP_201_CREATED)
def registrar_consulta(
    datos: ConsultaIn,
    _user: dict = Depends(require_permission("consultation")),
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.registrar_consulta(datos)
    except ClinicalConflictError:
        raise
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
    _user: dict = Depends(require_permission("clinical_write")),
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.agregar_diagnostico(datos)
    except ClinicalConflictError:
        raise
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
    _user: dict = Depends(require_permission("clinical_write")),
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.recetar_medicamento(datos)
    except ClinicalConflictError:
        raise
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


@router.post("/tratamiento", status_code=status.HTTP_201_CREATED)
def registrar_tratamiento(
    datos: TratamientoIn,
    _user: dict = Depends(require_permission("clinical_write")),
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.registrar_tratamiento(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ConnectionError:
        raise

