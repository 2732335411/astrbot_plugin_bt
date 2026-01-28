"""AstrBot BT Panel plugin package."""

from .client import BtPanelClient, BtPanelConfig, BtPanelError
from .plugin import Plugin, register

__all__ = [
    "BtPanelClient",
    "BtPanelConfig",
    "BtPanelError",
    "Plugin",
    "register",
]

__version__ = "0.1.0"
