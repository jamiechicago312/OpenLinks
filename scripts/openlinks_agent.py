#!/usr/bin/env python3
"""
OpenLinks Agent - Issue-triggered link management and feature implementation

This agent processes GitHub issues labeled with 'openlinks' and either:
1. Creates/updates/deletes links (LINK operations)
2. Implements features (FEATURE requests)

Environment Variables:
    GITHUB_TOKEN: GitHub authentication token
    LLM_API_KEY: LLM API key for agent
    LLM_MODEL: LLM model to use (default: anthropic/claude-sonnet-4-5-20250929)
    LLM_BASE_URL: Optional LLM base URL
    ISSUE_NUMBER: GitHub issue number
    ISSUE_TITLE: Issue title
    ISSUE_BODY: Issue body text
    GITHUB_REPOSITORY: Repository in format owner/repo
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import link_manager
from openlinks_prompts import (
    CLASSIFICATION_PROMPT,
    LINK_OPERATION_PROMPT,
    FEATURE_IMPLEMENTATION_PROMPT
)


def get_env_or_exit(var_name: str) -> str:
    """Get environment variable or exit with error"""
    value = os.getenv(var_name)
    if not value:
        print(f"❌ Error: {var_name} environment variable not set")
        sys.exit(1)
    return value


def run_command(cmd: str, check=True) -> subprocess.CompletedProcess:
    """Run shell command and return result"""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    
    return result


def setup_git():
    """Configure git for commits"""
    run_command('git config user.name "OpenLinks Agent"')
    run_command('git config user.email "openhands@all-hands.dev"')


def comment_on_issue(issue_number: str, comment: str):
    """Post a comment on the GitHub issue using gh CLI"""
    repo = os.getenv("GITHUB_REPOSITORY", "")
    
    if not repo:
        print("⚠️  GITHUB_REPOSITORY not set, skipping comment")
        return
    
    # Escape quotes in comment
    comment_escaped = comment.replace('"', '\\"').replace('\n', '\\n')
    
    cmd = f'gh issue comment {issue_number} --body "{comment_escaped}" --repo {repo}'
    result = run_command(cmd, check=False)
    
    if result.returncode != 0:
        print(f"⚠️  Failed to comment on issue: {result.stderr}")
    else:
        print("✅ Posted comment on issue")


def classify_request(issue_title: str, issue_body: str) -> str:
    """
    Classify whether this is a FEATURE request or LINK operation
    
    Returns:
        "FEATURE" or "LINK"
    """
    # Quick heuristics first
    combined_text = (issue_title + " " + issue_body).lower()
    
    # Strong LINK indicators
    link_patterns = [
        r'https?://',  # Contains URLs
        r'shorten',
        r'create\s+link',
        r'delete\s+link',
        r'update\s+link',
        r'→',  # Arrow symbol often used in link requests
        r'to\s+/',  # "to /slug"
        r'utm',
    ]
    
    link_score = sum(1 for pattern in link_patterns if re.search(pattern, combined_text))
    
    # Strong FEATURE indicators
    feature_patterns = [
        r'add\s+(support|ability|feature|capability)',
        r'implement',
        r'create\s+(a|an)\s+(feature|system|dashboard|page)',
        r'enable',
        r'build',
        r'develop',
    ]
    
    feature_score = sum(1 for pattern in feature_patterns if re.search(pattern, combined_text))
    
    # If clear winner, return it
    if link_score > feature_score + 1:
        return "LINK"
    elif feature_score > link_score:
        return "FEATURE"
    
    # Otherwise, use LLM for classification
    print("🤔 Using LLM to classify request...")
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv("LLM_API_KEY")
        model = os.getenv("LLM_MODEL", "gpt-4o")
        base_url = os.getenv("LLM_BASE_URL")
        
        if not api_key:
            print("⚠️  LLM_API_KEY not set, defaulting to LINK operation")
            return "LINK"
        
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        client = OpenAI(**client_kwargs)
        
        prompt = CLASSIFICATION_PROMPT.format(
            issue_title=issue_title,
            issue_body=issue_body
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        
        classification = response.choices[0].message.content.strip().upper()
        
        if "FEATURE" in classification:
            return "FEATURE"
        else:
            return "LINK"
    
    except Exception as e:
        print(f"⚠️  Error classifying with LLM: {e}")
        print("Defaulting to LINK operation")
        return "LINK"


def parse_link_operation(request_text: str) -> dict:
    """
    Parse natural language link operation request
    
    Returns:
        Dictionary with operation details
    """
    try:
        from openai import OpenAI
        
        api_key = os.getenv("LLM_API_KEY")
        model = os.getenv("LLM_MODEL", "gpt-4o")
        base_url = os.getenv("LLM_BASE_URL")
        
        if not api_key:
            raise ValueError("LLM_API_KEY not set")
        
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        client = OpenAI(**client_kwargs)
        
        prompt = LINK_OPERATION_PROMPT.format(request_text=request_text)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response (might be wrapped in markdown)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        parsed = json.loads(response_text)
        return parsed
    
    except Exception as e:
        print(f"⚠️  Error parsing with LLM: {e}")
        print("Falling back to simple parsing...")
        
        # Simple fallback parsing
        text = request_text.lower()
        
        # Extract URL
        url_match = re.search(r'(https?://[^\s]+)', request_text)
        destination = url_match.group(1) if url_match else None
        
        # Extract slug
        slug_match = re.search(r'/(\w+)', request_text)
        slug = slug_match.group(1) if slug_match else None
        
        # Detect operation
        if 'delete' in text:
            operation = 'delete'
        elif 'update' in text:
            operation = 'update'
        elif 'list' in text:
            operation = 'list'
        else:
            operation = 'create'
        
        return {
            "operation": operation,
            "slug": slug,
            "destination": destination,
            "utm_params": {},
            "expires_at": None,
            "redirect_after_expiry": None,
            "tags": [],
            "description": None
        }


def handle_link_operation(operation_data: dict, issue_number: str) -> str:
    """
    Execute a link operation and return result message
    
    Args:
        operation_data: Parsed operation details
        issue_number: GitHub issue number for tagging
    
    Returns:
        Success message to post as comment
    """
    operation = operation_data.get("operation", "create")
    
    try:
        if operation == "create":
            slug = operation_data.get("slug")
            destination = operation_data.get("destination")
            
            if not slug or not destination:
                return "❌ Error: Missing slug or destination URL for link creation"
            
            # Add issue number as tag
            tags = operation_data.get("tags", [])
            tags.append(f"issue-{issue_number}")
            
            link_data = link_manager.create_link(
                slug=slug,
                destination=destination,
                utm_params=operation_data.get("utm_params"),
                expires_at=operation_data.get("expires_at"),
                redirect_after_expiry=operation_data.get("redirect_after_expiry"),
                tags=tags,
                description=operation_data.get("description"),
                created_by="openlinks-agent"
            )
            
            # Commit and push
            setup_git()
            run_command(f'git add data/links/active/{slug}.json')
            run_command(f'git commit -m "Add link: /{slug} → {destination} (issue #{issue_number})"')
            run_command('git push origin main')
            
            full_url = link_manager.get_full_url(slug)
            
            message = f"✅ **Link created successfully!**\n\n"
            message += f"**Short URL:** {full_url}\n"
            message += f"**Destination:** {destination}\n"
            
            if operation_data.get("utm_params"):
                message += f"**UTM Parameters:** {json.dumps(operation_data['utm_params'], indent=2)}\n"
            
            if operation_data.get("expires_at"):
                message += f"**Expires:** {operation_data['expires_at']}\n"
                if operation_data.get("redirect_after_expiry"):
                    message += f"**After expiry redirects to:** {operation_data['redirect_after_expiry']}\n"
            
            message += f"\n🚀 Your link is live! Changes will deploy to Vercel automatically.\n"
            
            return message
        
        elif operation == "update":
            slug = operation_data.get("slug")
            if not slug:
                return "❌ Error: Missing slug for link update"
            
            updates = {k: v for k, v in operation_data.items() if k not in ['operation', 'slug'] and v is not None}
            
            link_data = link_manager.update_link(slug, updates)
            
            # Commit and push
            setup_git()
            run_command(f'git add data/links/active/{slug}.json')
            run_command(f'git commit -m "Update link: /{slug} (issue #{issue_number})"')
            run_command('git push origin main')
            
            return f"✅ **Link updated successfully!**\n\n{link_manager.get_full_url(slug)}"
        
        elif operation == "delete":
            tags = operation_data.get("tags")
            slug = operation_data.get("slug")
            
            if tags:
                # Bulk delete by tag
                count = link_manager.bulk_delete_by_tag(tags[0])
                
                setup_git()
                run_command('git add data/links/')
                run_command(f'git commit -m "Delete {count} links with tag: {tags[0]} (issue #{issue_number})"')
                run_command('git push origin main')
                
                return f"✅ **Deleted {count} links with tag:** {tags[0]}"
            
            elif slug:
                # Delete single link
                if link_manager.delete_link(slug):
                    setup_git()
                    run_command('git add data/links/')
                    run_command(f'git commit -m "Delete link: /{slug} (issue #{issue_number})"')
                    run_command('git push origin main')
                    
                    return f"✅ **Link deleted:** /{slug}"
                else:
                    return f"❌ Link not found: /{slug}"
            else:
                return "❌ Error: Specify either a slug or tags for deletion"
        
        elif operation == "list":
            tags = operation_data.get("tags")
            links = link_manager.list_links(tags=tags)
            
            if not links:
                return "📭 No links found"
            
            message = f"📋 **Found {len(links)} link(s):**\n\n"
            for link in links[:10]:  # Limit to 10 for comment
                full_url = link_manager.get_full_url(link['slug'])
                message += f"- `{full_url}` → {link['destination']}\n"
            
            if len(links) > 10:
                message += f"\n...and {len(links) - 10} more"
            
            return message
        
        else:
            return f"❌ Unknown operation: {operation}"
    
    except Exception as e:
        return f"❌ **Error:** {str(e)}"


def handle_feature_request(issue_number: str, issue_title: str, issue_body: str) -> str:
    """
    Use SDK agent to implement feature request
    
    Returns:
        Success message with PR link
    """
    try:
        # Import SDK here to avoid dependency issues if not installed
        from openhands.sdk import LLM, Conversation, get_logger
        from openhands.tools.preset.default import get_default_agent
        
        logger = get_logger(__name__)
        
        # Configure LLM
        api_key = get_env_or_exit("LLM_API_KEY")
        model = os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929")
        base_url = os.getenv("LLM_BASE_URL")
        
        llm_config = {
            "model": model,
            "api_key": api_key,
            "usage_id": "openlinks_agent",
            "drop_params": True,
        }
        
        if base_url:
            llm_config["base_url"] = base_url
        
        llm = LLM(**llm_config)
        
        # Create prompt
        prompt = FEATURE_IMPLEMENTATION_PROMPT.format(
            issue_title=issue_title,
            issue_body=issue_body,
            issue_number=issue_number
        )
        
        # Create agent
        agent = get_default_agent(llm=llm, cli_mode=True)
        
        # Get workspace (project root)
        workspace = Path(__file__).parent.parent
        
        # Create conversation
        conversation = Conversation(agent=agent, workspace=str(workspace))
        
        logger.info("Starting feature implementation...")
        logger.info(f"Prompt: {prompt[:200]}...")
        
        # Run agent
        conversation.send_message(prompt)
        conversation.run()
        
        logger.info("Feature implementation completed")
        
        # Check if PR was created
        result = run_command("gh pr list --head feature/issue-{issue_number} --json number,url", check=False)
        
        if result.returncode == 0 and result.stdout:
            pr_data = json.loads(result.stdout)
            if pr_data:
                pr_url = pr_data[0]['url']
                return f"✅ **Feature implemented!**\n\nPull Request: {pr_url}"
        
        return "✅ **Feature implementation completed!**\n\nCheck the repository for changes."
    
    except ImportError:
        return "❌ **Error:** OpenHands SDK not installed. Cannot implement features automatically.\n\nPlease implement this manually or install the SDK."
    
    except Exception as e:
        return f"❌ **Error implementing feature:** {str(e)}"


def main():
    """Main entry point"""
    print("🤖 OpenLinks Agent starting...")
    
    # Get issue details from environment
    issue_number = get_env_or_exit("ISSUE_NUMBER")
    issue_title = get_env_or_exit("ISSUE_TITLE")
    issue_body = os.getenv("ISSUE_BODY", "")
    
    print(f"\n📋 Processing Issue #{issue_number}")
    print(f"Title: {issue_title}")
    print(f"Body: {issue_body[:100]}...")
    
    # Classify request
    print("\n🔍 Classifying request...")
    request_type = classify_request(issue_title, issue_body)
    print(f"✅ Classification: {request_type}")
    
    # Handle based on type
    if request_type == "LINK":
        print("\n🔗 Processing link operation...")
        
        # Parse the request
        request_text = f"{issue_title}\n{issue_body}"
        operation_data = parse_link_operation(request_text)
        
        print(f"Parsed operation: {json.dumps(operation_data, indent=2)}")
        
        # Execute operation
        result_message = handle_link_operation(operation_data, issue_number)
        
        print(f"\n{result_message}")
        
        # Comment on issue
        comment_on_issue(issue_number, result_message)
    
    else:  # FEATURE
        print("\n⚙️  Processing feature request...")
        
        result_message = handle_feature_request(issue_number, issue_title, issue_body)
        
        print(f"\n{result_message}")
        
        # Comment on issue
        comment_on_issue(issue_number, result_message)
    
    print("\n✅ OpenLinks Agent finished!")


if __name__ == "__main__":
    main()
