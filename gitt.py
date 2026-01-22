import os
import time
import subprocess
from threading import Lock

# Thread-safe lock for git operations
_git_lock = Lock()

# Track if git config has been set
_git_configured = False


def _run_git_command(
    cmd: str, cwd: str | None = None, hide_output: bool = False
) -> tuple[bool, str]:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
        if not hide_output:
            print(f"[gitt.py] Command: {cmd[:50]}... -> {'OK' if success else 'FAIL'}")
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def _ensure_git_configured(repo_dir: str) -> None:
    """Configure git user if not already done."""
    global _git_configured
    if _git_configured:
        return

    username = os.environ.get("NEWSPAPER_URLS_USERNAME", "newspaper-bot")
    email = os.environ.get("NEWSPAPER_URLS_USEREMAIL", "bot@example.com")

    _run_git_command(f'git config user.name "{username}"', cwd=repo_dir)
    _run_git_command(f'git config user.email "{email}"', cwd=repo_dir)
    _git_configured = True
    print("[gitt.py] Git user configured")


def commit_file(file_path: str, commit_message: str) -> str:
    """
    Thread-safe function to commit a specific file.

    Args:
        file_path: Path to the file to commit (relative to repo root)
        commit_message: Commit message

    Returns:
        String with operation result
    """
    repo_dir = os.environ.get("NEWSPAPER_URLS_GIT_REPO", "newspaper-bot-urls")

    with _git_lock:
        print(f"[gitt.py] Committing: {file_path} - {commit_message}")

        # Ensure we're in the right directory
        if not os.path.isdir(repo_dir):
            return f"[gitt.py] Error: Repository directory '{repo_dir}' not found"

        _ensure_git_configured(repo_dir)

        # Get just the filename for git add (file is already in repo dir)
        filename = os.path.basename(file_path)

        # Check if file has changes
        success, status = _run_git_command(
            f"git status --porcelain {filename}", cwd=repo_dir
        )
        if not status.strip():
            print(f"[gitt.py] No changes in {filename}, skipping commit")
            return f"No changes in {filename}"

        # Stage the file
        success, output = _run_git_command(f"git add {filename}", cwd=repo_dir)
        if not success:
            return f"[gitt.py] Failed to stage {filename}: {output}"

        # Commit
        success, output = _run_git_command(
            f'git commit -m "{commit_message}"', cwd=repo_dir
        )
        if not success and "nothing to commit" not in output:
            return f"[gitt.py] Failed to commit {filename}: {output}"

        # Push
        git_username = os.environ.get("NEWSPAPER_URLS_GIT_USERNAME")
        git_token = os.environ.get("GIT_TOKEN")
        git_repo = os.environ.get("NEWSPAPER_URLS_GIT_REPO")

        push_url = f"https://{git_username}:{git_token}@github.com/{git_username}/{git_repo}.git"
        success, output = _run_git_command(
            f"git push {push_url}", cwd=repo_dir, hide_output=True
        )

        if success:
            result = f"[gitt.py] Committed and pushed: {filename}"
            print(result)
            return result
        else:
            # Try pull and push again in case of conflict
            print(f"[gitt.py] Push failed, trying pull --rebase...")
            _run_git_command("git pull --rebase", cwd=repo_dir)
            success, output = _run_git_command(
                f"git push {push_url}", cwd=repo_dir, hide_output=True
            )
            if success:
                result = f"[gitt.py] Committed and pushed (after rebase): {filename}"
                print(result)
                return result
            else:
                return f"[gitt.py] Failed to push {filename}: {output}"


def gitTask():
    """
    Legacy function - commits all changes at once.
    Kept for backward compatibility.
    """
    print("[gitt.py] Starting git operations to save URL data...")
    all_output = ""

    repo_dir = os.environ.get("NEWSPAPER_URLS_GIT_REPO", "newspaper-bot-urls")

    if not os.path.isdir(repo_dir):
        return f"Error: Repository directory '{repo_dir}' not found"

    with _git_lock:
        _ensure_git_configured(repo_dir)

        # Check if there are any changes
        success, status = _run_git_command("git status --porcelain", cwd=repo_dir)
        if not status.strip():
            print("[gitt.py] No changes to commit")
            return "No changes to commit"

        # Stage all changes
        success, output = _run_git_command("git add .", cwd=repo_dir)
        all_output += output

        # Commit
        success, output = _run_git_command('git commit -m "Added urls"', cwd=repo_dir)
        all_output += output

        if not success and "nothing to commit" in output:
            print("[gitt.py] Nothing to commit")
            return "Nothing to commit"

        # Push
        git_username = os.environ.get("NEWSPAPER_URLS_GIT_USERNAME")
        git_token = os.environ.get("GIT_TOKEN")
        git_repo = os.environ.get("NEWSPAPER_URLS_GIT_REPO")

        push_url = f"https://{git_username}:{git_token}@github.com/{git_username}/{git_repo}.git"
        success, output = _run_git_command(
            f"git push {push_url}", cwd=repo_dir, hide_output=True
        )

        if success:
            all_output += "Push successful\n"
        else:
            all_output += f"Push failed: {output}\n"

    print("[gitt.py] Git operations completed")
    return all_output
