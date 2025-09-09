# 🚀 Bot Telegram para Railway

Este é um bot Telegram em Python pronto para deploy gratuito no Railway.

## 📁 Arquivos do Projeto

- `bot.py` - Código principal do bot
- `requirements.txt` - Dependências Python
- `Procfile` - Configuração para Railway
- `README_RAILWAY.md` - Este arquivo com instruções

## 🤖 Funcionalidades do Bot

- `/start` - Inicia o bot e mostra mensagem de boas-vindas
- `/help` - Mostra comandos disponíveis
- `/status` - Verifica se o bot está funcionando
- Echo de mensagens - Repete qualquer texto enviado

## 🛠️ Como Deployar no Railway

### Passo 1: Criar Bot no Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Digite `/newbot`
3. Escolha um nome para seu bot (ex: "Meu Bot Railway")
4. Escolha um username (ex: "meubot_railway_bot")
5. **Copie o token** que o BotFather forneceu (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Passo 2: Preparar o Código

1. Faça upload dos arquivos para um repositório GitHub:
   - `bot.py`
   - `requirements.txt`
   - `Procfile`
   - `README_RAILWAY.md`

### Passo 3: Deploy no Railway

1. **Acesse o Railway**
   - Vá para [railway.app](https://railway.app)
   - Faça login com sua conta GitHub

2. **Criar Novo Projeto**
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha o repositório com os arquivos do bot

3. **Configurar Variável de Ambiente**
   - No dashboard do projeto, vá para a aba "Variables"
   - Clique em "New Variable"
   - Nome: `BOT_TOKEN`
   - Valor: Cole o token que você copiou do BotFather
   - Clique em "Add"

4. **Deploy Automático**
   - O Railway detectará automaticamente o `Procfile`
   - O deploy começará automaticamente
   - Aguarde alguns minutos para o deploy completar

### Passo 4: Verificar se Está Funcionando

1. **Verificar Logs**
   - No dashboard do Railway, vá para a aba "Deployments"
   - Clique no deployment mais recente
   - Verifique os logs para ver se há erros

2. **Testar o Bot**
   - Abra o Telegram
   - Procure pelo username do seu bot
   - Digite `/start`
   - Você deve receber: "🚀 Bot ativo no Railway!"

## 🔧 Comandos Disponíveis

| Comando | Descrição |
|---------|----------|
| `/start` | Inicia o bot |
| `/help` | Mostra ajuda |
| `/status` | Verifica status |

## 📝 Estrutura do Código

### bot.py
- Usa `python-telegram-bot` v20.7
- Configurado para polling (não webhook)
- Lê token da variável de ambiente `BOT_TOKEN`
- Inclui tratamento de erros
- Logging configurado

### requirements.txt
- `python-telegram-bot==20.7` - Biblioteca principal
- `requests==2.31.0` - Para requisições HTTP

### Procfile
- `worker: python bot.py` - Comando para Railway executar

## 🆘 Solução de Problemas

### Bot não responde
1. **Verificar token**
   - Confirme se o `BOT_TOKEN` está correto no Railway
   - Token deve ter formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

2. **Verificar logs**
   - Vá para Railway → Deployments → Ver logs
   - Procure por erros em vermelho

3. **Verificar deploy**
   - Certifique-se que o deploy foi bem-sucedido
   - Status deve estar "Active"

### Erro de dependências
- Verifique se o `requirements.txt` está correto
- Railway instala automaticamente as dependências

### Bot para de funcionar
- Railway gratuito tem limite de horas mensais
- Verifique se não excedeu o limite
- Considere upgrade para plano pago se necessário

## 💡 Dicas Importantes

1. **Plano Gratuito Railway**
   - 500 horas por mês
   - Suficiente para bots pequenos
   - Bot "dorme" após inatividade

2. **Manter Bot Ativo**
   - Bots podem "dormir" após inatividade
   - Use serviços como UptimeRobot para ping periódico

3. **Monitoramento**
   - Verifique logs regularmente
   - Configure alertas se necessário

4. **Segurança**
   - Nunca compartilhe seu token
   - Use apenas variáveis de ambiente
   - Não commite tokens no código

## 🔄 Atualizações

Para atualizar o bot:
1. Faça push das mudanças para o GitHub
2. Railway fará deploy automático
3. Verifique logs para confirmar sucesso

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs no Railway
2. Confirme se todas as variáveis estão configuradas
3. Teste localmente primeiro
4. Consulte documentação do Railway

---

✅ **Pronto! Seu bot está rodando gratuitamente no Railway!**