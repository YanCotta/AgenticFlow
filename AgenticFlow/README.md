# AgenticFlow

AgenticFlow is a multi-agent system designed to automate email processing, analysis, and response generation, with additional capabilities for social media management. The system uses AI agents to process incoming emails, generate appropriate responses, and manage social media content.

## 🚀 Project Status

### ✅ Completed
- **Project Setup**
  - Project structure and virtual environment
  - Git repository initialization with proper .gitignore
  - Environment configuration

- **Database Models**
  - SQLAlchemy models for all core entities
  - Database initialization and configuration
  - PostgreSQL and SQLite support

### 🚧 In Progress
- **Agents Implementation** (Starting Next)
  - Email fetcher
  - Email analyzer
  - Reply generator
  - Newsletter processor
  - Social media poster

## 📁 Project Structure

```
AgenticFlow/
├── backend/                     # Backend application
│   ├── agents/                  # AI agent implementations
│   ├── api/                     # API endpoints
│   ├── database/                # Database models and migrations
│   ├── static/                  # Static files
│   ├── templates/               # HTML templates
│   ├── utils/                   # Utility functions
│   ├── .env.example             # Example environment variables
│   ├── config.py                # Application configuration
│   ├── main.py                  # Application entry point
│   └── requirements.txt         # Python dependencies
├── frontend/                    # Frontend application (To be implemented)
├── tests/                       # Test suite (To be implemented)
└── README.md                    # This file
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

## 🤖 Agents Overview

### Implemented Agents
- None yet

### Upcoming Agents
- Email Fetcher: Fetches emails from configured accounts
- Email Analyzer: Analyzes email content and extracts key information
- Reply Generator: Generates context-aware email replies
- Newsletter Processor: Extracts and processes newsletter content
- Social Media Poster: Manages social media posts

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

### [0.1.0] - 2025-05-17
#### Added
- Initial project setup
- Database models and configuration
- Basic Flask application structure
- Authentication system
- API documentation
