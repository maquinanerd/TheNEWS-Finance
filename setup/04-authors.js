/**
 * setup/04-authors.js
 * Atualiza os perfis dos autores E-E-A-T no WordPress usando as Application Passwords
 * de cada autor (lidas do .env). Requer que os usuários já existam no WP.
 *
 * Uso:  node setup/04-authors.js
 *
 * Para adicionar mais autores:
 *  1. Crie o usuário em WP Admin → Usuários → Adicionar Novo (role: Editor)
 *  2. Gere uma Application Password em WP Admin → Usuários → [nome] → Application Passwords
 *  3. Adicione WP_AUTHOR_N_USER e WP_AUTHOR_N_KEY no .env
 *  4. Adicione a entrada correspondente no array AUTHORS abaixo
 */

'use strict';

const fs   = require('fs');
const path = require('path');

// ── Ler .env manualmente ──────────────────────────────────────────────────────
const envPath = path.resolve(__dirname, '..', '.env');
const env = {};
fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
  const t = line.trim();
  if (!t || t.startsWith('#')) return;
  const idx = t.indexOf('=');
  if (idx === -1) return;
  env[t.slice(0, idx).trim()] = t.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
});

const WP_URL = (env.WORDPRESS_URL || '').replace(/\/?$/, '/');

function makeApi(user, key) {
  const auth = Buffer.from(`${user}:${key}`).toString('base64');
  return async function api(method, endpoint, body) {
    const res  = await fetch(WP_URL + endpoint, {
      method,
      headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'application/json' },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    const text = await res.text();
    let json; try { json = JSON.parse(text); } catch { json = text; }
    if (!res.ok) throw Object.assign(new Error(`HTTP ${res.status} — ${json?.message || text}`), { body: json });
    return json;
  };
}

// ── Autores — adicionar entradas conforme .env for preenchido ─────────────────
const AUTHORS = [
  {
    envUser: 'WP_AUTHOR_1_USER',
    envKey:  'WP_AUTHOR_1_KEY',
    display: 'Sarah Mitchell',
    description: 'Sarah Mitchell is a financial journalist with over 10 years of experience covering personal finance, credit cards and mortgages. Former contributor to MarketWatch and Kiplinger. She holds a degree in Economics from the University of Michigan.',
  },
  {
    envUser: 'WP_AUTHOR_2_USER',
    envKey:  'WP_AUTHOR_2_KEY',
    display: 'James Carter',
    description: 'James Carter covers US equity markets, ETFs and macroeconomics. He spent 8 years as a financial analyst on Wall Street before transitioning to financial journalism. CFA Level II candidate.',
  },
  {
    envUser: 'WP_AUTHOR_3_USER',
    envKey:  'WP_AUTHOR_3_KEY',
    display: 'Priya Nair',
    description: 'Priya Nair specializes in tax planning, retirement accounts and Social Security optimization. She is an Enrolled Agent (EA) with the IRS and has helped thousands of Americans navigate tax season.',
  },
  {
    envUser: 'WP_AUTHOR_4_USER',
    envKey:  'WP_AUTHOR_4_KEY',
    display: 'Derek Walsh',
    description: 'Derek Walsh has covered the cryptocurrency industry since 2017, reporting on Bitcoin, DeFi, blockchain regulation and digital asset markets. Former reporter at CoinDesk.',
  },
  {
    envUser: 'WP_AUTHOR_5_USER',
    envKey:  'WP_AUTHOR_5_KEY',
    display: 'Lisa Chen',
    description: 'Lisa Chen covers insurance, health finance and small business financial planning. She brings 7 years of experience in the insurance industry and holds a CLU (Chartered Life Underwriter) designation.',
  },
];

async function run() {
  console.log('👤  Updating author profiles...\n');

  for (const author of AUTHORS) {
    const user = env[author.envUser];
    const key  = env[author.envKey];

    if (!user || !key) {
      console.log(`  ⏭️  ${author.display.padEnd(20)} — skipped (${author.envKey} not set in .env)`);
      continue;
    }

    const api = makeApi(user, key);
    try {
      // Cada autor autentica como si mesmo para atualizar o próprio perfil
      const me = await api('GET', 'users/me');
      await api('PUT', `users/${me.id}`, { description: author.description });
      console.log(`  ✅  ${author.display.padEnd(20)} →  ID ${me.id}  (bio updated)`);
    } catch (e) {
      console.error(`  ❌  ${author.display.padEnd(20)} →  ${e.message}`);
    }
  }

  console.log('\n💡  Next: upload author photos in WP Admin → Users → [name] → Profile photo');
  console.log('    Or use PublishPress Authors to set photos via the Authors menu.');
}
run().catch(console.error);

