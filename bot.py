import os
import re
import string
import joblib
import pdfplumber
from telegram import Update
from dotenv import load_dotenv
import google.api_core.exceptions
import google.generativeai as genai
from telegram.constants import ChatAction
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters



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


# Function to handle greetings
def handle_greeting(message):
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    message = message.lower()
    for greeting in greetings:
        if greeting in message:
            return "Hello! Feel free to ask me anything about Me. 😊"
    return None


# Function to handle compliments
def handle_compliment(message):
    compliments = ["thank you", "thanks", "great job", "well done", "good bot", "awesome", "amazing", "excellent"] 
    message = message.lower()
    for compliment in compliments:
        if compliment in message:
            return "You're welcome! I'm glad I could help. 😊"
    return None


# Cached version of query_gemini_model
def cached_query_gemini_model(question, pdf_text):
    try:
        cache = joblib.load(CACHE_FILE)
    except FileNotFoundError:
        cache = {}
    
    if question in cache:
        return cache[question]
    else:
        answer = query_gemini_model(question, pdf_text)
        cache[question] = answer
        joblib.dump(cache, CACHE_FILE)
        return answer


# Command handler for /start
async def start(update: Update, context):
   
    await update.message.reply_text("Hi there 👋")
    await update.message.reply_text("Welcome to My Portfolio Bot. 🎉")
    await update.message.reply_text("I'm Nicholas a Software Engineer from Kenya.")
    await update.message.reply_text("Feel free to ask me anything you want to know about Me. 🤩🤩")


# Function to preprocess the user's question
def preprocess_question(question):
    # Remove extra whitespace
    question = question.strip()
    
    # Remove trailing punctuation marks like question marks
    if question.endswith('?'):
        question = question[:-1]
    
    # Replace other special punctuation marks with spaces
    question = re.sub(r'[{}]+'.format(re.escape(string.punctuation.replace("?", ""))), " ", question)
    
    # Convert to lowercase for uniformity
    question = question.lower()
    
    return question

async def handle_message(update: Update, context):
    user_message = update.message.text
    print(f"Received message: '{user_message}'")

    # Preprocess the user message
    preprocessed_message = preprocess_question(user_message)

    greeting_response = handle_greeting(preprocessed_message)
    compliment_response = handle_compliment(preprocessed_message)

    # Send the typing action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if greeting_response is not None:
        await update.message.reply_text(greeting_response)
    elif compliment_response is not None:
        await update.message.reply_text(compliment_response)
    else:
        try:
            answer = cached_query_gemini_model(preprocessed_message, pdf_text)

            if answer is not None:
                if len(answer) > MESSAGE_CHARACTER_LIMIT:
                    for i in range(0, len(answer), MESSAGE_CHARACTER_LIMIT):
                        await update.message.reply_text(answer[i:i + MESSAGE_CHARACTER_LIMIT])
                else:
                    await update.message.reply_text(answer)
            else:
                await update.message.reply_text("Sorry, I couldn't process your request.")
        except google.api_core.exceptions.DeadlineExceeded:
            await update.message.reply_text("Sorry, the request is taking too long. Please try again later.")
        except Exception as e:
            await update.message.reply_text(f"An unexpected error occurred: {str(e)}")


# Main function to run the bot
def main():
    print("Starting bot...")
    global pdf_text
    pdf_text = extract_pdf_text("pdf/Portfolio Questions.pdf") 

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is now polling for messages...")
    application.run_polling()

if __name__ == '__main__':
    main()
    print("Bot has stopped.")

