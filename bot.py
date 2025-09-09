import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde ao comando /start"""
    await update.message.reply_text('🚀 Bot ativo no Railway!')

# Função para o comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde ao comando /help"""
    help_text = """
🤖 *Comandos disponíveis:*

/start - Iniciar o bot
/help - Mostrar esta mensagem de ajuda
/status - Verificar status do bot

✅ Bot rodando no Railway!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Função para o comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra o status do bot"""
    await update.message.reply_text('✅ Bot funcionando perfeitamente no Railway!')

# Função para dar boas-vindas a novos membros
async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dá boas-vindas a novos membros do grupo"""
    for member in update.message.new_chat_members:
        if member.id != context.bot.id:  # Não dar boas-vindas ao próprio bot
            welcome_text = f"🎉 Bem-vindo(a) ao grupo, {member.first_name}!\n\n✨ Esperamos que você se divirta aqui!\n\nDigite /help para ver os comandos disponíveis."
            await update.message.reply_text(welcome_text)
        else:
            # Mensagem quando o bot é adicionado ao grupo
            bot_welcome = """
🤖 **Olá! Sou o Bot Auge!**

✅ Fui adicionado com sucesso ao grupo!

Comandos disponíveis:
/start - Iniciar
/help - Ajuda
/status - Status do bot

Para funcionar perfeitamente, me adicione como administrador! 👑
            """
            await update.message.reply_text(bot_welcome, parse_mode='Markdown')

# Função para mensagens de texto
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde a mensagens de texto"""
    await update.message.reply_text(f'Você disse: {update.message.text}')

# Função para tratar erros
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log de erros causados por Updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# Adicione esta função para detectar quando o bot é adicionado a um grupo
async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensagem de boas-vindas quando o bot é adicionado ao grupo"""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            welcome_text = """
🤖 **Olá! Sou o Bot Auge!**

✅ Fui adicionado com sucesso ao grupo!

Comandos disponíveis:
/start - Iniciar
/help - Ajuda
/status - Status do bot

Para funcionar perfeitamente, me adicione como administrador! 👑
            """
            await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Adicione esta função para mensagens de boas-vindas a novos membros
async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dá boas-vindas a novos membros do grupo"""
    for member in update.message.new_chat_members:
        if member.id != context.bot.id:  # Não dar boas-vindas ao próprio bot
            welcome_text = f"🎉 Bem-vindo(a) ao grupo, {member.first_name}!"
            await update.message.reply_text(welcome_text)

# No main(), adicione estes handlers:
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))

def main() -> None:
    """Função principal para iniciar o bot"""
    # Obter token do bot das variáveis de ambiente
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        logger.error("❌ BOT_TOKEN não encontrado nas variáveis de ambiente!")
        return
    
    # Criar aplicação
    application = Application.builder().token(token).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    
    # Handler para novos membros (boas-vindas)
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    
    # Handler para mensagens de texto (echo)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Handler para erros
    application.add_error_handler(error_handler)
    
    # Iniciar o bot
    logger.info("🚀 Iniciando bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()