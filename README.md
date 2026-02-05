# Dreamer
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/ArProvat/Dreamer)

Dreamer is the backend API for a web application that uses a multi-agent AI system to generate personalized children's storybooks, complete with text and illustrations.

## Overview

This project leverages a sophisticated AI pipeline to transform a simple story idea into a fully illustrated picture book. It uses a crew of specialized AI agents, each responsible for a different part of the creative process: planning, writing, art direction, and image prompt engineering.

The final output is a complete storybook with consistent characters and a cohesive visual style, ready for presentation.

## Features

-   **Multi-Agent Generation:** Utilizes CrewAI to orchestrate a team of specialized agents (Planner, Writer, Art Director, Prompt Engineer) for a structured and high-quality creative process.
-   **Dynamic Story Concepts:** Generates three unique storyline overviews from a single user prompt, allowing for choice in genre and theme.
-   **Age-Appropriate Content:** Tailors the story structure, page count, and vocabulary to specific age ranges (0-3, 4-6, 7-9).
-   **Consistent Visuals:** Employs an intelligent reference image selection system. For each new page illustration, it selects the most relevant previously generated images to ensure character and style consistency.
-   **High-Quality Illustrations:** Generates detailed, print-ready images using Google's Gemini-3 Pro model, based on meticulously engineered prompts.
-   **Full Book Orchestration:** Manages the end-to-end process from initial idea to a complete, illustrated book stored and ready for access.
-   **Cloud Storage:** Uploads and stores all generated images on AWS S3 for reliable access and delivery.
-   **Data Persistence:** Uses MongoDB to store session data, story overviews, book structure, page text, and image metadata.

## Tech Stack

-   **Backend:** FastAPI
-   **AI Framework:** CrewAI
-   **Language Models:** Google GenAI (Gemini 2.x Flash, Gemini 3 Pro)
-   **Database:** MongoDB with Motor (async driver)
-   **File Storage:** AWS S3
-   **Containerization:** Docker, Docker Compose
-   **Language:** Python 3.11

## Workflow

The book generation process is divided into two main phases:

1.  **Story Conception:**
    -   A user submits a story idea, character descriptions, age range, and other preferences to the `/v1/story_overview` endpoint.
    -   The `StoryGenerator` uses a Gemini model to create three distinct story overviews, each with a different genre and theme.
    -   These overviews are saved to MongoDB and returned to the user.

2.  **Full Book Generation:**
    -   Once a user selects a storyline, the main orchestration process begins.
    -   A crew of AI agents is assembled:
        1.  **Planner Agent:** Creates a detailed, page-by-page structure for the book, defining the narrative arc and story beat for each page.
        2.  **Writer Agent:** Writes the story text for every page according to the planner's structure and target age group.
        3.  **Art Director Agent:** Designs the visual composition for each page, specifying character expressions, scene details, lighting, and color palette to ensure emotional resonance.
        4.  **Prompt Engineer Agent:** Crafts highly detailed, 150-250 word prompts for the image generation model. This agent intelligently selects 1-3 previously generated images as references to maintain character consistency.
    -   The `ImageGenerationService` executes these prompts sequentially, generating an illustration for each page and uploading it to AWS S3.
    -   Finally, all page data (text, image URL, prompts, art direction) is compiled and stored in MongoDB, and the book's status is marked as complete.

## Getting Started

### Prerequisites

-   Docker and Docker Compose
-   An AWS S3 bucket and corresponding credentials
-   A Google API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/arprovat/dreamer.git
    cd dreamer
    ```

2.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project and add the following environment variables:

    ```env
    # Google API Key
    GOOGLE_API_KEY="your_google_api_key"

    # MongoDB Configuration
    DATABASE_URL="your_mongodb_connection_string"
    DATABASE_NAME="your_database_name"
    COLLECTION_NAME="Books"
    COLLECTION_SESSION="sessions"

    # AWS S3 Configuration
    AWS_ACCESS_KEY="your_aws_access_key"
    AWS_SECRET_KEY="your_aws_secret_key"
    S3_BUCKET_NAME="your_s3_bucket_name"
    ```

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

The API will be available at `http://localhost:8000`.

## Project Structure

```
├── app/
│   ├── agents/         # CrewAI agent definitions and tasks
│   ├── DB/             # MongoDB manager and Pydantic schemas
│   ├── modules/        # Reusable components like AWS S3 manager and Auth
│   ├── services/       # Core business logic and API endpoints
│   │   ├── three_story_overview/ # Logic for generating initial story concepts
│   │   ├── generate_story_book/  # Main book generation orchestration
│   │   └── image_genertor/       # Image generation service using Google GenAI
│   └── prompt/         # Centralized storage for LLM prompts
├── Dockerfile          # Multi-stage Dockerfile for the application
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Python dependencies
└── main.py             # FastAPI application entry point
```

## API Endpoints

### Health Check

-   `GET /`
    -   Checks the health of the service.

### Story Generation

-   `POST /v1/story_overview`
    -   Initiates the book creation process. Takes a detailed JSON payload with story ideas, character descriptions, and user preferences.
    -   Creates a new session, generates three story overviews using AI, and saves them to the database.
    -   **Returns:** A session ID, a book ID, and the three generated story concepts.
    -   **Authentication:** Requires a valid JWT Bearer token.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
