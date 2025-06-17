# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# - build-essential for packages that might need compilation
# - Matplotlib dependencies (libfreetype6-dev, libpng-dev, pkg-config)
# Using --no-install-recommends to keep the image slim.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    # Clean up apt lists to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce layer size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
# This includes bot/, database/, utils/ directories.
# If finance_data.db exists in the build context, it will be copied too.
# For persistent data, a volume should be mounted at runtime for finance_data.db.
COPY . .

# Expose TELEGRAM_TOKEN as an environment variable to be set during container run
# The actual value will be provided when running 'docker run -e TELEGRAM_TOKEN=...'
ENV TELEGRAM_TOKEN=""

# Command to run the application
# Using python -u for unbuffered stdout/stderr, useful for Docker logs.
# Using -m bot.main to run the bot as a module, assuming /app is the project root.
CMD ["python", "-u", "-m", "bot.main"]
