#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Launcher - Простой запуск системы автоматизации
"""

import asyncio
import sys
from pathlib import Path

# Добавляем core в путь
sys.path.append(str(Path(__file__).parent / "core"))

async def simple_test():
    """Простой тест системы"""
    print("🧪 Запуск простого теста системы...")
    
    try:
        from simple_main import SimpleAutomationSystem
        
        system = SimpleAutomationSystem()
        success = await system.test_basic_functionality()
        
        if success:
            print("\n🎉 Тест завершен успешно!")
            print("Система готова к работе!")
        else:
            print("\n❌ Тест не пройден")
            print("Проверьте установку зависимостей:")
            print("pip install -r requirements.txt")
            print("playwright install chromium")
        
        return success
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что все файлы созданы корректно")
        return False
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

async def interactive_mode():
    """Интерактивный режим"""
    try:
        from simple_main import SimpleCLI
        
        cli = SimpleCLI()
        await cli.run()
        
    except ImportError:
        print("❌ Основные модули не найдены")
        print("Запустите создание системы заново")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def show_help():
    """Показать справку"""
    help_text = """
🤖 Universal Browser Automation - Simple Launcher

Команды:
  test        - Запустить тест системы
  interactive - Интерактивный режим
  help        - Показать эту справку

Примеры:
  python simple_launcher.py test
  python simple_launcher.py interactive
  python simple_launcher.py

Требования:
  Python 3.8+
  pip install -r requirements.txt
  playwright install chromium
"""
    print(help_text)

async def main():
    """Главная функция"""
    print("🤖 Universal Browser Automation - Simple Launcher")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            await simple_test()
        elif command == "interactive":
            await interactive_mode()
        elif command == "help":
            show_help()
        else:
            print(f"Неизвестная команда: {command}")
            show_help()
    else:
        # По умолчанию интерактивный режим
        choice = input("Выберите режим:\n1. Тест\n2. Интерактивный\nВыбор (1/2): ")
        
        if choice == "1":
            await simple_test()
        else:
            await interactive_mode()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
