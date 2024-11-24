FROM python:3.12
RUN apt-get update && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ../requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app
COPY ../docker_settings/Backend/app.sh /sh_files/app.sh
RUN chmod +x /sh_files/app.sh
ENTRYPOINT ["/sh_files/app.sh"]
