# Use Python 3.12 as base image (slim version for smaller size)
FROM python:3.12-slim

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for extremely fast package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml ./

# Install Python dependencies using uv directly into system Python
RUN uv pip install --no-cache -r pyproject.toml

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (Dash default is 8050)
EXPOSE 8050

# Run the application using gunicorn in production
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8050"]
