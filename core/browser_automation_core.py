#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Browser Automation System - Core Module
Базовая архитектура системы автоматизации браузера
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("⚠️ Playwright не установлен. Запустите: pip install playwright")
    PLAYWRIGHT_AVAILABLE = False

@dataclass
class BrowserProfile:
    """Конфигурация профиля браузера"""
    id: str
    name: str
    user_agent: str
    viewport: Dict[str, int]
    locale: str
    timezone: str
    extensions: List[str] = field(default_factory=list)
    cookies: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфигурацию"""
        default_config = {
            "browser": {
                "headless": False,
                "timeout": 30000,
                "viewport": {"width": 1440, "height": 900}
            },
            "ai": {
                "provider": "openai",
                "api_key": "",
                "model": "gpt-4-vision-preview"
            },
            "profiles": {"count": 30},
            "logging": {"level": "INFO", "file": "logs/automation.log"}
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
        
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value

class CoordinateDatabase:
    """База данных координат"""
    
    def __init__(self, db_path: str = "data/coordinates.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coordinates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extension_name TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    screen_width INTEGER NOT NULL,
                    screen_height INTEGER NOT NULL,
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_coordinates(self, extension_name: str, action_type: str,
                        screen_resolution: Tuple[int, int],
                        coordinates: Tuple[int, int]) -> bool:
        """Сохранить координаты"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO coordinates 
                    (extension_name, action_type, screen_width, screen_height, x, y)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (extension_name, action_type, screen_resolution[0],
                      screen_resolution[1], coordinates[0], coordinates[1]))
            return True
        except Exception as e:
            print(f"Ошибка сохранения координат: {e}")
            return False
    
    def get_coordinates(self, extension_name: str, action_type: str,
                       screen_resolution: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Получить координаты"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT x, y FROM coordinates 
                    WHERE extension_name = ? AND action_type = ? 
                    AND screen_width = ? AND screen_height = ?
                    ORDER BY success_count DESC
                    LIMIT 1
                """, (extension_name, action_type, screen_resolution[0], screen_resolution[1]))
                
                result = cursor.fetchone()
                return (result[0], result[1]) if result else None
        except Exception as e:
            print(f"Ошибка получения координат: {e}")
            return None

class ProfileManager:
    """Менеджер профилей браузера"""
    
    def __init__(self, profiles_count: int = 30):
        self.profiles_count = profiles_count
        self.profiles: List[BrowserProfile] = []
        self.active_profiles: Dict[str, Any] = {}
        self._generate_profiles()
    
    def _generate_profiles(self):
        """Генерация уникальных профилей"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1440, "height": 900},
            {"width": 1366, "height": 768}
        ]
        
        locales = ["en-US", "en-GB", "de-DE", "fr-FR"]
        timezones = ["America/New_York", "Europe/London", "Europe/Berlin", "Europe/Paris"]
        
        for i in range(self.profiles_count):
            profile = BrowserProfile(
                id=f"profile_{i:02d}",
                name=f"Profile {i+1}",
                user_agent=random.choice(user_agents),
                viewport=random.choice(viewports),
                locale=random.choice(locales),
                timezone=random.choice(timezones),
                extensions=["rabby_wallet"]
            )
            self.profiles.append(profile)
    
    def get_profile(self, profile_id: str) -> Optional[BrowserProfile]:
        """Получить профиль по ID"""
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        return None
    
    def get_available_profile(self) -> Optional[BrowserProfile]:
        """Получить доступный профиль"""
        for profile in self.profiles:
            if profile.id not in self.active_profiles:
                return profile
        return None

class UniversalBrowserAutomator:
    """Основной класс автоматизации браузера"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = ConfigManager(config_path)
        self.coordinate_db = CoordinateDatabase()
        self.profile_manager = ProfileManager(30)
        self.playwright = None
        self.browsers: Dict[str, Any] = {}
    
    async def initialize(self):
        """Инициализация системы"""
        print("Инициализация Universal Browser Automator")
        
        if not PLAYWRIGHT_AVAILABLE:
            print("❌ Playwright недоступен")
            return False
        
        try:
            self.playwright = await async_playwright().start()
            print("✅ Playwright инициализирован")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def cleanup(self):
        """Очистка ресурсов"""
        print("Очистка ресурсов")
        
        for browser in self.browsers.values():
            try:
                await browser.close()
            except:
                pass
        
        if self.playwright:
            try:
                await self.playwright.stop()
            except:
                pass
        
        print("✅ Очистка завершена")
    
    async def create_browser_context(self, profile: BrowserProfile):
        """Создать контекст браузера"""
        try:
            if profile.id not in self.browsers:
                browser = await self.playwright.chromium.launch(
                    headless=self.config.get("browser.headless", False)
                )
                self.browsers[profile.id] = browser
            
            context = await self.browsers[profile.id].new_context(
                user_agent=profile.user_agent,
                viewport=profile.viewport,
                locale=profile.locale,
                timezone_id=profile.timezone
            )
            
            self.profile_manager.active_profiles[profile.id] = context
            print(f"✅ Создан контекст браузера для профиля {profile.id}")
            return context
            
        except Exception as e:
            print(f"❌ Ошибка создания контекста браузера: {e}")
            raise

# Тестирование
async def test_browser_core():
    """Тест основной функциональности"""
    print("🧪 Тестирование browser_automation_core...")
    
    automator = UniversalBrowserAutomator()
    
    if not await automator.initialize():
        print("❌ Не удалось инициализировать систему")
        return False
    
    try:
        profile = automator.profile_manager.get_available_profile()
        if profile:
            print(f"✅ Профиль получен: {profile.id}")
            
            if PLAYWRIGHT_AVAILABLE:
                context = await automator.create_browser_context(profile)
                page = await context.new_page()
                
                await page.goto("https://example.com")
                print("✅ Страница загружена")
                
                await context.close()
            
        print("✅ Тест browser_automation_core пройден!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        return False
    
    finally:
        await automator.cleanup()

if __name__ == "__main__":
    asyncio.run(test_browser_core())
