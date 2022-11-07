import asyncio

from api.ws_manager import WebsocketManager


async def increment_film_timestamp_coro(manager: WebsocketManager):
    cinema_room = manager.cinema_room
    while cinema_room.film_view_timestamp < cinema_room.film_duration:  # type: ignore
        # log.main_logger.info(f"Timestamp updating")
        cinema_room = manager.cinema_room
        if cinema_room.is_film_pause:
            return

        if cinema_room.is_film_stoped:
            manager.cinema_room = await manager.cinema_crud.update_film_timestamp(
                cinema_room=manager.cinema_room, film_timestamp=0
            )
            break

        cinema_room = await manager.cinema_crud.update_film_timestamp(
            cinema_room=cinema_room, film_timestamp=cinema_room.film_view_timestamp + 5
        )
        manager.cinema_room = cinema_room
        await asyncio.sleep(5)
    manager.cinema_room = await manager.cinema_crud.update_film_timestamp(
        cinema_room=manager.cinema_room, film_timestamp=0
    )
    manager.cinema_room = await manager.cinema_crud.stop_film(cinema_room=manager.cinema_room)
