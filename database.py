import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DB_PATH', './data/bot.db')
        self.ensure_data_directory()
        self.init_database()
    
    def ensure_data_directory(self):
        """Garante que o diretório de dados existe"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
    
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    funnel_step INTEGER DEFAULT 0,
                    last_funnel_message DATETIME,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabela de cliques em links
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS link_clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    link_type TEXT NOT NULL,
                    clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabela de mensagens agendadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message_type TEXT NOT NULL,
                    scheduled_for DATETIME NOT NULL,
                    sent BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Tabela de configurações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Inserir configuração padrão do link da reunião
            cursor.execute('''
                INSERT OR IGNORE INTO bot_settings (setting_key, setting_value)
                VALUES ('meeting_link', 'https://meet.google.com/auge-traders-weekly')
            ''')
            
            conn.commit()
            logger.info("✅ Banco de dados inicializado com sucesso")
    
    def add_user(self, user_info: Dict) -> bool:
        """Adiciona ou atualiza um usuário no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, joined_at, is_active)
                    VALUES (?, ?, ?, ?, COALESCE((SELECT joined_at FROM users WHERE user_id = ?), CURRENT_TIMESTAMP), 1)
                ''', (
                    user_info.get('id'),
                    user_info.get('username'),
                    user_info.get('first_name'),
                    user_info.get('last_name'),
                    user_info.get('id')
                ))
                
                conn.commit()
                logger.info(f"✅ Usuário {user_info.get('first_name')} ({user_info.get('id')}) adicionado/atualizado")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar usuário: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Busca um usuário pelo ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuário: {e}")
            return None
    
    def update_user_funnel_step(self, user_id: int, step: int) -> bool:
        """Atualiza o passo do funil do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users 
                    SET funnel_step = ?, last_funnel_message = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (step, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar passo do funil: {e}")
            return False
    
    def get_users_for_funnel_step(self, current_step: int, hours_ago: int) -> List[Dict]:
        """Busca usuários elegíveis para o próximo passo do funil"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Calcular o timestamp de corte
                cutoff_time = datetime.now() - timedelta(hours=hours_ago)
                
                cursor.execute('''
                    SELECT * FROM users 
                    WHERE funnel_step = ? 
                    AND is_active = 1
                    AND (
                        (funnel_step = 0 AND joined_at <= ?)
                        OR (funnel_step > 0 AND last_funnel_message <= ?)
                    )
                ''', (current_step, cutoff_time, cutoff_time))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuários para funil: {e}")
            return []
    
    def record_link_click(self, user_id: int, link_type: str) -> bool:
        """Registra um clique em link"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO link_clicks (user_id, link_type)
                    VALUES (?, ?)
                ''', (user_id, link_type))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar clique: {e}")
            return False
    
    def get_link_click_stats(self, link_type: str = None, days: int = 30) -> List[Dict]:
        """Obtém estatísticas de cliques em links"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                if link_type:
                    cursor.execute('''
                        SELECT link_type, COUNT(*) as clicks, COUNT(DISTINCT user_id) as unique_users
                        FROM link_clicks 
                        WHERE link_type = ? AND clicked_at >= ?
                        GROUP BY link_type
                    ''', (link_type, cutoff_date))
                else:
                    cursor.execute('''
                        SELECT link_type, COUNT(*) as clicks, COUNT(DISTINCT user_id) as unique_users
                        FROM link_clicks 
                        WHERE clicked_at >= ?
                        GROUP BY link_type
                    ''', (cutoff_date,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas de cliques: {e}")
            return []
    
    def get_user_stats(self) -> Dict:
        """Obtém estatísticas gerais dos usuários"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de usuários
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
                total_users = cursor.fetchone()[0]
                
                # Usuários por passo do funil
                cursor.execute('''
                    SELECT funnel_step, COUNT(*) as count
                    FROM users 
                    WHERE is_active = 1
                    GROUP BY funnel_step
                    ORDER BY funnel_step
                ''')
                funnel_stats = dict(cursor.fetchall())
                
                # Novos usuários hoje
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(joined_at) = DATE('now') AND is_active = 1
                ''')
                new_today = cursor.fetchone()[0]
                
                # Novos usuários esta semana
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE joined_at >= DATE('now', '-7 days') AND is_active = 1
                ''')
                new_week = cursor.fetchone()[0]
                
                return {
                    'total_users': total_users,
                    'funnel_stats': funnel_stats,
                    'new_today': new_today,
                    'new_week': new_week
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def get_recent_users(self, limit: int = 10) -> List[Dict]:
        """Obtém os usuários mais recentes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, username, first_name, joined_at, funnel_step
                    FROM users 
                    WHERE is_active = 1
                    ORDER BY joined_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuários recentes: {e}")
            return []
    
    def get_all_active_users(self) -> List[Dict]:
        """Obtém todos os usuários ativos para broadcast"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, first_name, username
                    FROM users 
                    WHERE is_active = 1
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuários ativos: {e}")
            return []
    
    def get_all_users(self) -> List[Dict]:
        """Obtém todos os usuários (ativos e inativos)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, first_name, username, joined_at, funnel_step, is_active
                    FROM users
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar todos os usuários: {e}")
            return []
    
    def get_setting(self, setting_key: str) -> Optional[str]:
        """Obtém uma configuração do bot"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT setting_value FROM bot_settings
                    WHERE setting_key = ?
                ''', (setting_key,))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter configuração {setting_key}: {e}")
            return None
    
    def set_setting(self, setting_key: str, setting_value: str) -> bool:
        """Define uma configuração do bot"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO bot_settings (setting_key, setting_value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (setting_key, setting_value))
                
                conn.commit()
                logger.info(f"✅ Configuração {setting_key} atualizada")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao definir configuração {setting_key}: {e}")
            return False
    
    def get_meeting_link(self) -> str:
        """Obtém o link da reunião atual"""
        link = self.get_setting('meeting_link')
        return link or 'https://meet.google.com/auge-traders-weekly'
    
    def set_meeting_link(self, new_link: str) -> bool:
        """Define um novo link da reunião"""
        return self.set_setting('meeting_link', new_link)

    def close(self):
        """Fecha a conexão com o banco de dados"""
        # SQLite não precisa de fechamento explícito quando usando context manager
        pass