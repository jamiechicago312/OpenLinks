const test = require("node:test");
const assert = require("node:assert/strict");

const {
  buildDestinationUrl,
  buildRedirectIndex,
  getRedirectDefinition,
  normalizePathname,
} = require("../redirects");

test("normalizePathname adds a leading slash and trims trailing slash", () => {
  assert.equal(normalizePathname("slack/"), "/slack");
  assert.equal(normalizePathname("/slack"), "/slack");
  assert.equal(normalizePathname(""), "/");
  assert.equal(normalizePathname("/"), "/");
});

test("buildRedirectIndex maps slugs to their normalized redirect entries", () => {
  const index = buildRedirectIndex([
    { slug: "/luma", destination: "https://lu.ma/openhands", permanent: false },
    { slug: "github", destination: "https://github.com/jamiechicago312", permanent: true },
  ]);

  assert.equal(index.get("/luma").destination, "https://lu.ma/openhands");
  assert.equal(index.get("/luma").permanent, false);
  assert.equal(index.get("/github").permanent, true);
});

test("buildRedirectIndex skips entries missing slug or destination", () => {
  const index = buildRedirectIndex([
    { slug: "/ok", destination: "https://ok.example.com" },
    { slug: null, destination: "https://bad.example.com" },
    { destination: "https://bad.example.com" },
    null,
  ]);

  assert.equal(index.size, 1);
  assert.equal(index.get("/ok").destination, "https://ok.example.com");
});

test("getRedirectDefinition returns configured redirects when present", () => {
  const index = buildRedirectIndex([
    { slug: "/slack", destination: "https://join.slack.com/t/example", permanent: false },
  ]);

  const redirect = getRedirectDefinition("/slack", index, "https://example.com");

  assert.equal(redirect.destination, "https://join.slack.com/t/example");
  assert.equal(redirect.isFallback, false);
  assert.equal(redirect.statusCode, 307);
});

test("getRedirectDefinition returns a 308 for permanent redirects", () => {
  const index = buildRedirectIndex([
    { slug: "/github", destination: "https://github.com/jamiechicago312", permanent: true },
  ]);

  const redirect = getRedirectDefinition("/github", index, "https://example.com");

  assert.equal(redirect.statusCode, 308);
  assert.equal(redirect.permanent, true);
});

test("getRedirectDefinition falls back when the slug is unknown", () => {
  const index = buildRedirectIndex([]);
  const redirect = getRedirectDefinition("/unknown-link", index, "https://fallback.example.com");

  assert.equal(redirect.destination, "https://fallback.example.com");
  assert.equal(redirect.isFallback, true);
  assert.equal(redirect.statusCode, 307);
});

test("buildDestinationUrl preserves destination query params and appends incoming ones", () => {
  const destinationUrl = buildDestinationUrl(
    "https://example.com/contact?utm_source=newsletter",
    new URLSearchParams("ref=partner&utm_medium=app"),
  );

  assert.equal(
    destinationUrl.toString(),
    "https://example.com/contact?utm_source=newsletter&ref=partner&utm_medium=app",
  );
});

test("buildDestinationUrl only forwards caller-supplied query params", () => {
  const destinationUrl = buildDestinationUrl(
    "https://example.com",
    new URLSearchParams("q=1"),
  );

  assert.equal(destinationUrl.toString(), "https://example.com/?q=1");
});
