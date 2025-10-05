Use a slim Python 3.11 base image
FROM python:3.11-slim

Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

Install system dependencies (GTK+ libraries) required by WeasyPrint
This step is essential for PDF rendering.
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
0.0.0.0 is required to listen publicly inside the container.
10000 is the default port expected by Render's free tier.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]