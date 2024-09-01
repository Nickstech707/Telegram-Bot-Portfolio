# Telegram-Bot-Portfolio

A Telegram bot that automate answers to questions about Personal infomation using the Google Gemini API.

## Requirements

To run this bot, you'll need to install the following libraries:

1. dotenv
2. google-generativeai
3. python-telegram-bot
4. joblib
5. pdfplumber
6. scikit-learn

You can install them using `pip install -r requirements.txt`.

## Environment Variables

Create a `.env` file with the following environment variables:
`API_KEY=your_google_gemini_api_key`
`TELEGRAM_BOT_TOKEN=your_telegram_bot_token`

Replace `your_google_gemini_api_key` and `your_telegram_bot_token` with your actual API keys.

## PDF Document

Place your PDF document in the `pdf` directory or which ever way you want to create it.

## Running the Bot

To run the bot, simply execute `python main.py`. The bot will start polling for messages.

## Features

The bot has the following features:

- Answers questions about the PDF document using the Google Gemini API.
- Handles greetings and compliments.
- Caches results to improve performance.
- Supports multiple messages for long answers.

## Note

This bot is designed to work with a specific PDF document and may require modifications to work with other documents.

## Technologies used

Python 3.
