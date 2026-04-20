'use strict';

/**
 * Convert HTML email body to clean markdown-style plain text.
 *
 * Rules:
 *  - <svg>               → removed entirely
 *  - <img src="https?">  → ![alt](url)
 *  - <img> other src     → removed (base64, cid:, relative, etc.)
 *  - <blockquote>        → lines prefixed with "> " (nesting adds "> > ")
 *  - Links, bold, italic → markdown equivalents
 *  - Non-inline attachments appended as "📎 filename"
 */
function htmlToMarkdown(html, attachments) {
  if (!html || !html.trim()) return '';
  let text = html;

  // Strip style / script blocks
  text = text.replace(/<style\b[\s\S]*?<\/style>/gi, '');
  text = text.replace(/<script\b[\s\S]*?<\/script>/gi, '');

  // Strip SVG (including inline)
  text = text.replace(/<svg\b[\s\S]*?<\/svg>/gi, '');

  // Images: URL src → markdown image, everything else → removed
  text = text.replace(/<img\b([^>]*?)(?:\s*\/?>)/gi, (_, attrs) => {
    const src = extractAttr(attrs, 'src');
    const alt = extractAttr(attrs, 'alt') || '';
    if (src && /^https?:\/\//i.test(src)) {
      return `![${alt}](${src})`;
    }
    return '';
  });

  // Horizontal rules
  text = text.replace(/<hr\b[^>]*?\/?>/gi, '\n\n---\n\n');

  // Headings
  for (let i = 6; i >= 1; i--) {
    const hashes = '#'.repeat(i);
    text = text.replace(
      new RegExp(`<h${i}\\b[^>]*?>([\\s\\S]*?)<\\/h${i}>`, 'gi'),
      (_, c) => `\n${hashes} ${innerText(c).trim()}\n`
    );
  }

  // Links
  text = text.replace(
    /<a\b[^>]*?href=["']([^"']*)["'][^>]*?>([\s\S]*?)<\/a>/gi,
    (_, href, inner) => {
      const linkText = innerText(inner).trim();
      if (!linkText) return href || '';
      if (linkText === href) return href;
      return `[${linkText}](${href})`;
    }
  );

  // Bold / italic (after links so nested markup resolves cleanly)
  text = text.replace(/<(?:b|strong)\b[^>]*?>([\s\S]*?)<\/(?:b|strong)>/gi, (_, c) => {
    const t = innerText(c).trim();
    return t ? `**${t}**` : '';
  });
  text = text.replace(/<(?:i|em)\b[^>]*?>([\s\S]*?)<\/(?:i|em)>/gi, (_, c) => {
    const t = innerText(c).trim();
    return t ? `*${t}*` : '';
  });

  // List items
  text = text.replace(/<li\b[^>]*?>([\s\S]*?)<\/li>/gi, (_, c) => `\n- ${innerText(c).trim()}`);
  text = text.replace(/<\/?[uo]l\b[^>]*?>/gi, '\n');

  // Blockquotes: process inside-out using \x02 sentinel per indentation level.
  // The negative-lookahead pattern ensures we always match the innermost one first.
  {
    let prev, iterations = 0;
    do {
      prev = text;
      text = text.replace(
        /<blockquote\b[^>]*?>((?:(?!<\/?blockquote)[\s\S])*?)<\/blockquote>/gi,
        (_, content) => '\n\x02' + content.replace(/\n/g, '\n\x02') + '\n'
      );
    } while (text !== prev && ++iterations < 10);
  }

  // Block-level elements → newlines
  text = text.replace(/<br\s*\/?>/gi, '\n');
  text = text.replace(/<\/(?:p|div|tr|li|pre)>/gi, '\n');
  text = text.replace(/<(?:p|div|pre)\b[^>]*?>/gi, '\n');
  text = text.replace(/<\/(?:table|ul|ol)>/gi, '\n');

  // Strip all remaining tags
  text = text.replace(/<[^>]+>/g, '');

  // Decode HTML entities
  text = decodeEntities(text);

  // Convert \x02 sentinels to "> " blockquote prefixes (each \x02 = one level)
  text = text.split('\n').map(line => {
    let depth = 0;
    while (line.startsWith('\x02')) { depth++; line = line.slice(1); }
    return depth > 0 ? '> '.repeat(depth) + line : line;
  }).join('\n');

  // Collapse 3+ blank lines → max 2
  text = text.replace(/\n{3,}/g, '\n\n');
  text = text.trim();

  // Append non-inline attachments
  const attLines = buildAttachmentLines(attachments);
  if (attLines.length > 0) {
    text += '\n\n---\n**Attachments:**\n' + attLines.join('\n');
  }

  return text;
}

// ── helpers ──────────────────────────────────────────────────────────────────

function extractAttr(attrs, name) {
  const m = attrs.match(new RegExp(`${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'));
  if (!m) return '';
  return m[1] !== undefined ? m[1] : m[2] !== undefined ? m[2] : (m[3] || '');
}

function innerText(html) {
  return decodeEntities(html.replace(/<[^>]+>/g, ''));
}

function decodeEntities(text) {
  return text
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n))
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCharCode(parseInt(h, 16)));
}

function buildAttachmentLines(attachments) {
  if (!attachments || !attachments.length) return [];
  return attachments
    .filter(a => a.contentDisposition !== 'inline' && !a.contentId)
    .map(a => `- 📎 ${a.filename || a.name || 'attachment'}`);
}

module.exports = { htmlToMarkdown };
