# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: test_router.py
# DESCRIÇÃO: Testes básicos do roteador de mensagens
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.1
# ================================================================

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "luminus"))

from core.router import MessageRouter
from core.models import MessageTask


def test_router_init():
    router = MessageRouter()
    assert router is not None
    assert router.memory is not None
    assert router.decision is not None
    assert "GROQ" in router.nodes
    assert "GEMINI" in router.nodes
    assert "MOBILE" in router.nodes
    print("[OK] test_router_init")


def test_fallback_chain():
    router = MessageRouter()
    assert router.fallback_chain == ["GROQ", "GEMINI", "MOBILE"]
    print("[OK] test_fallback_chain")


def test_message_task():
    task = MessageTask(
        user_id="5500000000000@s.whatsapp.net",
        text="Oi",
        history=[],
        sender_name="Silvano",
        is_audio=False
    )
    assert task.user_id == "5500000000000@s.whatsapp.net"
    assert task.text == "Oi"
    assert task.sender_name == "Silvano"
    assert task.is_audio is False
    print("[OK] test_message_task")


if __name__ == "__main__":
    test_router_init()
    test_fallback_chain()
    test_message_task()
    print("\nTodos os testes passaram!")