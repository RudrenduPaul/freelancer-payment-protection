"""
Rate limiting — single canonical limiter instance used across all routers.
Default: 100 req/min per IP. Legal doc routes use stricter 10/min limit.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Single instance — imported by main.py and all routers
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
