# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: base_node.py
# DESCRIÇÃO: Classe base abstrata para nós de processamento
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.1
# ================================================================

from abc import ABC, abstractmethod
from luminus.core.models import MessageTask

class BaseNode(ABC):
    @abstractmethod
    def execute(self, task: MessageTask) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass