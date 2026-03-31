# Project Status Slide Creator

A **Streamlit + Ollama** application that automatically generates professional PowerPoint slide decks from weekly project status updates. Chat with an AI assistant to collect structured project information, then generate beautifully formatted 5-slide presentations.

## Features

🤖 **AI-Powered Status Collection** — Guided Q&A interface with Ollama (llama3, llama2, mistral, etc.)

📊 **Automatic Slide Generation** — 5-slide PowerPoint decks with dark theme, styled with python-pptx

💾 **Project Management** — Full CRUD for projects, tasks, timelines, and milestones

📝 **Update History** — Persistent storage of all chats and generated slides

🔄 **Offline First** — All processing happens locally; no cloud dependencies

## Prerequisites

- **Python 3.11+**
- **Ollama** installed and running locally
- A local LLM model (e.g., phi3:mini)

### Install Ollama

Visit [https://ollama.ai](https://ollama.ai) and download Ollama for your OS.

### Pull a Model

```bash
ollama pull llama3
```

(Or: `llama2`, `mistral`, etc.)

### Start Ollama Server

```bash
ollama serve
```

The server will run on `http://localhost:11434` by default.

## Installation

1. Clone or download this project
2. Navigate to the project directory
3. Create a Python virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Project Structure

```
project_status_reporter/
├── app.py                  # Main Streamlit app (5 pages)
├── projects.py             # Project CRUD operations
├── settings.py             # Ollama config & model management
├── ai_chat.py              # Ollama API integration & conversation logic
├── slide_builder.py        # PowerPoint generation (python-pptx)
├── requirements.txt
├── README.md
├── data/
│   └── projects/           # {project_name}.json files
├── slides/
│   └── {project_name}/     # Generated .pptx files
└── templates/
    └── slide_preview.js    # In-app slide preview renderer
```

## Data Model

Each project is stored as a JSON file with this structure:

```json
{
  "project_name": "My Project",
  "owner": "John Doe",
  "team_members": ["John Doe", "Jane Smith"],
  "timeline": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "milestones": [
      {"label": "MVP Release", "date": "2024-03-31"},
      {"label": "Beta Launch", "date": "2024-06-30"}
    ]
  },
  "tasks": [
    {
      "id": "uuid",
      "description": "Build API",
      "responsible": "John",
      "status": "in_progress",
      "due_date": "2024-02-15"
    }
  ],
  "updates": [
    {
      "date": "2024-01-15",
      "results_so_far": "- Completed user authentication\n- Set up database",
      "next_steps": "- Build API endpoints\n- Write tests",
      "raw_chat_log": [...],
      "slide_path": "slides/My Project/My Project_2024-01-15.pptx"
    }
  ]
}
```

## Usage

### 1. **Home Page** (🏠)
- View all projects
- Create new projects
- Delete existing projects

### 2. **Project Detail** (📁)
- Edit project metadata (name, owner, team)
- Define timeline and milestones
- Manage tasks (add/edit/delete)
- Initiate AI update session

### 3. **AI Update** (🤖) — MAIN FEATURE
- **One-question-at-a-time chat** with Ollama
- AI asks about: task completion, results, blockers, next steps, timeline changes
- AI automatically determines when conversation is complete
- Extracts structured data (results, next steps, task status changes)
- Preview and generate PowerPoint slide deck

### 4. **Slides** (📊)
- Browse all generated slide decks for a project
- Download .pptx files
- View interactive slide preview

### 5. **Settings** (⚙️)
- Select Ollama model
- Configure Ollama base URL
- View Ollama connection status

## PowerPoint Slide Template

Each generated deck contains 5 slides with a dark professional theme:

1. **Title Slide** — Project name, owner, date, team
2. **Results So Far** — Bulleted achievements
3. **Task Status** — Color-coded table (green=done, yellow=in progress, red=not started)
4. **Next Steps** — Bulleted action items
5. **Timeline** — Milestone bar with visual representation

Colors:
- Background: `#1E1E2E` (dark)
- Accent: `#7C3AED` (purple)
- Text: `#FFFFFF` (white)

## Troubleshooting

### "Cannot connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check that it's on `http://localhost:11434` (or set custom URL in Settings)
- Verify model is available: `ollama list`

### Slow responses
- Check your internet/network (if running Ollama on different machine)
- Try a smaller model: `ollama pull mistral`
- Increase timeout in `settings.py` if needed

### .pptx files not generating
- Ensure `slides/` directory is writable
- Check python-pptx version: `pip install --upgrade python-pptx`

## API Integration

The app calls Ollama's `/api/chat` endpoint (non-streaming mode):

```
POST http://localhost:11434/api/chat
{
  "model": "llama3",
  "messages": [{"role": "user", "content": "..."}],
  "stream": false,
  "system": "..."
}
```

Responses include full project context to maintain conversation coherence.

## Requirements

See `requirements.txt`:
- `streamlit>=1.35.0`
- `python-pptx>=0.6.23`
- `requests>=2.31.0`

## License

Open source. Feel free to modify and distribute.

## Support

For questions or issues, refer to:
- [Streamlit docs](https://docs.streamlit.io)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [python-pptx docs](https://python-pptx.readthedocs.io)