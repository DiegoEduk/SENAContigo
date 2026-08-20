from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.benefits.models import AprendizBeneficio, Beneficio
from app.modules.benefits.schemas import AprendizBeneficioCreate, BeneficioCreate, BeneficioUpdate


async def get_beneficios(db: AsyncSession, only_active: bool = True) -> List[Beneficio]:
    query = select(Beneficio)
    if only_active:
        query = query.where(Beneficio.activo == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_beneficio_by_id(db: AsyncSession, beneficio_id: int) -> Optional[Beneficio]:
    result = await db.execute(select(Beneficio).where(Beneficio.id == beneficio_id))
    return result.scalar_one_or_none()


async def get_beneficio_by_codigo(db: AsyncSession, codigo: str) -> Optional[Beneficio]:
    result = await db.execute(select(Beneficio).where(Beneficio.codigo == codigo))
    return result.scalar_one_or_none()


async def create_beneficio(db: AsyncSession, data: BeneficioCreate) -> Beneficio:
    beneficio = Beneficio(**data.model_dump())
    db.add(beneficio)
    await db.commit()
    await db.refresh(beneficio)
    return beneficio


async def update_beneficio(db: AsyncSession, beneficio_id: int, data: BeneficioUpdate) -> Optional[Beneficio]:
    beneficio = await get_beneficio_by_id(db, beneficio_id)
    if not beneficio:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(beneficio, field, value)
    await db.commit()
    await db.refresh(beneficio)
    return beneficio


async def assign_beneficio_to_aprendiz(db: AsyncSession, data: AprendizBeneficioCreate) -> AprendizBeneficio:
    # Check if benefit is already assigned
    existing = await db.execute(
        select(AprendizBeneficio).where(
            AprendizBeneficio.aprendiz_id == data.aprendiz_id,
            AprendizBeneficio.beneficio_id == data.beneficio_id,
            AprendizBeneficio.estado == "ACTIVO"
        )
    )
    obj = existing.scalar_one_or_none()
    if obj:
        return obj  # Already assigned and active

    aprendiz_beneficio = AprendizBeneficio(
        aprendiz_id=data.aprendiz_id,
        beneficio_id=data.beneficio_id,
        origen=data.origen,
        caso_id=data.caso_id,
        observaciones=data.observaciones,
        estado="ACTIVO"
    )
    db.add(aprendiz_beneficio)
    await db.commit()
    
    # Reload with relationship
    result = await db.execute(
        select(AprendizBeneficio)
        .options(selectinload(AprendizBeneficio.beneficio))
        .where(AprendizBeneficio.id == aprendiz_beneficio.id)
    )
    return result.scalar_one()


async def assign_automatic_benefits_for_aprendiz(db: AsyncSession, aprendiz_id: int) -> List[AprendizBeneficio]:
    """Asigna automáticamente todos los beneficios institucionales de matrícula por defecto a un aprendiz."""
    # Find all active automatic benefits
    automatic_benefits = await db.execute(
        select(Beneficio).where(
            Beneficio.activo == True,
            Beneficio.es_automatico_matricula == True
        )
    )
    benefits_list = automatic_benefits.scalars().all()
    assigned = []
    for ben in benefits_list:
        ab = await assign_beneficio_to_aprendiz(
            db,
            AprendizBeneficioCreate(
                aprendiz_id=aprendiz_id,
                beneficio_id=ben.id,
                origen="MATRICULA_AUTOMATICA",
                observaciones="Asignado automáticamente por estado de matrícula activa en el SENA."
            )
        )
        assigned.append(ab)
    return assigned


async def get_aprendiz_beneficios(db: AsyncSession, aprendiz_id: int) -> List[AprendizBeneficio]:
    result = await db.execute(
        select(AprendizBeneficio)
        .options(selectinload(AprendizBeneficio.beneficio))
        .where(AprendizBeneficio.aprendiz_id == aprendiz_id)
        .order_by(AprendizBeneficio.created_at.desc())
    )
    return list(result.scalars().all())


async def update_aprendiz_beneficio_state(
    db: AsyncSession,
    aprendiz_beneficio_id: int,
    estado: str,
    observaciones: Optional[str] = None
) -> Optional[AprendizBeneficio]:
    result = await db.execute(
        select(AprendizBeneficio)
        .options(selectinload(AprendizBeneficio.beneficio))
        .where(AprendizBeneficio.id == aprendiz_beneficio_id)
    )
    ab = result.scalar_one_or_none()
    if not ab:
        return None
    ab.estado = estado
    if observaciones:
        ab.observaciones = observaciones
    await db.commit()
    await db.refresh(ab)
    return ab
