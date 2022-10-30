from uuid import uuid4


async def get_current_user_id():
    return str(uuid4())
