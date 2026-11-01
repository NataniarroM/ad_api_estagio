FROM python:3.12-slim

WORKDIR /app

# Este é o próprio requirements cedido pelo professor ao longo de suas aulas 
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]