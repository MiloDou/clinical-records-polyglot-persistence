from fastapi import APIRouter, Depends, HTTPException, status

from core.auth import get_current_institution, require_permission
from core.models import CitaCambioIn, CitaIn
from core.routing import get_repository
from core.errors import ClinicalConflictError
from domain.ports import IRepository

router = APIRouter(prefix="/citas", tags=["Citas"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_cita(datos: CitaIn, _user: dict = Depends(require_permission("appointment")), institucion: str = Depends(get_current_institution), repo: IRepository = Depends(get_repository)):
    if institucion == "laboratorio":
        raise HTTPException(status_code=403, detail="El laboratorio no agenda citas")
    try:
        return repo.registrar_cita(datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/{id_cita}")
def cambiar_cita(id_cita: str, datos: CitaCambioIn, _user: dict = Depends(require_permission("appointment")), institucion: str = Depends(get_current_institution), repo: IRepository = Depends(get_repository)):
    if institucion == "laboratorio":
        raise HTTPException(status_code=403, detail="El laboratorio no agenda citas")
    if datos.fecha is None and datos.estado is None:
        raise HTTPException(status_code=422, detail="Indique fecha o estado")
    try:
        return repo.cambiar_cita(id_cita, datos)
    except ClinicalConflictError:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
