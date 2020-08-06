from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PageView(BaseModel):
    domain: str
    url: str
    timestamp: datetime
    metadata: Optional[dict]

    class Config:
        orm_mode = True
