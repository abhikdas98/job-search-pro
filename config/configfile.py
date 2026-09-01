import os
from dotenv import load_dotenv
from pathlib import Path



class config:
    def __init__(self):
        #Loading the environment variables by the explicitly mentioning the root directory for robustness
        ROOT_DIR = Path(__file__).resolve().parent
        env_path = ROOT_DIR / ".env"
        load_dotenv(env_path)

        self.groq_api_key = os.getenv("GROQ_API_KEY")

        self._validate()

    def _validate(self):
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is missing from .env")