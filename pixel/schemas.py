from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# =============== This schemas are for testing purposes ========
class PageView(BaseModel):
    domain: str
    url: str
    timestamp: datetime
    title: str
    ip: Optional[str]
    referrer: str
    headers: dict
    params: dict

    class Config:
        orm_mode = True


class TestSchema(BaseModel):
    email: str
    pageviews: List[PageView]

    class Config:
        orm_mode = True
# =======================
