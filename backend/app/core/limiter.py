from slowapi import Limiter
from slowapi.util import get_remote_address

# Define the limiter in a separate file to avoid circular import error
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
