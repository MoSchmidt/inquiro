from fastapi import APIRouter, status, Depends

from app.core.deps import get_openai_provider
from app.llm.openai.provider import OpenAIProvider
from app.schemas.search_dto import SearchRequest

router = APIRouter(prefix="/search", tags=["Search"])

# TODO remove - testing purposes only
@router.post("/", response_model=str, status_code=status.HTTP_200_OK, summary="Authenticate a user and return JWT tokens")
def search(search_request: SearchRequest, provider: OpenAIProvider = Depends(get_openai_provider)) -> str:
    return provider.extract_keywords(search_request.search_text)

