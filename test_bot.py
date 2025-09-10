#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token do bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de teste simples"""
    user = update.effective_user
    chat = update.effective_chat
    
    logger.info(f"Comando /test executado por {user.first_name} ({user.id}) no chat {chat.id}")
    
    await update.message.reply_text(
        f"✅ Bot funcionando!\n\n"
        f"👤 Usuário: {user.first_name}\n"
        f"💬 Chat ID: {chat.id}\n"
        f"🤖 Bot respondendo corretamente!"
    )

def main():
    """Função principal"""
    if not BOT_TOKEN:
        logger.error("Token do bot não encontrado!")
        return
    
    # Criar aplicação com timeouts
    application = Application.builder().token(BOT_TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()
    
    # Adicionar handler de teste
    application.add_handler(CommandHandler("test", test_command))
    
    logger.info("🧪 Bot de teste iniciado!")
    logger.info("Digite /test em qualquer chat para testar")
    
    try:
        # Usar webhook mode para evitar conflito
        application.run_polling(drop_pending_updates=True, allowed_updates=['message'])
    except Exception as e:
        logger.error(f"Erro: {e}")
        logger.error(f"Tipo: {type(e).__name__}")

if __name__ == '__main__':
    main()