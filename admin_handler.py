import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from telegram import Update
from telegram.ext import ContextTypes
from database import Database

logger = logging.getLogger(__name__)

class AdminHandler:
    def __init__(self, bot, database: Database):
        self.bot = bot
        self.db = database
        self.group_chat_id = os.getenv('GROUP_CHAT_ID')
        self.admin_ids = self._get_admin_ids()
    
    def _get_admin_ids(self) -> List[int]:
        """Obtém a lista de IDs de administradores das variáveis de ambiente"""
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        if admin_ids_str:
            try:
                return [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
            except ValueError:
                logger.error("❌ Erro ao processar ADMIN_IDS")
        return []
    
    def is_admin(self, user_id: int) -> bool:
        """Verifica se o usuário é administrador"""
        return user_id in self.admin_ids
    
    async def handle_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processa comandos de administração"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Verificar se é administrador
        if not self.is_admin(user_id):
            await update.message.reply_text('❌ Você não tem permissão para usar comandos de administrador.')
            return
        
        # Extrair comando e parâmetros
        parts = message_text.split(' ', 2)
        if len(parts) < 2:
            await self.handle_admin_help(update, context)
            return
        
        command = parts[1].lower()
        params = parts[2] if len(parts) > 2 else ''
        
        # Processar comandos
        if command == 'broadcast':
            await self.handle_broadcast(update, context, params)
        elif command == 'stats':
            await self.handle_detailed_stats(update, context)
        elif command == 'users':
            await self.handle_users_list(update, context)
        elif command == 'test':
            await self.handle_test_message(update, context)
        elif command == 'help':
            await self.handle_admin_help(update, context)
        elif command == 'setphoto':
            await self.handle_setphoto_info(update, context)
        else:
            await update.message.reply_text(
                '❌ Comando não reconhecido. Use `/admin help` para ver os comandos disponíveis.'
            )
    
    async def handle_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
        """Envia mensagem para todos os usuários ativos"""
        if not message.strip():
            await update.message.reply_text('❌ Você precisa fornecer uma mensagem para o broadcast.\n\nExemplo: `/admin broadcast Olá pessoal!`')
            return
        
        users = self.db.get_all_active_users()
        if not users:
            await update.message.reply_text('❌ Nenhum usuário ativo encontrado.')
            return
        
        # Confirmar broadcast
        confirm_text = f"📢 **Confirmar Broadcast**\n\n📝 **Mensagem:** {message}\n👥 **Usuários:** {len(users)}\n\n⚠️ Esta ação enviará a mensagem para todos os usuários ativos. Tem certeza?"
        
        await update.message.reply_text(confirm_text, parse_mode='Markdown')
        
        # Aguardar confirmação (simplificado - em produção usar CallbackQuery)
        await asyncio.sleep(2)
        
        # Enviar broadcast
        success_count = 0
        error_count = 0
        
        status_message = await update.message.reply_text('📤 Iniciando broadcast...')
        
        for i, user in enumerate(users):
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=message,
                    parse_mode='Markdown'
                )
                success_count += 1
                
                # Atualizar status a cada 10 usuários
                if (i + 1) % 10 == 0:
                    await status_message.edit_text(
                        f'📤 Enviando broadcast... {i + 1}/{len(users)}\n✅ Sucesso: {success_count}\n❌ Erros: {error_count}'
                    )
                
                # Delay para evitar rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Erro ao enviar para {user['user_id']}: {e}")
        
        # Resultado final
        final_text = f"📢 **Broadcast Concluído**\n\n✅ **Enviados:** {success_count}\n❌ **Erros:** {error_count}\n👥 **Total:** {len(users)}"
        await status_message.edit_text(final_text, parse_mode='Markdown')
    
    async def handle_detailed_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Mostra estatísticas detalhadas do bot"""
        try:
            stats = self.db.get_user_stats()
            recent_users = self.db.get_recent_users(5)
            link_stats = self.db.get_link_click_stats(days=7)
            
            # Montar texto das estatísticas
            stats_text = "📊 **Estatísticas Detalhadas**\n\n"
            
            # Estatísticas gerais
            stats_text += f"👥 **Total de Usuários:** {stats.get('total_users', 0)}\n"
            stats_text += f"🆕 **Novos Hoje:** {stats.get('new_today', 0)}\n"
            stats_text += f"📅 **Novos esta Semana:** {stats.get('new_week', 0)}\n\n"
            
            # Estatísticas do funil
            funnel_stats = stats.get('funnel_stats', {})
            if funnel_stats:
                stats_text += "🎯 **Funil de Conversão:**\n"
                for step, count in funnel_stats.items():
                    step_name = self._get_funnel_step_name(step)
                    stats_text += f"   • {step_name}: {count}\n"
                stats_text += "\n"
            
            # Cliques em links
            if link_stats:
                stats_text += "🔗 **Cliques em Links (7 dias):**\n"
                for link in link_stats:
                    stats_text += f"   • {link['link_type']}: {link['clicks']} cliques ({link['unique_users']} usuários únicos)\n"
                stats_text += "\n"
            
            # Usuários recentes
            if recent_users:
                stats_text += "👤 **Usuários Recentes:**\n"
                for user in recent_users:
                    username = f"@{user['username']}" if user['username'] else "Sem username"
                    stats_text += f"   • {user['first_name']} ({username}) - Passo {user['funnel_step']}\n"
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            await update.message.reply_text('❌ Erro ao obter estatísticas.')
    
    def _get_funnel_step_name(self, step: int) -> str:
        """Converte número do passo em nome legível"""
        step_names = {
            0: "Recém-chegados",
            1: "Mensagem 24h enviada",
            2: "Mensagem 48h enviada",
            3: "Mensagem 72h enviada",
        }
        return step_names.get(step, f"Passo {step}")
    
    async def handle_users_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Lista usuários recentes com detalhes"""
        try:
            users = self.db.get_recent_users(20)
            
            if not users:
                await update.message.reply_text('❌ Nenhum usuário encontrado.')
                return
            
            users_text = f"👥 **Lista de Usuários** (últimos {len(users)})\n\n"
            
            for user in users:
                username = f"@{user['username']}" if user['username'] else "Sem username"
                joined_date = datetime.fromisoformat(user['joined_at']).strftime('%d/%m/%Y %H:%M')
                step_name = self._get_funnel_step_name(user['funnel_step'])
                
                users_text += f"**{user['first_name']}**\n"
                users_text += f"   • ID: `{user['user_id']}`\n"
                users_text += f"   • Username: {username}\n"
                users_text += f"   • Entrou: {joined_date}\n"
                users_text += f"   • Funil: {step_name}\n\n"
            
            await update.message.reply_text(users_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar usuários: {e}")
            await update.message.reply_text('❌ Erro ao listar usuários.')
    
    async def handle_test_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envia mensagem de teste"""
        test_text = "🧪 **Mensagem de Teste**\n\n✅ Bot funcionando perfeitamente!\n\n📊 **Informações do Sistema:**\n"
        test_text += f"• Chat ID: `{update.effective_chat.id}`\n"
        test_text += f"• User ID: `{update.effective_user.id}`\n"
        test_text += f"• Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        test_text += f"• Administrador: {'✅ Sim' if self.is_admin(update.effective_user.id) else '❌ Não'}"
        
        await update.message.reply_text(test_text, parse_mode='Markdown')
    
    async def handle_setphoto_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Informa sobre alteração de foto do bot"""
        info_text = "❌ **Funcionalidade não disponível**\n\n"
        info_text += "📋 A API do Telegram não permite que bots alterem sua própria foto de perfil programaticamente.\n\n"
        info_text += "💡 **Para alterar a foto do bot, você deve:**\n"
        info_text += "1. Acessar @BotFather no Telegram\n"
        info_text += "2. Usar o comando `/setuserpic`\n"
        info_text += "3. Selecionar seu bot\n"
        info_text += "4. Enviar a nova foto"
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
    
    async def handle_admin_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Mostra ajuda dos comandos de administração"""
        help_text = "🔧 **Comandos de Administração**\n\n"
        help_text += "📢 `/admin broadcast <mensagem>` - Enviar mensagem para todos os usuários\n"
        help_text += "📊 `/admin stats` - Estatísticas detalhadas do bot\n"
        help_text += "👥 `/admin users` - Lista dos usuários recentes\n"
        help_text += "🧪 `/admin test` - Mensagem de teste do sistema\n"
        help_text += "📷 `/admin setphoto` - Informações sobre foto do bot\n"
        help_text += "❓ `/admin help` - Esta mensagem de ajuda\n\n"
        help_text += "⚠️ **Nota:** Apenas administradores podem usar estes comandos."
        
        await update.message.reply_text(help_text, parse_mode='Markdown')