from typing import Dict
from fastapi import Depends, HTTPException, status

from core.auth import get_current_institution, normalize_institution
from domain.ports import IRepository
from adapters.hospital_postgres import HospitalPostgresAdapter
from adapters.laboratorio_mongo import LaboratorioMongoAdapter

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
            # Asignado a Ronaldo (PostgreSQL)
            _adapters[normalized] = HospitalPostgresAdapter()
        elif normalized == "laboratorio":
            # Asignado a Ronaldo (MongoDB)
            _adapters[normalized] = LaboratorioMongoAdapter()
        elif normalized == "pediatria":
            # Asignado a Brayan (MySQL)
            try:
                from adapters.pediatria_mysql import PediatriaMysqlAdapter
                _adapters[normalized] = PediatriaMysqlAdapter()
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Adaptador de Pediatría (MySQL) pendiente de ser implementado por Brayan.",
                )
        elif normalized == "odontologia":
            # Asignado a Brayan (Firebase Firestore)
            try:
                from adapters.odontologia_firebase import OdontologiaFirebaseAdapter
                _adapters[normalized] = OdontologiaFirebaseAdapter()
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Adaptador de Odontología (Firebase) pendiente de ser implementado por Brayan.",
                )
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
