import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".commitwise"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "provider": "openai",
    "model": "gpt-4",
    "style": "conventional",
    "max_length": 72,
    "locale": "en",
    "temperature": 0.3,
    "scope_detection": True,
}


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load():
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return {**DEFAULTS, **json.load(f)}
    return dict(DEFAULTS)


def save(config):
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def set_key(key, value):
    config = load()
    config[key] = value
    save(config)


def get_api_key(provider):
    env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    env_var = env_map.get(provider)
    if env_var:
        key = os.getenv(env_var)
        if key:
            return key
    config = load()
    return config.get(f"{provider}_api_key")
