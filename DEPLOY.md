# Deploy no Render - Guia Passo a Passo 🚀

## Pré-requisitos
- Conta no GitHub
- Conta no Render (gratuita)
- Bot do Telegram criado via @BotFather

## Passo 1: Preparar o Repositório

1. **Criar repositório no GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Auge Bot"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/auge-bot.git
   git push -u origin main
   ```

## Passo 2: Deploy no Render

1. **Acessar Render:**
   - Vá para https://render.com
   - Faça login com GitHub

2. **Criar Web Service:**
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub
   - Selecione o repositório do bot

3. **Configurações do Deploy:**
   - **Name:** `auge-bot`
   - **Environment:** `Node`
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
   - **Plan:** `Free`

## Passo 3: Configurar Variáveis de Ambiente

No painel do Render, adicione as seguintes variáveis:

```
TELEGRAM_BOT_TOKEN=seu_token_aqui
MAIN_GROUP_CHAT_ID=id_do_grupo_principal
DUVIDAS_GROUP_CHAT_ID=id_do_grupo_duvidas
ADMIN_USER_IDS=123456789,987654321
NODE_ENV=production
```

## Passo 4: Deploy Automático

- O Render fará deploy automaticamente
- Aguarde alguns minutos
- Verifique os logs para confirmar que está funcionando

## Passo 5: Verificar Funcionamento

1. **Health Check:**
   - Acesse: `https://seu-app.onrender.com/health`
   - Deve retornar: `{"status": "ok", "message": "Auge Bot is running"}`

2. **Teste no Telegram:**
   - Envie uma mensagem no grupo
   - Teste comandos de admin
   - Verifique mensagens programadas

## Recursos do Render (Plano Gratuito)

- ✅ **750 horas/mês** (suficiente para 24/7)
- ✅ **Deploy automático** via GitHub
- ✅ **HTTPS gratuito**
- ✅ **Logs em tempo real**
- ✅ **Reinicialização automática**

## Monitoramento

- **Logs:** Painel do Render → "Logs"
- **Status:** Painel do Render → "Events"
- **Métricas:** Painel do Render → "Metrics"

## Troubleshooting

### Bot não responde:
1. Verificar variáveis de ambiente
2. Checar logs no Render
3. Confirmar token do bot
4. Verificar IDs dos grupos

### Deploy falha:
1. Verificar package.json
2. Checar dependências
3. Revisar logs de build

### Health check falha:
1. Verificar se a porta está correta
2. Confirmar se o servidor HTTP está rodando
3. Checar se a rota `/health` está acessível

## Comandos Úteis

```bash
# Atualizar código
git add .
git commit -m "Update bot"
git push

# Ver logs localmente
npm run dev

# Testar health check localmente
curl http://localhost:3000/health
```

## Próximos Passos

- ✅ Bot funcionando 24/7
- ✅ Deploy automático configurado
- ✅ Monitoramento ativo
- ✅ Backup automático via GitHub

**Seu bot agora está rodando 24/7 no Render! 🎉**