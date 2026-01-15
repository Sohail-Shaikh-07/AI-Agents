from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)

# Load API Key from environment or use a default (NOT RECOMMENDED for production to hardcode, using from env is best)
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
DEEPINFRA_BASE_URL = "https://api.deepinfra.com/v1/openai"

client = None
if DEEPINFRA_API_KEY:
    client = OpenAI(
        api_key=DEEPINFRA_API_KEY,
        base_url=DEEPINFRA_BASE_URL,
    )
else:
    logger.warning("DEEPINFRA_API_KEY not set. LLM features will be disabled.")


def tailor_resume(resume_text: str, job_description: str) -> str:
    """
    Uses the LLM to tailor a resume for a specific job description.
    """
    if not client:
        return "LLM Service Unavailable: Missing API Key"

    prompt = f"""
    You are an expert resume writer.
    
    Here is my current resume:
    {resume_text}
    
    Here is the job description I am applying for:
    {job_description}
    
    Please rewrite my resume to better match this job description. 
    Focus on highlighting relevant skills and experiences. 
    Keep the formatting clean and professional (Markdown).
    Do not invent false information, but emphasize the truth that matches the job.
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # Requested model
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error tailoring resume: {e}")
        return f"Error tailoring resume: {str(e)}"
