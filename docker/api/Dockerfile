FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip -r /app/requirements.txt

ENV PYTHONUNBUFFERED 1

EXPOSE 8000