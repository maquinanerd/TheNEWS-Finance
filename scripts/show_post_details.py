#!/usr/bin/env python3
"""
Script para mostrar detalhes COMPLETOS do último post processado.
Correlaciona dados de tokens com o JSON gerado e banco de dados.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

def get_last_token_record():
    """Retorna o último registro de tokens."""
    log_file = Path("logs/tokens/tokens_2026-02-05.jsonl")
    
    if not log_file.exists():
        return None
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        return None
    
    return json.loads(lines[-1])

def find_corresponding_json(timestamp):
    """Encontra o arquivo JSON mais próximo do timestamp."""
    debug_dir = Path("debug")
    json_files = sorted(debug_dir.glob("ai_response_batch_*.json"), reverse=True)
    
    if not json_files:
        return None
    
    # Retorna o mais recente próximo ao timestamp
    return json_files[0]

def read_json_response(json_file):
    """Lê o arquivo JSON de resposta."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def get_article_from_db(title):
    """Procura o artigo no banco de dados pelo título."""
    try:
        conn = sqlite3.connect("app/store.db")
        cursor = conn.cursor()
        
        # Procurar por título similar
        cursor.execute("""
            SELECT db_id, source_url, article_title, status, date_published
            FROM articles 
            WHERE article_title LIKE ? OR article_title LIKE ?
            ORDER BY date_published DESC 
            LIMIT 1
        """, (f"%{title[:30]}%", f"%{title.split()[0]}%"))
        
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Erro ao consultar DB: {e}")
        return None

def get_wordpress_post(db_id):
    """Procura o post publicado no WordPress."""
    try:
        conn = sqlite3.connect("app/store.db")
        cursor = conn.cursor()
        
        # Procurar post processado
        cursor.execute("""
            SELECT wp_post_id, status, processed_at
            FROM processed_articles 
            WHERE article_db_id = ?
            LIMIT 1
        """, (db_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Erro ao consultar DB: {e}")
        return None

def format_html(html, max_lines=5):
    """Formata HTML para visualização."""
    # Remover tags
    import re
    text = re.sub('<[^<]+?>', '', html)
    # Pegar primeiros caracteres
    return text[:200].replace('\n', ' ').strip() + "..."

def main():
    print("\n" + "="*100)
    print("📋 DETALHES COMPLETOS DO ÚLTIMO POST PROCESSADO")
    print("="*100 + "\n")
    
    # 1. Pegar registro de tokens
    token_record = get_last_token_record()
    if not token_record:
        print("❌ Nenhum registro de tokens encontrado!")
        return
    
    print(f"⏰ Timestamp do processamento: {token_record['timestamp']}")
    print()
    
    # 2. Encontrar JSON correspondente
    json_file = find_corresponding_json(token_record['timestamp'])
    if not json_file:
        print("⚠️  Arquivo JSON não encontrado")
        json_data = None
    else:
        print(f"📦 Arquivo JSON gerado: {json_file.name}")
        json_data = read_json_response(json_file)
    
    print()
    print("="*100)
    print("📝 DADOS DO POST")
    print("="*100)
    print()
    
    if json_data:
        # Se é um array de resultados
        if isinstance(json_data, dict) and 'resultados' in json_data:
            post = json_data['resultados'][0] if json_data['resultados'] else {}
        else:
            post = json_data
        
        print(f"📌 Título final:        {post.get('titulo_final', 'N/A')}")
        print(f"🔗 Slug:                {post.get('slug', 'N/A')}")
        print(f"📂 Categorias:          {', '.join([c.get('nome', 'N/A') for c in post.get('categorias', [])])}")
        print(f"🏷️  Tags:                {', '.join(post.get('tags_sugeridas', [])[:5])}")
        print()
        print("Conteúdo (primeiros 200 caracteres):")
        print("-" * 100)
        print(format_html(post.get('conteudo_final', 'N/A')))
        print("-" * 100)
        print()
    else:
        print("⚠️  Não consegui ler o JSON")
        print()
    
    print("="*100)
    print("🔗 URLs")
    print("="*100)
    print()
    
    # Pegar título do JSON
    titulo = "N/A"
    if json_data:
        if isinstance(json_data, dict) and 'resultados' in json_data:
            post = json_data['resultados'][0] if json_data['resultados'] else {}
        else:
            post = json_data
        titulo = post.get('titulo_final', 'N/A')
    
    # Procurar no banco de dados
    article_info = None
    if titulo != "N/A":
        article_info = get_article_from_db(titulo)
    
    if article_info:
        db_id, source_url, db_title, status, date_pub = article_info
        print(f"📥 Link de origem:      {source_url}")
        
        # Procurar post no WordPress
        wp_info = get_wordpress_post(db_id)
        if wp_info:
            wp_id, wp_status, processed_at = wp_info
            print(f"✅ Link publicado:      https://www.thefinance.news/?p={wp_id}")
            print(f"   Status: {wp_status}")
        else:
            print(f"✅ Link publicado:      Post encontrado no DB (status: {status})")
    else:
        print(f"📥 Link de origem:      Não encontrado no banco")
        print(f"✅ Link publicado:      Não encontrado no banco")
    
    print()
    print("="*100)
    print("⚡ CONSUMO DE TOKENS")
    print("="*100)
    print()
    
    entrada = token_record.get('prompt_tokens', 0)
    saida = token_record.get('completion_tokens', 0)
    total = entrada + saida
    
    print(f"📥 Entrada (Prompt):    {entrada:,} tokens")
    print(f"📤 Saída (Resposta):    {saida:,} tokens")
    print("-" * 100)
    print(f"✅ TOTAL:               {total:,} tokens")
    print()
    
    # Calcular custos
    custo_entrada = entrada * (0.0375 / 1_000_000)
    custo_saida = saida * (0.15 / 1_000_000)
    custo_total = custo_entrada + custo_saida
    
    print("💰 Custo (gemini-2.5-flash-lite):")
    print(f"   Entrada: {entrada:,} × $0.0375/1M = ${custo_entrada:.8f}")
    print(f"   Saída:   {saida:,} × $0.15/1M  = ${custo_saida:.8f}")
    print("   " + "-" * 90)
    print(f"   Total:                                = ${custo_total:.8f}")
    
    if custo_total > 0:
        print(f"   ({1/custo_total:.0f}º de um centavo)")
    
    print()
    print("="*100)
    print("🔬 REQUISIÇÃO (PROMPT ENVIADO)")
    print("="*100)
    print()
    
    # Não temos o prompt armazenado, mas podemos mostrar que foi enviado
    print(f"🤖 Modelo:              {token_record.get('model', 'N/A')}")
    print(f"🔄 Operação:            {token_record.get('metadata', {}).get('operation', 'N/A')}")
    print(f"📊 Tamanho do batch:     {token_record.get('metadata', {}).get('batch_size', 'N/A')}")
    print()
    print("⚠️  Nota: O prompt completo não é armazenado (seria muito grande).")
    print("          Mas foi enviado para a API Gemini com base no template de prompt.")
    print()
    print("="*100 + "\n")

if __name__ == "__main__":
    main()
