import os
from dotenv import load_dotenv
from script.exchange.gemini import GeminiApi

load_dotenv()

GeminiApi(os.getenv('GEMINI_API_KEY'), os.getenv('GEMINI_API_SECRET')).run()