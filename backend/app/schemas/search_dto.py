from pydantic import BaseModel


class SearchRequest(BaseModel):
    search_text: str
