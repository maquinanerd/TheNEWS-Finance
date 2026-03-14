# Troubleshooting & FAQ

## ❓ Perguntas Frequentes

### P1: O título está muito curto depois da otimização

**Situação**: `"Marvel"` - muito curto (6 caracteres)

**Solução**:
```python
# Aumentar tamanho mínimo
title, report = optimize_title(
    original_title,
    content,
    min_length=40,      # Reduz de 50
    target_length=65    # Mantém target
)
```

---

### P2: As imagens ainda aparecem quebradas

**Verificação rápida**:
```python
from app.html_utils import unescape_html_content, validate_and_fix_figures

# 1. Verificar se está desescapado
html = unescape_html_content(html_bruto)
print(html[:500])  # Ver primeiros 500 chars

# 2. Verificar se está validado
html_corrigido = validate_and_fix_figures(html)
print(html_corrigido[:500])
```

**Causas comuns**:
- ❌ HTML não foi desescapado antes de validar
- ❌ URL extraída está vazia (regex não funcionou)
- ❌ Falta `<figure>` envoltório

---

### P3: O verbo de ação não está sendo detectado

**Situação**: Título contém verbo mas score diz que não

**Verificação**:
```python
from app.seo_title_optimizer import analyze_title_quality

title = "Seu título aqui"
score, issues = analyze_title_quality(title)

print(f"Score: {score}")
for issue in issues:
    print(f"  - {issue}")
```

**Solução**:
- Adicionar o verbo à lista `ACTION_VERBS` em `app/seo_title_optimizer.py`
- Verbos devem estar em **minúsculas** na lista
- Verbo no título será convertido para minúsculas para comparação

---

### P4: Muita qualidade está sendo removida

**Situação**: Título `"Elon Musk anuncia mudança radical em X"` vira `"Musk muda X"` (muito curto)

**Raiz**: Função de truncamento sendo agressiva

**Solução**:
```python
# Aumentar tolerância
title, report = optimize_title(
    original_title,
    content,
    min_length=40,
    max_length=100,     # Permitir mais caracteres
    target_length=80
)
```

---

### P5: Score de título sempre baixo

**Verificação**:
```python
from app.seo_title_optimizer import analyze_title_quality

# Testar vários títulos
titulos_teste = [
    "Marvel anuncia novo filme",
    "Você não vai acreditar",
    "Novo filme da Marvel chega em 2025"
]

for t in titulos_teste:
    score, issues = analyze_title_quality(t)
    print(f"{t}: {score}/100")
    for i in issues:
        print(f"  - {i}")
```

**Pontos de melhoria**:
- ✅ Adicionar número/data (+5 pts)
- ✅ Adicionar verbo de ação (+15 pts)
- ✅ Remover palavras vagas (+10 pts)
- ✅ Manter entre 50-70 chars (+20 pts)

---

## 🐛 Bugs Conhecidos

### Bug #1: Caracteres especiais em alt text

**Situação**: `alt="imagem &lt; com"` no resultado

**Status**: ✅ FIXADO  
**Localização**: `app/html_utils.py` linha ~245  
**Solução**: Função `_sanitize_alt_text()` remove caracteres problemáticos

---

### Bug #2: Figcaption repetida

**Situação**: `<figcaption>descrição</figcaption><figcaption>descrição</figcaption>`

**Status**: ✅ FIXADO  
**Localização**: `app/html_utils.py` função `validate_and_fix_figures()` linha ~350

---

### Bug #3: URLs com quebra de linha em src

**Situação**: HTML com quebra: `src="https://example.com\nimage.jpg"`

**Status**: ⚠️ PARCIALMENTE FIXADO  
**Workaround**: 
```python
content = content.replace('\n', '').replace('\r', '')
content = validate_and_fix_figures(content)
```

---

## 🔧 Customização

### Adicionar Novo Verbo de Ação

**Arquivo**: `app/seo_title_optimizer.py`

**Local**: Procurar por `ACTION_VERBS = {`

**Fazer**:
```python
ACTION_VERBS = {
    "anuncia", "lança", "vence", "fecha",
    # ADICIONE AQUI:
    "suspende", "atrasa", "cancela"  # novos verbos
}
```

---

### Remover Padrão de Clickbait

**Arquivo**: `app/seo_title_optimizer.py`

**Local**: Procurar por `CLICKBAIT_PATTERNS = [`

**Fazer**:
```python
CLICKBAIT_PATTERNS = [
    r"você (não )?vai acreditar",
    r"é incrível",
    # REMOVER A LINHA QUE NÃO QUER:
    # r"celebridade (famosa|renomada|conhecida)",
]
```

---

### Ajustar Limites de Caracteres

**Arquivo**: `app/pipeline.py`

**Local**: Procurar por `optimize_title(`

**Fazer**:
```python
title, title_report = optimize_title(
    title, 
    content_html,
    min_length=45,      # ALTERAR AQUI
    max_length=80,      # ALTERAR AQUI
    target_length=70    # ALTERAR AQUI
)
```

---

## 📊 Monitoramento

### Ver Histórico de Otimizações

```python
# Em app/pipeline.py, os logs mostram:
# "Título otimizado: 67.0 → 95.0"

# Verificar logs:
tail -f logs/app.log | grep "Título otimizado"
```

### Dashboard de Qualidade

```python
# Criar script para análise
from app.seo_title_optimizer import analyze_title_quality
import app.store as store

# Buscar todos os artigos
articles = store.get_all_articles()

scores = []
for article in articles:
    score, _ = analyze_title_quality(article['title'])
    scores.append(score)

print(f"Score médio: {sum(scores)/len(scores):.1f}")
print(f"Mínimo: {min(scores)}")
print(f"Máximo: {max(scores)}")
```

---

## 🚨 Erros Comuns

### Erro: "ModuleNotFoundError: No module named 'bs4'"

**Solução**:
```bash
pip install beautifulsoup4
```

---

### Erro: "AttributeError: 'NoneType' object has no attribute 'text'"

**Causa**: HTML vazio ou malformado antes de BeautifulSoup

**Solução**:
```python
# Verificar antes de processar
if not html or not html.strip():
    return html  # Retornar vazio se entrada vazia
    
content_html = validate_and_fix_figures(content_html)
```

---

### Erro: "TypeError: 'dict' object is not subscriptable"

**Causa**: `optimize_title()` retorna tupla, não dict

**Solução**:
```python
# ❌ ERRADO:
title_report = optimize_title(title, content)
print(title_report['original_score'])

# ✅ CORRETO:
title, title_report = optimize_title(title, content)
print(title_report['original_score'])
```

---

## 🧪 Testes Rápidos

### Test #1: SEO Title Optimizer

```bash
cd e:\Área de Trabalho 2\Portal The News\Nerd\TheNews_TheFinance
python app/seo_title_optimizer.py
```

**Resultado esperado**: Múltiplos exemplos com scores 85-100

---

### Test #2: Image Fixer

```bash
python tests/test_image_fix.py
```

**Resultado esperado**: 4 testes passando

---

### Test #3: Integração Completa

```bash
python tests/test_integrated_seo_images.py
```

**Resultado esperado**: 8/8 validações passando

---

## 🔍 Debug Passo-a-Passo

### Debugar Título Específico

```python
from app.seo_title_optimizer import optimize_title, analyze_title_quality

# Seu título
original = "Você não vai acreditar no que Marvel descobriu"
content = "<p>Marvel descobriu um novo caminho...</p>"

# Análise do original
print("=== ANTES ===")
score_before, issues_before = analyze_title_quality(original)
print(f"Score: {score_before}/100")
print(f"Problemas: {issues_before}")

# Otimizar
optimized, report = optimize_title(original, content)

# Análise do otimizado
print("\n=== DEPOIS ===")
score_after, issues_after = analyze_title_quality(optimized)
print(f"Score: {score_after}/100")
print(f"Problemas: {issues_after}")
print(f"Título otimizado: '{optimized}'")
print(f"Tamanho: {len(optimized)} caracteres")
```

---

### Debugar Imagem Específica

```python
from app.html_utils import validate_and_fix_figures, unescape_html_content

# Seu HTML com imagem quebrada
html = '<img src="&lt;figure&gt;&lt;img src=&quot;https://example.com/image.jpg&quot;&gt;&lt;/figure&gt;">'

# Passo 1: Desescapar
print("=== HTML BRUTO ===")
print(html)

html_unescaped = unescape_html_content(html)
print("\n=== APÓS UNESCAPE ===")
print(html_unescaped)

# Passo 2: Validar e corrigir
html_fixed = validate_and_fix_figures(html_unescaped)
print("\n=== APÓS FIX ===")
print(html_fixed)

# Verificar se ficou bom
if '<figure>' in html_fixed and '<figcaption>' in html_fixed:
    print("\n✅ Estrutura corrigida!")
else:
    print("\n❌ Estrutura ainda tem problemas")
```

---

## 📈 Otimizações Futuras

### Performance: Cache de Scores

```python
# IDEIA: Cachear títulos já analisados
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_title_quality_cached(title):
    return analyze_title_quality(title)
```

### Segurança: Validação de URL

```python
# IDEIA: Validar URLs antes de adicionar
from urllib.parse import urlparse

def is_valid_image_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
```

### Qualidade: Multi-idioma

```python
# IDEIA: Suporte para outros idiomas
ACTION_VERBS_PT = {"anuncia", "lança", ...}
ACTION_VERBS_EN = {"announces", "launches", ...}
ACTION_VERBS_ES = {"anuncia", "lanza", ...}
```

---

**Última atualização**: 29 de Outubro de 2025  
**Versão**: 1.0  
**Status**: ✅ Estável
