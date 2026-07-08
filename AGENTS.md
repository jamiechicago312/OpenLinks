# Repository memory

> **Repo-specific guard - read first.** This file is for
> `jamiechicago312/OpenLinks` only. Do **not** copy these rules to
> other repositories; they exist because of this repo's specific
> Vercel setup, not as a general policy.

## Author identity (Vercel Hobby limit)

**No exceptions.** Every commit and every PR merge on this repo must be
authored by `Jamie Chicago <87397251+jamiechicago312@users.noreply.github.com>`.

### Why

This Vercel project is on the **Hobby** plan, which does not support
collaborators. Vercel blocks any deployment whose commit author is not
the Vercel account owner, with this exact error:

> "The Deployment was blocked because the commit author does not have
> contributing access to the project on Vercel. Hobby teams do not
> support collaboration."

The same rule applies to all of jamiechicago312's Vercel-Hobby projects
(including `chicago-jamie-portfolio`, `jamierocks606`, and
`jamie-and-matt`). An identical "Author identity" section lives in
each repo's `AGENTS.md`. If you find yourself working across multiple
Jamie Chicago repos, set the author to `Jamie Chicago` before the
first commit in each one.

### Rules for any agent (OpenHands, CI bot, etc.) working in this repo

1. **Never `git commit` as yourself.** Always set the commit author to
   the human owner before committing:
   ```bash
   git config user.name "Jamie Chicago"
   git config user.email "87397251+jamiechicago312@users.noreply.github.com"
   git commit ...
   ```
   Or pass `--author="Jamie Chicago <87397251+jamiechicago312@users.noreply.github.com>"`
   per commit.
2. **Never merge a PR yourself**, even if you have a token that lets
   you. Open the PR as a **draft** and hand it to Jamie to review and
   merge. If a merge is required for the task, ask first.
3. **Never push a tag.** Tagged releases trigger production deploys
   the same way merges do, and the same author rule applies.
4. **If asked to do a release**, walk Jamie through it; do not run
   `gh release create` or `git tag` on your own.
5. The `Co-authored-by: openhands <...>` trailer is fine - Vercel
   checks the **author**, not the co-author trailer.

### Quick check before pushing

```bash
git log -1 --format='%an <%ae>'  # must print: Jamie Chicago <87397251+jamiechicago312@users.noreply.github.com>
```

If it prints anything else, fix the author (`git commit --amend
--reset-author`) before pushing.

## What this is

`jamiechicago312/OpenLinks` - a tiny short-link service. Each short
link is a JSON file under `data/links/active/`, and a single Vercel
serverless function performs a 307/308 redirect to the configured
destination. There is intentionally no UI and no admin panel. Click
notifications are opt-in via Telegram (see Conventions).

## Stack

- Vercel serverless function at `api/redirect.js` (Node.js).
- `redirects.js` - lookup, pathname normalization, destination URL
  building. Pure functions, no I/O.
- `redirects-loader.js` - reads `data/links/active/*.json` at cold
  start and exposes `redirectsBySource` plus `fallbackDestination`.
- `redirects.config.json` - fallback destination. Overridable via the
  `FALLBACK_DESTINATION` env var.
- `vercel.json` - routes non-file paths through the handler using the
  `__oh_redirect_pathname` internal query param, matching the
  filesystem-first pattern.
- Tests: `node --test` (no test framework dependency). Run with
  `npm test`.
- No build step, no framework, no `node_modules` in production.

## Conventions

- **One short link = one JSON file** in `data/links/active/`. The
  public short path is the `slug` field inside the file, not the
  filename - keep both consistent anyway, so anyone browsing the
  directory can guess the slug without opening the file.
- **Never add tracking by default.** The redirect handler is
  side-effect free unless the operator opts in via env vars. No
  analytics calls, no cookies, no logging of referrer / IP / UA in
  the default deployment.
- **Click notifications are opt-in via Telegram.** Setting both
  `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the Vercel project's
  environment variables enables a fire-and-forget POST to the
  Telegram bot API on every click, with city, country, user agent,
  and referer. Without both env vars, no notification fires. The
  notification MUST be fire-and-forget (never `await`, always
  `.catch(() => {})`) - analytics must never block or fail the
  redirect.
- **Use one short link per job application** when tracking
  application engagement. Name files `app-<company>.json` with the
  matching `slug` (e.g. `/app-google`). The path itself tells you
  which application received a click, with no need to disambiguate
  from referer or other signals.
- **Path matching is normalized** in `redirects.js` before lookup, so
  a request to `/Foo/` and `/foo` resolve identically.
- **Status codes are per-link**, not a single global default. Pick 307
  (preserves method) or 308 (permanent, preserves method) deliberately
  in each JSON file.
- The fallback destination in `redirects.config.json` is meant to be
  obvious/placeholder (currently `https://example.com`). Override in
  the Vercel dashboard, do not edit the JSON to point at a real
  destination - it would silently send unmatched traffic somewhere
  unexpected.
- Edit files directly in this repo; no admin/UI exists by design. Push
  to trigger a Vercel deploy.

## Things to watch

- Vercel preview deployments may have Deployment Protection enabled;
  if a preview URL returns a login page, see the `vercel` skill notes
  for the protection-bypass workflow.
- The handler runs on Vercel's default Node runtime, not Edge. Don't
  introduce Node-only APIs that aren't available in `nodejs` runtime
  (most are, but `fs` reads happen at cold start only via
  `redirects-loader.js`).
- Hobby-plan function timeout defaults apply (10s on Hobby). The
  handler is synchronous and finishes in single-digit ms; do not add
  network calls inside it.
- The `data/links/active/` directory must keep a `.gitkeep` placeholder
  so the directory survives empty checkouts. Removing it breaks first
  deploys on a fresh clone.

## Learnings

- `vercel.json` routes non-file paths to `/api/redirect` with the
  original path smuggled in `__oh_redirect_pathname`. The handler must
  strip that query key from the destination's URL before redirecting,
  or it leaks into the `Location` header. This is handled in
  `getIncomingSearchParams`; do not remove that line without testing
  every existing short link.
- `cleanUrls: true` in `vercel.json` means `/foo` resolves before the
  rewrite runs, so a JSON file at `data/links/active/foo.json` will be
  served as a static file if one ever leaks into the deploy - which is
  why `data/` is intentionally not exposed as a public path.