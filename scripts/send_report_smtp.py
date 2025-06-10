#!/usr/bin/env python3
# Skrypt: send_report_smtp.py
# Wysyła raport PDF na e-mail przez SMTP
import os
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))
except ImportError:
    print("[!] Brak biblioteki python-dotenv. Zainstaluj ją: pip install --break-system-packages python-dotenv")
    # Skrypt działa dalej, jeśli zmienne są już w środowisku

import smtplib
from email.message import EmailMessage

# Pobierz dane z ENV lub .env
PDF_FILE = os.environ.get("PDF_FILE", "./raport.pdf")
RECIPIENT = os.environ.get("RECIPIENT", "bso-projekt@outlook.com")
SENDER = os.environ.get("SENDER", "bso-projekt@outlook.com")
MTA_HOST = os.environ.get("MTA_HOST", "smtp.office365.com")
MTA_PORT = int(os.environ.get("MTA_PORT", 587))
MTA_USER = os.environ.get("MTA_USER", SENDER)
MTA_PASS = os.environ.get("MTA_PASSWORD", "")
SUBJECT = "Automatyczny raport GVM"
BODY = "W załączniku przesyłam najnowszy raport PDF z Greenbone."

if not os.path.isfile(PDF_FILE):
    print(f"Brak pliku PDF: {PDF_FILE}")
    exit(1)

msg = EmailMessage()
msg["Subject"] = SUBJECT
msg["From"] = SENDER
msg["To"] = RECIPIENT
msg.set_content(BODY)

with open(PDF_FILE, "rb") as f:
    msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(PDF_FILE))

try:
    with smtplib.SMTP(MTA_HOST, MTA_PORT) as server:
        server.starttls()
        server.login(MTA_USER, MTA_PASS)
        server.send_message(msg)
    print(f"[✓] Raport wysłany na {RECIPIENT}")
except Exception as e:
    print(f"[✗] Błąd wysyłki: {e}")
    exit(2)
