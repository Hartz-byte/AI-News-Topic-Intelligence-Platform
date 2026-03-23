from datetime import datetime
from pydantic import BaseModel

class ArticleOut(BaseModel):
    id: int
    title: str
    url: str
    source_name: str
    published_at: datetime | None = None
    category: str
    summary: str

    model_config = {"from_attributes": True}
