/**
 * setup/02-tags.js
 * Cria todas as tags do TheNEWS-Finance no WordPress.
 * Uso:  node setup/02-tags.js
 */

'use strict';

const { api } = require('./config');

const TAGS = [
  // Produtos financeiros
  'credit-score', 'mortgage-rates', 'roth-ira', '401k', 'index-funds',
  'etf', 'social-security', 'high-yield-savings', 'cd-rates', 'treasury-bonds',
  // Macro / eventos
  'fed-rate-decision', 'inflation', 'recession', 'sp500', 'bitcoin',
  'earnings', 'ipo', 'tax-season', 'fafsa', 'open-enrollment',
  // Audiência
  'beginners', 'millennials', 'gen-z', 'retirees', 'first-time-homebuyers',
  'freelancers', 'small-business-owners',
  // Tipo de conteúdo
  'how-to-guide', 'comparison', 'review', 'explainer', 'calculator',
  // Instituições
  'vanguard', 'fidelity', 'chase', 'robinhood', 'coinbase', 'sofi',
];

async function run() {
  console.log('🏷  Creating tags...\n');
  for (const slug of TAGS) {
    const name = slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    try {
      const res = await api('POST', 'tags', { name, slug });
      console.log(`  ✅  ${name.padEnd(28)} →  ID ${res.id}`);
    } catch {
      console.log(`  ⚠️  ${name.padEnd(28)} already exists`);
    }
  }
  console.log('\n✅  Done!');
}
run().catch(console.error);
