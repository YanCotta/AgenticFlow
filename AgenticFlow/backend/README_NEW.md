# AgenticFlow Backend

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.1.0-4B32C3)](https://www.crewai.com/)

This is the backend service for AgenticFlow, an intelligent automation platform that leverages AI agents to manage email communications and social media content.

## 🚀 Features

### Email Processing Pipeline

- **Email Fetcher**: Retrieves and processes incoming emails using Gmail API
- **Email Analyzer**: Analyzes email content, intent, and sentiment
- **Reply Generator**: Crafts context-aware email responses
- **Newsletter Processor**: Extracts valuable content from newsletters

### Social Media Automation

- **Post Formatter**: Optimizes content for different platforms
- **Social Poster**: Manages content distribution to social networks
- **Multi-platform Support**: Twitter, LinkedIn, and more

### Core Infrastructure

- **FastAPI**: High-performance async API framework
- **SQLAlchemy 2.0**: Modern ORM with async support
- **JWT Authentication**: Secure API access
- **Asynchronous Task Queue**: For background processing
- **Comprehensive Logging**: Built-in monitoring and debugging

## 🏗️ Architecture

The backend follows a clean architecture with clear separation of concerns:

```text
backend/
├── agents/           # AI agent implementations
│   ├── email_fetcher.py
│   ├── email_analyzer.py
│   ├── reply_generator.py
│   ├── newsletter_processor.py
│   ├── post_formatter.py
│   └── social_poster.py
├── api/              # API endpoints
│   ├── auth_endpoints.py
│   ├── email_endpoints.py
│   ├── social_endpoints.py
│   └── __init__.py
├── database/         # Database models and migrations
├── models/           # Pydantic models
├── services/         # Business logic
├── utils/            # Utility functions
├── main.py           # FastAPI application
└── requirements.txt  # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis 6.0+
- Gmail API credentials
- Social media API credentials (Twitter, LinkedIn)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/AgenticFlow.git
   cd AgenticFlow/backend
   ```

2. **Set up a virtual environment**

   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy `.env.example` to `.env` and update with your credentials:

   ```env
   # App
   APP_NAME=AgenticFlow
   APP_ENV=development
   DEBUG=True
   SECRET_KEY=your-secret-key
   
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/agenticflow
   
   # JWT
   JWT_SECRET_KEY=your-jwt-secret
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Gmail API
   GMAIL_CREDENTIALS_PATH=credentials.json
   
   # Social Media API Keys
   TWITTER_API_KEY=your-twitter-key
   TWITTER_API_SECRET=your-twitter-secret
   LINKEDIN_CLIENT_ID=your-linkedin-id
   LINKEDIN_CLIENT_SECRET=your-linkedin-secret
   ```

5. **Initialize the database**

   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create initial data (if needed)
   python -m scripts.create_initial_data
   ```

6. **Start the development server**

   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API docs**: <http://localhost:8000/docs>
- **Alternative API docs**: <http://localhost:8000/redoc>

## 🤖 Agent Orchestration

The system uses CrewAI to coordinate multiple specialized agents:

1. **Email Processing Crew**
   - Fetches unread emails
   - Analyzes content and intent
   - Generates draft responses

2. **Social Media Crew**
   - Processes newsletter content
   - Formats posts for different platforms
   - Manages posting schedule

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 🛠️ Development

### Code Style

This project uses:

- Black for code formatting
- isort for import sorting
- Flake8 for linting

Run formatting and checks:

```bash
black .
isort .
flake8
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks before each commit:

```bash
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
