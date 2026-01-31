import json
import os
from datetime import datetime

DB_FILE = 'user_data.json'


def load_database():
    """Load the user database from JSON file."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Corrupted database file. Creating new one.")
            return {}
    return {}


def save_database(db):
    """Save the database to JSON file."""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)


def get_user(phone_number):
    """
    Get user data by phone number.
    
    Args:
        phone_number (str): WhatsApp phone number (e.g., 'whatsapp:+1234567890')
    
    Returns:
        dict: User data or None if user doesn't exist
    """
    db = load_database()
    return db.get(phone_number)


def create_user(phone_number):
    """
    Create a new user entry.
    
    Args:
        phone_number (str): WhatsApp phone number
    
    Returns:
        dict: Newly created user data
    """
    db = load_database()
    
    user_data = {
        'phone': phone_number,
        'created_at': datetime.now().isoformat(),
        'state': 'NEW',  # NEW, ONBOARDING, READY, COLLECTING_ORDER, AWAITING_INFO
        'onboarding_step': 0,  # Track onboarding progress
        'company_details': {
            'name': None,
            'address': None,
            'gstin': None,
            'logo_path': None
        },
        'pending_order': None,  # Temporary storage for incomplete orders
        'conversation_history': []
    }
    
    db[phone_number] = user_data
    save_database(db)
    
    return user_data


def update_user(phone_number, updates):
    """
    Update user data.
    
    Args:
        phone_number (str): WhatsApp phone number
        updates (dict): Dictionary of fields to update
    
    Returns:
        dict: Updated user data
    """
    db = load_database()
    
    if phone_number not in db:
        db[phone_number] = create_user(phone_number)
    
    # Merge updates
    for key, value in updates.items():
        if key == 'company_details' and isinstance(value, dict):
            # Merge company details instead of replacing
            db[phone_number]['company_details'].update(value)
        else:
            db[phone_number][key] = value
    
    db[phone_number]['updated_at'] = datetime.now().isoformat()
    save_database(db)
    
    return db[phone_number]


def set_user_state(phone_number, state, pending_order=None):
    """
    Update user's conversation state.
    
    Args:
        phone_number (str): WhatsApp phone number
        state (str): NEW, ONBOARDING, READY, COLLECTING_ORDER, AWAITING_INFO
        pending_order (dict, optional): Order data to store temporarily
    """
    updates = {'state': state}
    if pending_order is not None:
        updates['pending_order'] = pending_order
    
    return update_user(phone_number, updates)


def add_conversation_entry(phone_number, message, response):
    """
    Add a conversation entry for context (optional, for debugging).
    
    Args:
        phone_number (str): WhatsApp phone number
        message (str): User's message
        response (str): Bot's response
    """
    user = get_user(phone_number)
    if not user:
        user = create_user(phone_number)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'response': response
    }
    
    # Keep only last 10 conversations to avoid bloat
    history = user.get('conversation_history', [])
    history.append(entry)
    history = history[-10:]  # Keep last 10
    
    update_user(phone_number, {'conversation_history': history})


def is_onboarding_complete(phone_number):
    """
    Check if user has completed onboarding.
    
    Args:
        phone_number (str): WhatsApp phone number
    
    Returns:
        bool: True if company name is set (minimum requirement)
    """
    user = get_user(phone_number)
    if not user:
        return False
    
    company_name = user.get('company_details', {}).get('name')
    return company_name is not None and company_name.strip() != ''
