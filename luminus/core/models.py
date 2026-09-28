# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: models.py
# DESCRIÇÃO: Modelos de dados para tarefas de mensagens
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.1
# ================================================================

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MessageTask:
    user_id: str
    text: str
    history: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    target_node: Optional[str] = None
    priority: int = 1
    sender_name: str = ""
    is_audio: bool = False
    context_type: str = "general" # 'general', 'secretary', 'sac'