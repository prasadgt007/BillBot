# BillBot — WhatsApp Invoicing Agent for Small Businesses

A multimodal AI agent that turns handwritten bills, voice notes, and text orders in Hindi, Marathi,
and English into GST-format invoices, entirely inside WhatsApp.

Built solo in 24 hours at the **AIBoomi Hackathon** (February 2026).

**[Watch the demo](https://drive.google.com/file/d/1DetR-IfN9p1njNY71FMreT0LXPDIJooS/view?usp=sharing)**:
a WhatsApp voice note and a photo of a handwritten bill, each turned into a finished invoice.

---

## The problem

Small distributors and shops in India take most orders over WhatsApp: a text, a voice note, or a
photo of a handwritten *kacha* bill, often in Hindi or Marathi. Their billing software only accepts
typed, structured input, so someone re-types every order to produce a GST invoice.

BillBot removes the re-typing. The owner forwards the order as it arrived and gets a PDF invoice back
in the same chat.

## How it works

```
WhatsApp message (photo / voice note / text)
        │
        ▼
Twilio WhatsApp API ──▶ Flask webhook (/whatsapp)
        │
        ▼
Conversation state ── new user? ──▶ onboarding: company name, address, GSTIN
        │
        ▼
Gemini (multimodal): read handwriting or audio, extract customer, items, quantities, rates,
translate item names to English
        │
        ├── fields missing? ──▶ ask a follow-up question, keep the partial order in state
        ▼
ReportLab: PDF invoice with GST breakdown and a Code128 barcode
        │
        ▼
Download link sent back on WhatsApp
```

| Capability | Detail |
|---|---|
| Inputs | Photos of handwritten bills, voice notes, free-form text |
| Languages | Hindi, Marathi, English (including mixed Hinglish) |
| Missing information | Asks for missing prices or quantities and completes the order on the next reply |
| Invoice | Seller details and GSTIN, itemised table, CGST + SGST, grand total, unique invoice number, barcode |
| Commands | `reset`, `help` |

## Tech stack

Python · Flask · Google Gemini (`google-genai`) · Twilio WhatsApp API · ReportLab · ngrok (local webhook)

## Limitations

This is a hackathon MVP. A production version would need:

- **Real tax logic.** GST is fixed at 18% (9% CGST + 9% SGST). It does not handle other GST slabs,
  inter-state IGST, or HSN codes.
- **A database.** User state and order history live in a local JSON file.
- **Hosted invoices.** PDFs are served from the Flask `static/` folder through the ngrok tunnel.

## Next

Adapting BillBot for Chartered Accountant (CA) firms, which handle GST filing for many small
businesses.

---

## Run locally

**Prerequisites:** Python 3.11+, a [Google Gemini API key](https://aistudio.google.com/app/apikey),
a [Twilio](https://console.twilio.com) account with the WhatsApp Sandbox, and [ngrok](https://ngrok.com).

```bash
git clone https://github.com/prasadgt007/BillBot.git
cd BillBot
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # add your Gemini and Twilio keys
python app.py                      # runs on http://127.0.0.1:5001
```

In a second terminal, expose the server and connect it to WhatsApp:

```bash
ngrok http 5001
```

In the Twilio Console, open **Messaging → Try it out → WhatsApp Sandbox**, set the
"When a message comes in" webhook to `https://<your-ngrok-url>/whatsapp` with method **POST**, and
join the sandbox from your phone.

**Test without WhatsApp:**

```bash
curl -X POST http://localhost:5001/whatsapp \
     -d "Body=Bill for Ramesh: 10 Rice at 50, 5 Oil at 120" \
     -d "From=whatsapp:+919876543210"
```

## Project structure

```
app.py           Flask webhook, conversation state machine, Gemini extraction
db_manager.py    JSON-file storage for users, company details, pending orders
invoice_gen.py   PDF invoice generation with GST breakdown and barcode
requirements.txt
.env.example
```

---

© 2026 Prasad Takwane. All rights reserved.
