# 🚀 TheNerdMN - Pipeline Automatizado de Conteúdo com IA

**Sistema completo de automatização de publicação de artigos**: lê feeds RSS, reescreve com IA (Gemini), e publica no WordPress em tempo real.

---

## 📋 Índice

1. [O que é](#o-que-é)
2. [Arquitetura](#arquitetura)
3. [Funcionalidades](#funcionalidades)
4. [Configuração](#configuração)
5. [Feeds RSS](#feeds-rss)
6. [Chaves de API](#chaves-de-api)
7. [Variáveis de Ambiente](#variáveis-de-ambiente)
8. [Como Executar](#como-executar)
9. [Fluxo de Processamento](#fluxo-de-processamento)
10. [Estrutura de Arquivos](#estrutura-de-arquivos)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 O que é

**TheNerdMN** é um sistema automatizado que:

1. **Lê feeds RSS** de múltiplas fontes (ScreenRant movies, news, TV)
2. **Extrai conteúdo completo** de cada artigo (HTML, imagens, vídeos)
3. **Reescreve com IA** (Gemini 2.5 Flash Lite) aplicando:
   - Otimização SEO
   - Ajuste de tom e estilo
   - Remoção de CTAs (Call-to-Actions)
   - Análise de qualidade
4. **Publica no WordPress** automaticamente com:
   - Upload de imagens
   - Categorias e tags
   - Meta-descrições
   - Validações finais

**Resultado**: Novos artigos publicados **a cada 15 minutos** (9h-19h, horário Brasil) sem intervenção manual.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTRADA (RSS)                             │
│  screenrant_movie_lists | screenrant_movie_news | screenrant_tv
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 EXTRATOR (extractor.py)                      │
│  - Baixa HTML completo                                       │
│  - Remove widgets/anúncios                                   │
│  - Extrai imagens e vídeos                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          FILA DE PROCESSAMENTO (BATCH SIZE 1)               │
│  - Aguarda 2 artigos (ou timeout)                            │
│  - Processa quando tem artigos disponíveis                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            IA PROCESSOR (ai_processor.py)                    │
│  - Envia para Gemini (2 chaves API com failover)            │
│  - Reescreve conteúdo (prompt customizável)                 │
│  - Gera título otimizado para SEO                           │
│  - Extrai categorias e tags                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           VALIDAÇÃO E SANITIZAÇÃO                            │
│  - Remove CTAs (5 camadas de detecção)                       │
│  - Valida meta-description                                   │
│  - Verifica score SEO                                        │
│  - Upload de imagens                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         PUBLICAÇÃO (wordpress.py)                            │
│  - POST /wp-json/wp/v2/posts                                │
│  - Cria categorias/tags se necessário                        │
│  - Define imagem destacada                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
            📰 ARTIGO PUBLICADO NO WORDPRESS
```

---

## ✨ Funcionalidades

### Core
- ✅ **Agendador APScheduler**: Executa a cada 15 minutos (9h-19h Brasil)
- ✅ **Batch Processing**: Processa artigos em lotes otimizados
- ✅ **Failover de API**: 2 chaves Gemini com fallback automático
- ✅ **Deduplicação**: Não publica artigos já processados
- ✅ **Retry com Backoff**: 3 tentativas com espera exponencial

### Processamento de Conteúdo
- ✅ **Extração Inteligente**: Remove anúncios, widgets, captions em inglês
- ✅ **Otimização SEO**: Títulos, meta-descriptions, slugs otimizados
- ✅ **Remoção de CTA**: 5 camadas de detecção de "Call-to-Actions"
- ✅ **Análise de Qualidade**: Score SEO (0-100) antes de publicar
- ✅ **Geração de Tags**: Extrai automaticamente do conteúdo

### WordPress
- ✅ **Upload de Imagens**: Download e upload automático
- ✅ **Categorias Dinâmicas**: Cria automaticamente se não existir
- ✅ **Meta Dados**: Description, keywords, Open Graph
- ✅ **Sanitização**: Remove código malicioso antes de publicar

### Monitoring
- ✅ **Logs Detalhados**: Arquivo `logs/app.log` com toda a execução
- ✅ **Database SQLite**: Rastreia artigos, posts, falhas
- ✅ **Debug Automático**: Salva respostas de erro para análise

---

## ⚙️ Configuração

### Pré-requisitos
- Python 3.10+
- WordPress com REST API ativada
- 2 chaves Gemini API (free ou paid)
- Usuário WordPress com permissão de publicar

### Instalação

```bash
# Clone o repositório
git clone https://github.com/TheFinance/TheNerdMN.git
cd TheNerdMN

# Crie e ative ambiente virtual
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt
```

### Arquivo .env (Variáveis de Ambiente)

Crie um arquivo `.env` na raiz do projeto:

```env
# =============================================
# GEMINI API (Google AI)
# =============================================
# Você pode ter múltiplas chaves para failover
GEMINI_1=sua_primeira_chave_gemini_aqui
GEMINI_2=sua_segunda_chave_gemini_aqui

# Modelo de IA
AI_MODEL=gemini-2.5-flash-lite

# =============================================
# WORDPRESS
# =============================================
WORDPRESS_URL=https://seu-site.com
WORDPRESS_USER=seu_usuario_wp
WORDPRESS_PASSWORD=sua_senha_wp_ou_token

# =============================================
# RSS FEEDS (configuradas em config.py)
# Padrão:
# - screenrant_movie_lists
# - screenrant_movie_news
# - screenrant_tv
# =============================================

# =============================================
# AGENDAMENTO
# =============================================
CHECK_INTERVAL_MINUTES=15  # A cada 15 minutos
MAX_ARTICLES_PER_FEED=3    # Máximo 3 por feed
PER_ARTICLE_DELAY_SECONDS=8
PER_FEED_DELAY_SECONDS=15

# =============================================
# IMAGENS
# =============================================
IMAGES_MODE=hotlink  # 'hotlink' ou 'download_upload'
PUBLISHER_LOGO_URL=https://seu-site.com/logo.png

# =============================================
# LIMPEZA
# =============================================
CLEANUP_AFTER_HOURS=72  # Limpa dados com 72h+
```

---

## 🔗 Feeds RSS

### Feeds Configurados

O pipeline atualmente lê de **3 feeds ScreenRant**:

| Feed | URL | Categoria | Max Artigos |
|------|-----|-----------|-------------|
| **Movie Lists** | `https://screenrant.com/feed/movie-lists/` | Filmes | 3 |
| **Movie News** | `https://screenrant.com/feed/movie-news/` | Filmes | 3 |
| **TV** | `https://screenrant.com/feed/tv/` | Séries | 3 |

**Total por ciclo**: Até 9 artigos novos a cada 15 minutos.

### Como Adicionar Novo Feed

Edite `app/config.py`:

```python
RSS_FEEDS: Dict[str, Dict[str, Any]] = {
    'seu_feed_id': {
        'urls': ['https://exemplo.com/feed/'],
        'category': 'sua_categoria',
        'source_name': 'Nome da Fonte',
    },
}

PIPELINE_ORDER = [
    'seu_feed_id',  # Adicione aqui
    # ... outros feeds
]

SOURCE_CATEGORY_MAP = {
    'seu_feed_id': ['Sua Categoria'],
}
```

---

## 🔑 Chaves de API

### Google Gemini

Você precisa de **2 chaves Gemini API** para failover:

1. **Acesse** [ai.google.dev/](https://ai.google.dev/)
2. **Crie 2 projetos** (melhor ter 2 para quota independente)
3. **Gere chaves API** em cada projeto
4. **Cole no `.env`**:
   ```env
   GEMINI_1=sk-xxx...
   GEMINI_2=sk-yyy...
   ```

**Quota Gratuita**: 
- 20 requisições/dia por projeto = 40 total
- 1 milhão tokens/mês

**Com 2 chaves**: Até **40 artigos/dia** processados.

### WordPress REST API

Seu usuário WordPress precisa:
1. ✅ Permissão de "Editar Posts"
2. ✅ REST API ativada
3. ✅ Senha de aplicação gerada (não senha real)

Gere token em: `Configurações > Segurança > Senhas de Aplicação`

---

## 🌍 Variáveis de Ambiente Completas

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `GEMINI_1` | *obrigatório* | Primeira chave API Gemini |
| `GEMINI_2` | *obrigatório* | Segunda chave API Gemini |
| `WORDPRESS_URL` | *obrigatório* | URL completa do WordPress |
| `WORDPRESS_USER` | *obrigatório* | Usuário do WordPress |
| `WORDPRESS_PASSWORD` | *obrigatório* | Senha de aplicação WP |
| `AI_MODEL` | `gemini-2.5-flash-lite` | Modelo de IA |
| `CHECK_INTERVAL_MINUTES` | `15` | Intervalo de execução |
| `MAX_ARTICLES_PER_FEED` | `3` | Máx artigos por feed |
| `IMAGES_MODE` | `hotlink` | Como tratar imagens |
| `PUBLISHER_LOGO_URL` | `https://...` | Logo do publicador |
| `CLEANUP_AFTER_HOURS` | `72` | Limpeza de dados antigos |

---

## 🎬 Como Executar

### Execução Normal (Scheduler 9h-19h)

```bash
python main.py
```

Saída esperada:
```
Ativando o ambiente virtual...
Iniciando o programa...
...
Agendador iniciado. O pipeline será executado a cada 15 minutos entre 9h-19h (horário de Brasília).
Pressione Ctrl+C para sair.
```

**O sistema agora:**
- Roda continuamente entre 9h-19h Brasil
- Executa ciclo completo a cada 15 minutos
- Publica artigos assim que estiverem prontos
- Para automaticamente após 19h

### Execução Única (Teste)

```bash
python main.py --once
```

Executa um ciclo completo e sai. Útil para testes.

### Parar o Pipeline

```
Ctrl+C
```

---

## 📊 Fluxo de Processamento Completo

### 1️⃣ Leitura de Feeds (30 segundos)
```
├─ Lê screenrant_movie_lists
├─ Lê screenrant_movie_news
└─ Lê screenrant_tv
→ Enfileira até 9 artigos novos
```

### 2️⃣ Extração de Conteúdo (1-2 seg por artigo)
```
├─ Baixa HTML completo
├─ Remove widgets e anúncios
├─ Extrai imagens
├─ Extrai vídeos YouTube
└─ Limpa captions em inglês
```

### 3️⃣ Processamento em Batch (25 seg por batch)
```
├─ Aguarda 2 artigos na fila
├─ Envia para Gemini (1 requisição = 2 artigos)
├─ Reescreve conteúdo
├─ Gera título otimizado
└─ Extrai categorias/tags
```

### 4️⃣ Validações (2-3 seg por artigo)
```
├─ Verifica CTA (5 camadas)
├─ Valida meta-description
├─ Calcula score SEO
└─ Upload de imagens
```

### 5️⃣ Publicação WordPress (3-5 seg por artigo)
```
├─ Cria categorias se necessário
├─ Cria tags se necessário
├─ Publica POST
└─ Define imagem destacada
```

**Tempo total por ciclo**: ~2-3 minutos para 9 artigos

---

## 📁 Estrutura de Arquivos

```
TheNews_TheFinance/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 🔴 Ponto de entrada
│   ├── config.py               # ⚙️ Todas as configurações
│   ├── pipeline.py             # 🔄 Orquestração principal
│   ├── feeds.py                # 📡 Leitura de RSS
│   ├── extractor.py            # 🔗 Extração de HTML
│   ├── ai_processor.py         # 🤖 Integração Gemini
│   ├── ai_client_gemini.py     # 📞 Cliente Gemini
│   ├── wordpress.py            # 📰 API WordPress
│   ├── store.py                # 💾 Database SQLite
│   ├── cleaners.py             # 🧹 Limpeza de conteúdo
│   ├── rewriter.py             # ✏️ Sanitização
│   ├── categorizer.py          # 📂 Mapeo de categorias
│   ├── media.py                # 🖼️ Gerenciamento de imagens
│   ├── tags.py                 # 🏷️ Extração de tags
│   ├── exceptions.py           # ⚠️ Exceções customizadas
│   └── logging_conf.py         # 📝 Configuração de logs
│
├── data/
│   ├── articles.db             # SQLite database
│   └── internal_links.json     # Cache de links
│
├── debug/
│   └── failed_ai_*.json.txt    # Respostas falhadas da IA
│
├── logs/
│   ├── app.log                 # Log completo
│   └── error.log               # Apenas erros
│
├── templates/
│   └── seo_templates.json      # Templates SEO
│
├── universal_prompt.txt        # 🎯 Prompt principal da IA
├── .env                        # 🔑 Variáveis de ambiente
├── .env.example                # Exemplo de .env
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
└── README_COMPLETE.md          # Documentação completa
```

---

## 📝 Prompt da IA (universal_prompt.txt)

O arquivo `universal_prompt.txt` contém o prompt **exato** enviado para Gemini:

- ✅ Instruções de reescrita
- ✅ Otimização SEO
- ✅ Remoção de CTAs
- ✅ Geração de tags
- ✅ Validações de qualidade

**Customize conforme necessário** para mudar o estilo/tom do conteúdo.

---

## 🗄️ Database SQLite

O arquivo `data/articles.db` rastreia:

### Tabela: `articles`
```sql
- id (PK)
- source_id (feed origin)
- external_id (unique per feed)
- title
- url
- status (NEW, PROCESSING, PROCESSED, PUBLISHED, FAILED, QUEUED)
- content_extract
- published_at
- created_at
```

### Tabela: `published_posts`
```sql
- id (PK)
- article_id (FK)
- wordpress_post_id
- published_url
- created_at
```

---

## 🐛 Troubleshooting

### Problema: "JSON decoding failed"

**Causa**: Resposta Gemini truncada (conteúdo muito grande)

**Solução**: Reduzir `MAX_ARTICLES_PER_FEED` em `.env`:
```env
MAX_ARTICLES_PER_FEED=2  # Ao invés de 3
```

### Problema: "Quota exceeded"

**Causa**: Usou as 20 requisições/dia por chave

**Solução**: Aumentar número de chaves ou reduzir frequência:
```env
CHECK_INTERVAL_MINUTES=30  # Ao invés de 15
```

### Problema: "WordPress 403 Forbidden"

**Causa**: Credenciais erradas ou permissões insuficientes

**Solução**: Verificar:
1. URL do WordPress está correto
2. Usuário tem permissão de "Editar Posts"
3. Usar "Senha de Aplicação" (não senha real)

### Problema: Artigos não são publicados

**Verifique:**
1. Pipeline está rodando: `python main.py`
2. Horário está entre 9h-19h (Brasil)
3. Logs em `logs/app.log` para erros
4. Database em `data/articles.db` para status

---

## 📊 Monitoramento

### Verificar Status

```bash
# Ver últimas linhas do log
tail -f logs/app.log

# Ver apenas erros
grep "ERROR\|CRITICAL" logs/app.log

# Ver batches processados
grep "Sending batch\|Successfully processed" logs/app.log
```

### Verificar Database

```bash
# Instale sqlite3 CLI
sqlite3 data/articles.db

# Contar artigos por status
SELECT status, COUNT(*) FROM articles GROUP BY status;

# Ver últimos 5 artigos
SELECT * FROM articles ORDER BY created_at DESC LIMIT 5;
```

---

## 🚀 Performance

### Métricas Esperadas

| Métrica | Esperado |
|---------|----------|
| **Artigos/dia** | 40-60 |
| **Requisições Gemini/dia** | 20-40 |
| **Taxa de sucesso** | >95% |
| **Tempo por ciclo** | 2-3 minutos |
| **Score SEO médio** | 85-95 |

### Otimizações

1. **Aumentar Chaves Gemini**: Permite mais artigos/dia
2. **Reduzir Intervalo**: Altere `CHECK_INTERVAL_MINUTES` (default 15)
3. **Adicionar Feeds**: Mais feeds = mais artigos por ciclo
4. **Aumentar Artigos/Feed**: Altere `MAX_ARTICLES_PER_FEED` (default 3)

---

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs**: `tail -f logs/app.log`
2. **Veja arquivos de debug**: `debug/failed_ai_*.json.txt`
3. **Verifique database**: `sqlite3 data/articles.db`
4. **Teste com `--once`**: `python main.py --once`

---

## 📄 Licença

Este projeto é privado e propriedade de TheFinance.

---

**Versão**: 2.0 (Janeiro 2026)  
**Última atualização**: 6 de janeiro de 2026  
**Status**: ✅ Produção
