class MessageHandler {
    constructor(bot, database) {
        this.bot = bot;
        this.db = database;
        this.groupChatId = process.env.GROUP_CHAT_ID;
    }
    
    async handleMessage(msg) {
        const chatId = msg.chat.id;
        const userId = msg.from.id;
        const text = msg.text;
        
        // Ignorar mensagens de bots
        if (msg.from.is_bot) {
            return;
        }
        
        // Processar apenas mensagens do grupo principal
        if (chatId.toString() !== this.groupChatId) {
            return;
        }
        
        try {
            // Atualizar informações do usuário se necessário
            await this.updateUserInfo(msg.from);
            
            // Processar comandos específicos
            if (text && text.startsWith('/')) {
                await this.handleCommand(msg);
            }
            
            // Detectar e moderar spam (opcional)
            if (await this.isSpamMessage(msg)) {
                await this.handleSpamMessage(msg);
            }
            
        } catch (error) {
            console.error('❌ Erro ao processar mensagem:', error);
        }
    }
    
    async updateUserInfo(user) {
        try {
            const existingUser = await this.db.getUser(user.id);
            
            if (existingUser) {
                // Atualizar informações se mudaram
                if (existingUser.username !== user.username || 
                    existingUser.first_name !== user.first_name) {
                    await this.db.addUser(user);
                }
            } else {
                // Adicionar novo usuário
                await this.db.addUser(user);
            }
        } catch (error) {
            console.error('❌ Erro ao atualizar informações do usuário:', error);
        }
    }
    
    async handleCommand(msg) {
        const command = msg.text.toLowerCase();
        const chatId = msg.chat.id;
        const userId = msg.from.id;
        
        switch (command) {
            case '/start':
                await this.handleStartCommand(chatId, userId);
                break;
                
            case '/help':
                await this.handleHelpCommand(chatId);
                break;
                
            case '/links':
                await this.handleLinksCommand(chatId);
                break;
                
            case '/stats':
                await this.handleStatsCommand(chatId, userId);
                break;
                
            case '/reuniao':
                if (this.isAdmin(msg.from.id)) {
                    await this.handleMeetingCommand(chatId);
                } else {
                    await this.bot.sendMessage(chatId, '❌ Comando disponível apenas para administradores.');
                }
                break;
                
            default:
                // Comando não reconhecido - não fazer nada
                break;
        }
    }
    
    async handleStartCommand(chatId, userId) {
        const message = `👋 *Olá!*

Este é o bot oficial do *Grupo de Análises - Auge*.

🔗 *Links úteis:*
• Grupo de Dúvidas: ${process.env.DUVIDAS_GROUP_LINK || '[link]'}
• Mentoria Day Trade: ${process.env.MENTORIA_LINK || '[link]'}

💡 *Fique atento às análises diárias do Rafael e Daniel!*`;
        
        await this.bot.sendMessage(chatId, message, {
            parse_mode: 'Markdown'
        });
    }
    
    async handleHelpCommand(chatId) {
        const message = `ℹ️ *Comandos disponíveis:*

/start - Informações do bot
/help - Esta mensagem de ajuda
/links - Links importantes
/stats - Estatísticas do grupo (apenas admins)
/reuniao - Criar link de reunião (apenas admins)

📞 *Precisa de ajuda?*
Entre no nosso grupo de dúvidas: ${process.env.DUVIDAS_GROUP_LINK || '[link]'}`;
        
        await this.bot.sendMessage(chatId, message, {
            parse_mode: 'Markdown'
        });
    }
    
    async handleLinksCommand(chatId) {
        const duvidasLink = process.env.DUVIDAS_GROUP_LINK || '[link]';
        const mentoriaLink = process.env.MENTORIA_LINK || '[link]';
        
        const message = `🔗 *Links Importantes:*

❓ *Grupo de Dúvidas:*
${duvidasLink}

📚 *Mentoria Day Trade:*
${mentoriaLink}

💡 *Lembre-se:* Fique sempre atento às análises matinais do Rafael e Daniel!`;
        
        const options = {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [
                    [
                        {
                            text: '❓ Grupo de Dúvidas',
                            url: duvidasLink
                        }
                    ],
                    [
                        {
                            text: '📚 Mentoria Day Trade',
                            url: mentoriaLink
                        }
                    ]
                ]
            }
        };
        
        await this.bot.sendMessage(chatId, message, options);
    }
    
    async handleStatsCommand(chatId, userId) {
        // Verificar se é administrador
        if (!this.isAdmin(userId)) {
            await this.bot.sendMessage(chatId, '❌ Comando disponível apenas para administradores.');
            return;
        }
        
        try {
            const stats = await this.db.getLinkClickStats();
            let message = '📊 *Estatísticas do Bot:*\n\n';
            
            if (stats.length > 0) {
                stats.forEach(stat => {
                    const linkName = stat.link_type === 'duvidas_group' ? 'Grupo de Dúvidas' : 'Mentoria';
                    message += `🔗 *${linkName}:*\n`;
                    message += `   • Cliques: ${stat.clicks}\n`;
                    message += `   • Usuários únicos: ${stat.unique_users}\n\n`;
                });
            } else {
                message += 'Nenhum clique registrado ainda.';
            }
            
            await this.bot.sendMessage(chatId, message, {
                parse_mode: 'Markdown'
            });
            
        } catch (error) {
            console.error('❌ Erro ao buscar estatísticas:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao buscar estatísticas.');
        }
    }
    
    async isSpamMessage(msg) {
        const text = msg.text || '';
        const spamKeywords = [
            'http://', 'https://', 'www.',
            'telegram.me', 't.me',
            'bitcoin', 'crypto', 'investimento garantido',
            'ganhe dinheiro', 'renda extra'
        ];
        
        // Verificar se contém palavras de spam
        const hasSpamKeywords = spamKeywords.some(keyword => 
            text.toLowerCase().includes(keyword.toLowerCase())
        );
        
        // Verificar se é um link não autorizado
        const hasUnauthorizedLink = (text.includes('http') || text.includes('t.me')) &&
            !text.includes(process.env.DUVIDAS_GROUP_LINK) &&
            !text.includes(process.env.MENTORIA_LINK);
        
        return hasSpamKeywords || hasUnauthorizedLink;
    }
    
    async handleSpamMessage(msg) {
        try {
            // Deletar mensagem de spam
            await this.bot.deleteMessage(msg.chat.id, msg.message_id);
            
            // Enviar aviso (que será deletado automaticamente)
            const warningMsg = await this.bot.sendMessage(
                msg.chat.id,
                `⚠️ Mensagem removida por conter conteúdo não autorizado.\n\n@${msg.from.username || msg.from.first_name}, por favor, siga as regras do grupo.`,
                { parse_mode: 'Markdown' }
            );
            
            // Deletar aviso após 10 segundos
            setTimeout(async () => {
                try {
                    await this.bot.deleteMessage(msg.chat.id, warningMsg.message_id);
                } catch (error) {
                    // Ignorar erro se a mensagem já foi deletada
                }
            }, 10000);
            
            console.log(`🚫 Spam removido de: ${msg.from.first_name} (${msg.from.id})`);
            
        } catch (error) {
            console.error('❌ Erro ao remover spam:', error);
        }
    }
    
    async handleMeetingCommand(chatId) {
        try {
            // Gerar um link básico do Google Meet (pode ser expandido com Google Calendar API)
            const meetingId = Math.random().toString(36).substring(2, 15);
            const meetLink = `https://meet.google.com/${meetingId}`;
            
            const meetingMessage = `📢 Reunião da comunidade começando!
Clique no link abaixo para participar:

🔗 [Entrar na Reunião](${meetLink})

🎙 Prepare suas perguntas — vamos falar sobre setups, gestão de risco e estratégias ao vivo!`;
            
            await this.bot.sendMessage(chatId, meetingMessage, {
                parse_mode: 'Markdown'
            });
            
            console.log('✅ Link de reunião enviado com sucesso!');
        } catch (error) {
            console.error('❌ Erro ao enviar link de reunião:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao criar link da reunião. Tente novamente.');
        }
    }

    isAdmin(userId) {
        const adminIds = process.env.ADMIN_IDS ? process.env.ADMIN_IDS.split(',') : [];
        return adminIds.includes(userId.toString());
    }
}

module.exports = MessageHandler;