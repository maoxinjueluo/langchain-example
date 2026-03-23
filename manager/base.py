"""Generic async CRUD for SQLAlchemy models inheriting BaseModel."""

from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.const import DEFAULT_PAGE_SKIP, DEFAULT_PAGE_LIMIT
from models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseManager(Generic[T]):
    """Async CRUD and batch operations for a single model class."""

    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self.session = session
        self.model = model

    async def create(self, **kwargs: Any) -> T:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, pk: int) -> Optional[T]:
        result = await self.session.execute(select(self.model).where(self.model.id == pk))
        return result.scalar_one_or_none()

    async def update_by_id(self, pk: int, **kwargs: Any) -> Optional[T]:
        if not kwargs:
            return await self.get_by_id(pk)
        await self.session.execute(
            update(self.model).where(self.model.id == pk).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(pk)

    async def delete_by_id(self, pk: int) -> bool:
        obj = await self.get_by_id(pk)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def list_page(
        self,
        *,
        skip: int = DEFAULT_PAGE_SKIP,
        limit: int = DEFAULT_PAGE_LIMIT,
        status: Optional[int] = None,
    ) -> List[T]:
        stmt = select(self.model)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        stmt = stmt.order_by(self.model.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, *, status: Optional[int] = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def batch_create(self, items: List[Dict[str, Any]]) -> List[T]:
        objs = [self.model(**data) for data in items]
        self.session.add_all(objs)
        await self.session.flush()
        for obj in objs:
            await self.session.refresh(obj)
        return objs

    async def batch_get_by_ids(self, ids: List[int]) -> List[T]:
        if not ids:
            return []
        result = await self.session.execute(select(self.model).where(self.model.id.in_(ids)))
        return list(result.scalars().all())

    async def batch_delete_by_ids(self, ids: List[int]) -> int:
        if not ids:
            return 0
        result = await self.session.execute(delete(self.model).where(self.model.id.in_(ids)))
        await self.session.flush()
        return result.rowcount or 0

    async def batch_update_by_ids(self, updates: List[Tuple[int, Dict[str, Any]]]) -> int:
        """Apply each dict to the row with matching id. Empty dicts are skipped."""
        count = 0
        for pk, data in updates:
            if not data:
                continue
            await self.session.execute(
                update(self.model).where(self.model.id == pk).values(**data)
            )
            count += 1
        await self.session.flush()
        return count
