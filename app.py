import os
import json
import requests
import datetime
from flask import Flask, request, jsonify
import google.genai as genai
from google.genai import types
from twilio.twiml.messaging_response import MessagingResponse
from invoice_gen import generate_pdf
from db_manager import (
    get_user, create_user, update_user, set_user_state,
    add_conversation_entry, is_onboarding_complete
)

app = Flask(__name__)

# Configure Google Gemini API with new package
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)

# Twilio credentials for media downloads
TWILIO_ACCOUNT_SID = "ACc4e5d0d95c473b3bf0c28e1b4a83af1c"
TWILIO_AUTH_TOKEN = "ed0f3cc794912c58d9555a6b0b28e6eb"


def parse_order(media_url=None, text_body=None, pending_order=None, input_type='text', mime_type=None):
    """
    Parse order information from IMAGE, AUDIO, or TEXT using Google Gemini 1.5 Flash.
    Now with OCR support for handwritten notes and intelligent missing field detection.
    
    Args:
        media_url (str, optional): URL to media file (image/audio) to download and process
        text_body (str, optional): Text message to process
        pending_order (dict, optional): Previously extracted partial order data
        input_type (str): 'image', 'audio', or 'text'
        mime_type (str, optional): MIME type of the media (e.g., 'image/jpeg', 'audio/ogg')
    
    Returns:
        dict: Response with structure:
            {
                'status': 'complete' | 'incomplete' | 'error',
                'data': {'customer': str, 'items': [...]},
                'missing_fields': ['customer', 'item_X_rate', ...],
                'message': 'Human-readable message'
            }
    """
    
    # DYNAMIC SYSTEM PROMPT based on input type
    if input_type == 'image':
        # OCR-focused prompt for handwritten notes
        system_prompt = """You are an intelligent OCR assistant for handwritten Kacha Bills (rough customer order notes).

Analyze the image carefully. The handwriting may be:
- In Hindi, Marathi, English, or mixed languages
- Messy or unclear in some parts
- Using local abbreviations (e.g., "kg", "pc", "dz" for dozen)
- Containing crossed-out items (ignore these)

Extract order information and return a JSON object:

{
    "status": "complete" or "incomplete",
    "data": {
        "customer": "customer name or null",
        "items": [
            {"name": "item name", "qty": quantity_or_null, "rate": price_or_null}
        ]
    },
    "missing_fields": ["list of missing information"]
}

Rules:
- Infer context from messy handwriting using common sense
- If customer name is in the image, extract it
- Extract ALL items visible, even if some details are missing
- For quantities: look for numbers before item names
- For rates/prices: look for ₹ symbol or "Rs" or numbers after "@" or "per"
- If you cannot read something clearly, set it to null
- Set status to "complete" ONLY if: customer AND all items have name, qty, and rate
- Set status to "incomplete" if ANY information is missing or unclear
- Return ONLY the JSON object
"""
    else:
        # Original prompt for audio/text with Hinglish translation
        system_prompt = """You are an order processing assistant for Indian businesses. Extract order information and return a JSON object with this structure:

{
    "status": "complete" or "incomplete",
    "data": {
        "customer": "customer name or null",
        "items": [
            {"name": "item name in ENGLISH", "qty": quantity_or_null, "rate": price_or_null}
        ]
    },
    "missing_fields": ["list of missing information"]
}

Rules:
- Set status to "complete" ONLY if you have: customer name AND all items have name, qty, and rate
- Set status to "incomplete" if ANY information is missing
- In missing_fields, list what's missing: "customer", "item_X_qty", "item_X_rate"
- For items, if rate or qty is missing, use null (not 0)
- Extract ALL items mentioned, even if incomplete
- **IMPORTANT**: Translate Hindi/Hinglish item names to English (e.g., 'ande' → 'Eggs', 'chawal' → 'Rice', 'doodh' → 'Milk')
- If the message is just a greeting (Hi, Hello, etc.) or not an order, return status: incomplete with empty items
- Return ONLY the JSON object
"""
    
    try:
        # Use the new google.genai API
        # Gemini 1.5 Flash is the default and best for this use case
        model_name = 'gemini-2.5-flash'
        
        # Prepare context if there's a pending order
        context = ""
        if pending_order:
            context = f"\n\nPrevious partial order: {json.dumps(pending_order)}\nUpdate this with new information from the current message."
        
        if input_type == 'image' and media_url:
            # Download the image with Twilio authentication
            print(f"📸 Downloading IMAGE from: {media_url}")
            print(f"🎨 MIME Type: {mime_type}")
            response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            print(f"Media Download Status: {response.status_code}")
            response.raise_for_status()
            
            # Save temporarily
            temp_image_path = '/tmp/order_image.jpg'
            with open(temp_image_path, 'wb') as f:
                f.write(response.content)
            
            # Read image file
            print("📤 Uploading image to Gemini for OCR...")
            with open(temp_image_path, 'rb') as f:
                image_data = f.read()
            
            # Generate content with image using new API
            result = client.models.generate_content(
                model=model_name,
                contents=[
                    system_prompt + context,
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type=mime_type or 'image/jpeg'
                    ),
                    "Extract the order information from this handwritten note/bill image."
                ]
            )
            
            # Clean up
            os.remove(temp_image_path)
            print("✅ OCR processing complete")
            
        elif input_type == 'audio' and media_url:
            # Download the audio file with Twilio authentication
            print(f"🎤 Downloading AUDIO from: {media_url}")
            response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            print(f"Media Download Status: {response.status_code}")
            response.raise_for_status()
            
            # Save temporarily
            temp_audio_path = '/tmp/order_audio.ogg'
            with open(temp_audio_path, 'wb') as f:
                f.write(response.content)
            
            # Read audio file
            print("📤 Uploading audio to Gemini...")
            with open(temp_audio_path, 'rb') as f:
                audio_data = f.read()
            
            # Generate content with audio using new API
            result = client.models.generate_content(
                model=model_name,
                contents=[
                    system_prompt + context,
                    types.Part.from_bytes(
                        data=audio_data,
                        mime_type='audio/ogg'
                    ),
                    "Extract the order information from this audio."
                ]
            )
            
            # Clean up
            os.remove(temp_audio_path)
            
        elif text_body:
            # Process text input
            print(f"📝 Processing TEXT: {text_body}")
            result = client.models.generate_content(
                model=model_name,
                contents=[
                    system_prompt + context,
                    f"Extract the order information from this message: {text_body}"
                ]
            )
        
        else:
            return {
                "status": "error",
                "message": "No input provided"
            }
        
        # Parse the response
        response_text = result.text.strip()
        print(f"Gemini response: {response_text}")
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Parse JSON
        parsed_response = json.loads(response_text)
        
        # Validate and enhance the response
        if parsed_response.get('status') == 'complete':
            # Double-check completeness
            data = parsed_response.get('data', {})
            items = data.get('items', [])
            
            # Reject if no items or customer
            if not data.get('customer') or not items or len(items) == 0:
                parsed_response['status'] = 'incomplete'
                if not data.get('customer'):
                    parsed_response['missing_fields'] = ['customer'] + parsed_response.get('missing_fields', [])
                if not items or len(items) == 0:
                    parsed_response['missing_fields'] = parsed_response.get('missing_fields', []) + ['items']
            
            # Check each item has name, qty, and rate
            for idx, item in enumerate(items):
                if not item.get('name') or item.get('qty') is None or item.get('rate') is None:
                    parsed_response['status'] = 'incomplete'
                    if 'items' not in parsed_response.get('missing_fields', []):
                        parsed_response['missing_fields'] = parsed_response.get('missing_fields', []) + ['item details']
        
        return parsed_response
        
    except Exception as e:
        print(f"❌ Error parsing order: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.route('/', methods=['GET'])
def home():
    """Welcome page to verify server is running"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BillBot - AI Invoice Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #1a237e; }
            .status { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .endpoint { background: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }
            code { background: #fff3e0; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🤖 BillBot Server</h1>
        <div class="status">
            <h2>✅ Server Status: Running</h2>
            <p>Your BillBot AI server is up and running!</p>
        </div>
        
        <h3>📱 WhatsApp Webhook Endpoint:</h3>
        <div class="endpoint">POST /whatsapp</div>
        
        <h3>🎯 Features:</h3>
        <ul>
            <li>📸 OCR for handwritten notes (Hindi/Marathi/English)</li>
            <li>🎤 Voice message processing</li>
            <li>📝 Text order extraction</li>
            <li>📄 Automated PDF invoice generation</li>
        </ul>
        
        <h3>🚀 Next Steps:</h3>
        <ol>
            <li>Run <code>ngrok http 5000</code> to expose this server</li>
            <li>Copy the ngrok HTTPS URL</li>
            <li>Set it as your Twilio WhatsApp webhook: <code>https://your-ngrok-url.ngrok.io/whatsapp</code></li>
            <li>Send a message to your Twilio WhatsApp number!</li>
        </ol>
        
        <p><small>Built with ❤️ using Google Gemini AI</small></p>
    </body>
    </html>
    """, 200


@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    """
    Handle incoming WhatsApp messages via Twilio webhook with conversation state management.
    """
    # Get form data from the incoming request
    incoming_msg = request.form.get('Body', '').strip()
    sender = request.form.get('From', '')
    media_url = request.form.get('MediaUrl0', None)
    
    # Log the incoming message
    print(f"\n{'='*60}")
    print(f"Received message from {sender}: {incoming_msg}")
    if media_url:
        print(f"Media URL: {media_url}")
    
    # Get or create user
    user = get_user(sender)
    if not user:
        user = create_user(sender)
        print(f"New user created: {sender}")
    
    print(f"User state: {user.get('state')}")
    
    # Handle special commands (reset, help, etc.)
    command = incoming_msg.lower().strip()
    
    # Greeting detection - cancel any pending orders
    greetings = ['hi', 'hello', 'hey', 'namaste', 'hola', 'sup', 'yo']
    if command in greetings:
        # If user has pending order, cancel it
        if user.get('state') in ['AWAITING_INFO', 'COLLECTING_ORDER']:
            update_user(sender, {
                'state': 'READY',
                'pending_order': None
            })
            resp = MessagingResponse()
            resp.message("👋 Hi! I've cancelled the previous incomplete order.\n\n📋 Send me a new order to create an invoice!")
            return str(resp), 200
        
        # If already READY, just greet
        if user.get('state') == 'READY':
            resp = MessagingResponse()
            resp.message("👋 Hello! Ready to create invoices.\n\n📋 Send me an order like:\n\"Bill for Ramesh: 10 Rice at ₹50\"")
            return str(resp), 200
    
    if command in ['reset', 'start over', 'restart', 'new']:
        # Reset user to NEW state for re-onboarding
        update_user(sender, {
            'state': 'NEW',
            'onboarding_step': 0,
            'company_details': {},
            'pending_order': None
        })
        resp = MessagingResponse()
        resp.message("🔄 Account reset! Let's start fresh.\n\nSend 'hi' to begin onboarding.")
        return str(resp), 200
    
    if command in ['help', '?']:
        help_msg = "📚 **BillBot Commands:**\n\n• Send an order to create invoice\n• 'reset' - Start onboarding again\n• 'help' - Show this message\n\n📸 You can also send images of handwritten bills!"
        resp = MessagingResponse()
        resp.message(help_msg)
        return str(resp), 200
    
    # STATE MACHINE: Handle different conversation states
    response_message = ""
    
    # ========== STATE: NEW USER ==========
    if user['state'] == 'NEW':
        update_user(sender, {
            'state': 'ONBOARDING',
            'onboarding_step': 1
        })
        response_message = "👋 Welcome to BillBot!\n\nI'll help you generate invoices instantly. First, let me get your company details.\n\n📝 What is your Company Name?"
        add_conversation_entry(sender, incoming_msg, response_message)
        
        # Return TwiML response for WhatsApp
        resp = MessagingResponse()
        resp.message(response_message)
        return str(resp), 200
    
    # ========== STATE: ONBOARDING ==========
    elif user['state'] == 'ONBOARDING':
        step = user.get('onboarding_step', 1)
        
        if step == 1:
            # Capture company name
            update_user(sender, {
                'company_details': {'name': incoming_msg},
                'onboarding_step': 2
            })
            response_message = f"✅ Company: {incoming_msg}\n\n📍 What is your company address? (Type 'skip' if you want to add it later)"
            
        elif step == 2:
            # Capture address (optional)
            if incoming_msg.lower() != 'skip':
                update_user(sender, {
                    'company_details': {'address': incoming_msg},
                    'onboarding_step': 3
                })
            else:
                update_user(sender, {'onboarding_step': 3})
            response_message = "🔢 What is your GSTIN number? (Type 'skip' if not applicable)"
        
        elif step == 3:
            # Capture GSTIN (optional)
            if incoming_msg.lower() != 'skip':
                update_user(sender, {
                    'company_details': {'gstin': incoming_msg},
                    'state': 'READY'
                })
            else:
                update_user(sender, {'state': 'READY'})
            
            response_message = "🎉 Setup complete! You're all set.\n\n📋 To create an invoice, just send me an order like:\n\n\"Bill for Ramesh Kirana:\n- 10 Rice bags at ₹50 each\n- 5 Oil bottles at ₹120 each\"\n\nTry it now!"
        
        add_conversation_entry(sender, incoming_msg, response_message)
        
        # Return TwiML response for WhatsApp
        resp = MessagingResponse()
        resp.message(response_message)
        return str(resp), 200
    
    # ========== STATE: READY or COLLECTING_ORDER ==========
    elif user['state'] in ['READY', 'COLLECTING_ORDER', 'AWAITING_INFO']:
        
        # Detect input type based on MediaContentType0
        media_content_type = request.form.get('MediaContentType0', '')
        input_type = 'text'  # Default
        mime_type = None
        
        if media_url and media_content_type:
            print(f"🔍 Detected MediaContentType0: {media_content_type}")
            
            # Check if it's an image
            if 'image' in media_content_type.lower():
                input_type = 'image'
                mime_type = media_content_type
                print(f"📸 IMAGE detected: {mime_type}")
            
            # Check if it's audio
            elif 'audio' in media_content_type.lower():
                input_type = 'audio'
                mime_type = media_content_type
                print(f"🎤 AUDIO detected: {mime_type}")
        
        # Parse the order with context and input type
        pending_order = user.get('pending_order')
        parse_result = parse_order(
            media_url=media_url,
            text_body=incoming_msg if not media_url else None,  # Only use text if no media
            pending_order=pending_order,
            input_type=input_type,
            mime_type=mime_type
        )
        
        print(f"Parse result: {parse_result}")
        
        # Handle parsing error
        if parse_result.get('status') == 'error':
            response_message = f"❌ Sorry, I couldn't understand that. Error: {parse_result.get('message')}\n\nPlease try again."
            add_conversation_entry(sender, incoming_msg, response_message)
            
            # Return TwiML response for WhatsApp
            resp = MessagingResponse()
            resp.message(response_message)
            return str(resp), 200
        
        # Handle incomplete order - ask for missing info
        elif parse_result.get('status') == 'incomplete':
            missing = parse_result.get('missing_fields', [])
            order_data = parse_result.get('data', {})
            
            # Save the partial order
            set_user_state(sender, 'AWAITING_INFO', pending_order=order_data)
            
            # Generate human-friendly message about what's missing
            response_message = "📝 I got some information, but I need a bit more:\n\n"
            
            if 'customer' in missing:
                response_message += "• Customer name\n"
            
            if 'items' in missing or 'item' in str(missing).lower():
                response_message += "• Item details (name, quantity, price)\n"
            
            for field in missing:
                if 'rate' in field.lower() and 'items' not in missing:
                    response_message += f"• Price/rate for some items\n"
                    break
            
            for field in missing:
                if 'qty' in field.lower() and 'items' not in missing:
                    response_message += f"• Quantity for some items\n"
                    break
            
            response_message += "\nPlease provide the missing details."
            
            add_conversation_entry(sender, incoming_msg, response_message)
            
            # Return TwiML response for WhatsApp
            resp = MessagingResponse()
            resp.message(response_message)
            return str(resp), 200
        
        # Handle complete order - generate invoice!
        elif parse_result.get('status') == 'complete':
            order_data = parse_result.get('data', {})
            
            try:
                # Get company details from database
                company_details = user.get('company_details', {})
                
                # Create a unique filename
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                customer_clean = order_data.get('customer', 'Unknown').replace(' ', '_')
                pdf_filename = f"invoice_{customer_clean}_{timestamp}.pdf"
                
                # Generate the PDF with company details
                print(f"Generating invoice: {pdf_filename}")
                generate_pdf(order_data, pdf_filename, company_details)
                
                # Create the full URL to the invoice
                invoice_url = f"{request.host_url}static/{pdf_filename}"
                print(f"Invoice URL: {invoice_url}")
                
                # Clear pending order and reset state
                set_user_state(sender, 'READY', pending_order=None)
                
                response_message = f"✅ Invoice generated successfully!\n\n🧾 Customer: {order_data.get('customer')}\n📥 Download: {invoice_url}"
                
                add_conversation_entry(sender, incoming_msg, response_message)
                
                # Return TwiML response for WhatsApp
                resp = MessagingResponse()
                resp.message(response_message)
                return str(resp), 200
                
            except Exception as e:
                print(f"Error generating invoice: {str(e)}")
                response_message = f"❌ Sorry, invoice generation failed: {str(e)}"
                add_conversation_entry(sender, incoming_msg, response_message)
                
                # Return TwiML error response for WhatsApp
                resp = MessagingResponse()
                resp.message(response_message)
                return str(resp), 200
    
    # Default fallback
    resp = MessagingResponse()
    resp.message('Unknown state')
    return str(resp), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)
