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

# Função para mensagens de texto
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde a mensagens de texto"""
    await update.message.reply_text(f'Você disse: {update.message.text}')

# Função para tratar erros
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log de erros causados por Updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

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
    
    # Handler para mensagens de texto (echo)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Handler para erros
    application.add_error_handler(error_handler)
    
    # Iniciar o bot
    logger.info("🚀 Iniciando bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()