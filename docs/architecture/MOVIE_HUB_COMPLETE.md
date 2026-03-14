# 🎬 Movie Hub - Sistema Completo de Filmes & Séries

**Criado em:** 3 de fevereiro de 2026

---

## 📋 Visão Geral

O **Movie Hub** é um sistema completo e integrado para gerenciar, sincronizar e exibir informações sobre filmes e séries. Ele funciona **em paralelo** com as notícias RSS, criando um banco de dados rico com dados da **The Movie Database (TMDb)**.

### 🎯 Funcionalidades

✅ **Sincronização TMDb**
- Filmes em tendência
- Séries em tendência
- Próximos lançamentos
- Todos os gêneros

✅ **Banco de Dados Completo**
- Filmes e séries
- Atores/atrizes
- Gêneros
- Avaliações
- Provedores de streaming ("Onde Assistir")

✅ **Páginas Individuais**
- Design responsivo
- Informações detalhadas
- Elenco com fotos
- Watch providers integrados
- SEO otimizado

✅ **Listagens Dinâmicas**
- Filmes em tendência
- Séries em tendência
- Por gênero
- Busca full-text

---

## 📁 Arquivos Criados

### 1. **`app/tmdb_extended.py`** (485 linhas)
Cliente TMDb expandido com recursos avançados:
- Busca de filmes/séries
- Detalhes completos
- **Watch Providers** (onde assistir)
- Tendências
- Próximos lançamentos
- Gêneros

**Principais métodos:**
```python
client = TMDbExtendedClient(api_key)

# Busca
movies = client.search_movie("Inception")

# Detalhes com tudo
details = client.get_movie_details(movie_id)

# Onde assistir
providers = client.get_movie_watch_providers(movie_id)

# Formato para BD
formatted = client.format_movie_data(details)
```

### 2. **`app/models.py`** (450 linhas)
Modelos ORM para SQLAlchemy:
- `Movie` - Filmes completos
- `TvSeries` - Séries completas
- `Genre` - Gêneros
- `Actor` - Atores/atrizes
- `WatchProvider` - Provedores streaming
- `MovieReview` / `TvReview` - Avaliações
- `List` - Listas personalizadas

Relacionamentos M2M:
- Filmes ↔ Gêneros
- Séries ↔ Gêneros
- Atores ↔ Filmes
- Atores ↔ Séries

**Usa SQLite:**
```
movie_hub.db
├── movies (filmes)
├── tv_series (séries)
├── genres (gêneros)
├── actors (atores)
├── watch_providers (Netflix, Prime, etc)
└── reviews (avaliações)
```

### 3. **`app/movie_repository.py`** (480 linhas)
CRUD completo para dados:
- `MovieRepository` - Operações com filmes
- `TvRepository` - Operações com séries
- `GenreRepository` - Operações com gêneros

**Exemplo:**
```python
repo = MovieRepository()

# Adicionar
movie = repo.add_movie(formatted_data)

# Buscar
movie = repo.get_movie_by_slug('inception')

# Trending
trending = repo.get_trending_movies(limit=10)

# Buscar
results = repo.search_movies("Batman")
```

### 4. **`app/page_generator.py`** (550 linhas)
Gerador de páginas HTML responsivas:
- `MoviePageGenerator` - Páginas de filmes
- `TvPageGenerator` - Páginas de séries

**Gera:**
```
┌─────────────────────────────────────┐
│    HEADER (Backdrop + Título)       │
├──────────┬──────────────────────────┤
│ POSTER   │  SINOPSE + ELENCO        │
│  + INFO  │  + DETALHES              │
│  + ONDE  │  + ONDE ASSISTIR         │
│ASSISTIR  │                          │
└──────────┴──────────────────────────┘
```

### 5. **`app/movie_hub_manager.py`** (550 linhas)
Orquestrador principal:
- Sincronização TMDb ↔ BD
- Geração de páginas
- Gerenciamento de listagens

**Fluxo:**
```
TMDb API
   ↓
format_movie_data()
   ↓
movie_repo.add_movie()
   ↓
page_generator.generate_movie_page()
   ↓
HTML Pronto para WordPress
```

---

## 🚀 Como Usar

### Passo 1: Configurar Variáveis de Ambiente

Adicione ao `.env`:

```env
# TMDb
TMDB_ENABLED=true
TMDB_API_KEY=sua_chave_aqui
TMDB_ACCESS_TOKEN=seu_token_aqui  # Opcional, mais seguro

# Movie Hub
MOVIE_HUB_ENABLED=true
MOVIE_HUB_DB_PATH=./movie_hub.db
MOVIE_HUB_SYNC_INTERVAL=3600  # Sincronizar a cada hora
```

### Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

Novas dependências:
- `sqlalchemy` - ORM para banco de dados
- `tmdbv3api` - Cliente TMDb (já tinha)

### Passo 3: Inicializar o Hub

```python
from app.movie_hub_manager import init_movie_hub

# Inicializa banco + manager
hub = init_movie_hub()

# Sincronizar com TMDb
hub.sync_trending_movies(limit=20)
hub.sync_trending_tv(limit=20)
hub.sync_upcoming_movies(limit=10)
hub.sync_all_genres()
```

### Passo 4: Buscar Filme/Série e Adicionar

```python
# Buscar e adicionar
movie_data = hub.search_and_add_movie("Oppenheimer", year=2023)
tv_data = hub.search_and_add_tv("Breaking Bad")
```

### Passo 5: Gerar Página

```python
# Gerar página HTML
html = hub.generate_movie_page(movie_id=1)

# Publicar no WordPress
wordpress.publish_post(
    title=movie_data['title'],
    content=html,
    type='movie'
)
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Sincronizar Tudo Automaticamente

```python
from app.movie_hub_manager import init_movie_hub

hub = init_movie_hub()

# Sincronizar trending
print("Sincronizando filmes em tendência...")
hub.sync_trending_movies(limit=15)
hub.sync_trending_tv(limit=15)

# Sincronizar próximos
print("Sincronizando próximos lançamentos...")
hub.sync_upcoming_movies(limit=10)

# Sincronizar gêneros
print("Sincronizando gêneros...")
hub.sync_all_genres()

print("✅ Sincronização completa!")
```

### Exemplo 2: Criar Post sobre Filme

```python
hub = init_movie_hub()

# Buscar e adicionar
movie_data = hub.search_and_add_movie("Dune: Part Two")

if movie_data:
    # Obter ID no banco
    movie = hub.movie_repo.get_movie_by_tmdb_id(movie_data['tmdb_id'])
    
    # Gerar página
    page_html = hub.generate_movie_page(movie.id)
    
    # Publicar no WordPress
    from app.wordpress import WordPressClient
    wp = WordPressClient(url, user, pass)
    
    post_id = wp.publish_post(
        title=f"🎬 {movie_data['title']}",
        content=page_html,
        excerpt=movie_data['overview'][:200],
        categories=['filmes', 'reviews'],
        tags=movie_data['genres'],
        featured_image_url=movie_data['poster_url'],
        type='post'
    )
    
    print(f"✅ Post publicado: {post_id}")
```

### Exemplo 3: Página de Trending

```python
hub = init_movie_hub()

# Sincronizar
hub.sync_trending_movies(limit=20)

# Gerar página de listagem
html = hub.get_trending_movies_page()

# Ou para séries
html_tv = hub.get_trending_tv_page()

# Publicar como página
wp.publish_page(
    title="Filmes em Tendência",
    content=html,
    slug="filmes-em-tendencia"
)
```

### Exemplo 4: Buscar por Gênero

```python
hub = init_movie_hub()

# Obter todos os gêneros
genres = hub.genre_repo.get_all_genres()

# Filmes de um gênero
action_genre = hub.genre_repo.get_genre_by_name("Action")
action_movies = hub.movie_repo.get_by_genre(action_genre.id, limit=20)

# Gerar cards
html = '<div class="movies-grid">'
for movie in action_movies:
    html += f'''
    <div class="movie-card">
        <img src="{movie.poster_url}" alt="{movie.title}">
        <h3>{movie.title}</h3>
        <p>⭐ {movie.rating}/10</p>
    </div>
    '''
html += '</div>'
```

---

## 📺 Estrutura de Dados

### Tabela: movies

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INT | ID primário |
| tmdb_id | INT | ID único da TMDb |
| title | VARCHAR | Título do filme |
| slug | VARCHAR | URL amigável |
| overview | TEXT | Sinopse |
| release_date | VARCHAR | Data de lançamento |
| rating | FLOAT | Nota (0-10) |
| vote_count | INT | Número de votos |
| runtime | INT | Duração em minutos |
| genres | M2M | Relacionamento com gêneros |
| actors | M2M | Relacionamento com atores |
| watch_providers | JSON | Netflix, Prime, etc |
| poster_url | TEXT | URL do pôster |
| backdrop_url | TEXT | URL do backdrop |
| is_trending | BOOL | Está em tendência? |
| is_featured | BOOL | Está em destaque? |

### Tabela: tv_series

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INT | ID primário |
| tmdb_id | INT | ID único da TMDb |
| title | VARCHAR | Título da série |
| slug | VARCHAR | URL amigável |
| overview | TEXT | Sinopse |
| first_air_date | VARCHAR | Primeira exibição |
| status | VARCHAR | Returning/Ended |
| total_seasons | INT | Número de temporadas |
| total_episodes | INT | Número de episódios |
| networks | JSON | Netflix, HBO, etc |
| creators | JSON | Criadores |
| is_trending | BOOL | Em tendência |
| is_ongoing | BOOL | Série ativa |

---

## 🔄 Integração com Pipeline de Notícias

O Movie Hub **NÃO interfere** com as notícias RSS:

```
┌─────────────────────────────────────┐
│        Pipeline Original             │
├─────────────────────────────────────┤
│ RSS → Extract → Rewrite (IA) → WP   │
│      (Notícias normais)              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        Movie Hub (Novo)              │
├─────────────────────────────────────┤
│ TMDb → Sync → BD → Pages → WP       │
│      (Filmes & Séries)               │
└─────────────────────────────────────┘
```

Os dois sistemas funcionam independentemente:
- **Notícias**: Saem automaticamente do feed RSS
- **Filmes/Séries**: Sincronizados manualmente ou por agendador

---

## ⚙️ Agendamento (Opcional)

Para sincronizar automaticamente, adicione ao `app/main.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.movie_hub_manager import init_movie_hub

# Inicializar hub
hub = init_movie_hub()

# Agendador
scheduler = BackgroundScheduler()

# A cada 6 horas, sincronizar trending
scheduler.add_job(
    lambda: hub.sync_trending_movies(20),
    'interval',
    hours=6,
    id='sync_trending_movies'
)

# A cada 24 horas, sincronizar próximos lançamentos
scheduler.add_job(
    lambda: hub.sync_upcoming_movies(10),
    'interval',
    hours=24,
    id='sync_upcoming_movies'
)

scheduler.start()
```

---

## 🎨 Customização de Página

As páginas geradas usam CSS inline, compatível com WordPress:

```python
# Você pode customizar as cores
MoviePageGenerator.THEME_COLOR = '#667eea'
TvPageGenerator.THEME_COLOR = '#4169E1'
```

Para usar CSS externo, edite `page_generator.py`.

---

## 🐛 Troubleshooting

### Problema: "Banco de dados vazio"
**Solução**: Execute `hub.sync_trending_movies()` para popular

### Problema: "Imagens não aparecem"
**Solução**: Verifique se `TMDB_API_KEY` é válido

### Problema: "Detalhes incompletos"
**Solução**: Alguns filmes podem ter dados limitados na TMDb

### Problema: "Rate limit atingido"
**Solução**: Adicione delay entre requisições (`time.sleep()`)

---

## 📚 API Referência Rápida

### MovieHubManager

```python
hub = init_movie_hub()

# Sincronização
hub.sync_trending_movies(limit=20)
hub.sync_trending_tv(limit=20)
hub.sync_upcoming_movies(limit=10)
hub.sync_all_genres()

# Busca e adição
movie = hub.search_and_add_movie("Título", year=2023)
tv = hub.search_and_add_tv("Série")

# Geração de páginas
html = hub.generate_movie_page(movie_id)
html = hub.generate_tv_page(tv_id)

# Listagens
html = hub.get_trending_movies_page()
html = hub.get_trending_tv_page()
```

### MovieRepository

```python
repo = MovieRepository()

repo.add_movie(data)
repo.get_movie(id)
repo.get_movie_by_slug(slug)
repo.get_movie_by_tmdb_id(tmdb_id)
repo.get_all_movies(limit, offset)
repo.get_trending_movies(limit)
repo.get_featured_movies(limit)
repo.get_by_genre(genre_id, limit)
repo.update_movie(id, data)
repo.delete_movie(id)
repo.search_movies(query, limit)
```

---

## ✅ Checklist de Implementação

- [x] Cliente TMDb expandido
- [x] Modelos ORM (SQLAlchemy)
- [x] Repositórios (CRUD)
- [x] Gerador de páginas (Filmes)
- [x] Gerador de páginas (Séries)
- [x] Hub Manager (orquestrador)
- [x] Documentação completa

---

## 🎯 Próximos Passos

1. **Obter chave TMDb**: https://www.themoviedb.org/settings/api
2. **Configurar `.env`**: Adicionar `TMDB_API_KEY`
3. **Instalar dependências**: `pip install -r requirements.txt`
4. **Inicializar BD**: `python -c "from app.movie_hub_manager import init_movie_hub; init_movie_hub()"`
5. **Sincronizar dados**: Execute os exemplos acima
6. **Integrar ao WordPress**: Publicar páginas geradas

---

**Sistema criado para TheFinance | Fevereiro 2026**

Dúvidas? Consulte os docstrings nos arquivos Python!
