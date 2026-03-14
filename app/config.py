import os
import logging
from dotenv import load_dotenv
from typing import Dict, List, Any

# Carrega variáveis de ambiente de um arquivo .env
load_dotenv(override=True)  # override=True garante que .env sobrescreve variaveis do sistema

logger = logging.getLogger(__name__)

# --- Ordem de processamento dos feeds ---
PIPELINE_ORDER: List[str] = [
    'cnbc_top', 'yahoo_finance',                                     # 1º: breaking news
    'cnbc_pf', 'marketwatch_pf', 'kiplinger', 'usnews_money',       # 2º: personal finance (maior RPM)
    'cnbc_investing', 'seeking_alpha', 'investopedia',               # 3º: investing
    'nasdaq_markets', 'nasdaq_earnings', 'marketwatch_top',          # 4º: markets
    'cnbc_economy', 'economist', 'politico_econ',                    # 5º: macro
    'coindesk', 'cointelegraph',                                     # 6º: crypto
    'forbes',                                                        # 7º: general
]

# --- Feeds RSS ---
RSS_FEEDS: Dict[str, Dict[str, Any]] = {
    'cnbc_top':       {'urls': ['https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114'], 'category': 'News & Analysis',          'source_name': 'CNBC'},
    'cnbc_economy':   {'urls': ['https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258'],  'category': 'Economy & Macro',           'source_name': 'CNBC'},
    'cnbc_investing': {'urls': ['https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069'],  'category': 'Investing',                 'source_name': 'CNBC'},
    'cnbc_pf':        {'urls': ['https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=21324812'],  'category': 'Personal Finance',          'source_name': 'CNBC'},
    'marketwatch_top':{'urls': ['http://feeds.marketwatch.com/marketwatch/topstories'],                                   'category': 'Markets & Trading',         'source_name': 'MarketWatch'},
    'marketwatch_pf': {'urls': ['http://feeds.marketwatch.com/marketwatch/pf'],                                           'category': 'Personal Finance',          'source_name': 'MarketWatch'},
    'yahoo_finance':  {'urls': ['https://finance.yahoo.com/news/rssindex'],                                               'category': 'News & Analysis',           'source_name': 'Yahoo Finance'},
    'nasdaq_markets': {'urls': ['https://www.nasdaq.com/feed/rssoutbound?category=Markets'],                              'category': 'Markets & Trading',         'source_name': 'Nasdaq'},
    'nasdaq_earnings':{'urls': ['https://www.nasdaq.com/feed/rssoutbound?category=Earnings'],                             'category': 'Markets & Trading',         'source_name': 'Nasdaq'},
    'kiplinger':      {'urls': ['https://www.kiplinger.com/feed/all'],                                                    'category': 'Personal Finance',          'source_name': 'Kiplinger'},
    'investopedia':   {'urls': ['https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=rss_headline'],           'category': 'Investing',                 'source_name': 'Investopedia'},
    'seeking_alpha':  {'urls': ['https://seekingalpha.com/feed.xml'],                                                     'category': 'Investing',                 'source_name': 'Seeking Alpha'},
    'coindesk':       {'urls': ['https://www.coindesk.com/arc/outboundfeeds/rss/'],                                       'category': 'Crypto & Digital Assets',   'source_name': 'CoinDesk'},
    'cointelegraph':  {'urls': ['https://cointelegraph.com/rss'],                                                         'category': 'Crypto & Digital Assets',   'source_name': 'Cointelegraph'},
    'usnews_money':   {'urls': ['https://www.usnews.com/rss/money'],                                                      'category': 'Personal Finance',          'source_name': 'US News'},
    'economist':      {'urls': ['https://www.economist.com/finance-and-economics/rss.xml'],                               'category': 'Economy & Macro',           'source_name': 'The Economist'},
    'politico_econ':  {'urls': ['https://rss.politico.com/economy.xml'],                                                  'category': 'Economy & Macro',           'source_name': 'Politico'},
    'forbes':         {'urls': ['https://www.forbes.com/feed/'],                                                          'category': 'News & Analysis',           'source_name': 'Forbes'},
}

# --- HTTP ---
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/91.0.4472.124 Safari/537.36'
)

# --- Configuração da IA ---
def _load_ai_keys() -> List[str]:
    """
    Lê todas as chaves GEMINI_* do ambiente e as retorna em uma lista única e ordenada.
    Procura por padrões: GEMINI_*, GEMINI_KEY*, GEMINI_API*
    """
    keys = {}
    
    # Procurar por todas as variáveis que contenham GEMINI e sejam chaves de API
    for key, value in os.environ.items():
        if value and 'GEMINI' in key.upper() and (key.upper().startswith('GEMINI_') or 'KEY' in key.upper() or 'API' in key.upper()):
            # Validar que é uma chave real (começa com AIza...)
            if str(value).startswith('AIza'):
                keys[key] = value
                logger.info(f"API KEY: {key}")
            else:
                logger.warning(f"VARIAVEL: {key} encontrada mas nao eh chave de API (nao comeca com AIza)")
    
    if not keys:
        logger.error("ERRO: NENHUMA CHAVE DE API GEMINI ENCONTRADA! Verificar .env")
    
    # Sort by key name for predictable order
    sorted_key_names = sorted(keys.keys())
    result = [keys[k] for k in sorted_key_names]
    
    logger.info(f"CARREGADAS {len(result)} chaves de API")
    for idx, key in enumerate(result, 1):
        logger.info(f"  [{idx}] {key[:15]}...{key[-4:]}")
    
    return result

AI_API_KEYS = _load_ai_keys()

# Caminho para o prompt universal na raiz do projeto
PROMPT_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'universal_prompt.txt'
)

AI_MODEL = os.getenv('AI_MODEL', 'gemini-2.5-flash-lite')

AI_GENERATION_CONFIG = {
    'temperature': 0.7,
    'top_p': 1.0,
    'max_output_tokens': 8192,
}

# --- WordPress ---
WORDPRESS_CONFIG = {
    'url': os.getenv('WORDPRESS_URL'),
    'user': os.getenv('WORDPRESS_USER'),
    'password': os.getenv('WORDPRESS_PASSWORD'),
}

# --- Posts Pilares para Linkagem Interna ---
PILAR_POSTS: List[str] = [
    'https://www.thefinance.news/investing/what-is-an-etf-complete-guide/',
    'https://www.thefinance.news/investing/roth-ira-complete-guide/',
    'https://www.thefinance.news/personal-finance/credit-score-explained/',
]

# IDs das categorias no WordPress
# Verificar em: WP Admin → Posts → Categories (ID na URL ao editar)
WORDPRESS_CATEGORIES: Dict[str, int] = {
    'Personal Finance':        132,
    'Credit Cards':            133,
    'Banking':                 134,
    'Investing':               135,
    'News & Analysis':         136,
    'Loans & Mortgages':       137,
    'Retirement':              138,
    'Taxes':                   139,
    'Insurance':               140,
    'Crypto & Digital Assets': 141,
    'Economy & Macro':         142,
    'Markets & Trading':       143,
    'Financial Planning':      144,
    'Fintech & Innovation':    145,
    'Small Business Finance':  146,
}

# Mapeia o source_id para uma lista de nomes de categorias
SOURCE_CATEGORY_MAP: Dict[str, List[str]] = {
    'cnbc_top':       ['News & Analysis'],
    'cnbc_economy':   ['Economy & Macro', 'News & Analysis'],
    'cnbc_investing': ['Investing', 'Markets & Trading'],
    'cnbc_pf':        ['Personal Finance'],
    'marketwatch_top':['Markets & Trading', 'News & Analysis'],
    'marketwatch_pf': ['Personal Finance'],
    'yahoo_finance':  ['News & Analysis'],
    'nasdaq_markets': ['Markets & Trading'],
    'nasdaq_earnings':['Markets & Trading', 'News & Analysis'],
    'kiplinger':      ['Personal Finance', 'Retirement'],
    'investopedia':   ['Investing', 'Personal Finance'],
    'seeking_alpha':  ['Investing'],
    'coindesk':       ['Crypto & Digital Assets'],
    'cointelegraph':  ['Crypto & Digital Assets'],
    'usnews_money':   ['Personal Finance'],
    'economist':      ['Economy & Macro'],
    'politico_econ':  ['Economy & Macro'],
    'forbes':         ['News & Analysis'],
}


# --- Sinônimos de Categorias ---
CATEGORY_ALIASES: Dict[str, str] = {
    'finance':          'Personal Finance',
    'personal finance': 'Personal Finance',
    'investing':        'Investing',
    'investment':       'Investing',
    'markets':          'Markets & Trading',
    'trading':          'Markets & Trading',
    'economy':          'Economy & Macro',
    'macro':            'Economy & Macro',
    'crypto':           'Crypto & Digital Assets',
    'bitcoin':          'Crypto & Digital Assets',
    'cryptocurrency':   'Crypto & Digital Assets',
    'tax':              'Taxes',
    'taxes':            'Taxes',
    'retirement':       'Retirement',
    'fintech':          'Fintech & Innovation',
    'credit card':      'Credit Cards',
    'credit cards':     'Credit Cards',
    'mortgage':         'Loans & Mortgages',
    'loans':            'Loans & Mortgages',
    'insurance':        'Insurance',
    'banking':          'Banking',
    'small business':   'Small Business Finance',
    'news':             'News & Analysis',
    'analysis':         'News & Analysis',
}


# --- Agendador / Pipeline ---
SCHEDULE_CONFIG = {
    'check_interval_minutes': int(os.getenv('CHECK_INTERVAL_MINUTES', 15)),
    'max_articles_per_feed': int(os.getenv('MAX_ARTICLES_PER_FEED', 3)),
    'per_article_delay_seconds': int(os.getenv('PER_ARTICLE_DELAY_SECONDS', 8)),
    'per_feed_delay_seconds': int(os.getenv('PER_FEED_DELAY_SECONDS', 15)),
    'cleanup_after_hours': int(os.getenv('CLEANUP_AFTER_HOURS', 72)),
}

PIPELINE_CONFIG = {
    'images_mode': os.getenv('IMAGES_MODE', 'hotlink'),  # 'hotlink' ou 'download_upload'
    'attribution_policy': 'Fonte: {domain}',
    'publisher_name': 'TheFinance',
    'publisher_logo_url': os.getenv(
        'PUBLISHER_LOGO_URL',
        'https://exemplo.com/logo.png'  # TODO: atualizar para a URL real do logo
    ),
}

# --- Configuração TMDb (The Movie Database) ---
TMDB_CONFIG = {
    'enabled': os.getenv('TMDB_ENABLED', 'false').lower() == 'true',
    'api_key': os.getenv('TMDB_API_KEY', ''),
    'max_enrichments_per_article': int(os.getenv('TMDB_MAX_ENRICHMENTS', 3)),
    'extract_trending': os.getenv('TMDB_EXTRACT_TRENDING', 'false').lower() == 'true',
    'extract_upcoming': os.getenv('TMDB_EXTRACT_UPCOMING', 'false').lower() == 'true',
}
