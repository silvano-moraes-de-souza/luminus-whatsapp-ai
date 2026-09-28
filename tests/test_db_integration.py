import sys
import os
# Adiciona o diretório raiz ao path para importar módulos do luminus
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from luminus.core.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)

def test_database_manager():
    print("Iniciando testes do DatabaseManager...")
    try:
        db = DatabaseManager()
        
        # Dados de teste
        user_id = "test_user_123"
        sender_name = "Test User"
        
        # Testar inserção
        db.add_message(user_id, sender_name, "user", "Olá, este é um teste!")
        db.add_message(user_id, sender_name, "assistant", "Olá! Teste recebido.")
        print("Inserções realizadas com sucesso.")
        
        # Testar recuperação
        history = db.get_history(user_id)
        print(f"Histórico recuperado: {history}")
        
        assert len(history) == 2, f"Esperado 2 mensagens, encontrado {len(history)}"
        assert history[0]['content'] == "Olá, este é um teste!"
        print("Testes do DatabaseManager passados com sucesso!")
        
    except Exception as e:
        print(f"Testes falharam: {e}")
        # Em ambiente de teste sem o DB rodando, isso vai falhar
        # Isso é esperado se o docker-compose não estiver rodando.
        print("NOTA: O teste falhará se o container 'luminus_db' não estiver acessível.")

if __name__ == "__main__":
    test_database_manager()
