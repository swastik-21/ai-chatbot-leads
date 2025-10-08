# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ai_chatbot_leads.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories for FAISS index and static files
RUN mkdir -p /app/faiss_index /app/static

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
python manage.py migrate\n\
python manage.py seed_faqs\n\
gunicorn ai_chatbot_leads.wsgi:application --bind 0.0.0.0:8000' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
