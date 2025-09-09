import logging
import re
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

class LinkTracker:
    def __init__(self, database: Database):
        self.db = database
        self.logger = logging.getLogger(__name__)
        
        # Padrões de URL para detectar links
        self.url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}'
        ]
        
        # Domínios confiáveis (não precisam de rastreamento especial)
        self.trusted_domains = {
            'auge.com.br',
            'youtube.com',
            'youtu.be',
            'instagram.com',
            'facebook.com',
            'linkedin.com',
            'twitter.com',
            'x.com',
            'telegram.org',
            't.me'
        }
        
        # Domínios suspeitos (requerem moderação)
        self.suspicious_domains = {
            'bit.ly',
            'tinyurl.com',
            'short.link',
            'rebrand.ly',
            'ow.ly',
            'buff.ly'
        }
    
    def extract_links_from_text(self, text: str):
        """Extrai todos os links de um texto"""
        links = []
        
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Normaliza o link
                if not match.startswith(('http://', 'https://')):
                    if match.startswith('www.'):
                        match = 'https://' + match
                    else:
                        match = 'https://' + match
                
                links.append(match)
        
        return list(set(links))  # Remove duplicatas
    
    async def process_message_links(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa links em mensagens e registra cliques"""
        try:
            message = update.message
            if not message or not message.text:
                return
            
            user = message.from_user
            chat = message.chat
            
            # Extrai links da mensagem
            links = self.extract_links_from_text(message.text)
            
            if not links:
                return
            
            # Processa cada link
            for link in links:
                await self._process_single_link(link, user, chat, message)
            
            # Verifica se precisa de moderação
            if await self._needs_moderation(links, user, chat):
                await self._moderate_message(update, context, links)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar links da mensagem: {e}")
    
    async def _process_single_link(self, link: str, user, chat, message):
        """Processa um link individual"""
        try:
            # Gera ID único para o link
            link_id = self._generate_link_id(link)
            
            # Analisa o domínio
            domain = self._extract_domain(link)
            
            # Classifica o link
            link_type = self._classify_link(domain)
            
            # Registra o link no banco de dados
            link_data = {
                'link_id': link_id,
                'original_url': link,
                'domain': domain,
                'link_type': link_type,
                'user_id': user.id,
                'chat_id': chat.id,
                'message_id': message.message_id,
                'shared_date': datetime.now().isoformat(),
                'click_count': 0
            }
            
            self.db.add_link_click(link_data)
            
            self.logger.info(f"Link processado: {domain} por {user.first_name} (ID: {user.id})")
            
        except Exception as e:
            self.logger.error(f"Erro ao processar link individual: {e}")
    
    def _generate_link_id(self, url: str):
        """Gera ID único para um link"""
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _extract_domain(self, url: str):
        """Extrai domínio de uma URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' se presente
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return 'unknown'
    
    def _classify_link(self, domain: str):
        """Classifica um link baseado no domínio"""
        if domain in self.trusted_domains:
            return 'trusted'
        elif domain in self.suspicious_domains:
            return 'suspicious'
        elif any(keyword in domain for keyword in ['auge', 'curso', 'treinamento']):
            return 'promotional'
        else:
            return 'external'
    
    async def _needs_moderation(self, links: list, user, chat):
        """Verifica se os links precisam de moderação"""
        try:
            # Verifica se há links suspeitos
            for link in links:
                domain = self._extract_domain(link)
                if domain in self.suspicious_domains:
                    return True
            
            # Verifica limite de links por usuário
            user_links_today = self.db.get_user_links_count(user.id, datetime.now().date())
            if user_links_today > 5:  # Máximo 5 links por dia
                return True
            
            # Verifica se usuário é novo (menos de 24h no grupo)
            user_data = self.db.get_user(user.id)
            if user_data and user_data.get('join_date'):
                join_date = datetime.fromisoformat(user_data['join_date'])
                if datetime.now() - join_date < timedelta(hours=24):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar necessidade de moderação: {e}")
            return False
    
    async def _moderate_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, links: list):
        """Modera mensagem com links suspeitos"""
        try:
            message = update.message
            user = message.from_user
            
            # Deleta a mensagem original
            await context.bot.delete_message(
                chat_id=message.chat_id,
                message_id=message.message_id
            )
            
            # Envia aviso de moderação
            warning_text = f'''⚠️ **Mensagem Moderada** ⚠️

👤 **Usuário:** {user.first_name}
🔗 **Motivo:** Link suspeito ou spam

📋 **Links detectados:**
'''
            
            for link in links[:3]:  # Mostra apenas os 3 primeiros
                domain = self._extract_domain(link)
                warning_text += f"• `{domain}`\n"
            
            if len(links) > 3:
                warning_text += f"• ... e mais {len(links) - 3} links\n"
            
            warning_text += "\n🛡️ **Ação:** Mensagem removida automaticamente"
            
            # Envia para administradores
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=warning_text,
                parse_mode='Markdown'
            )
            
            # Registra a moderação
            self.logger.warning(f"Mensagem moderada: {user.first_name} (ID: {user.id}) - Links: {len(links)}")
            
        except Exception as e:
            self.logger.error(f"Erro ao moderar mensagem: {e}")
    
    async def get_link_statistics(self, chat_id: int = None, days: int = 7):
        """Retorna estatísticas de links"""
        try:
            # Busca dados dos últimos X dias
            start_date = datetime.now() - timedelta(days=days)
            
            if chat_id:
                links_data = self.db.get_links_by_chat(chat_id, start_date)
            else:
                links_data = self.db.get_all_links(start_date)
            
            if not links_data:
                return f"📊 Nenhum link compartilhado nos últimos {days} dias."
            
            # Calcula estatísticas
            total_links = len(links_data)
            unique_domains = len(set(link['domain'] for link in links_data))
            total_clicks = sum(link.get('click_count', 0) for link in links_data)
            
            # Conta por tipo
            types_count = {}
            domains_count = {}
            
            for link in links_data:
                link_type = link.get('link_type', 'unknown')
                domain = link.get('domain', 'unknown')
                
                types_count[link_type] = types_count.get(link_type, 0) + 1
                domains_count[domain] = domains_count.get(domain, 0) + 1
            
            # Top 5 domínios
            top_domains = sorted(domains_count.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Monta relatório
            stats = f'''📊 **Estatísticas de Links ({days} dias)**

📈 **Resumo Geral:**
• Total de links: {total_links}
• Domínios únicos: {unique_domains}
• Total de cliques: {total_clicks}
• Média de cliques: {total_clicks/total_links if total_links > 0 else 0:.1f}

🏷️ **Por Tipo:**
'''
            
            for link_type, count in types_count.items():
                emoji = {'trusted': '✅', 'suspicious': '⚠️', 'promotional': '📢', 'external': '🔗'}.get(link_type, '❓')
                stats += f"• {emoji} {link_type.title()}: {count}\n"
            
            stats += "\n🌐 **Top Domínios:**\n"
            for domain, count in top_domains:
                stats += f"• `{domain}`: {count} links\n"
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de links: {e}")
            return "❌ Erro ao obter estatísticas de links."
    
    async def create_tracked_link(self, original_url: str, campaign: str = None):
        """Cria um link rastreado"""
        try:
            # Gera ID único
            link_id = self._generate_link_id(original_url + str(datetime.now()))
            
            # Cria entrada no banco
            tracked_data = {
                'link_id': link_id,
                'original_url': original_url,
                'campaign': campaign or 'default',
                'created_date': datetime.now().isoformat(),
                'click_count': 0
            }
            
            self.db.add_tracked_link(tracked_data)
            
            # Retorna URL rastreada
            tracked_url = f"https://auge.com.br/track/{link_id}"
            
            self.logger.info(f"Link rastreado criado: {link_id} para {original_url}")
            
            return tracked_url, link_id
            
        except Exception as e:
            self.logger.error(f"Erro ao criar link rastreado: {e}")
            return None, None
    
    async def register_click(self, link_id: str, user_id: int = None, ip_address: str = None):
        """Registra um clique em link rastreado"""
        try:
            click_data = {
                'link_id': link_id,
                'user_id': user_id,
                'ip_address': ip_address,
                'click_date': datetime.now().isoformat()
            }
            
            self.db.register_link_click(click_data)
            
            self.logger.info(f"Clique registrado: {link_id} por usuário {user_id}")
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar clique: {e}")
    
    def get_domain_reputation(self, domain: str):
        """Retorna reputação de um domínio"""
        if domain in self.trusted_domains:
            return {'status': 'trusted', 'score': 100, 'description': 'Domínio confiável'}
        elif domain in self.suspicious_domains:
            return {'status': 'suspicious', 'score': 20, 'description': 'Domínio suspeito - encurtador'}
        elif 'auge' in domain:
            return {'status': 'internal', 'score': 100, 'description': 'Domínio interno da Auge'}
        else:
            return {'status': 'unknown', 'score': 50, 'description': 'Domínio desconhecido'}
    
    async def cleanup_old_links(self, days: int = 30):
        """Remove links antigos do banco de dados"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = self.db.cleanup_old_links(cutoff_date)
            
            self.logger.info(f"Limpeza concluída: {deleted_count} links removidos")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de links: {e}")
            return 0