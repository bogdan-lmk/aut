#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extension Handler - Обработчик расширений кошельков
Универсальная работа с Rabby, Phantom и другими кошельками
"""

import asyncio
import base64
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

try:
    from playwright.async_api import Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("⚠️ Playwright не установлен")
    PLAYWRIGHT_AVAILABLE = False

class WalletType(str, Enum):
    RABBY = "rabby"
    PHANTOM = "phantom"
    METAMASK = "metamask"

class ActionType(str, Enum):
    CONNECT = "connect"
    CONFIRM = "confirm"
    APPROVE = "approve"
    REJECT = "reject"
    SIGN = "sign"

@dataclass
class WalletExtension:
    """Конфигурация расширения кошелька"""
    name: str
    wallet_type: WalletType
    extension_id: Optional[str] = None
    default_coordinates: Dict[str, Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.default_coordinates is None:
            self.default_coordinates = {}

# Конфигурации кошельков
WALLET_CONFIGS = {
    WalletType.RABBY: WalletExtension(
        name="Rabby Wallet",
        wallet_type=WalletType.RABBY,
        extension_id="acmacodkjbdgmoleebolmdjonilkdbch",
        default_coordinates={
            "connect": (720, 450),
            "confirm": (720, 500),
            "approve": (720, 480),
            "reject": (600, 500),
            "sign": (720, 470)
        }
    ),
    
    WalletType.PHANTOM: WalletExtension(
        name="Phantom Wallet",
        wallet_type=WalletType.PHANTOM,
        extension_id="bfnaelmomeimhlpmgjnjophhpkkoljpa",
        default_coordinates={
            "connect": (720, 450),
            "approve": (720, 500),
            "sign": (720, 470),
            "reject": (600, 500)
        }
    )
}

class ExtensionDetector:
    """Детектор расширений"""
    
    def __init__(self):
        self.detection_cache = {}
    
    async def detect_extension_popup(self, page: Page) -> Optional[WalletExtension]:
        """Обнаружить попап расширения"""
        if not PLAYWRIGHT_AVAILABLE:
            return None
            
        try:
            # Поиск страниц расширений
            extension_page = await self._find_extension_page(page)
            if extension_page:
                return await self._identify_wallet_from_page(extension_page)
            
            return None
            
        except Exception as e:
            print(f"Ошибка обнаружения расширения: {e}")
            return None
    
    async def _find_extension_page(self, page: Page) -> Optional[Page]:
        """Найти страницу расширения"""
        try:
            all_pages = page.context.pages
            
            for p in all_pages:
                url = p.url
                if "chrome-extension://" in url:
                    for wallet_config in WALLET_CONFIGS.values():
                        if wallet_config.extension_id and wallet_config.extension_id in url:
                            return p
            
            return None
        except Exception as e:
            print(f"Ошибка поиска страницы расширения: {e}")
            return None
    
    async def _identify_wallet_from_page(self, extension_page: Page) -> Optional[WalletExtension]:
        """Идентифицировать кошелек по странице"""
        try:
            url = extension_page.url
            
            for wallet_type, wallet_config in WALLET_CONFIGS.items():
                if wallet_config.extension_id and wallet_config.extension_id in url:
                    return wallet_config
            
            return None
        except Exception as e:
            print(f"Ошибка идентификации кошелька: {e}")
            return None

class ExtensionActionHandler:
    """Обработчик действий с расширениями"""
    
    def __init__(self, coordinate_db, ai_client=None):
        self.coordinate_db = coordinate_db
        self.ai_client = ai_client
        self.detector = ExtensionDetector()
    
    async def perform_wallet_action(self, page: Page, action_type: str,
                                  wallet_type: Optional[WalletType] = None) -> bool:
        """Выполнить действие с кошельком"""
        print(f"Выполнение действия кошелька: {action_type}")
        
        if not PLAYWRIGHT_AVAILABLE:
            print("❌ Playwright недоступен")
            return False
        
        try:
            # Обнаружить кошелек
            detected_wallet = await self.detector.detect_extension_popup(page)
            
            if not detected_wallet:
                print("⚠️ Расширение кошелька не обнаружено")
                # Попробуем координаты по умолчанию для указанного кошелька
                if wallet_type and wallet_type in WALLET_CONFIGS:
                    detected_wallet = WALLET_CONFIGS[wallet_type]
                else:
                    return False
            
            print(f"✅ Обнаружен кошелек: {detected_wallet.name}")
            
            # Получить разрешение экрана
            viewport = page.viewport_size
            screen_resolution = (viewport["width"], viewport["height"])
            
            # Попробовать разные стратегии
            success = await self._try_action_strategies(
                page, detected_wallet, action_type, screen_resolution
            )
            
            return success
            
        except Exception as e:
            print(f"❌ Ошибка выполнения действия кошелька: {e}")
            return False
    
    async def _try_action_strategies(self, page: Page, wallet_config: WalletExtension,
                                   action_type: str, screen_resolution: Tuple[int, int]) -> bool:
        """Попробовать разные стратегии действий"""
        
        strategies = [
            self._try_saved_coordinates,
            self._try_default_coordinates,
            self._try_dom_selector
        ]
        
        for strategy in strategies:
            try:
                print(f"Попытка стратегии: {strategy.__name__}")
                success = await strategy(page, wallet_config, action_type, screen_resolution)
                
                if success:
                    await asyncio.sleep(1)  # Человекоподобная задержка
                    return True
                    
            except Exception as e:
                print(f"Стратегия {strategy.__name__} не удалась: {e}")
                continue
        
        return False
    
    async def _try_saved_coordinates(self, page: Page, wallet_config: WalletExtension,
                                   action_type: str, screen_resolution: Tuple[int, int]) -> bool:
        """Попытка с сохраненными координатами"""
        coords = self.coordinate_db.get_coordinates(
            wallet_config.wallet_type, action_type, screen_resolution
        )
        
        if coords:
            await page.mouse.click(coords[0], coords[1])
            print(f"✅ Клик по сохраненным координатам: {coords}")
            return True
        
        return False
    
    async def _try_default_coordinates(self, page: Page, wallet_config: WalletExtension,
                                     action_type: str, screen_resolution: Tuple[int, int]) -> bool:
        """Попытка с координатами по умолчанию"""
        default_coords = wallet_config.default_coordinates.get(action_type)
        
        if default_coords:
            # Масштабирование координат
            scaled_coords = self._scale_coordinates(default_coords, screen_resolution, (1440, 900))
            
            await page.mouse.click(scaled_coords[0], scaled_coords[1])
            print(f"✅ Клик по координатам по умолчанию: {scaled_coords}")
            
            # Сохранить успешные координаты
            self.coordinate_db.save_coordinates(
                wallet_config.wallet_type, action_type, screen_resolution, scaled_coords
            )
            return True
        
        return False
    
    async def _try_dom_selector(self, page: Page, wallet_config: WalletExtension,
                              action_type: str, screen_resolution: Tuple[int, int]) -> bool:
        """Попытка с DOM селекторами"""
        # Найти страницу расширения
        extension_page = await self.detector._find_extension_page(page)
        
        if not extension_page:
            return False
        
        # Общие селекторы для действий кошелька
        selectors = {
            "connect": ["button:has-text('Connect')", "[data-testid='connect']"],
            "confirm": ["button:has-text('Confirm')", "[data-testid='confirm']"],
            "approve": ["button:has-text('Approve')", "[data-testid='approve']"],
            "sign": ["button:has-text('Sign')", "[data-testid='sign']"]
        }
        
        action_selectors = selectors.get(action_type, [])
        
        for selector in action_selectors:
            try:
                element = await extension_page.wait_for_selector(selector, timeout=2000)
                if element:
                    await element.click()
                    print(f"✅ Клик по DOM селектору: {selector}")
                    return True
            except:
                continue
        
        return False
    
    def _scale_coordinates(self, coords: Tuple[int, int],
                          current_resolution: Tuple[int, int],
                          base_resolution: Tuple[int, int]) -> Tuple[int, int]:
        """Масштабировать координаты"""
        scale_x = current_resolution[0] / base_resolution[0]
        scale_y = current_resolution[1] / base_resolution[1]
        
        return (int(coords[0] * scale_x), int(coords[1] * scale_y))

# Тестирование
async def test_extension_handler():
    """Тест обработчика расширений"""
    print("🧪 Тестирование extension_handler...")
    
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️ Playwright недоступен, пропускаем тест")
        return True
    
    try:
        from browser_automation_core import UniversalBrowserAutomator
        
        automator = UniversalBrowserAutomator()
        
        if not await automator.initialize():
            print("❌ Не удалось инициализировать систему")
            return False
        
        extension_handler = ExtensionActionHandler(automator.coordinate_db)
        
        profile = automator.profile_manager.get_available_profile()
        context = await automator.create_browser_context(profile)
        page = await context.new_page()
        
        await page.goto("https://example.com")
        
        # Тест координатных действий
        success = await extension_handler.perform_wallet_action(
            page, "connect", WalletType.RABBY
        )
        
        print(f"✅ Тест действия кошелька: {success}")
        
        await context.close()
        await automator.cleanup()
        
        print("✅ Тест extension_handler пройден!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_extension_handler())
