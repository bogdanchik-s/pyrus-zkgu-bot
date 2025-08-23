FROM python:3.12-slim

WORKDIR /pyrus-zkgu-bot

RUN python -m venv venv
ENV PATH=/venv/bin:$PATH

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
