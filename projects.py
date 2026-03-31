"""
Project CRUD operations - manage project data stored as JSON files.
"""
import json
import os
from datetime import datetime
from pathlib import Path
import uuid


DATA_DIR = Path("data/projects")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_project_path(project_name: str) -> Path:
    """Get the file path for a project."""
    return DATA_DIR / f"{project_name}.json"


def create_project(project_name: str, owner: str) -> dict:
    """Create a new project with default structure."""
    project = {
        "project_name": project_name,
        "owner": owner,
        "team_members": [owner],
        "timeline": {
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": "",
            "milestones": []
        },
        "tasks": [],
        "updates": []
    }
    save_project(project)
    return project


def load_project(project_name: str) -> dict:
    """Load a project from JSON file."""
    path = get_project_path(project_name)
    if not path.exists():
        raise FileNotFoundError(f"Project '{project_name}' not found")
    
    with open(path, "r") as f:
        return json.load(f)


def save_project(project: dict) -> None:
    """Save a project to JSON file."""
    path = get_project_path(project["project_name"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(project, f, indent=2)


def delete_project(project_name: str) -> None:
    """Delete a project file."""
    path = get_project_path(project_name)
    if path.exists():
        path.unlink()


def list_projects() -> list:
    """List all project names."""
    return [f.stem for f in DATA_DIR.glob("*.json")]


def project_exists(project_name: str) -> bool:
    """Check if a project exists."""
    return get_project_path(project_name).exists()


def add_task(project: dict, description: str, responsible: str, due_date: str) -> dict:
    """Add a task to a project."""
    task = {
        "id": str(uuid.uuid4()),
        "description": description,
        "responsible": responsible,
        "status": "not_started",
        "due_date": due_date
    }
    project["tasks"].append(task)
    return task


def update_task(project: dict, task_id: str, **kwargs) -> None:
    """Update a task by ID."""
    for task in project["tasks"]:
        if task["id"] == task_id:
            task.update(kwargs)
            break


def delete_task(project: dict, task_id: str) -> None:
    """Delete a task by ID."""
    project["tasks"] = [t for t in project["tasks"] if t["id"] != task_id]


def add_update(project: dict, results_so_far: str, next_steps: str, 
               raw_chat_log: list, slide_path: str = "") -> dict:
    """Add an update entry to project history."""
    update = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "results_so_far": results_so_far,
        "next_steps": next_steps,
        "raw_chat_log": raw_chat_log,
        "slide_path": slide_path
    }
    project["updates"].append(update)
    return update


def get_last_update(project: dict) -> dict:
    """Get the most recent update, or None if no updates exist."""
    if project["updates"]:
        return project["updates"][-1]
    return None
