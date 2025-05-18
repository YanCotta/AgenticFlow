# AgenticFlow Backend

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.1.0-4B32C3)](https://www.crewai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

The AgenticFlow Backend is a high-performance, scalable service that powers the intelligent automation platform. It leverages modern Python technologies and AI to provide seamless email management and social media automation capabilities.

## ✨ Key Features

### 🤖 Email Processing Pipeline

- **Email Fetcher**: Asynchronously retrieves and processes emails via Gmail API with OAuth2 authentication
- **Email Analyzer**: Utilizes NLP to analyze content, extract entities, and determine sentiment and intent
- **Reply Generator**: Creates contextually appropriate responses using advanced language models
- **Newsletter Processor**: Intelligently extracts and structures content from various newsletter formats

### 📱 Social Media Integration

- **Multi-Platform Support**: Native integration with Twitter, LinkedIn, and extensible to other platforms
- **Content Optimization**: Automatically formats content for each platform's specifications
- **Scheduling Engine**: Advanced scheduling system for optimal post timing
- **Analytics**: Tracks engagement metrics and performance

### 🏗️ Core Infrastructure

- **Asynchronous Architecture**: Built on FastAPI for high concurrency and performance
- **Database Layer**: PostgreSQL with SQLAlchemy 2.0 ORM and Alembic for migrations
- **Authentication**: JWT-based stateless authentication with refresh tokens
- **Task Queue**: Distributed task processing with Celery and Redis
- **Caching**: Redis-based caching for improved performance
- **Logging & Monitoring**: Structured logging with Sentry integration
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Testing**: Comprehensive test suite with pytest
- **Containerization**: Docker support for easy deployment

### 🔌 API Endpoints

- **Authentication**: JWT-based auth with refresh tokens
- **Email Management**: Fetch, analyze, and respond to emails
- **Social Media**: Schedule and publish content across platforms
- **Analytics**: Access performance metrics and insights
- **Settings**: Configure system behavior and integrations

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
   SECRET_KEY=your-secret-key-here
   
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/agenticflow
   
   # JWT
   JWT_SECRET_KEY=your-jwt-secret-key
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Email (for sending notifications)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-email-password
   
   # Social Media API Keys
   TWITTER_API_KEY=your-twitter-api-key
   TWITTER_API_SECRET=your-twitter-api-secret
   LINKEDIN_CLIENT_ID=your-linkedin-client-id
   LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Running the Application

#### Development

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` and the interactive API documentation at `http://localhost:8000/docs`.

#### Production

For production, you should use a production-grade ASGI server like Gunicorn with Uvicorn workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative API docs**: `http://localhost:8000/redoc`
- **OpenAPI schema**: `http://localhost:8000/openapi.json`

## Project Structure

```
backend/
├── alembic/                 # Database migrations
├── api/                      # API endpoints
│   ├── __init__.py
│   ├── auth_endpoints.py     # Authentication endpoints
│   ├── email_endpoints.py    # Email processing endpoints
│   └── social_endpoints.py   # Social media endpoints
├── agents/                   # Agent implementations
│   ├── __init__.py
│   ├── email_fetcher.py      # Fetches emails from various sources
│   ├── email_analyzer.py     # Analyzes email content
│   ├── reply_generator.py    # Generates email replies
│   ├── newsletter_processor.py # Processes newsletter content
│   ├── post_formatter.py     # Formats content for social media
│   ├── social_poster.py      # Posts to social media platforms
│   └── orchestrator.py       # Coordinates all agents
├── config/                   # Configuration
│   └── settings.py           # Application settings
├── database/                 # Database models and session
│   ├── __init__.py
│   ├── models.py             # SQLAlchemy models
│   └── session.py            # Database session management
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── logger.py             # Logging configuration
│   └── security.py           # Security utilities
├── .env.example              # Example environment variables
├── .gitignore
├── alembic.ini               # Alembic configuration
├── main.py                   # FastAPI application entry point
├── README.md                 # This file
└── requirements.txt          # Project dependencies
```

## Testing

To run the test suite:

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - The ORM used
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Uvicorn](https://www.uvicorn.org/) - ASGI server
