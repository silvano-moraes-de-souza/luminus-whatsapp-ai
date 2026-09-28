# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: memory.py
# DESCRIÇÃO: Gerenciador de memória persistente por usuário
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.2
# ================================================================

import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, storage_dir: str = "memory_db") -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.storage_dir = os.path.join(base_dir, storage_dir)
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _get_user_file(self, user_id: str) -> str:
        safe_id = user_id.replace("@", "_").replace(".", "_")
        return os.path.join(self.storage_dir, f"{safe_id}.json")

    def get_history(self, user_id: str, limit: int = 10) -> list[dict]:
        file_path = self._get_user_file(user_id)
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                return history[-limit:]
        except Exception:
            return []

    def add_message(self, user_id: str, role: str, content: str) -> None:
        file_path = self._get_user_file(user_id)
        history = self.get_history(user_id, limit=50)
        
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        if len(history) > 100:
            history = history[-100:]

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")

    def clear(self, user_id: str) -> None:
        file_path = self._get_user_file(user_id)
        if os.path.exists(file_path):
            os.remove(file_path)