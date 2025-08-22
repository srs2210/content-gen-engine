# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your application code into the container
COPY . .

# 6. Expose the port the app runs on
EXPOSE 8080

# 7. Run uvicorn server. Cloud Run sets the PORT env var.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
