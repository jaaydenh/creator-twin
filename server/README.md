# Transcript Ingestion, Personality and Knowledge Services

This project is a comprehensive platform for creating and interacting with AI-powered character personas. It analyzes the communication style of a content creator from their YouTube video transcripts and generates a detailed personality profile. This profile is then used to power a conversational AI that can be interacted with via a web interface.

The project is divided into two main components:

1.  **FastAPI Backend**: A robust backend that handles data ingestion, processing, personality generation, chat workflows, and user/message management.
2.  **Streamlit Frontend**: An interactive web application for chatting with the generated AI persona.

## Features

- **Personality Generation**: Automatically analyzes YouTube video transcripts to create a detailed communication profile, including lexicon, syntax, and rhetorical style.
- **Vector Search**: Utilizes Pinecone to store and perform semantic searches on video transcript chunks, enabling efficient information retrieval.
- **Conversational AI**: Powers a LangChain agent with the generated personality, allowing for natural and in-character interactions.
- **Web Interface**: Provides a user-friendly chat interface built with Streamlit for interacting with the AI persona.
- **Data Management**: Includes tools for managing video data, including storing and retrieving transcript chunks from a local SQLite database.
- **User and Chat Workflow Management**: Internal and workflow routers for user creation, chat message storage, chat history summarization, and rate limiting.

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **AI/ML**: LangChain, Google Gemini, Pinecone
- **Database**: SQLite
- **Other**: `youtube-transcript-api`, `pydantic`, `dotenv`

## Project Structure

```
creator-twin/
├── app.py                        # FastAPI application
├── config/
│   ├── client.py                 # Model client configuration
│   ├── gemini_config.py          # Google Gemini API config
│   └── pinecone_config.py        # Pinecone client configuration
├── database/
│   ├── character_db.py           # Character DB functions
│   ├── messages_db.py            # Chat message DB functions
│   ├── pinecone_retriever.py     # Pinecone data retrieval
│   ├── pinecone_upsert.py        # Pinecone data upserting
│   └── user_db.py                # User DB functions (rate limit, summary, etc.)
├── models/
│   ├── api_models.py             # API request/response models
│   └── personality.py            # Personality profile model
├── requirements.txt              # Python dependencies
├── routers/
│   ├── chat_workflow_router.py   # Main chat workflow router
│   └── user_db_routers.py        # User DB/internal routers
├── services/
│   ├── process_user_message.py   # Main chat workflow logic
│   └── summary.py                # Chat history summarization
├── tools/
│   ├── extract_details.py        # Transcript analysis and detail extraction
│   ├── get_details.py            # Personality generation
│   ├── my_details.py             # Creator information retrieval
│   ├── tools.py                  # Tool aggregation
│   └── transcript.py             # YouTube transcript fetching and processing
├── .env                          # Environment variables (API keys)
└── README.md                     # Project documentation
```

## Setup and Installation

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the `server` directory and add the following:

    ```
    GOOGLE_API_KEY=<your-google-gemini-api-key>
    PINECONE_API_KEY=<your-pinecone-api-key>
    ```

## Usage

### FastAPI Backend

To run the FastAPI backend, use the following command:

```bash
uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

#### API Endpoints

- `GET /`: Health check.
- `POST /generate_personality_from_videos`: Generates a personality profile from a list of YouTube video IDs.
- `GET /creator_background_details`: Retrieves background information about the content creator.
- `POST /load_data`: Loads video transcript chunks into the local SQLite database and Pinecone.
- `GET /retrieve_pinecone_data`: Performs a semantic search on the Pinecone database for a given creator and query.

**User DB/Internal endpoints** (via `/user_db` prefix):
- `POST /user_db/add_user`: Add a new user.
- `POST /user_db/store_chat_message`: Store a chat message.
- `GET /user_db/get_recent_chat_history`: Retrieve recent chat history.
- `POST /user_db/clear_old_chat_messages`: Clear old chat messages.
- `POST /user_db/summarize_chat_history`: Summarize chat history.
- `POST /user_db/create_tables`: Create user and chat message tables.
- `GET /user_db/get_user_info`: Retrieve user info.

**Main Chat Workflow** (via `/chat` prefix):
- `POST /chat/process_message`: Main workflow for processing user messages, enforcing rate limits, updating chat info, summarizing history, and clearing old messages.

### Streamlit Frontend

To run the Streamlit frontend, use the following command:

```bash
streamlit run main.py
```

The web application will be available at the URL provided in the terminal. The application will automatically generate a personality from a hardcoded list of videos and allow you to start chatting with the AI persona.

## Notes

- Ensure your `.env` file contains valid API keys for Google Gemini and Pinecone.
- The chat workflow automatically summarizes and clears chat history after a configurable threshold.
- Internal endpoints are intended for backend/service use and not exposed to external clients.

---