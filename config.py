from dotenv import load_dotenv
import os
from enum import Enum

load_dotenv()

proxy = {
    'http': f'http://{os.getenv("PROXY_LOGIN")}@{os.getenv("PROXY_HOST")}:{os.getenv("PROXY_PORT_HTTP")}',
    'https': f'http://{os.getenv("PROXY_LOGIN")}@{os.getenv("PROXY_HOST")}:{os.getenv("PROXY_PORT_HTTPS")}',
}
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class Language(Enum):
    PYTHON = 'Python'
    CPP = 'C++'
    JAVASCRIPT = 'JavaScript'

compillable = [Language.CPP]