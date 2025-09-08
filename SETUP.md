# 🚀 Setup Rápido - Auge Análises Bot

## ⚡ Instalação em 5 Minutos

### 1. Preparar o Ambiente
```bash
# Instalar dependências
npm install

# Copiar arquivo de configuração
copy .env.example .env
```

### 2. Criar o Bot no Telegram
1. Abra o Telegram
2. Procure por **@BotFather**
3. Digite: `/newbot`
4. Escolha um nome: `Auge Análises Bot`
5. Escolha um username: `auge_analises_bot` (ou similar)
6. **Copie o token fornecido**

### 3. Obter ID do Grupo
1. Adicione o bot ao seu grupo
2. Torne o bot administrador
3. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Procure pelo número negativo em `chat.id`

### 4. Configurar o Arquivo .env
```env
# Cole seu token aqui
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Cole o ID do grupo (número negativo)
GROUP_CHAT_ID=-1001234567890

# Configure seus links
DUVIDAS_GROUP_LINK=https://t.me/seu_grupo_duvidas
MENTORIA_LINK=https://sua-mentoria-link.com

# Seu ID de usuário (para ser admin)
ADMIN_IDS=123456789
```

### 5. Iniciar o Bot
```bash
npm start
```

## ✅ Verificar se Está Funcionando

1. **Teste básico**: Digite `/admin test` no grupo
2. **Adicione um usuário teste** ao grupo
3. **Verifique os logs** no terminal

## 🆘 Problemas Comuns

### Bot não responde
- ✅ Verificar se o token está correto
- ✅ Confirmar se o bot é administrador do grupo
- ✅ Verificar se o GROUP_CHAT_ID está correto

### Erro de permissão
- ✅ Bot precisa ser administrador
- ✅ Verificar se seu ID está em ADMIN_IDS

### Mensagens não chegam
- ✅ Verificar conexão com internet
- ✅ Confirmar se o bot não foi bloqueado

## 📱 Como Obter Seu ID de Usuário

1. Procure por **@userinfobot** no Telegram
2. Digite `/start`
3. Copie o número do seu ID
4. Adicione no arquivo `.env` em ADMIN_IDS

## 🎯 Próximos Passos

1. **Personalizar mensagens** em `src/handlers/`
2. **Configurar links reais** no `.env`
3. **Testar funil completo** com usuário teste
4. **Monitorar logs** para verificar funcionamento

---

**🚀 Pronto! Seu bot está funcionando!**

Para mais detalhes, consulte o arquivo `README.md`