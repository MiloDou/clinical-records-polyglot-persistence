from fastapi import APIRouter, Depends, HTTPException, status

from core.models import HistorialOut
from core.routing import get_repository
from domain.ports import IRepository

router = APIRouter(prefix="/historial", tags=["Historial Clínico"])


@router.get("/{id_paciente}", response_model=HistorialOut)
def obtener_historial_completo(
    id_paciente: str,
    repo: IRepository = Depends(get_repository),
):
    try:
        return repo.get_historial(id_paciente)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar historial clínico: {str(e)}",
        )
