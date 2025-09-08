class WelcomeHandler {
    constructor(bot, database) {
        this.bot = bot;
        this.db = database;
    }
    
    async handleNewMember(msg) {
        const chatId = msg.chat.id;
        const newMembers = msg.new_chat_members;
        
        // Verificar se é o grupo principal ou grupo de dúvidas
        const isMainGroup = chatId.toString() === process.env.GROUP_CHAT_ID;
        const isDuvidasGroup = chatId.toString() === process.env.DUVIDAS_GROUP_CHAT_ID;
        
        if (!isMainGroup && !isDuvidasGroup) {
            return;
        }
        
        for (const member of newMembers) {
            // Ignorar bots
            if (member.is_bot) {
                continue;
            }
            
            try {
                if (isMainGroup) {
                    // Adicionar usuário ao banco de dados apenas no grupo principal
                    await this.db.addUser(member);
                    
                    // Enviar mensagem de boas-vindas do grupo principal
                    await this.sendWelcomeMessage(chatId, member);
                    
                    console.log(`✅ Novo membro adicionado ao grupo principal: ${member.first_name} (${member.id})`);
                    
                    // Agendar mensagem de grupo de dúvidas após 5 minutos
                    setTimeout(async () => {
                        try {
                            const duvidasMessage = `💬 Quer tirar dúvidas ou trocar experiências com outros traders?
Participe do nosso *Grupo de Dúvidas* e compartilhe seu aprendizado.

🔗 [Clique aqui para entrar no grupo de dúvidas](${process.env.DUVIDAS_GROUP_LINK || '[link]'})

📢 Lembre-se: aqui é espaço de colaboração — quanto mais você interagir, mais você aprende!`;
                            
                            await this.bot.sendMessage(member.id, duvidasMessage, {
                                parse_mode: 'Markdown'
                            });
                            
                            console.log(`✅ Mensagem de grupo de dúvidas enviada para ${member.first_name}`);
                        } catch (error) {
                            console.error('❌ Erro ao enviar mensagem de grupo de dúvidas:', error);
                        }
                    }, 5 * 60 * 1000); // 5 minutos
                } else if (isDuvidasGroup) {
                    // Enviar mensagem de boas-vindas do grupo de dúvidas
                    await this.sendDuvidasWelcomeMessage(chatId, member);
                    
                    console.log(`✅ Novo membro adicionado ao grupo de dúvidas: ${member.first_name} (${member.id})`);
                }
            } catch (error) {
                console.error('❌ Erro ao processar novo membro:', error);
            }
        }
    }
    
    async sendWelcomeMessage(chatId, member) {
        const firstName = member.first_name || 'Trader';
        const duvidasLink = process.env.DUVIDAS_GROUP_LINK || '[link]';
        const mentoriaLink = process.env.MENTORIA_LINK || '[link]';
        
        const welcomeMessage = `🎉 Seja muito bem-vindo(a) ao *Grupo de Análises - Auge*!

Aqui você vai receber informações, insights e estratégias para potencializar seus resultados no Day Trade.
Nosso objetivo é criar uma comunidade de traders que evoluem juntos através de estudo, análise e disciplina.

💡 Dica: fique atento às mensagens diárias às 06:00 — preparamos você para o pré-mercado antes da abertura do pregão!`;
        
        const options = {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [
                    [
                        {
                            text: '📊 Grupo de Dúvidas',
                            url: duvidasLink,
                            callback_data: `click_duvidas_${member.id}`
                        }
                    ],
                    [
                        {
                            text: '🎯 Mentoria Day Trade',
                            url: mentoriaLink,
                            callback_data: `click_mentoria_${member.id}`
                        }
                    ]
                ]
            }
        };
        
        try {
            await this.bot.sendMessage(chatId, welcomeMessage, options);
            
            // Configurar callback para rastrear cliques
            this.setupClickTracking(member.id);
            
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem de boas-vindas:', error);
        }
    }
    
    async sendDuvidasWelcomeMessage(chatId, member) {
        const duvidasWelcomeText = `💬 Olá ${member.first_name}, bem-vindo(a) ao *Grupo de Dúvidas* do Auge Análises!

🤝 Este é o espaço ideal para:
• Tirar suas dúvidas sobre trading
• Compartilhar experiências
• Trocar conhecimentos com outros traders
• Discutir estratégias e análises

📋 *Regras importantes:*
• Seja respeitoso com todos os membros
• Mantenha o foco em trading e mercados
• Compartilhe conhecimento de qualidade
• Ajude outros traders quando possível

💡 *Lembre-se:* A colaboração é a chave do sucesso! Quanto mais você participa, mais você aprende.

🚀 Vamos crescer juntos no mundo do trading!`;
        
        try {
            await this.bot.sendMessage(chatId, duvidasWelcomeText, {
                parse_mode: 'Markdown'
            });
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem de boas-vindas do grupo de dúvidas:', error);
        }
    }
    
    setupClickTracking(userId) {
        // Callback para cliques nos botões
        this.bot.on('callback_query', async (callbackQuery) => {
            const data = callbackQuery.data;
            
            if (data.startsWith('click_duvidas_') && data.includes(userId.toString())) {
                await this.db.recordLinkClick(userId, 'duvidas_group');
                console.log(`📊 Clique registrado: Grupo de Dúvidas - Usuário ${userId}`);
            } else if (data.startsWith('click_mentoria_') && data.includes(userId.toString())) {
                await this.db.recordLinkClick(userId, 'mentoria_link');
                console.log(`📊 Clique registrado: Mentoria - Usuário ${userId}`);
            }
            
            // Responder ao callback para remover o loading
            await this.bot.answerCallbackQuery(callbackQuery.id);
        });
    }
}

module.exports = WelcomeHandler;