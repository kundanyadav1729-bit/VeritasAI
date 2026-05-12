# 1. Use a lightweight official Python cloud image
FROM python:3.11-slim

# 2. Install the Tesseract OCR engine directly into the cloud Linux OS
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

# 3. Set up our working directory
WORKDIR /app

# 4. Copy our library list and install the Python tools
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all our actual backend code into the container
COPY backend/ .

# 6. Start the AI Server!
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]