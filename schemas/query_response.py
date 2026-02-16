from typing import Optional

from pydantic import BaseModel


class QueryResponse(BaseModel):
    answer: str
    session_id: str
    ources: Optional[list] = None
