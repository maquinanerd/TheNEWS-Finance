/**
 * setup/03-pages.js
 * Cria as 6 páginas estáticas do TheNEWS-Finance no WordPress.
 * Uso:  node setup/03-pages.js
 */

'use strict';

const { api } = require('./config');

const PAGES = [
  {
    title:  'About TheFinance',
    slug:   'about',
    status: 'publish',
    content: `<h2>Who We Are</h2>
<p>TheFinance is an independent financial news and personal finance portal covering US markets, investing, credit, mortgages, taxes and macroeconomics. We publish daily news and expert guides to help Americans make smarter financial decisions.</p>

<h2>Our Editorial Standards</h2>
<p>Every article published on TheFinance is reviewed for accuracy, fairness and compliance with FTC disclosure requirements. We do not accept payment in exchange for positive coverage. Affiliate relationships are disclosed on every relevant article.</p>

<h2>Our Team</h2>
<p>TheFinance is produced by a team of financial journalists and editors with backgrounds in economics, banking, personal finance and market analysis.</p>

<h2>Contact Us</h2>
<p>Editorial: [email protected]<br>
Corrections: [email protected]<br>
Security: [email protected]</p>`,
    yoast_title: 'About TheFinance — Our Mission, Team & Editorial Standards',
    yoast_desc:  'Learn about TheFinance: our mission, editorial standards, team of financial journalists and how we cover US personal finance and markets.',
  },
  {
    title:  'Contact',
    slug:   'contact',
    status: 'publish',
    content: `<h2>Get in Touch</h2>
<p>We welcome questions, tips, corrections and partnership inquiries.</p>
<ul>
<li><strong>General inquiries:</strong> [email protected]</li>
<li><strong>Corrections & fact-checks:</strong> [email protected]</li>
<li><strong>Advertising & partnerships:</strong> [email protected]</li>
<li><strong>Security vulnerabilities:</strong> [email protected]</li>
</ul>
<p>We aim to respond within 2 business days.</p>`,
    yoast_title: 'Contact TheFinance — Editorial, Corrections & Partnerships',
    yoast_desc:  'Contact TheFinance editorial team for general inquiries, corrections, advertising or security vulnerability disclosures.',
  },
  {
    title:  'Privacy Policy',
    slug:   'privacy-policy',
    status: 'publish',
    content: `<p><em>Last updated: March 2025</em></p>
<h2>Information We Collect</h2>
<p>TheFinance collects anonymous usage data through Google Analytics 4 including page views, session duration, and general geographic location. We do not sell personal data to third parties.</p>
<h2>Cookies</h2>
<p>We use cookies for analytics (Google Analytics) and advertising (Google AdSense). You may opt out via your browser settings or Google's opt-out tools.</p>
<h2>Third-Party Links</h2>
<p>Our site contains affiliate links. When you click these links and make a purchase or sign up, we may earn a commission at no additional cost to you.</p>
<h2>Contact</h2>
<p>For privacy-related requests, email: [email protected]</p>`,
    yoast_title: 'Privacy Policy — TheFinance',
    yoast_desc:  'TheFinance Privacy Policy: how we collect, use and protect your data, our cookie policy and third-party disclosure practices.',
  },
  {
    title:  'Terms of Service',
    slug:   'terms',
    status: 'publish',
    content: `<p><em>Last updated: March 2025</em></p>
<h2>Acceptance of Terms</h2>
<p>By accessing TheFinance, you agree to these Terms of Service. If you do not agree, please do not use this site.</p>
<h2>Use of Content</h2>
<p>All content on TheFinance is for informational purposes only. You may not reproduce, distribute or monetize our content without written permission.</p>
<h2>No Financial Advice</h2>
<p>Nothing on TheFinance constitutes financial, legal or tax advice. Always consult a qualified professional before making financial decisions.</p>`,
    yoast_title: 'Terms of Service — TheFinance',
    yoast_desc:  'TheFinance Terms of Service: acceptable use, content ownership, financial disclaimer and limitation of liability.',
  },
  {
    title:  'Financial Disclaimer',
    slug:   'disclaimer',
    status: 'publish',
    content: `<h2>Not Financial Advice</h2>
<p>The content published on TheFinance is for <strong>informational and educational purposes only</strong> and does not constitute financial, investment, legal or tax advice. Always consult with a licensed financial advisor, attorney or tax professional before making any financial decisions.</p>
<h2>Affiliate Disclosure</h2>
<p>TheFinance participates in affiliate marketing programs. We may earn a commission when you click links to partner products or services, at no additional cost to you. Our editorial opinions are not influenced by affiliate relationships.</p>
<h2>Accuracy</h2>
<p>We strive to publish accurate and up-to-date information, but financial rates, regulations and product terms change frequently. Always verify information directly with financial institutions before acting on it.</p>`,
    yoast_title: 'Financial Disclaimer — TheFinance',
    yoast_desc:  'Important disclaimer: TheFinance content is for informational purposes only and does not constitute financial advice. Affiliate disclosure included.',
  },
  {
    title:  'Editorial Standards & Corrections Policy',
    slug:   'editorial-standards',
    status: 'publish',
    content: `<h2>Our Commitment to Accuracy</h2>
<p>TheFinance is committed to accurate, fair and transparent financial journalism. Our editorial process includes fact-checking against primary sources (Federal Reserve, IRS, SEC, BLS) before publication.</p>
<h2>Corrections Policy</h2>
<p>When errors are identified, we correct them promptly and transparently with an editor's note at the top of the article. To report an error, email [email protected].</p>
<h2>Independence</h2>
<p>TheFinance editorial content is produced independently of our advertising and affiliate relationships. Advertisers do not influence our coverage.</p>`,
    yoast_title: 'Editorial Standards & Corrections Policy — TheFinance',
    yoast_desc:  'How TheFinance maintains editorial accuracy, our fact-checking process, corrections policy and independence from advertising.',
  },
];

async function run() {
  console.log('📄  Creating static pages...\n');
  for (const page of PAGES) {
    const { yoast_title, yoast_desc, ...wpData } = page;
    try {
      const res = await api('POST', 'pages', {
        ...wpData,
        meta: {
          '_yoast_wpseo_title':               yoast_title,
          '_yoast_wpseo_metadesc':            yoast_desc,
          '_yoast_wpseo_meta-robots-noindex': '0',
        },
      });
      console.log(`  ✅  "${page.title}"  →  ID ${res.id}  →  ${res.link}`);
    } catch (e) {
      console.error(`  ❌  "${page.title}"  →  ${e.message}`);
    }
  }
  console.log('\n✅  All pages created!');
}
run().catch(console.error);
