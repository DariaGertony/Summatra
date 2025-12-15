FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webworker.py .

EXPOSE 8501

CMD ["streamlit", "run", "webworker.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \         
     "--server.headless=true", \
     "--server.enableXsrfProtection=false", \
     "--logger.level=debug"]