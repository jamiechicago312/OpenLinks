# Link Shortener Agent - Implementation Plan

> **Vision**: A free, open-source, AI-powered link management system that rivals Bitly/Dub.sh with natural language control, GitHub-based storage, and zero database costs.

## 🎯 Core Philosophy

- **GitHub is the database**: Links stored in JSON files, version-controlled, with built-in permissions
- **Agent SDK as interface**: Natural language commands for technical AND non-technical users  
- **Vercel for infrastructure**: Free hosting, automatic deployments, serverless redirects
- **Fully forkable**: Others can deploy their own instance in minutes

## 🏢 OpenHands Deployment Specifics

- **Primary Domain**: openhands.dev
- **Shortener Domain**: go.openhands.dev (deployed on Vercel)
- **Team Size**: 3-5 users, primarily 1 power user, low concurrency
- **Usage Pattern**: Few times per week, real production links
- **LLM Config**: Bring-your-own-key (BYOK) like OpenHands Cloud/CLI, including OpenHands-provided models (GPT-4o expected)

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    USER TERMINAL                             │
│  $ go-link "shorten luma.com to /luma with utm tags"        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              OPENHANDS AGENT (Local)                         │
│  - Parses natural language                                   │
│  - Calls appropriate tools                                   │
│  - Confirms destructive actions                              │
│  - BYOK: OpenHands models, OpenAI, Anthropic, etc.          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    AGENT TOOLS                               │
│  create_link()  | delete_links() | generate_qr()             │
│  update_link()  | list_links()   | bulk_operations()         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                 DATA LAYER (GitHub)                          │
│  /data/links/                                                │
│    ├── active/         - Current links (JSON per link)       │
│    ├── archived/       - Expired/deleted links               │
│    └── qr-codes/       - Generated QR images                 │
│                                                               │
│  Agent commits & pushes → triggers Vercel deployment         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼ (Webhook triggers deploy)
┌──────────────────────────────────────────────────────────────┐
│              VERCEL DEPLOYMENT (go.openhands.dev)            │
│  Next.js App Router                                          │
│  - /[slug] → redirect handler (302)                          │
│  - /qr/[slug] → serve QR code image                          │
│  - / → redirect to openhands.dev                             │
│  - Reads from /data/links/active/ at request time            │
│  - Optional: PostHog analytics (Phase 4)                     │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
          go.openhands.dev/luma → luma.com?utm_source=newsletter
```

---

## 📦 Repository Structure

```
link-shortener-agent/
├── README.md                      # Setup, usage, fork instructions
├── plan.md                        # This file
├── package.json                   # Node dependencies (Vercel app)
├── requirements.txt               # Python dependencies (Agent CLI)
├── pyproject.toml                 # Python project config
│
├── agent/                         # Agent SDK implementation
│   ├── __init__.py
│   ├── main.py                    # Entry point: `go-link` CLI
│   ├── agent.py                   # Agent SDK setup & configuration
│   ├── config.py                  # LLM configuration (BYOK)
│   ├── tools/                     # Agent tool definitions
│   │   ├── __init__.py
│   │   ├── link_tools.py          # create, update, delete, list
│   │   ├── qr_tools.py            # generate QR codes
│   │   ├── bulk_tools.py          # bulk operations (delete by tag)
│   │   └── git_tools.py           # commit & push to GitHub
│   └── utils/
│       ├── link_manager.py        # Read/write individual link files
│       ├── qr_generator.py        # QR code creation with styling
│       ├── validators.py          # URL, slug, expiration validation
│       └── git_helper.py          # Git operations wrapper
│
├── app/                           # Next.js app for redirects (root level)
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Root: redirect to openhands.dev
│   ├── [slug]/
│   │   └── route.ts               # Dynamic redirect handler
│   └── qr/
│       └── [slug]/
│           └── route.ts           # Serve QR images
│
├── lib/                           # Next.js utilities
│   ├── links.ts                   # Load all links from data/
│   ├── expiration.ts              # Check expiration logic
│   └── analytics.ts               # PostHog integration (Phase 4)
│
├── public/
│   └── favicon.png                # OpenHands favicon for QR overlay
│
├── data/                          # Data files (committed to repo)
│   ├── config.json                # Base URL, primary domain config
│   ├── links/
│   │   ├── active/                # Active links (one JSON per link)
│   │   │   ├── luma.json          # Example: slug "luma"
│   │   │   ├── docs.json          # Example: slug "docs"
│   │   │   └── .gitkeep
│   │   ├── archived/              # Expired/deleted links
│   │   │   └── .gitkeep
│   │   └── qr-codes/              # Generated QR images
│   │       ├── luma.png
│   │       └── .gitkeep
│
├── scripts/
│   └── setup.sh                   # One-command setup for forks
│
├── .env.example                   # Environment variables template
├── .gitignore
├── next.config.js                 # Next.js configuration
└── vercel.json                    # Vercel deployment config
```

---

## 📋 Data Schema

### Individual Link File (`data/links/active/{slug}.json`)
```json
{
  "id": "luma_20260117_abc123",
  "slug": "luma",
  "destination": "https://luma.com",
  "created_at": "2026-01-17T00:00:00Z",
  "created_by": "username",
  "expires_at": "2026-01-31T00:00:00Z",
  "tags": ["january", "newsletter"],
  "utm_params": {
    "utm_source": "newsletter",
    "utm_medium": "email",
    "utm_campaign": "jan-2026"
  },
  "qr_config": {
    "enabled": true,
    "bg_color": "#000000",
    "fg_color": "#FFFF00",
    "has_logo": true,
    "file_path": "data/links/qr-codes/luma.png"
  },
  "metadata": {
    "description": "Luma calendar link for newsletter",
    "last_modified": "2026-01-17T00:00:00Z"
  }
}
```

### Configuration File (`data/config.json`)
```json
{
  "base_url": "https://go.openhands.dev",
  "primary_domain": "https://openhands.dev",
  "default_utm_medium": "link",
  "default_expiration_days": null,
  "qr_defaults": {
    "bg_color": "#FFFFFF",
    "fg_color": "#000000",
    "include_logo": true,
    "error_correction": "H"
  }
}
```

---

## 🚀 PHASE 1-3: Complete Feature Implementation

> **Build Strategy**: Implement all core features (link management + UTMs/tags + QR codes) in rapid succession across 3 sub-phases. Each sub-phase builds on the previous.

---

## 🔧 PHASE 1: Core Agent + Basic Link Management

**Goal**: Terminal agent that can create, list, and delete links with Vercel redirects working

**Time Estimate**: 2-3 days

### 1.1 Repository & Data Setup (1 hour)

**Tasks:**
- [ ] Create GitHub repository: `openhands/link-shortener-agent`
- [ ] Initialize directory structure:
  ```bash
  mkdir -p data/links/{active,archived,qr-codes}
  mkdir -p agent/{tools,utils}
  mkdir -p app/{[slug],qr/[slug]}
  mkdir -p lib
  touch data/links/active/.gitkeep
  touch data/links/archived/.gitkeep
  touch data/links/qr-codes/.gitkeep
  ```
- [ ] Create `data/config.json` with go.openhands.dev settings
- [ ] Add `.gitignore` (node_modules, .env, __pycache__, etc.)
- [ ] Initialize git and push to GitHub

**Files to Create:**
```json
// data/config.json
{
  "base_url": "https://go.openhands.dev",
  "primary_domain": "https://openhands.dev",
  "default_utm_medium": "link",
  "default_expiration_days": null,
  "qr_defaults": {
    "bg_color": "#FFFFFF",
    "fg_color": "#000000",
    "include_logo": true,
    "error_correction": "H"
  }
}
```

---

### 1.2 Python Agent Foundation (3-4 hours)

**Tasks:**
- [ ] **Install dependencies** (`requirements.txt`):
  ```txt
  openhands-agent-sdk>=0.1.0
  GitPython>=3.1.0
  python-dateutil>=2.8.0
  rich>=13.0.0
  pydantic>=2.0.0
  ```

- [ ] **`agent/config.py`** - LLM configuration (BYOK)
  ```python
  # Support OpenHands-provided models + BYOK
  # Environment variables: LLM_PROVIDER, LLM_API_KEY, LLM_BASE_URL
  # Should mirror OpenHands Cloud/CLI config style
  ```
  - [ ] Load from environment variables
  - [ ] Support: OpenHands models, OpenAI, Anthropic, local LLMs
  - [ ] Default to GPT-4o if OpenAI key provided

- [ ] **`agent/agent.py`** - Agent SDK initialization
  ```python
  # Initialize agent with configured LLM
  # Define system prompt for link management context
  # Register all tools
  ```
  - [ ] System prompt explaining link shortener purpose
  - [ ] Agent personality: helpful, confirms destructive actions
  - [ ] Tool registration

- [ ] **`agent/main.py`** - CLI entry point
  ```python
  # Rich console for pretty output
  # Conversation loop
  # Handle Ctrl+C gracefully
  # Show link previews with rich tables
  ```
  - [ ] Welcome message with ASCII art (optional)
  - [ ] Interactive prompt: `> You: `
  - [ ] Pretty-print agent responses
  - [ ] Show link tables with `rich.table`

- [ ] **`agent/utils/validators.py`** - Input validation
  - [ ] Validate URLs (must be valid http/https)
  - [ ] Validate slugs (alphanumeric + dash, 1-50 chars, no reserved words)
  - [ ] Reserved slugs: `api`, `qr`, `admin`, `_next`, etc.
  - [ ] Validate expiration dates (future only)
  - [ ] Validate colors (hex format for QR)

- [ ] **`agent/utils/git_helper.py`** - Git operations
  ```python
  def commit_and_push(message: str, files: list[str]) -> bool:
      """Commit specific files and push to GitHub"""
      # Pull latest changes first (avoid conflicts)
      # Stage files
      # Commit with message
      # Push to origin/main
      # Return success/failure
  ```

- [ ] **`agent/utils/link_manager.py`** - File operations
  ```python
  def create_link_file(slug: str, data: dict) -> str:
      """Write data/links/active/{slug}.json"""
  
  def read_link_file(slug: str) -> dict | None:
      """Read link JSON, return None if not exists"""
  
  def delete_link_file(slug: str) -> bool:
      """Move to archived/ with timestamp"""
  
  def list_all_links(tags: list[str] = None) -> list[dict]:
      """Load all links from active/, optionally filter by tags"""
  
  def slug_exists(slug: str) -> bool:
      """Check if slug already used"""
  ```

---

### 1.3 Basic Agent Tools (2-3 hours)

**Tool 1: `create_link`**

File: `agent/tools/link_tools.py`

```python
from openhands_sdk import tool

@tool
def create_link(
    url: str,
    slug: str,
    tags: list[str] = None,
    utm_params: dict = None,
    expiration_days: int = None,
    description: str = ""
) -> str:
    """
    Create a new shortened link.
    
    Args:
        url: Destination URL (must include http:// or https://)
        slug: Short identifier for the link (e.g., "luma")
        tags: Optional list of tags for organization (e.g., ["newsletter", "january"])
        utm_params: Optional UTM parameters dict (e.g., {"utm_source": "newsletter"})
        expiration_days: Optional number of days until link expires
        description: Optional description of the link purpose
    
    Returns:
        Success message with full shortened URL
    """
    # 1. Validate inputs
    # 2. Check slug uniqueness
    # 3. Generate link ID
    # 4. Calculate expiration date if provided
    # 5. Build JSON data structure
    # 6. Write to data/links/active/{slug}.json
    # 7. Git commit & push
    # 8. Return formatted success message with go.openhands.dev/{slug}
```

**Implementation Checklist:**
- [ ] Validate URL format (add https:// if missing)
- [ ] Validate slug (no special chars, check reserved words)
- [ ] Check slug doesn't exist already
- [ ] Generate unique ID: `{slug}_{timestamp}_{random}`
- [ ] Set `created_at` to current UTC time
- [ ] Calculate `expires_at` if expiration_days provided
- [ ] Write JSON file with pretty formatting
- [ ] Commit with message: `"Add link: {slug} → {url}"`
- [ ] Push to GitHub
- [ ] Return: `"✅ Created: go.openhands.dev/{slug} → {url}"`

---

**Tool 2: `list_links`**

```python
@tool
def list_links(
    tags: list[str] = None,
    limit: int = 50,
    show_expired: bool = False
) -> str:
    """
    List all active links, optionally filtered by tags.
    
    Args:
        tags: Filter by these tags (AND logic)
        limit: Maximum number of links to return
        show_expired: Include expired links in results
    
    Returns:
        Formatted table of links
    """
    # 1. Load all link files from data/links/active/
    # 2. Filter by tags if provided
    # 3. Filter out expired if show_expired=False
    # 4. Sort by created_at (newest first)
    # 5. Format as rich table
    # 6. Return table string
```

**Implementation Checklist:**
- [ ] Load all JSON files from active directory
- [ ] Filter by tags (all tags must match)
- [ ] Check expiration dates
- [ ] Sort by creation date
- [ ] Format as rich table with columns: Slug, Destination, Tags, Expires, Created
- [ ] Truncate long URLs (show first 50 chars)
- [ ] Return formatted string

---

**Tool 3: `delete_link`**

```python
@tool
def delete_link(slug: str) -> str:
    """
    Delete (archive) a shortened link.
    
    Args:
        slug: The slug to delete
    
    Returns:
        Success message
    """
    # 1. Check if link exists
    # 2. Load link data
    # 3. Move to archived/ with timestamp suffix
    # 4. Delete QR code if exists
    # 5. Git commit & push
    # 6. Return success message
```

**Implementation Checklist:**
- [ ] Check if `data/links/active/{slug}.json` exists
- [ ] If not found, return friendly error
- [ ] Move to `data/links/archived/{slug}_{timestamp}.json`
- [ ] If QR code exists, move to archived too
- [ ] Commit with message: `"Delete link: {slug}"`
- [ ] Push to GitHub
- [ ] Return: `"✅ Deleted link: {slug}"`

---

### 1.4 Vercel Redirect App (3-4 hours)

**Tasks:**

- [ ] **Initialize Next.js project**
  ```bash
  npx create-next-app@latest . --typescript --app --no-src-dir
  ```

- [ ] **Install dependencies** (`package.json`):
  ```json
  {
    "dependencies": {
      "next": "^14.0.0",
      "react": "^18.0.0",
      "react-dom": "^18.0.0"
    }
  }
  ```

- [ ] **`lib/links.ts`** - Link loading utility
  ```typescript
  import fs from 'fs';
  import path from 'path';
  
  export interface Link {
    id: string;
    slug: string;
    destination: string;
    created_at: string;
    expires_at: string | null;
    tags: string[];
    utm_params: Record<string, string>;
    qr_config: {
      enabled: boolean;
      bg_color: string;
      fg_color: string;
      has_logo: boolean;
      file_path: string;
    };
  }
  
  export function getAllLinks(): Map<string, Link> {
    // Read all files from data/links/active/
    // Parse JSON
    // Return Map of slug -> link data
  }
  
  export function getLink(slug: string): Link | null {
    // Read data/links/active/{slug}.json
    // Return parsed data or null
  }
  
  export function buildDestinationUrl(link: Link): string {
    // Add UTM params to destination URL
    // Handle existing query params
    // Return full URL string
  }
  ```

- [ ] **`lib/expiration.ts`** - Expiration checking
  ```typescript
  export function isExpired(expiresAt: string | null): boolean {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  }
  ```

- [ ] **`app/[slug]/route.ts`** - Dynamic redirect handler
  ```typescript
  import { getLink, buildDestinationUrl } from '@/lib/links';
  import { isExpired } from '@/lib/expiration';
  import { NextRequest, NextResponse } from 'next/server';
  
  export async function GET(
    request: NextRequest,
    { params }: { params: { slug: string } }
  ) {
    const slug = params.slug;
    const link = getLink(slug);
    
    // If link doesn't exist, redirect to primary domain
    if (!link) {
      return NextResponse.redirect('https://openhands.dev', 302);
    }
    
    // If expired, redirect to primary domain
    if (isExpired(link.expires_at)) {
      return NextResponse.redirect('https://openhands.dev', 302);
    }
    
    // Build full URL with UTM params
    const destination = buildDestinationUrl(link);
    
    // Redirect
    return NextResponse.redirect(destination, 302);
  }
  ```

- [ ] **`app/page.tsx`** - Root page (redirect to primary domain)
  ```typescript
  import { redirect } from 'next/navigation';
  
  export default function Home() {
    redirect('https://openhands.dev');
  }
  ```

- [ ] **`app/layout.tsx`** - Root layout
  ```typescript
  export const metadata = {
    title: 'OpenHands Link Shortener',
    description: 'Managed by AI agent',
  };
  
  export default function RootLayout({ children }) {
    return (
      <html lang="en">
        <body>{children}</body>
      </html>
    );
  }
  ```

- [ ] **`next.config.js`** - Configuration
  ```javascript
  /** @type {import('next').NextConfig} */
  const nextConfig = {
    // Any special config needed
  };
  
  module.exports = nextConfig;
  ```

- [ ] **Deploy to Vercel**
  - [ ] Connect GitHub repo
  - [ ] Set root directory (if needed)
  - [ ] Deploy
  - [ ] Note deployment URL

- [ ] **Configure custom domain**
  - [ ] In Vercel: Add domain `go.openhands.dev`
  - [ ] Copy DNS instructions
  - [ ] Add CNAME record in domain registrar
  - [ ] Wait for verification (may take a few minutes)
  - [ ] Test: https://go.openhands.dev should redirect to openhands.dev

---

### 1.5 End-to-End Testing (1 hour)

**Test Scenarios:**

- [ ] **Test 1: Create link via agent**
  ```
  > You: shorten google.com to /g
  Agent: [Creates link]
  Expected: data/links/active/g.json exists
  Expected: Git commit pushed
  Expected: Agent says "✅ Created: go.openhands.dev/g → https://google.com"
  ```

- [ ] **Test 2: Verify redirect**
  ```
  Visit: https://go.openhands.dev/g
  Expected: Redirects to https://google.com
  Expected: Status code 302
  ```

- [ ] **Test 3: List links**
  ```
  > You: show me all links
  Agent: [Displays table]
  Expected: Table shows "g" link
  ```

- [ ] **Test 4: Delete link**
  ```
  > You: delete /g
  Agent: [Deletes link]
  Expected: data/links/active/g.json is gone
  Expected: data/links/archived/g_[timestamp].json exists
  Expected: Visiting go.openhands.dev/g redirects to openhands.dev
  ```

- [ ] **Test 5: Error handling**
  ```
  > You: create link with slug "g" again
  Expected: Agent says slug already exists
  ```

**Success Criteria:**
✅ User can type "shorten google.com to /g" and it works end-to-end
✅ Vercel redirects work within 10 seconds of push
✅ Agent provides clear feedback for all operations
✅ Git commits are clean and descriptive

---

---

## 🎨 PHASE 2: UTM Parameters, Tags & Advanced Metadata

**Goal**: Full metadata support (tags, UTM params, expiration) with natural language parsing

**Time Estimate**: 1-2 days

### 2.1 Enhanced Natural Language Parsing (2-3 hours)

**Tasks:**

- [ ] **`agent/utils/nlp_helpers.py`** - Natural language parsing utilities
  ```python
  from datetime import datetime, timedelta
  from dateutil import parser as date_parser
  
  def parse_utm_intent(text: str) -> dict:
      """
      Extract UTM parameters from natural language.
      
      Examples:
        "for newsletter on jan 17" → {utm_source: newsletter, utm_campaign: jan-17-2026}
        "utm_source=twitter utm_medium=social" → {utm_source: twitter, utm_medium: social}
        "because this will be in the newsletter" → {utm_source: newsletter}
      """
      # Pattern match for explicit utm_* parameters
      # Pattern match for intent ("for newsletter", "in the blog")
      # Auto-generate campaign name from date if mentioned
      # Return dict of UTM params
  
  def parse_tags(text: str) -> list[str]:
      """
      Extract tags from natural language.
      
      Examples:
        "tag this as january and newsletter" → ["january", "newsletter"]
        "add tags: conference, 2026" → ["conference", "2026"]
        "tags: january, newsletter" → ["january", "newsletter"]
      """
      # Pattern match for "tag(s)" followed by list
      # Clean and normalize tags (lowercase, no special chars)
      # Return list of tags
  
  def parse_expiration(text: str, reference_date: datetime = None) -> datetime | None:
      """
      Extract expiration date from natural language.
      
      Examples:
        "expires in 2 weeks" → datetime 14 days from now
        "expire in 1 month" → datetime 30 days from now  
        "expires on Jan 31 2026" → datetime(2026, 1, 31)
        "this link will expire in 2 weeks" → datetime 14 days from now
      """
      # Pattern match for "expires in X days/weeks/months"
      # Pattern match for "on [date]"
      # Calculate relative dates
      # Parse absolute dates
      # Return datetime or None
  ```

**Implementation Checklist:**
- [ ] Regex patterns for UTM extraction (explicit and intent-based)
- [ ] UTM intent mapping: "newsletter" → utm_source=newsletter, etc.
- [ ] Auto-generate utm_campaign from date context
- [ ] Tag extraction patterns (multiple formats)
- [ ] Relative date parsing (days, weeks, months)
- [ ] Absolute date parsing (various formats via dateutil)
- [ ] Unit tests for parsing functions

---

### 2.2 Enhanced `create_link` Tool (1-2 hours)

**Tasks:**

- [ ] **Update `agent/tools/link_tools.py`** to use NLP parsing
  ```python
  @tool
  def create_link(
      url: str,
      slug: str,
      prompt_context: str = "",  # NEW: full user prompt for context parsing
      tags: list[str] = None,
      utm_params: dict = None,
      expiration_days: int = None,
      description: str = ""
  ) -> str:
      """
      Create a new shortened link with intelligent parsing.
      
      Now supports natural language like:
      "shorten luma.com to /luma, tag as january and newsletter, 
       add utms for newsletter on jan 17, expires in 2 weeks"
      """
      # If prompt_context provided, parse it for implicit params
      if prompt_context and not tags:
          tags = parse_tags(prompt_context)
      
      if prompt_context and not utm_params:
          utm_params = parse_utm_intent(prompt_context)
      
      if prompt_context and not expiration_days:
          exp_date = parse_expiration(prompt_context)
          if exp_date:
              expiration_days = (exp_date - datetime.now()).days
      
      # Rest of implementation stays the same
  ```

**Agent Configuration:**
- [ ] Update system prompt to pass full user message as `prompt_context`
- [ ] Teach agent to call create_link with full context
- [ ] Test with natural language commands

---

### 2.3 Link Update Tool (2 hours)

**Tool: `update_link`**

File: `agent/tools/link_tools.py`

```python
@tool
def update_link(
    slug: str,
    new_destination: str = None,
    add_tags: list[str] = None,
    remove_tags: list[str] = None,
    utm_params: dict = None,
    expiration_days: int = None,
    description: str = None
) -> str:
    """
    Update an existing link's properties.
    
    Args:
        slug: The link to update
        new_destination: Change destination URL
        add_tags: Tags to add (preserves existing)
        remove_tags: Tags to remove
        utm_params: Replace UTM params (merges with existing)
        expiration_days: Set new expiration (days from now, or None to remove)
        description: Update description
    
    Returns:
        Success message with changes summary
    """
    # 1. Load existing link
    # 2. Apply updates to fields
    # 3. Merge tags (add - remove)
    # 4. Merge UTM params (update existing keys)
    # 5. Update last_modified timestamp
    # 6. Write back to file
    # 7. Git commit & push
    # 8. Return summary of changes
```

**Implementation Checklist:**
- [ ] Load existing link file
- [ ] Validate link exists (error if not)
- [ ] Apply each update parameter if provided
- [ ] Merge tags (union for add, difference for remove)
- [ ] Merge UTM params (dict update)
- [ ] Update `last_modified` timestamp
- [ ] Write back to same file
- [ ] Commit with message: `"Update link: {slug} ({changes})"`
- [ ] Return formatted change summary

**Example Usage:**
```
> You: update /luma to expire in 1 week
Agent: ✅ Updated luma: expires_at → 2026-01-24

> You: add tag "featured" to /luma
Agent: ✅ Updated luma: tags → ["january", "newsletter", "featured"]
```

---

### 2.4 Bulk Operations Tools (2-3 hours)

**Tool 1: `delete_links_by_tag`**

```python
@tool
def delete_links_by_tag(tag: str, auto_confirm: bool = False) -> str:
    """
    Delete all links with a specific tag.
    
    Args:
        tag: Tag to filter by
        auto_confirm: Skip confirmation (dangerous!)
    
    Returns:
        Success message with count deleted
    """
    # 1. Find all links with tag
    # 2. Show count and list of slugs
    # 3. If not auto_confirm, ask agent to confirm
    # 4. Archive each link
    # 5. Git commit & push
    # 6. Return success message
```

**Tool 2: `bulk_update_links`**

```python
@tool
def bulk_update_links(
    filter_tags: list[str] = None,
    filter_expired: bool = False,
    new_destination: str = None,
    add_tags: list[str] = None,
    new_expiration_days: int = None
) -> str:
    """
    Update multiple links at once.
    
    Args:
        filter_tags: Only update links with these tags (AND logic)
        filter_expired: Only update expired links
        new_destination: Set all to redirect here (e.g., landing page)
        add_tags: Add these tags to all matching links
        new_expiration_days: Set new expiration for all
    
    Returns:
        Success message with count updated
    """
    # 1. Find all matching links
    # 2. Show count and preview
    # 3. Ask for confirmation
    # 4. Update each link
    # 5. Git commit & push
    # 6. Return summary
```

**Implementation Checklist:**
- [ ] Implement `delete_links_by_tag`
- [ ] Add confirmation prompt in agent prompt
- [ ] Implement `bulk_update_links`
- [ ] Show preview of affected links before execution
- [ ] Handle errors gracefully (partial failures)
- [ ] Test with various filters

**Example Usage:**
```
> You: delete all links with tag conference-2026
Agent: Found 47 links with tag "conference-2026":
       - /conf-booth
       - /conf-schedule
       ...
       Proceed with deletion? (yes/no)
You: yes
Agent: ✅ Deleted 47 links with tag "conference-2026"

> You: make all old links redirect to the main landing page
Agent: Found 23 expired links. Update all to redirect to openhands.dev? (yes/no)
You: yes
Agent: ✅ Updated 23 links to redirect to https://openhands.dev
```

---

### 2.5 Vercel UTM Handling (1 hour)

**Tasks:**

- [ ] **Update `lib/links.ts`** - `buildDestinationUrl` function
  ```typescript
  export function buildDestinationUrl(link: Link): string {
    const url = new URL(link.destination);
    
    // Add UTM parameters from link config
    if (link.utm_params) {
      Object.entries(link.utm_params).forEach(([key, value]) => {
        // Don't override existing params in destination URL
        if (!url.searchParams.has(key)) {
          url.searchParams.set(key, value);
        }
      });
    }
    
    return url.toString();
  }
  ```

**Implementation Checklist:**
- [ ] Parse destination URL
- [ ] Append UTM params as query string
- [ ] Handle existing query params (don't override)
- [ ] Handle malformed URLs gracefully
- [ ] Test with various URL formats

---

### 2.6 Testing (1 hour)

**Test Scenarios:**

- [ ] **Test 1: Full natural language command**
  ```
  > You: take this link luma.com and shorten it to luma. add utms because this will be in the newsletter on jan 17, 2026. add a tag for january and newsletter. this link will expire in 2 weeks.
  
  Expected: Link created with:
    - slug: luma
    - destination: https://luma.com
    - tags: ["january", "newsletter"]
    - utm_params: {utm_source: "newsletter", utm_campaign: "jan-17-2026"}
    - expires_at: 2026-01-31
  ```

- [ ] **Test 2: UTM parameters in redirect**
  ```
  Visit: https://go.openhands.dev/luma
  Expected: Redirects to https://luma.com?utm_source=newsletter&utm_campaign=jan-17-2026
  ```

- [ ] **Test 3: Update link**
  ```
  > You: extend expiration of /luma by 1 week
  Agent: ✅ Updated luma: expires_at → 2026-02-07
  ```

- [ ] **Test 4: Bulk delete**
  ```
  > You: delete all links tagged test
  Agent: Found 3 links. Proceed? (yes/no)
  You: yes
  Agent: ✅ Deleted 3 links
  ```

**Success Criteria:**
✅ Full natural language command from example works perfectly
✅ UTM params appear in redirected URLs
✅ Bulk operations work reliably
✅ Agent confirms destructive actions

---

---

## 🖼️ PHASE 3: QR Code Generation with Branding

**Goal**: Generate beautiful, scannable QR codes with custom colors and logo overlay

**Time Estimate**: 1-2 days

### 3.1 QR Code Generation Utility (2-3 hours)

**Tasks:**

- [ ] **Install dependencies** (add to `requirements.txt`):
  ```txt
  qrcode[pil]>=7.4.0
  Pillow>=10.0.0
  ```

- [ ] **`agent/utils/qr_generator.py`** - QR code creation with styling
  ```python
  from qrcode import QRCode, constants
  from PIL import Image, ImageDraw
  import os
  
  def generate_qr_code(
      url: str,
      slug: str,
      bg_color: str = "#FFFFFF",
      fg_color: str = "#000000",
      include_logo: bool = True,
      logo_path: str = "public/favicon.png",
      output_path: str = None
  ) -> str:
      """
      Generate QR code with custom styling and optional logo overlay.
      
      Args:
          url: Full URL to encode (e.g., https://go.openhands.dev/luma)
          slug: Slug for filename
          bg_color: Background color (hex)
          fg_color: Foreground color (hex)
          include_logo: Whether to overlay logo in center
          logo_path: Path to logo file
          output_path: Where to save (default: data/links/qr-codes/{slug}.png)
      
      Returns:
          Path to generated QR code image
      """
      # 1. Create QR code with error correction level H (30%)
      qr = QRCode(
          version=1,  # Auto size
          error_correction=constants.ERROR_CORRECT_H,  # Highest (30%)
          box_size=10,
          border=4,
      )
      qr.add_data(url)
      qr.make(fit=True)
      
      # 2. Generate image with custom colors
      qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color)
      qr_img = qr_img.convert("RGB")
      
      # 3. Overlay logo if requested
      if include_logo and os.path.exists(logo_path):
          logo = Image.open(logo_path)
          
          # Calculate logo size (15% of QR code size)
          qr_width, qr_height = qr_img.size
          logo_size = int(min(qr_width, qr_height) * 0.15)
          
          # Resize logo maintaining aspect ratio
          logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
          
          # Add white border around logo for better scanning
          border_size = 10
          logo_with_border = Image.new(
              'RGB',
              (logo.size[0] + border_size*2, logo.size[1] + border_size*2),
              bg_color
          )
          logo_with_border.paste(
              logo,
              (border_size, border_size),
              logo if logo.mode == 'RGBA' else None
          )
          
          # Paste logo in center of QR code
          logo_pos = (
              (qr_width - logo_with_border.size[0]) // 2,
              (qr_height - logo_with_border.size[1]) // 2
          )
          qr_img.paste(logo_with_border, logo_pos)
      
      # 4. Save to output path
      if not output_path:
          output_path = f"data/links/qr-codes/{slug}.png"
      
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      qr_img.save(output_path)
      
      return output_path
  
  def validate_qr_colors(bg_color: str, fg_color: str) -> bool:
      """
      Validate that QR code colors have sufficient contrast.
      
      Returns:
          True if colors are valid and have good contrast
      """
      # Check hex format
      # Calculate contrast ratio
      # Warn if contrast is low (may not scan well)
      pass
  ```

**Implementation Checklist:**
- [ ] QR code generation with high error correction
- [ ] Custom color support (convert hex to RGB)
- [ ] Logo loading and resizing
- [ ] Logo border/padding for scanability
- [ ] Center positioning calculation
- [ ] File saving with proper paths
- [ ] Color contrast validation
- [ ] Error handling for missing logo

---

### 3.2 QR Code Agent Tool (1-2 hours)

**Tool: `generate_qr_code`**

File: `agent/tools/qr_tools.py`

```python
from openhands_sdk import tool
from ..utils.qr_generator import generate_qr_code as create_qr
from ..utils.link_manager import read_link_file, update_link_file
from ..utils.git_helper import commit_and_push
import json

@tool
def generate_qr_code(
    slug: str,
    bg_color: str = "#FFFFFF",
    fg_color: str = "#000000",
    include_logo: bool = True,
    regenerate: bool = False
) -> str:
    """
    Generate a QR code for an existing shortened link.
    
    Args:
        slug: The link slug to generate QR for
        bg_color: Background color in hex (e.g., "#000000" for black)
        fg_color: Foreground color in hex (e.g., "#FFFF00" for yellow)
        include_logo: Whether to include OpenHands logo in center
        regenerate: Regenerate even if QR already exists
    
    Returns:
        Success message with QR code path
    """
    # 1. Load link file
    link_data = read_link_file(slug)
    if not link_data:
        return f"❌ Link '{slug}' not found"
    
    # 2. Check if QR already exists
    if link_data.get('qr_config', {}).get('enabled') and not regenerate:
        return f"⚠️  QR code already exists for {slug}. Use regenerate=True to recreate."
    
    # 3. Build full URL
    config = json.load(open('data/config.json'))
    full_url = f"{config['base_url']}/{slug}"
    
    # 4. Generate QR code
    try:
        qr_path = create_qr(
            url=full_url,
            slug=slug,
            bg_color=bg_color,
            fg_color=fg_color,
            include_logo=include_logo
        )
    except Exception as e:
        return f"❌ Failed to generate QR code: {str(e)}"
    
    # 5. Update link file with QR config
    link_data['qr_config'] = {
        'enabled': True,
        'bg_color': bg_color,
        'fg_color': fg_color,
        'has_logo': include_logo,
        'file_path': qr_path
    }
    update_link_file(slug, link_data)
    
    # 6. Commit and push
    commit_and_push(
        message=f"Generate QR code for {slug}",
        files=[f"data/links/active/{slug}.json", qr_path]
    )
    
    # 7. Return success with preview URL
    qr_url = f"{config['base_url']}/qr/{slug}"
    return f"✅ Generated QR code for {slug}\n📱 View at: {qr_url}\n💾 Saved to: {qr_path}"

@tool
def regenerate_qr_code(
    slug: str,
    bg_color: str = None,
    fg_color: str = None,
    include_logo: bool = None
) -> str:
    """
    Regenerate QR code with new colors/settings.
    
    Args:
        slug: The link slug
        bg_color: New background color (or keep existing)
        fg_color: New foreground color (or keep existing)
        include_logo: New logo setting (or keep existing)
    
    Returns:
        Success message
    """
    # Load existing QR config
    link_data = read_link_file(slug)
    if not link_data:
        return f"❌ Link '{slug}' not found"
    
    existing_qr = link_data.get('qr_config', {})
    
    # Use existing settings if not provided
    bg_color = bg_color or existing_qr.get('bg_color', '#FFFFFF')
    fg_color = fg_color or existing_qr.get('fg_color', '#000000')
    include_logo = include_logo if include_logo is not None else existing_qr.get('has_logo', True)
    
    # Regenerate
    return generate_qr_code(
        slug=slug,
        bg_color=bg_color,
        fg_color=fg_color,
        include_logo=include_logo,
        regenerate=True
    )
```

**Implementation Checklist:**
- [ ] Implement `generate_qr_code` tool
- [ ] Implement `regenerate_qr_code` tool
- [ ] Load link data validation
- [ ] Build full URL from config
- [ ] Call QR generation utility
- [ ] Update link JSON with QR config
- [ ] Git commit QR image + JSON
- [ ] Return formatted success message

---

### 3.3 Integrate QR Generation into `create_link` (1 hour)

**Tasks:**

- [ ] **Update `agent/tools/link_tools.py`** - Add QR generation to create_link
  ```python
  @tool
  def create_link(
      url: str,
      slug: str,
      prompt_context: str = "",
      tags: list[str] = None,
      utm_params: dict = None,
      expiration_days: int = None,
      description: str = "",
      # NEW QR parameters
      generate_qr: bool = False,
      qr_bg_color: str = "#FFFFFF",
      qr_fg_color: str = "#000000",
      qr_include_logo: bool = True
  ) -> str:
      """
      Create link with optional QR code generation.
      """
      # ... existing link creation logic ...
      
      # After link is created, generate QR if requested
      if generate_qr:
          from .qr_tools import generate_qr_code
          qr_result = generate_qr_code(
              slug=slug,
              bg_color=qr_bg_color,
              fg_color=qr_fg_color,
              include_logo=qr_include_logo
          )
          return f"{link_result}\n{qr_result}"
      
      return link_result
  ```

- [ ] **Update natural language parsing** to detect QR requests
  ```python
  # In nlp_helpers.py
  def parse_qr_request(text: str) -> dict | None:
      """
      Detect if user wants QR code and extract settings.
      
      Examples:
        "create a qr code" → {generate: True}
        "qr with black background and yellow" → {generate: True, bg: "#000000", fg: "#FFFF00"}
        "make a qr code with my favicon in the middle" → {generate: True, include_logo: True}
      """
      # Pattern match for "qr code", "qr", "qr-code"
      # Parse colors from text
      # Detect logo request
      # Return QR config dict or None
  ```

**Implementation Checklist:**
- [ ] Add QR parameters to `create_link` tool
- [ ] Integrate QR generation after link creation
- [ ] Parse QR request from natural language
- [ ] Parse color specifications
- [ ] Test combined link + QR creation

---

### 3.4 Vercel QR Serving Endpoint (1 hour)

**Tasks:**

- [ ] **Create `app/qr/[slug]/route.ts`** - Serve QR images
  ```typescript
  import { NextRequest, NextResponse } from 'next/server';
  import fs from 'fs';
  import path from 'path';
  
  export async function GET(
    request: NextRequest,
    { params }: { params: { slug: string } }
  ) {
    const slug = params.slug;
    const qrPath = path.join(process.cwd(), 'data', 'links', 'qr-codes', `${slug}.png`);
    
    // Check if QR code exists
    if (!fs.existsSync(qrPath)) {
      return new NextResponse('QR code not found', { status: 404 });
    }
    
    // Read image file
    const imageBuffer = fs.readFileSync(qrPath);
    
    // Return image with proper headers
    return new NextResponse(imageBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'image/png',
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });
  }
  ```

**Implementation Checklist:**
- [ ] Create QR serving route
- [ ] File existence checking
- [ ] Read image file
- [ ] Set proper content-type headers
- [ ] Add caching headers (QR codes don't change)
- [ ] Handle 404 gracefully
- [ ] Test QR code access via URL

---

### 3.5 Testing (1-2 hours)

**Test Scenarios:**

- [ ] **Test 1: Full natural language QR generation**
  ```
  > You: take this link luma.com and shorten it to luma. add utms because this will be in the newsletter on jan 17, 2026. add a tag for january and newsletter. then create a qr code with a black background and yellow. this link will expire in 2 weeks. put my favicon in the middle of the qr code.
  
  Expected: Link created with QR code
  Expected: data/links/qr-codes/luma.png exists
  Expected: QR code has black background, yellow foreground
  Expected: OpenHands logo visible in center
  ```

- [ ] **Test 2: QR code scans correctly**
  ```
  1. Open data/links/qr-codes/luma.png
  2. Scan with phone camera or QR scanner app
  3. Expected: Opens https://go.openhands.dev/luma
  4. Expected: Redirects to https://luma.com?utm_source=newsletter&utm_campaign=jan-17-2026
  ```

- [ ] **Test 3: QR code accessible via web**
  ```
  Visit: https://go.openhands.dev/qr/luma
  Expected: Shows QR code image
  Expected: Image displays correctly
  ```

- [ ] **Test 4: Regenerate QR with new colors**
  ```
  > You: regenerate qr for /luma with white background and blue foreground
  Agent: ✅ Regenerated QR code for luma
  
  Expected: New QR code overwrites old one
  Expected: New colors applied
  Expected: Still scans correctly
  ```

- [ ] **Test 5: Generate QR for existing link**
  ```
  > You: create a qr code for /luma
  Agent: ✅ Generated QR code for luma
  
  Expected: QR code created for existing link
  Expected: Link JSON updated with qr_config
  ```

- [ ] **Test 6: Contrast validation**
  ```
  > You: create qr for /test with light gray bg and white foreground
  Agent: ⚠️  Warning: Low contrast may affect scanability
  
  Expected: Agent warns about poor color choices
  ```

**Success Criteria:**
✅ QR codes generate correctly with custom colors
✅ QR codes scan reliably with logo overlay
✅ QR codes accessible via go.openhands.dev/qr/{slug}
✅ Natural language color parsing works
✅ Full example command works end-to-end

---

---

## 📊 PHASE 4: Analytics & PostHog Integration (Optional, As Needed)

**Goal**: Track link visits and usage metrics

**Time Estimate**: 1-2 days (when prioritized)

### Overview

Since the OpenHands team already uses PostHog for openhands.dev and docs subdomain, this phase integrates link tracking into the existing PostHog project.

### Key Tasks

- [ ] **Add PostHog SDK** to Vercel app (`package.json`)
- [ ] **Track events** in redirect handler (`app/[slug]/route.ts`):
  - `link_visited`: {slug, destination, tags, utm_params}
  - `link_expired`: {slug}
  - `link_not_found`: {attempted_slug}
- [ ] **Agent tool: `get_link_stats`**:
  - Query PostHog API for specific slug or tag
  - Return: total clicks, unique visitors, referrers
  - Example: "how many clicks did /luma get this week?"
- [ ] **Environment variables**:
  - `POSTHOG_API_KEY` (from existing project)
  - `POSTHOG_HOST` (default: https://app.posthog.com)

### Notes

- **No PII storage**: PostHog handles privacy-compliant tracking
- **Optional feature**: Can be enabled/disabled via env var
- **Leverages existing setup**: Uses OpenHands' current PostHog project
- **Analytics queries**: Agent can fetch stats via PostHog API

**Success Criteria:**
✅ Link visits appear in PostHog dashboard
✅ Agent can query and report link statistics
✅ No impact on redirect performance (async tracking)

---

## 🚀 PHASE 5: Documentation, Polish & Community Readiness (As Needed)

**Goal**: Make the project forkable and production-ready for community use

**Time Estimate**: 2-3 days (when prioritized)

### 5.1 Documentation

- [ ] **README.md**: Feature showcase, quick start (5 steps to deploy), fork instructions, example commands
- [ ] **SETUP.md**: Detailed Vercel deployment, GitHub token setup, custom domain config, LLM provider options
- [ ] **CONTRIBUTING.md**: For community contributors
- [ ] **LICENSE**: MIT license for open source

### 5.2 Configuration & Setup Automation

- [ ] **`.env.example`**:
  ```env
  # GitHub
  GITHUB_TOKEN=ghp_xxx
  GITHUB_REPO=openhands/link-shortener-agent
  
  # LLM (choose one)
  LLM_PROVIDER=openai  # or anthropic, openhands, local
  OPENAI_API_KEY=sk-xxx
  # ANTHROPIC_API_KEY=sk-ant-xxx
  # OPENHANDS_API_KEY=oh-xxx
  
  # Deployment
  BASE_URL=https://go.openhands.dev
  PRIMARY_DOMAIN=https://openhands.dev
  
  # Optional: Analytics (Phase 4)
  # POSTHOG_API_KEY=phc_xxx
  # POSTHOG_HOST=https://app.posthog.com
  ```

- [ ] **`scripts/setup.sh`**: One-command setup for forks (install deps, create directories, guide through config)

### 5.3 Error Handling & UX Polish

- [ ] Confirmation prompts for destructive actions
- [ ] Link previews before creation
- [ ] Better error messages (git conflicts, invalid URLs, etc.)
- [ ] Graceful degradation if GitHub push fails

### 5.4 Advanced Features (Nice-to-Have for Community)

- [ ] **GitHub Issues integration**: Create/manage links via issues
- [ ] **Scheduled cleanup**: GitHub Action to archive expired links
- [ ] **Link templates**: Predefined configs (e.g., "newsletter link", "social link")
- [ ] **Web dashboard** (optional): Simple UI for non-CLI users
- [ ] **Analytics dashboard**: Embedded PostHog charts in Vercel app

**Success Criteria:**
✅ Fork-to-deploy time < 10 minutes
✅ Clear documentation for all features
✅ Community members can contribute easily

---

## 🛠️ Tech Stack Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| **Agent Runtime** | OpenHands Agent SDK | Natural language, flexible LLM support, BYOK |
| **Terminal UI** | Python `rich` | Beautiful CLI with tables, colors, formatting |
| **Data Storage** | Individual JSON files + Git | Scalable, version-controlled, GitHub permissions |
| **Web Framework** | Next.js 14 (App Router) | Serverless, fast redirects, great DX |
| **Hosting** | Vercel (go.openhands.dev) | Free tier, auto-deploy, custom domains, CDN |
| **QR Generation** | `qrcode` + `Pillow` | Mature, custom colors, logo overlay |
| **Analytics** | PostHog (optional) | Already used by OpenHands, privacy-compliant |
| **Git Operations** | GitPython | Programmatic commits/pushes |
| **LLM** | BYOK (OpenAI, Anthropic, OpenHands, local) | Cost control, flexibility, model choice |
| **Natural Language** | Regex + dateutil | Fast, no extra LLM calls, predictable |

---

## 📋 Quick Start Development Checklist

### Pre-Development (30 minutes)
- [ ] Create GitHub repository: `openhands/link-shortener-agent`
- [ ] Clone locally and set up development environment
- [ ] Get API key for LLM (OpenAI GPT-4o recommended for testing)
- [ ] Verify go.openhands.dev subdomain availability

### Phase 1-3: Core Implementation (4-5 days)
- [ ] **Day 1-2**: Agent CLI + basic link management + Vercel app
- [ ] **Day 3**: UTM params, tags, expiration, bulk ops
- [ ] **Day 4-5**: QR code generation with branding
- [ ] **End of Phase 3**: Full natural language example command works

### Phase 4-5: Optional Enhancements (As Needed)
- [ ] **When prioritized**: PostHog analytics integration
- [ ] **Before public release**: Documentation and setup automation
- [ ] **Ongoing**: Community features and improvements

---

## 🎯 Success Metrics

### Technical
- [ ] Agent responds within 2 seconds
- [ ] Vercel redirects in < 100ms
- [ ] QR codes scan reliably with logo overlay
- [ ] Zero downtime deploys (Vercel auto-updates on push)
- [ ] Individual link files scale to 1000s of links

### User Experience
- [ ] Non-technical team member can create link without help
- [ ] Complex command from your example works first try
- [ ] Bulk deletion of 100 links works smoothly
- [ ] Fork-to-deploy time < 10 minutes

### Business Value
- [ ] $0/month cost (within free tiers)
- [ ] Replaces Bitly/Dub.sh for team
- [ ] 10+ community forks
- [ ] 100+ links managed successfully

---

## 🚨 Known Challenges & Solutions

### Challenge 1: Vercel Cold Starts
- **Problem**: First request may be slow (fetch links.json)
- **Solution**: Cache links.json in memory, revalidate every 60s

### Challenge 2: Git Conflicts
- **Problem**: Multiple users editing simultaneously
- **Solution**: Agent pulls before push, retries with conflict resolution

### Challenge 3: QR Code with Logo Still Scanning
- **Problem**: Logo may obstruct QR data
- **Solution**: Use error correction level H (30%), keep logo < 15% size

### Challenge 4: Natural Language Ambiguity
- **Problem**: "delete all old links" - how old?
- **Solution**: Agent asks for clarification, shows preview of affected links

### Challenge 5: Repository Size with Many Links
- **Problem**: Thousands of link files + QR images = large repo
- **Solution**: Individual files already scale well; archive expired links to `data/links/archived/`; consider git LFS for QR images if repo exceeds 1GB

---

## 🎉 Future Enhancements (Post-MVP)

1. **Link Preview Cards**: Generate OpenGraph images for social sharing
2. **A/B Testing**: Support multiple destinations for one slug
3. **Browser Extension**: Right-click → "Shorten with Agent"
4. **Slack Integration**: Create links from Slack messages
5. **Email Integration**: Parse links from forwarded newsletters
6. **Analytics Dashboard**: Beautiful UI for team to view stats
7. **Link Bundles**: Group related links (e.g., "social-media-kit")
8. **Custom 404 Page**: Branded error page for invalid slugs
9. **Link Scheduling**: Create links that activate on a specific date
10. **API Keys**: Allow programmatic access for CI/CD pipelines

---

## 📝 Notes

- **Why not a database?** GitHub repo IS the database. Version control + permissions + free = perfect.
- **Why JSON?** Simple, human-readable, git-friendly, no query complexity needed.
- **Why Agent SDK?** Learning opportunity + natural language is genuinely better UX for this use case.
- **Why Vercel?** They want you to use it this way (JAMstack), free tier is generous, custom domains are easy.

---

## 🔗 Resources

- [OpenHands Agent SDK Docs](https://docs.openhands.dev/sdk/)
- [Vercel Next.js Deployment](https://vercel.com/docs)
- [PostHog Event Tracking](https://posthog.com/docs)
- [QR Code Error Correction](https://en.wikipedia.org/wiki/QR_code#Error_correction)

---

**Ready to build?** Start with Phase 1, commit to main, and iterate. The agent can help manage itself! 🤖

**Want to fork?** Everything will be MIT licensed. Star the repo, deploy your own, contribute back.

**Questions?** Open a GitHub issue - the agent might even help answer it. 😉
