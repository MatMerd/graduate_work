from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from crud.auth_crud import get_current_user_http
from crud.cinema_crud import CinemaCRUD, get_cinema_crud
from schemas.cinema_room import CinemaRoom, CinemaRoomCreate, CinemaRoomResponse, User


router = APIRouter()


@router.get(
    "/{cinema_room_id}",
    response_model=CinemaRoomResponse,
    summary="Get cinema room by id",
    description="Route return all data about room including admin, film, users in room and film_timestamp",
)
async def cinema_room_details(
    cinema_room_id: str,
    cinema_crud: CinemaCRUD = Depends(get_cinema_crud),
    identify: User = Depends(get_current_user_http),
) -> CinemaRoom:
    cinema_room = await cinema_crud.get_cinema_room(cinema_room_key=cinema_room_id)
    return cinema_room


@router.post(
    "/create",
    response_model=CinemaRoomResponse,
    summary="Create cinema room",
    description="Route for create cinema room with admin_id, film_id, user_ids and film_timestamp",
)
async def create_cinema_room(
    *,
    cinema_crud: CinemaCRUD = Depends(get_cinema_crud),
    cinema_room_create: CinemaRoomCreate,
    current_user: User = Depends(get_current_user_http),
) -> CinemaRoom:
    cinema_room = await cinema_crud.create_cinema_room(
        admin_id=current_user.user_id, cinema_room_create=cinema_room_create
    )
    return cinema_room


@router.delete(
    "/{cinema_room_id}",
    summary="Delete cinema room",
    description="Route for delete cinema room and assotiated data",
)
async def delete_cinema_room(
    *,
    cinema_room_id: str,
    cinema_crud: CinemaCRUD = Depends(get_cinema_crud),
    identify: User = Depends(get_current_user_http),
) -> ORJSONResponse:
    await cinema_crud.delete_cinema_room(
        cinema_room_key=cinema_room_id, admin_id=identify.user_id
    )
    return ORJSONResponse(content={"message": f"Room {cinema_room_id} was deleted"})
