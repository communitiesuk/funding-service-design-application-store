FROM python:3.10-bullseye

# install git as pip needs to clone fsd_utils
RUN apt update && apt -yq install git

WORKDIR /app
COPY requirements-dev.txt requirements-dev.txt
RUN python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt
COPY . .

EXPOSE 8080
ENV FLASK_ENV=development

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
