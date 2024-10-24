from flask import Flask, request
from twilio.rest import Client
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

# Hardcoded credentials
account_sid = 'ACa5cece43b75cb915157a22ffca14fde2'
with open('/etc/secrets/TWILIO_AUTH_TOKEN', 'r') as file:
    auth_token = file.read().strip()

client = Client(account_sid, auth_token)
   
# Your number
YOUR_NUMBER = 'whatsapp:+918586906652'
# Twilio's sandbox number
TWILIO_NUMBER = 'whatsapp:+14155238886'

# Store conversation state
user_state = {'current_question': 0, 'responses': []}

QUESTIONS = [
    "What did you work on today?",
    "How many hours did you spend on each task?",
    "Any blockers or challenges?",
    "What's your plan for tomorrow?"
]

@app.route('/')
def home():
    return 'WhatsApp Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.form.get('Body', '').strip()
    
    # Add response to list
    user_state['responses'].append(incoming_msg)
    
    # If we have more questions to ask
    if len(user_state['responses']) < len(QUESTIONS):
        # Send next question
        client.messages.create(
            body=QUESTIONS[len(user_state['responses'])],
            from_=TWILIO_NUMBER,
            to=YOUR_NUMBER
        )
    else:
        # Send thank you message
        client.messages.create(
            body="Thanks for your update! Have a great day! 👍",
            from_=TWILIO_NUMBER,
            to=YOUR_NUMBER
        )
        # Reset state
        user_state['responses'] = []
    
    return 'OK', 200

@app.route('/start', methods=['GET'])
def start():
    """Start the daily questions"""
    user_state['responses'] = []
    client.messages.create(
        body=QUESTIONS[0],
        from_=TWILIO_NUMBER,
        to=YOUR_NUMBER
    )
    return 'First question sent!'

# This is important for Render
port = int(os.environ.get('PORT', 10000))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
