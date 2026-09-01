FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY nse_to_bigquery.py .

CMD ["python", "nse_to_bigquery.py"]