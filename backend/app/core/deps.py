from app.llm.openai.provider import OpenAIProvider

_openai_provider = None

def get_openai_provider() -> OpenAIProvider:
    global _openai_provider
    if _openai_provider is None:
        _openai_provider = OpenAIProvider()
    return _openai_provider