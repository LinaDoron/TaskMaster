# TaskMaster // Autonomous AI Secretary

An intelligent, asynchronous Telegram bot architecture that integrates deeply with Notion and utilizes LLM Tool Calling (via DeepSeek/OpenRouter) for natural language task processing and behavioral enforcement.

Built to automate routine, enforce strict daily discipline, and provide analytical daily audits without human overhead.

## Core Features

- **Natural Language Parsing (NLP):** Send an unstructured message like *"remind me to pay for the VPS server tomorrow, critical priority"*, and the LLM will automatically extract the exact date, task payload, and severity level (CRITICAL) for database ingestion.
- **Notion API Integration:** Utilizes Notion as a persistent, long-term database for Tasks and Habit tracking.
- **Customizable AI Persona:** Through the BOT_PERSONA environment variable, the LLM adopts any specific persona required (e.g., a cold, ruthless taskmaster demanding flawless execution).
- **Asynchronous Routines (APScheduler):**
    - 08:00 — Morning briefing and pending task delivery (features Inline UI for one-click execution).
    - 21:00 — Evening habit tracker audit with AI-generated performance verdicts based on the daily completion rate.

## Tech Stack

- **Python 3.10+** (Asyncio-driven)
- **aiogram 3.x** (Telegram Bot Framework)
- **notion-client** (Notion REST API)
- **openai** (DeepSeek / OpenRouter API compatibility for JSON Mode & Tool Calls)
- **APScheduler** (Cron job scheduling)

```
ai_secretary_bot/
├── .env                    # Secrets & API Keys (gitignored)
├── requirements.txt        # Dependencies
├── main.py                 # Application entry point, bot & scheduler init
├── config.py               # Environment variables loading and validation
├── middlewares/
│   └── auth.py             # Security middleware (Strict ADMIN_ID validation)
├── handlers/               # Telegram message processors
│   ├── tasks.py            # Natural language task ingestion logic
│   └── callbacks.py        # Inline button handlers (✅ Execute / ❌ Cancel)
├── keyboards/
│   └── inline.py           # Dynamic UI markup generation
├── services/               # External integrations
│   ├── notion_api.py       # Notion REST API wrappers (GET/POST/PATCH)
│   └── deepseek_api.py     # LLM interactions, system prompts, and JSON Mode
└── scheduler/
    └── jobs.py             # Scheduled cron tasks (08:00 / 21:00 loops)
```

## Setup & Deployment

1. **Clone the repository:**
    
    ```
    git clone https://github.com/yourusername/taskmaster-ai.git
    cd taskmaster-ai
    ```
    
2. **Install dependencies:**
    
    ```
    pip install -r requirements.txt
    ```
    
3. **Environment Configuration:**
    
    Create a .env file based on .env.example and insert your API keys (Telegram, Notion, LLM provider) and your Telegram ADMIN_ID.
    
4. **Initialize the engine:**
    
    ```
    python main.py
    ```

## Notion Database Architecture

For the bot to function seamlessly, you must set up two databases in your Notion workspace and share them with your Notion Integration:

1. **Tasks DB**
    - Task (Title)
    - Execution Date (Date)
    - Status (Status: *Pending, Executed, Canceled*)
    - Severity (Select: *Low, Medium, CRITICAL*)
    - AI Log (Text)
2. **Habits DB**
    - Name (Title)
    - Date (Date)
    - Completion Rate (Formula)
    - Operator Note (Text)
    - AI Verdict (Text)
    - *[Add your custom habit checkboxes here]*
  
Note: Ensure that the exact names of your custom habit checkboxes are mapped inside the system prompt located in services/deepseek_api.py.
