from dotenv import load_dotenv
import os
import re
import string
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


# Function to check if the question is appropriate
def is_question_appropriate(question):
    # List of inappropriate words or phrases
    inappropriate_words = ["offensive", "inappropriate", "rude", "vulgar"]
    
    # Check for inappropriate content
    for word in inappropriate_words:
        if word in question.lower():
            return False
    
    return True

# Function to check if the question is well-formed
def is_question_well_formed(question):
    # Check if the question is too short
    if len(question.split()) < 3:
        return False
    
    # Check if the question starts with a question word or is phrased as a question
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does']
    if not any(question.lower().startswith(word) for word in question_words) and '?' not in question:
        return False
    
    return True

# Function to query Gemini model for an answer
def query_gemini_model(question, pdf_text):
    if not is_question_relevant(question, pdf_text):
        return "I'm sorry, but your question doesn't seem to be related to the information I have."

    if not is_question_appropriate(question):
        return "I'm sorry, but your question contains inappropriate content. "

    if not is_question_well_formed(question):
        return "Your question doesn't seem to be well-formed. "

    context = f"{pdf_text}\n\n{question}"
    response = genai.generate_text(prompt=context)

    if response.result is not None and len(response.candidates) > 0:
        answer = response.result
    else:
        answer = "Sorry, I couldn't find an answer best suited to your question."
    
    return answer
