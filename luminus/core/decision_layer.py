# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: decision_layer.py
# DESCRIÇÃO: Camada de decisão determinística para roteamento de mensagens
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.1
# ================================================================

import logging
from luminus.core.models import MessageTask

class DecisionLayer:
    def determine_node(self, task: MessageTask) -> str:
        text = task.text.lower()
        
        if "/mobile" in text:
            logging.info("[DECISION] Rota forçada: MOBILE")
            task.context_type = "mobile" # Reseta contexto para mobile
            return "MOBILE"
        
        if "/sac" in text:
            logging.info("[DECISION] Contexto alterado para: SAC")
            task.context_type = "sac"
        elif "/secretary" in text:
            logging.info("[DECISION] Contexto alterado para: SECRETARY")
            task.context_type = "secretary"
        
        logging.info(f"[DECISION] Usando GEMINI como nó primário (contexto: {task.context_type})")
        return "GEMINI"

