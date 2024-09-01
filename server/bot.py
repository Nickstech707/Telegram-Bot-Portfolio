from dotenv import load_dotenv
import os
import joblib
import pdfplumber
from telegram import Update
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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



# Extract text from the PDF
def extract_pdf_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    print("PDF text extraction complete.")
    return text


# Function to check relevance of the question to the PDF content
def is_question_relevant(question, pdf_text, threshold=0.1):
    vectorizer = TfidfVectorizer().fit([pdf_text])
    pdf_vector = vectorizer.transform([pdf_text])
    question_vector = vectorizer.transform([question])
    similarity = cosine_similarity(pdf_vector, question_vector)[0][0]
    return similarity > threshold
