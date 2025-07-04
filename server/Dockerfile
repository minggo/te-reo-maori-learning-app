# server/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY setup.py requirements.txt dev-requirements.txt  ./
RUN pip install --no-cache-dir .

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
