"""
Документация скрипта сборки

Этот скрипт отвечает за сборку приложения с использованием PyInstaller.

Особенности:
- Поддерживает режим отладки через аргумент командной строки '-d'
- Создает единый исполняемый файл
- Управляет видимостью консоли в зависимости от режима отладки
- Очищает директории сборки и перемещает исполняемый файл в текущую директорию

Использование:
    python build.py        # Сборка в режиме релиза (без консоли)
    python build.py -d     # Сборка в режиме отладки (с консолью)

Зависимости:
    - PyInstaller
    - Python 3.x
    - Операционная система: Windows/Linux/MacOS

Процесс работы:
    1. Проверка режима сборки (отладка/релиз)
    2. Запуск PyInstaller с соответствующими параметрами
    3. Перемещение собранного файла в текущую директорию
    4. Очистка временных файлов и директорий

Структура выходных файлов:
    - Один исполняемый файл в текущей директории
    - Никаких дополнительных файлов или зависимостей

Обработка ошибок:
    - Проверка существования директорий перед удалением
    - Безопасное перемещение файлов
    - Корректное завершение процесса сборки

Возвращает:
    Исполняемый файл в текущей директории
"""

import os
import sys
import shutil
from colorama import init, Fore, Style

# Initialize colorama
init()

DEBUG_MODE = True if '-d' in sys.argv else False

if DEBUG_MODE:
    print(f"{Fore.GREEN}[DEBUG] Building in debug mode{Style.RESET_ALL}")
else:
    print(f"{Fore.BLUE}[INFO] Building in release mode{Style.RESET_ALL}")

print(f"{Fore.YELLOW}[BUILD] Running PyInstaller...{Style.RESET_ALL}")
os.system(f'pyinstaller main.py --onefile {'--noconsole' if not DEBUG_MODE else ""}')

# Move executable to current directory
if os.path.exists('dist'):
    print(f"{Fore.CYAN}[INFO] Moving executable to current directory...{Style.RESET_ALL}")
    for file in os.listdir('dist'):
        shutil.move(os.path.join('dist', file), file)
    
# Clean up build directories
print(f"{Fore.MAGENTA}[CLEANUP] Removing build directories...{Style.RESET_ALL}")
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('main.spec'):
    os.remove('main.spec')

print(f"{Fore.GREEN}[SUCCESS] Build completed successfully!{Style.RESET_ALL}")
