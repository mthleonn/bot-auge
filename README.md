# Bot Auge Traders

🎯 Bot oficial da comunidade Auge Traders para Telegram.

## Funcionalidades

- ✅ Mensagens de boas-vindas automáticas
- ✅ Sistema de banco de dados SQLite
- ✅ Comandos administrativos
- ✅ Registro de usuários e mensagens
- ✅ Links para grupo de dúvidas e mentoria
- ✅ Estatísticas do bot

## Instalação

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure o arquivo `.env` com seus tokens e IDs
4. Execute o bot:
   ```bash
   python bot.py
   ```

## Comandos

- `/start` - Inicia o bot e mostra mensagem de boas-vindas
- `/stats` - Mostra estatísticas do bot (apenas admins)

## Configuração

Configure as seguintes variáveis no arquivo `.env`:

- `BOT_TOKEN` - Token do bot do Telegram
- `GROUP_CHAT_ID` - ID do grupo principal
- `DUVIDAS_GROUP_CHAT_ID` - ID do grupo de dúvidas
- `ADMIN_IDS` - IDs dos administradores
- `DUVIDAS_GROUP_LINK` - Link do grupo de dúvidas
- `MENTORIA_LINK` - Link da mentoria

## Estrutura do Banco de Dados

### Tabela `users`
- `user_id` - ID único do usuário
- `username` - Nome de usuário do Telegram
- `first_name` - Primeiro nome
- `last_name` - Último nome
- `join_date` - Data de entrada
- `is_active` - Status ativo

### Tabela `messages`
- `id` - ID da mensagem
- `user_id` - ID do usuário
- `message_text` - Texto da mensagem
- `message_date` - Data da mensagem
- `group_id` - ID do grupo

## Autor

Bot desenvolvido para a comunidade Auge Traders.