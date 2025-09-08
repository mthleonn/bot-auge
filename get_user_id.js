// Script temporário para descobrir seu ID de usuário no Telegram
const TelegramBot = require('node-telegram-bot-api');

// Use o token do seu bot
const token = '7482522123:AAH3h3h3h3h3h3h3h3h3h3h3h3h3h3h3';
const bot = new TelegramBot(token, {polling: true});

console.log('🤖 Bot iniciado! Envie qualquer mensagem para ele descobrir seu ID...');

// Escutar qualquer mensagem
bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    const username = msg.from.username || 'sem username';
    const firstName = msg.from.first_name || 'sem nome';
    
    console.log('\n📋 INFORMAÇÕES DO USUÁRIO:');
    console.log(`👤 Nome: ${firstName}`);
    console.log(`🆔 User ID: ${userId}`);
    console.log(`📱 Username: @${username}`);
    console.log(`💬 Chat ID: ${chatId}`);
    console.log('\n✅ Copie o User ID acima e configure no Render!');
    
    bot.sendMessage(chatId, `🆔 Seu User ID é: \`${userId}\`\n\n📋 Configure este ID na variável ADMIN_IDS no Render:\n\`ADMIN_IDS=${userId}\``, {
        parse_mode: 'Markdown'
    });
});

// Tratar erros
bot.on('error', (error) => {
    console.error('❌ Erro:', error);
});

console.log('\n📱 Agora envie uma mensagem para o bot no Telegram para descobrir seu ID!');