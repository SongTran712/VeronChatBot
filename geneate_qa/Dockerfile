# Use the official Python 3.10 slim image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libmagic-dev \
    libxml2-dev \
    libjpeg-dev \
    zlib1g-dev \
    ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port (optional, only needed if you're running a web app)
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]
