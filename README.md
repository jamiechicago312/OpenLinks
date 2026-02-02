# OpenLinks 🔗🤖

> An AI-powered link management system that rivals Bitly/Dub.sh — with natural language control, GitHub-based storage, and zero database costs.

**Status**: 🚀 **Issue-Triggered Agent Live!** — Create and manage links via GitHub issues

## Vision

Manage shortened links using natural language via **GitHub Issues**:

```
📝 Create an issue:
Title: "Create luma link"
Body: "Shorten luma.com to /luma with newsletter UTMs, expires in 2 weeks"
Label: openlinks

🤖 Agent automatically:
✅ Creates: go.openhands.dev/luma → https://luma.com
✅ Adds UTM parameters: ?utm_source=newsletter
✅ Sets expiration: 2 weeks from now
✅ Commits to repo and deploys to Vercel
✅ Comments back on issue with the link
```

## Key Features

- 🎫 **Issue-Triggered**: Just add the `openlinks` label to any issue
- 🔗 **Link Operations**: Create, update, delete links via natural language
- ⚙️ **Feature Requests**: Agent can implement new features and create PRs
- 🔐 **GitHub as Database**: Version-controlled, permissioned, free storage
- 🏷️ **Smart Tagging**: Organize and bulk-manage links by tags
- 📊 **UTM Tracking**: Automatic UTM parameter generation and management
- ⏰ **Expiration**: Set links to expire automatically with custom redirects
- 🚀 **Vercel Deployment**: Serverless redirects on go.openhands.dev
- 💰 **100% Free**: No database costs, uses free tiers of GitHub + Vercel
- 🍴 **Fully Forkable**: Deploy your own instance in minutes

## How It Works

### 1. Link Operations (via Issues)

Create an issue with natural language and add the `openlinks` label:

**Example 1: Simple Link**
```
Title: "Shorten google.com"
Body: "Create /ggl that redirects to google.com"
```
→ Agent creates the link and comments: `✅ Created: go.openhands.dev/ggl`

**Example 2: Complex Link**
```
Title: "Newsletter link with expiration"
Body: "Take google.com and make it /ggl with newsletter UTMs, 
       expires next week, redirect to homepage after expiration"
```
→ Agent creates link with UTM params, expiration, and fallback redirect

**Example 3: Bulk Delete**
```
Title: "Clean up January links"
Body: "Delete all links tagged with 'january'"
```
→ Agent deletes all matching links

### 2. Feature Requests (via Issues)

Request new features and the agent implements them:

```
Title: "Add QR code generation"
Body: "Add ability to generate QR codes for each link with custom colors"
Label: openlinks
```
→ Agent creates a PR implementing the feature

## Quick Start

### Prerequisites
1. GitHub repository with write access
2. OpenHands API key (get from [OpenHands](https://app.all-hands.dev/))

### Setup (5 minutes)

1. **Clone this repo** (or fork it)
   ```bash
   git clone https://github.com/openhands/openlinks.git
   cd openlinks
   ```

2. **Add GitHub Secret**
   - Go to Settings → Secrets and variables → Actions → Secrets
   - Add `LLM_API_KEY` with your OpenHands API key (starts with `sk-oh-...`)

3. **Optional: Configure LLM Model**
   - Go to Settings → Secrets and variables → Actions → Variables
   - Add `LLM_MODEL` if you want to override the default
   - Default: `claude-sonnet-4-5-20250929`
   - Other options: `gpt-4o`, `gpt-4-turbo`, etc.

4. **Enable GitHub Actions**
   - Go to Actions tab and enable workflows
   - Ensure Actions have write permissions (Settings → Actions → General → Workflow permissions)

5. **Create a test issue**
   ```
   Title: "Test link"
   Body: "Create /test that goes to example.com"
   Label: openlinks
   ```

6. **Watch the magic happen!** 🎉
   - Agent runs automatically
   - Creates the link
   - Comments back with the result

## Usage Examples

### Create a Link
```
Title: "Shorten luma.com"
Body: "Create /luma → luma.com with newsletter UTMs"
Label: openlinks
```

### Create Link with Expiration
```
Title: "Temporary promo link"
Body: "Create /promo → example.com/sale, expires in 1 week, 
       redirect to homepage after"
Label: openlinks
```

### Update a Link
```
Title: "Update docs link"
Body: "Update /docs to point to docs.openhands.dev"
Label: openlinks
```

### Delete Links
```
Title: "Delete single link"
Body: "Delete /old-link"
Label: openlinks
```

### Bulk Delete
```
Title: "Clean up campaign links"
Body: "Delete all links tagged 'campaign-2024'"
Label: openlinks
```

### List Links
```
Title: "Show newsletter links"
Body: "List all links with tag newsletter"
Label: openlinks
```

## Tech Stack

- **Agent**: OpenHands Agent SDK (BYOK for LLM)
- **Trigger**: GitHub Actions (issue labels)
- **Frontend**: Next.js 14 on Vercel (coming soon)
- **Storage**: JSON files in Git
- **Python**: Link management utilities
- **LLM**: OpenAI, Anthropic, or OpenHands models

## For OpenHands Team

This project will be deployed to **go.openhands.dev** and integrated with our existing PostHog analytics.

## Roadmap

- ✅ **Phase 0**: Planning & Architecture
- ✅ **Phase 1**: Issue-Triggered Agent (Link Operations)
- 📋 **Phase 2**: Vercel Deployment (Next.js app for redirects)
- 📋 **Phase 3**: QR Code Generation
- 📋 **Phase 4**: PostHog Analytics Integration
- 📋 **Phase 5**: Documentation & Community Release

## Architecture

```
┌─────────────────────┐
│  GitHub Issue       │
│  + "openlinks"      │
│     label           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  GitHub Actions     │
│  Workflow           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  OpenLinks Agent    │
│  - Classify request │
│  - Execute ops      │
│  - Comment back     │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐  ┌────────┐
│ LINK   │  │FEATURE │
│ OPS    │  │REQUEST │
└────┬───┘  └───┬────┘
     │          │
     ▼          ▼
┌─────────────────────┐
│  data/links/        │
│  active/*.json      │
└─────────────────────┘
```

## Troubleshooting

### Agent not running?
- Check that the `openlinks` label exists and is applied to the issue
- Verify `LLM_API_KEY` is set in repository secrets
- Check Actions tab for workflow runs and error logs

### Link not created?
- Check the agent's comment on the issue for error details
- Ensure the URL is valid (includes `http://` or `https://`)
- Verify slug is alphanumeric (letters, numbers, hyphens, underscores only)

### Permission errors?
- Go to Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests"

### LLM errors?
- Verify your API key is valid
- Check your LLM provider's rate limits
- Try a different model via `LLM_MODEL` variable

## Local Development

Test the agent locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LLM_API_KEY="your-key"
export GITHUB_TOKEN="your-token"
export GITHUB_REPOSITORY="owner/repo"
export ISSUE_NUMBER="1"
export ISSUE_TITLE="Test link"
export ISSUE_BODY="Create /test → example.com"

# Run the agent
python scripts/openlinks_agent.py
```

Test link management utilities:

```bash
# Create a link
python scripts/link_manager.py create test https://example.com

# Read a link
python scripts/link_manager.py read test

# List all links
python scripts/link_manager.py list

# Delete a link
python scripts/link_manager.py delete test
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a PR

## License

MIT License

---

Built with ❤️ by the OpenHands team
