# Use Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

# Install uv for faster dependency installation
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install dependencies using uv
RUN uv pip install --system -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the server via smithery CLI
CMD ["smithery", "dev"]
