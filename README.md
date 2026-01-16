# Link Shortener Agent 🔗🤖

> An AI-powered link management system that rivals Bitly/Dub.sh — with natural language control, GitHub-based storage, and zero database costs.

**Status**: 📋 Planning Phase — See [plan.md](./plan.md) for detailed implementation roadmap

## Vision

Manage shortened links using natural language commands:

```
> You: take this link luma.com and shorten it to luma. add utms because this 
  will be in the newsletter on jan 17, 2026. add a tag for january and newsletter. 
  then create a qr code with a black background and yellow. this link will expire 
  in 2 weeks. put my favicon in the middle of the qr code.

Agent: ✅ Created: go.openhands.dev/luma → https://luma.com
       📱 Generated QR code: go.openhands.dev/qr/luma
       ⏰ Expires: Jan 31, 2026
       🏷️  Tags: january, newsletter
```

## Key Features

- 🎙️ **Natural Language Interface**: Chat with your link shortener in plain English
- 🔐 **GitHub as Database**: Version-controlled, permissioned, free storage
- 🎨 **Custom QR Codes**: Branded QR codes with custom colors and logo overlays
- 🏷️ **Smart Tagging**: Organize and bulk-manage links by tags
- 📊 **UTM Tracking**: Automatic UTM parameter generation and management
- ⏰ **Expiration**: Set links to expire automatically
- 🚀 **Vercel Deployment**: Serverless redirects on go.openhands.dev
- 💰 **100% Free**: No database costs, uses free tiers of GitHub + Vercel
- 🍴 **Fully Forkable**: Deploy your own instance in minutes

## Tech Stack

- **Agent**: OpenHands Agent SDK (BYOK for LLM)
- **Frontend**: Next.js 14 on Vercel
- **Storage**: JSON files in Git
- **CLI**: Python with rich terminal UI
- **QR Codes**: Python qrcode + Pillow

## Quick Start

> Coming soon! See [plan.md](./plan.md) for implementation details.

## For OpenHands Team

This project will be deployed to **go.openhands.dev** and integrated with our existing PostHog analytics.

## Roadmap

- ✅ Phase 0: Planning (You are here)
- 🚧 Phase 1: Core Agent + Basic Links (2-3 days)
- 📋 Phase 2: UTM & Metadata (1-2 days)
- 📋 Phase 3: QR Code Generation (1-2 days)
- 📋 Phase 4: PostHog Analytics (optional, as needed)
- 📋 Phase 5: Documentation & Community Release (as needed)

## Contributing

This project is being actively developed. Contributions welcome once Phase 1-3 are complete!

## License

MIT License (Coming soon)

---

Built with ❤️ by the OpenHands team
