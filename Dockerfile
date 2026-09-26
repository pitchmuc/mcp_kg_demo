FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python build tool
RUN pip install --no-cache-dir hatchling

# Copy project files
COPY pyproject.toml pyproject.toml
COPY src src
COPY data data
COPY README.md README.md
COPY .env.example .env.example

# Install the package and runtime dependencies
RUN pip install --no-cache-dir .

# Default command to run the MCP server using stdio transport
CMD ["python", "src/kg_mcp_server/server.py"]
