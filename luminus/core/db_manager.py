import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import logging

class DatabaseManager:
    def __init__(self):
        self.conn_str = os.environ["DATABASE_URL"]
        self._init_db()

    def _get_conn(self):
        return psycopg2.connect(self.conn_str)

    def _init_db(self):
        # Apenas para garantir que a conexão funciona
        try:
            with self._get_conn() as conn:
                pass
        except Exception as e:
            logging.error(f"Erro ao conectar ao banco: {e}")

    def add_message(self, user_id, sender_name, role, content):
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                # Upsert conversation
                cur.execute("""
                    INSERT INTO conversations (user_id, sender_name, last_interaction)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET last_interaction = CURRENT_TIMESTAMP
                    RETURNING id
                """, (user_id, sender_name))
                conv_id = cur.fetchone()[0]

                # Insert message
                cur.execute("""
                    INSERT INTO messages (conversation_id, role, content)
                    VALUES (%s, %s, %s)
                """, (conv_id, role, content))
                conn.commit()

    def get_conversation_context(self, user_id):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT context_type FROM conversations WHERE user_id = %s", (user_id,))
                result = cur.fetchone()
                return result['context_type'] if result else 'general'

    def get_history(self, user_id, limit=20):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT m.role, m.content 
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.user_id = %s
                    ORDER BY m.created_at DESC
                    LIMIT %s
                """, (user_id, limit))
                return list(reversed(cur.fetchall()))

    def set_conversation_context(self, user_id, context_type):
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE conversations
                    SET context_type = %s
                    WHERE user_id = %s
                """, (context_type, user_id))
                conn.commit()

