FROM python:3.10-slim-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .

EXPOSE 8080
ENV FLASK_ENV=development

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]