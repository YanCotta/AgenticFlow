# AgenticFlow

AgenticFlow is an intelligent automation platform that leverages AI agents to manage email communications and social media content. The system automatically processes incoming emails, generates appropriate responses, extracts valuable content from newsletters, and shares it across social media platforms.

## ✨ Features

- **Smart Email Management**
  - Automated email fetching and analysis
  - Intelligent response generation
  - Newsletter content extraction

- **Social Media Automation**
  - Multi-platform content distribution (Twitter, LinkedIn, etc.)
  - Platform-optimized post formatting
  - Scheduled posting capabilities

- **AI-Powered Agents**
  - CrewAI-based agent orchestration
  - Specialized agents for different tasks
  - Extensible architecture

- **RESTful API**
  - FastAPI-based backend
  - JWT authentication
  - Comprehensive API documentation

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis (for task queue)
- Gmail API credentials
- Social media API credentials (Twitter, LinkedIn)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AgenticFlow.git
   cd AgenticFlow
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Copy `.env.example` to `.env` and update with your credentials.

4. Initialize the database:
   ```bash
   alembic upgrade head
   ```

5. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

## 🏗️ Project Structure

```
AgenticFlow/
├── backend/               # Backend application
│   ├── agents/           # AI agent implementations
│   ├── api/              # API endpoints
│   ├── database/         # Database models and migrations
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend (coming soon)
├── tests/                # Test suite
├── .env.example          # Example environment variables
├── .gitignore
└── README.md             # This file
```

## 🤖 Agent Architecture

The system is built around specialized AI agents that work together:

1. **Email Fetcher**: Retrieves and processes incoming emails
2. **Email Analyzer**: Analyzes email content and intent
3. **Reply Generator**: Crafts context-aware email responses
4. **Newsletter Processor**: Extracts valuable content from newsletters
5. **Post Formatter**: Optimizes content for different social platforms
6. **Social Poster**: Manages content distribution to social networks

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) (available when running locally)
- [Architecture Decision Records](./docs/adr/)
- [Development Guide](./docs/DEVELOPMENT.md)

## 🛠️ Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- Flake8 for linting

Run formatting and linting:
```bash
black .
isort .
flake8
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [CrewAI](https://www.crewai.com/)
- Inspired by modern AI agent architectures
