"""Schemas for Virtual Gas Meter config and options flows."""

from .config import get_user_schema
from .options import get_options_schema

__all__ = ["get_options_schema", "get_user_schema"]
