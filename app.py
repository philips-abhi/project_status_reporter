"""
Project Status Slide Creator - Main Streamlit Application
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import projects
import settings as settings_module
import ai_chat
import slide_builder
from uuid import uuid4


# Configure Streamlit
st.set_page_config(page_title="Project Status Slide Creator", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "current_project" not in st.session_state:
    st.session_state.current_project = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "update_complete" not in st.session_state:
    st.session_state.update_complete = False
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None


# Sidebar Navigation
st.sidebar.title("Project Status Slide Creator")

pages = {
    "🏠 Home": "home",
    "📁 Project Detail": "project_detail",
    "🤖 AI Update": "ai_update",
    "📊 Slides": "slides",
    "⚙️ Settings": "settings"
}

page_choice = st.sidebar.radio("Navigate", list(pages.keys()), format_func=lambda x: x)
st.session_state.current_page = pages[page_choice]

# Display current project if selected
if st.session_state.current_project:
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"📋 {st.session_state.current_project}")
    if st.sidebar.button("Clear Selection"):
        st.session_state.current_project = None
        st.rerun()


# PAGE: HOME
def page_home():
    st.title("🏠 All Projects")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Your Projects")
    with col2:
        if st.button("➕ New Project"):
            st.session_state.show_new_project_form = True
    
    # New project form
    if st.session_state.get("show_new_project_form", False):
        st.markdown("---")
        with st.form("new_project_form"):
            col1, col2 = st.columns(2)
            with col1:
                project_name = st.text_input("Project Name")
            with col2:
                owner = st.text_input("Owner")
            
            if st.form_submit_button("Create Project"):
                if project_name and owner:
                    if projects.project_exists(project_name):
                        st.error("Project already exists!")
                    else:
                        projects.create_project(project_name, owner)
                        st.toast(f"✅ Project '{project_name}' created!")
                        st.session_state.show_new_project_form = False
                        st.rerun()
                else:
                    st.error("Please fill in both fields")
    
    # List projects
    project_list = projects.list_projects()
    if not project_list:
        st.info("No projects yet. Create one!")
    else:
        for proj_name in project_list:
            try:
                proj = projects.load_project(proj_name)
                last_update = projects.get_last_update(proj)
                last_update_date = last_update["date"] if last_update else "Never"
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"### {proj['project_name']}")
                    st.caption(f"Owner: {proj['owner']} | Last update: {last_update_date}")
                
                with col2:
                    if st.button("Open", key=f"open_{proj_name}"):
                        st.session_state.current_project = proj_name
                        st.session_state.current_page = "project_detail"
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_{proj_name}"):
                        st.session_state.confirm_delete = proj_name
                
                # Confirm delete
                if st.session_state.get("confirm_delete") == proj_name:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❌ Confirm Delete"):
                            projects.delete_project(proj_name)
                            st.toast(f"🗑️ Project deleted")
                            st.session_state.confirm_delete = None
                            st.rerun()
                    with col2:
                        if st.button("Cancel"):
                            st.session_state.confirm_delete = None
                            st.rerun()
                
                st.markdown("---")
            except Exception as e:
                st.error(f"Error loading project {proj_name}: {e}")


# PAGE: PROJECT DETAIL
def page_project_detail():
    if not st.session_state.current_project:
        st.warning("No project selected. Go to Home and open a project.")
        return
    
    proj = projects.load_project(st.session_state.current_project)
    st.title(f"📁 {proj['project_name']}")
    
    # Handle milestone removal (before form)
    for i in range(len(proj["timeline"]["milestones"])):
        if st.session_state.get(f"rm_milestone_{i}"):
            proj["timeline"]["milestones"].pop(i)
            projects.save_project(proj)
            st.session_state[f"rm_milestone_{i}"] = False
            st.rerun()
    
    # Handle task removal (before form)
    for i in range(len(proj["tasks"])):
        if st.session_state.get(f"rm_task_{i}"):
            proj["tasks"].pop(i)
            projects.save_project(proj)
            st.session_state[f"rm_task_{i}"] = False
            st.rerun()
    
    # Main form for editing
    with st.form("project_detail_form"):
        col1, col2 = st.columns(2)
        with col1:
            proj["project_name"] = st.text_input("Project Name", value=proj["project_name"])
            proj["owner"] = st.text_input("Owner", value=proj["owner"])
        
        with col2:
            st.markdown("### Team Members")
            team_input = st.text_area("Team Members (one per line)", value="\n".join(proj.get("team_members", [])))
            proj["team_members"] = [t.strip() for t in team_input.split("\n") if t.strip()]
        
        st.markdown("### Timeline")
        col1, col2 = st.columns(2)
        with col1:
            proj["timeline"]["start_date"] = st.date_input("Start Date", 
                value=datetime.strptime(proj["timeline"]["start_date"], "%Y-%m-%d").date()).strftime("%Y-%m-%d")
        with col2:
            proj["timeline"]["end_date"] = st.date_input("End Date",
                value=datetime.strptime(proj["timeline"]["end_date"], "%Y-%m-%d").date() if proj["timeline"]["end_date"] else datetime.now().date()).strftime("%Y-%m-%d")
        
        st.markdown("### Milestones")
        milestones = proj["timeline"]["milestones"]
        for i, milestone in enumerate(milestones):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                milestone["label"] = st.text_input(f"Label {i+1}", value=milestone["label"], key=f"m_label_{i}")
            with col2:
                milestone["date"] = st.date_input(f"Date {i+1}", 
                    value=datetime.strptime(milestone["date"], "%Y-%m-%d").date(), key=f"m_date_{i}").strftime("%Y-%m-%d")
        
        st.markdown("### Tasks")
        tasks = proj["tasks"]
        for i, task in enumerate(tasks):
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.2, 1, 0.5])
            with col1:
                task["description"] = st.text_input(f"Task {i+1}", value=task["description"], key=f"t_desc_{i}")
            with col2:
                task["responsible"] = st.text_input("Responsible", value=task["responsible"], key=f"t_resp_{i}")
            with col3:
                task["status"] = st.selectbox("Status", ["not_started", "in_progress", "done"], 
                    index=["not_started", "in_progress", "done"].index(task["status"]), key=f"t_status_{i}")
            with col4:
                task["due_date"] = st.date_input("Due", 
                    value=datetime.strptime(task["due_date"], "%Y-%m-%d").date(), key=f"t_due_{i}").strftime("%Y-%m-%d")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save"):
                projects.save_project(proj)
                st.toast("✅ Project saved!")
        
        with col2:
            if st.form_submit_button("Start AI Update"):
                st.session_state.current_project = proj["project_name"]
                st.session_state.current_page = "ai_update"
                st.session_state.chat_history = []
                st.session_state.update_complete = False
                st.rerun()
    
    # Buttons outside form for adding/removing items
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Add Milestone"):
            proj["timeline"]["milestones"].append({"label": "", "date": datetime.now().strftime("%Y-%m-%d")})
            projects.save_project(proj)
            st.rerun()
    
    with col2:
        if st.button("➕ Add Task"):
            projects.add_task(proj, "", "", datetime.now().strftime("%Y-%m-%d"))
            projects.save_project(proj)
            st.rerun()
    
    # Remove buttons for milestones
    if proj["timeline"]["milestones"]:
        st.markdown("**Remove Milestones:**")
        cols = st.columns(len(proj["timeline"]["milestones"]))
        for i, milestone in enumerate(proj["timeline"]["milestones"]):
            with cols[i]:
                if st.button(f"Remove: {milestone['label']}", key=f"rm_milestone_{i}"):
                    st.session_state[f"rm_milestone_{i}"] = True
                    st.rerun()
    
    # Remove buttons for tasks
    if proj["tasks"]:
        st.markdown("**Remove Tasks:**")
        cols = st.columns(min(3, len(proj["tasks"])))
        for i, task in enumerate(proj["tasks"]):
            with cols[i % 3]:
                task_label = task["description"][:30] + "..." if len(task["description"]) > 30 else task["description"]
                if st.button(f"Remove: {task_label}", key=f"rm_task_{i}"):
                    st.session_state[f"rm_task_{i}"] = True
                    st.rerun()


# PAGE: AI UPDATE
def page_ai_update():
    if not st.session_state.current_project:
        st.warning("No project selected.")
        return
    
    proj = projects.load_project(st.session_state.current_project)
    st.title(f"🤖 Weekly Update - {proj['project_name']}")
    
    # Check Ollama connection
    ollama_connected = settings_module.check_ollama_connection()
    if not ollama_connected:
        st.error("❌ Cannot connect to Ollama. Make sure it's running at " + settings_module.get_ollama_base_url())
        return
    
    # Check available models
    available_models = settings_module.get_available_models()
    current_model = settings_module.get_model()
    
    if not available_models:
        st.warning("⚠️ No models found. Run in terminal: `ollama pull llama3`")
        return
    
    if current_model not in available_models and f"{current_model}:latest" not in available_models:
        st.error(f"❌ Model '{current_model}' not found.")
        st.info(f"Available models: {', '.join(available_models)}")
        st.info(f"To use a model, run: `ollama pull {available_models[0]}`")
        return
    
    # Initialize chat if needed
    if not st.session_state.chat_history:
        try:
            with st.spinner("Starting conversation..."):
                first_question = ai_chat.generate_first_question(proj)
            st.session_state.chat_history = [
                {"role": "assistant", "content": first_question}
            ]
        except ValueError as e:
            st.error(f"❌ Model Error: {e}")
            st.info(f"Available models: {', '.join(available_models)}")
            return
        except (TimeoutError, ConnectionError) as e:
            st.error(f"❌ Connection Error: {e}")
            return
        except Exception as e:
            st.error(f"❌ Error starting conversation: {e}")
            return
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Check if update is complete
    if st.session_state.update_complete:
        st.success("✅ Update conversation complete!")
        
        if st.session_state.extracted_data:
            st.markdown("---")
            st.markdown("### Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Results So Far:**")
                st.write(st.session_state.extracted_data.get("results_so_far", ""))
            
            with col2:
                st.markdown("**Next Steps:**")
                st.write(st.session_state.extracted_data.get("next_steps", ""))
            
            if st.button("📊 Generate Slide"):
                try:
                    with st.spinner("Generating PowerPoint..."):
                        slide_path = slide_builder.generate_slides(
                            proj,
                            st.session_state.extracted_data.get("results_so_far", ""),
                            st.session_state.extracted_data.get("next_steps", "")
                        )
                    
                    # Update project with new update and task status changes
                    projects.add_update(
                        proj,
                        st.session_state.extracted_data.get("results_so_far", ""),
                        st.session_state.extracted_data.get("next_steps", ""),
                        st.session_state.chat_history,
                        slide_path
                    )
                    
                    # Apply task status updates
                    task_updates = st.session_state.extracted_data.get("task_updates", {})
                    for task in proj["tasks"]:
                        for key, new_status in task_updates.items():
                            if key.lower() in task["description"].lower():
                                task["status"] = new_status
                    
                    projects.save_project(proj)
                    st.toast(f"✅ Slide generated: {slide_path}")
                    st.session_state.chat_history = []
                    st.session_state.update_complete = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating slide: {e}")
        
        return
    
    # User input
    user_input = st.chat_input("Your response...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Check if conversation should end
        if "done" in user_input.lower() or "finished" in user_input.lower() or "complete" in user_input.lower():
            st.session_state.update_complete = True
            st.session_state.extracted_data = ai_chat.extract_update_data(st.session_state.chat_history)
            st.rerun()
        
        try:
            with st.spinner("Getting next question..."):
                response = ai_chat.ask_next_question(st.session_state.chat_history, proj)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Check if AI says it's done
            if "UPDATE_COMPLETE:" in response or "done asking" in response.lower():
                st.session_state.update_complete = True
                st.session_state.extracted_data = ai_chat.extract_update_data(st.session_state.chat_history)
            
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.chat_history.pop()


# PAGE: SLIDES
def page_slides():
    if not st.session_state.current_project:
        st.warning("No project selected.")
        return
    
    proj = projects.load_project(st.session_state.current_project)
    st.title(f"📊 Slides - {proj['project_name']}")
    
    slides_dir = Path(f"slides/{proj['project_name']}")
    if not slides_dir.exists():
        st.info("No slides generated yet.")
        return
    
    slide_files = sorted(list(slides_dir.glob("*.pptx")), reverse=True)
    
    if not slide_files:
        st.info("No slides found.")
        return
    
    st.markdown("### Generated Slides")
    for slide_file in slide_files:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{slide_file.name}**")
        with col2:
            st.caption(f"Size: {slide_file.stat().st_size / 1024:.1f} KB")
        with col3:
            with open(slide_file, "rb") as f:
                st.download_button(
                    "⬇️ Download",
                    f,
                    file_name=slide_file.name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    key=f"download_{slide_file.name}"
                )
    
    # Slide preview
    st.markdown("---")
    st.markdown("### Slide Preview")
    
    latest_update = projects.get_last_update(proj)
    if latest_update:
        preview_data = {
            "project_name": proj["project_name"],
            "owner": proj["owner"],
            "team_members": proj.get("team_members", []),
            "results_so_far": latest_update.get("results_so_far", ""),
            "next_steps": latest_update.get("next_steps", ""),
            "tasks": proj.get("tasks", []),
            "timeline": proj.get("timeline", {})
        }
        
        # Read and embed the JS template
        with open("templates/slide_preview.js", "r") as f:
            js_code = f.read()
        
        html_content = f"""
        <div id="slide-preview-container"></div>
        <script>
        {js_code}
        window.slideData = {json.dumps(preview_data)};
        renderSlidePreview(window.slideData, 'slide-preview-container');
        </script>
        """
        
        st.components.v1.html(html_content, height=600)


# PAGE: SETTINGS
def page_settings():
    st.title("⚙️ Settings")
    
    settings = settings_module.load_settings()
    
    st.markdown("### Ollama Configuration")
    
    # Ollama connection status
    is_connected = settings_module.check_ollama_connection()
    status_color = "🟢" if is_connected else "🔴"
    st.metric("Ollama Status", "Connected" if is_connected else "Disconnected", status_color)
    
    # Show available models info
    available_models = settings_module.get_available_models()
    if is_connected:
        if available_models:
            st.success(f"✅ Found {len(available_models)} installed model(s)")
            st.caption("Installed: " + ", ".join(available_models))
        else:
            st.warning("⚠️ No models installed. Pull a model first:")
            st.code("ollama pull llama3", language="bash")
    
    with st.form("settings_form"):
        # Ollama base URL
        new_url = st.text_input(
            "Ollama Base URL",
            value=settings.get("ollama_base_url", "http://localhost:11434")
        )
        
        # Model selection
        if not available_models:
            st.warning("Could not fetch available models. Make sure Ollama is running.")
            available_models = ["llama3", "llama2", "mistral"]
        
        current_model = settings.get("model", "llama3")
        
        # Try to find current model in available models (with or without :latest)
        if current_model in available_models:
            current_index = available_models.index(current_model)
        elif f"{current_model}:latest" in available_models:
            current_index = available_models.index(f"{current_model}:latest")
        else:
            current_index = 0
        
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=current_index
        )
        
        if st.form_submit_button("💾 Save Settings"):
            settings_module.set_ollama_base_url(new_url)
            settings_module.set_model(selected_model)
            st.toast("✅ Settings saved!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### How to set up Ollama")
    st.code("""
# Install Ollama from https://ollama.ai
# Pull a model (e.g., llama3, llama2, mistral)
ollama pull llama3

# Start Ollama server
ollama serve

# Or run in background:
ollama serve &
    """, language="bash")


# Route to appropriate page
if st.session_state.current_page == "home":
    page_home()
elif st.session_state.current_page == "project_detail":
    page_project_detail()
elif st.session_state.current_page == "ai_update":
    page_ai_update()
elif st.session_state.current_page == "slides":
    page_slides()
elif st.session_state.current_page == "settings":
    page_settings()

# Footer
st.markdown("---")
st.caption("Project Status Slide Creator • Powered by Streamlit & Ollama")
