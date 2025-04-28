import os
import sys
import ctypes
import subprocess

def unblock_sites():
    """Разблокирует ранее заблокированные антивирусные сайты, восстанавливая файл hosts"""
    try:
        # Находим путь к файлу hosts
        hosts_file = os.path.join(os.environ['SystemRoot'], 'System32', 'drivers', 'etc', 'hosts')
        
        # Проверяем, можем ли мы писать в файл hosts
        try:
            with open(hosts_file, 'a') as f:
                pass
        except:
            # Нужны права администратора
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Требуются права администратора для изменения файла hosts")
                print("Пожалуйста, запустите эту программу от имени администратора")
                return False
        
        # Делаем файл доступным для записи, если он был помечен только для чтения
        try:
            subprocess.run(f'attrib -r "{hosts_file}"', shell=True, check=True)
        except:
            pass
        
        # Читаем текущее содержимое
        with open(hosts_file, 'r') as f:
            content = f.readlines()
        
        # Список заблокированных сайтов (должен совпадать со списком в block_sites)
        banned_sites = [
            'virustotal.com', 'avast.com', 'kaspersky.com', 'mcafee.com',
            'norton.com', 'malwarebytes.com', 'bitdefender.com', 'eset.com',
            'avg.com', 'comodo.com', 'drweb.com', 'cybereason.com', 'crowdstrike.com',
            'f-secure.com', 'sophos.com', 'avira.com', 'virusradar.com',
            'hybrid-analysis.com', 'any.run', 'virusscan.jotti.org'
        ]
        
        # Формируем список строк, которые нужно удалить из файла hosts
        to_remove = []
        for site in banned_sites:
            to_remove.append(f"127.0.0.1 {site}\n")
            to_remove.append(f"127.0.0.1 www.{site}\n")
        
        # Фильтруем строки, удаляя блокировки
        new_content = []
        for line in content:
            if line not in to_remove:
                new_content.append(line)
        
        # Записываем обновленный файл
        with open(hosts_file, 'w') as f:
            f.writelines(new_content)
        
        print(f"Файл hosts успешно обновлен. Блокировка антивирусных сайтов снята.")
        return True
    
    except Exception as e:
        print(f"Ошибка при разблокировке сайтов: {e}")
        return False

def main():
    """Основная функция для выполнения при запуске скрипта"""
    print("Запуск процесса разблокировки антивирусных сайтов...")
    
    if unblock_sites():
        print("Сайты успешно разблокированы!")
    else:
        print("Не удалось разблокировать сайты. Пожалуйста, запустите программу от имени администратора.")
    
    # Ждем нажатия кнопки, чтобы окно не закрылось сразу
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 