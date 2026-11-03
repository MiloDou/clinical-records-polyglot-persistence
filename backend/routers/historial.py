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
        safe_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=safe_msg,
        )
    except Exception as e:
        safe_msg = str(e).encode("utf-8", errors="replace").decode("utf-8")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar historial clínico: {safe_msg}",
        )

