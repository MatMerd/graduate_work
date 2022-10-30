def construct_cinema_room_chanel_name(cinema_room_id: str) -> str:
    return f"cinema-room::chanel-{cinema_room_id}"


def construct_cinema_room_chanel_messages_by_chanel_name(
    cinema_room_chanel_name: str,
) -> str:
    return f"{cinema_room_chanel_name}::messages"


def construct_cinema_room_chanel_messages_by_room_id(cinema_room_id: str) -> str:
    return f"{construct_cinema_room_chanel_name(cinema_room_id)}::messages"
