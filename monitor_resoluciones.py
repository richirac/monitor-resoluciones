import requests
from bs4 import BeautifulSoup
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
import re

URL = "https://fedepatin.org.co/resoluciones-artistico/#1738812804586-c49ea4e1-e022"
HASH_FILE = "last_hash.txt"
TEXT_FILE = "last_text.txt"

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def get_section_text():
    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error al acceder a la página: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.find("div", {"id": "1738812804586-c49ea4e1-e022"})
    if not section:
        print("⚠️ No se encontró la sección esperada en la página")
        return ""

    section_text = section.get_text(separator=" ", strip=True)
    section_text = re.sub(r"\s+", " ", section_text).strip()
    return section_text

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def send_email(subject, body):
    if not (EMAIL_FROM and EMAIL_TO and EMAIL_PASS):
        print("⚠️ Configuración de correo no encontrada en los secrets")
        return
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        print("📧 Correo enviado correctamente")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

def main():
    section_text = get_section_text()

    # 🔑 Siempre guardar last_text.txt aunque esté vacío
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(section_text)

    new_hash = compute_hash(section_text)

    old_hash = None
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            old_hash = f.read().strip()

    if old_hash != new_hash:
        print("🔔 Cambio detectado en la página")
        send_email("Cambio detectado en Resoluciones Artístico", "Se detectó un cambio en la página.")
        with open(HASH_FILE,_
