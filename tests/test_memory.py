# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: test_memory.py
# DESCRIÇÃO: Testes básicos do gerenciador de memória
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.1
# ================================================================

import sys
import os
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "luminus"))

from core.memory import MemoryManager


def test_memory_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryManager(storage_dir=tmpdir)
        assert mem is not None
        assert os.path.exists(mem.storage_dir)
        print("[OK] test_memory_init")


def test_add_and_get_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryManager(storage_dir=tmpdir)
        user_id = "5500000000000@s.whatsapp.net"
        
        mem.add_message(user_id, "user", "Olá")
        history = mem.get_history(user_id)
        
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Olá"
        print("[OK] test_add_and_get_message")


def test_history_limit():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryManager(storage_dir=tmpdir)
        user_id = "5500000000000@s.whatsapp.net"
        
        for i in range(15):
            mem.add_message(user_id, "user", f"Mensagem {i}")
        
        history = mem.get_history(user_id, limit=10)
        assert len(history) == 10
        print("[OK] test_history_limit")


def test_clear():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryManager(storage_dir=tmpdir)
        user_id = "5500000000000@s.whatsapp.net"
        
        mem.add_message(user_id, "user", "Teste")
        mem.clear(user_id)
        history = mem.get_history(user_id)
        
        assert len(history) == 0
        print("[OK] test_clear")


if __name__ == "__main__":
    test_memory_init()
    test_add_and_get_message()
    test_history_limit()
    test_clear()
    print("\nTodos os testes passaram!")