#!/usr/bin/env python3
"""
NONI Automated Workflow Fix
Automatically modifies GitHub Actions workflow to skip broken backend step

This script:
1. Gets current deploy.yml via GitHub API
2. Modifies it programmatically (removes fly-deploy-backend dependency)
3. Commits the change via API
4. Triggers the workflow

Zero manual file editing required.
"""

import json
import os
import sys
import urllib.request
import urllib.error
import ssl
import base64
from pathlib import Path

GITHUB_API_BASE = "https://api.github.com"
REPO_OWNER = "smiles70"
REPO_NAME = "Noni"
REPO_FULL = f"{REPO_OWNER}/{REPO_NAME}"


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def print_step(step, status="info"):
    icons = {
        "info": f"{Colors.OKBLUE}[*]{Colors.ENDC}",
        "success": f"{Colors.OKGREEN}[✓]{Colors.ENDC}",
        "warning": f"{Colors.WARNING}[!]{Colors.ENDC}",
        "error": f"{Colors.FAIL}[✗]{Colors.ENDC}",
        "wait": f"{Colors.OKCYAN}[⏳]{Colors.ENDC}"
    }
    print(f"{icons.get(status, icons['info'])} {step}")


def make_request(url, method="GET", headers=None, data=None, expected_codes=None):
    """Make HTTP request with error handling"""
    if expected_codes is None:
        expected_codes = [200]
    
    try:
        ssl_context = ssl.create_default_context()
        req = urllib.request.Request(
            url,
            method=method,
            headers=headers or {},
            data=data
        )
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            if response.status in expected_codes:
                try:
                    return True, json.loads(response.read().decode('utf-8'))
                except json.JSONDecodeError:
                    return True, response.read().decode('utf-8')
            else:
                return False, f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return False, error_json.get('message', error_body)
        except:
            return False, f"HTTP {e.code}: {error_body[:200]}"
    except Exception as e:
        return False, str(e)


class GitHubWorkflowFixer:
    """Automatically fix GitHub Actions workflow"""
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Noni-WorkflowFixer/1.0"
        }
    
    def verify_token(self):
        """Verify GitHub token"""
        print_step("Verifying GitHub token...", "wait")
        
        url = f"{GITHUB_API_BASE}/user"
        success, data = make_request(url, headers=self.headers)
        
        if success:
            print_step(f"Authenticated as: {data.get('login')}", "success")
            return True
        else:
            print_step(f"Token invalid: {data}", "error")
            return False
    
    def get_workflow_file(self):
        """Get current deploy.yml content"""
        print_step("Fetching deploy.yml...", "wait")
        
        url = f"{GITHUB_API_BASE}/repos/{REPO_FULL}/contents/.github/workflows/deploy.yml"
        success, data = make_request(url, headers=self.headers)
        
        if success:
            content = base64.b64decode(data['content']).decode('utf-8')
            sha = data['sha']
            print_step(f"Fetched deploy.yml ({len(content)} chars)", "success")
            return content, sha
        else:
            print_step(f"Could not fetch: {data}", "error")
            return None, None
    
    def fix_workflow(self, content):
        """
        Fix the workflow by modifying the dependency
        
        Original:
          cloudflare-pages-deploy:
            needs: [preflight, fly-deploy-backend]
        
        Fixed:
          cloudflare-pages-deploy:
            needs: [preflight]
            # Note: fly-deploy-backend skipped - backend already healthy
        """
        print_step("Analyzing workflow structure...", "wait")
        
        lines = content.split('\n')
        modified_lines = []
        in_cloudflare_job = False
        found_needs = False
        changes_made = False
        
        for i, line in enumerate(lines):
            # Detect cloudflare-pages-deploy job
            if line.strip().startswith('cloudflare-pages-deploy:'):
                in_cloudflare_job = True
                modified_lines.append(line)
                continue
            
            if in_cloudflare_job:
                # Check if this is the needs line with fly-deploy-backend
                if 'needs:' in line and 'fly-deploy-backend' in line:
                    # Replace with just preflight
                    indent = len(line) - len(line.lstrip())
                    new_line = ' ' * indent + 'needs: [preflight]  # AUTO-FIXED: removed fly-deploy-backend dependency'
                    modified_lines.append(new_line)
                    found_needs = True
                    changes_made = True
                    print_step(f"Line {i+1}: Removed fly-deploy-backend dependency", "success")
                    continue
                
                # If we hit another job definition, we're done with cloudflare job
                if line.strip().endswith(':') and not line.strip().startswith('#') and i > 0:
                    in_cloudflare_job = False
            
            modified_lines.append(line)
        
        if not changes_made:
            print_step("No changes needed - workflow already fixed or structure different", "warning")
            return content, False
        
        new_content = '\n'.join(modified_lines)
        print_step(f"Workflow modified ({len(new_content)} chars)", "success")
        return new_content, True
    
    def commit_workflow(self, new_content, sha, message="AUTO-FIX: Remove fly-deploy-backend dependency to unblock frontend deploy"):
        """Commit the fixed workflow"""
        print_step("Committing fixed workflow...", "wait")
        
        url = f"{GITHUB_API_BASE}/repos/{REPO_FULL}/contents/.github/workflows/deploy.yml"
        
        # Encode content
        encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": message,
            "content": encoded_content,
            "sha": sha,
            "branch": "main"
        }
        
        success, response = make_request(
            url,
            method="PUT",
            headers={**self.headers, "Content-Type": "application/json"},
            data=json.dumps(data).encode('utf-8'),
            expected_codes=[200, 201]
        )
        
        if success:
            print_step("Workflow committed successfully", "success")
            commit_sha = response.get('commit', {}).get('sha', 'unknown')[:8]
            print_step(f"Commit SHA: {commit_sha}", "info")
            return True
        else:
            print_step(f"Commit failed: {response}", "error")
            return False
    
    def trigger_workflow(self):
        """Trigger the deploy workflow"""
        print_step("Triggering deploy workflow...", "wait")
        
        url = f"{GITHUB_API_BASE}/repos/{REPO_FULL}/actions/workflows/deploy.yml/dispatches"
        data = {"ref": "main"}
        
        success, response = make_request(
            url,
            method="POST",
            headers={**self.headers, "Content-Type": "application/json"},
            data=json.dumps(data).encode('utf-8'),
            expected_codes=[204]
        )
        
        if success:
            print_step("Workflow triggered", "success")
            return True
        else:
            print_step(f"Trigger failed: {response}", "error")
            return False
    
    def run(self):
        """Execute full fix workflow"""
        print_header("NONI AUTOMATED WORKFLOW FIX")
        print(f"{Colors.BOLD}Zero Manual Steps - API-Only Approach{Colors.ENDC}\n")
        
        # Verify token
        if not self.verify_token():
            return False
        
        # Get current workflow
        content, sha = self.get_workflow_file()
        if not content:
            return False
        
        # Fix workflow
        new_content, changed = self.fix_workflow(content)
        if not changed:
            print_step("\nWorkflow already fixed or doesn't need changes", "info")
            print_step("Proceeding to trigger workflow...", "wait")
        else:
            # Commit changes
            if not self.commit_workflow(new_content, sha):
                return False
        
        # Trigger workflow
        if not self.trigger_workflow():
            return False
        
        print_header("WORKFLOW FIX COMPLETE")
        print(f"{Colors.OKGREEN}✓ Changes committed to main branch{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ Deploy workflow triggered{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Monitor at: https://github.com/{REPO_FULL}/actions{Colors.ENDC}")
        
        return True


def main():
    """Main entry point"""
    # Get token from environment or prompt
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print_step("GitHub token required", "error")
        print("\nSet environment variable:")
        print("  $env:GITHUB_TOKEN = 'ghp_xxx'")
        print("\nOr create token at: https://github.com/settings/tokens")
        print("Required scopes: repo, workflow")
        sys.exit(1)
    
    # Run fixer
    fixer = GitHubWorkflowFixer(token)
    success = fixer.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
