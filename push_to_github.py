import os
import sys
import getpass
from dulwich import porcelain

REPO_TARGET_URL = "https://github.com/trvismaya93-wq/useless_project.git"

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print("  WakeVerify -> GitHub Push Utility (Pure Python Git)")
    print("=" * 60)
    print(f"Target Repository: {REPO_TARGET_URL}")
    print()

    repo = porcelain.open_repo(project_dir)

    # 1. Stage all pending changes
    print("[1/4] Staging modified and new files...")
    porcelain.add(repo, paths=["."])

    # 2. Check status and commit if dirty
    status = porcelain.status(repo)
    if status.staged["add"] or status.staged["modify"] or status.staged["delete"]:
        print("[2/4] Committing local changes...")
        commit_msg = b"feat: update WakeVerify files, launcher, and documentation"
        commit_sha = porcelain.commit(repo, message=commit_msg, author=b"WakeVerify <wakeverify@example.com>")
        print(f"      Committed SHA: {commit_sha.decode('utf-8')[:8]}")
    else:
        print("[2/4] Working tree is clean.")

    # 3. Ensure refs/heads/main points to current HEAD
    repo.refs[b"refs/heads/main"] = repo.head()
    print(f"[3/4] Head commit on 'main': {repo.head().decode('utf-8')[:8]}")

    # 4. Get GitHub Personal Access Token
    token = os.environ.get("GITHUB_TOKEN")
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()

    if not token:
        print()
        print("GitHub requires a Personal Access Token (PAT) to authorize pushes.")
        print("You can generate one in 30 seconds:")
        print("  1. Visit: https://github.com/settings/tokens/new")
        print("  2. Note: 'WakeVerify Push'")
        print("  3. Check the scope: 'repo' (Full control of private repositories)")
        print("  4. Click 'Generate token' and copy the 'ghp_...' token.")
        print()
        try:
            token = getpass.getpass("Enter your GitHub Personal Access Token (hidden input): ").strip()
        except Exception:
            token = input("Enter your GitHub Personal Access Token: ").strip()

    if not token:
        print("[ERROR] Token cannot be empty. Push aborted.")
        sys.exit(1)

    # Build authenticated remote URL
    auth_url = f"https://{token}@github.com/trvismaya93-wq/useless_project.git"

    print()
    print(f"[4/4] Pushing to https://github.com/trvismaya93-wq/useless_project.git (main branch)...")
    try:
        result = porcelain.push(
            repo,
            auth_url,
            refspecs=b"refs/heads/main",
            force=True
        )
        print()
        print("=" * 60)
        print("  SUCCESS! Project successfully pushed to GitHub!")
        print("  View at: https://github.com/trvismaya93-wq/useless_project")
        print("=" * 60)
    except Exception as e:
        print()
        print(f"[ERROR] Push failed: {e}")
        print("Please verify that your GitHub token has 'repo' write permissions.")
        sys.exit(1)

if __name__ == "__main__":
    main()
