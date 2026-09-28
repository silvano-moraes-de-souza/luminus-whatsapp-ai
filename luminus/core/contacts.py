# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: contacts.py
# DESCRIÇÃO: Funções compartilhadas de whitelist de contatos
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.0
# ================================================================

import os
import json
import logging

ALLOWED_NUMBERS: list[str] = []
ALLOWED_NAMES: list[str] = []


def load_allowed_contacts() -> tuple[list[str], list[str]]:
    global ALLOWED_NUMBERS, ALLOWED_NAMES
    try:
        contacts = os.getenv("ALLOWED_CONTACTS", "{}")
        data = json.loads(contacts)
        ALLOWED_NUMBERS = [str(n).replace("@s.whatsapp.net", "").replace("@s.whatsapp_net", "") for n in data.get("numbers", [])]
        ALLOWED_NAMES = data.get("names", [])
    except Exception:
        pass
    return ALLOWED_NUMBERS, ALLOWED_NAMES


def is_contact_allowed(user_id: str, sender_name: str) -> bool:
    numbers, names = load_allowed_contacts()
    if not numbers and not names:
        return True

    user_clean = user_id.replace("@s.whatsapp.net", "").replace("@s.whatsapp_net", "")
    for num in numbers:
        if user_clean == num or user_clean.endswith(num):
            return True
    for name in names:
        if name.lower() == sender_name.lower():
            return True
    return False
