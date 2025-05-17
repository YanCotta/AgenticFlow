# AgenticFlow Backend

This is the backend service for AgenticFlow, a multi-agent system for processing emails and managing social media content.

## Features

- **Email Processing**: Fetch, analyze, and respond to emails automatically
- **Newsletter Extraction**: Identify and extract content from newsletters
- **Social Media Management**: Format and post content to various social media platforms
- **RESTful API**: Built with FastAPI for high performance and easy integration
- **Authentication**: JWT-based authentication for secure access
- **Asynchronous Processing**: Built with asyncio for high concurrency

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Redis (for background tasks, optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AgenticFlow.git
   cd AgenticFlow/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your configuration:
   ```env
   # App
   APP_NAME=AgenticFlow
   APP_ENV=development
   DEBUG=True
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
