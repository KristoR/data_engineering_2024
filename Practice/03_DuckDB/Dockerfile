FROM python:3.12.7-slim-bookworm

# Set a working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ca-certificates \
    unzip \ 
    && rm -rf /var/lib/apt/lists/*

# Check the architecture and download the corresponding DuckDB CLI
RUN arch=$(dpkg --print-architecture) && \
    if [ "$arch" = "amd64" ]; then \
        curl -L https://github.com/duckdb/duckdb/releases/download/v1.1.1/duckdb_cli-linux-amd64.zip -o duckdb.zip; \
    elif [ "$arch" = "arm64" ]; then \
        curl -L https://github.com/duckdb/duckdb/releases/download/v1.1.1/duckdb_cli-linux-aarch64.zip -o duckdb.zip; \
    else \
        echo "Unsupported architecture: $arch"; exit 1; \
    fi && \
    unzip duckdb.zip && \
    mv duckdb /usr/local/bin/ && \
    chmod +x /usr/local/bin/duckdb && \
    rm duckdb.zip

# Install DuckDB via pip for Python use
RUN pip install --no-cache-dir duckdb

# Set the default command to launch DuckDB CLI
CMD ["duckdb"]