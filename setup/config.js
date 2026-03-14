/**
 * setup/config.js
 * Shared WordPress REST API helper for TheNEWS-Finance setup scripts.
 * Reads credentials from ../.env — no npm packages required.
 * Requires Node 18+ (native fetch).
 */

'use strict';

const fs   = require('fs');
const path = require('path');

// ── 1. Parse .env ────────────────────────────────────────────────────────────
const envPath = path.resolve(__dirname, '..', '.env');
const env     = {};

if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8')
    .split('\n')
    .forEach(line => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;
      const idx = trimmed.indexOf('=');
      if (idx === -1) return;
      const key = trimmed.slice(0, idx).trim();
      const val = trimmed.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
      env[key] = val;
    });
} else {
  console.error('❌  .env not found at', envPath);
  process.exit(1);
}

const WP_URL  = (env.WORDPRESS_URL || '').replace(/\/?$/, '/'); // ensure trailing /
const WP_USER = env.WORDPRESS_USER;
const WP_PASS = env.WORDPRESS_PASSWORD;

if (!WP_URL || !WP_USER || !WP_PASS) {
  console.error('❌  WORDPRESS_URL, WORDPRESS_USER or WORDPRESS_PASSWORD missing in .env');
  process.exit(1);
}

const AUTH = Buffer.from(`${WP_USER}:${WP_PASS}`).toString('base64');

// ── 2. api() helper ──────────────────────────────────────────────────────────
/**
 * @param {'GET'|'POST'|'PUT'|'DELETE'} method
 * @param {string} endpoint  e.g. 'categories' or 'categories?slug=foo'
 * @param {object} [body]    JSON body for POST/PUT
 * @returns {Promise<any>}   Parsed JSON response; throws on HTTP ≥ 400
 */
async function api(method, endpoint, body) {
  const url = WP_URL + endpoint;
  const opts = {
    method,
    headers: {
      'Authorization': `Basic ${AUTH}`,
      'Content-Type':  'application/json',
    },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const text = await res.text();

  let json;
  try { json = JSON.parse(text); } catch { json = text; }

  if (!res.ok) {
    const msg = json?.message || text;
    throw Object.assign(new Error(`HTTP ${res.status} — ${msg}`), { status: res.status, body: json });
  }
  return json;
}

module.exports = { api, WP_URL, WP_USER };
