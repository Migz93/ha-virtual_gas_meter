"""
Entity package for virtual_gas_meter.

Architecture:
    All platform entities inherit from (PlatformEntity, VirtualGasMeterEntity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the VirtualGasMeterEntity base class.
"""

from .base import VirtualGasMeterEntity

__all__ = ["VirtualGasMeterEntity"]
