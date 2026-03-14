#!/usr/bin/env python3
"""Test Gutenberg block conversion with WordPress"""

import requests
from requests.auth import HTTPBasicAuth
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from app.html_utils import html_to_gutenberg_blocks

load_dotenv()

user = os.getenv('WORDPRESS_USER')
password = os.getenv('WORDPRESS_PASSWORD')

print("=" * 80)
print("TESTE: Enviar conteúdo Gutenberg para WordPress")
print("=" * 80)

# HTML de teste - simples
html_input = """
<p>Primeiro parágrafo do artigo.</p>
<p>Segundo parágrafo com <b>texto em negrito</b>.</p>
<p>Terceiro parágrafo normal.</p>
"""

print("\n📝 HTML de entrada:")
print(html_input)

# Converter para Gutenberg
print("\n🔄 Convertendo para Gutenberg...")
gutenberg_content = html_to_gutenberg_blocks(html_input)

print("\n✅ Conteúdo Gutenberg:")
print(gutenberg_content[:500])

#  Enviar para WordPress
payload = {
    'title': f'Teste Gutenberg - {datetime.now().strftime("%H:%M:%S")}',
    'content': gutenberg_content,
    'status': 'draft',
    'categories': [20],
}

url = 'https://www.thefinance.news/wp-json/wp/v2/posts'
payload_size = len(json.dumps(payload))

print(f"\n📊 Payload:")
print(f"   Tamanho: {payload_size} bytes ({payload_size/1024:.2f} KB)")

print(f"\n🚀 Enviando POST para WordPress...")

try:
    response = requests.post(url, auth=HTTPBasicAuth(user, password), json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.ok:
        post_id = response.json().get('id')
        print(f"✅ POST criado com sucesso! ID: {post_id}")
    else:
        print(f"❌ Erro {response.status_code}:")
        try:
            error_data = response.json()
            print(f"   Código: {error_data.get('code')}")
            print(f"   Mensagem: {error_data.get('message')[:200]}...")
        except:
            print(f"   Resposta: {response.text[:300]}")
            
except Exception as e:
    print(f"❌ Exceção: {str(e)[:300]}")

print("\n" + "=" * 80)
