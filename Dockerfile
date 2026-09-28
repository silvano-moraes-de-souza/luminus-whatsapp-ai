FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema para psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Garante que /app esteja no PYTHONPATH para resolução de pacotes
ENV PYTHONPATH=/app

CMD ["python", "luminus/api/server.py"]
