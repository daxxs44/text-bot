# Optional Dockerfile for Railway or other Docker-based hosting
# Railway uses Nixpacks by default, but this provides an alternative

FROM python:3.11-slim

# Install FFmpeg and other dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bot.py .
COPY audio_processor.py .
COPY voice_cloner.py .

# Create necessary directories
RUN mkdir -p recordings saved_voices temp

# Run the bot
CMD ["python", "-u", "bot.py"]
