import sys
import os
from dulwich import porcelain

project_dir = os.path.dirname(os.path.abspath(__file__))

def init_git():
    print(f"Initializing Git repository in: {project_dir}")
    repo = porcelain.init(project_dir)
    print("Adding files to repository...")
    porcelain.add(repo, paths=["."])
    print("Committing files...")
    commit_sha = porcelain.commit(repo, message=b"feat: initial commit for WakeVerify AI accountability alarm", author=b"WakeVerify <wakeverify@example.com>")
    print(f"Initial commit created successfully! Commit SHA: {commit_sha.decode('utf-8')}")

def push_git(remote_url):
    repo = porcelain.open_repo(project_dir)
    print(f"Pushing to remote: {remote_url}")
    porcelain.push(repo, remote_url, "refs/heads/main")
    print("Push complete!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "push":
        if len(sys.argv) < 3:
            print("Usage: py init_and_push.py push <GITHUB_REPO_URL>")
            sys.exit(1)
        push_git(sys.argv[2])
    else:
        init_git()
