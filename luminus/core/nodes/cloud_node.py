# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: cloud_node.py
# DESCRIÇÃO: Nó de processamento via motor de IA na nuvem
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.1
# ================================================================

from luminus.core.nodes.base_node import BaseNode
from luminus.core.models import MessageTask
from luminus.core.engine import AIEngine
import logging

class CloudNode(BaseNode):
    def __init__(self):
        self.engine = AIEngine()

    @property
    def name(self) -> str:
        return "IA_CLOUD_SUPERPOOL"

    def execute(self, task: MessageTask) -> str:
        try:
            return self.engine.get_response(task.text, task.history)
        except Exception as e:
            logging.error(f"[{self.name}] Erro: {e}")
            return "Erro ao processar via Cloud."