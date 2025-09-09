import os
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from admin_handler import AdminHandler

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, bot, database: Database, admin_handler: AdminHandler):
        self.bot = bot
        self.db = database
        self.admin_handler = admin_handler
        self.group_chat_id = os.getenv('GROUP_CHAT_ID')
        self.duvidas_group_id = os.getenv('DUVIDAS_GROUP_CHAT_ID')
        self.meeting_link = os.getenv('MEETING_LINK', 'https://meet.google.com/seu-link')
        
        # Configurações de spam
        self.spam_keywords = [
            'compre agora', 'ganhe dinheiro fácil', 'investimento garantido',
            'lucro certo', 'sem risco', 'dinheiro rápido', 'oportunidade única',
            'clique aqui', 'telegram.me', 't.me', 'whatsapp', 'zap'
        ]
        self.max_links_per_message = 2
        self.max_messages_per_minute = 5
        
        # Cache para controle de spam
        self.user_message_count = {}
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa mensagens recebidas"""
        msg = update.message
        chat_id = msg.chat.id
        user_id = msg.from_user.id
        text = msg.text
        
        # Ignorar mensagens de bots
        if msg.from_user.is_bot:
            return
        
        # Processar apenas mensagens dos grupos principais
        if not self._is_monitored_group(chat_id):
            return
        
        try:
            # Atualizar informações do usuário
            await self.update_user_info(msg.from_user)
            
            # Processar comandos específicos
            if text and text.startswith('/'):
                await self.handle_command(update, context)
                return
            
            # Detectar e moderar spam
            if await self.is_spam_message(msg):
                await self.handle_spam_message(update, context)
                return
            
            # Processar mensagens normais
            await self.process_normal_message(update, context)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
    
    def _is_monitored_group(self, chat_id: int) -> bool:
        """Verifica se o chat é um dos grupos monitorados"""
        monitored_groups = []
        
        if self.group_chat_id:
            monitored_groups.append(int(self.group_chat_id))
        
        if self.duvidas_group_id:
            monitored_groups.append(int(self.duvidas_group_id))
        
        return chat_id in monitored_groups
    
    async def update_user_info(self, user) -> None:
        """Atualiza informações do usuário no banco de dados"""
        try:
            user_info = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            
            existing_user = self.db.get_user(user.id)
            
            if existing_user:
                # Verificar se houve mudanças
                if (existing_user.get('username') != user.username or 
                    existing_user.get('first_name') != user.first_name):
                    self.db.add_user(user_info)
                    logger.info(f"📝 Informações atualizadas para {user.first_name}")
            else:
                # Novo usuário
                self.db.add_user(user_info)
                logger.info(f"👤 Novo usuário registrado: {user.first_name}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar usuário: {e}")
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa comandos específicos"""
        text = update.message.text.lower()
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Comandos de administração
        if text.startswith('/admin'):
            await self.admin_handler.handle_admin_command(update, context)
            return
        
        # Outros comandos específicos
        if text == '/start':
            await self.handle_start_command(update, context)
        elif text == '/help':
            await self.handle_help_command(update, context)
        elif text == '/links':
            await self.handle_links_command(update, context)
        elif text == '/stats':
            await self.handle_stats_command(update, context)
        elif text == '/meeting' or text == '/reuniao':
            await self.handle_meeting_command(update, context)
        else:
            # Comando não reconhecido - não fazer nada para não poluir o chat
            pass
    
    async def handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa comando /start"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        
        if chat_id == int(self.group_chat_id or 0):
            # Mensagem no grupo principal
            welcome_text = f"👋 Olá {first_name}! Bem-vindo(a) ao nosso grupo de trading!\n\n"
            welcome_text += "📚 Use /help para ver os comandos disponíveis."
        else:
            # Mensagem privada
            welcome_text = f"🎯 Olá {first_name}! Bot Auge Traders ativo!\n\n"
            welcome_text += "✅ Sistema funcionando perfeitamente!\n\n"
            welcome_text += "📋 Use /help para ver os comandos disponíveis."
        
        await update.message.reply_text(welcome_text)
    
    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa comando /help"""
        help_text = "🤖 **Comandos Disponíveis:**\n\n"
        help_text += "📋 `/start` - Iniciar o bot\n"
        help_text += "❓ `/help` - Esta mensagem de ajuda\n"
        help_text += "📊 `/stats` - Suas estatísticas\n"
        help_text += "🔗 `/links` - Links úteis\n"
        help_text += "📹 `/meeting` - Link da reunião\n\n"
        
        # Comandos de admin (apenas para administradores)
        if self.admin_handler.is_admin(update.effective_user.id):
            help_text += "🔧 **Comandos de Admin:**\n"
            help_text += "⚙️ `/admin help` - Ajuda de administração\n\n"
        
        help_text += "💡 **Dica:** Interaja no grupo para aproveitar ao máximo nossa comunidade!"
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_links_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa comando /links"""
        user_id = update.effective_user.id
        
        # Registrar clique
        self.db.record_link_click(user_id, 'links_command')
        
        links_text = "🔗 **Links Úteis:**\n\n"
        links_text += "📚 **Educação:**\n"
        links_text += "• [Guia para Iniciantes](https://exemplo.com/guia)\n"
        links_text += "• [Análise Técnica](https://exemplo.com/analise)\n"
        links_text += "• [Gerenciamento de Risco](https://exemplo.com/risco)\n\n"
        
        links_text += "🛠️ **Ferramentas:**\n"
        links_text += "• [TradingView](https://tradingview.com)\n"
        links_text += "• [Calculadora de Risco](https://exemplo.com/calc)\n"
        links_text += "• [Calendário Econômico](https://exemplo.com/calendario)\n\n"
        
        links_text += "💬 **Comunidade:**\n"
        if self.duvidas_group_id:
            links_text += f"• [Grupo de Dúvidas]({os.getenv('DUVIDAS_GROUP_LINK', '#')})\n"
        links_text += "• [Canal de Sinais](https://exemplo.com/sinais)\n\n"
        
        links_text += "⚠️ **Lembre-se:** Sempre faça sua própria análise!"
        
        await update.message.reply_text(links_text, parse_mode='Markdown', disable_web_page_preview=True)
    
    async def handle_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa comando /stats"""
        user_id = update.effective_user.id
        user = self.db.get_user(user_id)
        
        if not user:
            await update.message.reply_text('❌ Usuário não encontrado no banco de dados.')
            return
        
        # Calcular tempo no grupo
        joined_date = datetime.fromisoformat(user['joined_at'])
        days_in_group = (datetime.now() - joined_date).days
        
        # Obter estatísticas de cliques
        user_clicks = self.db.get_link_click_stats(days=30)
        total_clicks = sum(stat['clicks'] for stat in user_clicks)
        
        stats_text = f"📊 **Suas Estatísticas:**\n\n"
        stats_text += f"👤 **Nome:** {user['first_name']}\n"
        stats_text += f"📅 **No grupo há:** {days_in_group} dias\n"
        stats_text += f"🎯 **Passo do funil:** {self._get_funnel_step_name(user['funnel_step'])}\n"
        stats_text += f"🔗 **Cliques em links:** {total_clicks} (últimos 30 dias)\n\n"
        
        stats_text += "💡 **Continue participando para evoluir ainda mais!"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    def _get_funnel_step_name(self, step: int) -> str:
        """Converte número do passo em nome legível"""
        step_names = {
            0: "Recém-chegado",
            1: "Mensagem 24h recebida",
            2: "Mensagem 48h recebida",
            3: "Mensagem 72h recebida",
        }
        return step_names.get(step, f"Passo {step}")
    
    async def handle_meeting_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa comando /meeting"""
        user_id = update.effective_user.id
        
        # Registrar clique
        self.db.record_link_click(user_id, 'meeting_link')
        
        meeting_text = "📹 **Link da Reunião:**\n\n"
        meeting_text += f"🔗 [Clique aqui para entrar na reunião]({self.meeting_link})\n\n"
        meeting_text += "⏰ **Horários das reuniões:**\n"
        meeting_text += "• Segunda-feira: 20:00\n"
        meeting_text += "• Quarta-feira: 20:00\n"
        meeting_text += "• Sexta-feira: 20:00\n\n"
        meeting_text += "💡 **Dica:** Chegue alguns minutos antes para testar áudio e vídeo!"
        
        await update.message.reply_text(meeting_text, parse_mode='Markdown')
    
    async def is_spam_message(self, msg) -> bool:
        """Detecta se a mensagem é spam"""
        try:
            user_id = msg.from_user.id
            text = msg.text or msg.caption or ''
            
            # Verificar se é admin (admins não são considerados spam)
            if self.admin_handler.is_admin(user_id):
                return False
            
            # Verificar palavras-chave de spam
            text_lower = text.lower()
            for keyword in self.spam_keywords:
                if keyword in text_lower:
                    logger.warning(f"🚨 Spam detectado (palavra-chave): {keyword} - Usuário: {user_id}")
                    return True
            
            # Verificar excesso de links
            link_count = len(re.findall(r'http[s]?://|www\.|t\.me|telegram\.me', text, re.IGNORECASE))
            if link_count > self.max_links_per_message:
                logger.warning(f"🚨 Spam detectado (muitos links): {link_count} - Usuário: {user_id}")
                return True
            
            # Verificar frequência de mensagens
            current_time = datetime.now()
            if user_id not in self.user_message_count:
                self.user_message_count[user_id] = []
            
            # Limpar mensagens antigas (mais de 1 minuto)
            self.user_message_count[user_id] = [
                timestamp for timestamp in self.user_message_count[user_id]
                if current_time - timestamp < timedelta(minutes=1)
            ]
            
            # Adicionar timestamp atual
            self.user_message_count[user_id].append(current_time)
            
            # Verificar se excedeu o limite
            if len(self.user_message_count[user_id]) > self.max_messages_per_minute:
                logger.warning(f"🚨 Spam detectado (muitas mensagens): {len(self.user_message_count[user_id])} - Usuário: {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar spam: {e}")
            return False
    
    async def handle_spam_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa mensagens identificadas como spam"""
        try:
            msg = update.message
            user_id = msg.from_user.id
            chat_id = msg.chat.id
            
            # Deletar a mensagem de spam
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            
            # Enviar aviso (que será deletado automaticamente)
            warning_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ Mensagem de @{msg.from_user.username or msg.from_user.first_name} foi removida por suspeita de spam."
            )
            
            # Deletar o aviso após 10 segundos
            await asyncio.sleep(10)
            await context.bot.delete_message(chat_id=chat_id, message_id=warning_msg.message_id)
            
            logger.info(f"🗑️ Mensagem de spam removida - Usuário: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar spam: {e}")
    
    async def process_normal_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa mensagens normais (não spam, não comandos)"""
        # Aqui você pode adicionar lógica adicional para mensagens normais
        # Por exemplo: análise de sentimento, estatísticas de participação, etc.
        pass