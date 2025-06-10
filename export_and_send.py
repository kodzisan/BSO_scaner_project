#!/usr/bin/env python3
import os, base64, smtplib
from email.message import EmailMessage
from lxml import etree
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp

# ─── KONFIGURACJA z env ────────────────────────────────────
REPORT_ID     = os.environ["REPORT_ID"]
GVM_USER      = os.environ["GVM_USER"]
GVM_PASS      = os.environ["GVM_PASS"]
RECIPIENT     = os.environ["RECIPIENT"]
SENDER        = os.environ["SENDER"]
# PDF format ID
PDF_FORMAT_ID = "c402cc3e-b531-11e1-9163-406186ea4fc5"
SOCKET_PATH   = "/run/gvmd/gvmd.sock"

# SMTP (Office365)
MTA_HOST      = os.environ["MTA_HOST"]
MTA_PORT      = int(os.environ.get("MTA_PORT", 587))
MTA_USER      = os.environ["MTA_USER"]
MTA_PASS      = os.environ["MTA_PASSWORD"]
USE_TLS       = os.environ.get("MTA_TLS", "off").lower() in ("on","1","true")

# Ścieżka wyjściowa PDF w kontenerze
PDF_PATH      = f"/tmp/{REPORT_ID}.pdf"

def fetch_pdf():
    conn = UnixSocketConnection(path=SOCKET_PATH)
    with Gmp(connection=conn) as gmp:
        gmp.authenticate(GVM_USER, GVM_PASS)
        rsp = gmp.get_report(
    report_id=REPORT_ID,
    report_format_id=PDF_FMT,
    details=True
)

    root = etree.fromstring(rsp.encode()) if isinstance(rsp, str) else rsp
    node = root.find(".//report_format/content")
    if node is None or not node.text:
        raise RuntimeError("Brak danych PDF w odpowiedzi")
    pdf_data = base64.b64decode(node.text)
    with open(PDF_PATH, "wb") as f:
        f.write(pdf_data)
    print(f"[✓] Raport zapisany w kontenerze jako {PDF_PATH}")

def send_mail():
    msg = EmailMessage()
    msg["Subject"] = "Automatyczny raport GVM"
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT
    msg.set_content("W załączniku przesyłam najnowszy raport PDF z Greenbone.")

    with open(PDF_PATH, "rb") as f:
        msg.add_attachment(f.read(),
                           maintype="application",
                           subtype="pdf",
                           filename=os.path.basename(PDF_PATH))

    with smtplib.SMTP(MTA_HOST, MTA_PORT) as s:
        if USE_TLS:
            s.starttls()
        s.login(MTA_USER, MTA_PASS)
        s.send_message(msg)

    print(f"[✓] Email wysłany do {RECIPIENT}")

if __name__ == "__main__":
    fetch_pdf()
    send_mail()
