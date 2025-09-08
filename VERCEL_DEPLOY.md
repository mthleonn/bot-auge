# 🚀 Deploy do Bot no Vercel

## 📋 Pré-requisitos

1. **Conta no Vercel**: [vercel.com](https://vercel.com)
2. **Conta no GitHub**: Código já está no repositório
3. **Token do Bot**: `7482522123:AAH3h3h3h3h3h3h3h3h3h3h3h3h3h3h3`

## 🔧 Passo a Passo

### 1. Conectar Repositório

1. Acesse [vercel.com](https://vercel.com)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione o repositório `auge-bot`
5. Clique em "Import"

### 2. Configurar Variáveis de Ambiente

Na seção "Environment Variables", adicione:

```
TELEGRAM_BOT_TOKEN=7482522123:AAH3h3h3h3h3h3h3h3h3h3h3h3h3h3h3
GROUP_CHAT_ID=-1002132456789
DUVIDAS_GROUP_CHAT_ID=-4797522493
DUVIDAS_GROUP_LINK=https://t.me/+YgugjrIQHt1lNGNh
MENTORIA_LINK=https://www.mentoriaaugetraders.com.br/
ADMIN_IDS=SEU_ID_AQUI
DB_PATH=/tmp/bot.db
TIMEZONE=America/Sao_Paulo
NODE_ENV=production
```

**⚠️ IMPORTANTE**: Substitua `SEU_ID_AQUI` pelo seu ID real do Telegram!

### 3. Configurações de Build

- **Framework Preset**: Other
- **Root Directory**: `./`
- **Build Command**: `npm install`
- **Output Directory**: Deixe vazio
- **Install Command**: `npm install`

### 4. Deploy

1. Clique em "Deploy"
2. Aguarde o build completar
3. Anote a URL gerada (ex: `https://auge-bot.vercel.app`)

### 5. Configurar Webhook

Após o deploy, configure o webhook do Telegram:

```bash
curl -X POST "https://api.telegram.org/bot7482522123:AAH3h3h3h3h3h3h3h3h3h3h3h3h3h3h3/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://SUA_URL_VERCEL.vercel.app/api/bot"}'
```

**Substitua `SUA_URL_VERCEL` pela URL real do seu deploy!**

## 🔍 Como Descobrir Seu ID

1. Procure `@userinfobot` no Telegram
2. Envie `/start`
3. Copie o User ID
4. Atualize a variável `ADMIN_IDS` no Vercel

## ✅ Verificar se Funcionou

1. **Health Check**: Acesse `https://SUA_URL.vercel.app/api/bot`
2. **Teste no Telegram**: Envie `/testmsg` no grupo
3. **Logs**: Verifique os logs no painel do Vercel

## 🆘 Troubleshooting

### Bot não responde:
- Verifique se o webhook foi configurado
- Confirme as variáveis de ambiente
- Verifique os logs no Vercel

### Erro 401:
- Token incorreto
- Verifique a variável `TELEGRAM_BOT_TOKEN`

### Comandos admin não funcionam:
- Verifique se seu ID está em `ADMIN_IDS`
- Use `@userinfobot` para descobrir seu ID

## 🎯 Vantagens do Vercel

- ✅ Deploy automático via GitHub
- ✅ Escalabilidade automática
- ✅ SSL gratuito
- ✅ Logs em tempo real
- ✅ Fácil configuração

## 📱 Próximos Passos

1. Configure o webhook
2. Teste todos os comandos
3. Monitore os logs
4. Aproveite o bot 24/7! 🚀