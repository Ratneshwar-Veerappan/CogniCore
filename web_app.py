import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load local environment variables securely from .env
load_dotenv()

# Initialize Groq Client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "Put your own API key here")
try:
    ai_client = Groq(api_key=GROQ_API_KEY)
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

# Creator Credit Node
st.sidebar.markdown("---")
st.sidebar.caption("🛸 **System Creator:** Ratneshwar Veerappan")
st.sidebar.caption("⚙️ **Core version:** 2026.1.0 // Operational")

# Render Notebook Node Access Controls
st.sidebar.subheader("🗂️ Stored Notebook Repositories")
selected_node = None
for note_id, data in list(st.session_state.notes.items()):
    if search_query in data['title'].lower() or search_query in note_id.lower():
        if st.sidebar.button(f"📂 [{note_id.upper()}] {data['title']}", key=note_id):
            selected_node = note_id

# --- MAIN DASHBOARD WORKSPACE PANELS ---
st.title("🤖 CogniCore Workspace // Web Node")

# Build Responsive Web Tabs Layout
tab_editor, tab_chat, tab_tools = st.tabs(["📝 Core Data Workspace", "💬 Neural Chat Engine", "⚡ AI Compilation Tools"])

# Pre-populate variables if a sidebar notebook was clicked
default_subj = st.session_state.notes[selected_node]["title"] if selected_node else ""
default_cont = st.session_state.notes[selected_node]["content"] if selected_node else ""

with tab_editor:
    st.subheader("// Active Matrix Entry Window")
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Core Academic Field / Subject Unit:", value=selected_node or "")
    with col2:
        title = st.text_input("Topic Target Header:", value=default_subj)
        
    content = st.text_area("Source Lecture Document Metadata Matrix:", value=default_cont, height=250)
    
    if st.button("💾 Compile & Commit to Local Memory"):
        if subject and title and content:
            st.session_state.notes[subject] = {"title": title, "content": content}
            st.success(f"Success: Node '{title}' committed to runtime database layer!")
            st.rerun()
        else:
            st.warning("Validation Error: All framework fields must be populated.")

with tab_chat:
    st.subheader("// Direct LLM Communication Stream")
    user_query = st.text_input("Ask any complex scientific question or prompt concept verification here:", key="chat_in")
    if user_query:
        with st.spinner("Streaming from Groq Neural Matrix..."):
            response = query_ai(user_query, "You are a highly capable engineering instructor.")
            st.markdown(f"**🤖 CogniCore AI Platform Engine:**\n\n{response}")

with tab_tools:
    st.subheader("// Asynchronous Core Execution Operations")
    if not content.strip():
        st.info("System Standby: Populate database notes inside the Core Workspace Tab first.")
    else:
        col_actions, col_display = st.columns([1, 2])
        
        with col_actions:
            run_sum = st.button("📝 Generate Core Summary")
            run_flash = st.button("🧠 Build Flashcard Matrix")
            run_quiz = st.button("🎯 Compile Evaluation Quiz")
            
            st.markdown("---")
            days = st.slider("Target Exam Buffer Threshold (Days):", 1, 30, 7)
            run_sched = st.button("📅 Build Tactical Roadmap")
            
        with col_display:
            if run_sum:
                with st.spinner("Summarizing..."):
                    st.write(query_ai(f"Summarize cleanly into structural bullets:\n\n{content}"))
            elif run_flash:
                with st.spinner("Generating flashcards..."):
                    st.write(query_ai(f"Create 5 Q&A layout flashcard pairs:\n\n{content}"))
            elif run_quiz:
                with st.spinner("Compiling evaluation..."):
                    st.write(query_ai(f"Create a 3-question multiple choice quiz with answer keys:\n\n{content}"))
            elif run_sched:
                with st.spinner("Scheduling..."):
                    st.write(query_ai(f"Create a high efficiency day-by-day study roadmap for an exam on {subject}: {title} in {days} days."))
# --- GLOBAL WEB FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-family: 'Courier New', monospace; color: #9ca3af; font-size: 0.85rem; padding: 20px;">
        // CogniCore OS Engine built & operationalized by <span style="color: #00f0ff; font-weight: bold;">Ratneshwar Veerappan</span> © 2026
    </div>
    """, 
    unsafe_allow_html=True
)
