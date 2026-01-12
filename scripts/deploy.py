#!/usr/bin/env python
"""
Deploy to DataRobot Custom Applications.

Usage:
    python scripts/deploy.py              # Build and create new app
    python scripts/deploy.py --update     # Build and update existing app
    python scripts/deploy.py --build-only # Only build, don't deploy

Configuration is loaded from .env file in the project root.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")
    print("Install with: pip install python-dotenv")

# Configuration from environment
ENV_ID = os.getenv("DATAROBOT_ENV_ID", "")
APP_NAME = os.getenv("DATAROBOT_APP_NAME", "Hello World App")
APP_ID = os.getenv("DATAROBOT_APP_ID", "")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DEPLOY_DIR = PROJECT_ROOT / "deploy"
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DEPLOY_CONFIG_DIR = PROJECT_ROOT / "deploy-config"


def run(cmd: list[str], cwd: Path = PROJECT_ROOT, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command with output."""
    cmd_str = " ".join(str(c) for c in cmd)
    print(f"\n> {cmd_str}")

    # Use shell=True on Windows for npm commands
    use_shell = os.name == 'nt' and any(c in ['npm', 'npx', 'drapps', 'pip'] for c in cmd)

    if use_shell:
        return subprocess.run(cmd_str, cwd=cwd, check=check, shell=True)
    else:
        return subprocess.run(cmd, cwd=cwd, check=check)


def run_capture(cmd: list[str], cwd: Path = PROJECT_ROOT) -> str | None:
    """Run a command and capture output."""
    try:
        cmd_str = " ".join(str(c) for c in cmd)
        use_shell = os.name == 'nt'

        result = subprocess.run(
            cmd_str if use_shell else cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=use_shell
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def copy_dir(src: Path, dest: Path) -> None:
    """Recursively copy a directory."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def clean_deploy_dir() -> None:
    """Remove and recreate the deploy directory."""
    print("\n[1/5] Cleaning deploy directory...")
    if DEPLOY_DIR.exists():
        shutil.rmtree(DEPLOY_DIR)
    DEPLOY_DIR.mkdir()


def build_frontend() -> None:
    """Build the frontend React application."""
    print("\n[2/5] Building frontend...")
    run(["npm", "install"], cwd=FRONTEND_DIR)
    run(["npm", "run", "build"], cwd=FRONTEND_DIR)


def copy_backend() -> None:
    """Copy backend Python files to deploy directory."""
    print("\n[3/5] Copying backend files...")
    backend_files = ["main.py", "config.py", "agent_client.py", "llm_client.py", "requirements.txt"]
    for filename in backend_files:
        src = BACKEND_DIR / filename
        if src.exists():
            shutil.copy(src, DEPLOY_DIR / filename)
            print(f"  Copied {filename}")
        else:
            print(f"  Warning: {filename} not found")


def copy_frontend() -> None:
    """Copy built frontend to deploy directory."""
    print("\n[4/5] Copying frontend build...")
    frontend_dist = FRONTEND_DIR / "dist"
    if frontend_dist.exists():
        dest = DEPLOY_DIR / "frontend" / "dist"
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy_dir(frontend_dist, dest)
        print("  Copied frontend/dist/")
    else:
        print("  ERROR: frontend/dist not found! Run 'npm run build' in frontend/")
        sys.exit(1)


def copy_deploy_config() -> None:
    """Copy deployment configuration files."""
    print("\n[5/5] Copying deployment config...")
    config_files = ["start-app.sh", "metadata.yaml"]
    for filename in config_files:
        src = DEPLOY_CONFIG_DIR / filename
        if src.exists():
            shutil.copy(src, DEPLOY_DIR / filename)
            print(f"  Copied {filename}")
        else:
            print(f"  Warning: {filename} not found in deploy-config/")


def build() -> None:
    """Build the complete deployment package."""
    print("=" * 60)
    print("PHASE 1: Building Deployment Package")
    print("=" * 60)

    clean_deploy_dir()
    build_frontend()
    copy_backend()
    copy_frontend()
    copy_deploy_config()

    print("\n" + "=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)
    print(f"\nDeploy directory: {DEPLOY_DIR}")
    print("\nContents:")
    for item in sorted(DEPLOY_DIR.rglob("*")):
        if item.is_file():
            rel_path = item.relative_to(DEPLOY_DIR)
            print(f"  {rel_path}")


def check_drapps() -> bool:
    """Verify drapps CLI is installed."""
    # Try to find drapps using shutil.which or by running it
    import shutil

    # First check if drapps is in PATH
    drapps_path = shutil.which("drapps")
    if drapps_path:
        print(f"\ndrapps CLI found: {drapps_path}")
        return True

    # Try running drapps --help as fallback
    try:
        result = subprocess.run(
            "drapps --help",
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 or "Usage: drapps" in (result.stdout + result.stderr):
            print("\ndrapps CLI found")
            return True
    except Exception:
        pass

    print("\nWARNING: drapps CLI not found.")
    print("Install with: pip install git+https://github.com/datarobot/dr-apps")
    return False


def get_app_id_by_name(app_name: str) -> str | None:
    """Find existing app ID by name."""
    print(f"\nLooking for existing app '{app_name}'...")
    output = run_capture(["drapps", "ls", "apps"])
    if output:
        for line in output.split("\n"):
            if app_name in line:
                # Extract 24-character hex ID
                match = re.search(r"([a-f0-9]{24})", line)
                if match:
                    print(f"  Found app ID: {match.group(1)}")
                    return match.group(1)
    print(f"  App '{app_name}' not found")
    return None


def deploy(update_mode: bool = False) -> None:
    """Deploy to DataRobot."""
    print("\n" + "=" * 60)
    print("PHASE 2: Deploying to DataRobot")
    print("=" * 60)

    if not check_drapps():
        print("\nCannot deploy without drapps CLI.")
        print("Install it and run again, or deploy manually:")
        print(f'  drapps create --name "{APP_NAME}" --base-env <env_id> ./deploy')
        return

    if update_mode:
        app_id = APP_ID or get_app_id_by_name(APP_NAME)
        if app_id:
            print(f"\nUpdating existing app (ID: {app_id})...")
            # drapps uses 'publish' to update an existing app
            run(["drapps", "publish", "-i", app_id, "-s", f"{APP_NAME}Source"])
        else:
            print(f"\nApp '{APP_NAME}' not found. Creating new app...")
            if not ENV_ID:
                print("ERROR: DATAROBOT_ENV_ID not set in .env")
                print("Run 'drapps ls envs' to find available environment IDs")
                sys.exit(1)
            run(["drapps", "create", APP_NAME, "--base-env", ENV_ID, "--path", str(DEPLOY_DIR)])
    else:
        if not ENV_ID:
            print("ERROR: DATAROBOT_ENV_ID not set in .env")
            print("Run 'drapps ls envs' to find available environment IDs")
            sys.exit(1)
        print(f"\nCreating new app '{APP_NAME}'...")
        print(f"Environment ID: {ENV_ID}")
        run(["drapps", "create", APP_NAME, "--base-env", ENV_ID, "--path", str(DEPLOY_DIR)])

    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Go to DataRobot > Custom Applications")
    print(f'2. Find "{APP_NAME}"')
    print("3. Configure Runtime Parameters if needed")
    print("4. Start the application")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and deploy to DataRobot Custom Applications"
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Only build the deployment package, don't deploy"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing app instead of creating new"
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("DataRobot Custom Application Deployment")
    print("=" * 60)
    print(f"App Name: {APP_NAME}")
    print(f"Mode: {'Build Only' if args.build_only else 'Update' if args.update else 'Create New'}")

    if not ENV_ID and not args.build_only:
        print(f"\nWarning: DATAROBOT_ENV_ID not set in .env")

    # Build
    build()

    # Deploy (unless build-only)
    if not args.build_only:
        deploy(update_mode=args.update)
    else:
        print("\n--build-only specified. Skipping deployment.")
        print(f"\nTo deploy manually:")
        if ENV_ID:
            print(f'  drapps create "{APP_NAME}" --base-env {ENV_ID} --path ./deploy')
        else:
            print(f'  drapps create "{APP_NAME}" --base-env <env_id> --path ./deploy')
            print("\nFirst, find your environment ID:")
            print("  drapps ls envs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n\nDeployment failed: Command returned non-zero exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nDeployment failed: {e}")
        sys.exit(1)
