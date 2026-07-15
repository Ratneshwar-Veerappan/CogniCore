import os
import csv
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from tinydb import TinyDB, Query  # 🗄️ Lightweight JSON database storage

# Load local environment variables
load_dotenv()

# Initialize Persistent Local Database (Saves data to a file on your disk)
db = TinyDB("cognicore_db.json")
NotesQuery = Query()

# Initialize Groq Client securely (Forces loading from .env without risk of leakage)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
try:
    if GROQ_API_KEY:
        ai_client = Groq(api_key=GROQ_API_KEY)
    else:
        ai_client = None
except Exception:
    ai_client = None

# Configure Streamlit Dashboard Theme & Layout
st.set_page_config(page_title="CogniCore // AI Web Hub", page_icon="🧠", layout="wide")

# --- PREMIUM UI THEME STYLING ---
st.markdown("""
    <style>
    /* Main Layout & Dark Theme Overrides */
    .stApp { background-color: #0f1115; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #16181d; border-right: 1px solid #2d3748; }
    
    /* Input Fields Custom Tech Borders */
    .stTextInput > div > div > input {
        background-color: #1e2128 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        border: 1px solid #2d3748 !important;
    }
    
    /* Content Editor Text Area */
    .stTextArea > div > div > textarea {
        background-color: #1e2128 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        border: 1px solid #2d3748 !important;
    }
    
    /* Action Bar Buttons */
    .stButton > button {
        background-color: transparent !important;
        color: #9ca3af !important;
        border: 1px solid #4b5563 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #718096 !important;
    }
    
    /* Clean Typography */
    h1, h2, h3, h4 { font-family: 'Inter', sans-serif; }
    div[data-testid="stExpander"] { background-color: #16181d; border: 1px solid #2d3748; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# Helper Function: Query the AI Engine
def query_ai(prompt, system_instruction="You are an expert academic tutor."):
    if not ai_client or not GROQ_API_KEY:
        return "⚠️ Setup Error: Groq API Key missing or unconfigured in runtime environment (.env)."
    try:
        completion = ai_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2048
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ System Error querying AI: {str(e)}"

# --- SIDEBAR USER MANAGEMENT & DATA RETRIEVAL ---
st.sidebar.title("👤 User Session Node")

# Simple profile switching configuration
current_user = st.sidebar.text_input("Access Credentials / Profile Key:", value="Guest").strip().lower()

if current_user == "guest":
    st.sidebar.warning("⚠️ Running as guest. Connect a custom Profile Key to preserve notes forever.")
else:
    st.sidebar.success(f"🔓 Node connected: {current_user}")

st.sidebar.markdown("---")

# Query only the notes belonging to the currently authenticated profile
db_records = db.search(NotesQuery.user == current_user)
user_notes = {rec["subject"]: {"title": rec["title"], "content": rec["content"]} for rec in db_records}

# Interactive Global Search Node
search_query = st.sidebar.text_input("🔍 Filter Network Nodes...", "").lower()

# Render Notebook Node Access Controls from Database
st.sidebar.subheader("🗂️ Stored Notebook Repositories")
selected_node = None
for note_id, data in list(user_notes.items()):
    if search_query in data['title'].lower() or search_query in note_id.lower():
        if st.sidebar.button(f"📂 [{note_id.upper()}] {data['title']}", key=f"btn_{note_id}"):
            selected_node = note_id

st.sidebar.markdown("---")
st.sidebar.caption("🛸 **System Creator:** Ratneshwar Veerappan")
st.sidebar.caption("⚙️ **Core version:** 2026.1.2 // Permanent Storage")

# --- MAIN DASHBOARD WORKSPACE PANELS ---
st.title("CogniCore Workspace // Web Node")

tab_editor, tab_chat, tab_tools = st.tabs(["📝 Core Data Workspace", "💬 Neural Chat Engine", "⚡ AI Compilation Tools"])

# Load selected note details if active
default_subj = user_notes[selected_node]["title"] if selected_node else ""
default_cont = user_notes[selected_node]["content"] if selected_node else ""

with tab_editor:
    st.subheader("Workspace Editor")
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject Group / Academic Unit:", value=selected_node or "")
    with col2:
        title = st.text_input("Topic Target Header:", value=default_subj)
        
    content = st.text_area("Source Lecture Document Metadata Matrix:", value=default_cont, height=280)
    
    # Elegant, clean button column layout mimicking your design reference image
    st.write("") 
    col_new, col_save, col_del, col_exp, col_spacer = st.columns([1, 1, 1, 1, 4])
    
    with col_new:
        if st.button("New", use_container_width=True):
            st.rerun()
            
    with col_save:
        if st.button("Save", use_container_width=True):
            if subject and title and content:
                # Remove existing record of the same subject for this user before updating
                db.remove((NotesQuery.user == current_user) & (NotesQuery.subject == subject))
                # Commit clean record
                db.insert({
                    "user": current_user,
                    "subject": subject,
                    "title": title,
                    "content": content
                })
                st.toast(f"Node '{title}' saved to database!", icon="💾")
                st.rerun()
            else:
                st.toast("Validation Error: All inputs are required to save.", icon="⚠️")
                
    with col_del:
        if st.button("Delete", use_container_width=True):
            if subject:
                db.remove((NotesQuery.user == current_user) & (NotesQuery.subject == subject))
                st.toast(f"Deleted topic unit: '{subject}'", icon="🗑️")
                st.rerun()
            else:
                st.toast("Select a saved subject to delete.", icon="⚠️")
                
    with col_exp:
        # Simple JSON download of raw active note structure
        note_json = json.dumps({"subject": subject, "title": title, "content": content}, indent=4)
        st.download_button(
            label="Export",
            data=note_json,
            file_name=f"{subject.replace(' ', '_') or 'Node'}_Export.json",
            mime="application/json",
            use_container_width=True
        )

    # 3. Premium Interactive Document Upload & Automatic Parsing Node
    st.markdown("---")
    st.caption("📥 Import an external study file (.txt or .csv data)")
    uploaded_file = st.file_uploader("Upload Node Configuration File", type=["txt", "csv"], label_visibility="collapsed")
    
    if uploaded_file:
        try:
            file_type = uploaded_file.name.split(".")[-1]
            if file_type == "txt":
                imported_text = uploaded_file.read().decode("utf-8")
                # Pre-populate content with txt data
                st.session_state[f"import_{uploaded_file.name}"] = imported_text
                st.info(f"✅ Text loaded! Press 'Save' to commit to user database.")
                content = imported_text
            elif file_type == "csv":
                imported_text = uploaded_file.read().decode("utf-8")
                reader = csv.reader(imported_text.splitlines())
                rows = list(reader)
                if len(rows) > 1:
                    subject = rows[1][0]
                    title = rows[1][1]
                    content = rows[1][2]
                    st.success(f"✅ Loaded structured node matrix dynamically from CSV!")
        except Exception as upload_err:
            st.error(f"Failed to read file layout: {str(upload_err)}")

with tab_chat:
    st.subheader("Neural Chat Engine")
    
    col_input_txt, col_input_mic = st.columns([3, 1])
    
    with col_input_txt:
        user_query = st.text_input("Type manual concept queries here:", key="chat_in")
        
    with col_input_mic:
        voice_audio = st.audio_input("🎙️ Voice Capture Command")

    # Asynchronous Audio Matrix Parsing Process
    if voice_audio:
        audio_bytes = voice_audio.read()
        audio_id = f"audio_{len(audio_bytes)}"
        
        if "last_processed_audio" not in st.session_state or st.session_state.last_processed_audio != audio_id:
            with st.spinner("Transcribing Voice Transmission..."):
                try:
                    transcription = ai_client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=("audio.wav", audio_bytes),
                        response_format="text"
                    )
                    user_query = transcription.strip()
                    st.session_state.last_processed_audio = audio_id
                    st.success(f"🗣️ Decrypted Audio Vector: \"{user_query}\"")
                except Exception as audio_err:
                    st.error(f"❌ Core Transcription Failure: {str(audio_err)}")

    if user_query:
        with st.spinner("Streaming from Groq Neural Matrix..."):
            response = query_ai(user_query, "You are a highly capable engineering instructor.")
            st.markdown(f"**🤖 CogniCore AI Platform Engine:**\n\n{response}")

with tab_tools:
    st.subheader("AI Compilation & Synthesis Matrix")
    
    if not content.strip():
        st.info("🔌 System Standby: Populate source lecture metadata in the Core Workspace first to unlock synthesis tools.")
    else:
        col_controls, col_output = st.columns([1, 2])
        
        with col_controls:
            st.markdown("### 🛠️ Execution Controls")
            
            st.caption("CORE COMPILATION")
            run_sum = st.button("📝 Compile Core Summary", use_container_width=True)
            run_flash = st.button("🧠 Build Flashcard Matrix", use_container_width=True)
            run_quiz = st.button("🎯 Compile Evaluation Quiz", use_container_width=True)
            
            st.markdown("---")
            
            st.caption("PLANNING & STRATEGY")
            days = st.slider("Exam Buffer Threshold (Days):", 1, 30, 7)
            run_sched = st.button("📅 Build Tactical Roadmap", use_container_width=True)
            
        with col_output:
            st.markdown("### 🖥️ Output Terminal")
            
            if "last_compiled_output" not in st.session_state:
                st.session_state.last_compiled_output = ""
            if "last_compiled_type" not in st.session_state:
                st.session_state.last_compiled_type = ""

            if run_sum:
                with st.spinner("Executing Summary Compilation Protocol..."):
                    result = query_ai(f"Summarize cleanly into structural bullets:\n\n{content}")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Summary_{subject.replace(' ', '_')}"

            elif run_flash:
                with st.spinner("Structuring Neural Flashcard Matrix..."):
                    result = query_ai(f"Create 5 Q&A layout flashcard pairs:\n\n{content}")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Flashcards_{subject.replace(' ', '_')}"

            elif run_quiz:
                with st.spinner("Generating Evaluation Metrics..."):
                    result = query_ai(f"Create a 3-question multiple choice quiz with answer keys:\n\n{content}")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Quiz_{subject.replace(' ', '_')}"

            elif run_sched:
                with st.spinner("Mapping Temporal Roadmap..."):
                    result = query_ai(f"Create a high efficiency day-by-day study roadmap for an exam on {subject}: {title} in {days} days.")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Schedule_{subject.replace(' ', '_')}"

            if st.session_state.last_compiled_output:
                st.markdown(st.session_state.last_compiled_output)
                
                st.markdown("---")
                st.download_button(
                    label="💾 Export Output to Local Disk (.txt)",
                    data=st.session_state.last_compiled_output,
                    file_name=f"{st.session_state.last_compiled_type}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.info("System Idle. Select an execution command from the console panel to compile.")

# --- GLOBAL APPLICATION FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-family: 'Courier New', monospace; color: #9ca3af; font-size: 0.85rem; padding: 20px;">
        // CogniCore OS Engine built & operationalized by <span style="color: #00f0ff; font-weight: bold;">Ratneshwar Veerappan</span> © 2026
    </div>
    """, 
    unsafe_allow_html=True
)
