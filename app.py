import os
import json
import customtkinter as ctk
from tkinter import messagebox, filedialog
from groq import Groq

# Initialize CustomTkinter Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- AI Integration Layer ---
# Replace with your actual key or set the GROQ_API_KEY environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "Put your own API key here")

try:
    ai_client = Groq(api_key=GROQ_API_KEY)
except Exception:
    ai_client = None

class AIStudyAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🤖 AI Study Assistant Pro")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Application Data State
        self.notes_file = "study_notes.json"
        self.notes = self.load_notes()
        self.current_note_id = None

        self.setup_ui()

    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_notes(self):
        with open(self.notes_file, "w") as f:
            json.dump(self.notes, f, indent=4)

    def query_ai(self, prompt, system_instruction="You are an expert academic tutor."):
        if not ai_client or "PASTE_YOUR" in GROQ_API_KEY:
            return "⚠️ API Key Error: Please configure a valid Groq API key in the source code."
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

    def setup_ui(self):
        # Configure Grid Layout (1 Row, 2 Columns)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR (Navigation & Notes Panel) ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(3, weight=1)

        self.brand_lbl = ctk.CTkLabel(self.sidebar, text="🧠 AI Study Hub", font=ctk.CTkFont(size=22, weight="bold"))
        self.brand_lbl.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Action Buttons
        self.new_note_btn = ctk.CTkButton(self.sidebar, text="+ New Study Note", fg_color="#22c55e", hover_color="#16a34a", text_color="white", command=self.clear_editor)
        self.new_note_btn.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # Search Panel
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_notes_list())
        self.search_bar = ctk.CTkEntry(self.sidebar, placeholder_text="🔍 Search notes by topic...", textvariable=self.search_var)
        self.search_bar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Notes List Box (Scrollable)
        self.notes_scroll = ctk.CTkScrollableFrame(self.sidebar, label_text="My Notebooks")
        self.notes_scroll.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # Sidebar Footer Controls
        self.export_btn = ctk.CTkButton(self.sidebar, text="📤 Export Notebook", fg_color="transparent", border_width=1, command=self.export_current_note)
        self.export_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # --- RIGHT MAIN WORKSPACE (Tabs Layout) ---
        self.workspace = ctk.CTkTabview(self)
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)
        
        self.tab_editor = self.workspace.add("📝 Workspace & Editor")
        self.tab_chat = self.workspace.add("💬 Ask AI Brain")
        self.tab_tools = self.workspace.add("⚡ AI Engine Tools")

        self.build_editor_tab()
        self.build_chat_tab()
        self.build_tools_tab()
        
        self.refresh_notes_list()

    # --- TAB 1: WORKSPACE EDITOR ---
    def build_editor_tab(self):
        self.tab_editor.grid_columnconfigure(1, weight=1)
        self.tab_editor.grid_rowconfigure(2, weight=1)

        # Form Controls
        ctk.CTkLabel(self.tab_editor, text="Subject / Core Unit:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.subject_ent = ctk.CTkEntry(self.tab_editor, placeholder_text="e.g., Computer Science, Physics")
        self.subject_ent.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.tab_editor, text="Topic Title:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.title_ent = ctk.CTkEntry(self.tab_editor, placeholder_text="e.g., Binary Trees, Thermodynamics Fluid Laws")
        self.title_ent.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Core Notebook Editor
        self.editor_txt = ctk.CTkTextbox(self.tab_editor, font=ctk.CTkFont(family="Consolas", size=13))
        self.editor_txt.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Action Buttons Tray
        self.tray_frame = ctk.CTkFrame(self.tab_editor, fg_color="transparent")
        self.tray_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.save_note_btn = ctk.CTkButton(self.tray_frame, text="💾 Save Current Note", command=self.save_current_note)
        self.save_note_btn.pack(side="left", padx=5)

        self.delete_note_btn = ctk.CTkButton(self.tray_frame, text="🗑️ Delete Note", fg_color="#ef4444", hover_color="#dc2626", command=self.delete_current_note)
        self.delete_note_btn.pack(side="left", padx=5)

    # --- TAB 2: CHAT HUB ---
    def build_chat_tab(self):
        self.tab_chat.grid_columnconfigure(0, weight=1)
        self.tab_chat.grid_rowconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(self.tab_chat, font=ctk.CTkFont(size=13), state="disabled")
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.chat_input = ctk.CTkEntry(self.tab_chat, placeholder_text="Ask any complex scientific question or prompt concept verification here...")
        self.chat_input.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.chat_input.bind("<Return>", lambda event: self.send_chat_message())

        self.send_chat_btn = ctk.CTkButton(self.tab_chat, text="🚀 Ask AI", width=100, command=self.send_chat_message)
        self.send_chat_btn.grid(row=1, column=1, padx=10, pady=10)

    # --- TAB 3: ENGINE TOOLS ---
    def build_tools_tab(self):
        self.tab_tools.grid_columnconfigure(1, weight=1)
        self.tab_tools.grid_rowconfigure(0, weight=1)

        # Operational Control Frame
        self.tools_sidebar = ctk.CTkFrame(self.tab_tools, width=220)
        self.tools_sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Output Matrix Display Viewport
        self.tools_display = ctk.CTkTextbox(self.tab_tools, font=ctk.CTkFont(size=13))
        self.tools_display.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Automation Engine Core Actions Buttons
        ctk.CTkLabel(self.tools_sidebar, text="AI Engine Operations", font=ctk.CTkFont(weight="bold")).pack(pady=15, padx=10)

        ctk.CTkButton(self.tools_sidebar, text="📝 Summarize Note", command=self.run_ai_summarizer).pack(pady=8, padx=15, fill="x")
        ctk.CTkButton(self.tools_sidebar, text="🧠 Flashcard Matrix", command=self.run_ai_flashcards).pack(pady=8, padx=15, fill="x")
        ctk.CTkButton(self.tools_sidebar, text="🎯 Interactive Quiz", command=self.run_ai_quiz).pack(pady=8, padx=15, fill="x")
        
        # Scheduler Parameter Widgets Block
        ctk.CTkLabel(self.tools_sidebar, text="Days Until Exam:", font=ctk.CTkFont(size=11)).pack(pady=(15,0))
        self.days_slider_lbl = ctk.CTkLabel(self.tools_sidebar, text="7 Days", font=ctk.CTkFont(weight="bold"))
        self.days_slider_lbl.pack()
        
        self.days_slider = ctk.CTkSlider(self.tools_sidebar, from_=1, to=60, number_of_steps=59, command=self.update_slider_label)
        self.days_slider.set(7)
        self.days_slider.pack(pady=5, padx=15, fill="x")

        ctk.CTkButton(self.tools_sidebar, text="📅 Build Schedule", fg_color="#3b82f6", command=self.run_ai_scheduler).pack(pady=10, padx=15, fill="x")

    # --- CORE REPOSITORY ENGINE FUNCTIONS ---
    def refresh_notes_list(self):
        for widget in self.notes_scroll.winfo_children():
            widget.destroy()

        search_term = self.search_var.get().lower()

        for note_id, data in self.notes.items():
            if search_term and search_term not in data['title'].lower() and search_term not in data['subject'].lower():
                continue

            display_txt = f"[{data['subject'].upper()}] {data['title']}"
            btn = ctk.CTkButton(
                self.notes_scroll, 
                text=display_txt, 
                anchor="w", 
                fg_color="transparent", 
                text_color="#e2e8f0", 
                hover_color="#1e293b",
                command=lambda nid=note_id: self.load_selected_note(nid)
            )
            btn.pack(fill="x", pady=2, padx=5)

    def load_selected_note(self, note_id):
        self.current_note_id = note_id
        note = self.notes[note_id]
        
        self.subject_ent.delete(0, "end")
        self.subject_ent.insert(0, note["subject"])
        
        self.title_ent.delete(0, "end")
        self.title_ent.insert(0, note["title"])
        
        self.editor_txt.delete("1.0", "end")
        self.editor_txt.insert("1.0", note["content"])
        
        self.workspace.set("📝 Workspace & Editor")

    def save_current_note(self):
        subject = self.subject_ent.get().strip()
        title = self.title_ent.get().strip()
        content = self.editor_txt.get("1.0", "end-1c").strip()

        if not title or not content:
            messagebox.showwarning("Incomplete Fields", "Please make sure your note has a Title and Content.")
            return

        if not subject:
            subject = "General Study"

        if not self.current_note_id:
            self.current_note_id = str(os.urandom(4).hex())

        self.notes[self.current_note_id] = {
            "subject": subject,
            "title": title,
            "content": content
        }
        self.save_notes()
        self.refresh_notes_list()
        messagebox.showinfo("Success", "Study Note successfully compiled into memory state database!")

    def delete_current_note(self):
        if self.current_note_id and self.current_note_id in self.notes:
            del self.notes[self.current_note_id]
            self.save_notes()
            self.clear_editor()
            self.refresh_notes_list()
            messagebox.showinfo("Deleted", "Note successfully removed from internal memory array.")
        else:
            messagebox.showwarning("Selection Error", "No active note selected to delete.")

    def clear_editor(self):
        self.current_note_id = None
        self.subject_ent.delete(0, "end")
        self.title_ent.delete(0, "end")
        self.editor_txt.delete("1.0", "end")

    def export_current_note(self):
        content = self.editor_txt.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Export Failed", "There is no text data content loaded in the current layout framework to dump.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("Markdown Files", "*.md")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"SUBJECT: {self.subject_ent.get().upper()}\nTITLE: {self.title_ent.get()}\n\n{content}")
            messagebox.showinfo("Export complete", "Data successfully output to system filesystem.")

    # --- RUN TIME AI LAYER ACTIONS ---
    def send_chat_message(self):
        query = self.chat_input.get().strip()
        if not query:
            return

        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"🧑 You:\n{query}\n\n")
        self.chat_input.delete(0, "end")
        
        # Run AI Interface Query
        ai_response = self.query_ai(query, "You are a smart, interactive AI study helper who explains things clearly with examples.")
        
        self.chat_display.insert("end", f"🤖 AI Assistant:\n{ai_response}\n\n--------------------\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def run_ai_summarizer(self):
        content = self.editor_txt.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Missing Data Source", "The script layout engine cannot run without notes text data.")
            return
        
        self.workspace.set("⚡ AI Engine Tools")
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", "⏳ Generating summary using Groq Pipeline Neural Lattice...")
        self.update()

        prompt = f"Please read the following text data notes and summarize them cleanly into brief bullet points:\n\n{content}"
        summary = self.query_ai(prompt, "You are an advanced text summarizing engine processing complex raw lecture documentation.")
        
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", summary)

    def run_ai_flashcards(self):
        content = self.editor_txt.get("1.0", "end-1c").strip()
        if not content:
            return
        
        self.workspace.set("⚡ AI Engine Tools")
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", "⏳ Generating study flashcards...")
        self.update()

        prompt = f"Create a list of 5 dynamic Flashcard pairs (Question and Answer structural layout format) derived from these notes:\n\n{content}"
        cards = self.query_ai(prompt, "You are a flashcard processing sub-module breaking down study topics into precise question/answer pairs.")
        
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", cards)

    def run_ai_quiz(self):
        content = self.editor_txt.get("1.0", "end-1c").strip()
        if not content:
            return
        
        self.workspace.set("⚡ AI Engine Tools")
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", "⏳ Compiling runtime custom quiz evaluation...")
        self.update()

        prompt = f"Create a 3-question multiple-choice quiz based on these study notes. Include an answer key at the bottom:\n\n{content}"
        quiz = self.query_ai(prompt, "You are an automated evaluation system crafting multiple-choice verification testing blueprints.")
        
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", quiz)

    def update_slider_label(self, val):
        self.days_slider_lbl.configure(text=f"{int(val)} Days")

    def run_ai_scheduler(self):
        subject = self.subject_ent.get().strip() or "General Study Fields"
        title = self.title_ent.get().strip() or "Core Curriculum Data"
        days = int(self.days_slider.get())

        self.workspace.set("⚡ AI Engine Tools")
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", "⏳ Generating personalized roadmap matrix...")
        self.update()

        prompt = f"I have an exam on '{subject}: {title}' in exactly {days} days. Generate a day-by-day structured execution study timetable to help me study efficiently."
        schedule = self.query_ai(prompt, "You are a high-efficiency time management scheduling system tracking target academic deadlines.")
        
        self.tools_display.delete("1.0", "end")
        self.tools_display.insert("end", schedule)

if __name__ == "__main__":
    app = AIStudyAssistant()
    app.mainloop()
