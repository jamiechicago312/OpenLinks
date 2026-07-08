const test = require("node:test");
const assert = require("node:assert/strict");

const {
  escapeMarkdown,
  formatClickMessage,
  isTelegramConfigured,
  notifyClick,
} = require("../lib/telegram");

test("escapeMarkdown escapes Telegram Markdown special characters", () => {
  assert.equal(escapeMarkdown("hello"), "hello");
  assert.equal(escapeMarkdown("a_b*c"), "a\\_b\\*c");
  assert.equal(escapeMarkdown("[link]"), "\\[link]");
  assert.equal(escapeMarkdown("`code`"), "\\`code\\`");
});

test("escapeMarkdown handles nullish and non-string input safely", () => {
  assert.equal(escapeMarkdown(null), "");
  assert.equal(escapeMarkdown(undefined), "");
  assert.equal(escapeMarkdown(42), "42");
});

test("formatClickMessage produces a multi-line Markdown message with all fields", () => {
  const message = formatClickMessage({
    shortPath: "/app-google",
    timestamp: "2026-06-30T15:00:00.000Z",
    city: "Chicago",
    country: "US",
    userAgent: "Mozilla/5.0",
    referer: "https://mail.google.com/",
  });

  assert.match(message, /app-google/);
  assert.match(message, /2026-06-30T15:00:00/);
  assert.match(message, /Chicago/);
  assert.match(message, /US/);
  assert.match(message, /Mozilla/);
  assert.match(message, /mail\.google\.com/);
});

test("formatClickMessage falls back to ? and (direct) when fields are missing", () => {
  const message = formatClickMessage({
    shortPath: "/foo",
    timestamp: "2026-01-01T00:00:00.000Z",
  });

  assert.match(message, /\?/);
  assert.match(message, /\(direct\)/);
});

test("isTelegramConfigured reflects env vars at call time", () => {
  const savedToken = process.env.TELEGRAM_BOT_TOKEN;
  const savedChat = process.env.TELEGRAM_CHAT_ID;

  delete process.env.TELEGRAM_BOT_TOKEN;
  delete process.env.TELEGRAM_CHAT_ID;
  assert.equal(isTelegramConfigured(), false);

  process.env.TELEGRAM_BOT_TOKEN = "token";
  assert.equal(isTelegramConfigured(), false);

  process.env.TELEGRAM_CHAT_ID = "123";
  assert.equal(isTelegramConfigured(), true);

  if (savedToken === undefined) delete process.env.TELEGRAM_BOT_TOKEN;
  else process.env.TELEGRAM_BOT_TOKEN = savedToken;
  if (savedChat === undefined) delete process.env.TELEGRAM_CHAT_ID;
  else process.env.TELEGRAM_CHAT_ID = savedChat;
});

test("notifyClick is a no-op when telegram is not configured", async () => {
  const savedToken = process.env.TELEGRAM_BOT_TOKEN;
  const savedChat = process.env.TELEGRAM_CHAT_ID;
  delete process.env.TELEGRAM_BOT_TOKEN;
  delete process.env.TELEGRAM_CHAT_ID;

  let fetchCalled = false;
  const originalFetch = global.fetch;
  global.fetch = async () => {
    fetchCalled = true;
    return { ok: true };
  };
  try {
    notifyClick({
      shortPath: "/x",
      timestamp: "t",
      city: "c",
      country: "C",
      userAgent: "u",
      referer: "r",
    });
    await new Promise((resolve) => setImmediate(resolve));
  } finally {
    global.fetch = originalFetch;
    if (savedToken !== undefined) process.env.TELEGRAM_BOT_TOKEN = savedToken;
    if (savedChat !== undefined) process.env.TELEGRAM_CHAT_ID = savedChat;
  }
  assert.equal(fetchCalled, false);
});

test("notifyClick fires a fire-and-forget fetch when configured", async () => {
  const savedToken = process.env.TELEGRAM_BOT_TOKEN;
  const savedChat = process.env.TELEGRAM_CHAT_ID;
  process.env.TELEGRAM_BOT_TOKEN = "test-token";
  process.env.TELEGRAM_CHAT_ID = "12345";

  let captured = null;
  const originalFetch = global.fetch;
  global.fetch = async (url, options) => {
    captured = { url, options };
    return { ok: true, status: 200 };
  };
  try {
    notifyClick({
      shortPath: "/app-google",
      timestamp: "2026-06-30T15:00:00.000Z",
      city: "Chicago",
      country: "US",
      userAgent: "Mozilla/5.0",
      referer: "https://mail.google.com/",
    });
    await new Promise((resolve) => setImmediate(resolve));
  } finally {
    global.fetch = originalFetch;
    if (savedToken === undefined) delete process.env.TELEGRAM_BOT_TOKEN;
    else process.env.TELEGRAM_BOT_TOKEN = savedToken;
    if (savedChat === undefined) delete process.env.TELEGRAM_CHAT_ID;
    else process.env.TELEGRAM_CHAT_ID = savedChat;
  }

  assert.ok(captured, "fetch was called");
  assert.match(
    captured.url,
    /api\.telegram\.org\/bottest-token\/sendMessage/,
  );
  const body = JSON.parse(captured.options.body);
  assert.equal(body.chat_id, "12345");
  assert.equal(body.parse_mode, "Markdown");
  assert.equal(body.disable_web_page_preview, true);
  assert.match(body.text, /app-google/);
  assert.match(body.text, /Chicago/);
});

test("notifyClick swallows fetch errors silently", async () => {
  const savedToken = process.env.TELEGRAM_BOT_TOKEN;
  const savedChat = process.env.TELEGRAM_CHAT_ID;
  process.env.TELEGRAM_BOT_TOKEN = "test-token";
  process.env.TELEGRAM_CHAT_ID = "12345";

  const originalFetch = global.fetch;
  global.fetch = async () => {
    throw new Error("network down");
  };
  try {
    notifyClick({
      shortPath: "/x",
      timestamp: "t",
      city: "c",
      country: "C",
      userAgent: "u",
      referer: "r",
    });
    await new Promise((resolve) => setImmediate(resolve));
  } finally {
    global.fetch = originalFetch;
    if (savedToken === undefined) delete process.env.TELEGRAM_BOT_TOKEN;
    else process.env.TELEGRAM_BOT_TOKEN = savedToken;
    if (savedChat === undefined) delete process.env.TELEGRAM_CHAT_ID;
    else process.env.TELEGRAM_CHAT_ID = savedChat;
  }
  // Reaching here without an unhandled rejection is the assertion.
});