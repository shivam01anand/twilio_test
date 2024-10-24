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


YOUR_NUMBER = 'whatsapp:+918586906652'
TWILIO_NUMBER = 'whatsapp:+14155238886'

# Track conversations for multiple users
conversations = {}

QUESTIONS = [
    "What construction tasks did you work on today? (e.g., foundation work, framing, electrical)",
    "How many hours did you spend on each task?",
    "Did you have any materials or equipment expenses today? Please list items and costs.",
    "Any safety concerns, delays, or challenges to report?",
    "Do you need any materials or equipment for tomorrow?",
    "Any additional comments or questions?"
]

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("Webhook called!")
    
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From', '')
    
    # Get or create conversation state for this user
    if from_number not in conversations:
        conversations[from_number] = {
            'responses': [],
            'is_active': False
        }
    
    conversation = conversations[from_number]
    
    # Only process messages if conversation is active
    if conversation['is_active']:
        conversation['responses'].append(incoming_msg)
        
        # If we have all answers, save and end conversation
        if len(conversation['responses']) >= len(QUESTIONS):
            try:
                # Here you could save to database or spreadsheet
                logger.info(f"Complete responses from {from_number}: {conversation['responses']}")
                
                # Send thank you message
                client.messages.create(
                    body="Thanks for your daily report! Have a good day! 👍",
                    from_=TWILIO_NUMBER,
                    to=from_number
                )
                
                # Reset conversation
                conversation['responses'] = []
                conversation['is_active'] = False
                
            except Exception as e:
                logger.error(f"Error processing complete response: {str(e)}")
        
        # If we still need more answers, send next question
        else:
            try:
                next_question = QUESTIONS[len(conversation['responses'])]
                client.messages.create(
                    body=next_question,
                    from_=TWILIO_NUMBER,
                    to=from_number
                )
            except Exception as e:
                logger.error(f"Error sending next question: {str(e)}")
    
    return 'OK', 200

@app.route('/start', methods=['GET'])
def start():
    try:
        # Reset and start new conversation
        conversations[YOUR_NUMBER] = {
            'responses': [],
            'is_active': True
        }
        
        # Send first question
        client.messages.create(
            body=QUESTIONS[0],
            from_=TWILIO_NUMBER,
            to=YOUR_NUMBER
        )
        logger.info("Started new conversation")
        return 'Daily report questions started!'
    
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        return 'Error starting conversation', 500

port = int(os.environ.get('PORT', 10000))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
   
