FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (GTK+ libraries) required by WeasyPrint
# Note: The backslashes ensure this is all treated as one RUN instruction
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libharfbuzz0b \
        libpangoft2-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        libcairo-dev \
        libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files, including the crucial template file
COPY main.py .
COPY invoice_template.html .

# Start the uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
