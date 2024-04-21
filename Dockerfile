FROM python:3.12.1-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=flask_app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]