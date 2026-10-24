import json
import requests
import streamlit as st
from pypdf import PdfReader
from datetime import date

st.set_page_config(page_title="LazyStudent", page_icon="📚", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1100px;}
.hero {padding: 1.5rem; border-radius: 18px; background: linear-gradient(120deg, #14213d, #294c60); color: white; margin-bottom: 1rem;}
.small-muted {color: #6b7280; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>📚 LazyStudent</h1><p>Your morning study brief — less planning, more progress.</p></div>', unsafe_allow_html=True)

if "tasks" not in st.session_state:
    st.session_state.tasks = []

with st.sidebar:
    st.header("⚙️ Settings")
    ollama_url = st.text_input("Ollama URL", "http://localhost:11434")
    model = st.text_input("Model name", "qwen2.5:3b")
    st.caption("Your documents are processed on this computer when using local Ollama.")
    st.divider()
    st.subheader("➕ Add a task")
    with st.form("task_form", clear_on_submit=True):
        task_title = st.text_input("Task name", placeholder="e.g. Finish DLD Assignment 2")
        task_due = st.date_input("Deadline", value=date.today())
        task_minutes = st.number_input("Estimated time (minutes)", min_value=15, max_value=600, value=60, step=15)
        task_subject = st.text_input("Subject (optional)", placeholder="e.g. Digital Logic Design")
        add_task = st.form_submit_button("Add task", use_container_width=True)
        if add_task and task_title.strip():
            st.session_state.tasks.append({
                "title": task_title.strip(),
                "deadline": task_due.isoformat(),
                "minutes": int(task_minutes),
                "subject": task_subject.strip() or "General",
                "source": "Added manually",
                "done": False
            })
            st.success("Task added!")

left, right = st.columns([1, 1], gap="large")
with left:
    st.subheader("1. Add assignment PDFs")
    uploaded_files = st.file_uploader("Upload PDFs (text-based PDFs work best)", type=["pdf"], accept_multiple_files=True)
    extracted_text = ""
    if uploaded_files:
        for pdf in uploaded_files:
            try:
                reader = PdfReader(pdf)
                pages = []
                for page in reader.pages:
                    pages.append(page.extract_text() or "")
                text = "\n".join(pages)
                extracted_text += f"\n\n--- FILE: {pdf.name} ---\n{text[:18000]}"
                st.caption(f"Read {pdf.name}: {len(text)} characters extracted")
            except Exception as e:
                st.warning(f"Could not read {pdf.name}: {e}")
    manual_notes = st.text_area("Extra notes / to-do list", placeholder="Example:\nCalculus assignment due Friday\nRevise heaps for DSA quiz\nPrepare DLD lab record", height=160)
    study_hours = st.slider("How much time can you study today?", min_value=1, max_value=12, value=3)
    energy = st.select_slider("Today's energy level", options=["Very low", "Low", "Okay", "Good", "High"], value="Okay")

with right:
    st.subheader("2. Build your morning brief")
    st.write("LazyStudent combines your PDFs, notes, and manually added tasks into a realistic plan.")
    if st.button("✨ Generate my study plan", type="primary", use_container_width=True):
        task_context = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
        source_text = (extracted_text + "\n\nUSER NOTES:\n" + manual_notes).strip()
        if not source_text and not st.session_state.tasks:
            st.warning("Upload a PDF, add notes, or create a task first.")
        else:
            prompt = f"""You are LazyStudent, a careful study-planning assistant.
Create a practical study plan for TODAY.
Available study time: {study_hours} hours.
Student's energy level: {energy}.
Existing tasks (JSON): {task_context}
Assignment/notes text:
{source_text[:24000]}

Rules:
- Use only deadlines and requirements actually present in the input. Do not invent dates or claim an unclear deadline is certain.
- Prioritize overdue and soon-due tasks, then important study/revision.
- Fit the plan into the available time; include short breaks.
- If information is missing, clearly label assumptions or ask the student to confirm.
- Keep the language simple and encouraging.
- Format the answer with: Today's focus, Prioritized task list (priority + estimated time + reason), Time-block schedule, and Questions/uncertain deadlines.
"""
            with st.spinner("Asking your local model to plan your day..."):
                try:
                    response = requests.post(
                        f"{ollama_url.rstrip('/')}/api/generate",
                        json={"model": model, "prompt": prompt, "stream": False},
                        timeout=180
                    )
                    response.raise_for_status()
                    result = response.json().get("response", "").strip()
                    st.session_state.study_plan = result
                except requests.exceptions.ConnectionError:
                    st.error("Can't connect to Ollama. Open Ollama and make sure the model is installed.")
                    st.code("ollama pull qwen2.5:3b\nollama run qwen2.5:3b")
                except requests.exceptions.Timeout:
                    st.error("The model took too long. Try a smaller model or shorter PDFs.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

if "study_plan" in st.session_state and st.session_state.study_plan:
    st.divider()
    st.subheader("☀️ Your Morning Brief")
    st.markdown(st.session_state.study_plan)
    st.download_button("Download plan as text", st.session_state.study_plan, file_name="lazystudent_morning_brief.txt", mime="text/plain")

st.divider()
st.subheader("3. Your task checklist")
if not st.session_state.tasks:
    st.info("No manual tasks yet. Add one from the sidebar, or upload an assignment and generate a plan.")
else:
    for i, task in enumerate(st.session_state.tasks):
        cols = st.columns([0.08, 0.62, 0.18, 0.12])
        checked = cols[0].checkbox("Done", value=task["done"], key=f"done_{i}", label_visibility="collapsed")
        st.session_state.tasks[i]["done"] = checked
        label = f"~~{task['title']}~~" if checked else f"**{task['title']}**"
        cols[1].markdown(label + f"\n\n<small>{task['subject']} · {task['minutes']} min · Due {task['deadline']}</small>", unsafe_allow_html=True)
        cols[2].caption(task["source"])
        if cols[3].button("Remove", key=f"remove_{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()

st.caption("Privacy note: this prototype sends prompts to the Ollama service configured above. With local Ollama on your own computer, inference stays local. Do not expose Ollama to the public internet.")
