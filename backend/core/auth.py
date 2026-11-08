import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

# Cargar variables de entorno
# Sin clave configurada se genera una efímera; nunca firmar con un secreto publicado.
JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_urlsafe(48)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

# Esquema Bearer
security = HTTPBearer(auto_error=False)

# Cuentas locales de demostración. Para despliegue real, sustituir por un almacén de usuarios.
_DEMO_HASH = "pbkdf2_sha256$310000$636c696e6963612d64656d6f2d32303236$5a9feb5af7656419730ccf9d6251c066b05edd47a57eef422753bfdf17c4ff89"
USUARIOS_DB: Dict[str, Dict[str, Any]] = {
    "medico@hospital.gt": {
        "usuario": "medico@hospital.gt",
        "password_hash": _DEMO_HASH,
        "institution": "hospital",
        "rol": "medico",
        "user_id": 1,
        "nombre": "Dr. Fernando García"
    },
    "tecnico@laboratorio.gt": {
        "usuario": "tecnico@laboratorio.gt",
        "password_hash": _DEMO_HASH,
        "institution": "laboratorio",
        "rol": "tecnico",
        "user_id": 2,
        "nombre": "Lic. Carlos Méndez"
    },
    "medico@laboratorio.gt": {
        "usuario": "medico@laboratorio.gt",
        "password_hash": _DEMO_HASH,
        "institution": "laboratorio",
        "rol": "medico_laboratorio",
        "user_id": 5,
        "nombre": "Profesional de laboratorio"
    },
    "medico@pediatria.gt": {
        "usuario": "medico@pediatria.gt",
        "password_hash": _DEMO_HASH,
        "institution": "pediatria",
        "rol": "pediatra",
        "user_id": 3,
        "nombre": "Dra. Sofía Morales"
    },
    "secretaria@dental.gt": {
        "usuario": "secretaria@dental.gt",
        "password_hash": _DEMO_HASH,
        "institution": "odontologia",
        "rol": "secretaria",
        "user_id": 4,
        "nombre": "Secretaria Dental"
    },
    "odontologo@dental.gt": {
        "usuario": "odontologo@dental.gt",
        "password_hash": _DEMO_HASH,
        "institution": "odontologia",
        "rol": "odontologo",
        "user_id": 6,
        "nombre": "Odontólogo clínico"
    },
}

CLINICAL_ROLES = {"medico", "pediatra", "medico_laboratorio", "odontologo"}
PERMISSIONS = {
    "patient_write": CLINICAL_ROLES | {"tecnico", "secretaria"},
    "patient_read": CLINICAL_ROLES | {"tecnico", "secretaria"},
    "archive": CLINICAL_ROLES,
    "consultation": CLINICAL_ROLES | {"tecnico"},
    "clinical_write": CLINICAL_ROLES,
    "appointment": CLINICAL_ROLES | {"secretaria"},
    "lab_result": {"tecnico", "medico_laboratorio"},
    "dental_procedure": {"odontologo"},
    "pediatric_write": {"pediatra"},
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
    algorithm, rounds, salt_hex, expected_hex = stored_password.split("$")
    if algorithm != "pbkdf2_sha256":
        return False
    actual = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"),
                                bytes.fromhex(salt_hex), int(rounds))
    return hmac.compare_digest(actual, bytes.fromhex(expected_hex))


def authenticate_user(usuario: str, password: str) -> Optional[Dict[str, Any]]:
    u = USUARIOS_DB.get(usuario.strip().lower())
    if not u:
        return None
    if not verify_password(password, u["password_hash"]):
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


def require_permission(action: str):
    allowed = PERMISSIONS[action]

    def dependency(claims: Dict[str, Any] = Depends(get_current_user_claims)) -> Dict[str, Any]:
        if claims.get("rol") not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta no tiene permiso para esta operación",
            )
        return claims

    return dependency

