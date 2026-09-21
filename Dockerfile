FROM python:3.14-slim

# Copy the uv binary from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install dependencies first (cached unless pyproject/uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy the rest of the app (main.py, db.py, pages/, etc.)
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV DATABASE_PATH=/data/database.db

RUN mkdir -p /data
VOLUME /data

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501"]