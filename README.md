# 🤖 BillBot - AI-Powered Invoice Generator

> **Transform handwritten bills, voice messages, or text into professional GST invoices via WhatsApp**

[Product Demo](https://drive.google.com/file/d/1DetR-IfN9p1njNY71FMreT0LXPDIJooS/view?usp=sharing)

---

## 📖 Overview

**BillBot** is an intelligent WhatsApp-based invoice generation system designed for small businesses, distributors, and vendors across India. It solves the critical problem of converting rough handwritten bills (Kacha Bills) and verbal orders into professional, GST-compliant invoices instantly.

### The Problem We Solve

Small business owners often:
- Receive orders via WhatsApp as text, voice notes, or photos of handwritten notes
- Waste hours manually creating invoices in Excel or accounting software
- Face language barriers (orders in Hindi, Marathi, Hinglish)
- Struggle with messy handwriting and incomplete information

**BillBot automates this entire workflow with AI-powered OCR, natural language processing, and intelligent conversation management.**

---

## 💡 The Idea

BillBot acts as a conversational AI assistant that:

1. **Onboards vendors** by collecting company details (name, address, GSTIN)
2. **Accepts orders** in 3 formats:
   - 📸 **Photos of handwritten bills** (supports Hindi, Marathi, English)
   - 🎤 **Voice messages** (natural speech)
   - 📝 **Text messages** (any format)
3. **Extracts data** using Google Gemini 2.5 Flash AI with advanced OCR
4. **Handles missing info** by asking follow-up questions intelligently
5. **Generates professional PDF invoices** with GST calculations and barcodes
6. **Delivers via WhatsApp** with instant download links

---

## 🎥 Product Demo

Watch BillBot in action: **[View Demo Video](https://drive.google.com/file/d/1DetR-IfN9p1njNY71FMreT0LXPDIJooS/view?usp=sharing)**

---

## ✨ Key Features

### 🧠 **Intelligent AI Processing**
- **Multi-language OCR**: Reads handwritten Hindi, Marathi, and English
- **Context awareness**: Understands messy handwriting and local abbreviations
- **Smart translation**: Converts Hindi items to English for professional invoices
- **Missing field detection**: Asks for incomplete information conversationally

### 💬 **Conversational State Machine**
- **Onboarding flow**: Guides users through company setup
- **Memory**: Remembers previous orders and customer context
- **Multi-turn conversations**: Handles incomplete orders gracefully
- **Command support**: `reset`, `help`, greeting detection

### 📄 **Professional Invoice Generation**
- **GST compliance**: Auto-calculates 9% CGST + 9% SGST
- **Barcode integration**: Code128 barcodes for tracking
- **Clean layout**: Professional PDF with company branding
- **Download links**: Instant access via WhatsApp

### 🔒 **Secure & Scalable**
- **Environment-based secrets**: API keys in `.env` file
- **Twilio authentication**: Secure media downloads
- **JSON database**: Fast, hackathon-friendly storage
- **Ngrok tunneling**: Easy local testing

---

## 🛠️ Technology Stack

### **Backend Framework**
- **Flask** (3.1.0) - Lightweight Python web framework
- **Python 3.11** - Core language

### **AI/ML Engine**
- **Google Gemini 2.5 Flash** - Multimodal AI for OCR, NLP, and data extraction
- **google-generativeai** - Official Gemini SDK

### **Communication**
- **Twilio WhatsApp API** (9.4.0) - Message handling and media downloads
- **Ngrok** - Secure tunneling for webhooks

### **PDF Generation**
- **ReportLab** (4.2.5) - Professional invoice PDFs with tables, colors, and barcodes

### **Data Management**
- **JSON** - Lightweight database for user state and conversation history
- **python-dotenv** (1.0.0) - Environment variable management

### **Deployment**
- **Flask Development Server** (Port 5001)
- **Ngrok Custom Domain** - Public HTTPS endpoint

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd BillBot
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

**Get API Keys:**
- Google Gemini: https://aistudio.google.com/app/apikey
- Twilio: https://console.twilio.com

### 4. Run the Application

```bash
python app.py
```

Server starts on `http://127.0.0.1:5001`

### 5. Expose with Ngrok

```bash
ngrok http --domain=your-custom-domain.ngrok-free.dev 5001
```

### 6. Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com) → WhatsApp Sandbox
2. Set webhook URL: `https://your-domain.ngrok-free.dev/whatsapp`
3. Method: **POST**
4. Save configuration

---

## 💬 Usage Examples

### First Time Setup (Onboarding)

```
You: Hi
Bot: 👋 Welcome to BillBot! What is your Company Name?

You: Sharma Distributors
Bot: ✅ Company: Sharma Distributors
     📍 What is your company address?

You: 123 Market Street, Mumbai
Bot: 🔢 What is your GSTIN number? (Type 'skip' if not applicable)

You: 29ABCDE1234F1Z5
Bot: 🎉 Setup complete! Send me an order to create an invoice.
```

### Creating Invoices

#### 📸 **Image Input (Handwritten Bill)**
- Take photo of Kacha Bill in Hindi/Marathi/English
- Send via WhatsApp
- Bot extracts customer, items, quantities, prices
- Generates PDF with English translations

#### 🎤 **Voice Message**
```
Record: "Bill for Generic Store: 2 Rice bags at 50 rupees, 
         4 Flour bags at 100, and 5 Garam Masala at 20"

Bot: ✅ Invoice generated successfully!
     🧾 Customer: Generic Store
     📥 Download: [PDF Link]
```

#### 📝 **Text Order**
```
You: Bill for Raju Fruits:
     10 Apples @ ₹50/kg
     5 Bananas @ ₹20/dozen

Bot: ✅ Invoice generated successfully!
     📥 Download: [PDF Link]
```

### Handling Incomplete Orders

```
You: Bill for Ashish - 10 apples

Bot: 📝 I need a bit more:
     • Price/rate for some items
     
You: Apples are 120 for 2 pieces

Bot: ✅ Invoice generated successfully!
```

---

## 📁 Project Structure

```
BillBot/
├── app.py              # Main Flask application & state machine
├── db_manager.py       # JSON database operations
├── invoice_gen.py      # PDF invoice generation with barcodes
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not in Git)
├── .env.example        # Template for environment setup
├── .gitignore          # Git exclusions
├── user_data.json      # Auto-generated user database
├── static/             # Generated PDF invoices
│   └── invoice_*.pdf   # Customer invoices
└── README.md           # This file
```

---

## 🧪 Local Testing (Without WhatsApp)

Use cURL to test locally:

```bash
# New user onboarding
curl -X POST http://localhost:5001/whatsapp \
     -d "Body=Hi" \
     -d "From=whatsapp:+919876543210"

# Text order
curl -X POST http://localhost:5001/whatsapp \
     -d "Body=Bill for Ramesh: 10 Rice at 50, 5 Oil at 120" \
     -d "From=whatsapp:+919876543210"

# Simulate image upload
curl -X POST http://localhost:5001/whatsapp \
     -d "MediaUrl0=https://example.com/bill.jpg" \
     -d "MediaContentType0=image/jpeg" \
     -d "From=whatsapp:+919876543210"
```

---

## 📊 Invoice Features

Generated PDFs include:
- ✅ **Company branding** with name, address, GSTIN
- ✅ **Unique invoice number** with timestamp
- ✅ **Itemized table** with quantities and rates
- ✅ **GST breakdown** (9% CGST + 9% SGST)
- ✅ **Grand total** calculation
- ✅ **Code128 barcode** for tracking
- ✅ **Professional styling** with colors and layout

---

## 🔒 Security Best Practices

- **Environment variables**: All API keys stored in `.env` (gitignored)
- **Twilio authentication**: Media downloads use Basic Auth
- **HTTPS only**: Ngrok provides secure tunneling
- **Input validation**: Gemini handles malicious inputs safely

---

## 🤝 Contributing

This is a hackathon project! Contributions welcome:

### Ideas for Enhancement
- 🌐 Multi-language invoice support
- 🖼️ Company logo upload
- 🗄️ Excel integration
- 📈 Sales dashboard and analytics
- 📧 Email invoice delivery
- 🔄 Integration with accounting software

---

### Common Issues

**Issue**: WhatsApp not receiving replies  
**Solution**: Check Ngrok tunnel is active and Twilio webhook is configured correctly

**Issue**: 401 Unauthorized on media download  
**Solution**: Verify `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in `.env`

### Debugging

- Check Flask logs in terminal
- View Ngrok dashboard at `http://localhost:4040`
- Inspect `user_data.json` for conversation history

---

🎥 **[Watch Demo](https://drive.google.com/file/d/1DetR-IfN9p1njNY71FMreT0LXPDIJooS/view?usp=sharing)**
