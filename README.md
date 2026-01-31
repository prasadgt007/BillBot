# 🤖 BillBot - AI-Powered Invoice Generator

An intelligent WhatsApp bot that converts handwritten notes, voice messages, or text into professional GST invoices.

## ✨ Features

- 📸 **OCR for Handwritten Notes** - Upload photos of rough bills (Kacha Bills) in Hindi/Marathi/English
- 🎤 **Voice Message Support** - Speak your orders naturally
- 📝 **Text Order Processing** - Type orders in any format
- 🧠 **Conversational Memory** - Remembers your company details and context
- 📄 **Professional PDF Invoices** - Auto-generates GST invoices with 9% CGST + 9% SGST
- 🏪 **Multi-Customer Support** - Handle orders for different customers

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export GOOGLE_API_KEY="your-gemini-api-key-here"
```

Get your API key from: https://aistudio.google.com/app/apikey

### 3. Run the App

```bash
python app.py
```

The app will start on `http://localhost:5000`

## 📱 WhatsApp Integration

### Using Twilio + Ngrok

1. **Start Ngrok:**
   ```bash
   ngrok http 5000
   ```

2. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

3. **Configure Twilio Webhook:**
   - Go to Twilio Console → WhatsApp Sandbox
   - Set webhook URL: `https://abc123.ngrok.io/whatsapp`
   - Method: POST

4. **Test it!**
   - Send "Hi" to your Twilio WhatsApp number
   - Complete onboarding
   - Send a handwritten bill photo or text order

## 💬 How to Use

### First Time Setup

```
You: Hi
Bot: Welcome to BillBot! What is your Company Name?

You: Sharma Distributors
Bot: What is your company address? (Type 'skip' to add later)

You: 123 Market Street, Mumbai
Bot: What is your GSTIN number? (Type 'skip' if not applicable)

You: 29ABCDE1234F1Z5
Bot: Setup complete! Send me an order to create an invoice.
```

### Creating Invoices

**Option 1: Send a Photo 📸**
- Take a photo of your handwritten bill
- Send it via WhatsApp
- Bot extracts everything and generates PDF

**Option 2: Voice Message 🎤**
- Record: "Bill for Ramesh: 10 Rice bags at 50 rupees each, 5 Oil bottles at 120"
- Bot processes and creates invoice

**Option 3: Text Message 📝**
```
Bill for Ramesh Kirana:
- 10 Rice bags @ ₹50
- 5 Oil bottles @ ₹120
```

### Missing Information

If you forget something, the bot asks:

```
You: Bill for Suresh - 20 boxes of Tea
Bot: I need a bit more:
     • Price/rate for some items
     
You: Tea is 30 per box
Bot: ✅ Invoice generated!
```

## 📁 Project Structure

```
billbot/
├── app.py              # Main Flask app with state machine
├── db_manager.py       # JSON database operations
├── invoice_gen.py      # PDF invoice generator
├── requirements.txt    # Dependencies
├── user_data.json     # Auto-created user database
└── static/            # Generated PDF invoices
```

## 🔧 Tech Stack

- **Flask** - Web framework
- **Google Gemini 1.5 Flash** - AI/OCR engine
- **ReportLab** - PDF generation
- **Twilio** - WhatsApp integration
- **JSON** - Database (hackathon-friendly!)

## 🧪 Testing Locally

Use cURL to simulate Twilio:

```bash
# Onboarding
curl -X POST http://localhost:5000/whatsapp \
     -d "Body=Hello" \
     -d "From=whatsapp:+919876543210"

# Text Order
curl -X POST http://localhost:5000/whatsapp \
     -d "Body=Bill for Ramesh: 10 Rice at 50, 5 Oil at 120" \
     -d "From=whatsapp:+919876543210"

# Image Order
curl -X POST http://localhost:5000/whatsapp \
     -d "MediaUrl0=https://example.com/bill.jpg" \
     -d "MediaContentType0=image/jpeg" \
     -d "From=whatsapp:+919876543210"
```

## 📊 Invoice Features

- Professional layout with company branding
- Itemized table with quantities and rates
- Auto-calculated GST (9% CGST + 9% SGST)
- Grand total calculation
- Unique invoice numbers
- Downloadable PDF links

## 🤝 Contributing

This is a hackathon project! Feel free to:
- Add support for more languages
- Implement logo upload
- Add database persistence (SQL/MongoDB)
- Create a dashboard

## 📄 License

MIT License - Built for Hackathon 2026

## 🙋 Support

For issues or questions, check the conversation logs in your terminal or Ngrok dashboard.

---

**Built with ❤️ using Google Gemini AI**
