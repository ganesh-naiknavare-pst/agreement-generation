import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
SMTP2GO_API_KEY = os.getenv("SMTP2GO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")
BASE_APPROVAL_URL = os.getenv("BASE_APPROVAL_URL")
