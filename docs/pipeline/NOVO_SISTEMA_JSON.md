# 🎯 NOVO SISTEMA DE ARMAZENAMENTO JSON

## ✅ Mudanças Implementadas

### 1. **Nomenclatura dos JSONs**
Antes:
```
debug/ai_response_batch_YYYYMMDD-HHMMSS.json
```

**Depois (NOVO):**
```
debug/ai_response_batch_{slug}_YYYYMMDD-HHMMSS.json
```

**Exemplo:**
```
debug/ai_response_batch_jogos-olimpicos-inverno-2026-filmes-series_20260205-143521.json
```

### 2. **Quando o JSON é Salvo**
- **Antes**: Só eram salvos JSONs de ERRO (em `failed_ai_*.json.txt`)
- **Depois**: JSONs são salvos **APÓS PUBLICAÇÃO** no WordPress

**Fluxo:**
```
RSS Feed 
  ↓
Extrai conteúdo 
  ↓
Processa com IA (recebe JSON estruturado)
  ↓
Publica no WordPress (wp_post_id criado)
  ↓
✅ SALVA JSON no debug/ com SLUG + timestamp
  ↓
Registra nos TOKENS com corr...
```

### 3. **Localização do JSON Para Qualquer Post**

Se você conhece o **slug** do post:
```powershell
Get-ChildItem debug/*{slug}*.json
```

**Exemplo:**
```powershell
Get-ChildItem debug/*jogos-olimpicos-inverno*.json
```

Se você conhece a **data de publicação**:
```powershell
Get-ChildItem debug/*20260205*.json
```

### 4. **Tokens + JSON + WordPress ID - Tudo Conectado**

Arquivo de log: `logs/tokens/tokens_2026-02-05.jsonl`

Exemplo de correlação:
```json
{
  "timestamp": "2026-02-05T14:35:21",
  "api_type": "publishing",
  "model": "wordpress",
  "wp_post_id": 71064,
  "article_title": "Jogos Olímpicos de Inverno 2026: Filmes e Séries para Assistir",
  "source_url": "https://screenrant.com/...",
  "metadata": {
    "slug": "jogos-olimpicos-inverno-2026-filmes-series"
  }
}
```

**Para encontrar tudo sobre este post:**
```powershell
# 1. Encontra o JSON
Get-ChildItem debug/*jogos-olimpicos-inverno-2026*.json

# 2. Abre o WordPress
Start-Process "https://www.thefinance.news/?p=71064"

# 3. Verifica os tokens
Select-String -Path "logs/tokens/tokens_2026-02-05.jsonl" -Pattern "jogos-olimpicos"
```

### 5. **Como Executar**

Tudo é **automático**! Só rodeos:

```bash
python main.py
```

E o sistema irá:
1. ✅ Processar artigos em lote
2. ✅ Publicar no WordPress
3. ✅ Salvar JSON com slug (identifica o post)
4. ✅ Registrar tokens e wp_post_id no JSONL
5. ✅ Tudo correlacionado para rastreamento completo

---

## 📊 Verificação Rápida

**Ver último post publicado:**
```powershell
$lastJson = Get-ChildItem debug/ai_response_batch_*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $lastJson | ConvertFrom-Json | Select-Object titulo_final, slug | Format-List
```

**Ver todos os posts de hoje:**
```powershell
Get-ChildItem debug/ai_response_batch_*20260205*.json | ForEach-Object { 
  $json = Get-Content $_ | ConvertFrom-Json
  Write-Host "- $($json.titulo_final) ($($json.slug))"
}
```

---

## 🎯 Estrutura Final

```
debug/
├── ai_response_batch_slugs-do-post_20260205-143521.json  ← NOVO!
├── ai_response_batch_outro-slug_20260205-144015.json    ← NOVO!
└── failed_ai_20251029-192256.json.txt  ← Ainda mantém erros

logs/
└── tokens/
    └── tokens_2026-02-05.jsonl  ← Todos os tokens + slug + wp_post_id

WordPress:
└── Post ID 71064 (jogos-olimpicos-inverno-2026-filmes-series)
```

**TUDO CONECTADO!** 🎉
