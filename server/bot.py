from dotenv import load_dotenv
import os
import joblib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Google Gemini API
genai.configure(api_key=os.environ["API_KEY"])

# Telegram message character limit
MESSAGE_CHARACTER_LIMIT = 4096


# Cache file path
CACHE_FILE = "cache.joblib"
