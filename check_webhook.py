#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

def check_webhook_info():
    """Verifica informações do webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print("=== INFORMAÇÕES DO WEBHOOK ===")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {data}")
        
        if data.get('ok'):
            webhook_info = data.get('result', {})
            webhook_url = webhook_info.get('url', '')
            
            if webhook_url:
                print(f"\n🚨 WEBHOOK ATIVO: {webhook_url}")
                print("\n⚠️  Há uma instância do bot rodando em produção!")
                print("Isso está causando o conflito com a instância local.")
                
                # Tentar deletar o webhook
                delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
                delete_response = requests.post(delete_url)
                delete_data = delete_response.json()
                
                print(f"\n🔄 Tentando deletar webhook...")
                print(f"Resultado: {delete_data}")
                
                if delete_data.get('ok'):
                    print("✅ Webhook deletado com sucesso!")
                    print("Agora você pode rodar o bot localmente.")
                else:
                    print("❌ Erro ao deletar webhook.")
            else:
                print("\n✅ Nenhum webhook configurado.")
                print("O bot pode rodar localmente sem conflitos.")
        else:
            print(f"❌ Erro na API: {data}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar webhook: {e}")

def check_bot_updates():
    """Verifica se há atualizações pendentes"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print("\n=== ATUALIZAÇÕES PENDENTES ===")
        if data.get('ok'):
            updates = data.get('result', [])
            print(f"Número de atualizações pendentes: {len(updates)}")
            
            if updates:
                print("\n📝 Últimas atualizações:")
                for update in updates[-3:]:  # Mostrar apenas as 3 últimas
                    update_id = update.get('update_id')
                    message = update.get('message', {})
                    if message:
                        user = message.get('from', {})
                        text = message.get('text', 'N/A')
                        print(f"  - ID: {update_id}, Usuário: {user.get('first_name', 'N/A')}, Texto: {text[:50]}...")
        else:
            print(f"❌ Erro: {data}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar atualizações: {e}")

if __name__ == '__main__':
    print("🔍 Verificando status do bot...\n")
    check_webhook_info()
    check_bot_updates()
    print("\n✅ Verificação concluída!")