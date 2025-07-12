# -*- coding: utf-8 -*-
"""
Universal Browser Automation System - Core Package
Основной пакет системы автоматизации браузера
"""

try:
    from .browser_automation_core import (
        UniversalBrowserAutomator,
        ConfigManager,
        CoordinateDatabase,
        ProfileManager,
        BrowserProfile
    )
    BROWSER_CORE_AVAILABLE = True
except ImportError:
    BROWSER_CORE_AVAILABLE = False

try:
    from .extension_handler import (
        ExtensionActionHandler,
        ExtensionDetector,
        WalletType,
        ActionType,
        WalletExtension
    )
    EXTENSION_HANDLER_AVAILABLE = True
except ImportError:
    EXTENSION_HANDLER_AVAILABLE = False

try:
    from .simple_main import (
        SimpleAutomationSystem,
        SimpleCLI
    )
    SIMPLE_MAIN_AVAILABLE = True
except ImportError:
    SIMPLE_MAIN_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "Universal Browser Automation Team"

# Экспорт только доступных модулей
__all__ = []

if BROWSER_CORE_AVAILABLE:
    __all__.extend([
        "UniversalBrowserAutomator",
        "ConfigManager", 
        "CoordinateDatabase",
        "ProfileManager",
        "BrowserProfile"
    ])

if EXTENSION_HANDLER_AVAILABLE:
    __all__.extend([
        "ExtensionActionHandler",
        "ExtensionDetector",
        "WalletType",
        "ActionType", 
        "WalletExtension"
    ])

if SIMPLE_MAIN_AVAILABLE:
    __all__.extend([
        "SimpleAutomationSystem",
        "SimpleCLI"
    ])
