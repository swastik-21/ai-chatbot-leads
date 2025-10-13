#!/bin/bash

# Railway start script
echo "Starting AI Chatbot..."

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Seed FAQs
echo "Seeding FAQs..."
python manage.py seed_faqs

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn ai_chatbot_leads.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --workers 1 \
    --access-logfile - \
    --error-logfile -
