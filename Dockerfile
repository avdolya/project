FROM python:3.12-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создаем необходимые файлы
RUN mkdir -p /app/my_package/core/certs

# Настраиваем Poetry
RUN pip install --no-cache-dir poetry
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./
RUN touch README.md  # Фикс для отсутствующего README

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем проект
COPY . .

# Команда запуска
CMD ["uvicorn", "my_package.main:app", "--host", "0.0.0.0", "--port", "8000"]



