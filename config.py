from dotenv import load_dotenv
import os
from enum import Enum

load_dotenv()

PROXY_URL = os.getenv('PROXY_URL')
PROXY_LOGIN = os.getenv('PROXY_LOGIN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class Language(Enum):
    PYTHON = 'Python'
    CPP = 'C++'
    JAVASCRIPT = 'JavaScript'
    CS = 'C#'
    JAVA = 'Java'