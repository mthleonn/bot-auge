require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const cron = require('node-cron');
const Database = require('./database');
const WelcomeHandler = require('./handlers/welcomeHandler');
const AdminHandler = require('./handlers/adminHandler');
const MessageHandler = require('./handlers/messageHandler');
const FunnelHandler = require('./handlers/funnelHandler');
const { startHealthCheck } = require('./healthCheck');

class AugeAnalysesBot {
    constructor() {
        this.token = process.env.TELEGRAM_BOT_TOKEN;
        this.groupChatId = process.env.GROUP_CHAT_ID;
        
        if (!this.token) {
            throw new Error('TELEGRAM_BOT_TOKEN não encontrado nas variáveis de ambiente');
        }
        
        this.bot = new TelegramBot(this.token, { polling: true });
        this.db = new Database();
        
        this.initializeHandlers();
        this.setupEventListeners();
        this.scheduleDailyMessages();
        
        console.log('🤖 Auge Análises Bot iniciado com sucesso!');
        
        // Iniciar health check server para Render
        startHealthCheck();
    }
    
    initializeHandlers() {
        this.messageHandler = new MessageHandler(this.bot, this.db);
        this.welcomeHandler = new WelcomeHandler(this.bot, this.db);
        this.funnelHandler = new FunnelHandler(this.bot, this.db);
        this.adminHandler = new AdminHandler(this.bot, this.db);
    }
    
    setupEventListeners() {
        // Novos membros
        this.bot.on('new_chat_members', (msg) => {
            this.welcomeHandler.handleNewMember(msg);
        });
        
        // Mensagens de texto
        this.bot.on('message', (msg) => {
            this.messageHandler.handleMessage(msg);
        });
        
        // Comandos de administrador
        this.bot.onText(/\/admin (.+)/, (msg, match) => {
            this.adminHandler.handleAdminCommand(msg, match[1]);
        });
        

        
        // Comando de teste para mensagens programadas
        this.bot.onText(/\/testmsg/, async (msg) => {
            if (this.adminHandler.isAdmin(msg.from.id)) {
                try {
                    const testMessage = `🧪 **Teste de Mensagem Programada**\n\nEste é um teste para verificar se o sistema de mensagens está funcionando corretamente.\n\nHorário atual: ${new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' })}`;
                    
                    await this.bot.sendMessage(process.env.GROUP_CHAT_ID, testMessage, {
                        parse_mode: 'Markdown'
                    });
                    
                    await this.bot.sendMessage(msg.chat.id, '✅ Mensagem de teste enviada com sucesso!');
                } catch (error) {
                    console.error('❌ Erro no teste de mensagem:', error);
                    await this.bot.sendMessage(msg.chat.id, '❌ Erro ao enviar mensagem de teste.');
                }
            }
        });
        
        // Tratamento de erros
        this.bot.on('error', (error) => {
            console.error('Erro no bot:', error);
        });
        
        this.bot.on('polling_error', (error) => {
            console.error('Erro de polling:', error);
        });
    }
    
    scheduleDailyMessages() {
        console.log('📅 Configurando mensagens programadas...');
        
        // Mensagem diária às 06:00
        cron.schedule('0 6 * * *', async () => {
            try {
                const morningMessage = `☀️ Bom dia, trader!
Prepare seu setup, revise sua estratégia e esteja pronto para aproveitar o dia de mercado com disciplina e foco.
Bons trades para você!`;

                await this.bot.sendMessage(process.env.GROUP_CHAT_ID, morningMessage, {
                    parse_mode: 'Markdown'
                });

                console.log('✅ Mensagem diária enviada com sucesso!');
            } catch (error) {
                console.error('❌ Erro ao enviar mensagem diária:', error);
            }
        }, {
            timezone: process.env.TIMEZONE || 'America/Sao_Paulo'
        });
        console.log('✅ Mensagem diária às 06:00 configurada');
        
        // Mensagens periódicas para manter o grupo ativo
        // Terça e Quinta às 14:00 - Dicas educativas
        cron.schedule('0 14 * * 2,4', async () => {
            try {
                const educationalMessage = this.getRandomEducationalMessage();
                await this.bot.sendMessage(process.env.GROUP_CHAT_ID, educationalMessage, {
                    parse_mode: 'Markdown'
                });
                console.log('✅ Mensagem educativa enviada com sucesso!');
            } catch (error) {
                console.error('❌ Erro ao enviar mensagem educativa:', error);
            }
        }, {
            timezone: process.env.TIMEZONE || 'America/Sao_Paulo'
        });
        console.log('✅ Mensagens educativas (Ter/Qui 14:00) configuradas');
        
        // Sexta às 16:00 - Reflexão semanal
        cron.schedule('0 16 * * 5', async () => {
            try {
                const weeklyMessage = this.getRandomWeeklyMessage();
                await this.bot.sendMessage(process.env.GROUP_CHAT_ID, weeklyMessage, {
                    parse_mode: 'Markdown'
                });
                console.log('✅ Mensagem semanal enviada com sucesso!');
            } catch (error) {
                console.error('❌ Erro ao enviar mensagem semanal:', error);
            }
        }, {
            timezone: process.env.TIMEZONE || 'America/Sao_Paulo'
        });
        console.log('✅ Mensagens semanais (Sex 16:00) configuradas');
        
        // Verificar funil de conversão a cada hora
        cron.schedule('0 * * * *', () => {
            this.funnelHandler.checkFunnelMessages();
        });
        console.log('✅ Verificação de funil (a cada hora) configurada');
        console.log('🎯 Todas as mensagens programadas foram configuradas com sucesso!');
        
        // Teste de cron - executa a cada minuto para verificar se está funcionando
        cron.schedule('* * * * *', () => {
            console.log(`🕐 Teste de cron executado às: ${new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' })}`);
        }, {
            timezone: process.env.TIMEZONE || 'America/Sao_Paulo'
        });
        console.log('🧪 Teste de cron configurado (executa a cada minuto)');
    }
    
    getRandomEducationalMessage() {
        const messages = [
            `📚 *Dica de Trading:*

Gerenciamento de risco é fundamental! Nunca arrisque mais de 2% do seu capital em uma única operação.

💡 Lembre-se: preservar capital é mais importante que ganhar dinheiro.`,
            
            `🎯 *Estratégia do Dia:*

Antes de entrar em qualquer trade, defina:
✅ Ponto de entrada
✅ Stop loss
✅ Take profit

📈 Planejamento é a chave do sucesso!`,
            
            `🧠 *Psicologia do Trading:*

Controle emocional é 80% do sucesso no trading. Medo e ganância são os maiores inimigos do trader.

🎯 Mantenha-se disciplinado e siga seu plano!`,
            
            `📊 *Análise Técnica:*

Suportes e resistências são níveis-chave no mercado. Observe como o preço reage nesses pontos.

💪 Conhecimento técnico + experiência = resultados consistentes!`,
            
            `⏰ *Gestão de Tempo:*

Nem todo momento é bom para operar. Aprenda a identificar os melhores horários e setups.

🎯 Qualidade > Quantidade sempre!`
        ];
        
        return messages[Math.floor(Math.random() * messages.length)];
    }
    
    getRandomWeeklyMessage() {
        const messages = [
            `🗓️ *Reflexão da Semana:*

Como foram seus trades esta semana? Anote os acertos e erros para evoluir continuamente.

📝 Manter um diário de trading é essencial para o crescimento!`,
            
            `🎯 *Planejamento Semanal:*

Fim de semana é hora de planejar! Revise suas estratégias e prepare-se para a próxima semana.

💪 Preparação adequada = melhores resultados!`,
            
            `📈 *Evolução Constante:*

Cada semana é uma oportunidade de aprender algo novo. Estude, pratique e mantenha-se atualizado.

🚀 O mercado recompensa quem se dedica!`,
            
            `🎖️ *Disciplina Semanal:*

Parabéns por mais uma semana de dedicação! Consistência e disciplina são os pilares do sucesso.

💎 Continue firme no seu objetivo!`,
            
            `🔄 *Reset Mental:*

Use o fim de semana para descansar e renovar as energias. Mente descansada = decisões melhores.

⚡ Segunda-feira chegando com tudo!`
        ];
        
        return messages[Math.floor(Math.random() * messages.length)];
    }

    async sendDailyMessage() {
        const message = `🌅 Bom dia, trader!

Já já Rafael e Daniel vão mandar a análise do pré-mercado.
Fiquem ligados para se preparar antes do pregão! 🔥`;
        
        try {
            await this.bot.sendMessage(this.groupChatId, message, {
                parse_mode: 'Markdown'
            });
            console.log('✅ Mensagem diária enviada com sucesso');
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem diária:', error);
        }
    }
}

// Inicializar o bot
try {
    new AugeAnalysesBot();
} catch (error) {
    console.error('❌ Erro ao inicializar o bot:', error);
    process.exit(1);
}