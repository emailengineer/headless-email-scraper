# docker/Dockerfile
FROM python:3.12-slim

# Install dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl wget gnupg unzip libnss3 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libxrender1 libxss1 libxtst6 libgtk-3-0 libcups2 libdrm2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install

COPY app/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
