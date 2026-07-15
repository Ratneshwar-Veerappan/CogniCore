import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load local environment variables securely from .env configuration
load_dotenv()

# Initialize Groq Client Securely (Hardcoded fallback token text removed to protect assets)
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

# Custom Tech Styling UI Enhancement
st.markdown("""
    <style>
    .reportview-container { background: #030712; }
    h1 { color: #00f0ff !important; font-family: 'Courier New', monospace; }
    .stButton>button { background-color: transparent; color: #39ff14; border: 1px solid #39ff14; }
    .stButton>button:hover { background-color: rgba(57, 255, 20, 0.1); color: #39ff14; }
    </style>
""", unsafe_allow_html=True)

# Helper Function: Query the AI Engine
def query_ai(prompt, system_instruction="You are an expert academic tutor."):
    if not ai_client or not GROQ_API_KEY:
        return "⚠️ Setup Error: Groq API Key missing or unconfigured in runtime environment."
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

# --- SIDEBAR NOTEBOOK PERSISTENCE SYSTEM ---
st.sidebar.title("🧠 CogniCore OS")
st.sidebar.markdown("---")

# Simulated local notebook state storage block
if "notes" not in st.session_state:
    st.session_state.notes = {"General": {"title": "Example", "content": "Paste study fields here..."}}

# Interactive Global Search Node
search_query = st.sidebar.text_input("🔍 Filter Network Nodes...", "").lower()

# Render Notebook Node Access Controls
st.sidebar.subheader("🗂️ Stored Notebook Repositories")
selected_node = None
for note_id, data in list(st.session_state.notes.items()):
    if search_query in data['title'].lower() or search_query in note_id.lower():
        if st.sidebar.button(f"📂 [{note_id.upper()}] {data['title']}", key=note_id):
            selected_node = note_id

# 🛸 Creator Credit Node added to sidebar matrix footer
st.sidebar.markdown("---")
st.sidebar.caption("🛸 **System Creator:** Ratneshwar Veerappan")
st.sidebar.caption("⚙️ **Core version:** 2026.1.0 // Operational")

# --- MAIN DASHBOARD WORKSPACE PANELS ---
st.title("🤖 CogniCore Workspace // Web Node")

# Build Responsive Web Tabs Layout
tab_editor, tab_chat, tab_tools = st.tabs(["📝 Core Data Workspace", "💬 Neural Chat Engine", "⚡ AI Compilation Tools"])

# Pre-populate variables if a sidebar notebook was clicked
default_subj = st.session_state.notes[selected_node]["title"] if selected_node else ""
default_cont = st.session_state.notes[selected_node]["content"] if selected_node else ""

with tab_editor:
    st.subheader("Editor")
    
    # 1. Input Fields
    subject = st.text_input("Subject", value=selected_node or "")
    title = st.text_input("Title", value=default_subj)
    content = st.text_area("Content", value=default_cont, height=350)
    
    # 2. The Action Bar (New, Save, Delete, Export)
    st.write("") # Spacer
    col_new, col_save, col_del, col_exp, spacer = st.columns([1, 1, 1, 1, 4])
    
    with col_new:
        if st.button("New"):
            # Clear logic here
            st.rerun()
            
    with col_save:
        if st.button("Save"):
            if subject and title:
                st.session_state.notes[subject] = {"title": title, "content": content}
                st.toast(f"Node '{title}' saved successfully!", icon="💾") # Use toast instead of big success block!
                st.rerun()
            else:
                st.toast("Subject and Title are required.", icon="⚠️")
                
    with col_del:
        if st.button("Delete"):
            if subject in st.session_state.notes:
                del st.session_state.notes[subject]
                st.toast("Node deleted.", icon="🗑️")
                st.rerun()
                
    with col_exp:
        if st.button("Export"):
            st.toast("Exporting to CSV...", icon="📥")
            # Export logic here

    # 3. Document Upload Zone
    st.markdown("---")
    st.caption("Import a note (.txt, .pdf) or bulk-import notes (.csv)")
    uploaded_file = st.file_uploader("Upload", type=["txt", "csv", "pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        st.toast(f"File {uploaded_file.name} loaded into matrix buffer.", icon="✅")

with tab_chat:
    st.subheader("// Neural Chat Engine // Voice & Text Node")
    
    # 1. Dual-Input Interface Layout (Voice vs Text)
    col_input_txt, col_input_mic = st.columns([3, 1])
    
    with col_input_txt:
        user_query = st.text_input("Type manual concept queries here:", key="chat_in")
        
    with col_input_mic:
        # High-efficiency recording node using native browser audio pipelines
        voice_audio = st.audio_input("🎙️ Voice Capture Command")

    # 2. Asynchronous Audio Matrix Parsing Process
    if voice_audio:
        # Check if we have already compiled this unique audio clip to prevent loops
        audio_bytes = voice_audio.read()
        audio_id = f"audio_{len(audio_bytes)}"
        
        if "last_processed_audio" not in st.session_state or st.session_state.last_processed_audio != audio_id:
            with st.spinner("Transcribing Voice Transmission..."):
                try:
                    # Leverage Groq's high-speed Whisper model to translate audio to text string
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

    # 3. LLM Query Submission Core
    if user_query:
        with st.spinner("Streaming from Groq Neural Matrix..."):
            response = query_ai(user_query, "You are a highly capable engineering instructor.")
            st.markdown(f"**🤖 CogniCore AI Platform Engine:**\n\n{response}")

with tab_tools:
    st.subheader("AI Compilation & Synthesis Matrix")
    
    if not content.strip():
        st.info("🔌 System Standby: Populate source lecture metadata in the Core Workspace first to unlock synthesis tools.")
    else:
        # Create a split screen: Left is controls, Right is live output
        col_controls, col_output = st.columns([1, 2])
        
        with col_controls:
            st.markdown("### 🛠️ Execution Controls")
            
            # --- GROUP 1: FAST SYNTHESIS ---
            st.caption("CORE COMPILATION")
            run_sum = st.button("📝 Compile Core Summary", use_container_width=True)
            run_flash = st.button("🧠 Build Flashcard Matrix", use_container_width=True)
            run_quiz = st.button("🎯 Compile Evaluation Quiz", use_container_width=True)
            
            st.markdown("---")
            
            # --- GROUP 2: TACTICAL PLANNING ---
            st.caption("PLANNING & STRATEGY")
            days = st.slider("Exam Buffer Threshold (Days):", 1, 30, 7)
            run_sched = st.button("📅 Build Tactical Roadmap", use_container_width=True)
            
        with col_output:
            st.markdown("### 🖥️ Output Terminal")
            
            # Placeholder container that updates based on button click
            output_placeholder = st.empty()
            
            # We initialize a session state key to hold the current compiled text
            if "last_compiled_output" not in st.session_state:
                st.session_state.last_compiled_output = ""
            if "last_compiled_type" not in st.session_state:
                st.session_state.last_compiled_type = ""

            # 1. Action: Summary
            if run_sum:
                with st.spinner("Executing Summary Compilation Protocol..."):
                    result = query_ai(f"Summarize cleanly into structural bullets:\n\n{content}")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Summary_{subject.replace(' ', '_')}"

            # 2. Action: Flashcards
            elif run_flash:
                with st.spinner("Structuring Neural Flashcard Matrix..."):
                    result = query_ai(f"Create 5 Q&A layout flashcard pairs:\n\n{content}")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Flashcards_{subject.replace(' ', '_')}"

            # 3. Action: Quiz
            elif run_quiz:
                with st.spinner("Generating Evaluation Metrics..."):
                    result = query_ai(f"Create a 3-question multiple choice quiz with answer keys:\n\n{content}")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Quiz_{subject.replace(' ', '_')}"

            # 4. Action: Schedule
            elif run_sched:
                with st.spinner("Mapping Temporal Roadmap..."):
                    result = query_ai(f"Create a high efficiency day-by-day study roadmap for an exam on {subject}: {title} in {days} days.")
                    st.session_state.last_compiled_output = result
                    st.session_state.last_compiled_type = f"Schedule_{subject.replace(' ', '_')}"

            # Display the compiled output in a code-styled console block or markdown block
            if st.session_state.last_compiled_output:
                # Render the text beautifully
                st.markdown(st.session_state.last_compiled_output)
                
                # --- PROFESSIONAL ADDITION: EXPORT FILE LINK ---
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
# Premium UI Styling Matrix
st.markdown("""
    <style>
    /* Main Backgrounds */
    .stApp { background-color: #0f1115; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #16181d; border-right: 1px solid #2d3748; }
    
    /* Input Fields (Subject, Title, Search) */
    .stTextInput > div > div > input {
        background-color: #1e2128;
        color: #ffffff;
        border-radius: 6px;
        border: 1px solid #2d3748;
    }
    
    /* Text Area (Main Content) */
    .stTextArea > div > div > textarea {
        background-color: #1e2128;
        color: #ffffff;
        border-radius: 6px;
        border: 1px solid #2d3748;
    }
    
    /* Modern Action Buttons */
    .stButton > button {
        background-color: transparent;
        color: #9ca3af;
        border: 1px solid #4b5563;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2d3748;
        color: #ffffff;
        border: 1px solid #718096;
    }
    
    /* Typography improvements */
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)
