import tiktoken
from fastapi import HTTPException

ENCODING = tiktoken.get_encoding("o200k_base")


def ensure_fits_token_limit(
    text: str,
    max_tokens: int,
    *,
    error_status: int = 413,
    error_detail: str | None = None,
) -> None:
    """
    Checks if the given text fits the o200k_base encoding limit.
    """
    if not text:
        token_count = 0
    else:
        token_count = len(ENCODING.encode(text))

    if token_count > max_tokens:
        raise HTTPException(
            status_code=error_status,
            detail=error_detail or f"Input too long ({token_count} tokens, limit {max_tokens}).",
        )
