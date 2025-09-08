// API endpoint para manter o bot rodando no Vercel
const TelegramBot = require('node-telegram-bot-api');
const Database = require('../src/database');
const WelcomeHandler = require('../src/handlers/welcomeHandler');
const AdminHandler = require('../src/handlers/adminHandler');
const MessageHandler = require('../src/handlers/messageHandler');
const FunnelHandler = require('../src/handlers/funnelHandler');
const cron = require('node-cron');

// Configurações
const token = process.env.TELEGRAM_BOT_TOKEN;
const groupChatId = process.env.GROUP_CHAT_ID;
const duvidasGroupChatId = process.env.DUVIDAS_GROUP_CHAT_ID;

if (!token) {
    console.error('❌ TELEGRAM_BOT_TOKEN não encontrado!');
    process.exit(1);
}

// Inicializar bot
const bot = new TelegramBot(token, { polling: false });
const database = new Database();

// Inicializar handlers
const welcomeHandler = new WelcomeHandler(bot, database);
const adminHandler = new AdminHandler(bot, database);
const messageHandler = new MessageHandler(bot, database);
const funnelHandler = new FunnelHandler(bot, database);

// Configurar webhook
bot.setWebHook(`${process.env.VERCEL_URL}/api/bot`);

// Função para processar updates
async function processUpdate(update) {
    try {
        if (update.message) {
            const msg = update.message;
            
            // Log da mensagem recebida
            console.log(`📨 Mensagem recebida de ${msg.from.first_name} (${msg.from.id}): ${msg.text}`);
            
            // Verificar se é comando de admin
            if (msg.text && msg.text.startsWith('/admin ')) {
                const command = msg.text.substring(7);
                await adminHandler.handleAdminCommand(msg, command);
                return;
            }
            
            // Verificar outros comandos
            if (msg.text && msg.text.startsWith('/')) {
                await messageHandler.handleCommand(msg);
                return;
            }
            
            // Processar mensagem normal
            await messageHandler.handleMessage(msg);
        }
    } catch (error) {
        console.error('❌ Erro ao processar update:', error);
    }
}

// Configurar cron jobs (apenas uma vez)
let cronJobsConfigured = false;

function setupCronJobs() {
    if (cronJobsConfigured) return;
    
    console.log('⏰ Configurando cron jobs...');
    
    // Mensagem diária às 06:00
    cron.schedule('0 6 * * *', async () => {
        try {
            const message = `🌅 *Bom dia, traders!*\n\nUm novo dia de oportunidades nos aguarda! Lembrem-se:\n\n📈 Disciplina é a chave do sucesso\n💪 Mantenham o foco nos objetivos\n🎯 Sigam sempre o plano de trading\n\n*Que hoje seja um dia próspero para todos!* 🚀`;
            
            await bot.sendMessage(groupChatId, message, { parse_mode: 'Markdown' });
            console.log('✅ Mensagem diária enviada!');
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem diária:', error);
        }
    }, {
        timezone: process.env.TIMEZONE || 'America/Sao_Paulo'
    });
    
    // Verificar funil de conversão a cada hora
    cron.schedule('0 * * * *', async () => {
        try {
            await funnelHandler.checkConversionFunnel();
        } catch (error) {
            console.error('❌ Erro no funil de conversão:', error);
        }
    });
    
    cronJobsConfigured = true;
    console.log('✅ Cron jobs configurados!');
}

// Handler principal para o Vercel
module.exports = async (req, res) => {
    try {
        // Configurar cron jobs na primeira execução
        setupCronJobs();
        
        if (req.method === 'POST') {
            // Processar webhook do Telegram
            await processUpdate(req.body);
            res.status(200).json({ ok: true });
        } else if (req.method === 'GET') {
            // Health check
            res.status(200).json({ 
                status: 'Bot online',
                timestamp: new Date().toISOString(),
                timezone: process.env.TIMEZONE || 'America/Sao_Paulo'
            });
        } else {
            res.status(405).json({ error: 'Method not allowed' });
        }
    } catch (error) {
        console.error('❌ Erro no handler:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
};