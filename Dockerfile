# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install the package
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python", "-m", "spotify_mcp.server"]
