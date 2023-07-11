FROM python:3.10-bullseye

# install git as pip needs to clone fsd_utils
RUN apt update && apt -yq install git
# install manually to workaround issue in psycopg2-binary 2.9.5
RUN pip3 install psycopg2-binary --no-binary psycopg2-binary

WORKDIR /app
COPY requirements-dev.txt requirements-dev.txt
RUN python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt
COPY . .

EXPOSE 8080
ENV FLASK_ENV=development

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
