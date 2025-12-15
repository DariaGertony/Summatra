FROM python:3.11-slim

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dbworker.py .

CMD ["python", "-u", "dbworker.py"]