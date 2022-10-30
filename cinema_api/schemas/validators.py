from uuid import UUID


def is_valid_uuid(checked_string: str):
    try:
        UUID(checked_string)
        return True
    except ValueError:
        return False
