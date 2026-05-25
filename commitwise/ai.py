import json
import urllib.request
import urllib.error


def generate_messages(diff, config):
    provider = config.get("provider", "openai")
    style = config.get("style", "conventional")
    max_length = config.get("max_length", 72)
    locale = config.get("locale", "en")
    temperature = config.get("temperature", 0.3)

    prompt = _build_prompt(diff, style, max_length, locale)

    if provider == "openai":
        return _call_openai(prompt, config)
    elif provider == "anthropic":
        return _call_anthropic(prompt, config)
    elif provider == "ollama":
        return _call_ollama(prompt, config)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _build_prompt(diff, style, max_length, locale):
    style_guide = {
        "conventional": (
            "Use Conventional Commits format: "
            "<type>(<scope>): <description>\n"
            "Types: feat, fix, refactor, chore, docs, style, test, perf, ci, build, revert"
        ),
        "gitmoji": "Prefix each commit with a relevant gitmoji (e.g. ✨, 🐛, ♻️, 📝)",
        "plain": "Write clear, imperative-mood commit messages without prefixes",
    }.get(style, "Use Conventional Commits format")

    return f"""You are an expert git commit message generator. Analyze the git diff below.

Rules:
- {style_guide}
- Max {max_length} characters per line
- Language: {locale}
- Use imperative mood ("Add feature" not "Added feature")
- Detect the scope from file/module names
- Generate exactly 4 distinct, meaningful suggestions
- Return ONLY a JSON array of strings, no other text

Diff:
{diff[:8000]}"""


def _call_openai(prompt, config):
    api_key = config.get("openai_api_key") or config.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not set. Use: commitwise config set OPENAI_API_KEY sk-...")

    model = config.get("model", "gpt-4")
    temperature = config.get("temperature", 0.3)

    data = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a commit message generator. Return only JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": 500,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            return _parse_json_response(content)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"OpenAI API error ({e.code}): {body}")


def _call_anthropic(prompt, config):
    api_key = config.get("anthropic_api_key") or config.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Anthropic API key not set.")

    model = config.get("model", "claude-3-haiku-20240307")
    temperature = config.get("temperature", 0.3)

    data = json.dumps({
        "model": model,
        "max_tokens": 500,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            content = result["content"][0]["text"]
            return _parse_json_response(content)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Anthropic API error ({e.code}): {body}")


def _call_ollama(prompt, config):
    model = config.get("model", "llama3")
    temperature = config.get("temperature", 0.3)

    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result.get("response", "")
            return _parse_json_response(content)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Ollama error ({e.code}): {body}")
    except urllib.error.URLError:
        raise RuntimeError(
            "Cannot connect to Ollama. Is it running? (ollama serve)"
        )


def _parse_json_response(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        content = content.rsplit("\n", 1)[0]
        if content.endswith("```"):
            content = content[:-3]
    content = content.strip()

    try:
        messages = json.loads(content)
        if isinstance(messages, list) and all(isinstance(m, str) for m in messages):
            return messages[:4]
    except json.JSONDecodeError:
        pass

    lines = [l.strip().strip('"').strip("'") for l in content.split("\n") if l.strip()]
    messages = [l for l in lines if l and not l.startswith("[") and not l.startswith("]")]
    return messages[:4]
