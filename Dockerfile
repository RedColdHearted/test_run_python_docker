# Использование базового образа с Python 3.12.4
FROM python:3.12.4-slim

# Копирование и запуск скрипта, который блокирует доступ к модулям
COPY restrict_modules.py /usr/local/lib/python3.12/restrict_modules.py
COPY restrict_modules_init.py /usr/local/lib/python3.12/site-packages/sitecustomize.py


RUN groupadd -r sandboxuser && useradd -r -g sandboxuser sandboxuser
USER sandboxuser


# Установление рабочей директории в контейнере
WORKDIR /tests_to_exec

# Копирование только директории tests_to_exec в контейнер
COPY tests_to_exec /tests_to_exec

# Keep the container alive
CMD ["tail", "-f", "/dev/null"]
