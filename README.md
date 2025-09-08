# 🤖 Auge Análises Bot

Bot oficial do Telegram para o **Grupo de Análises - Auge**, especializado em Day Trade com funcionalidades automatizadas de boas-vindas, funil de vendas e mensagens programadas.

## 📋 Funcionalidades

### ✅ Implementadas

- **🎉 Mensagem de Boas-Vindas Automática**
  - Detecta novos membros automaticamente
  - Mensagem de boas-vindas ao Grupo de Análises - Auge
  - Rastreamento de cliques nos botões

- **📈 Funil de Conversão Automático**
  - **5 minutos**: Mensagem sobre grupo de dúvidas
  - **24h**: Mensagem com benefícios da mentoria
  - **48h**: Case de sucesso de aluno

- **🌅 Mensagem Diária Programada**
  - "Bom dia, trader!" enviada às 06:00 (horário de Brasília)
  - Cria expectativa para análises do Rafael e Daniel

- **📊 Sistema de Monitoramento**
  - Rastreamento de cliques nos links
  - Estatísticas detalhadas para administradores
  - Banco de dados SQLite integrado

- **🔧 Comandos de Administrador**
  - Envio de comunicados manuais
  - Visualização de estatísticas
  - Gerenciamento de usuários
  - Criação de links do Google Meet para reuniões

- **🛡️ Moderação Básica**
  - Detecção e remoção de spam
  - Proteção contra links não autorizados

## 🚀 Instalação e Configuração

### Pré-requisitos

- Node.js 16+ instalado
- Token do bot do Telegram (obtenha com @BotFather)
- ID do grupo do Telegram

### Passo a Passo

1. **Clone ou baixe o projeto**
   ```bash
   cd BotAuge
   ```

2. **Instale as dependências**
   ```bash
   npm install
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   ```
   
   Edite o arquivo `.env` com suas informações:
   ```env
   TELEGRAM_BOT_TOKEN=seu_token_aqui
   GROUP_CHAT_ID=id_do_seu_grupo
   DUVIDAS_GROUP_LINK=https://t.me/seu_grupo_duvidas
   MENTORIA_LINK=https://sua-mentoria-link.com
   ADMIN_IDS=123456789,987654321
   ```

4. **Inicie o bot**
   ```bash
   npm start
   ```
   
   Para desenvolvimento:
   ```bash
   npm run dev
   ```

## 📁 Estrutura do Projeto

```
BotAuge/
├── src/
│   ├── bot.js                 # Arquivo principal do bot
│   ├── database.js            # Gerenciamento do banco de dados
│   └── handlers/
│       ├── messageHandler.js  # Processamento de mensagens
│       ├── welcomeHandler.js  # Mensagens de boas-vindas
│       ├── funnelHandler.js   # Funil de conversão
│       └── adminHandler.js    # Comandos administrativos
├── data/                      # Banco de dados SQLite (criado automaticamente)
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

## 🎯 Como Obter as Informações Necessárias

### 1. Token do Bot
1. Abra o Telegram e procure por @BotFather
2. Digite `/newbot` e siga as instruções
3. Escolha um nome e username para seu bot
4. Copie o token fornecido

### 2. ID do Grupo
1. Adicione o bot ao seu grupo
2. Envie uma mensagem no grupo
3. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Procure pelo `chat.id` (número negativo)

### 3. IDs dos Administradores
1. Procure por @userinfobot no Telegram
2. Envie `/start` para obter seu ID
3. Adicione os IDs no arquivo `.env` separados por vírgula

## 📱 Comandos Disponíveis

### Para Usuários
- `/start` - Informações do bot
- `/help` - Ajuda e comandos
- `/links` - Links importantes

### Para Administradores
- `/admin broadcast <mensagem>` - Enviar comunicado
- `/admin stats` - Estatísticas detalhadas
- `/admin users` - Lista de usuários recentes
- `/admin reuniao` - Criar link do Google Meet para reuniões
- `/admin test` - Mensagem de teste
- `/admin help` - Ajuda administrativa

## 🔧 Configurações Avançadas

### Personalizar Mensagens

As mensagens podem ser editadas nos seguintes arquivos:
- **Boas-vindas**: `src/handlers/welcomeHandler.js`
- **Funil 24h/48h/72h**: `src/handlers/funnelHandler.js`
- **Mensagem diária**: `src/bot.js`

### Horários

- **Mensagem diária**: Configurada para 06:00 (timezone configurável)
- **Verificação do funil**: A cada hora
- **Timezone padrão**: America/Sao_Paulo

### Banco de Dados

O bot utiliza SQLite com as seguintes tabelas:
- `users` - Informações dos usuários
- `link_clicks` - Rastreamento de cliques
- `scheduled_messages` - Mensagens agendadas

## 📊 Monitoramento

### Logs
O bot registra todas as atividades importantes no console:
- Novos membros
- Mensagens do funil enviadas
- Cliques nos links
- Erros e problemas

### Estatísticas
Administradores podem acessar:
- Total de usuários
- Cliques nos links
- Progresso no funil de conversão
- Usuários recentes

## 🛠️ Manutenção

### Backup do Banco de Dados
```bash
cp data/bot.db data/bot_backup_$(date +%Y%m%d).db
```

### Logs de Erro
Verifique o console para mensagens de erro. Problemas comuns:
- Token inválido
- Bot não adicionado ao grupo
- Permissões insuficientes

### Atualizações
```bash
npm update
```

## 🔒 Segurança

- ✅ Arquivo `.env` no `.gitignore`
- ✅ Validação de administradores
- ✅ Proteção contra spam
- ✅ Sanitização de mensagens

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs no console
2. Confirme as configurações no `.env`
3. Teste com `/admin test`
4. Entre no grupo de dúvidas configurado

## 📄 Licença

MIT License - Veja o arquivo LICENSE para detalhes.

---

**Desenvolvido para o Grupo de Análises - Auge** 🚀

*Bot criado para automatizar e otimizar a experiência dos traders no grupo de análises, facilitando o processo de conversão e engajamento.*