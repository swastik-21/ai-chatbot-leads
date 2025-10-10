# AI Chatbot for Lead Generation

Simple Django chatbot that talks to potential clients and captures their info. Uses OpenAI API and FAISS for smart responses.

## What it does

- Chat with visitors about AI development services
- Automatically detect when someone's interested (name + email)
- Store qualified leads in database
- Simple web interface
- REST API for everything

## Tech stack

- Django + DRF
- OpenAI GPT-3.5-turbo
- FAISS for document search
- SQLite database
- Docker for deployment

## Setup

1. Clone and install:
   ```bash
   git clone <repo>
   cd ai_chatbot_leads
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. Run the app:
   ```bash
   python manage.py migrate
   python manage.py seed_faqs
   python manage.py runserver
   ```

Visit http://localhost:8000

## Docker

```bash
docker build -t chatbot .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key chatbot
```

## API

- `POST /api/chat/` - Send message, get response
- `GET /api/leads/` - View qualified leads
- `GET /api/session/{id}/history/` - Chat history

Example:
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, I need a chatbot"}'
```

## Notes

- Uses GPT-3.5-turbo (cheap)
- Stores leads when someone gives name + email
- FAQ data gets loaded automatically
- Works with Docker

That's it.