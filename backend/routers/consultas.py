from fastapi import APIRouter, Depends, HTTPException, status

from core.models import (
    ConsultaIn,
    ConsultaOut,
    DiagnosticoIn,
    DiagnosticoOut,
    RecetaIn,
    RecetaOut,
    TratamientoIn,
    EncuentroHospitalIn,
)
from core.routing import get_repository
from core.errors import ClinicalConflictError
from core.auth import get_current_institution, require_permission
from domain.ports import IRepository

router = APIRouter(prefix="/consultas", tags=["Consultas Clínicas"])


def _assert_split_hospital_write_allowed(institucion: str) -> None:
    if institucion == "hospital":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="En el Hospital General registre cita, consulta, diagnóstico, tratamiento y receta desde Atención integral para mantener la transacción atómica.",
        )


@router.post("/hospital/encuentro-completo", status_code=status.HTTP_201_CREATED)
def registrar_encuentro_hospitalario(
    datos: EncuentroHospitalIn,
    _user: dict = Depends(require_permission("clinical_write")),
    institucion: str = Depends(get_current_institution),
    repo: IRepository = Depends(get_repository),
):
    """Ruta hospitalaria: toda la cadena clínica se confirma o revierte junta."""
    if institucion != "hospital":
        raise HTTPException(status_code=403, detail="Esta operación integrada es exclusiva del Hospital General")
    try:
        return repo.registrar_encuentro_completo(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ConnectionError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar la atención integral; la transacción se revirtió.",
        ) from e


@router.post("/", response_model=ConsultaOut, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ConsultaOut, status_code=status.HTTP_201_CREATED)
def registrar_consulta(
    datos: ConsultaIn,
    _user: dict = Depends(require_permission("consultation")),
    institucion: str = Depends(get_current_institution),
    repo: IRepository = Depends(get_repository),
):
    _assert_split_hospital_write_allowed(institucion)
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
    institucion: str = Depends(get_current_institution),
    repo: IRepository = Depends(get_repository),
):
    _assert_split_hospital_write_allowed(institucion)
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
    institucion: str = Depends(get_current_institution),
    repo: IRepository = Depends(get_repository),
):
    _assert_split_hospital_write_allowed(institucion)
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
    institucion: str = Depends(get_current_institution),
    repo: IRepository = Depends(get_repository),
):
    _assert_split_hospital_write_allowed(institucion)
    try:
        return repo.registrar_tratamiento(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ConnectionError:
        raise

