# Character AI

This project is a comprehensive platform for creating and interacting with AI-powered character personas. It analyzes the communication style of a content creator from their YouTube video transcripts and generates a detailed personality profile. This profile is then used to power a conversational AI that can be interacted with via a web interface.

The project is divided into two main components:

1.  **FastAPI Backend**: A robust backend that handles data ingestion, processing, and personality generation.
2.  **Streamlit Frontend**: An interactive web application for chatting with the generated AI persona.

## Features

- **Personality Generation**: Automatically analyzes YouTube video transcripts to create a detailed communication profile, including lexicon, syntax, and rhetorical style.
- **Vector Search**: Utilizes Pinecone to store and perform semantic searches on video transcript chunks, enabling efficient information retrieval.
- **Conversational AI**: Powers a LangChain agent with the generated personality, allowing for natural and in-character interactions.
- **Web Interface**: Provides a user-friendly chat interface built with Streamlit for interacting with the AI persona.
- **Data Management**: Includes tools for managing video data, including storing and retrieving transcript chunks from a local SQLite database.

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **AI/ML**: LangChain, AWS Bedrock, Pinecone
- **Database**: SQLite
- **Other**: `youtube-transcript-api`, `pydantic`

## Project Structure

```
Charachter/
├── app.py                  # FastAPI application
├── character_db.db         # SQLite database for character data
├── config/                 # Configuration files for clients and services
│   ├── client.py           # AWS Bedrock client configuration
│   └── pinecone_config.py  # Pinecone client configuration
├── database/               # Database interaction modules
│   ├── charachter_db.py    # SQLite database functions
│   ├── pinecone_retriever.py # Pinecone data retrieval
│   └── pinecone_upsert.py    # Pinecone data upserting
├── main.py                 # Streamlit application
├── models/                 # Pydantic data models
│   ├── api_models.py       # API request/response models
│   └── personality.py      # Personality profile model
├── requirements.txt        # Python dependencies
├── services/               # External service integrations
│   └── pinecone.py
├── tools/                  # Core logic and tools
│   ├── extract_details.py  # Transcript analysis and detail extraction
│   ├── get_details.py      # Personality generation
│   ├── my_details.py       # Creator information retrieval
│   ├── tools.py            # Tool aggregation
│   └── transcript.py       # YouTube transcript fetching and processing
└── video_chunks.db         # SQLite database for video chunks
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Charachter
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add the following:

    Currently this project uses bedrock but we can change it to any model  gemini,openai etc
    To update the model u can modify config/client.py file .
    ```
    BEDROCK_INFERENCE_PROFILE_ARN=<your-bedrock-arn>
    AWS_DEFAULT_REGION=<your-aws-region>
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
- `GET /creator_background_details`: Retrieves background information about the content creator from a Google Doc.
- `POST /load_data`: Loads video transcript chunks into the local SQLite database and Pinecone.
- `GET /retrieve_pinecone_data`: Performs a semantic search on the Pinecone database for a given creator and query.

### Streamlit Frontend

To run the Streamlit frontend, use the following command:

```bash
streamlit run main.py
```

The web application will be available at the URL provided in the terminal. The application will automatically generate a personality from a hardcoded list of videos and allow you to start chatting with the AI persona. 