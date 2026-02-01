# OpenLinks Parameters Reference

Complete reference of all parameters supported by OpenLinks for link operations.

## 🔗 Create Link Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `slug` | string | ✅ Yes | Short URL path (alphanumeric, hyphens, underscores) | `luma`, `docs`, `my-link` |
| `destination` | string (URL) | ✅ Yes | Full destination URL including protocol | `https://luma.com` |
| `utm_source` | string | ❌ No | UTM source parameter | `newsletter`, `twitter`, `email` |
| `utm_medium` | string | ❌ No | UTM medium parameter | `email`, `social`, `cpc` |
| `utm_campaign` | string | ❌ No | UTM campaign parameter | `january-2024`, `product-launch` |
| `utm_content` | string | ❌ No | UTM content parameter | `header-link`, `sidebar` |
| `utm_term` | string | ❌ No | UTM term parameter | `keyword`, `product-name` |
| `expires_at` | string/date | ❌ No | Expiration date or natural language | `next week`, `2024-12-31`, `30 days` |
| `redirect_after_expiry` | string (URL) | ❌ No | URL to redirect after expiration | `https://openhands.dev` |
| `tags` | array/string | ❌ No | Tags for organization (comma-separated) | `newsletter, january, promo` |
| `description` | string | ❌ No | Human-readable description | `Link for January newsletter` |

---

## 🔄 Update Link Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `slug` | string | ✅ Yes | Slug of the link to update | `luma` |
| `destination` | string (URL) | ❌ No | New destination URL | `https://new-destination.com` |
| `utm_source` | string | ❌ No | Update UTM source | `newsletter` |
| `utm_medium` | string | ❌ No | Update UTM medium | `email` |
| `utm_campaign` | string | ❌ No | Update UTM campaign | `february-2024` |
| `utm_content` | string | ❌ No | Update UTM content | `footer-link` |
| `utm_term` | string | ❌ No | Update UTM term | `new-keyword` |
| `expires_at` | string/date | ❌ No | Update expiration | `next month`, `2024-12-31` |
| `redirect_after_expiry` | string (URL) | ❌ No | Update expiry redirect | `https://openhands.dev` |
| `tags` | array/string | ❌ No | Update tags (replaces existing) | `newsletter, february` |
| `description` | string | ❌ No | Update description | `Updated for February` |

**Note:** Only include parameters you want to change. Omitted parameters remain unchanged.

---

## 🗑️ Delete Link Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `slug` | string | ❌ No* | Single slug to delete | `old-promo` |
| `tag` | string | ❌ No* | Delete all links with this tag | `january-2024` |

**\*Note:** Must specify either `slug` OR `tag`, not both.

---

## 📋 List Links Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `tags` | array/string | ❌ No | Filter by tags (comma-separated) | `newsletter`, `promo` |

**Note:** If no tags specified, lists all links (limited to first 10 in comment).

---

## 📐 Expiration Natural Language Examples

The agent understands various natural language formats for expiration:

| Format | Parsed As |
|--------|-----------|
| `next week` | 7 days from now |
| `1 week` | 7 days from now |
| `2 weeks` | 14 days from now |
| `3 days` | 3 days from now |
| `30 days` | 30 days from now |
| `next month` | 30 days from now |
| `1 month` | 30 days from now |
| `2 months` | 60 days from now |
| `2024-12-31` | Exact date (ISO format) |
| `Dec 31 2024` | Parsed date |

---

## 🎯 UTM Parameters Best Practices

### Standard UTM Parameters

| Parameter | Purpose | Examples |
|-----------|---------|----------|
| `utm_source` | Where traffic comes from | `newsletter`, `twitter`, `facebook`, `linkedin` |
| `utm_medium` | Marketing medium | `email`, `social`, `cpc`, `banner`, `qr-code` |
| `utm_campaign` | Campaign identifier | `january-sale`, `product-launch`, `webinar-2024` |
| `utm_content` | Differentiate similar content | `header-link`, `footer-link`, `sidebar-cta` |
| `utm_term` | Paid search keywords | `link-shortener`, `ai-tools` |

### Example Combinations

**Newsletter Link:**
```
utm_source: newsletter
utm_medium: email
utm_campaign: january-2024
```

**Social Media Post:**
```
utm_source: twitter
utm_medium: social
utm_campaign: product-launch
utm_content: announcement-post
```

**QR Code on Flyer:**
```
utm_source: conference
utm_medium: qr-code
utm_campaign: booth-visit
```

---

## 🏷️ Tag Naming Conventions

Recommended tag formats for organization:

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `month-year` | Time-based grouping | `january-2024`, `feb-2024` |
| `campaign-name` | Campaign tracking | `product-launch`, `holiday-sale` |
| `medium` | Distribution channel | `newsletter`, `social`, `email` |
| `team` | Team ownership | `marketing`, `sales`, `growth` |
| `status` | Link status | `active`, `testing`, `archived` |

---

## 📝 Natural Language Examples

The agent understands natural language requests. Here are examples:

### Simple Creation
```
"Create /docs that goes to docs.openhands.dev"
"Shorten luma.com to /luma"
"Make /gh point to github.com/openhands"
```

### With UTM Parameters
```
"Create /luma → luma.com with newsletter UTMs"
"Shorten twitter.com to /tw with utm_source=social and utm_campaign=launch"
"Create /promo with email medium and january campaign"
```

### With Expiration
```
"Create /sale → example.com/sale that expires in 1 week"
"Shorten promo.com to /promo, expires next month"
"Create /temp that goes to example.com and expires in 3 days"
```

### With Expiration & Redirect
```
"Create /promo that goes to sale.com, expires in 1 week, then redirect to homepage"
"Shorten event.com to /event, expires next week, redirect to openhands.dev after"
```

### With Tags
```
"Create /luma for luma.com tagged with newsletter and january"
"Shorten docs.openhands.dev to /docs with tag documentation"
```

### Complex Example
```
"Take google.com and make it /ggl with newsletter UTMs, 
expires next week, redirect to homepage after expiration, 
tagged with promo and january"
```

### Updates
```
"Update /docs to point to docs.new-domain.com"
"Change /luma destination to luma.com/new-page"
"Extend /promo expiration by 2 weeks"
```

### Deletions
```
"Delete /old-link"
"Delete all links tagged january"
"Remove all expired links"
```

### Lists
```
"List all links"
"Show me all newsletter links"
"List links tagged with campaign-2024"
```

---

## 🔍 Validation Rules

### Slug Validation
- ✅ Allowed: letters (a-z, A-Z), numbers (0-9), hyphens (-), underscores (_)
- ❌ Not allowed: spaces, special characters, emojis
- ✅ Valid: `my-link`, `docs`, `promo_2024`, `link123`
- ❌ Invalid: `my link`, `link!`, `🔗link`

### URL Validation
- ✅ Must include protocol: `https://` or `http://`
- ✅ Must have valid domain
- ✅ Valid: `https://example.com`, `http://localhost:3000`
- ❌ Invalid: `example.com`, `www.example.com`, `example`

### Tag Validation
- ✅ Allowed: any string
- ✅ Multiple tags: comma-separated
- ✅ Valid: `newsletter`, `january-2024`, `promo, sale, urgent`

---

## 📊 Data Schema (JSON)

When a link is created, it's stored as JSON in `data/links/active/{slug}.json`:

```json
{
  "id": "luma_20240201_143022",
  "slug": "luma",
  "destination": "https://luma.com",
  "created_at": "2024-02-01T14:30:22Z",
  "created_by": "openlinks-agent",
  "expires_at": "2024-02-15T00:00:00Z",
  "redirect_after_expiry": "https://openhands.dev",
  "tags": ["newsletter", "january", "issue-123"],
  "utm_params": {
    "utm_source": "newsletter",
    "utm_medium": "email",
    "utm_campaign": "january-2024"
  },
  "qr_config": {
    "enabled": false,
    "file_path": null
  },
  "metadata": {
    "description": "Link for January newsletter",
    "last_modified": "2024-02-01T14:30:22Z"
  }
}
```

---

## 🎓 Tips for Power Users

1. **Batch Operations**: Create multiple issues with the same tag, then bulk delete later
2. **Campaign Tracking**: Use consistent tag naming for easy filtering
3. **Expiration Strategy**: Set expirations with fallback redirects for temporary campaigns
4. **UTM Consistency**: Use standard utm_source values across campaigns for better analytics
5. **Natural Language**: The more natural your request, the better the agent understands

---

## 🚀 Quick Reference

### Create Link (Minimal)
```
Slug: luma
Destination: https://luma.com
```

### Create Link (Full)
```
Slug: promo
Destination: https://example.com/sale
UTM Source: newsletter
UTM Medium: email
UTM Campaign: january-2024
Expires: 2 weeks
Redirect After Expiry: https://example.com
Tags: promo, january, email
Description: January promotional link
```

### Update Link
```
Slug: luma
Destination: https://luma.com/new-page
```

### Delete Link
```
Slug: old-promo
```

### Bulk Delete
```
Tag: january-2024
```

### List Links
```
Tags: newsletter, promo
```

---

For more examples, see [README.md](./README.md)
