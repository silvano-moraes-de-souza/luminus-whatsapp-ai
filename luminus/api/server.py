# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: server.py
# DESCRIÇÃO: Servidor principal (Webhook Receiver)
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================

import sys
import os
import re
import time
import logging
from collections import defaultdict
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luminus.core.router import MessageRouter
from luminus.core.tasks import process_whatsapp_message
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3
        )
    ]
)

EVO_API_URL = os.getenv("EVOLUTION_API_URL")
EVO_API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

rate_limit_store = defaultdict(list)

def log_info(msg: str) -> None:
    logging.info(msg)
    print(msg, flush=True)

def _get_client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"

def sanitize_input(text: str, max_length: int = 5000) -> str:
    if not text: return ""
    text = text[:max_length]
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()

def verify_webhook_auth() -> bool:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "): return False
    return auth_header[7:] == os.getenv("WEBHOOK_SECRET")

@app.route("/webhook", methods=["POST"])
def webhook():
    if not verify_webhook_auth():
        return jsonify({"status": "unauthorized"}), 401

    data = request.json
    try:
        msg_data = data.get("data", {})
        if not isinstance(msg_data, dict): return jsonify({"status": "ignored"}), 200

        sender = msg_data.get("key", {}).get("remoteJid")
        from_me = msg_data.get("key", {}).get("fromMe", False)
        
        if from_me or not sender or sender.endswith("@g.us"):
            return jsonify({"status": "ignored"}), 200

        push_name = msg_data.get("pushName", "Contato")
        is_audio = bool(msg_data.get("message", {}).get("audioMessage"))
        
        message_text = msg_data.get("message", {}).get("conversation") or \
                       msg_data.get("message", {}).get("extendedTextMessage", {}).get("text") or \
                       msg_data.get("message", {}).get("text")
        
        message_text = sanitize_input(message_text)
        if is_audio and not message_text:
            message_text = "[Áudio]"

        if not message_text:
            return jsonify({"status": "empty"}), 200

        log_info(f"RECEBIDO: {sender} -> {message_text}")
        
        # Enfileira para processamento assíncrono
        process_whatsapp_message.delay(sender, message_text, push_name, is_audio)
        
        return jsonify({"status": "queued"}), 200

    except Exception as e:
        logging.error(f"ERRO WEBHOOK: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
