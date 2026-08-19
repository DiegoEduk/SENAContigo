from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Categoria, Variable, VariableVersion, OpcionVariable
from app.schemas.schemas import (
    CategoriaResponse, VariableCreate, VariableResponse, OpcionVariableCreate
)
from app.core.security import get_current_user_data, TokenData, RoleChecker

router = APIRouter(prefix="/variables", tags=["Motor de Variables Dinámicas"])


@router.get("/categorias", response_model=List[CategoriaResponse])
def get_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).order_by(Categoria.orden.asc()).all()


@router.post("/categorias", response_model=CategoriaResponse)
def create_categoria(
    nombre: str,
    descripcion: str = None,
    icono: str = "folder",
    orden: int = 0,
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(RoleChecker(["superadmin", "direccion", "coordinador"]))
):
    cat = Categoria(nombre=nombre, descripcion=descripcion, icono=icono, orden=orden)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/", response_model=List[VariableResponse])
def list_variables(db: Session = Depends(get_db)):
    return db.query(Variable).filter(Variable.activa == True).all()


@router.post("/", response_model=VariableResponse)
def create_variable(
    payload: VariableCreate,
    db: Session = Depends(get_db),
    user_data: TokenData = Depends(RoleChecker(["superadmin", "direccion", "coordinador"]))
):
    # Check code unique
    existing = db.query(Variable).filter(Variable.codigo == payload.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe una variable con el código '{payload.codigo}'")

    var = Variable(
        categoria_id=payload.categoria_id,
        nombre=payload.nombre,
        codigo=payload.codigo,
        descripcion=payload.descripcion,
        tipo_respuesta=payload.tipo_respuesta,
        obligatoria=payload.obligatoria,
        activa=payload.activa
    )
    db.add(var)
    db.commit()
    db.refresh(var)

    # Initial Version 1
    ver = VariableVersion(variable_id=var.id, version=1, descripcion_cambio="Versión inicial")
    db.add(ver)
    db.commit()
    db.refresh(ver)

    # Add Options with affectation levels (0..4)
    for op in payload.opciones:
        op_db = OpcionVariable(
            variable_id=var.id,
            version_id=ver.id,
            codigo=op.codigo,
            texto=op.texto,
            valor_numerico=op.valor_numerico,
            orden=op.orden,
            nivel_afectacion=op.nivel_afectacion,
            activa=op.activa
        )
        db.add(op_db)

    db.commit()
    db.refresh(var)
    return var
