#!/usr/bin/env python3
"""
Link Manager - CRUD operations for OpenLinks

Handles creating, reading, updating, and deleting link JSON files.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urlparse, urlencode


# Constants
PROJECT_ROOT = Path(__file__).parent.parent
ACTIVE_LINKS_DIR = PROJECT_ROOT / "data" / "links" / "active"
ARCHIVED_LINKS_DIR = PROJECT_ROOT / "data" / "links" / "archived"
QR_CODES_DIR = PROJECT_ROOT / "data" / "links" / "qr-codes"
CONFIG_FILE = PROJECT_ROOT / "data" / "config.json"


def load_config() -> Dict:
    """Load configuration from config.json"""
    if not CONFIG_FILE.exists():
        return {
            "base_url": "https://go.openhands.dev",
            "primary_domain": "https://openhands.dev"
        }
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def validate_slug(slug: str) -> bool:
    """Validate slug format (alphanumeric, hyphens, underscores only)"""
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', slug))


def slug_exists(slug: str) -> bool:
    """Check if a slug already exists"""
    link_file = ACTIVE_LINKS_DIR / f"{slug}.json"
    return link_file.exists()


def generate_link_id(slug: str) -> str:
    """Generate unique ID for a link"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{slug}_{timestamp}"


def parse_expiration(expiration_text: Optional[str]) -> Optional[str]:
    """
    Parse natural language expiration text to ISO timestamp
    
    Examples:
    - "next week" -> 7 days from now
    - "1 week" -> 7 days from now
    - "3 days" -> 3 days from now
    - "Jan 31" -> January 31 of current/next year
    - "2024-01-31" -> exact date
    """
    if not expiration_text:
        return None
    
    text = expiration_text.lower().strip()
    now = datetime.utcnow()
    
    # Handle relative times
    if "day" in text:
        days_match = re.search(r'(\d+)\s*days?', text)
        if days_match:
            days = int(days_match.group(1))
        else:
            days = 7  # default "next week"
        expire_date = now + timedelta(days=days)
        return expire_date.isoformat() + "Z"
    
    if "week" in text:
        weeks_match = re.search(r'(\d+)\s*weeks?', text)
        if weeks_match:
            weeks = int(weeks_match.group(1))
        else:
            weeks = 1
        expire_date = now + timedelta(weeks=weeks)
        return expire_date.isoformat() + "Z"
    
    if "month" in text:
        months_match = re.search(r'(\d+)\s*months?', text)
        if months_match:
            months = int(months_match.group(1))
        else:
            months = 1
        expire_date = now + timedelta(days=months * 30)
        return expire_date.isoformat() + "Z"
    
    # Handle ISO format
    if re.match(r'\d{4}-\d{2}-\d{2}', text):
        try:
            expire_date = datetime.fromisoformat(text.replace('Z', ''))
            return expire_date.isoformat() + "Z"
        except:
            pass
    
    return None


def create_link(
    slug: str,
    destination: str,
    utm_params: Optional[Dict[str, str]] = None,
    expires_at: Optional[str] = None,
    redirect_after_expiry: Optional[str] = None,
    tags: Optional[List[str]] = None,
    description: Optional[str] = None,
    created_by: str = "github-agent"
) -> Dict:
    """
    Create a new link
    
    Args:
        slug: Short URL path (e.g., "luma")
        destination: Target URL
        utm_params: Dictionary of UTM parameters
        expires_at: Expiration timestamp (ISO format) or natural language
        redirect_after_expiry: URL to redirect to after expiration
        tags: List of tags for organization
        description: Human-readable description
        created_by: Username of creator
    
    Returns:
        Dictionary with link data
    
    Raises:
        ValueError: If validation fails
    """
    # Validate inputs
    if not validate_slug(slug):
        raise ValueError(f"Invalid slug: {slug}. Use only letters, numbers, hyphens, and underscores.")
    
    if slug_exists(slug):
        raise ValueError(f"Slug already exists: {slug}")
    
    if not validate_url(destination):
        raise ValueError(f"Invalid destination URL: {destination}")
    
    if redirect_after_expiry and not validate_url(redirect_after_expiry):
        raise ValueError(f"Invalid redirect URL: {redirect_after_expiry}")
    
    # Parse expiration if it's natural language
    if expires_at and not expires_at.endswith('Z'):
        expires_at = parse_expiration(expires_at)
    
    # Build link data
    link_data = {
        "id": generate_link_id(slug),
        "slug": slug,
        "destination": destination,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "created_by": created_by,
        "expires_at": expires_at,
        "redirect_after_expiry": redirect_after_expiry,
        "tags": tags or [],
        "utm_params": utm_params or {},
        "qr_config": {
            "enabled": False,
            "file_path": None
        },
        "metadata": {
            "description": description or f"Link to {destination}",
            "last_modified": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    # Save to file
    link_file = ACTIVE_LINKS_DIR / f"{slug}.json"
    with open(link_file, 'w') as f:
        json.dump(link_data, f, indent=2)
    
    return link_data


def read_link(slug: str) -> Optional[Dict]:
    """Read link data by slug"""
    link_file = ACTIVE_LINKS_DIR / f"{slug}.json"
    
    if not link_file.exists():
        return None
    
    with open(link_file, 'r') as f:
        return json.load(f)


def update_link(slug: str, updates: Dict) -> Dict:
    """
    Update an existing link
    
    Args:
        slug: Link slug to update
        updates: Dictionary of fields to update
    
    Returns:
        Updated link data
    
    Raises:
        ValueError: If link doesn't exist or validation fails
    """
    link_data = read_link(slug)
    if not link_data:
        raise ValueError(f"Link not found: {slug}")
    
    # Validate updates
    if 'destination' in updates and not validate_url(updates['destination']):
        raise ValueError(f"Invalid destination URL: {updates['destination']}")
    
    if 'redirect_after_expiry' in updates and updates['redirect_after_expiry']:
        if not validate_url(updates['redirect_after_expiry']):
            raise ValueError(f"Invalid redirect URL: {updates['redirect_after_expiry']}")
    
    # Parse expiration if provided
    if 'expires_at' in updates and updates['expires_at']:
        if not updates['expires_at'].endswith('Z'):
            updates['expires_at'] = parse_expiration(updates['expires_at'])
    
    # Apply updates
    link_data.update(updates)
    link_data['metadata']['last_modified'] = datetime.utcnow().isoformat() + "Z"
    
    # Save
    link_file = ACTIVE_LINKS_DIR / f"{slug}.json"
    with open(link_file, 'w') as f:
        json.dump(link_data, f, indent=2)
    
    return link_data


def delete_link(slug: str, archive: bool = True) -> bool:
    """
    Delete a link (optionally archive it)
    
    Args:
        slug: Link slug to delete
        archive: If True, move to archived/ instead of deleting
    
    Returns:
        True if deleted, False if not found
    """
    link_file = ACTIVE_LINKS_DIR / f"{slug}.json"
    
    if not link_file.exists():
        return False
    
    if archive:
        # Move to archived
        archived_file = ARCHIVED_LINKS_DIR / f"{slug}.json"
        link_file.rename(archived_file)
    else:
        # Permanently delete
        link_file.unlink()
    
    # Also delete QR code if exists
    qr_file = QR_CODES_DIR / f"{slug}.png"
    if qr_file.exists():
        qr_file.unlink()
    
    return True


def list_links(tags: Optional[List[str]] = None) -> List[Dict]:
    """
    List all active links, optionally filtered by tags
    
    Args:
        tags: List of tags to filter by (returns links with ANY of these tags)
    
    Returns:
        List of link data dictionaries
    """
    links = []
    
    for link_file in ACTIVE_LINKS_DIR.glob("*.json"):
        with open(link_file, 'r') as f:
            link_data = json.load(f)
        
        # Filter by tags if specified
        if tags:
            link_tags = link_data.get('tags', [])
            if not any(tag in link_tags for tag in tags):
                continue
        
        links.append(link_data)
    
    return links


def bulk_delete_by_tag(tag: str, archive: bool = True) -> int:
    """
    Delete all links with a specific tag
    
    Args:
        tag: Tag to filter by
        archive: If True, archive instead of delete
    
    Returns:
        Number of links deleted
    """
    links = list_links(tags=[tag])
    deleted_count = 0
    
    for link in links:
        if delete_link(link['slug'], archive=archive):
            deleted_count += 1
    
    return deleted_count


def get_full_url(slug: str, include_utm: bool = True) -> str:
    """
    Get the full shortened URL for a slug
    
    Args:
        slug: Link slug
        include_utm: If True, include UTM parameters in display
    
    Returns:
        Full URL (e.g., "https://go.openhands.dev/luma")
    """
    config = load_config()
    base_url = config.get('base_url', 'https://go.openhands.dev')
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    return f"{base_url}/{slug}"


if __name__ == "__main__":
    # Simple CLI testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python link_manager.py <command> [args...]")
        print("Commands: create, read, list, delete")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 4:
            print("Usage: python link_manager.py create <slug> <destination>")
            sys.exit(1)
        
        slug = sys.argv[2]
        destination = sys.argv[3]
        
        try:
            link = create_link(slug, destination)
            print(f"✅ Created: {get_full_url(slug)}")
            print(json.dumps(link, indent=2))
        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif command == "read":
        if len(sys.argv) < 3:
            print("Usage: python link_manager.py read <slug>")
            sys.exit(1)
        
        slug = sys.argv[2]
        link = read_link(slug)
        
        if link:
            print(json.dumps(link, indent=2))
        else:
            print(f"❌ Link not found: {slug}")
            sys.exit(1)
    
    elif command == "list":
        links = list_links()
        print(f"Found {len(links)} links:")
        for link in links:
            print(f"  - {get_full_url(link['slug'])} → {link['destination']}")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python link_manager.py delete <slug>")
            sys.exit(1)
        
        slug = sys.argv[2]
        if delete_link(slug):
            print(f"✅ Deleted: {slug}")
        else:
            print(f"❌ Link not found: {slug}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
