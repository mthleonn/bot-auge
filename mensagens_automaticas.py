# Mensagens Automáticas - Bot Auge Traders
# Este arquivo contém as mensagens que podem ser enviadas automaticamente pelo bot

import random
from datetime import datetime

class MensagensAutomaticas:
    def __init__(self):
        self.mensagens_matinais = [
            {
                'texto': '''🌅 **BOM DIA, TRADERS!** 🌅

⏰ **6h em ponto** - Análise do pré-mercado chegando!

📊 Rafael e Daniel estão preparando:
• Setups do dia
• Possíveis entradas
• Níveis de saída
• Gestão de risco

👀 **Fiquem atentos** - oportunidades não esperam!

💪 Vamos fazer um dia **consistente**!'''
            },
            {
                'texto': '''☀️ **TRADERS, PREPAREM-SE!** ☀️

🎯 Em alguns minutos: **Análise completa do pré-mercado**

📈 **Foco total** nas oportunidades que Rafael e Daniel identificaram!

⚡ **Lembrete importante:**
• Sigam o plano de trade
• Respeitem o stop loss
• Disciplina sempre em primeiro lugar

🚀 **Sucesso é consistência!**'''
            }
        ]
        
        self.alertas_mercado = [
            {
                'texto': '''🚨 **ALERTA DE MERCADO** 🚨

📊 **Movimento importante** detectado!

⚡ **Atenção traders:**
• Acompanhem os níveis indicados
• Aguardem confirmação
• Mantenham a disciplina

🎯 **Oportunidade pode estar se formando!**

💪 Foco e execução!'''
            }
        ]
        
        self.mensagens_motivacionais = [
            {
                'texto': '''🔥 **MINDSET DE TRADER VENCEDOR** 🔥

💭 **Lembre-se:**
"O mercado recompensa a **disciplina**, não a pressa."

✅ **Trader consistente:**
• Segue o plano
• Controla as emoções
• Estuda constantemente
• Respeita o risco

📚 **Continue estudando** - conhecimento é poder!

🎯 [Acelere seu aprendizado na Mentoria](https://www.mentoriaaugetraders.com.br/)'''
            },
            {
                'texto': '''⚖️ **DISCIPLINA = CONSISTÊNCIA** ⚖️

🎯 **Trader disciplinado:**
• Não força trades
• Espera o setup perfeito
• Corta loss rapidamente
• Deixa o lucro correr

📈 **Resultado:** Conta crescendo mês após mês!

💪 **Seja paciente** - o mercado sempre oferece novas oportunidades!

🔥 **Foco no processo, não no resultado!**'''
            },
            {
                'texto': '''🌟 **VOCÊ ESTÁ NO CAMINHO CERTO!** 🌟

🎯 **Lembre-se:**
• Todo trader passou por dificuldades
• Consistência vem com tempo e prática
• Cada erro é uma lição valiosa
• Persistência é a chave do sucesso

📈 **Continue firme** na sua jornada!

🚀 **O sucesso** está mais próximo do que imagina!

💪 **Auge Traders** - juntos somos imparáveis!'''
            }
        ]
        
        self.mensagens_engajamento = [
            {
                'texto': '''💪 **TRADERS, COMO ESTÁ O DIA?** 💪

📊 **Compartilhem:**
• Como estão seguindo o plano?
• Alguma dúvida sobre os setups?
• Resultados do dia?

🤝 **Juntos somos mais fortes!**

❓ **Dúvidas?** Entre no nosso grupo:
[💬 Grupo de Dúvidas](https://t.me/+YgugjrIQHt1lNGNh)'''
            }
        ]
        
        self.lembretes_duvidas = [
            {
                'texto': '''❓ **TEM DÚVIDAS? NÓS TEMOS RESPOSTAS!** ❓

🎯 **Grupo exclusivo** para esclarecer:
• Análises técnicas
• Estratégias de entrada
• Gestão de risco
• Psicologia do trader

👥 **Nossa equipe** está pronta para ajudar!

[💬 Acesse o Grupo de Dúvidas](https://t.me/+YgugjrIQHt1lNGNh)

🚀 **Não fique com dúvidas - tire agora!**'''
            }
        ]
        
        self.promocao_mentoria = [
            {
                'texto': '''🎓 **QUER ACELERAR SEUS RESULTADOS?** 🎓

🚀 **Mentoria Auge Traders:**
• Aulas ao vivo com Rafael e Daniel
• Estratégias exclusivas
• Acompanhamento personalizado
• Comunidade de traders vencedores

💡 **Transforme** sua operação de vez!

[🎯 Conheça a Mentoria Completa](https://www.mentoriaaugetraders.com.br/)

⏰ **Vagas limitadas** - não perca!'''
            }
        ]
        
        self.mensagens_reuniao = [
            {
                'tipo': 'convite',
                'texto': '''📅 **REUNIÃO SEMANAL AUGE TRADERS** 📅

🎯 **Esta semana:**
📆 **Data:** {data}
⏰ **Horário:** {horario}
🔗 **Link:** {link_meet}

💡 **Pauta:**
• Review da semana
• Estratégias para próxima semana
• Tire suas dúvidas ao vivo
• Networking com outros traders

👥 **Presença confirmada?** Nos vemos lá!'''
            },
            {
                'tipo': 'lembrete',
                'texto': '''⏰ **LEMBRETE: REUNIÃO HOJE!** ⏰

📊 **Reunião Semanal Auge Traders**
🕐 **Horário:** {horario}
🔗 **Link:** {link_meet}

🎯 **Não perca:**
• Análise da semana
• Planejamento próxima semana
• Sessão de perguntas e respostas
• Dicas exclusivas dos mentores

👥 **Te esperamos lá!**'''
            },
            {
                'tipo': 'pos_reuniao',
                'texto': '''✅ **REUNIÃO FINALIZADA - OBRIGADO!** ✅

🎯 **Principais pontos:**
• Estratégias para próxima semana definidas
• Dúvidas esclarecidas
• Networking fortalecido

📚 **Não participou?** Fique atento às próximas!

💪 **Vamos aplicar** tudo que discutimos!

🚀 **Próxima reunião:** {proxima_data}'''
            }
        ]
        
        self.mensagens_fim_semana = [
            {
                'texto': '''🏁 **SEMANA FINALIZADA!** 🏁

📊 **Hora do review:**
• Como foi sua semana de trades?
• Objetivos alcançados?
• Lições aprendidas?

🔄 **Fim de semana é para:**
• Descansar a mente
• Estudar estratégias
• Planejar próxima semana

💪 **Segunda-feira voltamos** ainda mais fortes!

🎯 **Bom descanso, traders!**'''
            }
        ]
    
    def get_mensagem_matinal(self):
        """Retorna uma mensagem matinal aleatória"""
        return random.choice(self.mensagens_matinais)['texto']
    
    def get_alerta_mercado(self):
        """Retorna um alerta de mercado"""
        return random.choice(self.alertas_mercado)['texto']
    
    def get_mensagem_motivacional(self):
        """Retorna uma mensagem motivacional aleatória"""
        return random.choice(self.mensagens_motivacionais)['texto']
    
    def get_mensagem_engajamento(self):
        """Retorna uma mensagem de engajamento"""
        return random.choice(self.mensagens_engajamento)['texto']
    
    def get_lembrete_duvidas(self):
        """Retorna um lembrete sobre o grupo de dúvidas"""
        return random.choice(self.lembretes_duvidas)['texto']
    
    def get_promocao_mentoria(self):
        """Retorna uma mensagem de promoção da mentoria"""
        return random.choice(self.promocao_mentoria)['texto']
    
    def get_mensagem_reuniao(self, tipo, **kwargs):
        """Retorna uma mensagem de reunião formatada
        
        Args:
            tipo: 'convite', 'lembrete' ou 'pos_reuniao'
            **kwargs: data, horario, link_meet, proxima_data
        """
        for msg in self.mensagens_reuniao:
            if msg['tipo'] == tipo:
                return msg['texto'].format(**kwargs)
        return None
    
    def get_mensagem_fim_semana(self):
        """Retorna uma mensagem de fim de semana"""
        return random.choice(self.mensagens_fim_semana)['texto']
    
    def should_send_matinal(self):
        """Verifica se deve enviar mensagem matinal (6h)"""
        now = datetime.now()
        return now.hour == 6 and now.minute == 0
    
    def should_send_fim_semana(self):
        """Verifica se deve enviar mensagem de fim de semana (sexta 18h)"""
        now = datetime.now()
        return now.weekday() == 4 and now.hour == 18 and now.minute == 0  # Sexta-feira

# Exemplo de uso:
# mensagens = MensagensAutomaticas()
# print(mensagens.get_mensagem_matinal())
# print(mensagens.get_mensagem_reuniao('convite', data='15/01/2024', horario='20h', link_meet='https://meet.google.com/xxx'))