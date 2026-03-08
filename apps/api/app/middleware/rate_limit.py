"""
Rate limiting configuration using slowapi.
Default: 100 requests/minute per IP.
Legal doc routes: 10 requests/minute (AI generation is expensive).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
