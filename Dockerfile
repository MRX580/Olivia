# Ваш текущий Dockerfile
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем необходимые пакеты для сборки зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libsqlite3-dev \
    build-essential \
    default-mysql-client

# Устанавливаем переменную окружения PYTHONPATH
ENV PYTHONPATH=/app

# Создаем необходимые директории
RUN mkdir -p /app/telegram_bot/utils /app/telegram_bot/logs /app/telegram_bot/static/img/decks_1

# Копируем файл requirements.txt в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы в рабочую директорию
COPY . .

# Указываем команду для запуска бота
CMD ["python", "telegram_bot/start.py"]
