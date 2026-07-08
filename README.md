# OpenLinks

A small, Vercel-hosted short link service.

Each short link lives in its own JSON file under `data/links/active/`.
A single Vercel serverless function handles redirects. There is no analytics,
no tracking by default, and no database — just static JSON files and a 307/308
response. Click notifications to a Telegram bot are available as an optional
opt-in via environment variables (see "Click notifications" below).

## How it works

- `data/links/active/*.json` defines every short link (one file per link).
- `redirects.config.json` sets the fallback destination for unknown paths.
- `api/redirect.js` is the Vercel serverless function that performs the redirect.
- `vercel.json` routes every non-file path (paths without a `.`) to the function.

When someone visits `https://your-domain/<slug>`:

1. Vercel's filesystem handler lets real files (images, etc.) serve normally.
2. Anything else is rewritten to `/api/redirect?__oh_redirect_pathname=<slug>`.
3. The function looks up the slug in the in-memory redirect index and 307/308s
   the user to the configured destination, preserving any incoming query
   parameters (UTMs, campaign tags, etc.).

## Add a short link

Create a new JSON file in `data/links/active/`. The filename does not matter;
each link is keyed by its `slug` field.

```json
{
  "slug": "luma",
  "destination": "https://lu.ma/openhands",
  "permanent": false,
  "description": "Community call landing page",
  "tags": ["newsletter", "events"]
}
```

Required fields:

- `slug` — the path without the host (e.g. `/luma`). Leading and trailing
  slashes are normalized.
- `destination` — the full URL to redirect to.

Optional fields:

- `permanent` — `true` for a 308 (permanent) redirect, `false` (default) for a
  307 (temporary) redirect. Use 307 unless the destination will never change.
- `description` — free-form text, ignored by the redirector. Use it for notes.
- `tags` — array of strings, ignored by the redirector. Use it for grouping.

Commit and push. Vercel redeploys automatically and the new link is live.

## Update or remove a short link

- **Update:** edit the JSON file and change the `destination` (or any other
  field). Push.
- **Remove:** delete the JSON file from `data/links/active/` and push. Any
  traffic to that slug will fall through to the fallback destination.

## Fallback destination

Unknown paths (no dots in the name, no matching slug) are sent to the
fallback destination. It is set in `redirects.config.json`:

```json
{
  "fallbackDestination": "https://example.com"
}
```

You can also override it at runtime by setting the `FALLBACK_DESTINATION`
environment variable in your Vercel project settings.

## Query parameters

Incoming query parameters are appended to the destination URL. This means
campaign links like `https://your-domain/luma?utm_source=newsletter` continue
to work without you having to bake UTMs into the destination.

Internal routing parameter (`__oh_redirect_pathname`) is stripped before the
redirect.

## Click notifications (optional, opt-in)

If you set both of these environment variables in your Vercel project, every
click will fire-and-forget POST a message to a Telegram bot:

- `TELEGRAM_BOT_TOKEN` — the bot token from `@BotFather`.
- `TELEGRAM_CHAT_ID` — your numeric chat ID (DM your bot once, then call
  `https://api.telegram.org/bot<TOKEN>/getUpdates` to find it).

If either is unset, no notification fires and the redirect behaves exactly as
before. There is no other knob to flip.

The message includes the short path, timestamp, approximate city/country
(from Vercel's edge geo headers), user agent, and referer. The fetch is
fired without `await`, so a slow or unreachable Telegram endpoint can never
delay or fail the redirect.

Set up a bot in 2 minutes:

1. DM `@BotFather`, send `/newbot`, follow the prompts, copy the token.
2. DM your new bot any message so it can DM you back.
3. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` and copy the
   `chat.id` from the response.
4. In Vercel: Settings → Environment Variables → add `TELEGRAM_BOT_TOKEN`
   and `TELEGRAM_CHAT_ID`. Redeploy.

## Per-application link pattern

If you're sending these links to recruiters as part of a job search, the
simplest way to know which company clicked is to give each application its
own short link. Filename and slug should both reflect the company:

```text
data/links/active/app-google.json   → /app-google
data/links/active/app-meta.json     → /app-meta
data/links/active/app-acme.json     → /app-acme
```

The path itself is the only signal you need; no need to disambiguate from
referer or other header data. Combine with Telegram notifications and you get
a push on your phone each time a recruiter opens a specific application.

## Local verification

```bash
npm test
```

That runs `node --test` over `test/redirects.test.js`. The tests cover path
normalization, index building, fallback behavior, status codes, and query
parameter forwarding.

You can also syntax-check the runtime files:

```bash
node --check api/redirect.js
node --check redirects.js
node --check redirects-loader.js
```

## Deploying

1. Push this repo to GitHub.
2. Import it into Vercel as a new project.
3. (Optional) Set `FALLBACK_DESTINATION` in Vercel environment variables.
4. (Optional) Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to enable
   click notifications. See "Click notifications" above.
5. Done — every push to `main` redeploys.

No build step, no database. Environment secrets are only needed if you opt
into Telegram notifications.

## File layout

```
.
├── api/
│   └── redirect.js          # Vercel serverless redirect handler
├── data/
│   └── links/
│       └── active/          # One JSON file per short link
├── lib/
│   └── telegram.js          # Optional Telegram click-notification module
├── test/
│   ├── redirects.test.js    # Unit tests for the redirect logic
│   └── telegram.test.js     # Unit tests for the telegram module
├── redirects.config.json    # Fallback destination
├── redirects.js             # Core redirect logic (lookup, normalize, build URL)
├── redirects-loader.js      # Loads link JSON files into an in-memory index
├── vercel.json              # Vercel routing config
├── package.json
├── .gitignore
├── LICENSE
├── AGENTS.md                # Repo-specific agent guardrails
└── README.md
```
