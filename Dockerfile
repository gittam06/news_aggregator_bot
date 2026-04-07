# 1. Use an official, lightweight Python image as the foundation
FROM python:3.11-slim

# 2. Create a working directory inside the cloud server
WORKDIR /app

# 3. Copy your requirements file and install the dependencies (Pandas, feedparser, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all the rest of your code into the cloud server
COPY . .

# 5. The command that wakes the bot up and keeps it running
CMD ["python", "run_bot.py"]