FROM python:3.11-alpine

WORKDIR /app

# Устанавливаем системные зависимости
RUN apk add --no-cache \
    tzdata \
    curl \
    && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем скрипт
COPY sendler.py .

# Создаем пользователя для безопасности
RUN adduser -D -u 1001 pythonuser \
    && chown -R pythonuser:pythonuser /app
USER pythonuser

# Запускаем скрипт каждые 4 часа (14400 секунд)
CMD ["sh", "-c", "while true; do python sendler.py; echo 'Sleeping for 4 hours...'; sleep 14400; done"]

# HEALTHCHECK (опционально)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; response = requests.get('https://api.openweathermap.org/data/2.5/weather?q=London&appid=dummy'); print('Health check: API connection test')" || exit 1