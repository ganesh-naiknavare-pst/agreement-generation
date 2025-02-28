from enum import Enum

# Enum for AI models
class Model(Enum):
    GPT_4 = "gpt-4o"

# Local OpenAI-compatible API URL
CHAT_OPENAI_BASE_URL = "http://0.0.0.0:1337/v1"

# SMTP2GO email API endpoint
SMTP2GO_EMAIL_SEND_URL = "https://api.smtp2go.com/v3/email/send"

MAX_RETRIES = 5
RETRY_DELAY = 2
