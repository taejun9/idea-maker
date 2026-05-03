FROM node:22-slim AS node_runtime

RUN npm install -g @google/gemini-cli@0.40.0

FROM python:3.12-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node_runtime /usr/local/lib/node_modules /usr/local/lib/node_modules

COPY pyproject.toml ./
COPY services ./services
COPY tests ./tests
COPY tools ./tools

RUN ln -s /usr/local/lib/node_modules/@google/gemini-cli/bundle/gemini.js /usr/local/bin/gemini \
  && python -m pip install --upgrade pip \
  && python -m pip install --no-cache-dir -e ".[dev]"

CMD ["uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
