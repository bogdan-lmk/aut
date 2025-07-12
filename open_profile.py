#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Profile Browser - Простое открытие профиля
=================================================

Простой способ открыть любой профиль в обычном браузере Chromium
для ручной работы или проверки.

Использование:
python open_profile.py 1          # Открыть профиль #1
python open_profile.py 5          # Открыть профиль #5
python open_profile.py            # Выбрать интерактивно
"""

import asyncio
import sys
from pathlib import Path

# Добавляем core в путь
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "core"))

class SimpleProfileBrowser:
    """Простое открытие профилей в браузере"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    async def initialize(self):
        """Инициализация Playwright"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            print("✅ Playwright готов")
            return True
            
        except ImportError:
            print("❌ Playwright не установлен")
            print("💡 Установите: pip install playwright")
            print("💡 Затем: playwright install chromium")
            return False
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def open_profile_browser(self, profile_number: int, url: str = None):
        """Открыть профиль в браузере"""
        print(f"🚀 Открытие профиля #{profile_number}")
        
        try:
            # Проверяем есть ли постоянные профили
            if await self._try_persistent_profile(profile_number, url):
                return True
            
            # Если нет - используем временный профиль
            return await self._open_temporary_profile(profile_number, url)
            
        except Exception as e:
            print(f"❌ Ошибка открытия профиля: {e}")
            return False
    
    async def _try_persistent_profile(self, profile_number: int, url: str = None):
        """Попытка открыть постоянный профиль"""
        try:
            # Пробуем загрузить постоянные профили
            from persistent_profiles import PersistentProfileManager
            
            profile_manager = PersistentProfileManager()
            profile = profile_manager.get_profile_by_number(profile_number)
            
            if not profile:
                print(f"❌ Постоянный профиль #{profile_number} не найден")
                return False
            
            print(f"👤 Профиль: {profile.name}")
            print(f"📧 Email: {profile.email}")
            print(f"💰 Кошелек: {profile.wallet_type}")
            print(f"🌐 Браузер: {profile.user_agent.split('Chrome/')[1].split()[0] if 'Chrome/' in profile.user_agent else 'Chrome'}")
            
            # Путь к данным профиля
            profile_data_dir = Path("browser_profiles") / profile.id
            profile_data_dir.mkdir(exist_ok=True)
            
            print(f"📁 Данные профиля: {profile_data_dir}")
            print("🔄 Запуск браузера...")
            
            # Запустить постоянный браузер
            browser = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_data_dir),
                headless=False,
                viewport=profile.viewport,
                user_agent=profile.user_agent,
                locale=profile.locale,
                timezone_id=profile.timezone,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )
            
            # Открыть страницу
            if len(browser.pages) > 0:
                page = browser.pages[0]
            else:
                page = await browser.new_page()
            
            # Перейти на указанный URL или стартовую страницу
            target_url = url or "https://signup.billions.network/"
            print(f"🌐 Переход на: {target_url}")
            await page.goto(target_url)
            
            print("✅ Браузер открыт!")
            print("🔓 Браузер работает независимо")
            print("💡 Нажмите Enter чтобы завершить скрипт (браузер останется)")
            
            # Простое ожидание ввода
            try:
                # Ждем ввода пользователя в отдельном потоке
                import concurrent.futures
                loop = asyncio.get_event_loop()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Запускаем input в отдельном потоке
                    input_future = loop.run_in_executor(executor, input, "")
                    
                    # Ждем либо ввода, либо закрытия браузера (с таймаутом)
                    try:
                        await asyncio.wait_for(input_future, timeout=1.0)
                        print("🚀 Скрипт завершен, браузер остается открытым")
                    except asyncio.TimeoutError:
                        # Таймаут - это нормально, браузер остается открытым
                        print("🚀 Браузер запущен и работает независимо")
                        
            except Exception:
                # В любом случае даем браузеру время запуститься
                await asyncio.sleep(1)
                print("🚀 Браузер остается открытым")
            
            return True
            
        except ImportError:
            print("⚠️ Система постоянных профилей недоступна")
            return False
        except Exception as e:
            print(f"❌ Ошибка постоянного профиля: {e}")
            return False
    
    async def _open_temporary_profile(self, profile_number: int, url: str = None):
        """Открыть временный профиль"""
        try:
            print(f"🔄 Создание временного профиля #{profile_number}")
            
            # Генерируем данные временного профиля
            profile_data = self._generate_temp_profile_data(profile_number)
            
            print(f"👤 Временный профиль: User {profile_number}")
            print(f"🌐 User-Agent: {profile_data['user_agent'].split('Chrome/')[1].split()[0] if 'Chrome/' in profile_data['user_agent'] else 'Chrome'}")
            print(f"📱 Разрешение: {profile_data['viewport']['width']}x{profile_data['viewport']['height']}")
            
            # Создать временную папку для данных
            temp_profile_dir = Path("browser_profiles") / f"temp_profile_{profile_number:02d}"
            temp_profile_dir.mkdir(exist_ok=True)
            
            print("🔄 Запуск браузера...")
            
            # Запустить браузер
            browser = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(temp_profile_dir),
                headless=False,
                viewport=profile_data['viewport'],
                user_agent=profile_data['user_agent'],
                locale=profile_data['locale'],
                timezone_id=profile_data['timezone'],
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
                ]
            )
            
            # Открыть страницу
            if len(browser.pages) > 0:
                page = browser.pages[0]
            else:
                page = await browser.new_page()
            
            # Перейти на URL
            target_url = url or "https://signup.billions.network/"
            print(f"🌐 Переход на: {target_url}")
            await page.goto(target_url)
            
            print("✅ Временный браузер открыт!")
            print("🔓 Браузер работает независимо")
            print("💡 Нажмите Enter чтобы завершить скрипт (браузер останется)")
            
            # Простое ожидание
            try:
                import concurrent.futures
                loop = asyncio.get_event_loop()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    input_future = loop.run_in_executor(executor, input, "")
                    
                    try:
                        await asyncio.wait_for(input_future, timeout=1.0)
                        print("🚀 Скрипт завершен, браузер остается открытым")
                    except asyncio.TimeoutError:
                        print("🚀 Браузер запущен и работает независимо")
                        
            except Exception:
                await asyncio.sleep(1)
                print("🚀 Браузер остается открытым")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка временного профиля: {e}")
            return False
    
    def _generate_temp_profile_data(self, profile_number: int):
        """Генерация данных временного профиля"""
        import random
        
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
        
        locales = ["en-US", "en-GB", "en-CA"]
        timezones = ["America/New_York", "America/Los_Angeles", "Europe/London"]
        
        # Детерминированный выбор на основе номера профиля
        random.seed(profile_number)
        
        return {
            'user_agent': user_agents[profile_number % len(user_agents)],
            'viewport': viewports[profile_number % len(viewports)],
            'locale': locales[profile_number % len(locales)],
            'timezone': timezones[profile_number % len(timezones)]
        }
    
    async def cleanup(self):
        """Очистка ресурсов (НЕ закрывая браузеры)"""
        # НЕ закрываем браузеры - они должны остаться работать
        if self.playwright:
            try:
                # Отсоединяемся от playwright, но браузеры остаются
                pass  # Не вызываем stop() чтобы браузеры не закрылись
            except:
                pass

class ProfileBrowserCLI:
    """CLI для открытия профилей"""
    
    def __init__(self):
        self.browser_opener = SimpleProfileBrowser()
    
    async def run(self):
        """Запуск CLI"""
        print("🌐 Simple Profile Browser")
        print("=" * 30)
        
        if not await self.browser_opener.initialize():
            return
        
        while True:
            try:
                print("\nВыберите действие:")
                print("1. 🚀 Открыть профиль по номеру")
                print("2. 🎯 Открыть профиль с URL")
                print("3. 📋 Быстрые ссылки")
                print("4. 📊 Информация о профилях")
                print("0. 🚪 Выход")
                
                choice = input("\nВыбор (0-4): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    await self._open_profile_by_number()
                elif choice == "2":
                    await self._open_profile_with_url()
                elif choice == "3":
                    await self._quick_links()
                elif choice == "4":
                    await self._show_profiles_info()
                else:
                    print("❌ Неверный выбор")
                    
            except KeyboardInterrupt:
                print("\n👋 Выход...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        await self.browser_opener.cleanup()
        print("👋 Скрипт завершен!")
        print("💡 Открытые браузеры продолжают работать")
    
    async def _open_profile_by_number(self):
        """Открыть профиль по номеру"""
        try:
            number = int(input("Номер профиля (1-30): "))
            if 1 <= number <= 30:
                await self.browser_opener.open_profile_browser(number)
            else:
                print("❌ Номер должен быть от 1 до 30")
        except ValueError:
            print("❌ Введите корректный номер")
    
    async def _open_profile_with_url(self):
        """Открыть профиль с конкретным URL"""
        try:
            number = int(input("Номер профиля (1-30): "))
            if not (1 <= number <= 30):
                print("❌ Номер должен быть от 1 до 30")
                return
            
            url = input("URL (Enter для billions.network): ").strip()
            if not url:
                url = "https://signup.billions.network/"
            
            await self.browser_opener.open_profile_browser(number, url)
            
        except ValueError:
            print("❌ Введите корректный номер")
    
    async def _quick_links(self):
        """Быстрые ссылки"""
        quick_links = {
            "1": ("Billions Network", "https://signup.billions.network/"),
            "2": ("Uniswap", "https://app.uniswap.org"),
            "3": ("Aave", "https://app.aave.com"),
            "4": ("Google", "https://google.com"),
            "5": ("Gmail", "https://gmail.com")
        }
        
        print("\n🔗 Быстрые ссылки:")
        for key, (name, url) in quick_links.items():
            print(f"{key}. {name} - {url}")
        
        try:
            profile_num = int(input("\nНомер профиля (1-30): "))
            if not (1 <= profile_num <= 30):
                print("❌ Номер должен быть от 1 до 30")
                return
            
            link_choice = input("Выберите ссылку (1-5): ").strip()
            if link_choice in quick_links:
                name, url = quick_links[link_choice]
                print(f"🚀 Открытие {name} в профиле #{profile_num}")
                await self.browser_opener.open_profile_browser(profile_num, url)
            else:
                print("❌ Неверный выбор ссылки")
                
        except ValueError:
            print("❌ Введите корректный номер")
    
    async def _show_profiles_info(self):
        """Показать информацию о профилях"""
        try:
            # Попробовать загрузить информацию о постоянных профилях
            from persistent_profiles import PersistentProfileManager
            
            profile_manager = PersistentProfileManager()
            profiles = profile_manager.get_available_profiles(10)  # Первые 10
            
            print("\n👥 ДОСТУПНЫЕ ПРОФИЛИ:")
            print("-" * 50)
            
            for profile in profiles:
                status = "🟢" if profile.is_active else "🔴"
                print(f"{status} #{profile.number:02d} | {profile.name}")
                print(f"     📧 {profile.email}")
                print(f"     💰 {profile.wallet_type}")
                print(f"     🔢 Использований: {profile.usage_count}")
                print()
            
            if len(profiles) >= 10:
                print("... и еще профили")
                
        except ImportError:
            print("\n⚠️ Система постоянных профилей недоступна")
            print("📋 Доступны временные профили #1-30")
            print("💡 Создайте постоянные профили:")
            print("   python core/persistent_profiles.py test")

# Быстрые функции
async def quick_open(profile_number: int, url: str = None):
    """Быстро открыть профиль"""
    browser = SimpleProfileBrowser()
    
    if await browser.initialize():
        await browser.open_profile_browser(profile_number, url)
        await browser.cleanup()
    else:
        print("❌ Не удалось инициализировать браузер")

# Главная функция
async def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        try:
            # Если передан номер профиля
            profile_number = int(sys.argv[1])
            
            if not (1 <= profile_number <= 30):
                print("❌ Номер профиля должен быть от 1 до 30")
                return
            
            # URL (опционально)
            url = sys.argv[2] if len(sys.argv) > 2 else None
            
            print(f"🚀 Быстрое открытие профиля #{profile_number}")
            if url:
                print(f"🌐 URL: {url}")
            
            await quick_open(profile_number, url)
            
        except ValueError:
            print("❌ Первый аргумент должен быть номером профиля (1-30)")
            print("💡 Использование: python open_profile.py 5")
            print("💡 Или с URL: python open_profile.py 5 https://google.com")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    else:
        # Интерактивный режим
        cli = ProfileBrowserCLI()
        await cli.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()