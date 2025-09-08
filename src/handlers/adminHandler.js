class AdminHandler {
    constructor(bot, database) {
        this.bot = bot;
        this.db = database;
        this.groupChatId = process.env.GROUP_CHAT_ID;
        this.waitingForPhoto = null;
    }
    
    async handleAdminCommand(msg, command) {
        const chatId = msg.chat.id;
        const userId = msg.from.id;
        
        // Verificar se é administrador
        if (!this.isAdmin(userId)) {
            await this.bot.sendMessage(chatId, '❌ Você não tem permissão para usar comandos de administrador.');
            return;
        }
        
        const [action, ...params] = command.split(' ');
        
        switch (action.toLowerCase()) {
            case 'broadcast':
                await this.handleBroadcast(chatId, params.join(' '));
                break;
                
            case 'stats':
                await this.handleDetailedStats(chatId);
                break;
                
            case 'users':
                await this.handleUsersList(chatId);
                break;
                
            case 'test':
                await this.handleTestMessage(chatId);
                break;
                
            case 'help':
                await this.handleAdminHelp(chatId);
                break;
                
            case 'setphoto':
                await this.bot.sendMessage(chatId, '❌ Funcionalidade não disponível\n\n📋 A API do Telegram não permite que bots alterem sua própria foto de perfil programaticamente.\n\n💡 Para alterar a foto do bot, você deve:\n1. Acessar @BotFather no Telegram\n2. Usar o comando /setuserpic\n3. Selecionar seu bot\n4. Enviar a nova foto');
                break;
                
            default:
                await this.bot.sendMessage(chatId, '❌ Comando não reconhecido. Use `/admin help` para ver os comandos disponíveis.');
                break;
        }
    }
    
    async handleBroadcast(chatId, message) {
        if (!message || message.trim() === '') {
            await this.bot.sendMessage(chatId, '❌ Por favor, forneça uma mensagem para enviar.\n\nExemplo: `/admin broadcast Mensagem importante para todos!`', {
                parse_mode: 'Markdown'
            });
            return;
        }
        
        try {
            // Enviar mensagem no grupo principal
            await this.bot.sendMessage(this.groupChatId, `📢 *Comunicado Oficial*\n\n${message}`, {
                parse_mode: 'Markdown'
            });
            
            await this.bot.sendMessage(chatId, '✅ Comunicado enviado com sucesso!');
            
            console.log(`📢 Comunicado enviado por admin ${chatId}: ${message}`);
            
        } catch (error) {
            console.error('❌ Erro ao enviar comunicado:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao enviar comunicado.');
        }
    }
    
    async handleDetailedStats(chatId) {
        try {
            // Estatísticas de cliques
            const clickStats = await this.db.getLinkClickStats();
            
            // Estatísticas de usuários (implementar query personalizada)
            const userStats = await this.getUserStats();
            
            let message = '📊 *Estatísticas Detalhadas do Bot*\n\n';
            
            // Estatísticas de usuários
            message += `👥 *Usuários:*\n`;
            message += `   • Total: ${userStats.total}\n`;
            message += `   • Ativos: ${userStats.active}\n`;
            message += `   • Novos (últimos 7 dias): ${userStats.newThisWeek}\n\n`;
            
            // Estatísticas de cliques
            message += `🔗 *Cliques nos Links (últimos 30 dias):*\n`;
            if (clickStats.length > 0) {
                clickStats.forEach(stat => {
                    const linkName = stat.link_type === 'duvidas_group' ? 'Grupo de Dúvidas' : 'Mentoria';
                    message += `   • ${linkName}: ${stat.clicks} cliques (${stat.unique_users} usuários únicos)\n`;
                });
            } else {
                message += '   • Nenhum clique registrado\n';
            }
            
            // Estatísticas do funil
            message += `\n📈 *Funil de Conversão:*\n`;
            const funnelStats = await this.getFunnelStats();
            message += `   • Etapa 0 (novos): ${funnelStats.step0}\n`;
            message += `   • Etapa 1 (24h): ${funnelStats.step1}\n`;
            message += `   • Etapa 2 (48h): ${funnelStats.step2}\n`;
            message += `   • Etapa 3 (72h+): ${funnelStats.step3}\n`;
            
            await this.bot.sendMessage(chatId, message, {
                parse_mode: 'Markdown'
            });
            
        } catch (error) {
            console.error('❌ Erro ao buscar estatísticas detalhadas:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao buscar estatísticas.');
        }
    }
    
    async handleUsersList(chatId) {
        try {
            // Buscar últimos 10 usuários
            const recentUsers = await this.getRecentUsers(10);
            
            let message = '👥 *Últimos 10 Usuários:*\n\n';
            
            if (recentUsers.length > 0) {
                recentUsers.forEach((user, index) => {
                    const joinDate = new Date(user.joined_at).toLocaleDateString('pt-BR');
                    const name = user.first_name + (user.last_name ? ` ${user.last_name}` : '');
                    const username = user.username ? `@${user.username}` : 'Sem username';
                    
                    message += `${index + 1}. *${name}*\n`;
                    message += `   • ${username}\n`;
                    message += `   • Entrou em: ${joinDate}\n`;
                    message += `   • Funil: Etapa ${user.funnel_step}\n\n`;
                });
            } else {
                message += 'Nenhum usuário encontrado.';
            }
            
            await this.bot.sendMessage(chatId, message, {
                parse_mode: 'Markdown'
            });
            
        } catch (error) {
            console.error('❌ Erro ao buscar lista de usuários:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao buscar lista de usuários.');
        }
    }
    
    async handleTestMessage(chatId) {
        const testMessage = `🧪 *Mensagem de Teste*\n\nEsta é uma mensagem de teste enviada às ${new Date().toLocaleTimeString('pt-BR')}.\n\n✅ Bot funcionando corretamente!`;
        
        try {
            await this.bot.sendMessage(this.groupChatId, testMessage, {
                parse_mode: 'Markdown'
            });
            
            await this.bot.sendMessage(chatId, '✅ Mensagem de teste enviada!');
            
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem de teste:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao enviar mensagem de teste.');
        }
    }
    

    
    async handleAdminHelp(chatId) {
        const helpMessage = `🔧 *Comandos de Administrador:*\n\n` +
            `📢 \`/admin broadcast <mensagem>\` - Enviar comunicado\n` +
            `📊 \`/admin stats\` - Estatísticas detalhadas\n` +
            `👥 \`/admin users\` - Lista de usuários recentes\n` +
            `🧪 \`/admin test\` - Enviar mensagem de teste\n` +
            `❓ \`/admin help\` - Esta mensagem de ajuda\n\n` +
            `*Exemplos:*\n` +
            `\`/admin broadcast Hoje teremos análise especial às 14h!\`\n` +
            `\`/admin stats\`\n` +
            `\`/admin test\`\n\n` +
            `📸 *Nota sobre foto do bot:* Para alterar a foto, use @BotFather → /setuserpic`;
        
        await this.bot.sendMessage(chatId, helpMessage, {
            parse_mode: 'Markdown'
        });
    }
    
    // Métodos auxiliares
    async getUserStats() {
        return new Promise((resolve, reject) => {
            const queries = {
                total: 'SELECT COUNT(*) as count FROM users',
                active: 'SELECT COUNT(*) as count FROM users WHERE is_active = 1',
                newThisWeek: "SELECT COUNT(*) as count FROM users WHERE datetime(joined_at) >= datetime('now', '-7 days')"
            };
            
            const stats = {};
            let completed = 0;
            
            Object.keys(queries).forEach(key => {
                this.db.db.get(queries[key], (err, row) => {
                    if (err) {
                        reject(err);
                        return;
                    }
                    
                    stats[key] = row.count;
                    completed++;
                    
                    if (completed === Object.keys(queries).length) {
                        resolve(stats);
                    }
                });
            });
        });
    }
    
    async getFunnelStats() {
        return new Promise((resolve, reject) => {
            const query = `
                SELECT 
                    funnel_step,
                    COUNT(*) as count
                FROM users 
                WHERE is_active = 1
                GROUP BY funnel_step
            `;
            
            this.db.db.all(query, (err, rows) => {
                if (err) {
                    reject(err);
                    return;
                }
                
                const stats = { step0: 0, step1: 0, step2: 0, step3: 0 };
                
                rows.forEach(row => {
                    stats[`step${row.funnel_step}`] = row.count;
                });
                
                resolve(stats);
            });
        });
    }
    
    async getRecentUsers(limit = 10) {
        return new Promise((resolve, reject) => {
            const query = `
                SELECT * FROM users 
                ORDER BY joined_at DESC 
                LIMIT ?
            `;
            
            this.db.db.all(query, [limit], (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }
    
    isAdmin(userId) {
        const adminIds = process.env.ADMIN_IDS ? process.env.ADMIN_IDS.split(',') : [];
        return adminIds.includes(userId.toString());
    }
}

module.exports = AdminHandler;