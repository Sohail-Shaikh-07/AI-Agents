# Job Automation AI Agent

## Overview

A FastAPI-based agent that scrapes job boards (LinkedIn, Indeed, etc.) using `python-jobspy` and sends email alerts via `Resend`.

## Setup

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file (optional, or set in environment):

    ```env
    RESEND_API_KEY=re_123456789
    ```

3.  **Run API**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Usage

### Search Jobs

**POST** `/api/jobs/search`

```json
{
  "search_term": "Python Developer",
  "location": "Remote",
  "results_wanted": 5,
  "email_to": "your-email@example.com"
}
```

## Deployment via Render

1.  Connect repo to Render.
2.  Build Command: `pip install -r requirements.txt`
3.  Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
