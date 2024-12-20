# gunicorn.conf.py

# Количество рабочих процессов, которые Gunicorn будет использовать для обработки запросов.
# Рекомендуется использовать (2 * количество_ядер) + 1 для оптимальной производительности.
workers = 2

# Количество потоков на каждый рабочий процесс.
# Это может помочь в обработке I/O операций и увеличении пропускной способности.
threads = 2

# Класс рабочих процессов, определяющий, как будут обрабатываться запросы.
# 'sync' - стандартный класс, 'gevent' и 'eventlet' - для асинхронной обработки.
worker_class = "sync"

# Максимальное количество соединений, которые может обрабатывать каждый рабочий процесс.
# Используется только для асинхронных рабочих классов, таких как 'gevent'.
worker_connections = 1000

# Тайм-аут в секундах для обработки каждого запроса.
# Если запрос занимает больше времени, чем указано, процесс будет перезапущен.
timeout = 30

# Время ожидания в секундах для соединений keep-alive.
# Это время, в течение которого соединение остается открытым после завершения запроса.
keepalive = 2

# Привязка к адресу и порту, на которых Gunicorn будет слушать входящие запросы.
# Обычно используется 0.0.0.0 для прослушивания всех интерфейсов или localhost для локальной разработки.
bind = "0.0.0.0:8000"

# Размер очереди соединений.
# Это максимальное количество соединений, которые могут быть в очереди перед обработкой.
backlog = 2048

# Уровень логирования, определяющий, насколько подробными будут логи.
# 'debug' - самый подробный, 'info' - стандартный для продакшена, 'warning', 'error', 'critical' - для более серьезных сообщений.
loglevel = "info"

# Путь для логов доступа. '-' означает вывод в стандартный вывод (stdout).
accesslog = "-"

# Путь для логов ошибок. '-' означает вывод в стандартный вывод (stderr).
errorlog = "-"

# Захват вывода stdout/stderr в лог. Полезно для отладки.
capture_output = False

# Пользователь, от которого будет запущен процесс Gunicorn.
# Используется для повышения безопасности, чтобы приложение не работало от root.
user = None

# Группа, от которой будет запущен процесс Gunicorn.
# Аналогично user, помогает в управлении правами доступа.
group = None

# Маска создания файлов, определяющая права доступа к создаваемым файлам.
# Полезно для управления безопасностью файлов.
umask = 0

# Если True, приложение будет загружено перед форком рабочих процессов.
# Это может уменьшить время старта, но требует больше памяти.
preload_app = False

# Если True, Gunicorn будет работать в фоновом режиме как демон.
# Обычно не используется в Docker, так как Docker сам управляет процессами.
daemon = False

# Путь к файлу, в который будет записан PID процесса Gunicorn.
# Полезно для управления процессами и мониторинга.
pidfile = None

# Путь к SSL сертификату для настройки HTTPS.
certfile = None

# Путь к SSL ключу для настройки HTTPS.
keyfile = None

# Путь к файлам CA сертификатов для проверки цепочки доверия.
ca_certs = None

# Изменение рабочей директории перед запуском приложения.
# Полезно, если приложение должно работать из определенной директории.
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
chdir = os.path.abspath(os.path.join(current_dir, "..", "..", "app"))

# Список переменных окружения, которые будут установлены перед запуском приложения.
# Полезно для настройки окружения приложения.
raw_env = []

# Путь к дополнительным модулям Python, которые должны быть доступны приложению.
# Полезно, если приложение требует специфичных библиотек.
pythonpath = None

# Максимальная длина строки запроса.
# Это ограничение помогает защититься от атак переполнения буфера.
limit_request_line = 4094

# Максимальное количество заголовков запроса.
# Это ограничение помогает защититься от атак переполнения буфера.
limit_request_fields = 100

# Максимальный размер заголовка запроса.
# Это ограничение помогает защититься от атак переполнения буфера.
limit_request_field_size = 8190

# Разрешение повторного использования порта.
# Полезно для повышения производительности при частых перезапусках.
reuse_port = False

# Разрешенные IP для заголовка X-Forwarded-For.
# Полезно для работы за прокси-сервером, таким как Nginx.
forwarded_allow_ips = "127.0.0.1"

# Формат логов доступа.
# Позволяет настроить, какие данные будут включены в логи доступа.
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Тайм-аут для завершения рабочих процессов.
# Если рабочий процесс не завершится в течение этого времени, он будет принудительно завершен.
graceful_timeout = 30

# # Отладка
# reload = True
# reload_extra_files = ['']
