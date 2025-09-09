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
        f"🤖 Eu sou o Bot Auge!\n\n"
        f"📈 Estou aqui para ajudar com:\n"
        f"• Mensagens de boas-vindas automáticas\n"
        f"• Moderação avançada do grupo\n"
        f"• Sistema de funil automático\n"
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
    """
    
    if is_admin:
        help_text += """

**Comandos de Admin:**
/broadcast <mensagem> - Envia mensagem para todos
/users - Lista usuários do grupo
/test - Testa funcionalidades
/setphoto - Define foto do bot
/adminhelp - Ajuda completa de admin
        """
    
    help_text += """

**Informações:**
• Bot desenvolvido para o grupo Auge
• Versão: 2.0 - Completo
• Suporte: @AugeSuporte
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



async def initialize_components():
    """Inicializa todos os componentes do bot"""
    global database, admin_handler, funnel_handler, message_handler, welcome_handler, link_tracker
    
    try:
        # Inicializa banco de dados
        database = Database()
        logger.info("✅ Banco de dados inicializado")
        
        # Inicializa handlers
        admin_handler = AdminHandler(database)
        logger.info("✅ AdminHandler inicializado")
        
        funnel_handler = FunnelHandler(database)
        logger.info("✅ FunnelHandler inicializado")
        
        welcome_handler = WelcomeHandler(database, funnel_handler)
        logger.info("✅ WelcomeHandler inicializado")
        
        link_tracker = LinkTracker(database)
        logger.info("✅ LinkTracker inicializado")
        
        message_handler = CustomMessageHandler(database, admin_handler, link_tracker)
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
    
    # Handlers de admin (serão processados pelo AdminHandler)
    application.add_handler(CommandHandler("broadcast", lambda u, c: admin_handler.handle_broadcast(u, c) if admin_handler else None))
    application.add_handler(CommandHandler("users", lambda u, c: admin_handler.handle_users(u, c) if admin_handler else None))
    application.add_handler(CommandHandler("test", lambda u, c: admin_handler.handle_test(u, c) if admin_handler else None))
    application.add_handler(CommandHandler("setphoto", lambda u, c: admin_handler.handle_setphoto(u, c) if admin_handler else None))
    application.add_handler(CommandHandler("adminhelp", lambda u, c: admin_handler.handle_admin_help(u, c) if admin_handler else None))
    
    # Handler para novos membros
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        lambda u, c: welcome_handler.handle_new_members(u, c) if welcome_handler else None
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