import requests
from bs4 import BeautifulSoup
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
import re

# URL a monitorear
URL = "https://fedepatin.org.co/resoluciones-artistico/#1738812804586-c49ea4e1-e022"
HASH_FILE = "last_hash.txt"
TEXT_FILE = "last_text.txt"

# Variables de correo desde GitHub Secrets
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")


def get_section_text():
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

    # Normalizar el texto: quitar espacios múltiples, saltos de línea, tabs
    section_text = re.sub(r"\s+", " ", section_text).strip()

    return section_text


def get_section_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def send_email(message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = "⚠️ Resoluciones Artístico actualizadas"
        msg["From"] = EMAIL_USER
        msg["To"] = TO_EMAIL

        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
        print("Correo enviado correctamente.")
    except Exception as e:
        print("Error enviando correo:", e)


def main():
    section_text = get_section_text()
    if section_text is None:
        print("No se pudo obtener el texto. Se cancela la ejecución.")
        return

    new_hash = get_section_hash(section_text)

    try:
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            old_hash = f.read().strip()
    except FileNotFoundError:
        old_hash = ""

    if new_hash != old_hash:
        send_email(f"La sección de resoluciones artísticas cambió: {URL}")

        # Guardar nuevo hash
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            f.write(new_hash)

        # Guardar el texto actual para comparar después
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(section_text)

        print("Cambio detectado y guardado en last_text.txt")
    else:
        print("No hubo cambios detectados.")


if __name__ == "__main__":
    main()
