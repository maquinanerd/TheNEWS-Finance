/**
 * setup/01-categories.js
 * Creates all 15 TheNEWS-Finance WordPress categories.
 * Usage:  node setup/01-categories.js
 *
 * Output: prints the ID map ready to paste into app/config.py → WORDPRESS_CATEGORIES
 */

'use strict';

const { api } = require('./config');

const CATEGORIES = [
  { name: 'Personal Finance',       slug: 'personal-finance',
    description: 'Budgeting, saving, debt management and financial literacy guides for US readers.' },
  { name: 'Credit Cards',           slug: 'credit-cards',
    description: 'Credit card reviews, comparisons and best picks: cashback, travel rewards, 0% APR and business cards.' },
  { name: 'Banking',                slug: 'banking',
    description: 'Savings accounts, CDs, checking accounts and online bank reviews for US consumers.' },
  { name: 'Investing',              slug: 'investing',
    description: 'Stock market guides, ETF reviews, index fund strategies and investment news for US investors.' },
  { name: 'News & Analysis',        slug: 'news-analysis',
    description: 'Breaking financial news, market updates and expert analysis from TheFinance.' },
  { name: 'Loans & Mortgages',      slug: 'loans-mortgages',
    description: 'Mortgage rates, personal loan comparisons, student loans and home buying guides.' },
  { name: 'Retirement',             slug: 'retirement',
    description: '401(k), Roth IRA, Social Security and retirement planning guides for Americans.' },
  { name: 'Taxes',                  slug: 'taxes',
    description: 'US tax filing guides, IRS news, deduction strategies and state tax analysis.' },
  { name: 'Insurance',              slug: 'insurance',
    description: 'Health, auto, life and home insurance reviews and comparisons for US consumers.' },
  { name: 'Crypto & Digital Assets', slug: 'crypto',
    description: 'Bitcoin, Ethereum, DeFi, crypto exchange reviews and digital asset news.' },
  { name: 'Economy & Macro',        slug: 'economy',
    description: 'Federal Reserve decisions, inflation data, GDP reports and US economic analysis.' },
  { name: 'Markets & Trading',      slug: 'markets',
    description: 'Stock market news, earnings reports, IPO analysis and trading strategies.' },
  { name: 'Financial Planning',     slug: 'financial-planning',
    description: 'Estate planning, FIRE movement, wealth building and finding a financial advisor.' },
  { name: 'Fintech & Innovation',   slug: 'fintech',
    description: 'Neobanks, payment apps, robo-advisors, BNPL and emerging financial technology.' },
  { name: 'Small Business Finance', slug: 'small-business',
    description: 'Business banking, credit cards, loans, accounting and tax guides for small business owners.' },
];

async function run() {
  console.log('🗂  Creating categories...\n');
  const created = {};

  for (const cat of CATEGORIES) {
    try {
      const res = await api('POST', 'categories', cat);
      created[cat.name] = res.id;
      console.log(`  ✅  ${cat.name.padEnd(26)} →  ID ${res.id}`);
    } catch (e) {
      // term_exists → already created, fetch its ID
      const existing = await api('GET', `categories?slug=${cat.slug}&per_page=1`).catch(() => []);
      if (existing[0]) {
        created[cat.name] = existing[0].id;
        console.log(`  ⚠️  ${cat.name.padEnd(26)} already exists  →  ID ${existing[0].id}`);
      } else {
        console.error(`  ❌  ${cat.name}  —  ${e.message}`);
      }
    }
  }

  // ── Print config.py snippet ───────────────────────────────────────────────
  console.log('\n' + '─'.repeat(60));
  console.log('📋  Paste into app/config.py → WORDPRESS_CATEGORIES:\n');
  console.log('WORDPRESS_CATEGORIES: Dict[str, int] = {');
  for (const [name, id] of Object.entries(created)) {
    console.log(`    '${name}':${' '.repeat(Math.max(1, 28 - name.length))}${id},`);
  }
  console.log('}');
  console.log('─'.repeat(60));
}

run().catch(console.error);
