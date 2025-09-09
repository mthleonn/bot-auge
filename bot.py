import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Importa os handlers personalizados
from database import Database
from admin_handler import AdminHandler
from funnel_handler import FunnelHandler
from message_handler import MessageHandler as CustomMessageHandler
from welcome_handler import WelcomeHandler
from link_tracker import LinkTracker

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
# Criar diretório de logs se não existir
import os
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializa componentes globais
database = None
admin_handler = None
funnel_handler = None
message_handler = None
welcome_handler = None
link_tracker = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Adiciona usuário ao banco de dados se não existir
    if database:
        user_data = {
            'user_id': user.id,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'username': user.username or '',
            'chat_id': chat.id,
            'join_date': None  # Será definido quando entrar no grupo
        }
        database.add_user(user_data)
    
    await update.message.reply_html(
        f"Olá {user.mention_html()}!\n\n"
        f"🎯 **Bot Auge Traders ativo!**\n\n"
        f"📈 Funcionalidades disponíveis:\n"
        f"• Sistema de boas-vindas personalizado\n"
        f"• Moderação avançada do grupo\n"
        f"• Funil automático de mensagens\n"
        f"• Estatísticas detalhadas\n"
        f"• Rastreamento de links\n\n"
        f"Use /help para ver todos os comandos disponíveis."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    user = update.effective_user
    is_admin = admin_handler and await admin_handler.is_admin(user.id)
    
    help_text = """
🤖 **Comandos do Bot Auge**

**Comandos Gerais:**
/start - Inicia o bot
/help - Mostra esta mensagem
/status - Status do bot
/stats - Estatísticas do grupo
/links - Estatísticas de links
/testwelcome - Testa mensagem de boas-vindas
    """
    
    if is_admin:
        help_text += """

**Comandos de Admin:**
/broadcast <mensagem> - Envia mensagem para todos
/users - Lista usuários do grupo
/test - Testa funcionalidades
/setphoto - Define foto do bot
/adminhelp - Ajuda completa de admin
/testmsg - Mostra todas as mensagens automáticas
/reuniao - Envia lembrete da reunião semanal
/setmeeting <link> - Define novo link da reunião
        """
    
    help_text += """

**Informações:**
• Bot desenvolvido para o grupo Auge
• Versão: 2.1 - Atualizado
• Suporte: @AugeSuporte
• Reunião semanal: Segundas às 19h
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    try:
        # Verifica status dos componentes
        db_status = "✅ Conectado" if database else "❌ Desconectado"
        admin_status = "✅ Ativo" if admin_handler else "❌ Inativo"
        funnel_status = "✅ Ativo" if funnel_handler else "❌ Inativo"
        welcome_status = "✅ Ativo" if welcome_handler else "❌ Inativo"
        tracker_status = "✅ Ativo" if link_tracker else "❌ Inativo"
        
        # Estatísticas básicas
        total_users = len(database.get_all_users()) if database else 0
        
        status_text = f"""
✅ **Bot Auge - Status Completo**

🔧 **Componentes:**
• Banco de dados: {db_status}
• Admin Handler: {admin_status}
• Funil Handler: {funnel_status}
• Welcome Handler: {welcome_status}
• Link Tracker: {tracker_status}

📊 **Estatísticas:**
• Total de usuários: {total_users}
• Status geral: Online
• Versão: 2.0

🕐 **Última atualização:** Agora
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando status: {e}")
        await update.message.reply_text("❌ Erro ao obter status do bot.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Estatísticas do grupo"""
    try:
        if not database:
            await update.message.reply_text("❌ Banco de dados não disponível.")
            return
        
        chat_id = update.effective_chat.id
        stats = await welcome_handler.get_welcome_stats(chat_id) if welcome_handler else "Estatísticas não disponíveis"
        
        await update.message.reply_text(stats, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando stats: {e}")
        await update.message.reply_text("❌ Erro ao obter estatísticas.")

async def links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /links - Estatísticas de links"""
    try:
        if not link_tracker:
            await update.message.reply_text("❌ Rastreador de links não disponível.")
            return
        
        chat_id = update.effective_chat.id
        stats = await link_tracker.get_link_statistics(chat_id, 7)
        
        await update.message.reply_text(stats, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando links: {e}")
        await update.message.reply_text("❌ Erro ao obter estatísticas de links.")

async def test_welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /testwelcome - Testa mensagem de boas-vindas"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"🧪 Teste de boas-vindas solicitado por {user.first_name} no chat {chat.id}")
        
        if welcome_handler:
            # Simula um novo membro (o próprio usuário)
            fake_member = type('Member', (), {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username
            })()
            
            await welcome_handler._send_welcome_message(update, context, fake_member, chat)
            logger.info(f"✅ Mensagem de teste enviada para {user.first_name}")
        else:
            await update.message.reply_text("❌ WelcomeHandler não está inicializado!")
            logger.error("❌ WelcomeHandler não inicializado para teste")
            
    except Exception as e:
        logger.error(f"Erro no comando /testwelcome: {e}")
        await update.message.reply_text(f"❌ Erro ao testar boas-vindas: {e}")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa todas as mensagens através do MessageHandler"""
    try:
        if message_handler:
            await message_handler.process_message(update, context)
        
        # Processa links se disponível
        if link_tracker:
            await link_tracker.process_message_links(update, context)
            
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Lida com erros"""
    logger.error(f"Erro causado por update {update}: {context.error}")
    
    # Notifica admins se configurado
    if admin_handler and os.getenv('NOTIFY_ADMIN_ON_ERROR', 'true').lower() == 'true':
        try:
            await admin_handler.notify_admins(f"❌ Erro no bot: {context.error}")
        except:
            pass

async def show_all_automated_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra todas as mensagens automáticas do sistema"""
    try:
        messages_info = """
🧪 **Todas as Mensagens Automáticas do Bot**

📅 **Mensagens Diárias:**
• Mensagem diária às 06:00 (timezone: America/Sao_Paulo)
• Conteúdo: Análises e informações do dia

📈 **Funil de Mensagens:**
• 24h após entrada: Mensagem de engajamento
• 48h após entrada: Convite para mentoria
• 72h após entrada: Lembrete de participação

👋 **Mensagens de Boas-vindas:**
• Automática para novos membros
• Personalizada por tipo de grupo

📞 **Reunião Semanal:**
• Toda segunda-feira às 19:00
• Lembrete enviado às 18:00
• Link da reunião incluído

🔧 **Para testar individualmente:**
• `/testwelcome` - Testa boas-vindas
• `/test` - Teste geral do sistema
• `/admin test` - Teste administrativo
        """
        
        await update.message.reply_text(messages_info, parse_mode='Markdown')
        
        # Enviar exemplo de cada tipo de mensagem
        if funnel_handler:
            await update.message.reply_text("\n📨 **Exemplo - Mensagem 24h:**")
            try:
                await funnel_handler.send_24h_message(update.effective_chat.id, update.effective_user.first_name)
            except:
                await update.message.reply_text("Exemplo de mensagem 24h não disponível")
            
            await asyncio.sleep(1)
            await update.message.reply_text("\n📨 **Exemplo - Mensagem 48h:**")
            try:
                await funnel_handler.send_48h_message(update.effective_chat.id, update.effective_user.first_name)
            except:
                await update.message.reply_text("Exemplo de mensagem 48h não disponível")
            
            await asyncio.sleep(1)
            await update.message.reply_text("\n📨 **Exemplo - Mensagem 72h:**")
            try:
                await funnel_handler.send_72h_message(update.effective_chat.id, update.effective_user.first_name)
            except:
                await update.message.reply_text("Exemplo de mensagem 72h não disponível")
        
    except Exception as e:
        logger.error(f"Erro ao mostrar mensagens automáticas: {e}")
        await update.message.reply_text("❌ Erro ao carregar mensagens automáticas.")

async def send_meeting_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia lembrete da reunião semanal"""
    try:
        # Obter link da reunião do banco de dados
        meeting_link = database.get_meeting_link() if database else "https://meet.google.com/auge-traders-weekly"
        
        meeting_message = f"""
📞 **REUNIÃO SEMANAL AUGE TRADERS** 📞

🗓️ **Toda Segunda-feira às 19:00**
⏰ **Horário:** 19:00 (Brasília)
🔗 **Link:** {meeting_link}

💡 **Pauta desta semana:**
• Review da semana anterior
• Estratégias para próxima semana
• Tire suas dúvidas ao vivo
• Networking com outros traders

👥 **Presença confirmada?** Nos vemos lá!
        """
        
        await update.message.reply_text(meeting_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao enviar lembrete da reunião: {e}")
        await update.message.reply_text("❌ Erro ao enviar lembrete da reunião.")

async def set_meeting_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Define novo link da reunião"""
    try:
        if not context.args:
            current_link = database.get_meeting_link() if database else os.getenv('MEETING_LINK', 'Não definido')
            help_message = f"""
🔗 **Configurar Link da Reunião**

**Link atual:** {current_link}

**Como usar:**
`/setmeeting https://meet.google.com/seu-novo-link`

**Exemplo:**
`/setmeeting https://meet.google.com/abc-defg-hij`
            """
            await update.message.reply_text(help_message, parse_mode='Markdown')
            return
        
        new_link = context.args[0]
        
        # Validar se é um link válido
        if not (new_link.startswith('http://') or new_link.startswith('https://')):
            await update.message.reply_text("❌ Por favor, forneça um link válido (deve começar com http:// ou https://)")
            return
        
        # Salvar no banco de dados
        if database:
            database.set_meeting_link(new_link)
            success_message = f"""
✅ **Link da reunião atualizado!**

🔗 **Novo link:** {new_link}

📝 **Alteração salva no banco de dados.**
            """
        else:
            success_message = f"""
⚠️ **Link temporariamente atualizado!**

🔗 **Novo link:** {new_link}

📝 **Nota:** Banco de dados não disponível. Para que a alteração seja permanente, você precisa atualizar a variável de ambiente `MEETING_LINK` no seu servidor.
            """
        
        await update.message.reply_text(success_message, parse_mode='Markdown')
        
        # Log da alteração
        logger.info(f"Link da reunião alterado por {update.effective_user.first_name}: {new_link}")
        
    except Exception as e:
        logger.error(f"Erro ao definir link da reunião: {e}")
        await update.message.reply_text("❌ Erro ao definir link da reunião.")



async def initialize_components():
    """Inicializa todos os componentes do bot"""
    global database, admin_handler, funnel_handler, message_handler, welcome_handler, link_tracker
    
    try:
        # Inicializa banco de dados
        database = Database()
        logger.info("✅ Banco de dados inicializado")
        
        # Inicializa handlers
        admin_handler = AdminHandler(None, database)  # bot será definido depois
        logger.info("✅ AdminHandler inicializado")
        
        funnel_handler = FunnelHandler(None, database)  # bot será definido depois
        logger.info("✅ FunnelHandler inicializado")
        
        welcome_handler = WelcomeHandler(database, funnel_handler)
        logger.info("✅ WelcomeHandler inicializado")
        
        link_tracker = LinkTracker(database)
        logger.info("✅ LinkTracker inicializado")
        
        message_handler = CustomMessageHandler(None, database, admin_handler)
        logger.info("✅ MessageHandler inicializado")
        
        # Inicia tarefas em background
        await funnel_handler.start_background_tasks()
        logger.info("✅ Tarefas em background iniciadas")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar componentes: {e}")
        return False

def main():
    """Função principal"""
    # Obtém o token do bot
    token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN')
    if not token:
        logger.error("Token do bot não encontrado! Verifique o arquivo .env")
        return
    
    # Cria diretórios necessários
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Cria a aplicação
    application = Application.builder().token(token).build()
    
    # Inicializa componentes
    async def post_init(app):
        success = await initialize_components()
        if not success:
            logger.error("Falha ao inicializar componentes. Bot pode não funcionar corretamente.")
    
    application.post_init = post_init
    
    # Adiciona handlers básicos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("links", links_command))
    application.add_handler(CommandHandler("testwelcome", test_welcome_command))
    
    # Comando testmsg melhorado
    async def testmsg_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler and await admin_handler.is_admin(update.effective_user.id):
            await show_all_automated_messages(update, context)
        else:
            await update.message.reply_text("❌ Comando disponível apenas para administradores.")
    
    application.add_handler(CommandHandler("testmsg", testmsg_wrapper))
    
    # Comandos para reunião semanal
    async def reuniao_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler and await admin_handler.is_admin(update.effective_user.id):
            await send_meeting_reminder(update, context)
        else:
            await update.message.reply_text("❌ Comando disponível apenas para administradores.")
    
    async def setmeeting_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler and await admin_handler.is_admin(update.effective_user.id):
            await set_meeting_link(update, context)
        else:
            await update.message.reply_text("❌ Comando disponível apenas para administradores.")
    
    application.add_handler(CommandHandler("reuniao", reuniao_wrapper))
    application.add_handler(CommandHandler("setmeeting", setmeeting_wrapper))
    
    # Handlers de admin corrigidos
    async def broadcast_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler:
            message = ' '.join(context.args) if context.args else ''
            await admin_handler.handle_broadcast(update, context, message)
        else:
            await update.message.reply_text("❌ Sistema administrativo não disponível.")
    
    async def users_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler:
            await admin_handler.handle_users_list(update, context)
        else:
            await update.message.reply_text("❌ Sistema administrativo não disponível.")
    
    async def test_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler:
            await admin_handler.handle_test_message(update, context)
        else:
            await update.message.reply_text("❌ Sistema administrativo não disponível.")
    
    async def setphoto_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler:
            await admin_handler.handle_setphoto_info(update, context)
        else:
            await update.message.reply_text("❌ Sistema administrativo não disponível.")
    
    async def adminhelp_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if admin_handler:
            await admin_handler.handle_admin_help(update, context)
        else:
            await update.message.reply_text("❌ Sistema administrativo não disponível.")
    
    application.add_handler(CommandHandler("broadcast", broadcast_wrapper))
    application.add_handler(CommandHandler("users", users_wrapper))
    application.add_handler(CommandHandler("test", test_wrapper))
    application.add_handler(CommandHandler("setphoto", setphoto_wrapper))
    application.add_handler(CommandHandler("adminhelp", adminhelp_wrapper))
    
    # Handler para novos membros
    async def handle_new_members_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"🔍 Novo membro detectado! Chat: {update.effective_chat.id}, Membros: {[m.first_name for m in update.message.new_chat_members]}")
        if welcome_handler:
            await welcome_handler.handle_new_members(update, context)
        else:
            logger.error("❌ WelcomeHandler não inicializado!")
    
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        handle_new_members_wrapper
    ))
    
    # Handler para todas as mensagens de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))
    
    # Handler de erros
    application.add_error_handler(error_handler)
    
    # Inicia o bot
    logger.info("🚀 Bot Auge iniciado com todas as funcionalidades!")
    logger.info("📋 Funcionalidades ativas:")
    logger.info("   • Sistema de boas-vindas avançado")
    logger.info("   • Funil automático de mensagens")
    logger.info("   • Moderação inteligente")
    logger.info("   • Rastreamento de links")
    logger.info("   • Comandos administrativos")
    logger.info("   • Estatísticas detalhadas")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()