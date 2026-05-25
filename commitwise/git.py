import subprocess
import os


def get_staged_diff():
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError("Not a git repository or no git available.")

    stat_output = result.stdout.strip()
    if not stat_output:
        raise RuntimeError("No staged changes found. Run `git add` first.")

    diff_result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True, text=True
    )
    return diff_result.stdout


def get_branch_diff(base_branch="main"):
    result = subprocess.run(
        ["git", "diff", f"origin/{base_branch}...HEAD", "--stat"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        result = subprocess.run(
            ["git", "diff", base_branch, "--stat"],
            capture_output=True, text=True
        )
    if result.returncode != 0 or not result.stdout.strip():
        return get_staged_diff()

    diff_result = subprocess.run(
        ["git", "diff", f"origin/{base_branch}...HEAD"],
        capture_output=True, text=True
    )
    if not diff_result.stdout.strip():
        diff_result = subprocess.run(
            ["git", "diff", base_branch],
            capture_output=True, text=True
        )
    return diff_result.stdout


def get_current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_changed_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def commit(message):
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Commit failed: {result.stderr}")
    return result.stdout
