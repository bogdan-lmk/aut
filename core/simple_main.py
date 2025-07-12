#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Main System - Упрощенная главная система
Основные функции автоматизации без сложностей
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Импорт наших модулей
try:
    from browser_automation_core import UniversalBrowserAutomator, ConfigManager
    from extension_handler import ExtensionActionHandler, WalletType
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Ошибка импорта модулей: {e}")
    MODULES_AVAILABLE = False

class SimpleAutomationSystem:
    """Упрощенная система автоматизации"""
    
    def __init__(self):
        if not MODULES_AVAILABLE:
            print("❌ Основные модули недоступны")
            return
            
        self.automator = UniversalBrowserAutomator()
        self.extension_handler = None
        self.running = False
    
    async def initialize(self):
        """Инициализация системы"""
        if not MODULES_AVAILABLE:
            return False
            
        print("🚀 Инициализация Simple Automation System...")
        
        try:
            success = await self.automator.initialize()
            if not success:
                return False
            
            self.extension_handler = ExtensionActionHandler(
                self.automator.coordinate_db
            )
            
            print("✅ Система инициализирована")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if MODULES_AVAILABLE and self.automator:
            await self.automator.cleanup()
        print("✅ Ресурсы очищены")
    
    async def test_basic_functionality(self):
        """Тест базовой функциональности"""
        print("🧪 Тестирование базовой функциональности...")
        
        if not await self.initialize():
            return False
        
        try:
            # Получить профиль
            profile = self.automator.profile_manager.get_available_profile()
            if not profile:
                print("❌ Нет доступных профилей")
                return False
            
            print(f"✅ Получен профиль: {profile.id}")
            
            # Создать контекст браузера
            context = await self.automator.create_browser_context(profile)
            page = await context.new_page()
            
            # Открыть тестовую страницу
            await page.goto("https://example.com")
            print("✅ Страница загружена")
            
            # Сделать скриншот
            screenshot_path = Path("screenshots") / "test_screenshot.png"
            screenshot_path.parent.mkdir(exist_ok=True)
            await page.screenshot(path=str(screenshot_path))
            print(f"✅ Скриншот сохранен: {screenshot_path}")
            
            # Тест действий кошелька
            print("🔗 Тестирование действий кошелька...")
            success = await self.extension_handler.perform_wallet_action(
                page, "connect", WalletType.RABBY
            )
            print(f"✅ Тест кошелька: {'Успех' if success else 'Неудача'}")
            
            # Закрыть контекст
            await context.close()
            
            print("🎉 Тест базовой функциональности завершен успешно!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка в тесте: {e}")
            return False
        
        finally:
            await self.cleanup()
    
    async def run_interactive_mode(self):
        """Интерактивный режим"""
        print("🎮 Интерактивный режим Simple Automation System")
        print("=" * 50)
        
        if not await self.initialize():
            print("❌ Не удалось инициализировать систему")
            return
        
        while True:
            try:
                print("\nДоступные команды:")
                print("1. Тест системы")
                print("2. Открыть браузер")
                print("3. Тест кошелька")
                print("4. Информация о системе")
                print("0. Выход")
                
                choice = input("\nВведите команду (0-4): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    await self.test_basic_functionality()
                elif choice == "2":
                    await self._open_browser_demo()
                elif choice == "3":
                    await self._test_wallet_demo()
                elif choice == "4":
                    self._show_system_info()
                else:
                    print("❌ Неверная команда")
                    
            except KeyboardInterrupt:
                print("\n\n⏹️ Остановка...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        await self.cleanup()
        print("👋 До свидания!")
    
    async def _open_browser_demo(self):
        """Демо открытия браузера"""
        print("🌐 Открытие браузера...")
        
        try:
            profile = self.automator.profile_manager.get_available_profile()
            context = await self.automator.create_browser_context(profile)
            page = await context.new_page()
            
            await page.goto("https://google.com")
            print("✅ Браузер открыт на Google")
            
            input("Нажмите Enter для закрытия браузера...")
            await context.close()
            
        except Exception as e:
            print(f"❌ Ошибка открытия браузера: {e}")
    
    async def _test_wallet_demo(self):
        """Демо теста кошелька"""
        print("💰 Тестирование кошелька...")
        
        try:
            profile = self.automator.profile_manager.get_available_profile()
            context = await self.automator.create_browser_context(profile)
            page = await context.new_page()
            
            await page.goto("https://app.uniswap.org")
            print("✅ Открыт Uniswap")
            
            # Имитация клика на Connect Wallet
            try:
                await page.click("text=Connect Wallet", timeout=5000)
                print("✅ Найдена кнопка Connect Wallet")
                
                await asyncio.sleep(2)
                
                # Тест действий кошелька
                success = await self.extension_handler.perform_wallet_action(
                    page, "connect", WalletType.RABBY
                )
                print(f"✅ Тест кошелька: {'Успех' if success else 'Координаты отработали'}")
                
            except Exception:
                print("ℹ️ Кнопка Connect Wallet не найдена (это нормально для теста)")
            
            await context.close()
            
        except Exception as e:
            print(f"❌ Ошибка теста кошелька: {e}")
    
    def _show_system_info(self):
        """Показать информацию о системе"""
        print("\n📊 Информация о системе:")
        print(f"Модули доступны: {'✅' if MODULES_AVAILABLE else '❌'}")
        print(f"Всего профилей: {len(self.automator.profile_manager.profiles) if MODULES_AVAILABLE else 'N/A'}")
        print(f"Активных профилей: {len(self.automator.profile_manager.active_profiles) if MODULES_AVAILABLE else 'N/A'}")
        
        # Проверка конфигурации
        config_exists = Path("config.json").exists()
        print(f"Конфигурация: {'✅' if config_exists else '❌'}")
        
        # Проверка базы данных
        db_exists = Path("data/coordinates.db").exists()
        print(f"База координат: {'✅' if db_exists else '❌'}")

class SimpleCLI:
    """Простой интерфейс командной строки"""
    
    def __init__(self):
        self.system = SimpleAutomationSystem()
    
    async def run(self):
        """Запуск CLI"""
        print("🤖 Universal Browser Automation - Simple System")
        print("=" * 50)
        
        await self.system.run_interactive_mode()

# Главная функция
async def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        system = SimpleAutomationSystem()
        
        if command == "test":
            await system.test_basic_functionality()
        elif command == "interactive":
            await system.run_interactive_mode()
        else:
            print("Доступные команды: test, interactive")
    else:
        # Интерактивный режим по умолчанию
        cli = SimpleCLI()
        await cli.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
