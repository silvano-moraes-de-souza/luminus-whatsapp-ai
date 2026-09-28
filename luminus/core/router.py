# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: router.py
# DESCRIÇÃO: Roteador de mensagens que direciona para o nó correto
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.2
# ================================================================

import logging
import time
from luminus.core.db_manager import DatabaseManager
from luminus.core.models import MessageTask
from luminus.core.decision_layer import DecisionLayer
from luminus.core.nodes.mobile_node import MobileNode
from luminus.core.nodes.gemini_node import GeminiNode

last_message_time: dict[str, float] = {}
COOLDOWN_SECONDS = 10

class MessageRouter:
    def __init__(self) -> None:
        self.db = DatabaseManager()
        self.decision = DecisionLayer()
        
        self.nodes = {
            "GEMINI": GeminiNode(),
            "MOBILE": MobileNode()
        }
        
        self.fallback_chain = ["GEMINI", "MOBILE"]

    def process_message(self, user_id: str, message_text: str, sender_name: str = "", is_audio: bool = False) -> str:
        now = time.time()
        last_time = last_message_time.get(user_id, 0)
        if now - last_time < COOLDOWN_SECONDS:
            logging.info(f"[ROUTER] Cooldown ativo para {user_id}")
            return "[SILENT_IGNORE]"
        last_message_time[user_id] = now
        
        # PERSISTÊNCIA NO BANCO
        self.db.add_message(user_id, sender_name, "user", message_text)
        
        # Recupera contexto e histórico
        context_type = self.db.get_conversation_context(user_id)
        filtered_history = self.db.get_history(user_id)
        
        task = MessageTask(
            user_id=user_id,
            text=message_text,
            history=filtered_history,
            sender_name=sender_name,
            is_audio=is_audio
        )
        
        # Passa o contexto (mode) na tarefa
        task.context_type = context_type
        
        initial_target = self.decision.determine_node(task)
        
        # Persiste o novo contexto determinado no banco
        if task.context_type != context_type:
            self.db.set_conversation_context(user_id, task.context_type)
        
        response_text: str | None = None
        successful_node: str | None = None
        
        for node_name in self.fallback_chain:
            if node_name not in self.nodes:
                continue
            
            try:
                logging.info(f"[ROUTER] Tentando nó: {node_name}")
                response_text = self.nodes[node_name].execute(task)
                successful_node = node_name
                break
            except Exception as e:
                logging.warning(f"[ROUTER] Falha no nó {node_name}: {e}")
                continue
        
        if response_text is None:
            logging.error(f"[ROUTER] Todos os nós falharam!")
            response_text = "Desculpe Silvano, todos os meus núcleos de IA estão indisponíveis no momento."
            successful_node = "ERRO"
        
        if successful_node != initial_target and successful_node != "ERRO":
            node_names = {
                "GEMINI": "GEMINI", 
                "MOBILE": "MOBILE"
            }
            initial_name = node_names.get(initial_target, initial_target)
            successful_name = node_names.get(successful_node, successful_node)
            response_text = f"*(Nota: {initial_name} indisponível. Usando {successful_name})*\n{response_text}"
        
        # PERSISTÊNCIA NO BANCO
        self.db.add_message(user_id, sender_name, "assistant", response_text)
        
        response_text = self._truncate_response(response_text)
        return response_text
    
    def _truncate_response(self, text: str) -> str:
        if not text:
            return text
        text = text.strip()
        lines = text.split('\n')
        # Limite ampliado para 300 caracteres (mais natural), preservando a primeira linha
        text = lines[0][:300]
        return text

    def _filter_history(self, history: list[dict]) -> list[dict]:
        filtered = []
        for msg in history[-20:]:
            if isinstance(msg, dict):
                content = msg.get("content", "")
            elif isinstance(msg, list):
                continue
            else:
                content = str(msg) if msg else ""
            if content and not any(x in content for x in ["Desculpe Silvano", "Nota:", "Erro HTTP"]):
                filtered.append(msg)
        return filtered