class FunnelHandler {
    constructor(bot, database) {
        this.bot = bot;
        this.db = database;
        this.groupChatId = process.env.GROUP_CHAT_ID;
    }
    
    async checkFunnelMessages() {
        try {
            // Verificar usuários para mensagem de 24h (step 0 -> 1)
            await this.sendFunnelMessage24h();
            
            // Verificar usuários para mensagem de 48h (step 1 -> 2)
            await this.sendFunnelMessage48h();
            
            // Verificar usuários para mensagem de 72h (step 2 -> 3)
            await this.sendFunnelMessage72h();
            
        } catch (error) {
            console.error('❌ Erro ao verificar mensagens do funil:', error);
        }
    }
    
    async sendFunnelMessage24h() {
        const users = await this.db.getUsersForFunnelStep(0, 24);
        
        for (const user of users) {
            try {
                const message = this.getFunnelMessage24h();
                
                await this.bot.sendMessage(user.user_id, message.text, message.options);
                await this.db.updateUserFunnelStep(user.user_id, 1);
                
                console.log(`📧 Mensagem 24h enviada para: ${user.first_name} (${user.user_id})`);
                
                // Delay para evitar spam
                await this.delay(2000);
                
            } catch (error) {
                console.error(`❌ Erro ao enviar mensagem 24h para ${user.user_id}:`, error);
            }
        }
    }
    
    async sendFunnelMessage48h() {
        const users = await this.db.getUsersForFunnelStep(1, 48);
        
        for (const user of users) {
            try {
                const message = this.getFunnelMessage48h();
                
                await this.bot.sendMessage(user.user_id, message.text, message.options);
                await this.db.updateUserFunnelStep(user.user_id, 2);
                
                console.log(`📧 Mensagem 48h enviada para: ${user.first_name} (${user.user_id})`);
                
                // Delay para evitar spam
                await this.delay(2000);
                
            } catch (error) {
                console.error(`❌ Erro ao enviar mensagem 48h para ${user.user_id}:`, error);
            }
        }
    }
    
    async sendFunnelMessage72h() {
        const users = await this.db.getUsersForFunnelStep(2, 72);
        
        for (const user of users) {
            try {
                const message = this.getFunnelMessage72h();
                
                await this.bot.sendMessage(user.user_id, message.text, message.options);
                await this.db.updateUserFunnelStep(user.user_id, 3);
                
                console.log(`📧 Mensagem 72h enviada para: ${user.first_name} (${user.user_id})`);
                
                // Delay para evitar spam
                await this.delay(2000);
                
            } catch (error) {
                console.error(`❌ Erro ao enviar mensagem 72h para ${user.user_id}:`, error);
            }
        }
    }
    
    getFunnelMessage24h() {
        const mentoriaLink = process.env.MENTORIA_LINK || 'https://www.mentoriaaugetraders.com.br/';
        
        const text = `🚀 Já está por dentro das análises da Auge?
Agora é hora de dar o próximo passo e se tornar um trader ainda mais preparado!

🎯 Conheça nossa *Mentoria Day Trade*:
✅ Estratégias validadas
✅ Análise ao vivo do mercado
✅ Acompanhamento de mentores experientes

🔗 [Acesse aqui e garanta sua vaga](${mentoriaLink})`;
        
        const options = {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [
                    [
                        {
                            text: '🎯 Quero fazer parte da Mentoria',
                            url: mentoriaLink
                        }
                    ]
                ]
            }
        };
        
        return { text, options };
    }
    
    getFunnelMessage48h() {
        const text = `📈 Resultado vem para quem estuda e aplica.
Veja o que nossos alunos dizem sobre a *Mentoria Day Trade*:

💬 "Passei a operar com mais confiança e hoje tenho muito mais consistência nos meus trades."

🎯 Quer evoluir também?
🔗 [Garanta sua vaga na mentoria agora](${process.env.MENTORIA_LINK || 'https://www.mentoriaaugetraders.com.br/'})`;
        
        const mentoriaLink = process.env.MENTORIA_LINK || 'https://www.mentoriaaugetraders.com.br/';
        
        const options = {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [
                    [
                        {
                            text: '💎 Quero os mesmos resultados',
                            url: mentoriaLink
                        }
                    ]
                ]
            }
        };
        
        return { text, options };
    }
    
    getFunnelMessage72h() {
        const text = `⚠️ *ÚLTIMA CHAMADA - Vagas se encerrando!*

🕐 *Restam poucas horas para garantir sua vaga na Mentoria Day Trade*

Essa é sua última chance de:

🎯 Aprender as estratégias que geram resultados consistentes
📊 Ter acesso às análises exclusivas do Rafael e Daniel
💰 Transformar seu trading em uma fonte de renda real
🚀 Fazer parte de uma comunidade de traders vencedores

❌ *Não deixe essa oportunidade passar!*

Depois de hoje, as vagas só abrirão novamente no próximo mês.

👇 *Clique agora e garante sua transformação:*`;
        
        const mentoriaLink = process.env.MENTORIA_LINK || 'https://www.mentoriaaugetraders.com.br/';
        
        const options = {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [
                    [
                        {
                            text: '🔥 GARANTIR MINHA VAGA AGORA',
                            url: mentoriaLink
                        }
                    ]
                ]
            }
        };
        
        return { text, options };
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

module.exports = FunnelHandler;