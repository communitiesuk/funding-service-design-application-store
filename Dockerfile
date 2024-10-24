FROM python:3.10-bullseye

# install git as pip needs to clone fsd_utils
RUN apt update && apt -yq install git

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml .
RUN uv sync
COPY . .

ENV FLASK_ENV=development
EXPOSE 8080

CMD ["uv", "run", "gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "wsgi:app", "-b", "0.0.0.0:8080"]
