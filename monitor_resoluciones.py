import requests
from bs4 import BeautifulSoup
import hashlib
import smtplib
from email.mime.text import MIMEText
import os

# URL a monitorear
URL = "https://fedepatin.org.co/resoluciones-artistico/#1738812804586-c49ea4e1-e022"
HASH_FILE = "last_hash.txt"

# Configuración de correo (Yahoo) → desde GitHub Secrets
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")

def get_section_hash():
    try:
        response = requests.get(URL, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print("Error descargando la página:", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.select_one("#pg-1738812804586-c49ea4e1-e022")

    if not section:
        section_text = soup.get_text()
    else:
        section_text = section.get_text()

    return hashlib.sha256(section_text.encode("utf-8")).hexdigest()

def send_email(message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = "⚠️ Resoluciones Artístico actualizadas"
        msg["From"] = EMAIL_USER
        msg["To"] = TO_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
        print("Correo enviado correctamente.")
    except Exception as e:
        print("Error enviando correo:", e)

def main():
    new_hash = get_section_hash()
    if new_hash is None:
        print("No se pudo obtener el hash. Se cancela la ejecución.")
        return

    try:
        with open(HASH_FILE, "r") as f:
            old_hash = f.read().strip()
    except FileNotFoundError:
        old_hash = ""

    if new_hash != old_hash:
        send_email(f"La sección de resoluciones artísticas cambió: {URL}")
        with open(HASH_FILE, "w") as f:
            f.write(new_hash)
    else:
        print("No hubo cambios detectados.")

if __name__ == "__main__":
    main()
