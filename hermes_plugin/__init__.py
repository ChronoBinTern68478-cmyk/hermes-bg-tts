# hermes_plugin/__init__.py
# Този файл превръща папката в Python пакет.

from .bg_tts_provider import BG_TTS_Provider, get_provider

__version__ = "1.0.0"
__all__ = ["BG_TTS_Provider", "get_provider"]