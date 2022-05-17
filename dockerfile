FROM python:3.10-slim-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip --no-cache-dir install --ignore-installed distlib -r requirements.txt
RUN pip install gunicorn
COPY . .

EXPOSE 8080

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "app:create_app()"]