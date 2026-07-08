const TELEGRAM_API_BASE = "https://api.telegram.org";

function isTelegramConfigured() {
  return Boolean(
    process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID,
  );
}

// Telegram's legacy "Markdown" parse mode treats these characters as
// formatting markup and will reject the message if they appear unescaped
// inside a non-entity span. We use legacy Markdown (not MarkdownV2) so we
// only have to escape these four.
function escapeMarkdown(text) {
  return String(text == null ? "" : text).replace(/([_*`[])/g, "\\$1");
}

function formatClickMessage(click) {
  const shortPath = escapeMarkdown(click.shortPath);
  const timestamp = escapeMarkdown(click.timestamp);
  const city = escapeMarkdown(click.city || "?");
  const country = escapeMarkdown(click.country || "?");
  const userAgent = escapeMarkdown(click.userAgent || "?");
  const referer = escapeMarkdown(click.referer || "(direct)");

  return [
    `🟢 *${shortPath}* clicked`,
    "",
    `*When:* ${timestamp}`,
    `*Where:* ${city}, ${country}`,
    `*Device:* ${userAgent}`,
    `*Referer:* ${referer}`,
  ].join("\n");
}

function notifyClick(click) {
  if (!isTelegramConfigured()) {
    return;
  }
  const url = `${TELEGRAM_API_BASE}/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  const body = {
    chat_id: process.env.TELEGRAM_CHAT_ID,
    text: formatClickMessage(click),
    parse_mode: "Markdown",
    disable_web_page_preview: true,
  };

  // Fire-and-forget: never await, never throw.
  // Analytics must never block or fail the redirect.
  fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  }).catch(() => {});
}

module.exports = {
  escapeMarkdown,
  formatClickMessage,
  isTelegramConfigured,
  notifyClick,
};