# # Use official Python image as base
# FROM python:3.12-slim

# # Install system dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         poppler-utils \
#         tesseract-ocr \
#         gcc \
#         libgl1 \
#         libglib2.0-0 \
#         unixodbc \
#         unixodbc-dev \
#         && rm -rf /var/lib/apt/lists/*


# # RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
# #     curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
# #     apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# RUN apt install -y freetds-dev freetds-bin unixodbc unixodbc-dev tdsodbc

# # Set work directory
# WORKDIR /app

# # Copy requirements and install Python dependencies
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . /app

# # Expose FastAPI port
# EXPOSE 8000

# # Set environment variables (override in production as needed)
# ENV PYTHONUNBUFFERED=1

# # Start FastAPI app with uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]






FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system and ODBC/FreeTDS dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gnupg \
        curl \
        unixodbc \
        unixodbc-dev \
        odbcinst \
        build-essential \
        freetds-dev \
        freetds-bin \
        tdsodbc \
        poppler-utils \
        tesseract-ocr \
        gcc \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
