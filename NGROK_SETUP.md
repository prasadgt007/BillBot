# 🚀 BillBot - Ngrok + WhatsApp Setup Guide

## ✅ Your System is Ready!

**Working Configuration:**
- ✅ Flask server on port 5001
- ✅ `google.genai` package installed
- ✅ Model: `gemini-2.5-flash`
- ✅ PDF generation tested and working

---

## 📱 Step 1: Start Ngrok

Open a **new terminal** and run:

```bash
ngrok http 5001
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:5001
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

---

## 🔗 Step 2: Configure Twilio WhatsApp Sandbox

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Click **"Try WhatsApp"** or go to **Messaging → Try it out → Send a WhatsApp message**
3. Find your **"Sandbox Settings"** or **"Webhook Configuration"**
4. Set the webhook URL:
   ```
   https://abc123.ngrok-free.app/whatsapp
   ```
   (Replace `abc123` with your ngrok subdomain)
5. Set method to **POST**
6. Save configuration

---

## 💬 Step 3: Connect Your WhatsApp

1. Send the join code to the Twilio number (shown in the sandbox):
   ```
   join <your-sandbox-code>
   ```
   Example: `join happy-dog-1234`

2. You'll receive a confirmation message

---

## 🎯 Step 4: Test BillBot!

### Test 1: Onboarding
```
Hi
```
Bot will ask for company details.

### Test 2: Text Order
```
Bill for Ramesh Kirana:
- 10 Rice bags @ ₹50
- 5 Oil bottles @ ₹120
```

### Test 3: Handwritten Bill (OCR)
1. Write a sample bill on paper (Hindi/English/Marathi)
2. Take a photo
3. Send the photo via WhatsApp
4. Bot will extract and generate PDF!

---

## 🐛 Debugging

Watch your terminal logs:
- **Ngrok terminal**: Shows incoming HTTP requests
- **Flask terminal**: Shows BillBot processing logs

Look for:
```
📸 IMAGE detected: image/jpeg
📤 Uploading image to Gemini for OCR...
✅ OCR processing complete
```

---

## 📊 Check Generated Invoices

PDFs are saved in:
```
/Users/pgt/Antigravity Projects/static/
```

Download URL format:
```
https://abc123.ngrok-free.app/static/invoice_CustomerName_20260131_123456.pdf
```

---

## 🎉 You're Ready for the Hackathon!

**Features to Demo:**
- 📸 Upload handwritten bills (Kacha Bills)
- 🎤 Send voice orders (if Twilio supports audio)
- 📝 Type orders naturally
- 🧾 Instant GST invoices with download links
- 🧠 Conversational memory (remembers your company)
- ❓ Smart follow-ups for missing info

Good luck! 🚀
