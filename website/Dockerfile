FROM python:3.12
RUN apt-get update && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ../requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./website /app
COPY ../docker_settings/Backend/app.sh /app/config/app.sh
COPY ../docker_settings/Backend/gunicorn.conf.py /app/config/gunicorn.conf.py
RUN chmod +x ./config/app.sh
ENTRYPOINT ["/app/config/app.sh"]
