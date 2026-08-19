from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.modules.variables.models import CategoriaVariable, OpcionVariable, Variable, VariableVersion
from app.modules.variables.schemas import CategoriaVariableCreate, VariableCreate, VariableUpdate, VariableVersionCreate


class VariablesService:
    # Categorías
    @staticmethod
    async def list_categorias(session: AsyncSession) -> List[CategoriaVariable]:
        stmt = select(CategoriaVariable).where(CategoriaVariable.activa.is_(True))
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_categoria(session: AsyncSession, cat_in: CategoriaVariableCreate) -> CategoriaVariable:
        stmt = select(CategoriaVariable).where(CategoriaVariable.codigo == cat_in.codigo)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe una categoría con código '{cat_in.codigo}'")

        cat = CategoriaVariable(**cat_in.model_dump())
        session.add(cat)
        await session.commit()
        await session.refresh(cat)
        return cat

    # Variables
    @staticmethod
    async def list_variables(session: AsyncSession, categoria_id: Optional[int] = None) -> List[Variable]:
        stmt = select(Variable).options(
            selectinload(Variable.categoria),
            selectinload(Variable.versiones).selectinload(VariableVersion.opciones)
        )
        if categoria_id:
            stmt = stmt.where(Variable.categoria_id == categoria_id)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_variable_by_id(session: AsyncSession, variable_id: int) -> Variable:
        stmt = (
            select(Variable)
            .where(Variable.id == variable_id)
            .options(
                selectinload(Variable.categoria),
                selectinload(Variable.versiones).selectinload(VariableVersion.opciones)
            )
        )
        res = await session.execute(stmt)
        var = res.scalar_one_or_none()
        if not var:
            raise NotFoundException("Variable", variable_id)
        return var

    @staticmethod
    async def create_variable(session: AsyncSession, var_in: VariableCreate) -> Variable:
        stmt = select(Variable).where(Variable.codigo == var_in.codigo)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            raise DuplicateResourceException(f"Ya existe una variable con código '{var_in.codigo}'")

        var = Variable(
            categoria_id=var_in.categoria_id,
            codigo=var_in.codigo,
            nombre=var_in.nombre,
            descripcion=var_in.descripcion,
            tipo_respuesta=var_in.tipo_respuesta,
            version_actual=1,
            es_sensible=var_in.es_sensible,
            es_obligatoria=var_in.es_obligatoria,
            activa=var_in.activa
        )
        session.add(var)
        await session.flush()

        version = VariableVersion(
            variable_id=var.id,
            numero_version=1,
            titulo_pregunta=var_in.titulo_pregunta,
            descripcion=var_in.descripcion,
            activa=True
        )
        session.add(version)
        await session.flush()

        for idx, op in enumerate(var_in.opciones):
            opcion = OpcionVariable(
                variable_version_id=version.id,
                codigo=op.codigo,
                texto=op.texto,
                valor_numerico=op.valor_numerico,
                orden=op.orden if op.orden else idx,
                nivel_afectacion=op.nivel_afectacion,
                activa=op.activa
            )
            session.add(opcion)

        await session.commit()
        return await VariablesService.get_variable_by_id(session, var.id)

    @staticmethod
    async def create_new_version(session: AsyncSession, variable_id: int, version_in: VariableVersionCreate) -> VariableVersion:
        var = await VariablesService.get_variable_by_id(session, variable_id)
        new_version_num = var.version_actual + 1
        var.version_actual = new_version_num

        version = VariableVersion(
            variable_id=var.id,
            numero_version=new_version_num,
            titulo_pregunta=version_in.titulo_pregunta,
            descripcion=version_in.descripcion,
            activa=True
        )
        session.add(version)
        await session.flush()

        for idx, op in enumerate(version_in.opciones):
            opcion = OpcionVariable(
                variable_version_id=version.id,
                codigo=op.codigo,
                texto=op.texto,
                valor_numerico=op.valor_numerico,
                orden=op.orden if op.orden else idx,
                nivel_afectacion=op.nivel_afectacion,
                activa=op.activa
            )
            session.add(opcion)

        await session.commit()
        return version
