from typing import Any, Dict, Optional
from pydantic import BaseModel

from multidict import CIMultiDictProxy


class HttpResponse(BaseModel):
    status: int
    body: Dict[str, Any]
    headers: CIMultiDictProxy[str]


class RedisDataSchema(BaseModel):
    key: str
    value: Optional[Any] = None
