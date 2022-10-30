from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from schemas.base import BaseSchema

SchemaType = TypeVar("SchemaType", bound=BaseSchema)


class AbstractService(ABC, Generic[SchemaType]):
    async def get_cinema_room(self, cinema_key: str) -> SchemaType:
        return await self._get(cinema_key=cinema_key)

    async def create_cinema_room(
        self, cinema_key: str, admin_id: str, cinema_room_data: SchemaType
    ) -> SchemaType:
        return await self._create(
            cinema_key=cinema_key, admin_id=admin_id, cinema_room_data=cinema_room_data
        )

    async def update_cinema_room(
        self, cinema_room: SchemaType, update_room_data: SchemaType
    ) -> SchemaType:
        return await self._update(
            cinema_room=cinema_room, update_room_data=update_room_data
        )

    async def delete_cinema_room(self, cinema_key: str) -> bool:
        return await self._delete(cinema_key=cinema_key)

    @abstractmethod
    async def _get(self, cinema_key: str) -> SchemaType:
        raise NotImplementedError

    @abstractmethod
    async def _create(
        self, cinema_key: str, admin_id: str, cinema_room_data: SchemaType
    ) -> SchemaType:
        raise NotImplementedError

    @abstractmethod
    async def _update(
        self, cinema_room: SchemaType, update_room_data: SchemaType
    ) -> SchemaType:
        raise NotImplementedError

    @abstractmethod
    async def _delete(self, cinema_key: str) -> bool:
        raise NotImplementedError
