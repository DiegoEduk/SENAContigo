from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import LoginRequest, TokenResponse, UsuarioResponse
from app.core.security import verify_password, create_access_token, get_current_user_data, TokenData

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo_electronico == request.correo).first()
    if not usuario or not verify_password(request.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo en el sistema"
        )

    access_token = create_access_token(data={
        "sub": usuario.correo_electronico,
        "user_id": usuario.id,
        "rol": usuario.rol,
        "regional_id": usuario.regional_id,
        "centro_id": usuario.centro_id
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=UsuarioResponse.model_validate(usuario)
    )


@router.get("/me", response_model=UsuarioResponse)
def get_me(user_data: TokenData = Depends(get_current_user_data), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == user_data.user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioResponse.model_validate(usuario)
