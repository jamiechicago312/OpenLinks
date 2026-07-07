# OpenLinks

A small, Vercel-hosted short link service.

Each short link lives in its own JSON file under `data/links/active/`.
A single Vercel serverless function handles redirects. There is no analytics,
no tracking, and no database — just static JSON files and a 307/308 response.

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
4. Done — every push to `main` redeploys.

No build step, no environment secrets, no database.

## File layout

```
.
├── api/
│   └── redirect.js          # Vercel serverless redirect handler
├── data/
│   └── links/
│       └── active/          # One JSON file per short link
├── test/
│   └── redirects.test.js    # Unit tests for the redirect logic
├── redirects.config.json    # Fallback destination
├── redirects.js             # Core redirect logic (lookup, normalize, build URL)
├── redirects-loader.js      # Loads link JSON files into an in-memory index
├── vercel.json              # Vercel routing config
├── package.json
├── .gitignore
├── LICENSE
└── README.md
```

## Why no tracking?

This project intentionally has no analytics or tracking integrations. If you
need click counts, point your own analytics tool at the destination URLs or
add a tracking layer in front of `api/redirect.js`.
