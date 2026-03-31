"""
AI chat logic - handle Ollama API calls and conversation flow.
"""
import json
import requests
from typing import Generator, Optional
import settings as settings_module


def build_system_prompt(project: dict, update_history: str) -> str:
    """Build the system prompt for the AI with full project context."""
    return f"""You are a project status assistant helping to collect a weekly project update.

Project Context:
{json.dumps(project, indent=2)}

Update History:
{update_history if update_history else "No previous updates."}

Your role:
- Ask one question at a time about the project status
- Be concise and professional
- Adapt questions based on previous answers
- Follow this logical order (but adapt based on context):
  1. Ask about completion of each task that was "in_progress" or "not_started"
  2. Ask about new results or achievements since the last update
  3. Ask about blockers or risks
  4. Ask about next steps for the coming week
  5. Ask if any new tasks should be added
  6. Ask if the timeline has changed

Stop asking questions when you have enough information (typically 5-8 questions).
When done, respond with: "UPDATE_COMPLETE: [your summary]"
"""


def build_extraction_prompt() -> str:
    """Build the system prompt for extracting structured data from the conversation."""
    return """You are a data extraction assistant. 
    
Extract the following information from the conversation and return ONLY valid JSON, no explanation, no markdown:
{
  "results_so_far": "bullet points of what was accomplished",
  "next_steps": "bullet points of what will be done next",
  "task_updates": {
    "task_description_substring": "new_status"
  }
}"""


def chat_with_ollama(messages: list, system_prompt: str, timeout: float = 60.0) -> str:
    """
    Send a chat request to Ollama and get the response.
    
    Args:
        messages: List of message dicts with "role" and "content"
        system_prompt: System prompt to set context
        timeout: Request timeout in seconds
        
    Returns:
        The assistant's response text
    """
    base_url = settings_module.get_ollama_base_url()
    model = settings_module.get_model()
    
    # Validate model exists
    available_models = settings_module.get_available_models(timeout=5.0)
    if available_models and model not in available_models:
        # Try with :latest tag
        if f"{model}:latest" in available_models:
            model = f"{model}:latest"
        else:
            available_str = ", ".join(available_models) if available_models else "No models found"
            raise ValueError(f"Model '{model}' not found. Available models: {available_str}")
    
    url = f"{base_url}/api/chat"
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "system": system_prompt
    }
    
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        
        # Handle different error codes
        if response.status_code == 404:
            # Model not found
            raise ValueError(f"Model '{model}' returned 404. Verify the model is installed with 'ollama pull {model}'")
        elif response.status_code == 400:
            error_detail = response.text
            raise ValueError(f"Bad request to Ollama: {error_detail}")
        
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Ollama request timed out after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Could not connect to Ollama at {base_url}")
    except (ValueError, requests.exceptions.HTTPError) as e:
        raise e
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}")


def generate_first_question(project: dict) -> str:
    """Generate the first question for a project update."""
    update_history = ""
    if project.get("updates"):
        last_update = project["updates"][-1]
        update_history = f"Last update ({last_update['date']}):\nResults: {last_update['results_so_far']}\nNext steps: {last_update['next_steps']}"
    
    system_prompt = build_system_prompt(project, update_history)
    messages = [{"role": "user", "content": "Start the weekly status update interview."}]
    
    response = chat_with_ollama(messages, system_prompt)
    return response


def ask_next_question(chat_history: list, project: dict) -> str:
    """Ask the next question based on chat history."""
    update_history = ""
    if project.get("updates"):
        last_update = project["updates"][-1]
        update_history = f"Last update ({last_update['date']}):\nResults: {last_update['results_so_far']}\nNext steps: {last_update['next_steps']}"
    
    system_prompt = build_system_prompt(project, update_history)
    response = chat_with_ollama(chat_history, system_prompt)
    return response


def extract_update_data(chat_history: list) -> dict:
    """
    Extract structured data from the completed chat.
    
    Returns:
        dict with 'results_so_far', 'next_steps', and 'task_updates'
    """
    system_prompt = build_extraction_prompt()
    messages = [
        *chat_history,
        {"role": "user", "content": "Extract the update information as JSON."}
    ]
    
    response = chat_with_ollama(messages, system_prompt)
    
    # Try to parse JSON from response
    try:
        # If response contains markdown code block, extract it
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback: return the conversation as context
        return {
            "results_so_far": "See conversation history",
            "next_steps": "See conversation history",
            "task_updates": {}
        }
