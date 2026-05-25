import argparse
import sys

from commitwise import __version__
from commitwise.config import load, set_key
from commitwise.git import get_staged_diff, get_branch_diff, commit, get_current_branch, get_changed_files
from commitwise.ai import generate_messages


def print_header():
    print("╔══════════════════════════════════════════╗")
    print("║     CommitWise ✨  v" + __version__.ljust(21) + "║")
    print("║     AI-Powered Commit Messages           ║")
    print("╚══════════════════════════════════════════╝")
    print()


def print_suggestions(messages):
    if not messages:
        print("⚠ No suggestions generated.")
        return

    print("┌──────────────────────────────────────────────┐")
    print("│  CommitWise — {} suggestions ready            │".format(len(messages)))
    print("├──────────────────────────────────────────────┤")
    for i, msg in enumerate(messages, 1):
        padding = " " * (44 - len(msg))
        print(f"│  {i}. {msg}{padding}│")
    print("├──────────────────────────────────────────────┤")
    print("│  [1-{}] Pick  │  [r] Regenerate  │  [q] Quit  │".format(len(messages)))
    print("└──────────────────────────────────────────────┘")


def cmd_generate(args):
    config = load()
    try:
        diff = get_staged_diff()
    except RuntimeError as e:
        print(f"⚠ {e}")
        return

    print_header()
    print(f"📂 Changed files: {', '.join(get_changed_files())}")
    print(f"🔍 Analyzing with {config.get('provider', 'openai')}...\n")

    try:
        messages = generate_messages(diff, config)
    except RuntimeError as e:
        print(f"⚠ Generation failed: {e}")
        return
    except Exception as e:
        print(f"⚠ Unexpected error: {e}")
        return

    print_suggestions(messages)

    if not messages:
        return

    while True:
        try:
            choice = input("\n⌨ Select: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if choice == "q":
            return
        elif choice == "r":
            return cmd_generate(args)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(messages):
                selected = messages[idx]
                print(f"\n✅ Selected: {selected}")
                return selected
        print("Invalid choice. Try again.")


def cmd_commit(args):
    selected = cmd_generate(args)
    if selected:
        print(f"\n📦 Committing...")
        try:
            result = commit(selected)
            print(f"✅ {result.strip()}")
        except RuntimeError as e:
            print(f"⚠ {e}")
            proceed = input("Commit manually? (y/n): ").strip().lower()
            if proceed == "y":
                print(f"\n  git commit -m \"{selected}\"")


def cmd_pr_describe(args):
    config = load()
    branch = get_current_branch()
    print_header()
    print(f"📂 Branch: {branch}")
    print(f"🔍 Generating PR description...\n")

    try:
        diff = get_branch_diff(args.base)
    except RuntimeError as e:
        print(f"⚠ {e}")
        return

    config_copy = dict(config)
    config_copy["style"] = "plain"
    config_copy["max_length"] = 200

    prompt = (
        "You are a senior engineer writing a PR description. "
        "Given this diff, write:\n"
        "1. A short summary title\n"
        "2. What changed and why\n"
        "3. Key technical details\n"
        "Return ONLY the description text.\n\n"
        f"Diff:\n{diff[:6000]}"
    )

    try:
        from commitwise.ai import _call_openai
        result = _call_openai(prompt, config)
        if isinstance(result, list):
            result = "\n".join(result)
        print(result)
    except Exception as e:
        print(f"⚠ PR description generation failed: {e}")


def cmd_config(args):
    if args.config_command == "show":
        config = load()
        print_header()
        print("Current configuration:\n")
        for key, value in config.items():
            if "api_key" in key.lower():
                value = value[:8] + "..." if value else "(not set)"
            print(f"  {key}: {value}")
    elif args.config_command == "set":
        if not args.key or not args.value:
            print("Usage: commitwise config set <key> <value>")
            return
        set_key(args.key, args.value)
        print(f"✅ Set {args.key} = {args.value}")
    else:
        print("Usage: commitwise config <show|set>")


def cmd_install_hook(args):
    hook_content = """#!/bin/sh
exec commitwise commit
"""
    import subprocess
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("⚠ Not a git repository.")
        return

    git_dir = result.stdout.strip()
    hook_path = f"{git_dir}/hooks/pre-commit"

    with open(hook_path, "w") as f:
        f.write(hook_content)

    import os
    os.chmod(hook_path, 0o755)
    print(f"✅ Pre-commit hook installed at {hook_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="commitwise",
        description="AI-powered commit message generator",
    )
    parser.add_argument(
        "--version", action="version", version=f"commitwise {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    p_gen = subparsers.add_parser("generate", help="Generate commit messages")
    p_gen.set_defaults(func=cmd_generate)

    p_com = subparsers.add_parser("commit", help="Generate and commit")
    p_com.set_defaults(func=cmd_commit)

    p_pr = subparsers.add_parser("pr-describe", help="Generate PR description")
    p_pr.add_argument("--base", default="main", help="Base branch")
    p_pr.set_defaults(func=cmd_pr_describe)

    p_cfg = subparsers.add_parser("config", help="Manage configuration")
    p_cfg.add_argument("config_command", nargs="?", default="show", choices=["show", "set"])
    p_cfg.add_argument("key", nargs="?")
    p_cfg.add_argument("value", nargs="?")
    p_cfg.set_defaults(func=cmd_config)

    p_hook = subparsers.add_parser("install-hook", help="Install pre-commit hook")
    p_hook.set_defaults(func=cmd_install_hook)

    args = parser.parse_args()

    if not args.command:
        args.command = "generate"
        args.func = cmd_generate

    args.func(args)


if __name__ == "__main__":
    main()
