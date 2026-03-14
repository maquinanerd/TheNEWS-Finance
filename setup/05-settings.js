/**
 * setup/05-settings.js
 * Configura as definições gerais do site TheNEWS-Finance no WordPress.
 * Uso:  node setup/05-settings.js
 */

'use strict';

const { api } = require('./config');

const SETTINGS = {
  title:                    'TheFinance',
  description:              'Personal Finance, Investing & Money News',
  timezone_string:          'America/New_York',
  date_format:              'F j, Y',   // March 13, 2025
  time_format:              'g:i a',    // 2:30 pm
  posts_per_page:           12,
  posts_per_rss:            20,
  default_category:         136,        // News & Analysis (ID criado em 01-categories.js)
  default_comment_status:   'closed',   // desativa comentários globalmente
  default_ping_status:      'closed',
};

async function run() {
  console.log('⚙️  Updating site settings...\n');
  const data = await api('POST', 'settings', SETTINGS);

  console.log('  ✅  Site title:       ', data.title);
  console.log('  ✅  Tagline:          ', data.description);
  console.log('  ✅  Date format:      ', data.date_format);
  console.log('  ✅  Posts per page:   ', data.posts_per_page);
  console.log('  ✅  Default category: ', data.default_category, '(News & Analysis)');
  console.log('  ✅  Comments:          closed sitewide');
  console.log('  ⚠️  Timezone & posts_per_rss: set manually in WP Admin → Settings → General/Reading');
  console.log('      Timezone: America/New_York  |  RSS posts: 20');
  console.log('\n✅  Settings updated!');
}
run().catch(console.error);
