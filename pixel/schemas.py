from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PageView(BaseModel):
    domain: str
    url: str
    time_spent: float
    timestamp: datetime
    metadata: Optional[dict]

    class Config:
        orm_mode = True
