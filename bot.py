import os
import logging
import sqlite3
from datetime import datetime, time as dt_time
import time
import asyncio
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
from telegram.error import NetworkError, TimedOut, Conflict
from dotenv import load_dotenv
from flask import Flask, request
import threading

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configurações do bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_CHAT_ID = int(os.getenv('GROUP_CHAT_ID', '').strip().replace('=', ''))
DUVIDAS_GROUP_CHAT_ID = int(os.getenv('DUVIDAS_GROUP_CHAT_ID', '').strip().replace('=', ''))
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
DUVIDAS_GROUP_LINK = os.getenv('DUVIDAS_GROUP_LINK')
MENTORIA_LINK = os.getenv('MENTORIA_LINK')

# Configurações do Railway
PORT = int(os.getenv('PORT', 8000))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # 'production' para Railway

class AugeTradersBot:
    def __init__(self):
        self.db_path = './data/bot.db'
        self.init_database()
        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.messages = self.load_predefined_messages()
    
    def init_database(self):
        """Inicializa o banco de dados SQLite"""
        os.makedirs('./data', exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de mensagens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT,
                message_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                group_id INTEGER
            )
        ''')
        
        # Tabela de reuniões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_link TEXT,
                meeting_date TEXT,
                meeting_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados inicializado com sucesso")
    
    def load_predefined_messages(self):
        """Carrega mensagens prontas do sistema"""
        return {
            'welcome_main': """🎯 **Bem-vindo(a) ao Auge Traders!** 🎯

Olá {name}! 👋

📊 Aqui você receberá **análises diárias do pré-mercado** pelos nossos mentores **Rafael** e **Daniel**, com:
• Possíveis **entradas** e **saídas**
• Estratégias testadas e aprovadas
• Acompanhamento em tempo real

⏰ **Análises enviadas às 6h** todos os dias úteis!

🚀 Acelere seus resultados:
[🎯 Mentoria Completa]({mentoria_link})
[❓ Grupo de Dúvidas]({duvidas_link})

💪 Vamos conquistar a consistência juntos!""",
            
            'morning_alert': """🌅 **BOM DIA, TRADERS!** 🌅

⏰ **6h em ponto** - Análise do pré-mercado chegando!

📊 Rafael e Daniel estão preparando:
• Setups do dia
• Possíveis entradas
• Níveis de saída
• Gestão de risco

👀 **Fiquem atentos** - oportunidades não esperam!

💪 Vamos fazer um dia **consistente**!""",
            
            'market_alert': """🚨 **ALERTA DE MERCADO** 🚨

📊 **Movimento importante** detectado!

⚡ **Atenção traders:**
• Acompanhem os níveis indicados
• Aguardem confirmação
• Mantenham a disciplina

🎯 **Oportunidade pode estar se formando!**

💪 Foco e execução!""",
            
            'motivational': """🔥 **MINDSET DE TRADER VENCEDOR** 🔥

💭 **Lembre-se:**
"O mercado recompensa a **disciplina**, não a pressa."

✅ **Trader consistente:**
• Segue o plano
• Controla as emoções
• Estuda constantemente
• Respeita o risco

📚 **Continue estudando** - conhecimento é poder!

🎯 [Acelere seu aprendizado na Mentoria]({mentoria_link})""",
            
            'engagement': """💪 **TRADERS, COMO ESTÁ O DIA?** 💪

📊 **Compartilhem:**
• Como estão seguindo o plano?
• Alguma dúvida sobre os setups?
• Resultados do dia?

🤝 **Juntos somos mais fortes!**

❓ **Dúvidas?** Entre no nosso grupo:
[💬 Grupo de Dúvidas]({duvidas_link})""",
            
            'doubts_reminder': """❓ **TEM DÚVIDAS? NÓS TEMOS RESPOSTAS!** ❓

🎯 **Grupo exclusivo** para esclarecer:
• Análises técnicas
• Estratégias de entrada
• Gestão de risco
• Psicologia do trader

👥 **Nossa equipe** está pronta para ajudar!

[💬 Acesse o Grupo de Dúvidas]({duvidas_link})

🚀 **Não fique com dúvidas - tire agora!**""",
            
            'mentoria_promo': """🎓 **QUER ACELERAR SEUS RESULTADOS?** 🎓

🚀 **Mentoria Auge Traders:**
• Aulas ao vivo com Rafael e Daniel
• Estratégias exclusivas
• Acompanhamento personalizado
• Comunidade de traders vencedores

💡 **Transforme** sua operação de vez!

[🎯 Conheça a Mentoria Completa]({mentoria_link})

⏰ **Vagas limitadas** - não perca!""",
            
            'discipline': """⚖️ **DISCIPLINA = CONSISTÊNCIA** ⚖️

🎯 **Trader disciplinado:**
• Não força trades
• Espera o setup perfeito
• Corta loss rapidamente
• Deixa o lucro correr

📈 **Resultado:** Conta crescendo mês após mês!

💪 **Seja paciente** - o mercado sempre oferece novas oportunidades!

🔥 **Foco no processo, não no resultado!**""",
            
            'weekend': """🏁 **SEMANA FINALIZADA!** 🏁

📊 **Hora do review:**
• Como foi sua semana de trades?
• Objetivos alcançados?
• Lições aprendidas?

🔄 **Fim de semana é para:**
• Descansar a mente
• Estudar estratégias
• Planejar próxima semana

💪 **Segunda-feira voltamos** ainda mais fortes!

🎯 **Bom descanso, traders!**""",
            
            'motivation': """🌟 **VOCÊ ESTÁ NO CAMINHO CERTO!** 🌟

🎯 **Lembre-se:**
• Todo trader passou por dificuldades
• Consistência vem com tempo e prática
• Cada erro é uma lição valiosa
• Persistência é a chave do sucesso

📈 **Continue firme** na sua jornada!

🚀 **O sucesso** está mais próximo do que imagina!

💪 **Auge Traders** - juntos somos imparáveis!"""
        }
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Adiciona ou atualiza usuário no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    def log_message(self, user_id, message_text, group_id):
        """Registra mensagem no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (user_id, message_text, group_id)
            VALUES (?, ?, ?)
        ''', (user_id, message_text, group_id))
        
        conn.commit()
        conn.close()
    
    def save_meeting_config(self, link, date, time):
        """Salva configuração de reunião no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Desativar reuniões anteriores
            cursor.execute('UPDATE meetings SET is_active = 0')
            
            # Inserir nova configuração
            cursor.execute('''
                INSERT INTO meetings (meeting_link, meeting_date, meeting_time)
                VALUES (?, ?, ?)
            ''', (link, date, time))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração de reunião: {e}")
            return False
    
    def get_active_meeting(self):
        """Recupera a configuração ativa de reunião"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT meeting_link, meeting_date, meeting_time 
                FROM meetings 
                WHERE is_active = 1 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'link': result[0],
                    'date': result[1],
                    'time': result[2]
                }
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar configuração de reunião: {e}")
            return None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Mensagem de boas-vindas"""
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"[DEBUG] Comando /start executado por {user.first_name} ({user.id}) no chat {chat.id}")
        
        try:
            self.add_user(user.id, user.username, user.first_name, user.last_name)
            
            welcome_text = f"""🎯 *Bem-vindo ao Bot Auge Traders!*

Olá {user.first_name}! 👋

Este é o bot oficial da comunidade Auge Traders. Aqui você encontrará:

📊 Análises de mercado em tempo real
💡 Dicas e estratégias de trading
🎓 Conteúdo educacional exclusivo
📈 Sinais e oportunidades

🔗 *Links importantes:*
[🔗 Grupo de Dúvidas]({DUVIDAS_GROUP_LINK})
[🎯 Mentoria Auge Traders]({MENTORIA_LINK})

👥 **Nossa equipe** está pronta para ajudar!

Vamos juntos rumo ao sucesso! 🚀"""
            
            keyboard = [
                [InlineKeyboardButton("📊 Grupo de Dúvidas", url=DUVIDAS_GROUP_LINK)],
                [InlineKeyboardButton("🎯 Mentoria Day Trade", url=MENTORIA_LINK)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            logger.info(f"[DEBUG] Enviando mensagem de boas-vindas para {user.first_name}")
            
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            logger.info(f"[DEBUG] Comando /start executado com sucesso por {user.first_name} ({user.id})")
        except Exception as e:
            logger.error(f"[ERROR] Erro no comando /start: {e}")
            raise
    
    async def send_predefined_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_key: str):
        """Envia uma mensagem predefinida"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
            return
        
        if message_key not in self.messages:
            await update.message.reply_text(f"❌ Mensagem '{message_key}' não encontrada.")
            return
        
        message_text = self.messages[message_key].format(
            mentoria_link=MENTORIA_LINK,
            duvidas_link=DUVIDAS_GROUP_LINK
        )
        
        # Enviar para o grupo principal
        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=message_text,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            await update.message.reply_text(f"✅ Mensagem '{message_key}' enviada com sucesso!")
            logger.info(f"Mensagem '{message_key}' enviada por admin {update.effective_user.id}")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao enviar mensagem: {str(e)}")
            logger.error(f"Erro ao enviar mensagem '{message_key}': {e}")
    
    # Comandos específicos para cada mensagem
    async def cmd_morning_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /morning - Envia alerta matinal"""
        await self.send_predefined_message(update, context, 'morning_alert')
    
    async def cmd_market_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alert - Envia alerta de mercado"""
        await self.send_predefined_message(update, context, 'market_alert')
    
    async def cmd_motivational(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /motivacao - Envia mensagem motivacional"""
        await self.send_predefined_message(update, context, 'motivational')
    
    async def cmd_engagement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /engajamento - Envia mensagem de engajamento"""
        await self.send_predefined_message(update, context, 'engagement')
    
    async def cmd_doubts_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /duvidas - Lembra sobre grupo de dúvidas"""
        await self.send_predefined_message(update, context, 'doubts_reminder')
    
    async def cmd_mentoria_promo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /mentoria - Promove a mentoria"""
        await self.send_predefined_message(update, context, 'mentoria_promo')
    
    async def cmd_discipline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /disciplina - Mensagem sobre disciplina"""
        await self.send_predefined_message(update, context, 'discipline')
    
    async def cmd_weekend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /weekend - Mensagem de fim de semana"""
        await self.send_predefined_message(update, context, 'weekend')
    
    async def cmd_motivation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /motivacao_geral - Mensagem motivacional geral"""
        await self.send_predefined_message(update, context, 'motivation')
    
    async def cmd_list_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /mensagens - Lista todas as mensagens disponíveis"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
            return
        
        commands_list = """
📋 **Comandos de Mensagens Disponíveis:**

🌅 `/morning` - Alerta matinal (6h)
🚨 `/alert` - Alerta de mercado
🔥 `/motivacao` - Mindset de trader
💪 `/engajamento` - Interação com grupo
❓ `/duvidas` - Lembrete grupo dúvidas
🎓 `/mentoria` - Promoção mentoria
⚖️ `/disciplina` - Mensagem disciplina
🏁 `/weekend` - Fim de semana
🌟 `/motivacao_geral` - Motivação geral

🏢 **Comandos de Reunião:**
📝 `/set_meeting` - Configurar reunião (link, data, hora)
🧪 `/test_meeting` - Testar mensagem de reunião

📋 `/mensagens` - Esta lista
📊 `/stats` - Estatísticas do bot

💡 **Uso:** Digite o comando para enviar a mensagem correspondente ao grupo principal.
        """
        
        await update.message.reply_text(commands_list, parse_mode='Markdown')
        logger.info(f"Lista de comandos solicitada por admin {update.effective_user.id}")
    
    def get_meeting_message(self):
        """Gera mensagem de reunião com dados atuais"""
        meeting = self.get_active_meeting()
        if not meeting:
            return None
        
        message = f"""🚨 *Lembrete Importante!*

Nossa reunião da Auge acontece em *{meeting['date']}* às *{meeting['time']}*.

É o momento perfeito para estudarmos juntos, tirar dúvidas e ter contato direto com os mentores.

🔗 [Clique aqui para participar]({meeting['link']})"""
        
        return message
    
    async def cmd_set_meeting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /set_meeting - Configurar reunião"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
            return
        
        # Verificar se foram fornecidos os parâmetros necessários
        if len(context.args) < 3:
            await update.message.reply_text(
                "📝 *Uso correto:*\n\n"
                "`/set_meeting [LINK] [DATA] [HORA]`\n\n"
                "*Exemplo:*\n"
                "`/set_meeting https://meet.google.com/abc-def-ghi 15/01/2024 20:00`",
                parse_mode='Markdown'
            )
            return
        
        link = context.args[0]
        date = context.args[1]
        time = context.args[2]
        
        # Salvar configuração
        if self.save_meeting_config(link, date, time):
            await update.message.reply_text(
                f"✅ *Reunião configurada com sucesso!*\n\n"
                f"📅 **Data:** {date}\n"
                f"🕐 **Horário:** {time}\n"
                f"🔗 **Link:** {link}\n\n"
                f"A mensagem será enviada automaticamente para novos membros e nos horários programados.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Erro ao configurar reunião. Tente novamente.")
    
    async def cmd_test_meeting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /test_meeting - Testar mensagem de reunião"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
            return
        
        message = self.get_meeting_message()
        if message:
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                 "❌ Nenhuma reunião configurada.\n\n"
                 "Use `/set_meeting` para configurar uma reunião primeiro.",
                 parse_mode='Markdown'
             )
    
    async def send_scheduled_meeting_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Envia mensagem de reunião automaticamente nos horários programados"""
        meeting_message = self.get_meeting_message()
        if meeting_message:
            try:
                await context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=meeting_message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("Mensagem de reunião enviada automaticamente")
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem automática de reunião: {e}")
    
    def setup_meeting_scheduler(self, job_queue: JobQueue):
        """Configura o agendamento automático de mensagens de reunião"""
        # Horários para envio automático (10:00 e 18:00 horário de Brasília)
        morning_time = dt_time(hour=10, minute=0, second=0)
        evening_time = dt_time(hour=18, minute=0, second=0)
        
        # Agendar envios diários
        job_queue.run_daily(
            self.send_scheduled_meeting_message,
            time=morning_time,
            name='meeting_morning'
        )
        
        job_queue.run_daily(
            self.send_scheduled_meeting_message,
            time=evening_time,
            name='meeting_evening'
        )
        
        logger.info("Agendamento automático de reuniões configurado para 10:00 e 18:00")
    
    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mensagem automática para novos membros"""
        for new_member in update.message.new_chat_members:
            self.add_user(new_member.id, new_member.username, new_member.first_name, new_member.last_name)
            
            if update.effective_chat.id == GROUP_CHAT_ID:
                # Mensagem para grupo principal usando mensagem predefinida
                welcome_text = self.messages['welcome_main'].format(
                    name=new_member.first_name,
                    mentoria_link=MENTORIA_LINK,
                    duvidas_link=DUVIDAS_GROUP_LINK
                )
                
                keyboard = [
                    [InlineKeyboardButton("🎯 Mentoria Day Trade", url=MENTORIA_LINK)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
                
                # Enviar mensagem de reunião se configurada
                meeting_message = self.get_meeting_message()
                if meeting_message:
                    await update.message.reply_text(
                        meeting_message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
            
            elif update.effective_chat.id == DUVIDAS_GROUP_CHAT_ID:
                # Mensagem para grupo de dúvidas
                welcome_text = f"""🔗 *Bem-vindo ao Grupo de Dúvidas, {new_member.first_name}!*

👋 Este é o espaço ideal para suas perguntas sobre trading!

💡 Aqui você pode:
• Tirar dúvidas sobre análises técnicas
• Pedir ajuda com estratégias
• Compartilhar experiências de trading
• Aprender com a comunidade

🎯 *Link da Mentoria:*
[🎯 Mentoria Auge Traders]({MENTORIA_LINK})

📋 *Dicas para melhor aproveitamento:*
• Seja específico nas suas perguntas
• Use prints/gráficos quando necessário
• Respeite todos os membros
• Mantenha o foco em aprendizado

👥 **Nossa equipe** está pronta para ajudar!

Vamos aprender juntos! 📚"""
                
                keyboard = [
                    [InlineKeyboardButton("📊 Grupo de Dúvidas", url=DUVIDAS_GROUP_LINK)],
                    [InlineKeyboardButton("🎯 Mentoria Day Trade", url=MENTORIA_LINK)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            
            else:
                # Mensagem genérica para outros grupos
                welcome_text = f"""👋 Olá {new_member.first_name}!

Bem-vindo ao nosso grupo! 🎯

[🔗 Grupo de Dúvidas]({DUVIDAS_GROUP_LINK})
[🎯 Mentoria Auge Traders]({MENTORIA_LINK})

👥 **Nossa equipe** está pronta para ajudar!"""
                
                keyboard = [
                    [InlineKeyboardButton("📊 Grupo de Dúvidas", url=DUVIDAS_GROUP_LINK)],
                    [InlineKeyboardButton("🎯 Mentoria Day Trade", url=MENTORIA_LINK)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            
            logger.info(f"Mensagem de boas-vindas enviada para {new_member.first_name} ({new_member.id})")
    
    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Estatísticas do bot (apenas admins)"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de usuários
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Usuários ativos (últimos 30 dias)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM messages 
            WHERE message_date >= datetime('now', '-30 days')
        """)
        active_users = cursor.fetchone()[0]
        
        # Total de mensagens
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        # Mensagens hoje
        cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE date(message_date) = date('now')
        """)
        today_messages = cursor.fetchone()[0]
        
        conn.close()
        
        stats_text = f"""📊 *Estatísticas do Bot Auge Traders*

👥 Total de usuários: {total_users}
🟢 Usuários ativos (30 dias): {active_users}
💬 Total de mensagens: {total_messages}
📅 Mensagens hoje: {today_messages}

📅 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"""
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        logger.info(f"Estatísticas solicitadas por admin {update.effective_user.id}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens do grupo"""
        if update.message and update.message.text:
            user = update.effective_user
            chat = update.effective_chat
            
            logger.info(f"[DEBUG] Mensagem recebida de {user.first_name} ({user.id}) no chat {chat.id}: {update.message.text[:50]}...")
            
            try:
                # Adicionar usuário se não existir
                self.add_user(user.id, user.username, user.first_name, user.last_name)
                
                # Registrar mensagem
                self.log_message(user.id, update.message.text, chat.id)
                logger.info(f"[DEBUG] Mensagem processada e logada com sucesso")
            except Exception as e:
                logger.error(f"[ERROR] Erro ao processar mensagem: {e}")
                raise
    
    def run(self):
        """Inicia o bot"""
        if not BOT_TOKEN:
            logger.error("Token do bot não encontrado! Verifique o arquivo .env")
            return
        
        # Configurar application com timeouts mais robustos e retry
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .pool_timeout(30)
            .get_updates_read_timeout(30)
            .build()
        )
        
        # Configurar Flask para webhook (Railway)
        if ENVIRONMENT == 'production':
            self.setup_flask_webhook(application)
        
        # Handlers de comandos
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("stats", self.admin_stats))
        
        # Handlers de mensagens predefinidas (apenas admins)
        application.add_handler(CommandHandler("morning", self.cmd_morning_alert))
        application.add_handler(CommandHandler("alert", self.cmd_market_alert))
        application.add_handler(CommandHandler("motivacao", self.cmd_motivational))
        application.add_handler(CommandHandler("engajamento", self.cmd_engagement))
        application.add_handler(CommandHandler("duvidas", self.cmd_doubts_reminder))
        application.add_handler(CommandHandler("mentoria", self.cmd_mentoria_promo))
        application.add_handler(CommandHandler("disciplina", self.cmd_discipline))
        application.add_handler(CommandHandler("weekend", self.cmd_weekend))
        application.add_handler(CommandHandler("motivacao_geral", self.cmd_motivation))
        application.add_handler(CommandHandler("mensagens", self.cmd_list_messages))
        
        # Handlers de reunião
        application.add_handler(CommandHandler("set_meeting", self.cmd_set_meeting))
        application.add_handler(CommandHandler("test_meeting", self.cmd_test_meeting))
        
        # Handler para novos membros
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome_new_member))
        
        # Handler para todas as mensagens (logging)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("Handlers configurados com sucesso")
        logger.info(f"Total de handlers registrados: {len(application.handlers[0])}")
        
        # Configurar agendamento automático de reuniões
        self.setup_meeting_scheduler(application.job_queue)
        
        logger.info("🎯 Bot Auge Traders iniciado com sucesso!")
        logger.info(f"Bot configurado para grupos: {GROUP_CHAT_ID}, {DUVIDAS_GROUP_CHAT_ID}")
        
        # Escolher método de execução baseado no ambiente
        if ENVIRONMENT == 'production':
            logger.info("🚀 Iniciando bot em modo WEBHOOK (Railway)")
            self.run_webhook(application)
        else:
            logger.info("🔄 Iniciando bot em modo POLLING (desenvolvimento)")
            self.run_polling(application)
    
    def setup_flask_webhook(self, application):
        """Configura Flask para receber webhooks do Telegram"""
        self.flask_app = Flask(__name__)
        self.application = application
        
        @self.flask_app.route(f'/{BOT_TOKEN}', methods=['POST'])
        def webhook():
            """Processa updates do webhook"""
            try:
                update_data = request.get_json(force=True)
                update = Update.de_json(update_data, self.application.bot)
                
                # Processar update de forma síncrona
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.application.process_update(update))
                loop.close()
                
                return 'OK'
            except Exception as e:
                logger.error(f"Erro ao processar webhook: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return 'ERROR', 500
        
        @self.flask_app.route('/health', methods=['GET'])
        def health_check():
            """Health check para Railway"""
            from flask import jsonify
            try:
                # Verificar se o bot está inicializado
                if hasattr(self, 'application') and self.application:
                    status = 'healthy'
                    bot_status = 'running'
                else:
                    status = 'initializing'
                    bot_status = 'starting'
                
                return jsonify({
                    'status': status,
                    'bot': 'Auge Traders',
                    'bot_status': bot_status,
                    'timestamp': datetime.now().isoformat()
                }), 200
            except Exception as e:
                logger.error(f"Health check error: {e}")
                return jsonify({
                    'status': 'error',
                    'bot': 'Auge Traders',
                    'error': str(e)
                }), 500
        
        @self.flask_app.route('/', methods=['GET'])
        def root():
            """Endpoint raiz para verificação básica"""
            from flask import jsonify
            return jsonify({'message': 'Auge Traders Bot is running', 'status': 'ok'}), 200
    
    def run_webhook(self, application):
        """Executa o bot usando webhook (Railway)"""
        try:
            # Armazenar referência da aplicação para health check
            self.application = application
            
            # Inicializar Flask imediatamente
            logger.info(f"Iniciando servidor Flask na porta {PORT}")
            
            # Configurar webhook em thread separada após Flask estar rodando
            def init_telegram_app():
                try:
                    # Aguardar Flask inicializar
                    import time
                    time.sleep(3)
                    
                    # Configurar webhook
                    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
                    logger.info(f"Configurando webhook: {webhook_url}")
                    
                    async def setup_webhook():
                        await application.initialize()
                        await application.start()
                        await application.bot.set_webhook(url=webhook_url)
                        logger.info("Webhook configurado com sucesso!")
                    
                    # Executar inicialização
                    import asyncio
                    asyncio.run(setup_webhook())
                    
                except Exception as e:
                    logger.error(f"Erro ao configurar webhook: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Inicializar Telegram em thread separada
            import threading
            telegram_thread = threading.Thread(target=init_telegram_app, daemon=True)
            telegram_thread.start()
            
            # Iniciar Flask (isso bloqueia, mas o health check já estará disponível)
            self.flask_app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
            
        except Exception as e:
            logger.error(f"Erro ao iniciar webhook: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def run_polling(self, application):
        """Executa o bot usando polling (desenvolvimento)"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Iniciando polling... (tentativa {retry_count + 1}/{max_retries})")
                
                # Usar configurações mais específicas para evitar conflitos
                application.run_polling(
                    drop_pending_updates=True,
                    allowed_updates=['message', 'chat_member'],
                    timeout=30,
                    poll_interval=2.0,
                    bootstrap_retries=3
                )
                break  # Se chegou aqui, o bot está rodando com sucesso
                
            except (NetworkError, TimedOut) as e:
                retry_count += 1
                logger.warning(f"Erro de rede (tentativa {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    wait_time = retry_count * 5  # Espera progressiva: 5s, 10s, 15s
                    logger.info(f"Aguardando {wait_time}s antes da próxima tentativa...")
                    time.sleep(wait_time)
                else:
                    logger.error("Máximo de tentativas de reconexão atingido")
                    
            except Conflict as e:
                logger.error(f"Conflito detectado: {e}")
                logger.error("Há outra instância do bot rodando. Verifique:")
                logger.error("1. Se há uma instância em produção (Railway, etc.)")
                logger.error("2. Se há outro processo local rodando")
                break
                
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                logger.error(f"Tipo do erro: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback completo: {traceback.format_exc()}")
                break

if __name__ == '__main__':
    bot = AugeTradersBot()
    bot.run()