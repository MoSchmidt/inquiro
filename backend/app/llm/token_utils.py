import tiktoken

ENCODING = tiktoken.get_encoding("o200k_base")


def count_tokens(text: str) -> int:
    """
    Return the number of tokens in the given text using the o200k_base encoding.
    This closely matches the tokenizer used by GPT-4.1/GPT-5 models.
    """
    if not text:
        return 0
    return len(ENCODING.encode(text))
