"""
scripts/test_feeds.py
─────────────────────────────────────────────────────────────────────────────
Testa todos os feeds RSS do pipeline TheFinance.

O que verifica por feed:
  1. HTTP reachability  → status code + redirect chain
  2. Content-Type       → deve ser XML / RSS / Atom
  3. RSS/Atom parsing   → feedparser consegue ler + conta itens
  4. Circuit breaker    → lê consecutive_failures no banco (se existir)

Uso:
  cd <raiz do projeto>
  .venv\\Scripts\\activate
  python scripts/test_feeds.py

Saída:
  tabela no terminal + arquivo reports/feed_health_<timestamp>.txt
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import io
import time
import sqlite3
import datetime

# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError when piping)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── adiciona a raiz ao path para importar app.config ──────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import feedparser
except ImportError:
    sys.exit("feedparser não instalado. Rode: pip install feedparser")

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    sys.exit("requests não instalado. Rode: pip install requests")

from app.config import RSS_FEEDS, PIPELINE_ORDER

# ── Constantes ─────────────────────────────────────────────────────────────
TIMEOUT        = 10          # segundos por requisição (connect + read)
DELAY_BETWEEN  = 0.3         # segundos entre cada feed (evitar rate-limit)
DB_PATH        = os.path.join(ROOT, 'data', 'app.db')
REPORT_DIR     = os.path.join(ROOT, 'reports')
VALID_TYPES    = ('xml', 'rss', 'atom', 'feed', 'text/plain')   # substrings aceitas

# Cabeçalhos realistas para evitar bloqueios de Bot-User-Agent
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*',
}

# Sessão HTTP — sem retry em timeout (evita quadruplicar o tempo de espera)
session = requests.Session()
retry = Retry(
    total=1,
    backoff_factor=0,
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False,
)
session.mount('https://', HTTPAdapter(max_retries=retry))
session.mount('http://',  HTTPAdapter(max_retries=retry))

# ── Helpers ────────────────────────────────────────────────────────────────

def get_circuit_breaker_state(source_id: str) -> str:
    """Lê consecutive_failures do SQLite; retorna estado legível."""
    if not os.path.exists(DB_PATH):
        return '⬜ DB não inicializado'
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        # Verifica se a tabela existe antes de consultar
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='feed_circuit_breaker'"
        )
        if cur.fetchone() is None:
            con.close()
            return '⬜ pipeline não executado'
        cur.execute(
            "SELECT consecutive_failures FROM feed_circuit_breaker WHERE source_id = ?",
            (source_id,)
        )
        row = cur.fetchone()
        con.close()
        if row is None:
            return '✅ 0 falhas'
        n = row[0]
        if n == 0:
            return '✅ 0 falhas'
        if n >= 3:
            return f'🔴 ABERTO ({n} falhas)'
        return f'⚠️  {n} falha(s)'
    except Exception as e:
        return f'DB erro: {e}'


def test_feed(source_id: str, config: dict) -> dict:
    url = config['urls'][0]
    result = {
        'source_id':    source_id,
        'source_name':  config.get('source_name', ''),
        'url':          url,
        'http_status':  None,
        'content_type': None,
        'redirect':     None,
        'items':        None,
        'parse_ok':     False,
        'type_ok':      False,
        'circuit':      get_circuit_breaker_state(source_id),
        'error':        None,
        'final_url':    None,
    }

    # ── 1. HTTP HEAD (rápido) → fallback GET ─────────────────────────────
    try:
        resp = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        result['http_status'] = resp.status_code
        result['final_url']   = resp.url if resp.url != url else None
        result['redirect']    = len(resp.history) > 0

        ct = resp.headers.get('Content-Type', '').lower()
        result['content_type'] = ct
        result['type_ok'] = any(t in ct for t in VALID_TYPES)

        # ── 2. feedparser ──────────────────────────────────────────────
        if resp.status_code == 200:
            parsed = feedparser.parse(resp.content)
            bozo   = parsed.get('bozo', True)
            entries = parsed.get('entries', [])
            result['items']    = len(entries)
            result['parse_ok'] = not bozo or len(entries) > 0
        else:
            result['error'] = f'HTTP {resp.status_code}'

    except requests.exceptions.SSLError as e:
        result['error'] = f'SSL erro'
    except requests.exceptions.ConnectionError as e:
        result['error'] = f'Conn erro'
    except requests.exceptions.Timeout:
        result['error'] = f'Timeout >{TIMEOUT}s'
    except KeyboardInterrupt:
        raise
    except Exception as e:
        result['error'] = str(e)[:60]

    return result


def status_icon(r: dict) -> str:
    if r['error']:
        return '❌'
    if r['http_status'] == 200 and r['parse_ok']:
        return '✅'
    if r['http_status'] == 200:
        return '⚠️ '
    return '❌'


def format_row(r: dict, idx: int) -> str:
    icon  = status_icon(r)
    http  = str(r['http_status']) if r['http_status'] else '---'
    items = str(r['items'])       if r['items'] is not None else '---'
    redir = '→ redir' if r['redirect'] else ''
    err   = f" [{r['error']}]" if r['error'] else ''
    cb    = r['circuit']

    return (
        f"  {idx:02d}. {icon}  {r['source_id']:<25}"
        f"  HTTP {http:<4}  items={items:<4}  {redir:<8}"
        f"  CB: {cb}{err}"
    )


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(REPORT_DIR, f'feed_health_{timestamp}.txt')

    lines = []

    header = (
        f"\n{'═'*72}\n"
        f"  TheFinance — Feed Health Check\n"
        f"  {datetime.datetime.now().strftime('%B %d, %Y  %H:%M:%S')}\n"
        f"  {len(RSS_FEEDS)} feeds testados\n"
        f"{'═'*72}\n"
    )
    print(header)
    lines.append(header)

    results   = []
    ok_count  = 0
    err_count = 0

    total = len(PIPELINE_ORDER)
    # Feeds no PIPELINE_ORDER primeiro, depois eventuais extras
    ordered_ids = list(PIPELINE_ORDER) + [k for k in RSS_FEEDS if k not in PIPELINE_ORDER]

    for idx, source_id in enumerate(ordered_ids, 1):
        config = RSS_FEEDS.get(source_id)
        if not config:
            line = f"  {idx:02d}. ⚠️   {source_id:<25}  [não está em RSS_FEEDS]"
            print(line)
            lines.append(line)
            continue

        print(f"  [{idx:02d}/{total}] testando {source_id}...", end='\r')
        r = test_feed(source_id, config)
        results.append(r)

        row = format_row(r, idx)
        print(row + ' ' * 20)   # limpa o \r
        lines.append(row)

        if status_icon(r) == '✅':
            ok_count += 1
        else:
            err_count += 1

        time.sleep(DELAY_BETWEEN)

    # ── Sumário ────────────────────────────────────────────────────────────
    summary_lines = [
        f"\n{'─'*72}",
        f"  RESUMO: {ok_count} OK  |  {err_count} com problemas  |  {len(ordered_ids)} total",
        f"{'─'*72}",
    ]

    if err_count > 0:
        summary_lines.append("\n  FEEDS COM PROBLEMA:")
        for r in results:
            if status_icon(r) != '✅':
                summary_lines.append(
                    f"    • {r['source_id']:<25}  {r['url']}"
                )
                summary_lines.append(
                    f"    {'':27}HTTP {r['http_status']}  {r['error'] or ''}"
                )

    # ── Circuit Breaker summary ────────────────────────────────────────────
    cb_open = [r for r in results if '🔴' in r['circuit']]
    if cb_open:
        summary_lines.append("\n  ⚡ CIRCUIT BREAKERS ABERTOS (≥3 falhas no DB):")
        for r in cb_open:
            summary_lines.append(f"    • {r['source_id']:<25}  {r['circuit']}")
    else:
        summary_lines.append("\n  ⚡ Circuit Breakers: todos fechados (sem falhas acumuladas).")

    summary_lines.append(f"\n  Relatório salvo em: {report_path}\n")

    for line in summary_lines:
        print(line)
        lines.append(line)

    # ── Grava relatório ────────────────────────────────────────────────────
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # ── Detalhe completo de cada feed no relatório ─────────────────────────
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write(f"\n\n{'═'*72}\n  DETALHES\n{'═'*72}\n")
        for r in results:
            f.write(f"\n[{r['source_id']}]\n")
            f.write(f"  URL          : {r['url']}\n")
            f.write(f"  Final URL    : {r['final_url'] or '(sem redirect)'}\n")
            f.write(f"  HTTP Status  : {r['http_status']}\n")
            f.write(f"  Content-Type : {r['content_type']}\n")
            f.write(f"  Items parsed : {r['items']}\n")
            f.write(f"  Parse OK     : {r['parse_ok']}\n")
            f.write(f"  Content-Type OK: {r['type_ok']}\n")
            f.write(f"  Circuit Breaker: {r['circuit']}\n")
            if r['error']:
                f.write(f"  Error        : {r['error']}\n")


if __name__ == '__main__':
    main()
