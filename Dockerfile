FROM python:3.11-slim

Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

Install system dependencies (GTK+ libraries) required by WeasyPrint
This command is split using the '' continuation character for readability.
RUN apt-get update && 

apt-get install -y --no-install-recommends 

libpango-1.0-0 

libharfbuzz0b 

libpangoft2-1.0-0 

libgdk-pixbuf-2.0-0 

libffi-dev 

libcairo-dev 

libgirepository1.0-dev 

&& rm -rf /var/lib/apt/lists/*

Set the working directory
WORKDIR /app

Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

Copy the core application file
COPY main.py .

Define the command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
