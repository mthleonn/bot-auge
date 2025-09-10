# 🚀 Deploy do Bot Auge Traders no Railway

## 📋 Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Bot do Telegram criado via @BotFather
3. Repositório GitHub com o código

## 🔧 Configuração no Railway

### 1. Criar Novo Projeto

1. Acesse [Railway](https://railway.app)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha o repositório do bot

### 2. Configurar Variáveis de Ambiente

No painel do Railway, vá em **Variables** e adicione:

```env
# Token do Bot (obrigatório)
BOT_TOKEN=seu_token_aqui

# IDs dos Grupos (obrigatório)
GROUP_CHAT_ID=-1002132456789
DUVIDAS_GROUP_CHAT_ID=-4797522493

# Administradores (obrigatório)
ADMIN_IDS=123456789,987654321

# Links (opcional)
DUVIDAS_GROUP_LINK=https://t.me/+5ueqV0IGf7NlODIx
MENTORIA_LINK=https://www.mentoriaaugetraders.com.br/

# Configurações do Railway (obrigatório)
ENVIRONMENT=production
WEBHOOK_URL=https://seu-app-name.up.railway.app
PORT=8000
```

### 3. Configurar Webhook URL

⚠️ **IMPORTANTE**: Após o primeiro deploy, você receberá uma URL do Railway (ex: `https://bot-auge-production.up.railway.app`)

1. Copie essa URL
2. Vá em **Variables** no Railway
3. Atualize a variável `WEBHOOK_URL` com a URL real
4. Redeploy o projeto

## 🔄 Como Funciona

### Modo Desenvolvimento (Local)
- Usa **polling** para receber mensagens
- Variável `ENVIRONMENT=development`
- Executa: `python bot.py`

### Modo Produção (Railway)
- Usa **webhook** para receber mensagens
- Variável `ENVIRONMENT=production`
- Servidor Flask na porta definida por `PORT`
- Health check em `/health`

## 🛠️ Comandos Úteis

### Testar Localmente
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env para desenvolvimento
ENVIRONMENT=development

# Executar
python bot.py
```

### Verificar Logs no Railway
1. Acesse o painel do projeto
2. Clique na aba **Deployments**
3. Clique no deployment ativo
4. Veja os logs em tempo real

## 🔍 Troubleshooting

### Bot não responde no Railway
1. Verifique se `WEBHOOK_URL` está correto
2. Confirme que `ENVIRONMENT=production`
3. Verifique logs no Railway
4. Teste o health check: `https://sua-url.railway.app/health`

### Erro de webhook
1. Verifique se a URL está acessível
2. Confirme que o bot tem permissões no grupo
3. Teste manualmente: `curl https://sua-url.railway.app/health`

### Conflito de instâncias
- Certifique-se de que não há outra instância rodando
- Pare execução local antes do deploy
- Use apenas uma instância em produção

## 📊 Monitoramento

### Health Check
- URL: `https://sua-url.railway.app/health`
- Resposta esperada: `{"status": "healthy", "bot": "Auge Traders"}`

### Logs Importantes
```
🚀 Iniciando bot em modo WEBHOOK (Railway)
Configurado webhook: https://sua-url.railway.app/[token]
Webhook configurado com sucesso!
Iniciando servidor Flask na porta 8000
```

## 🔐 Segurança

- ✅ Token do bot protegido via variáveis de ambiente
- ✅ Webhook endpoint protegido com token
- ✅ Health check público (sem dados sensíveis)
- ✅ Logs não expõem informações confidenciais

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no Railway
2. Confirme todas as variáveis de ambiente
3. Teste o health check
4. Verifique se o bot está ativo no @BotFather