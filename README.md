# Universal Browser Automation System - Fixed Version

🤖 Система автоматизации браузера для Web3 и DeFi задач.

## ✨ Возможности

- **30 уникальных профилей браузера**
- **Поддержка кошельков Rabby и Phantom**
- **Координатная система действий**
- **AI fallback (опционально)**
- **Простой и надежный**

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Тест системы
```bash
python simple_launcher.py test
```

### 3. Интерактивный режим
```bash
python simple_launcher.py interactive
```

## 📁 Структура

```
core/                           # Основные модули
├── browser_automation_core.py  # Браузерный автоматор
├── extension_handler.py        # Обработчик кошельков
├── simple_main.py              # Упрощенная система
└── __init__.py                 # Пакет

projects/                       # Проекты
data/                          # Базы данных  
logs/                          # Логи
screenshots/                   # Скриншоты
browser_profiles/              # Профили (30 штук)
```

## ⚙️ Конфигурация

### Настройка API ключей (.env):
```
OPENAI_API_KEY=your_key_here
```

### Настройка системы (config.json):
```json
{
  "browser": {
    "headless": false,
    "viewport": {"width": 1440, "height": 900}
  }
}
```

## 🧪 Тестирование

```bash
# Простой тест
python simple_launcher.py test

# Интерактивный режим
python simple_launcher.py interactive
```

## 🔧 Возможности

### Автоматизация кошельков:
- Подключение кошельков (Rabby, Phantom)
- Подтверждение транзакций
- Координатные клики с fallback

### Управление профилями:
- 30 изолированных профилей браузера
- Уникальные User-Agent, viewport, локали
- Автоматическая ротация

### Простота использования:
- Интерактивный CLI интерфейс
- Автоматическое тестирование
- Подробное логирование

## 🆘 Решение проблем

### Playwright не установлен:
```bash
pip install playwright
playwright install chromium
```

### Модули не найдены:
```bash
# Проверьте структуру файлов
python simple_launcher.py test
```

### Кошелек не работает:
- Установите расширения браузера
- Проверьте координаты в базе данных
- Используйте интерактивный режим для отладки

## ⚠️ Важно

- Система работает без AI ключей (только координаты)
- С AI ключами добавляется fallback функциональность
- Все данные хранятся локально
- Безопасно для тестирования

---

Создано для автоматизации Web3 и DeFi задач 🚀
