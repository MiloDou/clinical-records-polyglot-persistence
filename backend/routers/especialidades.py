from fastapi import APIRouter, Depends, HTTPException, status

from core.auth import get_current_institution, require_permission
from core.models import ControlCrecimientoIn, ProcedimientoDentalIn, ResultadoLaboratorioIn, VacunaAplicadaIn
from core.routing import get_repository
from core.errors import ClinicalConflictError
from domain.ports import IRepository

router = APIRouter(prefix="/especialidades", tags=["Módulos clínicos"])


def _require(actual: str, expected: str):
    if actual != expected:
        raise HTTPException(status_code=403, detail="Operación no disponible para esta institución")


@router.post("/laboratorio/resultados", status_code=status.HTTP_201_CREATED)
def registrar_resultados(datos: ResultadoLaboratorioIn, _user: dict = Depends(require_permission("lab_result")), institucion: str = Depends(get_current_institution), repo: IRepository = Depends(get_repository)):
    _require(institucion, "laboratorio")
    try:
        return repo.registrar_resultados(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/odontologia/procedimientos", status_code=status.HTTP_201_CREATED)
def registrar_procedimiento(datos: ProcedimientoDentalIn, _user: dict = Depends(require_permission("dental_procedure")), institucion: str = Depends(get_current_institution), repo: IRepository = Depends(get_repository)):
    _require(institucion, "odontologia")
    try:
        return repo.registrar_procedimiento(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/pediatria/crecimiento", status_code=status.HTTP_201_CREATED)
def registrar_control(datos: ControlCrecimientoIn, _user: dict = Depends(require_permission("pediatric_write")), institucion: str = Depends(get_current_institution), repo: IRepository = Depends(get_repository)):
    _require(institucion, "pediatria")
    try:
        return repo.registrar_control(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/pediatria/vacunas", status_code=status.HTTP_201_CREATED)
def registrar_vacuna(datos: VacunaAplicadaIn, _user: dict = Depends(require_permission("pediatric_write")), institucion: str = Depends(get_current_institution), repo: IRepository = Depends(get_repository)):
    _require(institucion, "pediatria")
    try:
        return repo.registrar_vacuna(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
