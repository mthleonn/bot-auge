import logging
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from funnel_handler import FunnelHandler

class WelcomeHandler:
    def __init__(self, database: Database, funnel_handler: FunnelHandler):
        self.db = database
        self.funnel_handler = funnel_handler
        self.logger = logging.getLogger(__name__)
        
        # IDs dos grupos (configurados via variáveis de ambiente)
        self.main_group_id = int(os.getenv('GROUP_CHAT_ID', '0'))
        self.duvidas_group_id = int(os.getenv('DUVIDAS_GROUP_CHAT_ID', '0'))
        
        # Log das configurações
        self.logger.info(f"🔧 WelcomeHandler configurado:")
        self.logger.info(f"   • Grupo principal ID: {self.main_group_id}")
        self.logger.info(f"   • Grupo dúvidas ID: {self.duvidas_group_id}")
        
        if self.main_group_id == 0:
            self.logger.warning("⚠️ GROUP_CHAT_ID não configurado!")
        if self.duvidas_group_id == 0:
            self.logger.warning("⚠️ DUVIDAS_GROUP_CHAT_ID não configurado!")
        
        # Configurações de mensagens
        self.welcome_messages = {
            'main_group': {
                'title': '🎯 Bem-vindo(a) ao Auge Traders! 🎯',
                'message': '''Olá {name}! 👋

📊 Seja muito bem-vindo(a) ao **Auge Traders**!

🚀 **Aqui você receberá:**
• Análises diárias do **pré-mercado** às 6h
• Possíveis **entradas e saídas** pelos mentores **Rafael** e **Daniel**
• Estratégias testadas e comprovadas
• Acompanhamento em tempo real
• Comunidade de traders consistentes

💡 **Para aproveitar ao máximo:**
1️⃣ Fique atento às análises matinais
2️⃣ Siga o plano de trade
3️⃣ Mantenha a disciplina
4️⃣ Participe das discussões
5️⃣ Tire suas dúvidas no grupo específico

⏰ **Análises enviadas às 6h** todos os dias úteis!

🎯 **Acelere seus resultados** com nossa mentoria completa!

💪 Vamos conquistar a consistência juntos! 🔥''',
                'buttons': [
                    [InlineKeyboardButton("🚀 Mentoria Completa", url="https://www.mentoriaaugetraders.com.br/")],
                    [InlineKeyboardButton("❓ Grupo de Dúvidas", url="https://t.me/+YgugjrIQHt1lNGNh")]
                ]
            },
            'duvidas_group': {
                'title': '❓ Bem-vindo(a) ao Suporte Auge! ❓',
                'message': '''Olá {name}! 👋

🆘 Este é o grupo de suporte e dúvidas!

📋 Como funciona:
• Faça suas perguntas de forma clara
• Aguarde a resposta da nossa equipe
• Ajude outros membros quando possível
• Mantenha o foco em dúvidas técnicas

⚡ Resposta rápida garantida!

🔙 Voltar ao grupo principal: @AugeGrupo''',
                'buttons': [
                    [InlineKeyboardButton("🔙 Grupo Principal", url="https://t.me/AugeGrupo")],
                    [InlineKeyboardButton("📖 FAQ", url="https://auge.com.br/faq")]
                ]
            },
            'other_group': {
                'title': '👋 Olá! Sou o Bot Auge!',
                'message': '''Olá {name}! 👋

Obrigado por me adicionar ao grupo!

🤖 Eu sou o Bot Auge e posso ajudar com:
• Mensagens de boas-vindas
• Moderação básica
• Estatísticas do grupo
• Links úteis

⚙️ Configure-me como administrador para funcionar melhor!

📞 Suporte: @AugeSuporte''',
                'buttons': [
                    [InlineKeyboardButton("🌐 Conheça a Auge", url="https://auge.com.br")],
                    [InlineKeyboardButton("📞 Suporte", url="https://t.me/AugeSuporte")]
                ]
            }
        }
    
    async def handle_new_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa novos membros que entram no grupo"""
        try:
            chat = update.effective_chat
            new_members = update.message.new_chat_members
            
            for member in new_members:
                # Ignora se for o próprio bot
                if member.id == context.bot.id:
                    await self._handle_bot_added_to_group(update, context)
                    continue
                
                # Adiciona usuário ao banco de dados
                await self._add_user_to_database(member, chat)
                
                # Envia mensagem de boas-vindas
                await self._send_welcome_message(update, context, member, chat)
                
                # Inicia funil de mensagens automáticas (apenas para grupo principal)
                if chat.id == self.main_group_id:
                    await self.funnel_handler.schedule_funnel_check(member.id, chat.id)
                
                self.logger.info(f"Novo membro processado: {member.first_name} (ID: {member.id}) no chat {chat.id}")
                
        except Exception as e:
            self.logger.error(f"Erro ao processar novos membros: {e}")
    
    async def _add_user_to_database(self, member, chat):
        """Adiciona usuário ao banco de dados"""
        try:
            user_data = {
                'user_id': member.id,
                'first_name': member.first_name or '',
                'last_name': member.last_name or '',
                'username': member.username or '',
                'chat_id': chat.id,
                'join_date': datetime.now().isoformat()
            }
            
            self.db.add_user(user_data)
            self.logger.info(f"Usuário {member.first_name} adicionado ao banco de dados")
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar usuário ao banco: {e}")
    
    async def _send_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member, chat):
        """Envia mensagem de boas-vindas personalizada"""
        try:
            # Determina o tipo de grupo
            group_type = self._get_group_type(chat.id)
            
            # Obtém configuração da mensagem
            message_config = self.welcome_messages[group_type]
            
            # Personaliza a mensagem
            name = member.first_name or member.username or "Novo membro"
            welcome_text = f"**{message_config['title']}**\n\n{message_config['message'].format(name=name)}"
            
            # Cria teclado inline
            keyboard = InlineKeyboardMarkup(message_config['buttons'])
            
            # Envia mensagem
            await context.bot.send_message(
                chat_id=chat.id,
                text=welcome_text,
                parse_mode='Markdown',
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            
            self.logger.info(f"Mensagem de boas-vindas enviada para {name} no grupo {group_type}")
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem de boas-vindas: {e}")
    
    async def _handle_bot_added_to_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa quando o bot é adicionado a um grupo"""
        try:
            chat = update.effective_chat
            
            # Mensagem quando bot é adicionado
            bot_welcome = '''🤖 **Bot Auge Ativado!** 🤖

✅ Olá! Eu sou o Bot Auge e agora estou ativo neste grupo!

🔧 **Funcionalidades disponíveis:**
• Mensagens de boas-vindas automáticas
• Moderação de spam
• Comandos administrativos
• Estatísticas do grupo
• Sistema de funil automático

⚙️ **Para melhor funcionamento:**
1. Me torne administrador
2. Configure as variáveis de ambiente
3. Use /help para ver comandos

🚀 **Vamos começar!**'''
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Comandos", callback_data="help_commands")],
                [InlineKeyboardButton("🌐 Site Auge", url="https://auge.com.br")]
            ])
            
            await context.bot.send_message(
                chat_id=chat.id,
                text=bot_welcome,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
            self.logger.info(f"Bot adicionado ao grupo: {chat.title} (ID: {chat.id})")
            
        except Exception as e:
            self.logger.error(f"Erro ao processar adição do bot: {e}")
    
    def _get_group_type(self, chat_id):
        """Determina o tipo de grupo baseado no ID"""
        if chat_id == self.main_group_id:
            return 'main_group'
        elif chat_id == self.duvidas_group_id:
            return 'duvidas_group'
        else:
            return 'other_group'
    
    async def send_custom_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, custom_message: str = None):
        """Envia mensagem de boas-vindas customizada"""
        try:
            chat = update.effective_chat
            
            if custom_message:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=custom_message,
                    parse_mode='Markdown'
                )
            else:
                # Busca usuário no banco
                user = self.db.get_user(user_id)
                if user:
                    member_name = user.get('first_name', 'Membro')
                    await self._send_welcome_message(update, context, type('Member', (), {'first_name': member_name, 'id': user_id})(), chat)
            
            self.logger.info(f"Mensagem customizada enviada para usuário {user_id}")
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem customizada: {e}")
    
    async def get_welcome_stats(self, chat_id: int):
        """Retorna estatísticas de boas-vindas do grupo"""
        try:
            # Busca usuários do chat específico
            users = self.db.get_users_by_chat(chat_id)
            
            if not users:
                return "📊 Nenhum dado de boas-vindas encontrado para este grupo."
            
            total_users = len(users)
            today = datetime.now().date()
            
            # Conta novos membros hoje
            new_today = sum(1 for user in users 
                          if user.get('join_date') and 
                          datetime.fromisoformat(user['join_date']).date() == today)
            
            # Conta novos membros esta semana
            week_ago = today - timedelta(days=7)
            new_week = sum(1 for user in users 
                         if user.get('join_date') and 
                         datetime.fromisoformat(user['join_date']).date() >= week_ago)
            
            stats = f'''📊 **Estatísticas de Boas-vindas**

👥 **Total de membros:** {total_users}
🆕 **Novos hoje:** {new_today}
📅 **Novos esta semana:** {new_week}
📈 **Média diária (7 dias):** {new_week/7:.1f}

🎯 **Grupo:** {self._get_group_type(chat_id).replace('_', ' ').title()}'''
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de boas-vindas: {e}")
            return "❌ Erro ao obter estatísticas."
    
    def update_welcome_message(self, group_type: str, new_config: dict):
        """Atualiza configuração de mensagem de boas-vindas"""
        try:
            if group_type in self.welcome_messages:
                self.welcome_messages[group_type].update(new_config)
                self.logger.info(f"Mensagem de boas-vindas atualizada para {group_type}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao atualizar mensagem de boas-vindas: {e}")
            return False