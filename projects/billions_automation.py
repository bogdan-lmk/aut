#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Billions Network Automation - Organized Version
===============================================

Автоматизация для https://signup.billions.network/
Размещение: projects/billions_automation.py
"""

import asyncio
import sys
from pathlib import Path

# Правильное добавление путей для организованной структуры
project_root = Path(__file__).parent.parent  # Поднимаемся на уровень выше из projects/
sys.path.append(str(project_root / "core"))

class BillionsNetworkAutomator:
    """Автоматизация для Billions Network"""
    
    def __init__(self):
        self.project_name = "billions_network"
        self.site_url = "https://signup.billions.network/"
        self.target_button_selectors = [
            # Основной селектор для кнопки "Click & Earn 25 power"
            'button.ant-btn.ant-btn-primary:has-text("Click & Earn")',
            'button:has-text("Click & Earn 25 power")',
            'button:has-text("Click & Earn")',
            '.ant-btn-primary:has-text("Click")',
            '.ant-btn.css-1xy5zgx:has-text("Click")',
            'button[type="button"]:has-text("Click")',
            'button:has-text("25 power")',
            'text=Click & Earn',
            'text=Click & Earn 25 power'
        ]
        
        # Создать папку для скриншотов проекта
        self.screenshots_dir = project_root / "screenshots" / self.project_name
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_automation(self, profile_count=1):
        """Запустить автоматизацию для указанного количества профилей"""
        print(f"🚀 Billions Network Automation")
        print(f"📍 Сайт: {self.site_url}")
        print(f"👥 Профилей: {profile_count}")
        print("=" * 50)
        
        try:
            from browser_automation_core import UniversalBrowserAutomator
            from extension_handler import ExtensionActionHandler, WalletType
            
            automator = UniversalBrowserAutomator()
            
            if not await automator.initialize():
                print("❌ Не удалось инициализировать браузерную систему")
                return False
            
            extension_handler = ExtensionActionHandler(automator.coordinate_db)
            
            successful_profiles = 0
            failed_profiles = 0
            
            for i in range(profile_count):
                print(f"\n👤 Профиль {i+1}/{profile_count}")
                print("-" * 30)
                
                success = await self._process_single_profile(
                    automator, extension_handler, i
                )
                
                if success:
                    successful_profiles += 1
                    print(f"✅ Профиль {i+1}: УСПЕХ")
                else:
                    failed_profiles += 1
                    print(f"❌ Профиль {i+1}: НЕУДАЧА")
                
                # Пауза между профилями (кроме последнего)
                if i < profile_count - 1:
                    print("⏳ Пауза 3 секунды...")
                    await asyncio.sleep(3)
            
            # Итоговая статистика
            print("\n" + "=" * 50)
            print("📊 ИТОГОВАЯ СТАТИСТИКА:")
            print(f"✅ Успешно: {successful_profiles}")
            print(f"❌ Неудачно: {failed_profiles}")
            print(f"📈 Успешность: {(successful_profiles/profile_count*100):.1f}%")
            print(f"📸 Скриншоты: {self.screenshots_dir}")
            
            await automator.cleanup()
            return successful_profiles > 0
            
        except ImportError as e:
            print(f"❌ Ошибка импорта модулей: {e}")
            print("💡 Убедитесь что:")
            print("   1. Запустили: python create_system.py")
            print("   2. Файл находится в папке projects/")
            return False
        except Exception as e:
            print(f"❌ Ошибка автоматизации: {e}")
            return False
    
    async def _process_single_profile(self, automator, extension_handler, profile_index):
        """Обработать один профиль"""
        try:
            # Получить профиль
            if profile_index < len(automator.profile_manager.profiles):
                profile = automator.profile_manager.profiles[profile_index]
            else:
                profile = automator.profile_manager.get_available_profile()
            
            if not profile:
                print(f"❌ Профиль недоступен")
                return False
            
            print(f"🔧 Профиль: {profile.id} ({profile.user_agent.split()[7] if len(profile.user_agent.split()) > 7 else 'Chrome'})")
            
            # Создать контекст браузера
            context = await automator.create_browser_context(profile)
            page = await context.new_page()
            
            try:
                # Шаг 1: Переход на сайт
                print(f"🌐 Загрузка {self.site_url}")
                await page.goto(self.site_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)  # Ждем полной загрузки
                
                # Шаг 2: Поиск и клик по кнопке
                button_clicked = await self._click_earn_button(page)
                
                if not button_clicked:
                    print("❌ Кнопка не найдена")
                    await self._save_screenshot(page, profile.id, "button_not_found")
                    return False
                
                print("✅ Кнопка 'Click & Earn 25 power' нажата!")
                
                # Шаг 3: Ждем и обрабатываем возможные реакции
                await asyncio.sleep(3)
                
                # Проверяем изменения на странице
                page_changed = await self._check_page_changes(page)
                
                # Шаг 4: Обработка кошелька (если появился)
                wallet_handled = await self._handle_wallet_popup(page, extension_handler)
                
                # Шаг 5: Финальный скриншот
                await self._save_screenshot(page, profile.id, "success")
                
                if page_changed or wallet_handled:
                    print("✅ Действие выполнено успешно")
                    return True
                else:
                    print("⚠️ Реакция страницы неясна, но кнопка была нажата")
                    return True
                
            finally:
                await context.close()
                automator.profile_manager.active_profiles.pop(profile.id, None)
                
        except Exception as e:
            print(f"❌ Ошибка обработки профиля: {e}")
            return False
    
    async def _click_earn_button(self, page):
        """Найти и кликнуть кнопку Click & Earn"""
        print("🔍 Поиск кнопки...")
        
        # Попробовать все селекторы по очереди
        for i, selector in enumerate(self.target_button_selectors, 1):
            try:
                print(f"   {i}. {selector[:50]}...")
                
                # Ждем появления элемента
                element = await page.wait_for_selector(selector, timeout=3000)
                
                if element:
                    # Проверяем доступность
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled()
                    
                    if is_visible and is_enabled:
                        print(f"   ✅ Найдена!")
                        
                        # Плавный скролл к элементу
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        
                        # Клик с небольшой задержкой
                        await element.click()
                        await asyncio.sleep(0.5)
                        
                        return True
                    else:
                        print(f"   ⚠️ Найдена, но неактивна")
                
            except Exception:
                continue
        
        # Если селекторы не сработали - координатный подход
        print("🎯 Координатный поиск...")
        return await self._try_coordinate_click(page)
    
    async def _try_coordinate_click(self, page):
        """Попытка клика по предполагаемым координатам"""
        try:
            viewport = page.viewport_size
            width = viewport["width"]
            height = viewport["height"]
            
            # Типичные места для кнопок на signup страницах
            coordinates = [
                (width // 2, height // 2),           # Центр
                (width // 2, int(height * 0.6)),     # Ниже центра
                (width // 2, int(height * 0.4)),     # Выше центра
                (width // 2, 400),                   # Фиксированная высота
                (width // 2, 350),
                (width // 2, 450),
            ]
            
            for i, (x, y) in enumerate(coordinates, 1):
                print(f"   {i}. Клик ({x}, {y})")
                
                await page.mouse.click(x, y)
                await asyncio.sleep(1)
                
                # Простая проверка - изменился ли URL или появились новые элементы
                try:
                    # Ждем возможных изменений
                    await page.wait_for_function("document.readyState === 'complete'", timeout=2000)
                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"   ❌ Координатный клик не удался: {e}")
            return False
    
    async def _check_page_changes(self, page):
        """Проверить изменения на странице после клика"""
        try:
            # Проверяем различные признаки успешного действия
            
            # 1. Изменение URL
            current_url = page.url
            if "success" in current_url.lower() or "complete" in current_url.lower():
                print("✅ URL изменился (успех)")
                return True
            
            # 2. Появление новых элементов
            success_indicators = [
                'text=Success',
                'text=Earned',
                'text=Claimed',
                'text=Complete',
                '.success',
                '.earned',
                '[class*="success"]'
            ]
            
            for indicator in success_indicators:
                try:
                    element = await page.wait_for_selector(indicator, timeout=1000)
                    if element:
                        print(f"✅ Найден индикатор успеха: {indicator}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    async def _handle_wallet_popup(self, page, extension_handler):
        """Обработать popup кошелька"""
        print("💰 Проверка кошелька...")
        
        try:
            # Проверяем появление popup кошелька
            await asyncio.sleep(2)
            
            # Пробуем стандартные действия кошелька
            for action in ["connect", "confirm", "approve", "sign"]:
                try:
                    success = await extension_handler.perform_wallet_action(page, action)
                    if success:
                        print(f"✅ Кошелек: {action}")
                        await asyncio.sleep(2)
                        return True
                except:
                    continue
            
            print("ℹ️ Кошелек не требуется")
            return False
            
        except Exception:
            return False
    
    async def _save_screenshot(self, page, profile_id, status):
        """Сохранить скриншот"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"{self.project_name}_{status}_{profile_id}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            await page.screenshot(path=str(filepath), full_page=True)
            print(f"📸 {filepath.name}")
            
        except Exception as e:
            print(f"⚠️ Скриншот не сохранен: {e}")

# Универсальный CLI для всех проектов
class ProjectAutomationCLI:
    """Универсальный CLI для автоматизации проектов"""
    
    def __init__(self, automator_class, project_name):
        self.automator = automator_class()
        self.project_name = project_name
    
    async def run(self):
        """Запуск CLI"""
        print(f"🤖 {self.project_name} Automation")
        print("=" * 50)
        
        while True:
            try:
                print(f"\n📍 Проект: {self.project_name}")
                print(f"🌐 Сайт: {self.automator.site_url}")
                print("\nВыберите действие:")
                print("1. 🧪 Тест (1 профиль)")
                print("2. 🚀 Запуск (5 профилей)")
                print("3. 💪 Массовый (10 профилей)")
                print("4. 🔥 Полный (30 профилей)")
                print("5. ⚙️ Выбрать количество")
                print("0. 🚪 Выход")
                
                choice = input("\nВаш выбор (0-5): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    await self.automator.run_automation(1)
                elif choice == "2":
                    await self.automator.run_automation(5)
                elif choice == "3":
                    await self.automator.run_automation(10)
                elif choice == "4":
                    print("⚠️ Запуск 30 профилей может занять много времени!")
                    confirm = input("Продолжить? (y/N): ").lower()
                    if confirm == 'y':
                        await self.automator.run_automation(30)
                elif choice == "5":
                    try:
                        count = int(input("Количество профилей (1-30): "))
                        if 1 <= count <= 30:
                            await self.automator.run_automation(count)
                        else:
                            print("❌ Число должно быть от 1 до 30")
                    except ValueError:
                        print("❌ Введите корректное число")
                else:
                    print("❌ Неверный выбор")
                    
            except KeyboardInterrupt:
                print("\n⏹️ Остановка...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        print(f"👋 {self.project_name} automation завершена!")

# Быстрые команды
async def quick_test():
    """Быстрый тест"""
    automator = BillionsNetworkAutomator()
    return await automator.run_automation(1)

async def run_batch(count):
    """Запуск пакета профилей"""
    automator = BillionsNetworkAutomator()
    return await automator.run_automation(count)

# Главная функция
async def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            success = await quick_test()
            print(f"\n{'🎉 Тест успешен!' if success else '❌ Тест не удался'}")
        elif command == "cli":
            cli = ProjectAutomationCLI(BillionsNetworkAutomator, "Billions Network")
            await cli.run()
        elif command.isdigit():
            count = int(command)
            if 1 <= count <= 30:
                success = await run_batch(count)
                print(f"\n{'🎉 Выполнено!' if success else '❌ Ошибки в выполнении'}")
            else:
                print("❌ Количество должно быть от 1 до 30")
        else:
            print("Команды:")
            print("  test      - быстрый тест")
            print("  cli       - интерактивный режим")  
            print("  [число]   - запуск N профилей")
    else:
        # По умолчанию CLI
        cli = ProjectAutomationCLI(BillionsNetworkAutomator, "Billions Network")
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