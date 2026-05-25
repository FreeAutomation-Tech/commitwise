# CommitWise ✨

> **AI-powered commit messages that actually make sense — because "fixed stuff" isn't a message.**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/FreeAutomation-Tech/commitwise?style=social)](https://github.com/FreeAutomation-Tech/commitwise)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![CI](https://github.com/FreeAutomation-Tech/commitwise/actions/workflows/ci.yml/badge.svg)](https://github.com/FreeAutomation-Tech/commitwise/actions)

---

## 🚀 The Problem

```bash
git commit -m "fixed stuff"
git commit -m "updated files"
git commit -m "changes"
```

We've all been there. CommitWise fixes this by analyzing **what you actually changed** and generating meaningful commit messages.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🤖 AI-Powered** | Uses GPT-4, Claude, or local Ollama models |
| **🎨 Multiple Styles** | Conventional Commits, Gitmoji, or custom templates |
| **⚡ Blazing Fast** | Streams results in under 2 seconds |
| **🎯 Interactive Picker** | Browse suggestions, pick, edit — all in terminal |
| **🔧 Fully Configurable** | Max length, language, tone, scope detection |
| **🔄 Git Hook Ready** | Pre-commit hook support out of the box |
| **🚀 PR Descriptions** | Generate PR descriptions from branch diffs |
| **📦 Zero Friction** | `pip install` and go |

## 📦 Installation

```bash
pip install commitwise

# Or from source:
git clone https://github.com/FreeAutomation-Tech/commitwise.git
cd commitwise
pip install -e .
```

## 🎬 Quick Start

```bash
# 1. Set your API key (OpenAI, Anthropic, or Ollama)
commitwise config set OPENAI_API_KEY sk-...

# 2. Stage your changes
git add .

# 3. Generate commit messages
commitwise generate
```

You'll see something like:

```
┌──────────────────────────────────────────────┐
│  CommitWise — 4 suggestions ready            │
├──────────────────────────────────────────────┤
│  1. feat(auth): add JWT refresh token flow   │
│  2. fix(auth): resolve token expiry handling │
│  3. refactor(auth): extract token logic      │
│  4. style(auth): format auth middleware      │
│                                              │
│  [1-4] Pick  │  [e] Edit  │  [r] Regenerate │
│  [q] Quit    │  [c] Custom                  │
└──────────────────────────────────────────────┘
```

## 🎮 Commands

```bash
# Generate commit messages from staged changes
commitwise generate

# Generate + commit in one go
commitwise commit

# Generate PR description from branch diff
commitwise pr-describe

# Configure settings
commitwise config set OPENAI_API_KEY sk-...
commitwise config set style conventional   # conventional | gitmoji | plain
commitwise config set max_length 72
commitwise config set locale en

# View current config
commitwise config show

# Install pre-commit hook
commitwise install-hook
```

## ⚙️ Configuration

CommitWise looks for config in `~/.commitwise/config.json`:

```json
{
  "provider": "openai",
  "model": "gpt-4",
  "style": "conventional",
  "max_length": 72,
  "locale": "en",
  "temperature": 0.3,
  "scope_detection": true
}
```

### Providers

| Provider | Model | Env Variable |
|----------|-------|-------------|
| OpenAI | `gpt-4`, `gpt-3.5-turbo` | `OPENAI_API_KEY` |
| Anthropic | `claude-3-opus`, `claude-3-sonnet` | `ANTHROPIC_API_KEY` |
| Ollama | `llama3`, `codellama`, `mistral` | _(none — local)_ |

## 🔧 As a GitHub Action

```yaml
# .github/workflows/pr-description.yml
name: Auto PR Description
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  describe:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Generate PR Description
        uses: FreeAutomation-Tech/commitwise@main
        with:
          api_key: ${{ secrets.OPENAI_API_KEY }}
          mode: pr-describe
```

## 🏗️ Architecture

```
commitwise/
├── __init__.py          # Package info
├── __main__.py          # python -m entrypoint
├── cli.py               # CLI interface (argparse)
├── git.py               # Git diff parser & extraction
├── ai.py                # AI provider abstraction layer
├── config.py            # Configuration manager
└── ...
```

## 🤝 Contributing

PRs are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

Quick start for contributors:

```bash
git clone https://github.com/FreeAutomation-Tech/commitwise.git
cd commitwise
pip install -e ".[dev]"
pre-commit install
```

## 📄 License

MIT — see [LICENSE](LICENSE).

## ⭐ Support

If CommitWise saves you from writing one more "fixed stuff" message, give it a star ⭐

---

<p align="center">
  Made with ❤️ for developers who care about their git history.
</p>
