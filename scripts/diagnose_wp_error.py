#!/usr/bin/env python3
"""Ativar WP_DEBUG no WordPress via SSH/FTP ou direto no wp-config.php"""

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('WORDPRESS_USER')
password = os.getenv('WORDPRESS_PASSWORD')

print("=" * 80)
print("DIAGNÓSTICO: Ativar WP_DEBUG no WordPress")
print("=" * 80)

# Tentar via REST API primeiro (pode não funcionar, mas tentamos)
print("\n🔍 Tentando diagnosticar via WP REST API...")

# Fazer um POST simples para ver resposta de erro detalhada
payload = {
    'title': 'Teste Debug',
    'content': '<!-- wp:paragraph --><p>Teste simples.</p><!-- /wp:paragraph -->',
    'status': 'draft',
    'categories': [20],
}

url = 'https://www.thefinance.news/wp-json/wp/v2/posts'

try:
    response = requests.post(url, auth=HTTPBasicAuth(user, password), json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if not response.ok:
        print("\n❌ Erro na resposta:")
        print(response.text[:1000])
        
        # Salvar resposta completa em arquivo
        with open('wp_error_response.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("\n💾 Resposta completa salva em: wp_error_response.txt")
        
except Exception as e:
    print(f"❌ Exceção: {str(e)}")

print("\n" + "=" * 80)
print("⚠️  PRÓXIMOS PASSOS:")
print("=" * 80)
print("""
1. Acessar wp-admin do WordPress
2. Ir para Ferramentas → Site Health (Saúde do Site)
3. Verificar se há erros/warnings
4. Ou ativar WP_DEBUG no wp-config.php:

   define('WP_DEBUG', true);
   define('WP_DEBUG_LOG', true);
   define('WP_DEBUG_DISPLAY', false);

5. Isto criará arquivo wp-content/debug.log com erros detalhados
""")

print("=" * 80)
