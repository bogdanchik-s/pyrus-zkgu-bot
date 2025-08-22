FROM python:3.12-slim

WORKDIR /pyrus-zkgu-bot

RUN python -m venv venv
ENV PATH=/venv/bin:$PATH

COPY common .
COPY services .
COPY app.py .
COPY config.py .
COPY .env .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
