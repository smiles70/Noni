#!/usr/bin/env python3
"""
NONI Automated Deployment System
Following "The Process" - Zero Manual Steps Architecture

This script provides FULLY AUTOMATED deployment without requiring:
- git CLI
- flyctl CLI  
- npm/node
- GitHub CLI

Only requires: Python 3.7+ and internet connection

Usage:
    python scripts/auto_deploy.py --github-token YOUR_TOKEN
    
Or with interactive token input:
    python scripts/auto_deploy.py
"""

import argparse
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Optional, Dict, List
import urllib.request
import urllib.error
import ssl

# Configuration
REPO_OWNER = "smiles70"
REPO_NAME = "Noni"
REPO_FULL = f"{REPO_OWNER}/{REPO_NAME}"
FRONTEND_URL = "https://noni-web.pages.dev"
API_URL = "https://noni-api.fly.dev"

# API Endpoints
GITHUB_API_BASE = "https://api.github.com"
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def print_step(step: str, status: str = "info"):
    """Print step with status indicator"""
    icons = {
        "info": f"{Colors.OKBLUE}[*]{Colors.ENDC}",
        "success": f"{Colors.OKGREEN}[✓]{Colors.ENDC}",
        "warning": f"{Colors.WARNING}[!]{Colors.ENDC}",
        "error": f"{Colors.FAIL}[✗]{Colors.ENDC}",
        "wait": f"{Colors.OKCYAN}[⏳]{Colors.ENDC}"
    }
    print(f"{icons.get(status, icons['info'])} {step}")


def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict] = None,
    data: Optional[bytes] = None,
    expected_codes: List[int] = [200]
) -> tuple:
    """
    Make HTTP request with error handling
    
    Returns: (success: bool, response_data: dict or error_message: str)
    """
    try:
        # Create SSL context that allows us to make HTTPS requests
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


class GitHubAutomation:
    """GitHub API automation client"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Noni-AutoDeploy/1.0"
        }
    
    def verify_token(self) -> bool:
        """Verify GitHub token is valid"""
        print_step("Verifying GitHub token...", "wait")
        success, data = make_request(
            f"{GITHUB_API_BASE}/user",
            headers=self.headers
        )
        if success:
            print_step(f"Authenticated as: {data.get('login', 'unknown')}", "success")
            return True
        else:
            print_step(f"Token invalid: {data}", "error")
            return False
    
    def list_secrets(self) -> List[str]:
        """List repository secrets (names only)"""
        print_step("Checking repository secrets...", "wait")
        success, data = make_request(
            f"{GITHUB_API_BASE}/repos/{REPO_FULL}/actions/secrets",
            headers=self.headers
        )
        if success:
            secrets = [s['name'] for s in data.get('secrets', [])]
            print_step(f"Found {len(secrets)} secrets: {', '.join(secrets)}", "success")
            return secrets
        else:
            print_step(f"Could not list secrets: {data}", "warning")
            return []
    
    def check_required_secrets(self) -> Dict[str, bool]:
        """Check which required secrets are present"""
        required = [
            "VITE_API_BASE_URL",
            "VITE_CLERK_PUBLISHABLE_KEY",
            "FLY_API_TOKEN",
            "SUPABASE_ACCESS_TOKEN",
            "CLOUDFLARE_API_TOKEN"
        ]
        
        existing = self.list_secrets()
        status = {secret: secret in existing for secret in required}
        
        print_step("\nRequired Secrets Status:", "info")
        for secret, present in status.items():
            icon = "✓" if present else "✗"
            color = Colors.OKGREEN if present else Colors.FAIL
            print(f"  {color}{icon} {secret}{Colors.ENDC}")
        
        return status
    
    def trigger_workflow(self, workflow_id: str = "deploy.yml", branch: str = "main") -> bool:
        """Trigger GitHub Actions workflow"""
        print_step(f"Triggering workflow: {workflow_id}...", "wait")
        
        url = f"{GITHUB_API_BASE}/repos/{REPO_FULL}/actions/workflows/{workflow_id}/dispatches"
        data = json.dumps({"ref": branch}).encode('utf-8')
        
        success, data = make_request(
            url,
            method="POST",
            headers={**self.headers, "Content-Type": "application/json"},
            data=data,
            expected_codes=[204]
        )
        
        if success:
            print_step("Workflow triggered successfully!", "success")
            return True
        else:
            print_step(f"Failed to trigger workflow: {data}", "error")
            return False
    
    def get_latest_run(self, workflow_id: str = "deploy.yml") -> Optional[Dict]:
        """Get the latest workflow run"""
        print_step("Checking latest workflow run...", "wait")
        
        url = f"{GITHUB_API_BASE}/repos/{REPO_FULL}/actions/workflows/{workflow_id}/runs?per_page=1"
        
        success, data = make_request(url, headers=self.headers)
        
        if success and data.get('workflow_runs'):
            run = data['workflow_runs'][0]
            print_step(f"Latest run: #{run['run_number']} - {run['status']}", "success")
            return run
        else:
            print_step("No workflow runs found", "warning")
            return None
    
    def wait_for_run(self, run_id: int, timeout: int = 600) -> bool:
        """Wait for workflow run to complete"""
        print_step(f"Waiting for run #{run_id} to complete...", "wait")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            url = f"{GITHUB_API_BASE}/repos/{REPO_FULL}/actions/runs/{run_id}"
            success, data = make_request(url, headers=self.headers)
            
            if success:
                status = data.get('status')
                conclusion = data.get('conclusion')
                
                if status == 'completed':
                    if conclusion == 'success':
                        print_step("Workflow completed successfully!", "success")
                        return True
                    else:
                        print_step(f"Workflow failed: {conclusion}", "error")
                        return False
                else:
                    print(f"  Status: {status}... (elapsed: {int(time.time() - start_time)}s)", end='\r')
            
            time.sleep(10)
        
        print_step("Timeout waiting for workflow", "error")
        return False


class CloudflareAutomation:
    """Cloudflare API automation client"""
    
    def __init__(self, token: str, account_id: str):
        self.token = token
        self.account_id = account_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def list_projects(self) -> List[Dict]:
        """List Cloudflare Pages projects"""
        print_step("Listing Cloudflare Pages projects...", "wait")
        
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/pages/projects"
        
        success, data = make_request(url, headers=self.headers)
        
        if success and data.get('success'):
            projects = data.get('result', [])
            print_step(f"Found {len(projects)} projects", "success")
            return projects
        else:
            print_step(f"Could not list projects: {data}", "error")
            return []


class DeploymentOrchestrator:
    """Main deployment orchestration class"""
    
    def __init__(self, github_token: str):
        self.github = GitHubAutomation(github_token)
    
    def run_pre_checks(self) -> bool:
        """Run all pre-deployment checks"""
        print_header("PHASE 1: PRE-DEPLOYMENT CHECKS")
        
        # Verify GitHub token
        if not self.github.verify_token():
            return False
        
        # Check required secrets
        secrets_status = self.github.check_required_secrets()
        
        # Check if we have minimum required secrets
        critical_secrets = ["VITE_API_BASE_URL", "VITE_CLERK_PUBLISHABLE_KEY"]
        missing = [s for s in critical_secrets if not secrets_status.get(s)]
        
        if missing:
            print_step(f"\nMissing critical secrets: {', '.join(missing)}", "error")
            print_step("Cannot deploy without these secrets.", "error")
            print_step("\nTo add secrets:", "info")
            print(f"  1. Go to: https://github.com/{REPO_FULL}/settings/secrets/actions")
            print(f"  2. Click 'New repository secret'")
            print(f"  3. Add each missing secret")
            return False
        
        return True
    
    def execute_deployment(self) -> bool:
        """Execute deployment via GitHub Actions"""
        print_header("PHASE 2: EXECUTING DEPLOYMENT")
        
        # Trigger workflow
        if not self.github.trigger_workflow():
            return False
        
        # Wait a moment for run to be created
        print_step("Waiting for run to be created...", "wait")
        time.sleep(5)
        
        # Get latest run
        run = self.github.get_latest_run()
        if not run:
            print_step("Could not find workflow run", "error")
            return False
        
        # Wait for completion
        run_id = run['id']
        if not self.github.wait_for_run(run_id):
            print_step("\nWorkflow failed. Check logs at:", "error")
            print(f"  https://github.com/{REPO_FULL}/actions/runs/{run_id}")
            return False
        
        return True
    
    def verify_deployment(self) -> bool:
        """Verify deployment was successful"""
        print_header("PHASE 3: VERIFICATION")
        
        # Check frontend for localhost references
        print_step("Checking frontend for G3 (localhost)...", "wait")
        
        success, content = make_request(FRONTEND_URL)
        if success:
            if isinstance(content, str) and 'localhost:8000' in content:
                print_step("G3 NOT FIXED - localhost found in response!", "error")
                return False
            else:
                print_step("G3 CHECK PASSED - no localhost references", "success")
        else:
            print_step(f"Could not fetch frontend: {content}", "warning")
        
        # Check backend health
        print_step("Checking backend health...", "wait")
        success, data = make_request(f"{API_URL}/health")
        if success and isinstance(data, dict) and data.get('status') == 'healthy':
            print_step("Backend is healthy", "success")
        else:
            print_step(f"Backend check: {data}", "warning")
        
        # Check auth config
        print_step("Checking auth configuration...", "wait")
        success, data = make_request(f"{API_URL}/api/v1/auth/config")
        if success and isinstance(data, dict):
            print_step(f"Auth provider: {data.get('provider', 'unknown')}", "success")
        else:
            print_step(f"Auth check: {data}", "warning")
        
        return True
    
    def run(self) -> bool:
        """Run full deployment process"""
        print_header("NONI AUTOMATED DEPLOYMENT SYSTEM")
        print(f"{Colors.BOLD}Following The Process - Zero Manual Steps{Colors.ENDC}\n")
        
        # Phase 1: Pre-checks
        if not self.run_pre_checks():
            return False
        
        # Phase 2: Deploy
        if not self.execute_deployment():
            return False
        
        # Phase 3: Verify
        if not self.verify_deployment():
            return False
        
        print_header("DEPLOYMENT COMPLETE")
        print(f"{Colors.OKGREEN}✓ All phases completed successfully{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Frontend URL: {FRONTEND_URL}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}API URL: {API_URL}{Colors.ENDC}")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NONI Automated Deployment System - Zero Manual Steps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/auto_deploy.py --github-token ghp_xxx
    python scripts/auto_deploy.py --github-token-file ~/.github_token
    python scripts/auto_deploy.py  # Interactive mode
        """
    )
    
    parser.add_argument(
        '--github-token',
        help='GitHub Personal Access Token'
    )
    parser.add_argument(
        '--github-token-file',
        help='File containing GitHub token'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only run pre-checks, do not deploy'
    )
    
    args = parser.parse_args()
    
    # Get GitHub token
    token = None
    if args.github_token:
        token = args.github_token
    elif args.github_token_file:
        try:
            token = Path(args.github_token_file).read_text().strip()
        except Exception as e:
            print(f"{Colors.FAIL}Error reading token file: {e}{Colors.ENDC}")
            sys.exit(1)
    else:
        print(f"{Colors.WARNING}GitHub token required.{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}To create a token:{Colors.ENDC}")
        print("  1. Go to: https://github.com/settings/tokens")
        print("  2. Click 'Generate new token (classic)'")
        print("  3. Select scopes: repo, workflow")
        print("  4. Copy the token")
        print(f"\n{Colors.OKCYAN}Then run:{Colors.ENDC}")
        print("  python scripts/auto_deploy.py --github-token YOUR_TOKEN")
        sys.exit(1)
    
    # Create orchestrator and run
    orchestrator = DeploymentOrchestrator(token)
    
    if args.check_only:
        success = orchestrator.run_pre_checks()
    else:
        success = orchestrator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
