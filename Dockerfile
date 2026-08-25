FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copia a configuração do Nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
