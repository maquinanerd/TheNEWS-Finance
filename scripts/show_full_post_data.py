#!/usr/bin/env python3
"""
Script definitivo: MOSTRA TUDO sobre o último post processado.
Entrada, saída, tokens, link de origem, link publicado, tudo!
"""

import json
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

def get_all_token_records():
    """Retorna todos os registros de tokens de hoje."""
    log_file = Path("logs/tokens/tokens_2026-02-05.jsonl")
    
    if not log_file.exists():
        return []
    
    records = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line))
    
    return records

def find_json_for_title(article_title):
    """Encontra o arquivo JSON que contém o artigo."""
    debug_dir = Path("debug")
    json_files = sorted(debug_dir.glob("ai_response_batch*.json"), reverse=True)
    
    for json_file in json_files:
        try:
            with open(json_file) as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'resultados' in data:
                posts = data['resultados']
            else:
                posts = [data]
            
            for post in posts:
                if isinstance(post, dict):
                    if article_title and article_title.lower() in post.get('titulo_final', '').lower():
                        return json_file, post
        except:
            continue
    
    return None, None

def format_html(html, max_length=300):
    """Formata HTML para visualização."""
    import re
    text = re.sub('<[^<]+?>', '', html)
    text = text.replace('\n', ' ').replace('  ', ' ').strip()
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text

def print_section(title):
    """Imprime um título de seção."""
    print("\n" + "="*110)
    print(f"  {title}")
    print("="*110 + "\n")

def main():
    records = get_all_token_records()
    
    if not records:
        print("❌ Nenhum registro de tokens encontrado!")
        return
    
    print("\n" + "#"*110)
    print("#" + " "*108 + "#")
    print("#" + " "*25 + "📊 RASTREAMENTO COMPLETO DE POSTS PROCESSADOS" + " "*38 + "#")
    print("#" + " "*108 + "#")
    print("#"*110)
    
    # Separar registros por tipo
    processing_records = [r for r in records if r.get('metadata', {}).get('operation') in ['batch_rewrite', 'single_rewrite']]
    publishing_records = [r for r in records if r.get('metadata', {}).get('operation') == 'published']
    
    print(f"\n📈 RESUMO: {len(processing_records)} posts processados | {len(publishing_records)} posts publicados\n")
    
    # Mostrar últimos 5 posts processados com detalhes completos
    print_section("🔝 ÚLTIMOS 5 POSTS PROCESSADOS (Mais recentes primeiro)")
    
    for idx, record in enumerate(processing_records[-5:][::-1], 1):
        timestamp = record.get('timestamp', 'N/A')
        source_url = record.get('source_url', 'N/A')
        article_title = record.get('article_title', 'N/A')
        entrada = record.get('prompt_tokens', 0)
        saida = record.get('completion_tokens', 0)
        total = entrada + saida
        
        print(f"Post #{idx}")
        print(f"  ⏰ Timestamp:           {timestamp}")
        print(f"  📥 Link de Origem:      {source_url}")
        print(f"  📌 Título:              {article_title}")
        print(f"  📊 Tokens entrada:      {entrada:,}")
        print(f"  📊 Tokens saída:        {saida:,}")
        print(f"  ✅ Total:               {total:,} tokens")
        
        # Encontrar JSON correspondente
        json_file, post_data = find_json_for_title(article_title)
        if json_file and post_data:
            print(f"  📦 JSON gerado:         {json_file.name}")
            print(f"  🔗 Slug (URL amigável): {post_data.get('slug', 'N/A')}")
            print(f"  💰 Custo estimado:      ${(entrada * (0.0375 / 1_000_000) + saida * (0.15 / 1_000_000)):.8f}")
        
        # Procurar se foi publicado
        for pub_record in publishing_records:
            if pub_record.get('article_title') == article_title and pub_record.get('wp_post_id'):
                wp_id = pub_record.get('wp_post_id')
                print(f"  ✅ PUBLICADO NO WORDPRESS:")
                print(f"     - ID WordPress:     {wp_id}")
                print(f"     - URL publicada:    https://www.thefinance.news/?p={wp_id}")
                break
        
        print()
    
    # Mostrar posts publicados
    if publishing_records:
        print_section("✅ POSTS PUBLICADOS NO WORDPRESS")
        
        for idx, record in enumerate(publishing_records[-5:][::-1], 1):
            timestamp = record.get('timestamp', 'N/A')
            wp_id = record.get('wp_post_id', 'N/A')
            article_title = record.get('article_title', 'N/A')
            source_url = record.get('source_url', 'N/A')
            
            print(f"Publicação #{idx}")
            print(f"  ⏰ Timestamp:           {timestamp}")
            print(f"  📌 Título:              {article_title}")
            print(f"  📥 Link de Origem:      {source_url}")
            print(f"  🆔 ID WordPress:        {wp_id}")
            print(f"  🔗 URL Publicada:       https://www.thefinance.news/?p={wp_id}")
            print()
    
    # Resumo de tokens
    print_section("📊 RESUMO CONSOLIDADO DE TOKENS")
    
    total_entrada = sum(r.get('prompt_tokens', 0) for r in processing_records)
    total_saida = sum(r.get('completion_tokens', 0) for r in processing_records)
    total_posts = len(processing_records)
    
    print(f"Total de posts processados: {total_posts}")
    print(f"Total Tokens Entrada:       {total_entrada:,}")
    print(f"Total Tokens Saída:         {total_saida:,}")
    print(f"Total Tokens Geral:         {total_entrada + total_saida:,}")
    print(f"\nMédia por post:")
    print(f"  - Entrada: {(total_entrada // max(total_posts, 1)):,} tokens")
    print(f"  - Saída:   {(total_saida // max(total_posts, 1)):,} tokens")
    
    custo_entrada = total_entrada * (0.0375 / 1_000_000)
    custo_saida = total_saida * (0.15 / 1_000_000)
    custo_total = custo_entrada + custo_saida
    
    print(f"\nCusto total estimado (gemini-2.5-flash-lite):")
    print(f"  - Entrada: ${custo_entrada:.8f}")
    print(f"  - Saída:   ${custo_saida:.8f}")
    print(f"  - TOTAL:   ${custo_total:.8f}")
    
    if total_posts > 0:
        print(f"  - Por post: ${(custo_total / total_posts):.8f}")
    
    # Arquivo de dados brutos
    print_section("📄 DADOS BRUTOS (JSONL)")
    print(f"Arquivo: logs/tokens/tokens_2026-02-05.jsonl")
    print(f"Total de registros: {len(records)}")
    print(f"\nÚltimo registro (completo):")
    print(json.dumps(records[-1], indent=2, ensure_ascii=False))
    
    print("\n" + "#"*110 + "\n")
    print("✅ FIM DO RELATÓRIO\n")

if __name__ == "__main__":
    main()
