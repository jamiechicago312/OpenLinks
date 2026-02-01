#!/usr/bin/env python3
"""
Prompt templates for OpenLinks Agent
"""

FEATURE_IMPLEMENTATION_PROMPT = """
You are implementing a feature request for OpenLinks, a link shortening system.

**Issue Title:** {issue_title}

**Issue Description:**
{issue_body}

**Issue Number:** #{issue_number}

**Current Repository Structure:**
- `scripts/` - Python utilities (link_manager.py, openlinks_agent.py)
- `data/links/active/` - JSON files for each link
- `data/links/archived/` - Archived/expired links
- `data/links/qr-codes/` - QR code images
- `data/config.json` - Configuration file
- `.github/workflows/` - GitHub Actions workflows

**Your Task:**
1. Analyze the feature request
2. Implement the feature by modifying/creating the necessary files
3. Create a new branch: `feature/issue-{issue_number}`
4. Commit your changes with clear commit messages
5. Push the branch and create a pull request

**Important:**
- Follow the existing code style and patterns
- Add appropriate error handling
- Update documentation if needed
- Test your changes locally before creating the PR

**Example Features:**
- QR code generation for links
- Analytics integration
- Bulk operations by tag
- Link expiration handling
- Custom redirect pages

Begin implementation now.
"""


LINK_OPERATION_PROMPT = """
You are parsing a natural language link operation request for OpenLinks.

**Request:** {request_text}

**Your Task:**
Extract the following information from the request:

1. **Operation Type:** (create, update, delete, list)
2. **Slug:** The short URL path (e.g., "luma", "ggl")
3. **Destination URL:** The target URL to redirect to
4. **UTM Parameters:** Any UTM tags mentioned (source, medium, campaign)
5. **Expiration:** When the link should expire (natural language or date)
6. **Redirect After Expiry:** URL to redirect to after expiration
7. **Tags:** Any tags for organization
8. **Description:** Human-readable description

**Examples:**

Request: "Shorten luma.com to /luma with newsletter UTMs"
→ Operation: create
→ Slug: luma
→ Destination: https://luma.com
→ UTM: {{"utm_source": "newsletter"}}

Request: "Create google.com → /ggl with newsletter UTMs, expires next week, redirect to homepage"
→ Operation: create
→ Slug: ggl
→ Destination: https://google.com
→ UTM: {{"utm_source": "newsletter"}}
→ Expiration: next week
→ Redirect After Expiry: https://openhands.dev

Request: "Delete all links tagged january"
→ Operation: delete
→ Tags: ["january"]

Request: "List all links with tag newsletter"
→ Operation: list
→ Tags: ["newsletter"]

**Return Format:**
Return ONLY a valid JSON object with the extracted information:
```json
{{
  "operation": "create|update|delete|list",
  "slug": "slug-name",
  "destination": "https://example.com",
  "utm_params": {{
    "utm_source": "source",
    "utm_medium": "medium",
    "utm_campaign": "campaign"
  }},
  "expires_at": "natural language or ISO date",
  "redirect_after_expiry": "https://fallback.com",
  "tags": ["tag1", "tag2"],
  "description": "Description text"
}}
```

Parse the request now and return ONLY the JSON object.
"""


CLASSIFICATION_PROMPT = """
You are classifying a GitHub issue for OpenLinks, a link shortening system.

**Issue Title:** {issue_title}

**Issue Body:**
{issue_body}

**Your Task:**
Determine if this is a FEATURE request or a LINK operation.

**FEATURE Requests:**
These are requests to modify the codebase, add new capabilities, or change how the system works.
Examples:
- "Add QR code generation"
- "Implement analytics tracking"
- "Add bulk delete by tag"
- "Create a web dashboard"
- "Add expiration date support"

**LINK Operations:**
These are requests to create, update, delete, or manage specific links.
Examples:
- "Shorten luma.com to /luma"
- "Create google.com → /ggl with UTMs"
- "Delete all links tagged january"
- "Update /docs to point to new URL"
- "List all newsletter links"

**Response:**
Respond with ONLY one word: FEATURE or LINK

Classification:
"""
