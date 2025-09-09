import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from telegram.ext import ContextTypes
from database import Database

logger = logging.getLogger(__name__)

class FunnelHandler:
    def __init__(self, bot, database: Database):
        self.bot = bot
        self.db = database
        self.group_chat_id = os.getenv('GROUP_CHAT_ID')
        self.duvidas_group_link = os.getenv('DUVIDAS_GROUP_LINK', 'https://t.me/seu_grupo_duvidas')
    
    async def check_funnel_messages(self) -> None:
        """Verifica e envia mensagens do funil automaticamente"""
        try:
            logger.info("🔄 Verificando mensagens do funil...")
            
            # Verificar usuários para mensagem de 24h (step 0 -> 1)
            await self.send_funnel_message_24h()
            
            # Verificar usuários para mensagem de 48h (step 1 -> 2)
            await self.send_funnel_message_48h()
            
            # Verificar usuários para mensagem de 72h (step 2 -> 3)
            await self.send_funnel_message_72h()
            
            logger.info("✅ Verificação do funil concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar mensagens do funil: {e}")
    
    async def send_funnel_message_24h(self) -> None:
        """Envia mensagem de 24h após entrada no grupo"""
        users = self.db.get_users_for_funnel_step(0, 24)
        
        logger.info(f"📧 Enviando mensagens 24h para {len(users)} usuários")
        
        for user in users:
            try:
                message = self.get_funnel_message_24h(user['first_name'])
                
                await self.bot.send_message(
                    chat_id=user['user_id'],
                    text=message['text'],
                    parse_mode=message['parse_mode'],
                    disable_web_page_preview=message.get('disable_web_page_preview', False)
                )
                
                # Atualizar passo do funil
                self.db.update_user_funnel_step(user['user_id'], 1)
                
                logger.info(f"📧 Mensagem 24h enviada para: {user['first_name']} ({user['user_id']})")
                
                # Delay para evitar spam
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem 24h para {user['user_id']}: {e}")
    
    async def send_funnel_message_48h(self) -> None:
        """Envia mensagem de 48h após primeira mensagem"""
        users = self.db.get_users_for_funnel_step(1, 48)
        
        logger.info(f"📧 Enviando mensagens 48h para {len(users)} usuários")
        
        for user in users:
            try:
                message = self.get_funnel_message_48h(user['first_name'])
                
                await self.bot.send_message(
                    chat_id=user['user_id'],
                    text=message['text'],
                    parse_mode=message['parse_mode'],
                    disable_web_page_preview=message.get('disable_web_page_preview', False)
                )
                
                # Atualizar passo do funil
                self.db.update_user_funnel_step(user['user_id'], 2)
                
                logger.info(f"📧 Mensagem 48h enviada para: {user['first_name']} ({user['user_id']})")
                
                # Delay para evitar spam
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem 48h para {user['user_id']}: {e}")
    
    async def send_funnel_message_72h(self) -> None:
        """Envia mensagem de 72h após segunda mensagem"""
        users = self.db.get_users_for_funnel_step(2, 72)
        
        logger.info(f"📧 Enviando mensagens 72h para {len(users)} usuários")
        
        for user in users:
            try:
                message = self.get_funnel_message_72h(user['first_name'])
                
                await self.bot.send_message(
                    chat_id=user['user_id'],
                    text=message['text'],
                    parse_mode=message['parse_mode'],
                    disable_web_page_preview=message.get('disable_web_page_preview', False)
                )
                
                # Atualizar passo do funil
                self.db.update_user_funnel_step(user['user_id'], 3)
                
                logger.info(f"📧 Mensagem 72h enviada para: {user['first_name']} ({user['user_id']})")
                
                # Delay para evitar spam
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem 72h para {user['user_id']}: {e}")
    
    def get_funnel_message_24h(self, first_name: str) -> Dict:
        """Retorna a mensagem de 24h personalizada"""
        text = f"""👋 Olá, {first_name}!

🎯 **Bem-vindo(a) ao nosso grupo de traders!**

Vi que você entrou no grupo ontem e queria te dar algumas dicas importantes para aproveitar ao máximo nossa comunidade:

📚 **Para iniciantes:**
• Leia as mensagens fixadas do grupo
• Observe as análises compartilhadas pelos membros
• Não tenha pressa - aprendizado leva tempo

💡 **Dicas importantes:**
• Nunca invista mais do que pode perder
• Sempre faça sua própria análise
• Gerencie seus riscos adequadamente

🔗 **Links úteis:**
• [Guia para Iniciantes](https://exemplo.com/guia)
• [Estratégias Básicas](https://exemplo.com/estrategias)
• [Gerenciamento de Risco](https://exemplo.com/risco)

❓ **Tem alguma dúvida?** Fique à vontade para perguntar no grupo!

🚀 Vamos juntos nessa jornada de aprendizado!"""
        
        return {
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
    
    def get_funnel_message_48h(self, first_name: str) -> Dict:
        """Retorna a mensagem de 48h personalizada"""
        text = f"""📈 Oi {first_name}!

🎯 **Como está sendo sua experiência no grupo?**

Já faz 2 dias que você está conosco e espero que esteja aproveitando o conteúdo compartilhado!

💪 **Próximos passos para acelerar seu aprendizado:**

1️⃣ **Participe ativamente:**
   • Comente nas análises
   • Compartilhe suas dúvidas
   • Interaja com outros membros

2️⃣ **Estude consistentemente:**
   • Dedique pelo menos 30min/dia
   • Pratique em conta demo primeiro
   • Anote seus aprendizados

3️⃣ **Recursos recomendados:**
   • [Curso Básico de Trading](https://exemplo.com/curso)
   • [Análise Técnica Essencial](https://exemplo.com/analise)
   • [Psicologia do Trader](https://exemplo.com/psicologia)

💬 **Grupo de Dúvidas:**
Para perguntas mais específicas, temos um grupo dedicado:
{self.duvidas_group_link}

🎯 **Lembre-se:** Consistência é a chave do sucesso!

📊 Continue acompanhando nossas análises e em breve você estará fazendo as suas próprias!"""
        
        return {
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
    
    def get_funnel_message_72h(self, first_name: str) -> Dict:
        """Retorna a mensagem de 72h personalizada"""
        text = f"""🚀 {first_name}, você está evoluindo!

🎉 **Parabéns por completar 3 dias conosco!**

Essa dedicação já mostra que você tem o mindset certo para o trading.

🎯 **Chegou a hora de dar o próximo passo:**

📊 **Análise Prática:**
• Comece a fazer suas próprias análises
• Use as ferramentas que ensinamos
• Compartilhe suas ideias no grupo

💰 **Gestão de Capital:**
• Defina seu capital de risco
• Estabeleça metas realistas
• Nunca arrisque mais que 2% por operação

🧠 **Desenvolvimento Mental:**
• Mantenha um diário de trades
• Controle suas emoções
• Aprenda com os erros

🎁 **Recursos Exclusivos:**
• [Planilha de Controle](https://exemplo.com/planilha)
• [Checklist do Trader](https://exemplo.com/checklist)
• [Estratégias Avançadas](https://exemplo.com/avancado)

💡 **Dica especial:**
Os traders mais bem-sucedidos são aqueles que nunca param de aprender. Continue estudando, praticando e interagindo!

🔥 **Você tem potencial para ser um grande trader!**

Qualquer dúvida, estamos aqui para ajudar. Vamos juntos rumo ao sucesso! 🚀"""
        
        return {
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
    
    async def schedule_funnel_check(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Agenda verificação periódica do funil (para usar com JobQueue)"""
        await self.check_funnel_messages()
    
    def delay(self, ms: int) -> None:
        """Função de delay (compatibilidade com código JavaScript)"""
        return asyncio.sleep(ms / 1000)