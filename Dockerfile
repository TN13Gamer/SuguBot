# 1. Use a Python image that includes system tools
FROM python:3.10-slim

# 2. Install FFmpeg and git (System Level)
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# 3. Set up the working folder
WORKDIR /app

# 4. Copy your files into the container
COPY . /app

# 5. Install Python Libraries
RUN pip install --no-cache-dir -r requirements.txt

# 6. Command to start the bot

CMD ["python", "main.py"]
