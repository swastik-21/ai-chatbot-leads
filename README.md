# AI Chatbot Leads

A complete Django project that implements an AI chatbot with lead qualification using LangChain and OpenAI API. This system provides intelligent conversation capabilities with automatic lead detection and qualification.

## Features

- **AI-Powered Chat**: Uses OpenAI GPT-3.5-turbo for intelligent responses
- **RAG (Retrieval Augmented Generation)**: FAISS vector store for context-aware responses
- **Lead Qualification**: Automatic detection and extraction of lead information
- **Session Management**: Persistent chat sessions with history
- **REST API**: Full API endpoints for chat, session history, and leads
- **Modern Frontend**: Clean, responsive web interface
- **Rate Limiting**: Cached responses to prevent API abuse
- **Docker Support**: Easy deployment with Docker

## Project Structure

```
ai_chatbot_leads/
├── README.md
├── Dockerfile
├── requirements.txt
├── manage.py
├── ai_chatbot_leads/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── chat/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   ├── retriever.py
│   │   └── lead_qualifier.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_faqs.py
│   └── tests/
│       ├── test_chat_flow.py
│       └── test_lead_qualifier.py
├── frontend/
│   ├── index.html
│   └── app.js
└── env.example
```

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- pip (Python package manager)

### Local Development Setup

1. **Clone and navigate to the project:**
   ```bash
   cd ai_chatbot_leads
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Seed FAQ data:**
   ```bash
   python manage.py seed_faqs
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Open your browser:**
   Navigate to `http://localhost:8000`

### Docker Setup

1. **Build the Docker image:**
   ```bash
   docker build -t ai-chatbot-leads .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY=your-api-key-here ai-chatbot-leads
   ```

3. **Access the application:**
   Navigate to `http://localhost:8000`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `DJANGO_SECRET_KEY` | Django secret key | `django-insecure-change-this-in-production` |
| `DEBUG` | Django debug mode | `True` |
| `DATABASE_URL` | Database connection string | SQLite |
| `FAISS_PATH` | Path to FAISS index | `./faiss_index` |

## API Endpoints

### Chat Endpoint
- **POST** `/api/chat/`
- **Body:** `{"session_id": "uuid", "message": "user message"}`
- **Response:** `{"reply": "AI response", "session_id": "uuid", "lead_qualified": bool}`

### Session History
- **GET** `/api/session/{session_id}/history/`
- **Response:** Session with message history

### Leads List
- **GET** `/api/leads/`
- **Response:** List of qualified leads

## Example API Usage

### Start a chat session:
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I am interested in your premium package"}'
```

### Continue a session:
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-uuid", "message": "What are your pricing options?"}'
```

### Get session history:
```bash
curl http://localhost:8000/api/session/your-session-uuid/history/
```

### List qualified leads:
```bash
curl http://localhost:8000/api/leads/
```

## Lead Qualification

The system automatically analyzes each user message to detect potential leads. A message qualifies as a lead if it contains:

- **Contact Information**: Name and/or email address
- **Interest Indicators**: Expressions of interest in products/services
- **High Interest Score**: Above 0.3 threshold

Example qualifying messages:
- "Hi, I'm John Doe (john@example.com) and I'm very interested in your premium package!"
- "My name is Jane Smith, email jane@company.com. I'd like to learn more about your enterprise solutions."

## Testing

Run the test suite:

```bash
python manage.py test
```

Run specific test files:
```bash
python manage.py test chat.tests.test_chat_flow
python manage.py test chat.tests.test_lead_qualifier
```

## Management Commands

### Seed FAQ Data
```bash
python manage.py seed_faqs
```

### Clear and reseed FAQ data:
```bash
python manage.py seed_faqs --clear
```

## Production Deployment

### Using Docker (Recommended)

1. **Build production image:**
   ```bash
   docker build -t ai-chatbot-leads:prod .
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e OPENAI_API_KEY=your-api-key \
     -e DJANGO_SECRET_KEY=your-secret-key \
     -e DEBUG=False \
     -e DATABASE_URL=postgresql://user:pass@host:port/db \
     ai-chatbot-leads:prod
   ```

### Manual Deployment

1. **Set production environment variables:**
   ```bash
   export OPENAI_API_KEY=your-api-key
   export DJANGO_SECRET_KEY=your-secret-key
   export DEBUG=False
   export DATABASE_URL=postgresql://user:pass@host:port/db
   ```

2. **Install production dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

5. **Seed FAQ data:**
   ```bash
   python manage.py seed_faqs
   ```

6. **Start with Gunicorn:**
   ```bash
   gunicorn ai_chatbot_leads.wsgi:application --bind 0.0.0.0:8000
   ```

## Architecture

### Services

- **LLMClient**: Handles OpenAI API calls with retry logic and caching
- **FAISSRetriever**: Manages vector store for RAG functionality
- **LeadQualifier**: Analyzes messages for lead qualification

### Models

- **Session**: Chat session management
- **Message**: Individual chat messages
- **Lead**: Qualified lead information

### Key Features

- **Rate Limiting**: 10-second cache for identical requests
- **Error Handling**: Graceful fallbacks for API failures
- **Modular Design**: Clean separation of concerns
- **Test Coverage**: Comprehensive unit tests

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error:**
   - Ensure `OPENAI_API_KEY` is set in your environment
   - Verify the API key is valid and has sufficient credits

2. **FAISS Index Issues:**
   - Run `python manage.py seed_faqs` to create the index
   - Check file permissions for the FAISS_PATH directory

3. **Database Errors:**
   - Run `python manage.py migrate` to apply migrations
   - Check database connection settings

4. **Import Errors:**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.11+)

### Logs

Check application logs for detailed error information:
```bash
# For Docker
docker logs <container-id>

# For local development
# Logs appear in the console where you ran manage.py runserver
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test cases for usage examples
3. Create an issue in the repository

---

**Note**: This is a development-ready implementation. For production use, consider additional security measures, monitoring, and scaling considerations.
