FROM python:3.12-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml ./
COPY services ./services
COPY tests ./tests
COPY tools ./tools

RUN python -m pip install --upgrade pip \
  && python -m pip install --no-cache-dir -e ".[dev]"

CMD ["uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

