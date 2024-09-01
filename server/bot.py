from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Google Gemini API
genai.configure(api_key=os.environ["API_KEY"])
