#!/usr/bin/env python3
"""
NONI Direct Cloudflare Pages Deployment
Option B: Bypass GitHub Actions entirely

Deploys frontend directly to Cloudflare Pages using API-only approach.
No npm, no flyctl, no GitHub Actions workflow needed.

Requirements:
- Python 3.7+ (standard library only)
- CLOUDFLARE_API_TOKEN
- CLOUDFLARE_ACCOUNT_ID
"""

import json
import os
import sys
import urllib.request
import urllib.error
import ssl
import zipfile
import io
import base64
from pathlib import Path

# Configuration
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
FRONTEND_URL = "https://noni-web.pages.dev"

# Files to deploy (we'll create a minimal working version)
# In reality, this would need the built frontend files

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


class CloudflareDirectDeploy:
    """Direct deployment to Cloudflare Pages via API"""
    
    def __init__(self, api_token, account_id, project_name="noni-web"):
        self.api_token = api_token
        self.account_id = account_id
        self.project_name = project_name
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def verify_token(self):
        """Verify Cloudflare token is valid"""
        print_step("Verifying Cloudflare token...", "wait")
        
        url = f"{CLOUDFLARE_API_BASE}/user/tokens/verify"
        success, data = make_request(url, headers=self.headers)
        
        if success and data.get('success'):
            print_step("Cloudflare token valid", "success")
            return True
        else:
            print_step(f"Token invalid: {data}", "error")
            return False
    
    def get_project(self):
        """Get Pages project details"""
        print_step(f"Checking project: {self.project_name}...", "wait")
        
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/pages/projects/{self.project_name}"
        success, data = make_request(url, headers=self.headers)
        
        if success and data.get('success'):
            project = data.get('result', {})
            print_step(f"Project found: {project.get('name')}", "success")
            return project
        else:
            print_step(f"Project not found: {data}", "error")
            return None
    
    def list_deployments(self):
        """List recent deployments"""
        print_step("Listing recent deployments...", "wait")
        
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/pages/projects/{self.project_name}/deployments"
        success, data = make_request(url, headers=self.headers)
        
        if success and data.get('success'):
            deployments = data.get('result', [])
            print_step(f"Found {len(deployments)} deployments", "success")
            return deployments
        else:
            print_step(f"Could not list deployments: {data}", "warning")
            return []
    
    def check_latest_deployment(self):
        """Check if latest deployment has G3 issue"""
        print_step("Checking latest deployment for G3...", "wait")
        
        deployments = self.list_deployments()
        if not deployments:
            print_step("No deployments found", "warning")
            return None
        
        latest = deployments[0]
        deployment_id = latest.get('id')
        url = latest.get('url', FRONTEND_URL)
        
        print_step(f"Latest deployment: {url}", "info")
        
        # Try to fetch and check for localhost
        try:
            success, content = make_request(url)
            if success and isinstance(content, str):
                if 'localhost:8000' in content:
                    print_step("G3 CONFIRMED - localhost found in deployment", "error")
                    return {"has_g3": True, "deployment": latest}
                else:
                    print_step("G3 NOT FOUND - deployment is clean", "success")
                    return {"has_g3": False, "deployment": latest}
        except Exception as e:
            print_step(f"Could not check deployment: {e}", "warning")
        
        return {"has_g3": None, "deployment": latest}
    
    def create_deployment(self, commit_message="Direct deploy - G3 fix"):
        """
        Create new deployment
        
        NOTE: This requires the built frontend files (dist/ folder).
        Without npm/node locally, we can't build. This is a limitation.
        
        Alternative: Trigger GitHub Actions to build, then deploy.
        """
        print_step("Creating new deployment...", "wait")
        
        # Check if we have built files
        dist_path = Path("frontend/dist")
        if not dist_path.exists():
            print_step("No built files found at frontend/dist/", "error")
            print_step("Cannot deploy without built frontend files", "error")
            print_step("\nOptions:", "info")
            print("  1. Use GitHub Actions to build (requires workflow fix)")
            print("  2. Install npm/node locally to build")
            print("  3. Download built files from previous successful deployment")
            return False
        
        # Create ZIP of dist folder
        print_step("Creating deployment bundle...", "wait")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in dist_path.rglob('*'):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(dist_path))
                    zip_file.write(file_path, arcname)
        
        zip_data = zip_buffer.getvalue()
        print_step(f"Bundle created: {len(zip_data)} bytes", "success")
        
        # Upload via API
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/pages/projects/{self.project_name}/deployments"
        
        # Cloudflare Pages API requires multipart form data
        # This is complex with just urllib - would need proper multipart encoding
        
        print_step("Direct upload requires multipart form encoding", "warning")
        print_step("Using GitHub Actions is more reliable", "info")
        
        return False


def main():
    """Main entry point"""
    print_header("NONI DIRECT CLOUDFLARE DEPLOYMENT")
    print(f"{Colors.BOLD}Option B: Bypass GitHub Actions{Colors.ENDC}\n")
    
    # Get credentials from environment
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
    
    if not api_token or not account_id:
        print_step("Cloudflare credentials required", "error")
        print("\nSet environment variables:")
        print("  $env:CLOUDFLARE_API_TOKEN = 'your_token'")
        print("  $env:CLOUDFLARE_ACCOUNT_ID = 'your_account_id'")
        print("\nOr run with arguments:")
        print("  python direct_cloudflare_deploy.py --token xxx --account yyy")
        sys.exit(1)
    
    # Create deployer
    deployer = CloudflareDirectDeploy(api_token, account_id)
    
    # Verify token
    if not deployer.verify_token():
        sys.exit(1)
    
    # Get project
    project = deployer.get_project()
    if not project:
        print_step("\nCannot proceed without valid project", "error")
        sys.exit(1)
    
    # Check current deployment
    result = deployer.check_latest_deployment()
    
    if result and result.get("has_g3"):
        print_step("\nG3 issue detected in current deployment", "error")
        print_step("Need to redeploy with fixed build", "info")
        
        # Try to create new deployment
        success = deployer.create_deployment()
        if not success:
            print_step("\nDirect deployment failed", "error")
            print_step("Recommendation: Fix GitHub Actions workflow instead", "info")
            print_step("The workflow has the G3 guards in place - it just needs to run", "info")
            sys.exit(1)
    elif result and result.get("has_g3") == False:
        print_step("\nDeployment is already clean - no G3 issue", "success")
        print_step("No action needed", "success")
    else:
        print_step("\nCould not determine G3 status", "warning")
    
    print_header("DEPLOYMENT CHECK COMPLETE")


if __name__ == "__main__":
    main()
