from functools import lru_cache
from typing import Dict
from fastapi import Depends, HTTPException, status

from core.auth import get_current_institution, normalize_institution
from domain.ports import IRepository
from adapters.hospital_postgres import HospitalPostgresAdapter
from adapters.laboratorio_mongo import LaboratorioMongoAdapter
from adapters.pediatria_mysql import PediatriaMysqlAdapter
from adapters.odontologia_firebase import OdontologiaFirebaseAdapter


# Registro central de adaptadores instanciados
_adapters: Dict[str, IRepository] = {}


def get_adapter_for_institution(institution_name: str) -> IRepository:
    """
    Factoría de Adaptadores: Retorna la implementación concreta de IRepository
    según la institución asignada en el token del usuario.
    Arquitectura Hexagonal: Desacopla por completo la capa web/negocio del motor subyacente.
    """
    normalized = normalize_institution(institution_name)

    if normalized not in _adapters:
        if normalized == "hospital":
            _adapters[normalized] = HospitalPostgresAdapter()
        elif normalized == "laboratorio":
            _adapters[normalized] = LaboratorioMongoAdapter()
        elif normalized == "pediatria":
            _adapters[normalized] = PediatriaMysqlAdapter()
        elif normalized == "odontologia":
            _adapters[normalized] = OdontologiaFirebaseAdapter()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Institución no soportada: '{institution_name}'",
            )

    return _adapters[normalized]


def get_repository(institution: str = Depends(get_current_institution)) -> IRepository:
    """
    Inyección de dependencias para endpoints de FastAPI.
    Resuelve el adaptador correspondiente de manera transparente.
    """
    return get_adapter_for_institution(institution)
