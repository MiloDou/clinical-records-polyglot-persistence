import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

# Cargar variables de entorno
JWT_SECRET = os.getenv("JWT_SECRET", "clave_secreta_super_segura_bases_datos_ii_url_2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

# Esquema Bearer
security = HTTPBearer(auto_error=False)

# Mapeo de usuarios para cada institución según Plan Maestro
USUARIOS_DB: Dict[str, Dict[str, Any]] = {
    "medico@hospital.gt": {
        "usuario": "medico@hospital.gt",
        "password": "Test1234!",
        "institution": "hospital",
        "rol": "medico",
        "user_id": 1,
        "nombre": "Dr. Fernando García"
    },
    "tecnico@laboratorio.gt": {
        "usuario": "tecnico@laboratorio.gt",
        "password": "Test1234!",
        "institution": "laboratorio",
        "rol": "tecnico",
        "user_id": 2,
        "nombre": "Lic. Carlos Méndez"
    },
    "medico@pediatria.gt": {
        "usuario": "medico@pediatria.gt",
        "password": "Test1234!",
        "institution": "pediatria",
        "rol": "pediatra",
        "user_id": 3,
        "nombre": "Dra. Sofía Morales"
    },
    "secretaria@dental.gt": {
        "usuario": "secretaria@dental.gt",
        "password": "Test1234!",
        "institution": "odontologia",
        "rol": "secretaria",
        "user_id": 4,
        "nombre": "Secretaria Dental"
    },
}

# Normalización de instituciones (acepta nombres en inglés y español)
INSTITUTION_MAP = {
    "hospital": "hospital",
    "laboratorio": "laboratorio",
    "laboratory": "laboratorio",
    "pediatria": "pediatria",
    "pediatrics": "pediatria",
    "odontologia": "odontologia",
    "dental": "odontologia",
}


def normalize_institution(inst: str) -> str:
    cleaned = (inst or "").strip().lower()
    return INSTITUTION_MAP.get(cleaned, cleaned)


def verify_password(plain_password: str, stored_password: str) -> bool:
    # Comparación en tiempo constante para evitar ataques de temporización
    return hmac.compare_digest(plain_password.encode("utf-8"), stored_password.encode("utf-8"))


def authenticate_user(usuario: str, password: str) -> Optional[Dict[str, Any]]:
    u = USUARIOS_DB.get(usuario.strip().lower())
    if not u:
        return None
    if not verify_password(password, u["password"]):
        return None
    return u


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_claims(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Encabezado de autorización ausente o inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_access_token(credentials.credentials)


def get_current_institution(claims: Dict[str, Any] = Depends(get_current_user_claims)) -> str:
    inst = claims.get("institution") or claims.get("institucion")
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token no contiene la institución asignada"
        )
    return normalize_institution(inst)

