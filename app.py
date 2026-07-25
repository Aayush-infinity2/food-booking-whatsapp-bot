from flask import Flask, request
from dotenv import load_dotenv
import os
import hashlib
import hmac
from chatbot import send_whatsapp_message
from services.conversation_service import process_message
from routes.admin import admin_bp
from routes.order import orders_bp
from routes.student import student_bp
from utils.badge import status_badge
from utils.formatter import *
# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")


# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)
app.jinja_env.globals.update(

    status_badge=status_badge,

    format_currency=format_currency,

    format_datetime=format_datetime,

    mask_phone=mask_phone
)
app.register_blueprint(orders_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)
app.secret_key = os.getenv("SECRET_KEY")
@app.route("/")
def home():
    return "WhatsApp Bot Running 🚀"


# -----------------------------------
# Meta Webhook Verification
# -----------------------------------
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # Ignore manual browser visits
    if mode is None:
        return "Webhook is running!", 200

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Meta Verified Successfully")
        return challenge, 200

    return "Verification Failed", 403


# -----------------------------------
# Receive Messages
# -----------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():

    signature = request.headers.get("X-Hub-Signature-256")
    app_secret = os.getenv("APP_SECRET")
    if app_secret:
        expected = "sha256=" + hmac.new(
            app_secret.encode(), request.get_data(), hashlib.sha256
        ).hexdigest()
        if not signature or not hmac.compare_digest(signature, expected):
            return "Invalid signature", 403

    data = request.get_json(silent=True) or {}
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                if message.get("type") != "text":
                    continue

                sender = message.get("from")
                text = message.get("text", {}).get("body", "")
                if not sender or not text:
                    continue

                try:
                    reply = process_message(sender, text)
                    send_whatsapp_message(sender, reply)
                except Exception:
                    app.logger.exception("Unable to process WhatsApp message")

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    # WhatsApp Cloud API must reach this local server through a public HTTPS URL.
    # Start ngrok automatically when a token is configured; set RUN_NGROK=false
    # only when running behind another public reverse proxy.
    if NGROK_AUTH_TOKEN and os.getenv("RUN_NGROK", "true").lower() == "true":
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
            public_url = (
                ngrok.connect(5000, domain=NGROK_DOMAIN)
                if NGROK_DOMAIN
                else ngrok.connect(5000)
            )
            print(f"Webhook callback URL: {public_url.public_url}/webhook")
        except OSError as error:
            print(f"Ngrok could not start: {error}")
            print("The dashboard remains available, but WhatsApp cannot reach this server until ngrok is allowed.")
    elif not NGROK_AUTH_TOKEN:
        print("Ngrok is not configured; WhatsApp webhooks cannot reach this local server.")
    app.run(port=5000, debug=True, use_reloader=False)
