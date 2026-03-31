"""
Settings management - Ollama configuration and model selection.
"""
import json
import requests
import socket
from pathlib import Path


SETTINGS_PATH = Path("data/settings.json")


def get_hostname() -> str:
    """
    Get the actual hostname for use in Codespaces or local environments.
    Returns the CODESPACE_NAME if available, otherwise the machine hostname.
    """
    import os
    
    # For GitHub Codespaces
    if "CODESPACE_NAME" in os.environ:
        return os.environ["CODESPACE_NAME"]
    
    # For local environments
    try:
        return socket.gethostname()
    except Exception:
        return "localhost"


def get_default_settings() -> dict:
    """Get default settings."""
    hostname = get_hostname()
    return {
        "ollama_base_url": f"http://{hostname}:11434",
        "model": "qwen3:14b"
    }


def load_settings() -> dict:
    """Load settings from file or return defaults."""
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return get_default_settings()


def save_settings(settings: dict) -> None:
    """Save settings to file."""
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


def get_model() -> str:
    """Get the selected model name."""
    settings = load_settings()
    return settings.get("model", "llama3")


def set_model(model_name: str) -> None:
    """Set the selected model."""
    settings = load_settings()
    settings["model"] = model_name
    save_settings(settings)


def get_ollama_base_url() -> str:
    """Get the Ollama base URL."""
    settings = load_settings()
    return settings.get("ollama_base_url", "http://localhost:11434")


def set_ollama_base_url(url: str) -> None:
    """Set the Ollama base URL."""
    settings = load_settings()
    settings["ollama_base_url"] = url
    save_settings(settings)


def check_ollama_connection(timeout: float = 5.0) -> bool:
    """Check if Ollama is running by querying the tags endpoint."""
    try:
        base_url = get_ollama_base_url()
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def get_available_models(timeout: float = 5.0) -> list:
    """Get list of available local models from Ollama."""
    try:
        base_url = get_ollama_base_url()
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            return [m["name"] for m in models]
        return []
    except Exception:
        return []
