from fastapi import APIRouter, HTTPException, status
from core.auth import authenticate_user, create_access_token
from core.models import LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn):
    user = authenticate_user(datos.usuario, datos.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = {
        "sub": user["usuario"],
        "usuario": user["usuario"],
        "institution": user["institution"],
        "rol": user["rol"],
        "user_id": user["user_id"],
    }
    access_token = create_access_token(claims)

    return TokenOut(
        access_token=access_token,
        token_type="bearer",
        institution=user["institution"],
        usuario=user["usuario"],
        rol=user["rol"],
    )
