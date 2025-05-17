# AgenticFlow

AgenticFlow is an advanced multi-agent system that automates email processing, intelligent response generation, and social media content management. Built with Python and leveraging AI, it streamlines communication workflows by intelligently processing incoming emails, generating context-aware responses, and managing social media content distribution.

## 🚀 Project Status

### ✅ Completed
- **Project Setup**
  - Project structure and virtual environment
  - Git repository initialization with proper .gitignore
  - Environment configuration
  - Dependency management with requirements.txt

- **Database Models**
  - SQLAlchemy models for all core entities
  - Database initialization and configuration
  - PostgreSQL and SQLite support
  - Models for emails, newsletters, social posts, and user data

- **Core Agents Implementation**
  - **EmailFetcher**: Retrieves and filters emails from Gmail
  - **EmailAnalyzer**: Analyzes email content and extracts key information
  - **ReplyGenerator**: Generates context-aware email responses
  - **NewsletterProcessor**: Processes and extracts content from newsletters
  - **PostFormatter**: Optimizes content for different social media platforms
  - **SocialPoster**: Manages posting to various social networks

- **Orchestration**
  - **EmailCrew**: Coordinates email processing workflow
  - **SocialCrew**: Manages social media content workflow
  - Centralized orchestration for all agents

### 🚧 In Progress
- **API Endpoints**
  - Authentication and user management
  - Email processing endpoints
  - Social media management endpoints
  - Integration with frontend components

## 📁 Project Structure

```
AgenticFlow/
├── backend/                           # Backend application
│   ├── agents/                        # AI agent implementations
│   │   ├── email_fetcher.py          # Fetches and filters emails
│   │   ├── email_analyzer.py         # Analyzes email content
│   │   ├── reply_generator.py        # Generates email responses
│   │   ├── newsletter_processor.py   # Processes newsletter content
│   │   ├── post_formatter.py         # Formats content for social media
│   │   └── social_poster.py          # Manages social media posts
│   │
│   ├── api/                         # API endpoints
│   │   ├── __init__.py              
│   │   ├── auth_endpoints.py       # Authentication endpoints
│   │   ├── email_endpoints.py       # Email processing endpoints
│   │   └── social_endpoints.py      # Social media endpoints
│   │
│   ├── database/                    # Database models and migrations
│   │   ├── __init__.py
│   │   ├── models.py               # SQLAlchemy models
│   │   └── init_db.py              # Database initialization
│   │
│   ├── utils/                       # Utility functions
│   │   ├── gmail_integration.py    # Gmail API integration
│   │   └── social_integration.py   # Social media API integrations
│   │
│   ├── .env.example                # Example environment variables
│   ├── config.py                   # Application configuration
│   ├── main.py                     # Application entry point
│   ├── orchestrator.py             # Agent orchestration
│   └── requirements.txt            # Python dependencies
│
├── frontend/                      # Frontend application (Coming Soon)
├── tests/                         # Test suite
└── README.md                      # This file
```

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Node.js and npm (for frontend, coming soon)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AgenticFlow.git
   cd AgenticFlow/backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On Unix or MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   # For development (SQLite)
   python -m flask db upgrade
   
   # For production (PostgreSQL)
   # Set DB_URL in .env to your PostgreSQL connection string
   # Then run:
   # python -m flask db upgrade
   ```

6. **Run the development server**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:5000`

## 📚 API Documentation

Once the server is running, you can access:
- API Documentation: `http://localhost:5000/api/docs`
- Health Check: `http://localhost:5000/health`

## 🤖 Agents & Workflows

### Core Agents

#### Email Processing
- **EmailFetcher**: Retrieves and filters unread emails from Gmail using the Gmail API
- **EmailAnalyzer**: Analyzes email content, extracts key information, and categorizes emails
- **ReplyGenerator**: Generates context-aware email responses using AI

#### Social Media Management
- **NewsletterProcessor**: Extracts and structures content from newsletters
- **PostFormatter**: Optimizes content for different social media platforms
- **SocialPoster**: Handles authentication and posting to various social networks

### Workflow Orchestration

#### EmailCrew
1. Fetches unread emails
2. Analyzes and categorizes emails
3. Generates draft replies when needed

#### SocialCrew
1. Processes newsletter content
2. Formats content for different platforms
3. Schedules and posts content

### Features
- **AI-Powered Processing**: Leverages OpenAI's models for content understanding
- **Multi-Platform Support**: Works with Gmail, Twitter, LinkedIn, and more
- **Asynchronous Processing**: Efficient handling of multiple tasks
- **Extensible Architecture**: Easy to add new agents and workflows
- **Secure Authentication**: JWT-based authentication for API access

## 🔒 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

Yan Cotta - yanpcotta@gmail.com

Project Link: [https://github.com/YanCotta/AgenticFlow](https://github.com/YanCotta/AgenticFlow)

## 📝 Changelog

### [0.2.0] - 2025-05-17
#### Added
- Implemented all core agents (EmailFetcher, EmailAnalyzer, ReplyGenerator, etc.)
- Added workflow orchestration with CrewAI
- Integrated OpenAI for content processing
- Added Gmail and social media API integrations
- Implemented database models for all entities
- Added configuration management
- Comprehensive error handling and logging
- Asynchronous task processing
- Unit tests for core functionality

### [0.1.0] - 2025-05-16
#### Added
- Initial project setup
- Database models and configuration
- Basic Flask application structure
- Authentication system
- API documentation
