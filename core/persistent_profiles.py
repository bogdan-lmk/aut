#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistent Profiles System - Система постоянных профилей
========================================================

Создает и управляет постоянными профилями браузера с:
- Уникальными кошельками
- Постоянными email адресами  
- Сохранением cookies и session
- Историей браузера
- Persistent storage
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import random
import string
import secrets

@dataclass
class PersistentProfile:
    """Постоянный профиль браузера с полными данными"""
    # Основные данные профиля
    id: str
    number: int                              # Номер профиля (1-30)
    name: str
    
    # Браузерные настройки
    user_agent: str
    viewport: Dict[str, int]
    locale: str
    timezone: str
    
    # Постоянные данные пользователя
    email: str                               # Постоянный email
    password: str                            # Постоянный пароль
    username: str                            # Постоянное имя пользователя
    
    # Кошелек данные
    wallet_type: str                         # rabby, phantom, metamask
    wallet_address: str                      # Адрес кошелька (если есть)
    wallet_seed: str                         # Seed phrase (зашифрованная)
    
    # Профиль пользователя
    first_name: str
    last_name: str
    birth_date: str                          # YYYY-MM-DD
    phone_number: str                        # Телефон (если нужен)
    
    # Социальные сети
    twitter_username: str                    # Twitter аккаунт
    discord_username: str                    # Discord аккаунт
    telegram_username: str                   # Telegram аккаунт
    
    # Системные данные
    proxy: Optional[Dict[str, str]] = None   # Proxy настройки
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    
    # Статус активности
    is_active: bool = True
    notes: str = ""                          # Заметки о профиле

class PersistentProfileManager:
    """Менеджер постоянных профилей"""
    
    def __init__(self, profiles_count: int = 30):
        self.profiles_count = profiles_count
        self.profiles: List[PersistentProfile] = []
        self.profiles_db_path = Path("data/persistent_profiles.db")
        self.browser_data_dir = Path("browser_profiles")
        
        # Создать необходимые директории
        self.profiles_db_path.parent.mkdir(exist_ok=True)
        self.browser_data_dir.mkdir(exist_ok=True)
        
        self._init_database()
        self._load_or_create_profiles()
    
    def _init_database(self):
        """Инициализация базы данных профилей"""
        with sqlite3.connect(self.profiles_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persistent_profiles (
                    id TEXT PRIMARY KEY,
                    number INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    
                    -- Браузерные настройки
                    user_agent TEXT NOT NULL,
                    viewport_width INTEGER NOT NULL,
                    viewport_height INTEGER NOT NULL,
                    locale TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    
                    -- Пользовательские данные
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    username TEXT NOT NULL,
                    
                    -- Кошелек
                    wallet_type TEXT NOT NULL,
                    wallet_address TEXT,
                    wallet_seed TEXT,
                    
                    -- Профиль
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    phone_number TEXT,
                    
                    -- Социальные сети
                    twitter_username TEXT,
                    discord_username TEXT,
                    telegram_username TEXT,
                    
                    -- Системное
                    proxy_config TEXT,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    notes TEXT DEFAULT ''
                )
            """)
            
            # Таблица для истории использования
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profile_usage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (profile_id) REFERENCES persistent_profiles (id)
                )
            """)
    
    def _load_or_create_profiles(self):
        """Загрузить существующие профили или создать новые"""
        print("📋 Загрузка постоянных профилей...")
        
        # Попробовать загрузить из базы
        existing_profiles = self._load_profiles_from_db()
        
        if len(existing_profiles) == self.profiles_count:
            self.profiles = existing_profiles
            print(f"✅ Загружено {len(self.profiles)} существующих профилей")
        else:
            print(f"🔧 Создание {self.profiles_count} новых профилей...")
            self._create_new_profiles()
            print(f"✅ Создано {len(self.profiles)} профилей")
    
    def _load_profiles_from_db(self) -> List[PersistentProfile]:
        """Загрузить профили из базы данных"""
        profiles = []
        
        try:
            with sqlite3.connect(self.profiles_db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM persistent_profiles ORDER BY number
                """)
                
                for row in cursor.fetchall():
                    # Распаковать данные из БД
                    profile_data = {
                        'id': row[0],
                        'number': row[1],
                        'name': row[2],
                        'user_agent': row[3],
                        'viewport': {'width': row[4], 'height': row[5]},
                        'locale': row[6],
                        'timezone': row[7],
                        'email': row[8],
                        'password': row[9],
                        'username': row[10],
                        'wallet_type': row[11],
                        'wallet_address': row[12] or '',
                        'wallet_seed': row[13] or '',
                        'first_name': row[14],
                        'last_name': row[15],
                        'birth_date': row[16],
                        'phone_number': row[17] or '',
                        'twitter_username': row[18] or '',
                        'discord_username': row[19] or '',
                        'telegram_username': row[20] or '',
                        'proxy': json.loads(row[21]) if row[21] else None,
                        'created_at': datetime.fromisoformat(row[22]),
                        'last_used': datetime.fromisoformat(row[23]) if row[23] else None,
                        'usage_count': row[24],
                        'is_active': bool(row[25]),
                        'notes': row[26]
                    }
                    
                    profile = PersistentProfile(**profile_data)
                    profiles.append(profile)
                    
        except Exception as e:
            print(f"⚠️ Ошибка загрузки профилей: {e}")
            return []
        
        return profiles
    
    def _create_new_profiles(self):
        """Создать новые профили"""
        self.profiles = []
        
        # Базовые данные для генерации
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1440, "height": 900},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1280, "height": 720}
        ]
        
        locales = ["en-US", "en-GB", "en-CA", "en-AU"]
        timezones = ["America/New_York", "America/Los_Angeles", "Europe/London", "Europe/Berlin"]
        
        first_names = ["John", "Mike", "David", "Chris", "Alex", "Sam", "Tom", "Jack", "Nick", "Paul"]
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas"]
        
        email_domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "icloud.com"]
        wallet_types = ["rabby", "phantom", "metamask"]
        
        for i in range(self.profiles_count):
            # Генерация уникальных данных
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Уникальные имена пользователей
            username = f"{first_name.lower()}{last_name.lower()}{i+1:02d}"
            email = f"{username}@{random.choice(email_domains)}"
            
            # Генерация надежного пароля
            password = self._generate_password()
            
            # Даты рождения (от 18 до 35 лет)
            birth_year = random.randint(1988, 2005)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
            
            # Телефон (опционально)
            phone = f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
            
            # Социальные сети (на основе username)
            twitter_user = f"{username}_tw"
            discord_user = f"{username}#{random.randint(1000, 9999)}"
            telegram_user = f"@{username}_tg"
            
            profile = PersistentProfile(
                id=f"profile_{i:02d}",
                number=i + 1,
                name=f"{first_name} {last_name} (Profile {i+1})",
                
                # Браузерные настройки
                user_agent=random.choice(user_agents),
                viewport=random.choice(viewports),
                locale=random.choice(locales),
                timezone=random.choice(timezones),
                
                # Пользовательские данные
                email=email,
                password=password,
                username=username,
                
                # Кошелек
                wallet_type=random.choice(wallet_types),
                wallet_address="",  # Будет заполнен при создании кошелька
                wallet_seed="",     # Будет заполнен при создании кошелька
                
                # Профиль
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                phone_number=phone,
                
                # Социальные сети
                twitter_username=twitter_user,
                discord_username=discord_user,
                telegram_username=telegram_user,
                
                # Системное
                proxy=None,
                is_active=True,
                notes=f"Auto-generated profile {i+1}"
            )
            
            self.profiles.append(profile)
            
            # Создать папку для браузерных данных профиля
            profile_dir = self.browser_data_dir / profile.id
            profile_dir.mkdir(exist_ok=True)
            
            # Сохранить в базу данных
            self._save_profile_to_db(profile)
        
        print(f"✅ Создано {len(self.profiles)} уникальных профилей")
    
    def _generate_password(self, length: int = 12) -> str:
        """Генерация надежного пароля"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    def _save_profile_to_db(self, profile: PersistentProfile):
        """Сохранить профиль в базу данных"""
        with sqlite3.connect(self.profiles_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO persistent_profiles VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.id, profile.number, profile.name,
                profile.user_agent, profile.viewport['width'], profile.viewport['height'],
                profile.locale, profile.timezone,
                profile.email, profile.password, profile.username,
                profile.wallet_type, profile.wallet_address, profile.wallet_seed,
                profile.first_name, profile.last_name, profile.birth_date, profile.phone_number,
                profile.twitter_username, profile.discord_username, profile.telegram_username,
                json.dumps(profile.proxy) if profile.proxy else None,
                profile.created_at.isoformat(),
                profile.last_used.isoformat() if profile.last_used else None,
                profile.usage_count, profile.is_active, profile.notes
            ))
    
    def get_profile(self, profile_id: str) -> Optional[PersistentProfile]:
        """Получить профиль по ID"""
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        return None
    
    def get_profile_by_number(self, number: int) -> Optional[PersistentProfile]:
        """Получить профиль по номеру"""
        for profile in self.profiles:
            if profile.number == number:
                return profile
        return None
    
    def get_available_profiles(self, count: int = None) -> List[PersistentProfile]:
        """Получить доступные профили"""
        active_profiles = [p for p in self.profiles if p.is_active]
        
        if count:
            return active_profiles[:count]
        return active_profiles
    
    def update_profile_usage(self, profile_id: str, project_name: str, action: str, success: bool, details: str = ""):
        """Обновить статистику использования профиля"""
        profile = self.get_profile(profile_id)
        if profile:
            profile.last_used = datetime.now()
            profile.usage_count += 1
            self._save_profile_to_db(profile)
            
            # Сохранить в историю
            with sqlite3.connect(self.profiles_db_path) as conn:
                conn.execute("""
                    INSERT INTO profile_usage_history 
                    (profile_id, project_name, action, success, timestamp, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (profile_id, project_name, action, success, datetime.now().isoformat(), details))
    
    def update_wallet_data(self, profile_id: str, wallet_address: str, wallet_seed: str = ""):
        """Обновить данные кошелька профиля"""
        profile = self.get_profile(profile_id)
        if profile:
            profile.wallet_address = wallet_address
            if wallet_seed:
                profile.wallet_seed = wallet_seed  # В реальности нужно зашифровать
            self._save_profile_to_db(profile)
    
    def export_profiles_info(self) -> str:
        """Экспортировать информацию о профилях"""
        info = []
        info.append("📋 ПОСТОЯННЫЕ ПРОФИЛИ БРАУЗЕРА")
        info.append("=" * 50)
        
        for profile in self.profiles:
            info.append(f"\n👤 ПРОФИЛЬ #{profile.number} ({profile.id})")
            info.append(f"   Имя: {profile.first_name} {profile.last_name}")
            info.append(f"   Email: {profile.email}")
            info.append(f"   Логин: {profile.username}")
            info.append(f"   Пароль: {profile.password}")
            info.append(f"   Кошелек: {profile.wallet_type}")
            if profile.wallet_address:
                info.append(f"   Адрес: {profile.wallet_address}")
            info.append(f"   Twitter: {profile.twitter_username}")
            info.append(f"   Discord: {profile.discord_username}")
            info.append(f"   Телефон: {profile.phone_number}")
            info.append(f"   Использований: {profile.usage_count}")
            if profile.last_used:
                info.append(f"   Последнее: {profile.last_used.strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(info)
    
    def get_profiles_summary(self) -> Dict[str, Any]:
        """Получить сводку по профилям"""
        active_count = len([p for p in self.profiles if p.is_active])
        
        wallet_types = {}
        for profile in self.profiles:
            wallet_types[profile.wallet_type] = wallet_types.get(profile.wallet_type, 0) + 1
        
        total_usage = sum(p.usage_count for p in self.profiles)
        
        return {
            "total_profiles": len(self.profiles),
            "active_profiles": active_count,
            "wallet_distribution": wallet_types,
            "total_usage": total_usage,
            "avg_usage_per_profile": total_usage / len(self.profiles) if self.profiles else 0
        }

# Интеграция с браузерной системой
class PersistentBrowserAutomator:
    """Браузерный автоматор с постоянными профилями"""
    
    def __init__(self, config_path: str = "config.json"):
        from browser_automation_core import ConfigManager, CoordinateDatabase
        
        self.config = ConfigManager(config_path)
        self.coordinate_db = CoordinateDatabase()
        self.profile_manager = PersistentProfileManager(30)
        self.playwright = None
        self.browsers: Dict[str, Any] = {}
    
    async def initialize(self):
        """Инициализация с постоянными профилями"""
        print("🚀 Инициализация браузерной системы с постоянными профилями...")
        
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            print("✅ Playwright инициализирован")
            
            summary = self.profile_manager.get_profiles_summary()
            print(f"✅ Загружено {summary['total_profiles']} постоянных профилей")
            print(f"   Активных: {summary['active_profiles']}")
            print(f"   Кошельки: {summary['wallet_distribution']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    async def create_persistent_browser_context(self, profile: PersistentProfile):
        """Создать постоянный контекст браузера"""
        try:
            # Путь к данным профиля
            profile_data_dir = Path("browser_profiles") / profile.id
            profile_data_dir.mkdir(exist_ok=True)
            
            # Запустить браузер с постоянным профилем
            browser = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_data_dir),
                headless=self.config.get("browser.headless", False),
                viewport=profile.viewport,
                user_agent=profile.user_agent,
                locale=profile.locale,
                timezone_id=profile.timezone,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            
            print(f"✅ Создан постоянный контекст для {profile.name}")
            return browser
            
        except Exception as e:
            print(f"❌ Ошибка создания постоянного контекста: {e}")
            raise
    
    async def cleanup(self):
        """Очистка ресурсов"""
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

# CLI для управления профилями
class ProfileManagerCLI:
    """CLI для управления постоянными профилями"""
    
    def __init__(self):
        self.profile_manager = PersistentProfileManager()
    
    def run(self):
        """Запуск CLI управления профилями"""
        print("👥 Менеджер постоянных профилей")
        print("=" * 40)
        
        while True:
            try:
                print("\nДоступные команды:")
                print("1. 📋 Список всех профилей")
                print("2. 👤 Информация о профиле")
                print("3. 💰 Обновить данные кошелька")
                print("4. 📊 Статистика профилей")
                print("5. 📤 Экспорт данных профилей")
                print("6. 🔧 Деактивировать профиль")
                print("7. ✅ Активировать профиль")
                print("0. 🚪 Выход")
                
                choice = input("\nВыбор (0-7): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    self._list_profiles()
                elif choice == "2":
                    self._show_profile_info()
                elif choice == "3":
                    self._update_wallet_data()
                elif choice == "4":
                    self._show_statistics()
                elif choice == "5":
                    self._export_profiles()
                elif choice == "6":
                    self._deactivate_profile()
                elif choice == "7":
                    self._activate_profile()
                else:
                    print("❌ Неверный выбор")
                    
            except KeyboardInterrupt:
                print("\n👋 Выход из менеджера профилей")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    def _list_profiles(self):
        """Показать список профилей"""
        print("\n📋 СПИСОК ПРОФИЛЕЙ:")
        print("-" * 60)
        
        for profile in self.profile_manager.profiles:
            status = "🟢" if profile.is_active else "🔴"
            wallet_info = f"({profile.wallet_type})" if profile.wallet_type else ""
            usage_info = f"[{profile.usage_count} использований]"
            
            print(f"{status} #{profile.number:02d} | {profile.name} | {profile.email} {wallet_info} {usage_info}")
    
    def _show_profile_info(self):
        """Показать подробную информацию о профиле"""
        try:
            number = int(input("Номер профиля (1-30): "))
            profile = self.profile_manager.get_profile_by_number(number)
            
            if not profile:
                print("❌ Профиль не найден")
                return
            
            print(f"\n👤 ПРОФИЛЬ #{profile.number} - {profile.name}")
            print("=" * 50)
            print(f"ID: {profile.id}")
            print(f"Статус: {'🟢 Активен' if profile.is_active else '🔴 Неактивен'}")
            print(f"Email: {profile.email}")
            print(f"Пароль: {profile.password}")
            print(f"Логин: {profile.username}")
            print(f"Имя: {profile.first_name} {profile.last_name}")
            print(f"Дата рождения: {profile.birth_date}")
            print(f"Телефон: {profile.phone_number}")
            print(f"Кошелек: {profile.wallet_type}")
            if profile.wallet_address:
                print(f"Адрес кошелька: {profile.wallet_address}")
            print(f"Twitter: {profile.twitter_username}")
            print(f"Discord: {profile.discord_username}")
            print(f"Telegram: {profile.telegram_username}")
            print(f"Браузер: {profile.user_agent.split()[7] if len(profile.user_agent.split()) > 7 else 'Chrome'}")
            print(f"Разрешение: {profile.viewport['width']}x{profile.viewport['height']}")
            print(f"Локаль: {profile.locale}")
            print(f"Использований: {profile.usage_count}")
            if profile.last_used:
                print(f"Последнее использование: {profile.last_used.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Создан: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if profile.notes:
                print(f"Заметки: {profile.notes}")
                
        except ValueError:
            print("❌ Введите корректный номер")
    
    def _update_wallet_data(self):
        """Обновить данные кошелька"""
        try:
            number = int(input("Номер профиля (1-30): "))
            profile = self.profile_manager.get_profile_by_number(number)
            
            if not profile:
                print("❌ Профиль не найден")
                return
            
            print(f"Текущий кошелек: {profile.wallet_type}")
            print(f"Текущий адрес: {profile.wallet_address or 'Не задан'}")
            
            new_address = input("Новый адрес кошелька (Enter - пропустить): ").strip()
            if new_address:
                self.profile_manager.update_wallet_data(profile.id, new_address)
                print("✅ Адрес кошелька обновлен")
            
        except ValueError:
            print("❌ Введите корректный номер")
    
    def _show_statistics(self):
        """Показать статистику"""
        summary = self.profile_manager.get_profiles_summary()
        
        print("\n📊 СТАТИСТИКА ПРОФИЛЕЙ:")
        print("=" * 30)
        print(f"Всего профилей: {summary['total_profiles']}")
        print(f"Активных: {summary['active_profiles']}")
        print(f"Общее использований: {summary['total_usage']}")
        print(f"Среднее на профиль: {summary['avg_usage_per_profile']:.1f}")
        
        print("\n💰 Распределение кошельков:")
        for wallet_type, count in summary['wallet_distribution'].items():
            print(f"  {wallet_type}: {count} профилей")
    
    def _export_profiles(self):
        """Экспортировать данные профилей"""
        export_data = self.profile_manager.export_profiles_info()
        
        # Сохранить в файл
        export_file = Path("exports") / f"profiles_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        export_file.parent.mkdir(exist_ok=True)
        
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(export_data)
        
        print(f"✅ Данные экспортированы в {export_file}")
        
        # Показать краткую версию
        print("\n📤 КРАТКИЙ ЭКСПОРТ:")
        for profile in self.profile_manager.profiles[:5]:  # Первые 5
            print(f"#{profile.number}: {profile.email} | {profile.password} | {profile.wallet_type}")
        
        if len(self.profile_manager.profiles) > 5:
            print(f"... и еще {len(self.profile_manager.profiles) - 5} профилей")
    
    def _deactivate_profile(self):
        """Деактивировать профиль"""
        try:
            number = int(input("Номер профиля для деактивации (1-30): "))
            profile = self.profile_manager.get_profile_by_number(number)
            
            if not profile:
                print("❌ Профиль не найден")
                return
            
            if not profile.is_active:
                print("⚠️ Профиль уже неактивен")
                return
            
            profile.is_active = False
            self.profile_manager._save_profile_to_db(profile)
            print(f"✅ Профиль #{number} деактивирован")
            
        except ValueError:
            print("❌ Введите корректный номер")
    
    def _activate_profile(self):
        """Активировать профиль"""
        try:
            number = int(input("Номер профиля для активации (1-30): "))
            profile = self.profile_manager.get_profile_by_number(number)
            
            if not profile:
                print("❌ Профиль не найден")
                return
            
            if profile.is_active:
                print("⚠️ Профиль уже активен")
                return
            
            profile.is_active = True
            self.profile_manager._save_profile_to_db(profile)
            print(f"✅ Профиль #{number} активирован")
            
        except ValueError:
            print("❌ Введите корректный номер")

# Интегрированная автоматизация с постоянными профилями
async def test_persistent_profiles():
    """Тест системы постоянных профилей"""
    print("🧪 Тестирование системы постоянных профилей...")
    
    try:
        # Создать автоматор с постоянными профилями
        automator = PersistentBrowserAutomator()
        
        if not await automator.initialize():
            print("❌ Не удалось инициализировать систему")
            return False
        
        # Получить первый профиль
        profile = automator.profile_manager.get_profile_by_number(1)
        if not profile:
            print("❌ Профиль #1 не найден")
            return False
        
        print(f"👤 Тестирование профиля: {profile.name}")
        print(f"   Email: {profile.email}")
        print(f"   Кошелек: {profile.wallet_type}")
        
        # Создать постоянный контекст браузера
        browser = await automator.create_persistent_browser_context(profile)
        
        # Создать страницу
        page = await browser.new_page()
        
        # Перейти на тестовую страницу
        await page.goto("https://example.com")
        print("✅ Страница загружена")
        
        # Сделать скриншот
        screenshot_path = Path("screenshots") / f"persistent_test_{profile.id}.png"
        screenshot_path.parent.mkdir(exist_ok=True)
        await page.screenshot(path=str(screenshot_path))
        print(f"📸 Скриншот: {screenshot_path}")
        
        # Обновить статистику использования
        automator.profile_manager.update_profile_usage(
            profile.id, "test", "page_visit", True, "Тестовое посещение example.com"
        )
        
        # Закрыть браузер
        await browser.close()
        
        await automator.cleanup()
        
        print("🎉 Тест постоянных профилей прошел успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

# Интеграция с Billions Network автоматизацией
class BillionsWithPersistentProfiles:
    """Billions Network автоматизация с постоянными профилями"""
    
    def __init__(self):
        self.site_url = "https://signup.billions.network/"
        self.automator = None
    
    async def initialize(self):
        """Инициализация с постоянными профилями"""
        self.automator = PersistentBrowserAutomator()
        return await self.automator.initialize()
    
    async def run_with_persistent_profiles(self, profile_numbers: List[int]):
        """Запуск с указанными номерами профилей"""
        print(f"🚀 Billions Network с постоянными профилями")
        print(f"👥 Профили: {profile_numbers}")
        print("=" * 50)
        
        if not await self.initialize():
            print("❌ Не удалось инициализировать систему")
            return False
        
        successful = 0
        failed = 0
        
        for profile_number in profile_numbers:
            print(f"\n👤 Профиль #{profile_number}")
            print("-" * 30)
            
            profile = self.automator.profile_manager.get_profile_by_number(profile_number)
            if not profile:
                print(f"❌ Профиль #{profile_number} не найден")
                failed += 1
                continue
            
            if not profile.is_active:
                print(f"⚠️ Профиль #{profile_number} неактивен, пропускаем")
                continue
            
            success = await self._process_profile(profile)
            
            if success:
                successful += 1
                print(f"✅ Профиль #{profile_number}: УСПЕХ")
            else:
                failed += 1
                print(f"❌ Профиль #{profile_number}: НЕУДАЧА")
            
            # Пауза между профилями
            if profile_number != profile_numbers[-1]:
                print("⏳ Пауза 3 секунды...")
                await asyncio.sleep(3)
        
        # Итоги
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"✅ Успешно: {successful}")
        print(f"❌ Неудачно: {failed}")
        print(f"📈 Успешность: {(successful/(successful+failed)*100):.1f}%" if (successful+failed) > 0 else "N/A")
        
        await self.automator.cleanup()
        return successful > 0
    
    async def _process_profile(self, profile: PersistentProfile):
        """Обработать один постоянный профиль"""
        try:
            print(f"🔧 {profile.name}")
            print(f"   Email: {profile.email}")
            print(f"   Кошелек: {profile.wallet_type}")
            
            # Создать постоянный браузерный контекст
            browser = await self.automator.create_persistent_browser_context(profile)
            page = await browser.new_page()
            
            try:
                # Перейти на Billions Network
                print(f"🌐 Переход на {self.site_url}")
                await page.goto(self.site_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)
                
                # Поиск и клик кнопки "Click & Earn 25 power"
                button_clicked = await self._click_earn_button(page)
                
                if button_clicked:
                    print("✅ Кнопка нажата!")
                    
                    # Обработка возможного кошелька
                    await asyncio.sleep(2)
                    wallet_handled = await self._handle_wallet(page, profile)
                    
                    # Сохранить скриншот результата
                    await self._save_screenshot(page, profile, "success")
                    
                    # Обновить статистику
                    self.automator.profile_manager.update_profile_usage(
                        profile.id, "billions_network", "earn_click", True, 
                        f"Успешный клик на {self.site_url}"
                    )
                    
                    return True
                else:
                    print("❌ Кнопка не найдена")
                    await self._save_screenshot(page, profile, "button_not_found")
                    
                    # Обновить статистику
                    self.automator.profile_manager.update_profile_usage(
                        profile.id, "billions_network", "earn_click", False, 
                        "Кнопка не найдена"
                    )
                    
                    return False
                
            finally:
                await browser.close()
                
        except Exception as e:
            print(f"❌ Ошибка профиля: {e}")
            
            # Обновить статистику
            self.automator.profile_manager.update_profile_usage(
                profile.id, "billions_network", "earn_click", False, 
                f"Ошибка: {str(e)}"
            )
            
            return False
    
    async def _click_earn_button(self, page):
        """Найти и кликнуть кнопку"""
        selectors = [
            'button.ant-btn.ant-btn-primary:has-text("Click & Earn")',
            'button:has-text("Click & Earn 25 power")',
            'button:has-text("Click & Earn")',
            'text=Click & Earn'
        ]
        
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element and await element.is_visible():
                    await element.scroll_into_view_if_needed()
                    await element.click()
                    return True
            except:
                continue
        
        return False
    
    async def _handle_wallet(self, page, profile):
        """Обработать взаимодействие с кошельком"""
        try:
            # Попробовать базовые действия кошелька в зависимости от типа
            from extension_handler import ExtensionActionHandler
            
            handler = ExtensionActionHandler(self.automator.coordinate_db)
            
            # Попробовать подключение кошелька
            if profile.wallet_type == "rabby":
                from extension_handler import WalletType
                success = await handler.perform_wallet_action(page, "connect", WalletType.RABBY)
                if success:
                    print(f"✅ Кошелек {profile.wallet_type} подключен")
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Ошибка кошелька: {e}")
            return False
    
    async def _save_screenshot(self, page, profile, status):
        """Сохранить скриншот"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"billions_{status}_{profile.id}_{timestamp}.png"
            filepath = Path("screenshots") / "billions_persistent" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            await page.screenshot(path=str(filepath))
            print(f"📸 {filename}")
            
        except Exception as e:
            print(f"⚠️ Скриншот не сохранен: {e}")

# CLI для Billions с постоянными профилями
class BillionsPersistentCLI:
    """CLI для Billions Network с постоянными профилями"""
    
    def __init__(self):
        self.billions = BillionsWithPersistentProfiles()
    
    async def run(self):
        """Запуск CLI"""
        print("🤖 Billions Network - Постоянные профили")
        print("=" * 50)
        
        while True:
            try:
                print("\nРежимы работы:")
                print("1. 🧪 Тест с профилем #1")
                print("2. 🎯 Выбрать профили вручную")
                print("3. 📊 Первые 5 профилей")
                print("4. 💪 Первые 10 профилей")
                print("5. 🔥 Все активные профили")
                print("6. 👥 Управление профилями")
                print("0. 🚪 Выход")
                
                choice = input("\nВыбор (0-6): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    await self.billions.run_with_persistent_profiles([1])
                elif choice == "2":
                    await self._manual_profile_selection()
                elif choice == "3":
                    await self.billions.run_with_persistent_profiles(list(range(1, 6)))
                elif choice == "4":
                    await self.billions.run_with_persistent_profiles(list(range(1, 11)))
                elif choice == "5":
                    await self._run_all_active()
                elif choice == "6":
                    profile_cli = ProfileManagerCLI()
                    profile_cli.run()
                else:
                    print("❌ Неверный выбор")
                    
            except KeyboardInterrupt:
                print("\n⏹️ Остановка...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        print("👋 Billions automation завершена!")
    
    async def _manual_profile_selection(self):
        """Ручной выбор профилей"""
        try:
            print("Введите номера профилей через запятую (например: 1,3,5-8)")
            selection = input("Профили: ").strip()
            
            profile_numbers = []
            
            for part in selection.split(','):
                part = part.strip()
                if '-' in part:
                    # Диапазон (например 5-8)
                    start, end = map(int, part.split('-'))
                    profile_numbers.extend(range(start, end + 1))
                else:
                    # Отдельный номер
                    profile_numbers.append(int(part))
            
            # Убрать дубликаты и отсортировать
            profile_numbers = sorted(list(set(profile_numbers)))
            
            # Проверить диапазон
            valid_numbers = [n for n in profile_numbers if 1 <= n <= 30]
            
            if not valid_numbers:
                print("❌ Нет корректных номеров профилей")
                return
            
            print(f"Выбранные профили: {valid_numbers}")
            confirm = input("Продолжить? (y/N): ").lower()
            
            if confirm == 'y':
                await self.billions.run_with_persistent_profiles(valid_numbers)
            
        except ValueError:
            print("❌ Неверный формат ввода")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    async def _run_all_active(self):
        """Запуск всех активных профилей"""
        try:
            # Получить менеджер профилей
            if not hasattr(self.billions, 'automator') or not self.billions.automator:
                temp_automator = PersistentBrowserAutomator()
                await temp_automator.initialize()
                profile_manager = temp_automator.profile_manager
                await temp_automator.cleanup()
            else:
                profile_manager = self.billions.automator.profile_manager
            
            active_profiles = profile_manager.get_available_profiles()
            active_numbers = [p.number for p in active_profiles]
            
            if not active_numbers:
                print("❌ Нет активных профилей")
                return
            
            print(f"Найдено {len(active_numbers)} активных профилей: {active_numbers}")
            print("⚠️ ВНИМАНИЕ: Запуск всех профилей может занять много времени!")
            confirm = input("Продолжить? (y/N): ").lower()
            
            if confirm == 'y':
                await self.billions.run_with_persistent_profiles(active_numbers)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

# Главные функции
async def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            await test_persistent_profiles()
        elif command == "profiles":
            profile_cli = ProfileManagerCLI()
            profile_cli.run()
        elif command == "billions":
            billions_cli = BillionsPersistentCLI()
            await billions_cli.run()
        else:
            print("Команды:")
            print("  test     - тест системы постоянных профилей")
            print("  profiles - управление профилями")
            print("  billions - Billions Network с постоянными профилями")
    else:
        # По умолчанию меню
        billions_cli = BillionsPersistentCLI()
        await billions_cli.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()